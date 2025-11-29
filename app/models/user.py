import enum
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.submission import Submission
    from app.models.grade import Grade
    from app.models.enrollment import Enrollment
    from app.models.lesson_progress import LessonProgress
    from app.models.submission_comment import SubmissionComment


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="student")
    graded_submissions: Mapped[list["Grade"]] = relationship(back_populates="grader")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")
    lesson_progress: Mapped[list["LessonProgress"]] = relationship(back_populates="student")
    submission_comments: Mapped[list["SubmissionComment"]] = relationship(back_populates="user")