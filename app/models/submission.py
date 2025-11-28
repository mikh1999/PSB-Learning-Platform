from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubmissionStatus(str, Enum):
    DRAFT = "draft"              # черновик
    SUBMITTED = "submitted"      # на проверке
    GRADED = "graded"            # проверено
    RETURNED = "returned"        # вернули на доработку


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE")
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus), default=SubmissionStatus.DRAFT
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    assignment: Mapped["Assignment"] = relationship(back_populates="submissions")
    student: Mapped["User"] = relationship(back_populates="submissions")
    grade: Mapped["Grade | None"] = relationship(
        back_populates="submission", cascade="all, delete-orphan", uselist=False
    )
