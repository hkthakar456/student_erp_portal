import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from .base import BaseRepository

class SQLiteRepository(BaseRepository):
    """
    SQLite implementation of BaseRepository.
    Provides robust, localized database persistence with zero AWS dependencies.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._memory_conn = None
        if db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        else:
            db_dir = Path(db_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        if self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _rows_to_dicts(self, rows) -> List[Dict[str, Any]]:
        return [dict(row) for row in rows]

    def _row_to_dict(self, row) -> Optional[Dict[str, Any]]:
        return dict(row) if row else None

    def init_db(self) -> None:
        """Initializes tables, indices, and constraints."""
        conn = self.get_connection()
        try:
            with conn:
                conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student',
                    student_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id_code TEXT NOT NULL UNIQUE,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    program TEXT NOT NULL,
                    year_level TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    gpa REAL DEFAULT 0.0,
                    date_of_birth TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    instructor TEXT NOT NULL,
                    credits INTEGER NOT NULL DEFAULT 3,
                    term TEXT NOT NULL,
                    department TEXT NOT NULL,
                    capacity INTEGER NOT NULL DEFAULT 40,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Enrolled',
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE(student_id, course_id)
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    assessment_name TEXT NOT NULL,
                    score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    weight_percentage REAL DEFAULT 0.0,
                    remarks TEXT,
                    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'General',
                    author_name TEXT NOT NULL,
                    is_pinned INTEGER DEFAULT 0,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    contact_email TEXT,
                    status TEXT NOT NULL DEFAULT 'Open',
                    admin_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
                CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
                CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
                CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
                CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);
                CREATE INDEX IF NOT EXISTS idx_announcements_published ON announcements(published_at DESC);
                """)
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Auth / User ---
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def create_user(self, email: str, password_hash: str, role: str, student_id: Optional[int] = None) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
                    (email.strip().lower(), password_hash, role, student_id)
                )
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Students ---
    def list_students(
        self,
        query: Optional[str] = None,
        program: Optional[str] = None,
        year_level: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
            SELECT s.*, 
                   COUNT(DISTINCT e.course_id) AS active_enrollments_count
            FROM students s
            LEFT JOIN enrollments e ON s.id = e.student_id AND e.status = 'Enrolled'
            WHERE 1=1
            """
            params: List[Any] = []

            if query:
                sql += """ AND (
                    s.first_name LIKE ? OR 
                    s.last_name LIKE ? OR 
                    s.student_id_code LIKE ? OR 
                    s.email LIKE ?
                )"""
                pattern = f"%{query.strip()}%"
                params.extend([pattern, pattern, pattern, pattern])

            if program and program != "All":
                sql += " AND s.program = ?"
                params.append(program)

            if year_level and year_level != "All":
                sql += " AND s.year_level = ?"
                params.append(year_level)

            if status and status != "All":
                sql += " AND s.status = ?"
                params.append(status)

            sql += " GROUP BY s.id ORDER BY s.last_name ASC, s.first_name ASC"
            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_student_by_code(self, student_id_code: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE LOWER(student_id_code) = LOWER(?)", (student_id_code.strip(),))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def create_student(self, data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO students (
                    student_id_code, first_name, last_name, email, phone,
                    program, year_level, status, gpa, date_of_birth, address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["student_id_code"].strip().upper(),
                    data["first_name"].strip(),
                    data["last_name"].strip(),
                    data["email"].strip().lower(),
                    data.get("phone", "").strip(),
                    data["program"].strip(),
                    data["year_level"].strip(),
                    data.get("status", "Active"),
                    float(data.get("gpa", 0.0) or 0.0),
                    data.get("date_of_birth", ""),
                    data.get("address", "")
                ))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def update_student(self, student_id: int, data: Dict[str, Any]) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE students SET
                    student_id_code = ?,
                    first_name = ?,
                    last_name = ?,
                    email = ?,
                    phone = ?,
                    program = ?,
                    year_level = ?,
                    status = ?,
                    gpa = ?,
                    date_of_birth = ?,
                    address = ?
                WHERE id = ?
                """, (
                    data["student_id_code"].strip().upper(),
                    data["first_name"].strip(),
                    data["last_name"].strip(),
                    data["email"].strip().lower(),
                    data.get("phone", "").strip(),
                    data["program"].strip(),
                    data["year_level"].strip(),
                    data.get("status", "Active"),
                    float(data.get("gpa", 0.0) or 0.0),
                    data.get("date_of_birth", ""),
                    data.get("address", ""),
                    student_id
                ))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    def toggle_student_status(self, student_id: int, status: str) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET status = ? WHERE id = ?", (status, student_id))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Courses ---
    def list_courses(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
            SELECT c.*, 
                   COUNT(DISTINCT e.student_id) AS enrolled_count
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'Enrolled'
            WHERE 1=1
            """
            params: List[Any] = []
            if department and department != "All":
                sql += " AND c.department = ?"
                params.append(department)

            sql += " GROUP BY c.id ORDER BY c.code ASC"
            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_course_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.*, COUNT(DISTINCT e.student_id) AS enrolled_count
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'Enrolled'
            WHERE c.id = ?
            GROUP BY c.id
            """, (course_id,))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_course_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE LOWER(code) = LOWER(?)", (code.strip(),))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def create_course(self, data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO courses (
                    code, title, instructor, credits, term, department, capacity, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["code"].strip().upper(),
                    data["title"].strip(),
                    data["instructor"].strip(),
                    int(data.get("credits", 3)),
                    data["term"].strip(),
                    data["department"].strip(),
                    int(data.get("capacity", 40)),
                    data.get("description", "").strip()
                ))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def update_course(self, course_id: int, data: Dict[str, Any]) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE courses SET
                    code = ?,
                    title = ?,
                    instructor = ?,
                    credits = ?,
                    term = ?,
                    department = ?,
                    capacity = ?,
                    description = ?
                WHERE id = ?
                """, (
                    data["code"].strip().upper(),
                    data["title"].strip(),
                    data["instructor"].strip(),
                    int(data.get("credits", 3)),
                    data["term"].strip(),
                    data["department"].strip(),
                    int(data.get("capacity", 40)),
                    data.get("description", "").strip(),
                    course_id
                ))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Enrollments ---
    def get_enrollments_for_student(self, student_id: int) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT e.id AS enrollment_id, e.status AS enrollment_status, e.enrolled_at,
                   c.id AS course_id, c.code, c.title, c.instructor, c.credits, c.term, c.department
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = ?
            ORDER BY c.code ASC
            """, (student_id,))
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_enrollments_for_course(self, course_id: int) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT e.id AS enrollment_id, e.status AS enrollment_status, e.enrolled_at,
                   s.id AS student_id, s.student_id_code, s.first_name, s.last_name, s.email, s.program, s.year_level
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id = ? AND e.status = 'Enrolled'
            ORDER BY s.last_name ASC, s.first_name ASC
            """, (course_id,))
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def is_student_enrolled(self, student_id: int, course_id: int) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id FROM enrollments 
            WHERE student_id = ? AND course_id = ? AND status = 'Enrolled'
            """, (student_id, course_id))
            return cursor.fetchone() is not None
        finally:
            if self._memory_conn is None:
                conn.close()

    def enroll_student(self, student_id: int, course_id: int) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, status)
                VALUES (?, ?, 'Enrolled')
                ON CONFLICT(student_id, course_id) DO UPDATE SET status = 'Enrolled'
                """, (student_id, course_id))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def withdraw_student(self, enrollment_id: int) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE enrollments SET status = 'Dropped' WHERE id = ?", (enrollment_id,))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Attendance ---
    def list_attendance(
        self,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None,
        date_str: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
            SELECT a.*, 
                   s.first_name, s.last_name, s.student_id_code,
                   c.code AS course_code, c.title AS course_title
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN courses c ON a.course_id = c.id
            WHERE 1=1
            """
            params: List[Any] = []
            if student_id:
                sql += " AND a.student_id = ?"
                params.append(student_id)
            if course_id:
                sql += " AND a.course_id = ?"
                params.append(course_id)
            if date_str:
                sql += " AND a.date = ?"
                params.append(date_str)

            sql += " ORDER BY a.date DESC, a.id DESC"
            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def record_attendance(
        self,
        student_id: int,
        course_id: int,
        date_str: str,
        status: str,
        remarks: Optional[str] = None
    ) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO attendance (student_id, course_id, date, status, remarks)
                VALUES (?, ?, ?, ?, ?)
                """, (student_id, course_id, date_str, status, remarks or ""))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_student_attendance_summary(self, student_id: int) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) AS total_sessions,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) AS late_count,
                SUM(CASE WHEN status = 'Excused' THEN 1 ELSE 0 END) AS excused_count,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_count
            FROM attendance
            WHERE student_id = ?
            """, (student_id,))
            row = cursor.fetchone()
            total = row["total_sessions"] or 0
            present = row["present_count"] or 0
            late = row["late_count"] or 0
            excused = row["excused_count"] or 0
            absent = row["absent_count"] or 0

            # Calculation: Present & Excused count as attended; Late counts as 0.8
            effective_attended = present + excused + (0.8 * late)
            rate = round((effective_attended / total * 100), 1) if total > 0 else 100.0

            return {
                "total": total,
                "present": present,
                "late": late,
                "excused": excused,
                "absent": absent,
                "rate": rate
            }
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Grades ---
    def list_grades(
        self,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
            SELECT g.*, 
                   s.first_name, s.last_name, s.student_id_code,
                   c.code AS course_code, c.title AS course_title
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN courses c ON g.course_id = c.id
            WHERE 1=1
            """
            params: List[Any] = []
            if student_id:
                sql += " AND g.student_id = ?"
                params.append(student_id)
            if course_id:
                sql += " AND g.course_id = ?"
                params.append(course_id)

            sql += " ORDER BY g.graded_at DESC, g.id DESC"
            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def record_grade(
        self,
        student_id: int,
        course_id: int,
        assessment_name: str,
        score: float,
        max_score: float,
        weight_percentage: Optional[float] = None,
        remarks: Optional[str] = None
    ) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO grades (
                    student_id, course_id, assessment_name, score, max_score, weight_percentage, remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id, course_id, assessment_name.strip(),
                    float(score), float(max_score),
                    float(weight_percentage or 0.0), remarks or ""
                ))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_student_grade_summary(self, student_id: int) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT g.*, c.code AS course_code, c.title AS course_title
            FROM grades g
            JOIN courses c ON g.course_id = c.id
            WHERE g.student_id = ?
            ORDER BY c.code ASC, g.graded_at ASC
            """, (student_id,))
            grades = self._rows_to_dicts(cursor.fetchall())

            if not grades:
                return {"average_percentage": 0.0, "total_assessments": 0, "grades": []}

            total_pct = sum((g["score"] / g["max_score"] * 100) for g in grades if g["max_score"] > 0)
            avg_pct = round(total_pct / len(grades), 1)

            return {
                "average_percentage": avg_pct,
                "total_assessments": len(grades),
                "grades": grades
            }
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Announcements ---
    def list_announcements(self, limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM announcements WHERE 1=1"
            params: List[Any] = []
            if category and category != "All":
                sql += " AND category = ?"
                params.append(category)

            sql += " ORDER BY is_pinned DESC, published_at DESC"
            if limit:
                sql += " LIMIT ?"
                params.append(limit)

            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def get_announcement_by_id(self, announcement_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM announcements WHERE id = ?", (announcement_id,))
            return self._row_to_dict(cursor.fetchone())
        finally:
            if self._memory_conn is None:
                conn.close()

    def create_announcement(
        self,
        title: str,
        content: str,
        category: str,
        author_name: str,
        is_pinned: bool = False
    ) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO announcements (title, content, category, author_name, is_pinned)
                VALUES (?, ?, ?, ?, ?)
                """, (title.strip(), content.strip(), category.strip(), author_name.strip(), 1 if is_pinned else 0))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def delete_announcement(self, announcement_id: int) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Feedback ---
    def list_feedback(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM feedback WHERE 1=1"
            params: List[Any] = []
            if status and status != "All":
                sql += " AND status = ?"
                params.append(status)

            sql += " ORDER BY created_at DESC"
            cursor.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        finally:
            if self._memory_conn is None:
                conn.close()

    def create_feedback(self, category: str, message: str, contact_email: Optional[str] = None) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO feedback (category, message, contact_email, status)
                VALUES (?, ?, ?, 'Open')
                """, (category.strip(), message.strip(), (contact_email or "").strip()))
                return cursor.lastrowid
        finally:
            if self._memory_conn is None:
                conn.close()

    def update_feedback_status(
        self,
        feedback_id: int,
        status: str,
        admin_response: Optional[str] = None
    ) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                if admin_response is not None:
                    cursor.execute("""
                    UPDATE feedback SET status = ?, admin_response = ? WHERE id = ?
                    """, (status.strip(), admin_response.strip(), feedback_id))
                else:
                    cursor.execute("UPDATE feedback SET status = ? WHERE id = ?", (status.strip(), feedback_id))
                return cursor.rowcount > 0
        finally:
            if self._memory_conn is None:
                conn.close()

    # --- Dashboard Summary ---
    def get_dashboard_stats(self) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM students WHERE status = 'Active'")
            active_students = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM courses")
            active_courses = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM enrollments WHERE status = 'Enrolled'")
            total_enrollments = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM feedback WHERE status = 'Open'")
            open_feedback = cursor.fetchone()["count"]

            # Average attendance across campus
            cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status IN ('Present', 'Excused') THEN 1 ELSE 0 END) AS attended
            FROM attendance
            """)
            att_row = cursor.fetchone()
            avg_att_rate = round(att_row["attended"] / att_row["total"] * 100, 1) if att_row["total"] > 0 else 94.2

            return {
                "active_students": active_students,
                "active_courses": active_courses,
                "total_enrollments": total_enrollments,
                "open_feedback": open_feedback,
                "campus_attendance_rate": avg_att_rate,
                "semester": "Fall 2026 (Demo Term)"
            }
        finally:
            if self._memory_conn is None:
                conn.close()
