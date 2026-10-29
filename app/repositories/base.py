from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class BaseRepository(ABC):
    """
    Abstract interface for repository operations.
    Enables swapping SQLite persistence with DynamoDB in later stages.
    """

    # --- Lifecycle / Initialization ---
    @abstractmethod
    def init_db(self) -> None:
        pass

    # --- User / Auth ---
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_user(self, email: str, password_hash: str, role: str, student_id: Optional[int] = None) -> int:
        pass

    # --- Students ---
    @abstractmethod
    def list_students(
        self,
        query: Optional[str] = None,
        program: Optional[str] = None,
        year_level: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_student_by_code(self, student_id_code: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_student(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_student(self, student_id: int, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def toggle_student_status(self, student_id: int, status: str) -> bool:
        pass

    # --- Courses ---
    @abstractmethod
    def list_courses(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_course_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_course_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_course(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_course(self, course_id: int, data: Dict[str, Any]) -> bool:
        pass

    # --- Enrollments ---
    @abstractmethod
    def get_enrollments_for_student(self, student_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_enrollments_for_course(self, course_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def is_student_enrolled(self, student_id: int, course_id: int) -> bool:
        pass

    @abstractmethod
    def enroll_student(self, student_id: int, course_id: int) -> int:
        pass

    @abstractmethod
    def withdraw_student(self, enrollment_id: int) -> bool:
        pass

    # --- Attendance ---
    @abstractmethod
    def list_attendance(
        self,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None,
        date_str: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def record_attendance(
        self,
        student_id: int,
        course_id: int,
        date_str: str,
        status: str,
        remarks: Optional[str] = None
    ) -> int:
        pass

    @abstractmethod
    def get_student_attendance_summary(self, student_id: int) -> Dict[str, Any]:
        pass

    # --- Grades ---
    @abstractmethod
    def list_grades(
        self,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_student_grade_summary(self, student_id: int) -> Dict[str, Any]:
        pass

    # --- Announcements ---
    @abstractmethod
    def list_announcements(self, limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_announcement_by_id(self, announcement_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_announcement(
        self,
        title: str,
        content: str,
        category: str,
        author_name: str,
        is_pinned: bool = False
    ) -> int:
        pass

    @abstractmethod
    def delete_announcement(self, announcement_id: int) -> bool:
        pass

    # --- Feedback ---
    @abstractmethod
    def list_feedback(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_feedback(self, category: str, message: str, contact_email: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def update_feedback_status(
        self,
        feedback_id: int,
        status: str,
        admin_response: Optional[str] = None
    ) -> bool:
        pass

    # --- Dashboard Summary ---
    @abstractmethod
    def get_dashboard_stats(self) -> Dict[str, Any]:
        pass
