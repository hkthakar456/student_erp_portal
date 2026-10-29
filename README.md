# Beacon Student ERP Portal

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Persistence-SQLite%20(Repository%20Pattern)-orange.svg)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg)](https://docs.pytest.org/)

> **Educational Demonstration Notice:**  
> This application is built as an educational demonstration of an institutional student information and ERP portal. All student names, ID numbers, addresses, attendance logs, and academic records are **strictly fictional**.

---

## 📖 Overview

**Beacon ERP** is a campus student management portal designed for higher education administration, faculty, and students. Built with Python, Flask, Jinja2, and Vanilla CSS, it delivers a realistic campus information system with role-based access control, comprehensive academic records management, and clean data access decoupling.

The persistence layer uses a **Repository Pattern** (`BaseRepository`), keeping data access fully abstracted so the current local SQLite backend can easily be adapted or supplemented with AWS DynamoDB in future deployment phases without rewriting route controllers or business logic.

---

## ✨ Features

### 1. Centralized Dashboard
- **Executive KPI Cards**: Real-time summary metrics for active students, registered courses, total active enrollments, and open feedback tickets.
- **Academic Term Tracking**: Configured for the active academic term (`Fall 2026`).
- **Student Profile Snapshot**: When logged in as a student, displays personal GPA, personal attendance percentage, and enrolled courses.
- **Campus Announcements Feed**: Displays official university bulletins, highlights pinned urgent alerts, and recent campus news.
- **Illustrative Milestones**: Transparently labeled demonstration markers for academic term timelines and campus-wide statistics.

### 2. Student Directory & Profiles
- **Multi-Criteria Search & Filter**: Real-time search across student legal names, unique ID codes (e.g., `STU-2024-001`), degree programs, academic years, and enrollment statuses.
- **Comprehensive Profile View**: Displays legal names, email addresses, contact details, date of birth, mailing addresses, enrolled courses, attendance summaries, and grade breakdowns.
- **Complete CRUD Operations**: Create new student profiles, edit existing records, and deactivate or reactivate student statuses.
- **Direct Enrollment Management**: Enroll students in courses or process course withdrawals directly from their profile page.

### 3. Course Catalog & Roster Management
- **Course Directory**: Details course codes (e.g., `CS101`, `CS201`, `CS301`), title, faculty instructor, credits, academic term, department, and maximum enrollment capacity.
- **Roster Tracking**: View rosters of enrolled candidates per course section.
- **Duplicate Prevention**: Server-side validation guarantees a student cannot be actively enrolled in the same course twice.
- **Capacity Indicators**: Visual status badges and progress indicators prevent over-enrollment.

### 4. Attendance Roll-Call & Percentage Summary
- **Session Attendance Logging**: Record attendance status per student, course, and date: `Present`, `Late`, `Absent`, or `Excused` with optional remarks.
- **Automatic Attendance Rate Calculation**: Computes attendance percentage (`(Present + Excused + 0.8 * Late) / Total * 100`).
- **Role-Aware Filters**: Students view only their personal verified attendance history; administrators can filter across any student, course, or date.

### 5. Grade Book & Academic Performance
- **Continuous Assessment Scoring**: Track quizzes, lab assignments, milestone submissions, midterm evaluations, and final exams.
- **Score Validation**: Strict validation ensures scores are non-negative and do not exceed the declared maximum score (`score <= max_score`).
- **Demonstration Average & Letter Scale**: Computes simple/weighted percentage averages with letter grade estimates.
- **Disclaimer Banner**: Clearly identifies calculations as a simulated evaluation system.

### 6. Campus Announcements & Bulletins
- **Categorized Notices**: Filter bulletins by category (`Academic`, `Event`, `Alert`, `General`).
- **Pinned Bulletins**: Pin priority notices to the top of the dashboard and bulletin board.
- **Admin Authoring & Deletion**: Administrators can publish new notices and remove expired bulletins.

### 7. Student Voice & Feedback Ticketing
- **Inquiry Submission**: Students can submit feedback or facility tickets categorized by topic with optional email contact for administrative follow-up.
- **Administrative Triage Queue**: Administrators can filter tickets (`Open`, `In Progress`, `Resolved`) and attach official resolution notes.

### 8. Authentication, Roles & Security
- **Role-Based Access Control (RBAC)**: Enforces role checks (`@login_required`, `@admin_required`). Students cannot execute administrative mutations.
- **Password Hashing**: Passwords hashed securely using PBKDF2 with SHA-256 via `werkzeug.security`.
- **CSRF Defense**: All POST mutation requests require valid session CSRF tokens.
- **Secure Cookie Flags**: Session cookies configured with `HttpOnly` and `SameSite=Lax`.

---

## 🏛️ Architecture & Project Structure

```
Student_ERP_portal/
├── app/
│   ├── __init__.py           # Application factory (create_app), context processors, filters
│   ├── config.py             # Development, Testing, and Production configurations
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py           # BaseRepository abstract base class (interface contract)
│   │   └── sqlite_repo.py    # SQLite persistence implementation (safe queries & connection management)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Login, demo prefill, logout
│   │   ├── dashboard.py      # Summary metrics, term view, student snapshot
│   │   ├── students.py       # Directory, search/filter, CRUD, status toggle, enrollment
│   │   ├── courses.py        # Catalog, creation, editing, roster, student enrollment
│   │   ├── attendance.py     # Roll call, attendance history, rate calculation
│   │   ├── grades.py         # Grade book, score bounds validation, GPA simulation
│   │   ├── announcements.py  # Campus bulletins, pinning, category filtering
│   │   └── feedback.py       # Student feedback form & admin resolution queue
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py   # Password hashing, session helpers, RBAC decorators, CSRF
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Modern, responsive design system (Inter font, slate/indigo)
│   │   └── js/
│   │       └── main.js       # Mobile navigation toggle, instant table search, score preview
│   └── templates/
│       ├── base.html         # Responsive layout shell with sidebar, topbar & footer
│       ├── components/       # Reusable navbar, sidebar, flash messages, footer
│       ├── auth/             # Login template with quick demo fill helper
│       ├── dashboard.html    # KPI overview and activity feed
│       ├── students/         # List, detail profile, create/edit form
│       ├── courses/          # Catalog, roster detail, create/edit form
│       ├── attendance/       # Roll call form, summary cards, history table
│       ├── grades/           # Grade book, score validation preview, history table
│       ├── announcements/    # Bulletin feed and admin announcement publisher
│       ├── feedback/         # Student submission form and admin triage queue
│       └── errors/           # 404, 403, and 500 error pages
├── data/                     # Local SQLite database directory (gitignored)
├── tests/
│   ├── conftest.py           # Pytest fixtures, test client, and test database seeder
│   ├── test_auth.py          # Sign in, hashing, CSRF enforcement, role boundaries
│   ├── test_students.py      # Directory filtering, CRUD validation, duplicate check
│   ├── test_courses.py       # Catalog, roster, duplicate enrollment prevention
│   ├── test_attendance.py   # Attendance logging, percentage calculations
│   ├── test_grades.py       # Score <= max_score validation, simple averages
│   └── test_feedback.py     # Student submission, admin triage, status transitions
├── .env.example              # Sample environment configuration template
├── .gitignore                # Excludes local databases, secrets, pycache, and virtualenvs
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python project dependencies
├── run.py                    # Main development entry point
└── seed.py                   # Repeatable database seeder with rich fictional data
```

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 1. Clone the Repository
```bash
git clone https://github.com/hkthakar456/student_erp_portal.git
cd student_erp_portal
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database
Populate the database with realistic fictional students, courses, attendance sessions, grades, and announcements:
```bash
python seed.py
```
*(Alternatively, running `python run.py` will automatically seed the database on initial launch if no database file exists).*

### 5. Launch the Application
```bash
python run.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Demo User Credentials

The application comes pre-configured with demo accounts for evaluation:

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@campus.edu` | `AdminPass123!` | Full administrative CRUD, enroll/drop students, grade recording, roll-call, bulletin authoring, feedback triage |
| **Student** | `alex.rivers@campus.edu` | `StudentPass123!` | Personal profile view, course workload, personal attendance history, personal grade book, feedback submission |
| **Student** | `sophia.chen@campus.edu` | `StudentPass123!` | Secondary student profile candidate |

*(The login screen also features convenient **Quick Fill** buttons for immediate one-click testing).*

---

## 🧪 Running Automated Tests

A comprehensive test suite of 28 automated tests covers authentication, RBAC boundaries, CSRF protection, student CRUD, duplicate enrollment prevention, attendance calculations, score validation, and feedback workflows:

```bash
pytest -v
```

Output:
```text
tests/test_attendance.py::test_attendance_list PASSED
tests/test_attendance.py::test_record_attendance_success PASSED
tests/test_attendance.py::test_attendance_summary_calculation PASSED
tests/test_auth.py::test_login_page_renders PASSED
tests/test_auth.py::test_login_success_admin PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_login_csrf_protection PASSED
tests/test_auth.py::test_logout PASSED
tests/test_auth.py::test_unauthenticated_access_redirects PASSED
tests/test_auth.py::test_student_cannot_access_admin_routes PASSED
tests/test_courses.py::test_course_list PASSED
tests/test_courses.py::test_course_detail PASSED
tests/test_courses.py::test_create_course PASSED
tests/test_courses.py::test_prevent_duplicate_active_enrollment PASSED
tests/test_courses.py::test_enroll_and_withdraw PASSED
tests/test_feedback.py::test_student_submit_feedback PASSED
tests/test_feedback.py::test_admin_feedback_queue PASSED
tests/test_feedback.py::test_student_cannot_access_feedback_queue PASSED
tests/test_feedback.py::test_admin_update_feedback_status PASSED
tests/test_grades.py::test_grade_book_renders PASSED
tests/test_grades.py::test_record_grade_valid PASSED
tests/test_grades.py::test_record_grade_score_exceeding_max_rejected PASSED
tests/test_students.py::test_student_list_authenticated PASSED
tests/test_students.py::test_student_search_filtering PASSED
tests/test_students.py::test_student_detail_view PASSED
tests/test_students.py::test_admin_create_student_success PASSED
tests/test_students.py::test_admin_create_student_duplicate_id_code_rejected PASSED
tests/test_students.py::test_toggle_student_status PASSED

============================= 28 passed =============================
```

---

## 🔒 Security & Privacy Practices

- **Zero Real PII**: No real student personal information, social security numbers, or real institutional records are present.
- **No Committed Secrets**: Local database files (`*.db`), secrets (`.env`), and cache artifacts are strictly excluded from source control via `.gitignore`.
- **Hashed Credentials**: Plaintext passwords are never stored in memory or on disk; all passwords use PBKDF2 password hashing.
- **Clean Repository Decoupling**: Designed to allow zero-downtime migration to DynamoDB / AWS EC2 in later stages.
