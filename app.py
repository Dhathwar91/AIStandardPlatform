from flask import Flask, request, jsonify, send_from_directory, redirect
import os
import sqlite3
import re

app = Flask(__name__)

# --- Upload Folder ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Dummy File Store ---
files_list = []

# --- Database Setup ---
DB_NAME = 'users.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Add name column to users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
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
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# --- Routes for Pages ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('.', 'register.html')

# --- API Routes ---
@app.route('/api/register', methods=['POST'])
def api_register():
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

    if check_login(email, password):
        return jsonify({'success': True, 'message': '✅ Login successful!'})
    else:
        return jsonify({'success': False, 'errors': ['❌ Invalid email or password']}), 401

# --- Other Endpoints ---
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    bot_reply = f"🤖 You said: '{user_message}'"
    return jsonify({'reply': bot_reply})

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_type = request.form['type']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    tag = 'rfp' if file_type == 'document' else 'rfi'
    files_list.append({'name': file.filename, 'tag': tag})
    return jsonify({'reply': f"✅ File '{file.filename}' uploaded successfully."})

@app.route('/files')
def files():
    return jsonify(files_list)

@app.route('/logout')
def logout():
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, port=5050)

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # <-- Add this line after creating your Flask app


