from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole


class UserResponse(UserBase):
    id: int
    tenant_id: int
    name: Optional[str] = None
    is_active: bool = True
    must_change_password: bool = False
    password_expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

