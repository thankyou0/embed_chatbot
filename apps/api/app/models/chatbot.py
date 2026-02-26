import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SAEnum, func, TypeDecorator, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatbotStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"


class ChatbotStatusType(TypeDecorator):
    """Custom type to ensure enum values (not names) are used with PostgreSQL native enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("draft", "active", "paused", name="chatbotstatus", create_type=False)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to its value (string) before binding to database"""
        if value is None:
            return None
        if isinstance(value, ChatbotStatus):
            return value.value  # Use enum value, not name
        return value
    
    def process_result_value(self, value, dialect):
        """Convert database value back to enum"""
        if value is None:
            return None
        return ChatbotStatus(value)


class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    tenant_id = Column(ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    welcome_message = Column(Text, nullable=True)
    # Use custom type to ensure enum values are used, not names
    status = Column(ChatbotStatusType(), nullable=False, default=ChatbotStatus.DRAFT)
    confidence_threshold = Column(Float, nullable=False, server_default='0.7')
    created_by = Column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Per-chatbot message count (deleted with chatbot)
    message_count = Column(Integer, nullable=False, default=0, index=True)

    # Auto-generated scope description from crawl data
    # JSON: {brand_name, business_type, what_they_sell, topics_covered, not_about, auto_generated, last_updated}
    scope_description = Column(JSONB, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="chatbots")
    creator = relationship("User", back_populates="created_chatbots", foreign_keys=[created_by])
    permissions = relationship("ChatbotPermission", back_populates="chatbot", cascade="all, delete-orphan")
    appearance = relationship("ChatbotAppearance", back_populates="chatbot", uselist=False, cascade="all, delete-orphan")
    knowledge_sources = relationship("KnowledgeSource", back_populates="chatbot", cascade="all, delete-orphan")
    activities = relationship("ChatbotActivity", back_populates="chatbot", cascade="all, delete-orphan")


class ChatbotActivity(Base):
    __tablename__ = "chatbot_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    chatbot_id = Column(ForeignKey("chatbots.id"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=True)  # System actions might have no user
    activity_type = Column(String(50), nullable=False)  # 'status_change', 'knowledge_added', etc.
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    chatbot = relationship("Chatbot", back_populates="activities")
    user = relationship("User")


