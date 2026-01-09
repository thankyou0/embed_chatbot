from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.models.user import UserRole
from app.models.chatbot_permission import PermissionLevel


class ChatbotPermissionAssign(BaseModel):
    """Permission assignment for a specific chatbot"""
    chatbot_id: UUID
    permission_level: PermissionLevel
    can_manage_knowledge: bool = False
    can_manage_appearance: bool = False
    can_resolve_queries: bool = False
    can_view_analytics: bool = False


class MemberCreate(BaseModel):
    """Request to add a new member to tenant"""
    email: EmailStr
    username: str
    password: str
    name: Optional[str] = None
    role: UserRole = UserRole.USER
    password_expiry_hours: int = 72  # Default 72 hours (3 days) for temp password
    chatbot_permissions: Optional[List[ChatbotPermissionAssign]] = None  # Permissions per chatbot
    
    @field_validator('password_expiry_hours')
    @classmethod
    def validate_expiry_hours(cls, v):
        if v < 1 or v > 720:  # 1 hour to 30 days
            raise ValueError('Password expiry must be between 1 and 720 hours')
        return v


class MemberUpdate(BaseModel):
    """Request to update member details"""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class MemberPasswordReset(BaseModel):
    """Reset member's password with a new temporary one"""
    new_password: str
    password_expiry_hours: int = 72


class MemberChatbotPermissionsUpdate(BaseModel):
    """Update member's chatbot permissions"""
    permissions: List[ChatbotPermissionAssign]


class MemberChatbotPermissionResponse(BaseModel):
    """Chatbot permission for a member"""
    chatbot_id: UUID
    chatbot_name: str
    permission_level: PermissionLevel
    can_manage_knowledge: bool
    can_manage_appearance: bool
    can_resolve_queries: bool
    can_view_analytics: bool


class MemberResponse(BaseModel):
    """Member details response"""
    id: int
    tenant_id: int
    email: str
    username: str
    name: Optional[str]
    role: UserRole
    is_active: bool
    must_change_password: bool = False
    password_expires_at: Optional[datetime] = None
    invited_by: Optional[int] = None
    created_at: datetime
    chatbot_permissions: Optional[List[MemberChatbotPermissionResponse]] = None

    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    members: List[MemberResponse]
    total: int

