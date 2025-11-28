from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)