import sqlite3
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, is_admin=0):
        self.id = id
        self.email = email
        self.password = password
        self.is_admin = bool(is_admin)

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    conn = get_db_connection(db_path)
    
    # Simple table without email verification
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)
    
    # Create default admin user
    admin_email = "admin@forexpro.com"
    admin_password = "admin123"
    
    existing_admin = conn.execute("SELECT id FROM user WHERE email = ?", (admin_email,)).fetchone()
    if not existing_admin:
        conn.execute("INSERT INTO user (email, password, is_admin) VALUES (?, ?, ?)", 
                    (admin_email, admin_password, 1))
    
    conn.commit()
    conn.close()

def create_user(db_path, email, password):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO user (email, password, is_admin) VALUES (?, ?, ?)", (email, password, 0))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def get_user_by_email(db_path, email):
    conn = get_db_connection(db_path)
    row = conn.execute("SELECT id, email, password, is_admin FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        return User(row["id"], row["email"], row["password"], row["is_admin"])
    return None

def get_user_by_id(db_path, user_id):
    conn = get_db_connection(db_path)
    row = conn.execute("SELECT id, email, password, is_admin FROM user WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row["id"], row["email"], row["password"], row["is_admin"])
    return None

def get_all_users(db_path):
    conn = get_db_connection(db_path)
    users = conn.execute("SELECT id, email, is_admin FROM user ORDER BY id").fetchall()
    conn.close()
    return [{"id": row["id"], "email": row["email"], "is_admin": bool(row["is_admin"])} for row in users]

def delete_user(db_path, user_id):
    conn = get_db_connection(db_path)
    conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def toggle_admin_status(db_path, user_id):
    conn = get_db_connection(db_path)
    user = conn.execute("SELECT is_admin FROM user WHERE id = ?", (user_id,)).fetchone()
    if user:
        new_status = 0 if user["is_admin"] == 1 else 1
        conn.execute("UPDATE user SET is_admin = ? WHERE id = ?", (new_status, user_id))
        conn.commit()
    conn.close()

def verify_password(plain_password, stored_password):
    return plain_password == stored_password

def generate_verification_token():
    import secrets
    return secrets.token_urlsafe(32)

def verify_user_email(db_path, token):
    conn = get_db_connection(db_path)
    user = conn.execute("SELECT id FROM user WHERE verification_token = ?", (token,)).fetchone()
    if user:
        conn.execute("UPDATE user SET is_verified = 1, verification_token = NULL WHERE id = ?", (user['id'],))
        conn.commit()
    conn.close()
    return True
    conn.close()
    return False

def send_verification_email(email, token):
    # In production, you'd use actual email service like SendGrid, AWS SES, etc.
    # For now, we'll just print the verification link
    verification_link = f"http://127.0.0.1:5000/verify/{token}"
    print(f" Email verification link for {email}: {verification_link}")
    print("In production, this would be sent via email service")
    return True
