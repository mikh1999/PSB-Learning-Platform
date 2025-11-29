from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionCommentCreate(BaseModel):
    """Схема для создания комментария."""
    content: str


class SubmissionCommentRead(BaseModel):
    """Схема для чтения комментария."""
    id: int
    submission_id: int
    user_id: int
    content: str
    created_at: datetime
    # Дополнительные поля для отображения автора
    author_name: str | None = None
    author_role: str | None = None

    model_config = ConfigDict(from_attributes=True)
