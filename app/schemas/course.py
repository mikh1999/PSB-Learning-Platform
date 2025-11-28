from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    title: str
    description: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class CourseRead(CourseBase):
    id: int
    teacher_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseWithTeacher(CourseRead):
    teacher_name: str | None = None
