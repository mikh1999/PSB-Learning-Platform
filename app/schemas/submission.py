from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.submission import SubmissionStatus


class SubmissionBase(BaseModel):
    content: str | None = None
    file_url: str | None = None


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    content: str | None = None
    file_url: str | None = None


class SubmissionRead(SubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    status: SubmissionStatus
    submitted_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
