from datetime import datetime

from sqlalchemy import Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"), unique=True
    )
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    graded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    graded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    submission: Mapped["Submission"] = relationship(back_populates="grade")
    grader: Mapped["User"] = relationship(back_populates="graded_submissions")
