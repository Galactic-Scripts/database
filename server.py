from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt

app = Flask(__name__)
CORS(app)  # Allows requests from your frontend domain

DB_PATH = "users.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Register route
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "fail", "error": "Missing username or password"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "fail", "error": "Username already exists"}), 409

# Login route
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "fail", "error": "Missing username or password"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode("utf-8"), row[0]):
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "fail", "error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)
