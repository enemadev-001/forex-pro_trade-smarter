import os
import sqlite3
import re
import time
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt

# 1. Initialize Flask and Bcrypt
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_now")
bcrypt = Bcrypt(app)

# 2. Vercel Database Configuration
app.config["DATABASE"] = "/tmp/forexpro.sqlite"

login_manager = LoginManager(app)
login_manager.login_view = "login"

# Regular expression for email validation
email_re = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

# --- DATABASE HELPER FUNCTIONS ---

class User(UserMixin):
    def __init__(self, id, email, password, is_admin):
        self.id = id
        self.email = email
        self.password = password
        self.is_admin = bool(is_admin)

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    conn = get_db_connection(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    admin_exists = conn.execute("SELECT * FROM user WHERE email = ?", ('admin@forexpro.com',)).fetchone()
    if not admin_exists:
        pw_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        conn.execute("INSERT INTO user (email, password, is_admin) VALUES (?, ?, ?)",
                     ('admin@forexpro.com', pw_hash, 1))
    conn.commit()
    conn.close()

def get_user_by_email(db_path, email):
    conn = get_db_connection(db_path)
    user_data = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['password'], user_data['is_admin'])
    return None

def get_user_by_id(db_path, user_id):
    conn = get_db_connection(db_path)
    user_data = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['password'], user_data['is_admin'])
    return None

def create_user(db_path, email, password_hash):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user (email, password) VALUES (?, ?)", (email, password_hash))
    conn.commit()
    user_id = cursor.lastrow_id
    conn.close()
    return user_id

def verify_password(pw_hash, pw_plain):
    return bcrypt.check_password_hash(pw_hash, pw_plain)

# 3. Database Initialization (Global Scope)
with app.app_context():
    init_db(app.config["DATABASE"])

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(app.config["DATABASE"], int(user_id))

# --- ROUTES ---

@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/home")
def home():
    return render_template("index.html", user=current_user)

@app.route("/academy")
def academy():
    return render_template("academy.html", user=current_user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("signup"))
        if not email_re.match(email):
            flash("Invalid email format.", "danger")
            return redirect(url_for("signup"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("signup"))
        if get_user_by_email(app.config["DATABASE"], email):
            flash("Email already registered.", "danger")
            return redirect(url_for("signup"))
        
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        create_user(app.config["DATABASE"], email, pw_hash)
        flash("Account created! Log in below.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(app.config["DATABASE"], email)
        
        if user and verify_password(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# --- AUTH FIX FOR HTML BUILDERROR ---

@app.route("/auth/google")
def google_auth():
    return redirect(url_for('google_callback'))

@app.route("/auth/google/callback")
def google_callback():
    mock_email = 'user@gmail.com'
    user = get_user_by_email(app.config["DATABASE"], mock_email)
    if not user:
        pw_hash = bcrypt.generate_password_hash('google_user').decode("utf-8")
        create_user(app.config["DATABASE"], mock_email, pw_hash)
        user = get_user_by_email(app.config["DATABASE"], mock_email)
    login_user(user)
    return redirect(url_for('dashboard'))

# 4. Vercel Entry Point
app = app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)