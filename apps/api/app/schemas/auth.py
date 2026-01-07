from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.schemas.user import UserResponse
from app.schemas.tenant import TenantResponse


class SignupRequest(BaseModel):
    tenant_name: str
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class SignupResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    tenant: TenantResponse


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    tenant: TenantResponse


class RefreshResponse(BaseModel):
    access_token: str


class ChangePasswordResponse(BaseModel):
    message: str
    user: UserResponse
    tenant: Optional[TenantResponse] = None


class MeResponse(BaseModel):
    user: UserResponse
    tenant: TenantResponse

