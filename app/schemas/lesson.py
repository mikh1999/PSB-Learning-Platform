from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.lesson import LessonType


class LessonBase(BaseModel):
    title: str
    content: str | None = None
    order: int = 0
    type: LessonType = LessonType.TEXT
    file_url: str | None = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    order: int | None = None
    type: LessonType | None = None
    file_url: str | None = None


class LessonRead(LessonBase):
    id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
