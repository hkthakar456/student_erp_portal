import secrets
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, current_app
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Safely hash passwords using pbkdf2:sha256."""
    return generate_password_hash(password, method="pbkdf2:sha256")

def verify_password(password_hash: str, password: str) -> bool:
    """Verify password against stored hash."""
    return check_password_hash(password_hash, password)

def login_user(user: dict) -> None:
    """Stores user information in the session."""
    session.clear()
    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["role"] = user["role"]
    session["student_id"] = user.get("student_id")
    session["logged_in"] = True
    # Fresh CSRF token on login
    generate_csrf_token()

def logout_user() -> None:
    """Clears the session."""
    session.clear()

def get_current_user() -> dict:
    """Returns the current logged-in user dictionary from session if present."""
    if session.get("logged_in"):
        return {
            "id": session.get("user_id"),
            "email": session.get("email"),
            "role": session.get("role"),
            "student_id": session.get("student_id")
        }
    return None

def is_admin() -> bool:
    return session.get("role") == "admin"

def is_student() -> bool:
    return session.get("role") == "student"

def generate_csrf_token() -> str:
    """Generates and stores a CSRF token in the session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def validate_csrf(token: str) -> bool:
    """Validates the CSRF token against the session token."""
    session_token = session.get("_csrf_token")
    if not session_token or not token:
        return False
    return secrets.compare_digest(session_token, token)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please sign in with administrator credentials.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        if session.get("role") != "admin":
            flash("Access denied. Administrator privileges are required for this action.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function
