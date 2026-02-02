import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Enum as SAEnum, func, TypeDecorator, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, enum.Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIALING = "trialing"


class PlanTypeDB(TypeDecorator):
    """Custom type for PlanType enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("free", "pro", "enterprise", name="plantype", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, PlanType): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return PlanType(value)


class BillingCycleDB(TypeDecorator):
    """Custom type for BillingCycle enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("monthly", "annual", name="billingcycle", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, BillingCycle): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return BillingCycle(value)


class SubscriptionStatusDB(TypeDecorator):
    """Custom type for SubscriptionStatus enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("active", "cancelled", "expired", "trialing", name="subscriptionstatus", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, SubscriptionStatus): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return SubscriptionStatus(value)


class Subscription(Base):
    """Tenant subscription information"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True, index=True)
    plan_type = Column(PlanTypeDB(), nullable=False, default=PlanType.FREE)
    billing_cycle = Column(BillingCycleDB(), nullable=True)  # Null for free plan
    status = Column(SubscriptionStatusDB(), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Billing dates
    current_period_start = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription", cascade="all, delete-orphan")
    billing_history = relationship("BillingHistory", back_populates="subscription", cascade="all, delete-orphan")


class UsageRecord(Base):
    """Monthly usage tracking for tenants"""
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subscription_id = Column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    
    # Usage metrics
    chatbots_count = Column(Integer, nullable=False, default=0)
    messages_count = Column(Integer, nullable=False, default=0)
    conversations_count = Column(Integer, nullable=False, default=0)
    knowledge_pages_count = Column(Integer, nullable=False, default=0)
    knowledge_files_count = Column(Integer, nullable=False, default=0)
    team_members_count = Column(Integer, nullable=False, default=0)
    api_calls_count = Column(Integer, nullable=False, default=0)
    storage_mb = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Period tracking
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")


class BillingHistory(Base):
    """Billing transaction history"""
    __tablename__ = "billing_history"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subscription_id = Column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=False)
    invoice_number = Column(String(100), nullable=True)
    payment_status = Column(String(50), nullable=False, default="paid")  # paid, pending, failed
    
    # Billing period
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="billing_history")
