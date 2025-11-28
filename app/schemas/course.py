from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.course import CourseStatus


class CourseBase(BaseModel):
    title: str
    description: str | None = None


class CourseCreate(CourseBase):
    status: CourseStatus = CourseStatus.DRAFT


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: CourseStatus | None = None


class CourseRead(CourseBase):
    id: int
    teacher_id: int
    status: CourseStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseWithTeacher(CourseRead):
    teacher_name: str | None = None


class CoursePublic(BaseModel):
    """Публичная информация о курсе (без авторизации)."""

    id: int
    title: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
