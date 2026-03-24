from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import init_db, get_user_by_email, get_user_by_id, create_user, verify_password, User, get_db_connection, get_all_users, delete_user, toggle_admin_status
import re
import datetime
import time
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "replace-with-secure-random-value"
app.config["DATABASE"] = "/tmp/forexpro.sqlite"

# Initialize bcrypt
bcrypt = Bcrypt(app)

# Initialize database immediately when app starts
init_db(app.config["DATABASE"])

login_manager = LoginManager(app)
login_manager.login_view = "login"

email_re = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(app.config["DATABASE"], int(user_id))

@app.before_request
def setup():
    if not hasattr(app, '_db_initialized'):
        init_db(app.config["DATABASE"])
        app._db_initialized = True

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
        create_user(app.config["DATABASE"], email, password)
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

@app.route("/api/users")
@login_required
def get_all_users_api():
    # Only admins can view all users
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    users = get_all_users(app.config["DATABASE"])
    return jsonify(users)

@app.route("/api/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
def admin_delete_user(user_id):
    # Only admins can delete users
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    delete_user(app.config["DATABASE"], user_id)
    return jsonify({"success": True, "message": "User deleted successfully"})

@app.route("/api/admin/toggle-admin/<int:user_id>", methods=["POST"])
@login_required
def admin_toggle_admin(user_id):
    # Only admins can toggle admin status
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    # Prevent admin from removing their own admin status
    if user_id == current_user.id:
        return jsonify({"error": "Cannot modify your own admin status"}), 400
    
    toggle_admin_status(app.config["DATABASE"], user_id)
    return jsonify({"success": True, "message": "Admin status updated successfully"})

@app.route("/auth/google")
def google_auth():
    """Simulate Google OAuth - in production this would redirect to actual Google OAuth"""
    # Store a mock state for security
    session['oauth_state'] = 'google_auth_' + str(int(time.time()))
    flash("Redirecting to Google OAuth...", "info")
    return redirect(url_for('google_callback'))

@app.route("/auth/google/callback")
def google_callback():
    """Simulate Google OAuth callback - in production this would handle real Google response"""
    # Simulate successful Google OAuth
    mock_google_user = {
        'email': 'user@gmail.com',
        'name': 'Google User',
        'id': 'google_' + str(int(time.time()))
    }
    
    # Check if user already exists
    existing_user = get_user_by_email(app.config["DATABASE"], mock_google_user['email'])
    
    if existing_user:
        login_user(existing_user)
        flash(f"Welcome back, {existing_user.email}!", "success")
    else:
        # Create new user from Google data
        pw_hash = bcrypt.generate_password_hash('google_oauth_user').decode("utf-8")
        user_id = create_user(app.config["DATABASE"], mock_google_user['email'], pw_hash)
        user = get_user_by_id(app.config["DATABASE"], user_id)
        login_user(user)
        flash(f"Account created for {mock_google_user['email']} via Google!", "success")
    
    return redirect(url_for('dashboard'))

@app.route("/api/database-info")
@login_required
def get_database_info():
    conn = get_db_connection(app.config["DATABASE"])
    user_count = conn.execute("SELECT COUNT(*) as count FROM user").fetchone()["count"]
    conn.close()
    
    return jsonify({
        "total_users": user_count,
        "database_path": app.config["DATABASE"],
        "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "flask_version": Flask.__version__
    })

if __name__ == "__main__":
    import socket
    
    # Get local IP address for network access
    def get_local_ip():
        try:
            # Connect to an external host to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    print(f"🚀 ForexPro Server Starting...")
    print(f"📱 Local access: http://127.0.0.1:5000")
    print(f"🌐 Network access: http://{local_ip}:5000")
    print(f"🌍 FOR PUBLIC ACCESS: Configure port forwarding on your router!")
    print(f"💡 Or deploy to cloud services like Heroku, PythonAnywhere, etc.")
    
    # Bind to all interfaces for public access
    app.run(debug=False, host='0.0.0.0', port=5000)

# Vercel serverless handler - expose the Flask app
# The app variable is already defined above and ready for Vercel
