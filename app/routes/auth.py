from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_user, logout_user, verify_password, validate_csrf

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid). Please try again.", "danger")
            return redirect(url_for("auth.login"))

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("auth/login.html", email=email)

        repo = get_repo()
        user = repo.get_user_by_email(email)

        if user and verify_password(user["password_hash"], password):
            login_user(user)
            flash(f"Welcome back! Signed in as {user['email']} ({user['role'].title()}).", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid email or password. Please use the documented demo credentials below.", "danger")
            return render_template("auth/login.html", email=email)

    return render_template("auth/login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))
