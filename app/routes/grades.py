from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, get_current_user, validate_csrf

grades_bp = Blueprint("grades", __name__)

@grades_bp.route("/")
@login_required
def index():
    repo = get_repo()
    user = get_current_user()

    student_id = request.args.get("student_id", type=int)
    course_id = request.args.get("course_id", type=int)

    # Restrict student users to only their own grades
    if user and user.get("role") == "student" and user.get("student_id"):
        student_id = user["student_id"]

    grades = repo.list_grades(
        student_id=student_id if student_id else None,
        course_id=course_id if course_id else None
    )

    students = repo.list_students(status="Active")
    courses = repo.list_courses()

    summary = None
    if student_id:
        summary = repo.get_student_grade_summary(student_id)

    return render_template(
        "grades/index.html",
        grades=grades,
        students=students,
        courses=courses,
        selected_student_id=student_id,
        selected_course_id=course_id,
        summary=summary
    )

@grades_bp.route("/record", methods=["POST"])
@admin_required
def record():
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("grades.index"))

    student_id = request.form.get("student_id", type=int)
    course_id = request.form.get("course_id", type=int)
    assessment_name = request.form.get("assessment_name", "").strip()
    score_val = request.form.get("score", "").strip()
    max_score_val = request.form.get("max_score", "").strip()
    weight_val = request.form.get("weight_percentage", "0").strip()
    remarks = request.form.get("remarks", "").strip()

    if not student_id or not course_id or not assessment_name or not score_val or not max_score_val:
        flash("Please provide all required fields (Student, Course, Assessment, Score, Max Score).", "warning")
        return redirect(url_for("grades.index"))

    try:
        score = float(score_val)
        max_score = float(max_score_val)
        weight = float(weight_val or 0.0)

        if max_score <= 0:
            flash("Max score must be greater than zero.", "warning")
            return redirect(url_for("grades.index"))

        if score < 0 or score > max_score:
            flash(f"Score ({score}) cannot be negative or exceed the maximum score ({max_score}).", "warning")
            return redirect(url_for("grades.index"))

    except ValueError:
        flash("Score, Max Score, and Weight must be valid numbers.", "warning")
        return redirect(url_for("grades.index"))

    repo = get_repo()
    repo.record_grade(student_id, course_id, assessment_name, score, max_score, weight, remarks)
    flash(f"Grade for '{assessment_name}' recorded successfully ({score}/{max_score}).", "success")
    return redirect(url_for("grades.index", student_id=student_id, course_id=course_id))
