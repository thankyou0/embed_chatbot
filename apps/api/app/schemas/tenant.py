from pydantic import BaseModel, EmailStr
from datetime import datetime


class TenantBase(BaseModel):
    name: str
    email: EmailStr


class TenantResponse(TenantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

