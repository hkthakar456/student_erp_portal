from flask import Blueprint, render_template
from .. import get_repo
from ..services.auth_service import login_required, get_current_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def index():
    repo = get_repo()
    user = get_current_user()
    stats = repo.get_dashboard_stats()
    announcements = repo.list_announcements(limit=5)
    
    # If the user is a student, fetch their specific summary details
    student_info = None
    student_enrollments = []
    student_attendance = None
    student_grades = None

    if user and user.get("role") == "student" and user.get("student_id"):
        student_id = user["student_id"]
        student_info = repo.get_student_by_id(student_id)
        student_enrollments = repo.get_enrollments_for_student(student_id)
        student_attendance = repo.get_student_attendance_summary(student_id)
        student_grades = repo.get_student_grade_summary(student_id)

    # Recent feedback for admin view
    recent_feedback = []
    if user and user.get("role") == "admin":
        recent_feedback = repo.list_feedback()[:4]

    return render_template(
        "dashboard.html",
        stats=stats,
        announcements=announcements,
        student_info=student_info,
        student_enrollments=student_enrollments,
        student_attendance=student_attendance,
        student_grades=student_grades,
        recent_feedback=recent_feedback
    )
