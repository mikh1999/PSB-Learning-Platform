from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.enrollment import Enrollment


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus), default=CourseStatus.DRAFT
    )
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    teacher: Mapped["User"] = relationship(back_populates="courses")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
