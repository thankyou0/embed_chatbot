from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from app.models.chatbot_appearance import (
    WidgetPosition,
    PersonalityTone,
    ChatbotLanguage,
)


class ChatbotAppearanceBase(BaseModel):
    primary_color: Optional[str] = "#2563eb"
    header_text: Optional[str] = "Chat with us"
    avatar_url: Optional[str] = None
    position: Optional[WidgetPosition] = WidgetPosition.BOTTOM_RIGHT
    offset_x: Optional[int] = 0
    offset_y: Optional[int] = 0
    welcome_message: Optional[str] = None
    initial_suggestions: Optional[List[str]] = []
    show_branding: Optional[bool] = True
    # Personality customization
    personality_tone: Optional[
        Literal["formal", "casual", "friendly", "professional"]
    ] = "friendly"
    response_length: Optional[Literal["concise", "balanced", "detailed"]] = "balanced"
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    custom_instructions: Optional[str] = None
    # Language settings — multi-language support (list of codes)
    languages: Optional[List[Literal["en", "hi", "gu"]]] = ["en"]


class ChatbotAppearanceUpdate(ChatbotAppearanceBase):
    pass


class AvatarUploadResponse(BaseModel):
    chatbot_id: UUID
    avatar_url: Optional[str] = None


class ChatbotAppearanceResponse(ChatbotAppearanceBase):
    id: UUID
    chatbot_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WidgetConfigResponse(BaseModel):
    """Public widget configuration (no auth required)"""

    display_name: str
    primary_color: str
    header_text: str
    avatar_url: Optional[str]
    position: str  # "bottom-right" or "bottom-left"
    offset_x: int
    offset_y: int
    welcome_message: Optional[str]
    initial_suggestions: List[str]
    show_branding: bool
    is_paused: bool = False
    # Personality settings
    personality_tone: str = "friendly"
    response_length: str = "balanced"
    temperature: float = 0.7
    custom_instructions: Optional[str] = None
    # Language settings — list of allowed language codes
    languages: List[str] = ["en"]

    class Config:
        from_attributes = True
