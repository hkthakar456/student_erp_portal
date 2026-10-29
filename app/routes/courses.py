from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, validate_csrf

courses_bp = Blueprint("courses", __name__)

DEPARTMENTS = [
    "Computer Science",
    "Data Science & AI",
    "Information Technology",
    "Software Engineering",
    "Mathematics & Statistics"
]

TERMS = ["Fall 2026", "Spring 2027", "Summer 2027"]

@courses_bp.route("/")
@login_required
def index():
    repo = get_repo()
    department = request.args.get("department", "All")
    courses = repo.list_courses(department=department if department != "All" else None)
    return render_template(
        "courses/list.html",
        courses=courses,
        selected_dept=department,
        departments=DEPARTMENTS
    )

@courses_bp.route("/<int:course_id>")
@login_required
def detail(course_id: int):
    repo = get_repo()
    course = repo.get_course_by_id(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("courses.index"))

    enrollments = repo.get_enrollments_for_course(course_id)
    all_students = repo.list_students(status="Active")
    enrolled_student_ids = {e["student_id"] for e in enrollments}
    unenrolled_students = [s for s in all_students if s["id"] not in enrolled_student_ids]

    return render_template(
        "courses/detail.html",
        course=course,
        enrollments=enrollments,
        unenrolled_students=unenrolled_students
    )

@courses_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create():
    repo = get_repo()
    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid).", "danger")
            return redirect(url_for("courses.create"))

        code = request.form.get("code", "").strip().upper()
        title = request.form.get("title", "").strip()
        instructor = request.form.get("instructor", "").strip()
        credits_val = request.form.get("credits", "3").strip()
        term = request.form.get("term", "").strip()
        department = request.form.get("department", "").strip()
        capacity_val = request.form.get("capacity", "40").strip()
        description = request.form.get("description", "").strip()

        if not code or not title or not instructor or not term or not department:
            flash("Please fill in all required fields (Code, Title, Instructor, Term, Department).", "warning")
            return render_template("courses/form.html", course=request.form, is_edit=False, departments=DEPARTMENTS, terms=TERMS)

        if repo.get_course_by_code(code):
            flash(f"Course code '{code}' already exists.", "danger")
            return render_template("courses/form.html", course=request.form, is_edit=False, departments=DEPARTMENTS, terms=TERMS)

        try:
            credits_num = int(credits_val)
            capacity_num = int(capacity_val)
            if credits_num <= 0 or capacity_num <= 0:
                raise ValueError
        except ValueError:
            flash("Credits and Capacity must be positive whole numbers.", "warning")
            return render_template("courses/form.html", course=request.form, is_edit=False, departments=DEPARTMENTS, terms=TERMS)

        new_id = repo.create_course({
            "code": code,
            "title": title,
            "instructor": instructor,
            "credits": credits_num,
            "term": term,
            "department": department,
            "capacity": capacity_num,
            "description": description
        })

        flash(f"Course '{code} - {title}' created successfully.", "success")
        return redirect(url_for("courses.detail", course_id=new_id))

    return render_template("courses/form.html", course={}, is_edit=False, departments=DEPARTMENTS, terms=TERMS)

@courses_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(course_id: int):
    repo = get_repo()
    course = repo.get_course_by_id(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("courses.index"))

    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid).", "danger")
            return redirect(url_for("courses.edit", course_id=course_id))

        code = request.form.get("code", "").strip().upper()
        title = request.form.get("title", "").strip()
        instructor = request.form.get("instructor", "").strip()
        credits_val = request.form.get("credits", "3").strip()
        term = request.form.get("term", "").strip()
        department = request.form.get("department", "").strip()
        capacity_val = request.form.get("capacity", "40").strip()
        description = request.form.get("description", "").strip()

        if not code or not title or not instructor or not term or not department:
            flash("Please fill in all required fields.", "warning")
            return render_template("courses/form.html", course=request.form, is_edit=True, course_id=course_id, departments=DEPARTMENTS, terms=TERMS)

        existing_course = repo.get_course_by_code(code)
        if existing_course and existing_course["id"] != course_id:
            flash(f"Course code '{code}' is already used by another course.", "danger")
            return render_template("courses/form.html", course=request.form, is_edit=True, course_id=course_id, departments=DEPARTMENTS, terms=TERMS)

        try:
            credits_num = int(credits_val)
            capacity_num = int(capacity_val)
            if credits_num <= 0 or capacity_num <= 0:
                raise ValueError
        except ValueError:
            flash("Credits and Capacity must be positive whole numbers.", "warning")
            return render_template("courses/form.html", course=request.form, is_edit=True, course_id=course_id, departments=DEPARTMENTS, terms=TERMS)

        repo.update_course(course_id, {
            "code": code,
            "title": title,
            "instructor": instructor,
            "credits": credits_num,
            "term": term,
            "department": department,
            "capacity": capacity_num,
            "description": description
        })

        flash(f"Course '{code}' updated successfully.", "success")
        return redirect(url_for("courses.detail", course_id=course_id))

    return render_template("courses/form.html", course=course, is_edit=True, course_id=course_id, departments=DEPARTMENTS, terms=TERMS)

@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@admin_required
def enroll_student_to_course(course_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("courses.detail", course_id=course_id))

    student_id = request.form.get("student_id", type=int)
    if not student_id:
        flash("Please select a valid student.", "warning")
        return redirect(url_for("courses.detail", course_id=course_id))

    repo = get_repo()
    if repo.is_student_enrolled(student_id, course_id):
        flash("This student is already actively enrolled.", "warning")
        return redirect(url_for("courses.detail", course_id=course_id))

    repo.enroll_student(student_id, course_id)
    flash("Student enrolled into course roster.", "success")
    return redirect(url_for("courses.detail", course_id=course_id))

@courses_bp.route("/<int:course_id>/withdraw/<int:enrollment_id>", methods=["POST"])
@admin_required
def withdraw_student_from_course(course_id: int, enrollment_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("courses.detail", course_id=course_id))

    repo = get_repo()
    repo.withdraw_student(enrollment_id)
    flash("Student removed from course roster.", "info")
    return redirect(url_for("courses.detail", course_id=course_id))
