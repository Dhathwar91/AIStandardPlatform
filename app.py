from flask import Flask, request, jsonify, send_from_directory, redirect
import os
import sqlite3
import re
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

# --- Upload Folder ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database Setup ---
DB_NAME = 'users.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                     )''')
        conn.commit()
        conn.close()

init_db()

# --- Helper Functions ---
def validate_credentials(email, password, repeat_password=None):
    errors = []
    if '@' not in email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append("❌ Invalid email format.")
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$'
    if not re.match(password_regex, password):
        errors.append("❌ Password must be at least 8 characters long, include upper & lowercase letters, a number, and a special character.")
    if repeat_password is not None and password != repeat_password:
        errors.append("❌ Passwords do not match.")
    return errors

def user_exists(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user is not None

def save_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

def check_login(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        return user[0]  # Return the name (not just True)
    return None  # Return None if not found

# --- Routes ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# --- API Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    repeat_password = data.get('repeat_password')

    errors = validate_credentials(email, password, repeat_password)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    if user_exists(email):
        return jsonify({'success': False, 'errors': ['❌ User with this email already exists.']}), 400

    save_user(name, email, password)
    return jsonify({'success': True, 'message': '✅ Registration successful!'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            'success': True,
            'message': '✅ Login successful!',
            'name': user[0]  # Send the user's name
        })
    else:
        return jsonify({'success': False, 'errors': ['❌ Invalid email or password']}), 401

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    repeat_password = data.get('repeat_password')

    # Validate inputs
    errors = validate_credentials(email, password, repeat_password)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Check if user exists with given name and email
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name = ? AND email = ?", (name, email))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({'success': False, 'errors': ['❌ User with this name and email does not exist.']}), 404

    # Update password for existing user
    c.execute("UPDATE users SET password = ? WHERE name = ? AND email = ?", (password, name, email))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': '✅ Password updated successfully!'})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
