from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    chatbots = relationship("Chatbot", back_populates="tenant", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan")

