from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.core.database import Base


class PermissionLevel(str, enum.Enum):
    OWNER = "owner"       # Full control - created the chatbot
    ADMIN = "admin"       # Can edit, manage, view analytics
    EDITOR = "editor"     # Can edit configuration
    VIEWER = "viewer"     # Can only view, no changes
    CUSTOM = "custom"     # Custom granular permissions


class ChatbotPermission(Base):
    __tablename__ = "chatbot_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False, index=True)
    permission_level = Column(Enum(PermissionLevel, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PermissionLevel.VIEWER)
    
    # Granular permissions
    can_manage_knowledge = Column(Boolean, default=False, nullable=False)
    can_manage_appearance = Column(Boolean, default=False, nullable=False)
    can_resolve_queries = Column(Boolean, default=False, nullable=False)
    can_view_analytics = Column(Boolean, default=False, nullable=False)
    
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Unique constraint - one permission per user per chatbot
    __table_args__ = (
        UniqueConstraint('user_id', 'chatbot_id', name='uq_user_chatbot'),
    )

    # Relationships
    user = relationship("User", back_populates="chatbot_permissions", foreign_keys=[user_id])
    chatbot = relationship("Chatbot", back_populates="permissions")
    granter = relationship("User", foreign_keys=[granted_by])

