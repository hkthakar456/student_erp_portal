import os
from flask import Flask, render_template, current_app
from .config import config_by_name
from .repositories.sqlite_repo import SQLiteRepository
from .services.auth_service import (
    get_current_user, is_admin, is_student, generate_csrf_token
)

def get_repo() -> SQLiteRepository:
    """Convenience helper to retrieve the active repository from current_app."""
    return current_app.repository

def create_app(config_name: str = "default", config_override: dict = None) -> Flask:
    """Application factory for the Student Management Portal."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    cfg = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(cfg)

    if config_override:
        app.config.update(config_override)

    # Initialize persistence repository
    repo = SQLiteRepository(app.config["DATABASE_PATH"])
    repo.init_db()
    app.repository = repo

    # Context processors for all Jinja templates
    @app.context_processor
    def inject_context():
        return {
            "current_user": get_current_user(),
            "is_admin": is_admin(),
            "is_student": is_student(),
            "csrf_token": generate_csrf_token,
            "active_term": "Fall 2026",
            "app_title": "Beacon ERP - Student Management Portal"
        }

    # Template filters
    @app.template_filter("status_badge")
    def status_badge_filter(status: str) -> str:
        mapping = {
            "Active": "badge-success",
            "Inactive": "badge-secondary",
            "Enrolled": "badge-primary",
            "Completed": "badge-success",
            "Dropped": "badge-danger",
            "Present": "badge-success",
            "Late": "badge-warning",
            "Absent": "badge-danger",
            "Excused": "badge-info",
            "Open": "badge-warning",
            "In Progress": "badge-info",
            "Resolved": "badge-success",
        }
        return mapping.get(status, "badge-secondary")

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.students import students_bp
    from .routes.courses import courses_bp
    from .routes.attendance import attendance_bp
    from .routes.grades import grades_bp
    from .routes.announcements import announcements_bp
    from .routes.feedback import feedback_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(grades_bp, url_prefix="/grades")
    app.register_blueprint(announcements_bp, url_prefix="/announcements")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    return app
