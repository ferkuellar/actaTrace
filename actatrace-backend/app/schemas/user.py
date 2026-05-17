from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, UserStatus
from app.schemas.common import ORMModel


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    role: UserRole
    organization: str = Field(min_length=2, max_length=200)
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    password: str = Field(min_length=10, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    role: UserRole | None = None
    organization: str | None = Field(default=None, min_length=2, max_length=200)
    status: UserStatus | None = None


class UserRead(ORMModel):
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    organization: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
