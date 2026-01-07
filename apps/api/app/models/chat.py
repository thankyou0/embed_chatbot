import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageRoleType(TypeDecorator):
    """Custom type for MessageRole enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("user", "assistant", name="messagerole", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, MessageRole): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return MessageRole(value)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    chatbot_id = Column(ForeignKey("chatbots.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    conversation_summary = Column(Text, nullable=True)

    # Relationships
    chatbot = relationship("Chatbot")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    session_id = Column(ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(MessageRoleType(), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSONB, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

