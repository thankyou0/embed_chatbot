from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    MeResponse,
)
from app.schemas.user import UserResponse
from app.schemas.tenant import TenantResponse
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MemberPasswordReset,
    MemberChatbotPermissionsUpdate,
    MemberChatbotPermissionResponse,
    ChatbotPermissionAssign,
)
from app.schemas.chatbot import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotResponse,
    ChatbotWithPermission,
    ChatbotListResponse,
    PermissionAssign,
    PermissionUpdate,
    PermissionResponse,
    PermissionListResponse,
    AppearanceResponse,
    AppearanceUpdate,
)
from app.schemas.appearance import (
    ChatbotAppearanceBase,
    ChatbotAppearanceUpdate,
    ChatbotAppearanceResponse,
)

__all__ = [
    # Auth
    "SignupRequest",
    "SignupResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "RefreshResponse",
    "TokenResponse",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "MeResponse",
    # User/Tenant
    "UserResponse",
    "TenantResponse",
    # Members
    "MemberCreate",
    "MemberUpdate",
    "MemberResponse",
    "MemberListResponse",
    "MemberPasswordReset",
    "MemberChatbotPermissionsUpdate",
    "MemberChatbotPermissionResponse",
    "ChatbotPermissionAssign",
    # Chatbots
    "ChatbotCreate",
    "ChatbotUpdate",
    "ChatbotResponse",
    "ChatbotWithPermission",
    "ChatbotListResponse",
    # Permissions
    "PermissionAssign",
    "PermissionUpdate",
    "PermissionResponse",
    "PermissionListResponse",
    # Appearance
    "ChatbotAppearanceBase",
    "ChatbotAppearanceUpdate",
    "ChatbotAppearanceResponse",
]