from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.models.chatbot import ChatbotStatus
from app.models.chatbot_permission import PermissionLevel
from app.models.chatbot_appearance import WidgetPosition


# ============== Chatbot Schemas ==============


class ChatbotCreate(BaseModel):
    name: str
    welcome_message: Optional[str] = None


class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    welcome_message: Optional[str] = None
    status: Optional[ChatbotStatus] = None


class ChatbotResponse(BaseModel):
    id: UUID
    tenant_id: int
    name: str
    welcome_message: Optional[str]
    status: ChatbotStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatbotWithPermission(ChatbotResponse):
    """Chatbot response with user's permission level"""

    permission_level: PermissionLevel
    can_manage_knowledge: bool = False
    can_manage_appearance: bool = False
    can_resolve_queries: bool = False
    can_view_analytics_billing: bool = False  # Renamed from can_view_analytics


class ChatbotListResponse(BaseModel):
    chatbots: List[ChatbotWithPermission]
    total: int


# ============== Permission Schemas ==============


class PermissionAssign(BaseModel):
    user_id: int
    can_manage_knowledge: bool = False
    can_manage_appearance: bool = False
    can_resolve_queries: bool = False
    can_view_analytics_billing: bool = False  # Renamed from can_view_analytics


class PermissionUpdate(BaseModel):
    permission_level: Optional[PermissionLevel] = None
    can_manage_knowledge: Optional[bool] = None
    can_manage_appearance: Optional[bool] = None
    can_resolve_queries: Optional[bool] = None
    can_view_analytics_billing: Optional[bool] = None  # Renamed from can_view_analytics


class PermissionResponse(BaseModel):
    id: int
    user_id: int
    chatbot_id: UUID
    permission_level: PermissionLevel
    can_manage_knowledge: bool
    can_manage_appearance: bool
    can_resolve_queries: bool
    can_view_analytics_billing: bool  # Renamed from can_view_analytics
    granted_by: int
    created_at: datetime
    # Include user info for display
    user_email: Optional[str] = None
    user_username: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    permissions: List[PermissionResponse]
    total: int


# ============== Appearance Schemas ==============


class AppearanceResponse(BaseModel):
    id: UUID
    chatbot_id: UUID
    primary_color: str
    header_text: str
    avatar_url: Optional[str]
    position: WidgetPosition
    offset_x: int
    offset_y: int
    welcome_message: Optional[str]
    initial_suggestions: List[str]
    show_branding: bool
    # Personality customization
    personality_tone: str = "friendly"
    response_length: str = "balanced"
    temperature: float = 0.7
    custom_instructions: Optional[str] = None
    # Language settings — multi-language list
    languages: List[str] = ["en"]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppearanceUpdate(BaseModel):
    primary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    header_text: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    position: Optional[WidgetPosition] = None
    offset_x: Optional[int] = None
    offset_y: Optional[int] = None
    welcome_message: Optional[str] = None
    initial_suggestions: Optional[List[str]] = None
    show_branding: Optional[bool] = None
    # Personality customization
    personality_tone: Optional[str] = Field(
        None, pattern=r"^(formal|casual|friendly|professional)$"
    )
    response_length: Optional[str] = Field(
        None, pattern=r"^(concise|balanced|detailed)$"
    )
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    custom_instructions: Optional[str] = None
    # Language settings — list of allowed language codes
    languages: Optional[List[str]] = Field(
        None,
        description="List of allowed language codes. At least 1 required. Valid: en, hi, gu",
    )

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, v):
        if v is None:
            return v
        valid_codes = {"en", "hi", "gu"}
        if len(v) == 0:
            raise ValueError("At least one language must be selected")
        for code in v:
            if code not in valid_codes:
                raise ValueError(f"Invalid language code: {code}. Valid: en, hi, gu")
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for code in v:
            if code not in seen:
                seen.add(code)
                unique.append(code)
        return unique


# ============== Stats & Analytics Schemas ==============


class RecentActivity(BaseModel):
    id: UUID
    type: str  # 'knowledge_source', 'conversation', 'status_change'
    description: str
    created_at: datetime


class KnowledgeSourceBreakdown(BaseModel):
    total_crawled_urls: int
    total_uploaded_files: int
    total_qa_pairs: int
    total_crawled_pages: int
    total_file_size: int  # in bytes
    total_qa_count: int


class ChatbotStatsResponse(BaseModel):
    total_conversations: int
    total_knowledge_sources: int
    active_knowledge_sources: int
    total_kb_size: int
    knowledge_breakdown: KnowledgeSourceBreakdown
    recent_activity: List[RecentActivity]


class RecentActivityListResponse(BaseModel):
    activities: List[RecentActivity]
    total: int
    page: int
    page_size: int
    total_pages: int


# Analytics moved to app.schemas.analytics
from app.schemas.analytics import AnalyticsOverviewResponse
