from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GradeBase(BaseModel):
    score: int = Field(..., ge=0)
    comment: str | None = None


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    score: int | None = Field(None, ge=0)
    comment: str | None = None


class GradeRead(GradeBase):
    id: int
    submission_id: int
    graded_by: int
    graded_at: datetime

    model_config = ConfigDict(from_attributes=True)
