from flask import Flask, jsonify, render_template, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import pymysql
import os
import time
import logging
import json
import uuid
from collections import deque

app = Flask(__name__)

# =========================
# LOGGING CONFIG (JSON)
# =========================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
        }

        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)
		

LOG_BUFFER = deque(maxlen=100)  # store last 100 logs

logger = logging.getLogger("flask-app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger.addHandler(handler)


# =========================
# DB CONNECTION (with retry)
# =========================
def get_db_connection():
    retries = 10
    delay = 3

    for i in range(retries):
        try:
            conn = pymysql.connect(
                host=os.getenv("DB_HOST", "mysql-db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root"),
                db=os.getenv("DB_NAME", "cloud"),
                port=int(os.getenv("DB_PORT", 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn

        except Exception as e:
            print(f"[Retry {i+1}/{retries}] DB not ready: {e}")
            time.sleep(delay)

    raise Exception("Database connection failed after retries")


# =========================
# COMMON QUERY EXECUTOR
# =========================
def execute_query(query, args=None, fetch=False):
    conn = get_db_connection()

    logger.info(
        "db_query",
        extra={
            "extra_data": {
                "query": query,
                "args": args
            }
        }
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args or ())
            result = cursor.fetchall() if fetch else None

        conn.commit()
        return result

    except Exception as e:
        logger.error(
            "db_error",
            extra={
                "extra_data": {
                    "query": query,
                    "error": str(e)
                }
            }
        )
        raise

    finally:
        conn.close()


# =========================
# INIT DB
# =========================
def init_db():
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
    """)
    print("Table ensured (users)")


# =========================
# PROMETHEUS METRICS
# =========================
REQUEST_COUNT = Counter(
    'flask_http_request_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_http_request_duration_seconds',
    'Request latency',
    ['endpoint']
)

APP_VISITS = Counter(
    'flask_app_visits_total',
    'Total visits to home page'
)


# =========================
# REQUEST TRACKING
# =========================
@app.before_request
def start_timer():
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())

@app.after_request
def log_request(response):
    latency = time.time() - request.start_time

    # Prometheus metrics
    REQUEST_LATENCY.labels(request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

    # Capture response safely
    try:
        response_body = response.get_json()
    except Exception:
        response_body = response.get_data(as_text=True)

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request.request_id,
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "latency_ms": round(latency * 1000, 2),
        "client_ip": request.remote_addr,
        "response": response_body
    }

    if request.method in ["POST", "PUT"]:
        log_data["payload"] = request.get_json(silent=True)

    # ✅ Store clean structured log
    LOG_BUFFER.append(log_data)

    # ✅ Send to stdout (for Loki/ELK)
    logger.info("request_completed", 
		extra={"extra_data": log_data,
			"labels": {"app": "flask-webapp"}
	})

    return response

# =========================
# ERROR HANDLER
# =========================
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(
        "application_error",
        extra={
            "extra_data": {
                "request_id": getattr(request, "request_id", None),
                "path": request.path,
                "method": request.method,
                "error": str(e),
            }
        }
    )
    return jsonify({"error": "Internal Server Error"}), 500


# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    APP_VISITS.inc()
    return render_template('index.html')


@app.route('/health')
def health():
    return "Up & Running 🚀"


@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Invalid input"}), 400

    execute_query(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (data['name'], data['email'])
    )

    return jsonify({"message": "User added"})


@app.route('/users', methods=['GET'])
def users():
    result = execute_query("SELECT * FROM users", fetch=True)
    return jsonify(result)


@app.route('/update_user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Invalid input"}), 400

    execute_query(
        "UPDATE users SET name=%s, email=%s WHERE id=%s",
        (data['name'], data['email'], id)
    )

    return jsonify({"message": "User updated"})


@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    execute_query("DELETE FROM users WHERE id=%s", (id,))
    return jsonify({"message": "User deleted"})


# =========================
# METRICS ENDPOINT
# =========================
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# =========================
# LOGS ENDPOINT
# =========================
@app.route('/logs')
def get_logs():
    path = request.args.get("path")
    status = request.args.get("status")

    logs = list(LOG_BUFFER)

    if path:
        logs = [log for log in logs if log["path"] == path]

    if status:
        logs = [log for log in logs if str(log["status_code"]) == status]

    return jsonify(logs)

# =========================
# START APP
# =========================
if __name__ == '__main__':
    try:
        init_db()
        print("DB Connected ✅")
    except Exception as e:
        print(f"⚠️ DB not available, starting app without DB: {e}")

    app.run(host='0.0.0.0', port=5000)
