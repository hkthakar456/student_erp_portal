from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, get_current_user, validate_csrf

feedback_bp = Blueprint("feedback", __name__)

CATEGORIES = ["Academics", "Facilities & Housing", "IT & Portal Support", "Student Life", "General Inquiry"]
STATUSES = ["Open", "In Progress", "Resolved"]

@feedback_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    repo = get_repo()
    user = get_current_user()

    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid).", "danger")
            return redirect(url_for("feedback.index"))

        category = request.form.get("category", "").strip()
        message = request.form.get("message", "").strip()
        contact_email = request.form.get("contact_email", "").strip() or (user["email"] if user else None)

        if not category or not message:
            flash("Please choose a category and enter your message.", "warning")
            return render_template("feedback/index.html", categories=CATEGORIES, prefill_email=contact_email)

        repo.create_feedback(category, message, contact_email)
        flash("Thank you! Your feedback has been submitted to campus administration.", "success")
        return redirect(url_for("feedback.index"))

    # For students or users submitting
    prefill_email = user["email"] if user else ""
    return render_template("feedback/index.html", categories=CATEGORIES, prefill_email=prefill_email)

@feedback_bp.route("/admin", methods=["GET"])
@admin_required
def admin_list():
    repo = get_repo()
    status_filter = request.args.get("status", "All")
    feedback_items = repo.list_feedback(status=status_filter if status_filter != "All" else None)
    return render_template(
        "feedback/admin.html",
        feedback_items=feedback_items,
        selected_status=status_filter,
        statuses=STATUSES
    )

@feedback_bp.route("/<int:feedback_id>/status", methods=["POST"])
@admin_required
def update_status(feedback_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("feedback.admin_list"))

    new_status = request.form.get("status", "").strip()
    admin_response = request.form.get("admin_response", "").strip()

    if new_status not in STATUSES:
        flash("Invalid status value.", "danger")
        return redirect(url_for("feedback.admin_list"))

    repo = get_repo()
    repo.update_feedback_status(feedback_id, new_status, admin_response)
    flash(f"Feedback ticket #{feedback_id} status updated to '{new_status}'.", "success")
    return redirect(url_for("feedback.admin_list"))
