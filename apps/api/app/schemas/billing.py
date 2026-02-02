"""Billing and subscription schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum



class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIALING = "trialing"


class PlanLimits(BaseModel):
    """Plan limits configuration"""
    chatbots: int
    messages_per_month: int
    conversations_per_month: int
    knowledge_pages: int
    knowledge_files: int
    team_members: int
    api_calls_per_month: int
    storage_mb: int


class PlanPricing(BaseModel):
    """Plan pricing details"""
    monthly_price: Decimal
    annual_price: Decimal
    annual_discount_percent: int = 20


class PlanFeatures(BaseModel):
    """Plan features"""
    name: str
    description: str
    limits: PlanLimits
    pricing: PlanPricing
    features: List[str]
    popular: bool = False


class CurrentUsage(BaseModel):
    """Current usage metrics"""
    chatbots_count: int
    messages_count: int
    global_message_count: int  # Total messages across all bots (persists after deletion)
    conversations_count: int
    knowledge_pages_count: int
    knowledge_files_count: int
    team_members_count: int
    api_calls_count: int
    storage_mb: Decimal
    period_start: datetime
    period_end: datetime


class SubscriptionResponse(BaseModel):
    """Subscription details response"""
    id: UUID
    tenant_id: int
    plan_type: PlanType
    billing_cycle: Optional[BillingCycle]
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UsageWithLimits(BaseModel):
    """Usage with plan limits for comparison"""
    current_usage: CurrentUsage
    plan_limits: PlanLimits
    usage_percentages: dict  # key: metric_name, value: percentage


class BillingHistoryItem(BaseModel):
    """Billing history entry"""
    id: UUID
    amount: Decimal
    description: str
    invoice_number: Optional[str]
    payment_status: str
    billing_period_start: datetime
    billing_period_end: datetime
    created_at: datetime


class BillingOverviewResponse(BaseModel):
    """Complete billing overview"""
    subscription: SubscriptionResponse
    current_plan: PlanFeatures
    usage: UsageWithLimits
    billing_history: List[BillingHistoryItem]
    available_plans: List[PlanFeatures]


class ChangePlanRequest(BaseModel):
    """Request to change subscription plan"""
    new_plan: PlanType
    billing_cycle: BillingCycle
    

class ChangePlanResponse(BaseModel):
    """Response after changing plan"""
    success: bool
    message: str
    subscription: SubscriptionResponse
    effective_date: datetime


class ChatbotUsage(BaseModel):
    """Per-chatbot usage metrics"""
    chatbot_id: str
    chatbot_name: str
    message_count: int
    conversation_count: int
    knowledge_pages_count: int
    storage_mb: float
    created_at: datetime
    

class UsageOverviewResponse(BaseModel):
    """Usage overview with per-chatbot breakdown"""
    global_message_count: int
    total_conversations: int
    total_knowledge_pages: int
    total_knowledge_files: int
    total_storage_mb: Decimal
    per_chatbot_usage: List[ChatbotUsage]
    period_start: datetime
    period_end: datetime