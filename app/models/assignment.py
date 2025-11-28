from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="assignments")
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )
