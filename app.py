from flask import Flask, jsonify, render_template, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import pymysql
import os
import time

app = Flask(__name__)

# =========================
# DB CONNECTION (with retry)
# =========================
def get_db_connection():
    retries = 10
    delay = 3

    for i in range(retries):
        try:
            # added for localhost testing
            #conn = pymysql.connect(
             #   host=os.getenv("DB_HOST", "localhost"),
             #   user=os.getenv("DB_USER", "flaskuser"),
             #   password=os.getenv("DB_PASSWORD", "flaskpass"),
             #   db=os.getenv("DB_NAME", "cloud"),
             #   port=int(os.getenv("DB_PORT", 3306)),
             #   charset='utf8mb4',
             #   cursorclass=pymysql.cursors.DictCursor
            #)

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
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args or ())
            if fetch:
                result = cursor.fetchall()
            else:
                result = None

        conn.commit()
        return result

    except Exception as e:
        print(f"DB Error: {e}")
        raise

    finally:
        conn.close()


# =========================
# INIT DB (Auto create table)
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
# ROUTES
# =========================
@app.route('/')
def index():
    APP_VISITS.inc()
    return render_template('index.html')


@app.route('/health')
def health():
    return "Up & Running 🚀"


# =========================
# CREATE USER
# =========================
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


# =========================
# READ USERS
# =========================
@app.route('/users', methods=['GET'])
def users():
    result = execute_query("SELECT * FROM users", fetch=True)
    return jsonify(result)


# =========================
# UPDATE USER
# =========================
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


# =========================
# DELETE USER
# =========================
@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    execute_query("DELETE FROM users WHERE id=%s", (id,))
    return jsonify({"message": "User deleted"})

# =========================
# 📊 Prometheus Metrics
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

# Example custom metric
APP_VISITS = Counter(
    'flask_app_visits_total',
    'Total visits to home page'
)

# =========================
# ⏱️ Track request time
# =========================

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    latency = time.time() - request.start_time

    REQUEST_LATENCY.labels(request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

    return response

# =========================
# 📊 Metrics Endpoint
# =========================

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# =========================
# START APP
# =========================
if __name__ == '__main__':
    init_db()   # Ensure table exists before app starts
    app.run(host='0.0.0.0', port=5000)
