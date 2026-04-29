from flask import Flask, jsonify, render_template, request
import pymysql
import os
import time

app = Flask(__name__)

# DB connection
def get_db_connection():
    for i in range(10):
        try:
            return pymysql.connect(
                host=os.getenv("DB_HOST", "mysql-db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root"),
                db=os.getenv("DB_NAME", "cloud"),
                port=int(os.getenv("DB_PORT", 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print(f"DB not ready, retrying... {i}")
            time.sleep(3)
    raise Exception("Database connection failed")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return "Up & Running 🚀"

# Create table
@app.route('/create_table')
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
    """)

    conn.commit()
    conn.close()
    return "Table created"

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
    """)

    conn.commit()
    conn.close()

# Insert data
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (data['name'], data['email'])
    )

    conn.commit()
    conn.close()
    return "User added"

# Fetch data
@app.route('/users')
def users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()

    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
