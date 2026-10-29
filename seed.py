import os
from datetime import date, timedelta
from app.config import Config
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.auth_service import hash_password

def seed_database(db_path: str = None, repo: SQLiteRepository = None):
    if repo is None:
        target_path = db_path or Config.DATABASE_PATH
        print(f"[Seed] Initializing SQLite database at: {target_path}")
        repo = SQLiteRepository(target_path)
    repo.init_db()

    conn = repo.get_connection()
    try:
        with conn:
            # Clear existing data for fresh, repeatable seed
            conn.execute("DELETE FROM feedback")
            conn.execute("DELETE FROM announcements")
            conn.execute("DELETE FROM grades")
            conn.execute("DELETE FROM attendance")
            conn.execute("DELETE FROM enrollments")
            conn.execute("DELETE FROM courses")
            conn.execute("DELETE FROM users")
            conn.execute("DELETE FROM students")
            conn.execute("DELETE FROM sqlite_sequence")
    finally:
        if repo._memory_conn is None:
            conn.close()

    print("[Seed] Populating fictional students...")
    students_data = [
        {
            "student_id_code": "STU-2024-001",
            "first_name": "Alex",
            "last_name": "Rivers",
            "email": "alex.rivers@campus.edu",
            "phone": "+1 (555) 019-2831",
            "program": "Computer Science (B.Sc.)",
            "year_level": "Year 3 (Junior)",
            "status": "Active",
            "gpa": 3.82,
            "date_of_birth": "2003-04-14",
            "address": "402 University Crest, Apt 3B, Tech City"
        },
        {
            "student_id_code": "STU-2024-002",
            "first_name": "Sophia",
            "last_name": "Chen",
            "email": "sophia.chen@campus.edu",
            "phone": "+1 (555) 019-8472",
            "program": "Data Science (B.Sc.)",
            "year_level": "Year 2 (Sophomore)",
            "status": "Active",
            "gpa": 3.91,
            "date_of_birth": "2004-09-22",
            "address": "128 Oakwood Blvd, Tech City"
        },
        {
            "student_id_code": "STU-2024-003",
            "first_name": "Marcus",
            "last_name": "Johnson",
            "email": "marcus.j@campus.edu",
            "phone": "+1 (555) 018-3721",
            "program": "Software Engineering (M.Sc.)",
            "year_level": "Year 4 (Senior)",
            "status": "Active",
            "gpa": 3.65,
            "date_of_birth": "2001-11-05",
            "address": "77 North Quadrangle, Tech City"
        },
        {
            "student_id_code": "STU-2024-004",
            "first_name": "Elena",
            "last_name": "Rostova",
            "email": "elena.rostova@campus.edu",
            "phone": "+1 (555) 017-9923",
            "program": "Computer Science (B.Sc.)",
            "year_level": "Year 1 (Freshman)",
            "status": "Active",
            "gpa": 3.75,
            "date_of_birth": "2005-02-18",
            "address": "Hall of Residence 2, Room 104"
        },
        {
            "student_id_code": "STU-2024-005",
            "first_name": "Jordan",
            "last_name": "Taylor",
            "email": "jordan.t@campus.edu",
            "phone": "+1 (555) 014-5511",
            "program": "Information Technology (B.Sc.)",
            "year_level": "Year 3 (Junior)",
            "status": "Active",
            "gpa": 3.42,
            "date_of_birth": "2003-07-30",
            "address": "512 Pinecrest Way, Tech City"
        },
        {
            "student_id_code": "STU-2024-006",
            "first_name": "Maya",
            "last_name": "Patel",
            "email": "maya.patel@campus.edu",
            "phone": "+1 (555) 012-7744",
            "program": "Data Science (B.Sc.)",
            "year_level": "Year 3 (Junior)",
            "status": "Active",
            "gpa": 3.88,
            "date_of_birth": "2003-12-10",
            "address": "33 Maple Court, Tech City"
        },
        {
            "student_id_code": "STU-2023-089",
            "first_name": "Liam",
            "last_name": "O'Connor",
            "email": "liam.oc@campus.edu",
            "phone": "+1 (555) 011-3329",
            "program": "Electrical Engineering (B.Sc.)",
            "year_level": "Year 2 (Sophomore)",
            "status": "Inactive",
            "gpa": 2.95,
            "date_of_birth": "2004-05-15",
            "address": "90 Cedar Street, Tech City"
        }
    ]

    student_id_map = {}
    for s in students_data:
        sid = repo.create_student(s)
        student_id_map[s["student_id_code"]] = sid

    print("[Seed] Creating demo user credentials...")
    admin_pw_hash = hash_password("AdminPass123!")
    student_pw_hash = hash_password("StudentPass123!")

    # Demo Admin
    repo.create_user("admin@campus.edu", admin_pw_hash, "admin", None)
    # Demo Student (Alex Rivers)
    repo.create_user("alex.rivers@campus.edu", student_pw_hash, "student", student_id_map["STU-2024-001"])
    # Demo Student 2 (Sophia Chen)
    repo.create_user("sophia.chen@campus.edu", student_pw_hash, "student", student_id_map["STU-2024-002"])

    print("[Seed] Populating courses...")
    courses_data = [
        {
            "code": "CS101",
            "title": "Introduction to Computer Science & Problem Solving",
            "instructor": "Dr. Sarah Mitchell",
            "credits": 4,
            "term": "Fall 2026",
            "department": "Computer Science",
            "capacity": 45,
            "description": "Fundamental concepts of computing, algorithmic thinking, data structures, and procedural programming in Python."
        },
        {
            "code": "CS201",
            "title": "Data Structures & Algorithm Analysis",
            "instructor": "Prof. David Vance",
            "credits": 4,
            "term": "Fall 2026",
            "department": "Computer Science",
            "capacity": 35,
            "description": "Detailed study of stacks, queues, trees, graphs, sorting, searching, and algorithmic complexity."
        },
        {
            "code": "CS301",
            "title": "Database Management Systems",
            "instructor": "Dr. Elena Ramirez",
            "credits": 3,
            "term": "Fall 2026",
            "department": "Information Technology",
            "capacity": 40,
            "description": "Relational algebra, SQL, indexing, transaction management, and introduction to modern document stores."
        },
        {
            "code": "CS350",
            "title": "Modern Web Systems & Cloud Architectures",
            "instructor": "Prof. Michael Sterling",
            "credits": 3,
            "term": "Fall 2026",
            "department": "Software Engineering",
            "capacity": 30,
            "description": "Client-server web development, REST APIs, session management, secure deployment, and scaling strategies."
        },
        {
            "code": "DS210",
            "title": "Foundations of Applied Data Science",
            "instructor": "Dr. Kavita Rao",
            "credits": 3,
            "term": "Fall 2026",
            "department": "Data Science & AI",
            "capacity": 35,
            "description": "Exploratory data analysis, statistical inference, regression modeling, and visualization libraries."
        },
        {
            "code": "SE401",
            "title": "Software Architecture & Quality Engineering",
            "instructor": "Prof. Alan Turing",
            "credits": 4,
            "term": "Fall 2026",
            "department": "Software Engineering",
            "capacity": 25,
            "description": "Design patterns, modular architectures, automated testing, continuous integration, and maintainability."
        }
    ]

    course_id_map = {}
    for c in courses_data:
        cid = repo.create_course(c)
        course_id_map[c["code"]] = cid

    print("[Seed] Enrolling students in courses...")
    alex_id = student_id_map["STU-2024-001"]
    sophia_id = student_id_map["STU-2024-002"]
    marcus_id = student_id_map["STU-2024-003"]
    elena_id = student_id_map["STU-2024-004"]
    jordan_id = student_id_map["STU-2024-005"]
    maya_id = student_id_map["STU-2024-006"]

    # Alex (CS Junior)
    repo.enroll_student(alex_id, course_id_map["CS201"])
    repo.enroll_student(alex_id, course_id_map["CS301"])
    repo.enroll_student(alex_id, course_id_map["CS350"])

    # Sophia (Data Science)
    repo.enroll_student(sophia_id, course_id_map["CS201"])
    repo.enroll_student(sophia_id, course_id_map["DS210"])

    # Marcus (SE Senior)
    repo.enroll_student(marcus_id, course_id_map["CS350"])
    repo.enroll_student(marcus_id, course_id_map["SE401"])

    # Elena (Freshman)
    repo.enroll_student(elena_id, course_id_map["CS101"])

    # Jordan & Maya
    repo.enroll_student(jordan_id, course_id_map["CS301"])
    repo.enroll_student(maya_id, course_id_map["DS210"])

    print("[Seed] Recording attendance sessions...")
    today = date.today()
    dates = [(today - timedelta(days=d)).isoformat() for d in [14, 11, 7, 4, 2]]

    # Alex attendance in CS201 and CS350
    for d in dates:
        repo.record_attendance(alex_id, course_id_map["CS201"], d, "Present", "On time")
        repo.record_attendance(alex_id, course_id_map["CS350"], d, "Present" if d != dates[2] else "Late", "Lab session")
        repo.record_attendance(sophia_id, course_id_map["CS201"], d, "Present", "Active participation")
        repo.record_attendance(marcus_id, course_id_map["SE401"], d, "Present", "Team presentation")

    # One excused absence for Alex in CS301
    repo.record_attendance(alex_id, course_id_map["CS301"], dates[1], "Excused", "Academic conference")
    repo.record_attendance(alex_id, course_id_map["CS301"], dates[3], "Present", "Lecture")

    print("[Seed] Recording sample grades...")
    # Alex CS201 grades
    repo.record_grade(alex_id, course_id_map["CS201"], "Assignment 1: Linked Lists & Stacks", 94.0, 100.0, 15.0, "Excellent test coverage")
    repo.record_grade(alex_id, course_id_map["CS201"], "Midterm Exam", 88.5, 100.0, 30.0, "Strong algorithm analysis section")
    repo.record_grade(alex_id, course_id_map["CS201"], "Quiz 1: Big-O Complexity", 19.0, 20.0, 5.0, "Perfect derivation")

    # Alex CS350 grades
    repo.record_grade(alex_id, course_id_map["CS350"], "Milestone 1: REST API Design", 98.0, 100.0, 20.0, "Very clean OpenAPI documentation")
    repo.record_grade(alex_id, course_id_map["CS350"], "Milestone 2: Auth & Session Management", 95.0, 100.0, 25.0, "Secure cookie flags properly implemented")

    # Sophia DS210 grades
    repo.record_grade(sophia_id, course_id_map["DS210"], "Exploratory Data Analysis Project", 96.0, 100.0, 25.0, "Outstanding visualizations")
    repo.record_grade(sophia_id, course_id_map["DS210"], "Midterm Statistical Exam", 91.0, 100.0, 35.0, "Solid hypothesis testing")

    # Marcus SE401 grades
    repo.record_grade(marcus_id, course_id_map["SE401"], "Architecture Spike & ADR Report", 92.0, 100.0, 20.0, "Clear architectural trade-offs")

    print("[Seed] Adding announcements...")
    repo.create_announcement(
        title="Welcome to Fall 2026 Semester at Beacon Campus",
        content="Classes commence this Monday. Please verify your course enrollments in the portal and consult your academic advisors for any add/drop schedule adjustments before Friday.",
        category="Academic",
        author_name="Office of Academic Affairs",
        is_pinned=True
    )
    repo.create_announcement(
        title="Annual Campus Tech & Innovation Hackathon Announced",
        content="Registration is now open for the 48-hour Autumn Hackathon scheduled for November 12-14. Teams of up to 4 students can register through the student activities desk.",
        category="Event",
        author_name="Student Association",
        is_pinned=True
    )
    repo.create_announcement(
        title="Main Library Extended Study Hours During Midterms",
        content="From October 25 to November 8, the university library East Wing will remain open 24/7 with complimentary coffee stations and quiet study pods.",
        category="General",
        author_name="Campus Facilities",
        is_pinned=False
    )
    repo.create_announcement(
        title="Scheduled Portal Maintenance Window",
        content="Brief maintenance will be conducted on Saturday between 02:00 AM and 03:30 AM EST. Access may experience temporary interruptions.",
        category="Alert",
        author_name="IT Systems Team",
        is_pinned=False
    )

    print("[Seed] Adding student feedback tickets...")
    repo.create_feedback(
        category="Facilities & Housing",
        message="The Wi-Fi access point in the 3rd floor study commons has intermittent packet loss during peak afternoon hours.",
        contact_email="alex.rivers@campus.edu"
    )
    fb2 = repo.create_feedback(
        category="Academics",
        message="Request for additional evening tutoring slots for CS201 Data Structures ahead of the midterm exam.",
        contact_email="elena.rostova@campus.edu"
    )
    repo.update_feedback_status(fb2, "In Progress", "Academic center has scheduled two additional TA review sessions on Tuesday & Thursday.")

    fb3 = repo.create_feedback(
        category="IT & Portal Support",
        message="Dark mode contrast ratio for table headers in the grade book view could be slightly adjusted for accessibility.",
        contact_email="sophia.chen@campus.edu"
    )
    repo.update_feedback_status(fb3, "Resolved", "CSS update pushed with enhanced WCAG AA contrast colors.")

    print("\n[Seed] Complete! Demo accounts configured:")
    print("  -> Admin:   admin@campus.edu       / AdminPass123!")
    print("  -> Student: alex.rivers@campus.edu / StudentPass123!")
    print("  -> Student: sophia.chen@campus.edu / StudentPass123!")

if __name__ == "__main__":
    seed_database()
