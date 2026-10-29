from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import get_repo
from ..services.auth_service import login_required, admin_required, validate_csrf

students_bp = Blueprint("students", __name__)

PROGRAMS = [
    "Computer Science (B.Sc.)",
    "Data Science (B.Sc.)",
    "Information Technology (B.Sc.)",
    "Software Engineering (M.Sc.)",
    "Electrical Engineering (B.Sc.)"
]

YEAR_LEVELS = ["Year 1 (Freshman)", "Year 2 (Sophomore)", "Year 3 (Junior)", "Year 4 (Senior)"]

@students_bp.route("/")
@login_required
def index():
    repo = get_repo()
    query = request.args.get("q", "").strip()
    program = request.args.get("program", "All")
    year_level = request.args.get("year", "All")
    status = request.args.get("status", "All")

    students = repo.list_students(
        query=query if query else None,
        program=program if program != "All" else None,
        year_level=year_level if year_level != "All" else None,
        status=status if status != "All" else None
    )

    return render_template(
        "students/list.html",
        students=students,
        query=query,
        selected_program=program,
        selected_year=year_level,
        selected_status=status,
        programs=PROGRAMS,
        year_levels=YEAR_LEVELS
    )

@students_bp.route("/<int:student_id>")
@login_required
def detail(student_id: int):
    repo = get_repo()
    student = repo.get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students.index"))

    enrollments = repo.get_enrollments_for_student(student_id)
    attendance_summary = repo.get_student_attendance_summary(student_id)
    attendance_records = repo.list_attendance(student_id=student_id)[:10]
    grades_summary = repo.get_student_grade_summary(student_id)
    available_courses = repo.list_courses()

    # Filter out courses student is already enrolled in
    enrolled_course_ids = {e["course_id"] for e in enrollments if e["enrollment_status"] == "Enrolled"}
    unenrolled_courses = [c for c in available_courses if c["id"] not in enrolled_course_ids]

    return render_template(
        "students/detail.html",
        student=student,
        enrollments=enrollments,
        attendance_summary=attendance_summary,
        attendance_records=attendance_records,
        grades_summary=grades_summary,
        unenrolled_courses=unenrolled_courses
    )

@students_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create():
    repo = get_repo()
    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid).", "danger")
            return redirect(url_for("students.create"))

        student_id_code = request.form.get("student_id_code", "").strip().upper()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        program = request.form.get("program", "").strip()
        year_level = request.form.get("year_level", "").strip()
        status = request.form.get("status", "Active")
        gpa = request.form.get("gpa", "0.0").strip()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        address = request.form.get("address", "").strip()

        # Validation
        if not student_id_code or not first_name or not last_name or not email or not program or not year_level:
            flash("Please fill in all required fields (ID Code, First & Last Name, Email, Program, Year).", "warning")
            return render_template("students/form.html", student=request.form, is_edit=False, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        # Check unique constraints
        if repo.get_student_by_code(student_id_code):
            flash(f"Student ID Code '{student_id_code}' is already assigned to another student.", "danger")
            return render_template("students/form.html", student=request.form, is_edit=False, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        existing_students = repo.list_students(query=email)
        if any(s["email"].lower() == email.lower() for s in existing_students):
            flash(f"A student with email '{email}' already exists.", "danger")
            return render_template("students/form.html", student=request.form, is_edit=False, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        try:
            gpa_float = float(gpa) if gpa else 0.0
            if gpa_float < 0.0 or gpa_float > 4.0:
                raise ValueError
        except ValueError:
            flash("GPA must be a valid number between 0.00 and 4.00.", "warning")
            return render_template("students/form.html", student=request.form, is_edit=False, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        new_id = repo.create_student({
            "student_id_code": student_id_code,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "program": program,
            "year_level": year_level,
            "status": status,
            "gpa": gpa_float,
            "date_of_birth": date_of_birth,
            "address": address
        })

        flash(f"Student record for {first_name} {last_name} ({student_id_code}) successfully created.", "success")
        return redirect(url_for("students.detail", student_id=new_id))

    return render_template("students/form.html", student={}, is_edit=False, programs=PROGRAMS, year_levels=YEAR_LEVELS)

@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(student_id: int):
    repo = get_repo()
    student = repo.get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students.index"))

    if request.method == "POST":
        csrf_token = request.form.get("csrf_token")
        if not validate_csrf(csrf_token):
            flash("Security check failed (CSRF token invalid).", "danger")
            return redirect(url_for("students.edit", student_id=student_id))

        student_id_code = request.form.get("student_id_code", "").strip().upper()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        program = request.form.get("program", "").strip()
        year_level = request.form.get("year_level", "").strip()
        status = request.form.get("status", "Active")
        gpa = request.form.get("gpa", "0.0").strip()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        address = request.form.get("address", "").strip()

        if not student_id_code or not first_name or not last_name or not email or not program or not year_level:
            flash("Please fill in all required fields.", "warning")
            return render_template("students/form.html", student=request.form, is_edit=True, student_id=student_id, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        existing_code_student = repo.get_student_by_code(student_id_code)
        if existing_code_student and existing_code_student["id"] != student_id:
            flash(f"Student ID Code '{student_id_code}' is in use by another record.", "danger")
            return render_template("students/form.html", student=request.form, is_edit=True, student_id=student_id, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        try:
            gpa_float = float(gpa) if gpa else 0.0
            if gpa_float < 0.0 or gpa_float > 4.0:
                raise ValueError
        except ValueError:
            flash("GPA must be a valid number between 0.00 and 4.00.", "warning")
            return render_template("students/form.html", student=request.form, is_edit=True, student_id=student_id, programs=PROGRAMS, year_levels=YEAR_LEVELS)

        repo.update_student(student_id, {
            "student_id_code": student_id_code,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "program": program,
            "year_level": year_level,
            "status": status,
            "gpa": gpa_float,
            "date_of_birth": date_of_birth,
            "address": address
        })

        flash(f"Student profile for {first_name} {last_name} updated successfully.", "success")
        return redirect(url_for("students.detail", student_id=student_id))

    return render_template("students/form.html", student=student, is_edit=True, student_id=student_id, programs=PROGRAMS, year_levels=YEAR_LEVELS)

@students_bp.route("/<int:student_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_status(student_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("students.detail", student_id=student_id))

    repo = get_repo()
    student = repo.get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students.index"))

    new_status = "Inactive" if student["status"] == "Active" else "Active"
    repo.toggle_student_status(student_id, new_status)
    flash(f"Student status changed to {new_status}.", "info")
    return redirect(url_for("students.detail", student_id=student_id))

@students_bp.route("/<int:student_id>/enroll", methods=["POST"])
@admin_required
def enroll(student_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("students.detail", student_id=student_id))

    course_id = request.form.get("course_id", type=int)
    if not course_id:
        flash("Please select a valid course.", "warning")
        return redirect(url_for("students.detail", student_id=student_id))

    repo = get_repo()
    if repo.is_student_enrolled(student_id, course_id):
        flash("Student is already actively enrolled in this course.", "warning")
        return redirect(url_for("students.detail", student_id=student_id))

    repo.enroll_student(student_id, course_id)
    flash("Student successfully enrolled in course.", "success")
    return redirect(url_for("students.detail", student_id=student_id))

@students_bp.route("/<int:student_id>/withdraw/<int:enrollment_id>", methods=["POST"])
@admin_required
def withdraw(student_id: int, enrollment_id: int):
    csrf_token = request.form.get("csrf_token")
    if not validate_csrf(csrf_token):
        flash("Security token verification failed.", "danger")
        return redirect(url_for("students.detail", student_id=student_id))

    repo = get_repo()
    repo.withdraw_student(enrollment_id)
    flash("Course enrollment withdrawn.", "info")
    return redirect(url_for("students.detail", student_id=student_id))
