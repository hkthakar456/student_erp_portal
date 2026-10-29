from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, get_current_user, validate_csrf

attendance_bp = Blueprint("attendance", __name__)

ATTENDANCE_STATUSES = ["Present", "Late", "Absent", "Excused"]

@attendance_bp.route("/")
@login_required
def index():
    repo = get_repo()
    user = get_current_user()

    student_id = request.args.get("student_id", type=int)
    course_id = request.args.get("course_id", type=int)
    date_filter = request.args.get("date", "").strip()

    # If logged-in user is a student, constrain view to their own attendance
    if user and user.get("role") == "student" and user.get("student_id"):
        student_id = user["student_id"]

    records = repo.list_attendance(
        student_id=student_id if student_id else None,
        course_id=course_id if course_id else None,
        date_str=date_filter if date_filter else None
    )

    students = repo.list_students(status="Active")
    courses = repo.list_courses()

    # If student is selected or logged in, get their summary
    summary = None
    if student_id:
        summary = repo.get_student_attendance_summary(student_id)

    today_str = date.today().isoformat()

    return render_template(
        "attendance/index.html",
        records=records,
        students=students,
        courses=courses,
        selected_student_id=student_id,
        selected_course_id=course_id,
        selected_date=date_filter,
        summary=summary,
        statuses=ATTENDANCE_STATUSES,
        today_str=today_str
    )

@attendance_bp.route("/record", methods=["POST"])
@admin_required
def record():
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("attendance.index"))

    student_id = request.form.get("student_id", type=int)
    course_id = request.form.get("course_id", type=int)
    date_str = request.form.get("date", "").strip()
    status = request.form.get("status", "").strip()
    remarks = request.form.get("remarks", "").strip()

    if not student_id or not course_id or not date_str or not status:
        flash("Please provide student, course, date, and attendance status.", "warning")
        return redirect(url_for("attendance.index"))

    if status not in ATTENDANCE_STATUSES:
        flash("Invalid attendance status.", "danger")
        return redirect(url_for("attendance.index"))

    repo = get_repo()
    repo.record_attendance(student_id, course_id, date_str, status, remarks)
    flash("Attendance record saved successfully.", "success")
    return redirect(url_for("attendance.index", student_id=student_id, course_id=course_id))
