from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Temporary password fields
    password_expires_at = Column(DateTime(timezone=True), nullable=True)  # When temp password expires
    must_change_password = Column(Boolean, default=False, nullable=False)  # Force password change on login
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who invited this member

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    created_chatbots = relationship("Chatbot", back_populates="creator", foreign_keys="Chatbot.created_by")
    chatbot_permissions = relationship("ChatbotPermission", back_populates="user", foreign_keys="ChatbotPermission.user_id")
    inviter = relationship("User", remote_side=[id], foreign_keys=[invited_by])

