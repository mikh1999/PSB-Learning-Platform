from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentBase(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    max_score: int = 100


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    max_score: int | None = None


class AssignmentRead(AssignmentBase):
    id: int
    lesson_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
