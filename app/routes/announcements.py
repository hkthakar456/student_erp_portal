from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, get_current_user, validate_csrf

announcements_bp = Blueprint("announcements", __name__)

CATEGORIES = ["Academic", "Event", "Alert", "General"]

@announcements_bp.route("/")
@login_required
def index():
    repo = get_repo()
    category = request.args.get("category", "All")
    announcements = repo.list_announcements(
        category=category if category != "All" else None
    )
    return render_template(
        "announcements/index.html",
        announcements=announcements,
        selected_category=category,
        categories=CATEGORIES
    )

@announcements_bp.route("/new", methods=["POST"])
@admin_required
def create():
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("announcements.index"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "General").strip()
    is_pinned = bool(request.form.get("is_pinned"))

    user = get_current_user()
    author_name = "Campus Administration"

    if not title or not content:
        flash("Title and content are required.", "warning")
        return redirect(url_for("announcements.index"))

    repo = get_repo()
    repo.create_announcement(title, content, category, author_name, is_pinned=is_pinned)
    flash("Campus announcement published successfully.", "success")
    return redirect(url_for("announcements.index"))

@announcements_bp.route("/<int:announcement_id>/delete", methods=["POST"])
@admin_required
def delete(announcement_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("announcements.index"))

    repo = get_repo()
    repo.delete_announcement(announcement_id)
    flash("Announcement deleted.", "info")
    return redirect(url_for("announcements.index"))
