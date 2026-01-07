import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, TypeDecorator, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class WidgetPosition(str, enum.Enum):
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_LEFT = "bottom-left"


class WidgetPositionType(TypeDecorator):
    """Custom type for WidgetPosition enum"""
    impl = PG_ENUM
    cache_ok = True

    def __init__(self):
        super().__init__("bottom-right", "bottom-left", name="widgetposition", create_type=False)

    def process_bind_param(self, value, dialect):
        if isinstance(value, WidgetPosition):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return WidgetPosition(value)


class ChatbotAppearance(Base):
    __tablename__ = "chatbot_appearances"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False, unique=True, index=True)
    
    primary_color = Column(String(50), nullable=False, default="#2563eb")
    header_text = Column(String(255), nullable=False, default="Chat with us")
    avatar_url = Column(String(1024), nullable=True)
    position = Column(WidgetPositionType(), nullable=False, default=WidgetPosition.BOTTOM_RIGHT)
    offset_x = Column(Integer, nullable=False, default=0)
    offset_y = Column(Integer, nullable=False, default=0)
    welcome_message = Column(Text, nullable=True)
    initial_suggestions = Column(JSONB, nullable=False, server_default='[]')
    show_branding = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chatbot = relationship("Chatbot", back_populates="appearance")
