import os
import sqlite3
import re
import time
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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

# 3. Database Initialization (Global Scope)
# This replaces the problematic @app.before_request block
with app.app_context():
    try:
        # Assuming these helper functions are defined in your other files or below
        init_db(app.config["DATABASE"])
    except NameError:
        print("Note: init_db function not found. Ensure helper functions are included.")

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
        
        # Create user
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        create_user(app.config["DATABASE"], email, pw_hash)
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("login"))
        user = get_user_by_email(app.config["DATABASE"], email)
        if not user or not verify_password(password, user.password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out safely.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

# --- API & AUTH ---

@app.route("/auth/google/callback")
def google_callback():
    mock_google_user = {'email': 'user@gmail.com'}
    existing_user = get_user_by_email(app.config["DATABASE"], mock_google_user['email'])
    
    if existing_user:
        login_user(existing_user)
    else:
        pw_hash = bcrypt.generate_password_hash('google_oauth_user').decode("utf-8")
        user_id = create_user(app.config["DATABASE"], mock_google_user['email'], pw_hash)
        user = get_user_by_id(app.config["DATABASE"], user_id)
        login_user(user)
    
    return redirect(url_for('dashboard'))

# 4. Vercel Entry Point
app = app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)