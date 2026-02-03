"""Billing and usage tracking service"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import (
    Subscription, UsageRecord, BillingHistory,
    PlanType as DBPlanType, BillingCycle as DBBillingCycle, SubscriptionStatus as DBSubscriptionStatus
)
from app.models.tenant import Tenant
from app.models.user import User
from app.models.chatbot import Chatbot
from app.models.chat import ChatSession, ChatMessage
from app.models.knowledge import KnowledgeSource, CrawledPage, UploadedFile
from app.schemas.billing import (
    PlanType, BillingCycle, PlanLimits, PlanPricing, PlanFeatures,
    CurrentUsage, SubscriptionResponse, UsageWithLimits, BillingHistoryItem,
    BillingOverviewResponse, ChangePlanRequest, ChangePlanResponse
)
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.core.logging import get_logger

logger = get_logger(__name__)


# Plan configurations
PLAN_CONFIGS = {
    PlanType.FREE: PlanFeatures(
        name="Free",
        description="Perfect for trying out our chatbot platform",
        limits=PlanLimits(
            chatbots=1,
            messages_per_month=5,
            conversations_per_month=5,
            knowledge_pages=5,
            knowledge_files=5,
            team_members=1,
            api_calls_per_month=1000,
            storage_mb=5
        ),
        pricing=PlanPricing(
            monthly_price=Decimal("0.00"),
            annual_price=Decimal("0.00"),
            annual_discount_percent=0
        ),
        features=[
            "1 Chatbot",
            "5 messages/month",
            "5 conversations/month",
            "5 knowledge pages",
            "5 file uploads",
            "1 team member",
            "Basic analytics",
            "Email support"
        ],
        popular=False
    ),
    PlanType.PRO: PlanFeatures(
        name="Pro",
        description="For growing teams and businesses",
        limits=PlanLimits(
            chatbots=10,
            messages_per_month=10000,
            conversations_per_month=5000,
            knowledge_pages=1000,
            knowledge_files=100,
            team_members=10,
            api_calls_per_month=50000,
            storage_mb=5000
        ),
        pricing=PlanPricing(
            monthly_price=Decimal("29.00"),
            annual_price=Decimal("278.40"),  # 20% discount
            annual_discount_percent=20
        ),
        features=[
            "10 Chatbots",
            "10,000 messages/month",
            "5,000 conversations/month",
            "1,000 knowledge pages",
            "100 file uploads",
            "10 team members",
            "Advanced analytics",
            "Priority email support",
            "Custom branding",
            "API access"
        ],
        popular=True
    ),
    PlanType.ENTERPRISE: PlanFeatures(
        name="Enterprise",
        description="For large organizations with advanced needs",
        limits=PlanLimits(
            chatbots=100,
            messages_per_month=100000,
            conversations_per_month=50000,
            knowledge_pages=10000,
            knowledge_files=1000,
            team_members=100,
            api_calls_per_month=500000,
            storage_mb=50000
        ),
        pricing=PlanPricing(
            monthly_price=Decimal("99.00"),
            annual_price=Decimal("950.40"),  # 20% discount
            annual_discount_percent=20
        ),
        features=[
            "100 Chatbots",
            "100,000 messages/month",
            "50,000 conversations/month",
            "10,000 knowledge pages",
            "1,000 file uploads",
            "100 team members",
            "Advanced analytics & reporting",
            "24/7 priority support",
            "Custom branding",
            "API access",
            "Dedicated account manager",
            "Custom integrations",
            "SLA guarantee"
        ],
        popular=False
    ),
}


class BillingService:
    """Service for managing subscriptions and usage tracking"""

    @staticmethod
    async def get_or_create_subscription(
        db: AsyncSession,
        tenant_id: int
    ) -> Subscription:
        """Get or create subscription for tenant"""
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            # Create default free subscription
            subscription = Subscription(
                tenant_id=tenant_id,
                plan_type=DBPlanType.FREE,
                billing_cycle=None,
                status=DBSubscriptionStatus.ACTIVE,
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc) + timedelta(days=30)
            )
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            logger.info(f"Created free subscription for tenant {tenant_id}")

        return subscription

    @staticmethod
    async def calculate_current_usage(
        db: AsyncSession,
        tenant_id: int,
        period_start: datetime,
        period_end: datetime
    ) -> CurrentUsage:
        """Calculate current usage for tenant in the given period"""
        
        # Get subscription for global message count
        subscription = await BillingService.get_or_create_subscription(db, tenant_id)
        
        # Count chatbots (excluding deleted)
        chatbots_result = await db.execute(
            select(func.count(Chatbot.id)).where(
                and_(
                    Chatbot.tenant_id == tenant_id,
                    Chatbot.deleted_at.is_(None)
                )
            )
        )
        chatbots_count = chatbots_result.scalar() or 0

        # Get chatbot IDs for tenant
        chatbots_stmt = select(Chatbot.id).where(
            and_(
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None)
            )
        )
        chatbot_ids_result = await db.execute(chatbots_stmt)
        chatbot_ids = [row[0] for row in chatbot_ids_result.all()]

        # Count conversations in period (exclude preview)
        conversations_result = await db.execute(
            select(func.count(ChatSession.id)).where(
                and_(
                    ChatSession.chatbot_id.in_(chatbot_ids) if chatbot_ids else False,
                    ChatSession.started_at >= period_start,
                    ChatSession.started_at < period_end,
                    ChatSession.is_preview == False
                )
            )
        )
        conversations_count = conversations_result.scalar() or 0

        # Count messages in period (exclude preview sessions)
        if chatbot_ids:
            preview_sessions_stmt = select(ChatSession.id).where(
                and_(
                    ChatSession.chatbot_id.in_(chatbot_ids),
                    ChatSession.is_preview == True
                )
            )
            preview_session_ids_result = await db.execute(preview_sessions_stmt)
            preview_session_ids = [row[0] for row in preview_session_ids_result.all()]
            
            messages_result = await db.execute(
                select(func.count(ChatMessage.id)).where(
                    and_(
                        ChatMessage.session_id.in_(
                            select(ChatSession.id).where(
                                and_(
                                    ChatSession.chatbot_id.in_(chatbot_ids),
                                    ChatSession.started_at >= period_start,
                                    ChatSession.started_at < period_end
                                )
                            )
                        ),
                        ~ChatMessage.session_id.in_(preview_session_ids) if preview_session_ids else True
                    )
                )
            )
            messages_count = messages_result.scalar() or 0
        else:
            messages_count = 0

        # Count knowledge pages
        if chatbot_ids:
            pages_result = await db.execute(
                select(func.count(CrawledPage.id)).where(
                    CrawledPage.knowledge_source_id.in_(
                        select(KnowledgeSource.id).where(
                            KnowledgeSource.chatbot_id.in_(chatbot_ids)
                        )
                    ),
                    CrawledPage.is_removed == False
                )
            )
            knowledge_pages_count = pages_result.scalar() or 0

            # Count knowledge files
            files_result = await db.execute(
                select(func.count(UploadedFile.id)).where(
                    UploadedFile.knowledge_source_id.in_(
                        select(KnowledgeSource.id).where(
                            KnowledgeSource.chatbot_id.in_(chatbot_ids)
                        )
                    )
                )
            )
            knowledge_files_count = files_result.scalar() or 0

            # Calculate storage
            storage_result = await db.execute(
                select(func.sum(UploadedFile.file_size)).where(
                    UploadedFile.knowledge_source_id.in_(
                        select(KnowledgeSource.id).where(
                            KnowledgeSource.chatbot_id.in_(chatbot_ids)
                        )
                    )
                )
            )
            storage_bytes = storage_result.scalar() or 0
            storage_mb = Decimal(storage_bytes) / Decimal(1024 * 1024)
        else:
            knowledge_pages_count = 0
            knowledge_files_count = 0
            storage_mb = Decimal("0")

        # Count team members
        team_members_result = await db.execute(
            select(func.count(User.id)).where(User.tenant_id == tenant_id)
        )
        team_members_count = team_members_result.scalar() or 0

        # API calls count (placeholder for now - would need separate tracking)
        api_calls_count = 0

        return CurrentUsage(
            chatbots_count=chatbots_count,
            messages_count=messages_count,
            global_message_count=subscription.global_message_count or 0,
            conversations_count=conversations_count,
            knowledge_pages_count=knowledge_pages_count,
            knowledge_files_count=knowledge_files_count,
            team_members_count=team_members_count,
            api_calls_count=api_calls_count,
            storage_mb=storage_mb,
            period_start=period_start,
            period_end=period_end
        )

    @staticmethod
    async def get_billing_overview(
        db: AsyncSession,
        tenant_id: int,
        user: User
    ) -> BillingOverviewResponse:
        """Get complete billing overview for tenant"""
        
        # Verify user belongs to tenant
        if user.tenant_id != tenant_id:
            raise ForbiddenError("Access denied")

        # Get or create subscription
        subscription = await BillingService.get_or_create_subscription(db, tenant_id)

        # Calculate current usage
        current_usage = await BillingService.calculate_current_usage(
            db,
            tenant_id,
            subscription.current_period_start,
            subscription.current_period_end
        )

        # Get plan details
        plan_type = PlanType(subscription.plan_type.value)
        current_plan = PLAN_CONFIGS[plan_type]

        # Calculate usage percentages
        usage_percentages = {
            "chatbots": (current_usage.chatbots_count / current_plan.limits.chatbots * 100) if current_plan.limits.chatbots > 0 else 0,
            "messages": (current_usage.global_message_count / current_plan.limits.messages_per_month * 100) if current_plan.limits.messages_per_month > 0 else 0,
            "conversations": (current_usage.conversations_count / current_plan.limits.conversations_per_month * 100) if current_plan.limits.conversations_per_month > 0 else 0,
            "knowledge_pages": (current_usage.knowledge_pages_count / current_plan.limits.knowledge_pages * 100) if current_plan.limits.knowledge_pages > 0 else 0,
            "knowledge_files": (current_usage.knowledge_files_count / current_plan.limits.knowledge_files * 100) if current_plan.limits.knowledge_files > 0 else 0,
            "team_members": (current_usage.team_members_count / current_plan.limits.team_members * 100) if current_plan.limits.team_members > 0 else 0,
            "storage": (float(current_usage.storage_mb) / current_plan.limits.storage_mb * 100) if current_plan.limits.storage_mb > 0 else 0,
        }

        usage_with_limits = UsageWithLimits(
            current_usage=current_usage,
            plan_limits=current_plan.limits,
            usage_percentages=usage_percentages
        )

        # Get billing history (last 12 months)
        history_result = await db.execute(
            select(BillingHistory)
            .where(BillingHistory.subscription_id == subscription.id)
            .order_by(BillingHistory.created_at.desc())
            .limit(12)
        )
        billing_history = [
            BillingHistoryItem(
                id=h.id,
                amount=h.amount,
                description=h.description,
                invoice_number=h.invoice_number,
                payment_status=h.payment_status,
                billing_period_start=h.billing_period_start,
                billing_period_end=h.billing_period_end,
                created_at=h.created_at
            )
            for h in history_result.scalars().all()
        ]

        # Get all available plans
        available_plans = list(PLAN_CONFIGS.values())

        subscription_response = SubscriptionResponse(
            id=subscription.id,
            tenant_id=subscription.tenant_id,
            plan_type=PlanType(subscription.plan_type.value),
            billing_cycle=BillingCycle(subscription.billing_cycle.value) if subscription.billing_cycle else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            trial_end=subscription.trial_end,
            cancelled_at=subscription.cancelled_at,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )

        return BillingOverviewResponse(
            subscription=subscription_response,
            current_plan=current_plan,
            usage=usage_with_limits,
            billing_history=billing_history,
            available_plans=available_plans
        )

    @staticmethod
    async def change_plan(
        db: AsyncSession,
        tenant_id: int,
        user: User,
        request: ChangePlanRequest
    ) -> ChangePlanResponse:
        """Change subscription plan"""
        
        # Verify user has admin role
        from app.models.user import UserRole
        from app.core.config import settings
        if user.role != UserRole.ADMIN and not settings.BILLING_MOCK_MODE:
            raise ForbiddenError("Only admins can change subscription plans")

        # Get subscription
        subscription = await BillingService.get_or_create_subscription(db, tenant_id)

        # Validate plan change
        current_plan = PlanType(subscription.plan_type.value)
        if current_plan == request.new_plan:
            raise BadRequestError("Already on this plan")

        # Check if downgrade would exceed new limits
        if request.new_plan == PlanType.FREE:
            current_usage = await BillingService.calculate_current_usage(
                db, tenant_id,
                subscription.current_period_start,
                subscription.current_period_end
            )
            new_limits = PLAN_CONFIGS[request.new_plan].limits
            
            errors = []
            if current_usage.chatbots_count > new_limits.chatbots:
                errors.append(f"You have {current_usage.chatbots_count} chatbots but Free plan allows only {new_limits.chatbots}")
            if current_usage.team_members_count > new_limits.team_members:
                errors.append(f"You have {current_usage.team_members_count} team members but Free plan allows only {new_limits.team_members}")
            
            if errors:
                raise BadRequestError("Cannot downgrade: " + "; ".join(errors))

        # Update subscription
        old_plan = subscription.plan_type.value
        subscription.plan_type = DBPlanType(request.new_plan.value)
        subscription.billing_cycle = DBBillingCycle(request.billing_cycle.value) if request.new_plan != PlanType.FREE else None
        subscription.updated_at = datetime.now(timezone.utc)

        # For demo purposes, apply immediately
        # In production, this would be handled at period end or through payment processor
        effective_date = datetime.now(timezone.utc)

        # Create billing history entry for plan change
        plan_config = PLAN_CONFIGS[request.new_plan]
        amount = plan_config.pricing.annual_price if request.billing_cycle == BillingCycle.ANNUAL else plan_config.pricing.monthly_price
        
        if request.new_plan != PlanType.FREE:
            billing_entry = BillingHistory(
                subscription_id=subscription.id,
                amount=amount,
                description=f"Plan changed from {old_plan} to {request.new_plan.value} ({request.billing_cycle.value})",
                invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{tenant_id}",
                payment_status="paid",
                billing_period_start=subscription.current_period_start,
                billing_period_end=subscription.current_period_end
            )
            db.add(billing_entry)

        await db.commit()
        await db.refresh(subscription)

        logger.info(f"Tenant {tenant_id} changed plan from {old_plan} to {request.new_plan.value}")

        subscription_response = SubscriptionResponse(
            id=subscription.id,
            tenant_id=subscription.tenant_id,
            plan_type=PlanType(subscription.plan_type.value),
            billing_cycle=BillingCycle(subscription.billing_cycle.value) if subscription.billing_cycle else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            trial_end=subscription.trial_end,
            cancelled_at=subscription.cancelled_at,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )

        return ChangePlanResponse(
            success=True,
            message=f"Successfully changed to {request.new_plan.value} plan",
            subscription=subscription_response,
            effective_date=effective_date
        )

    @staticmethod
    async def check_message_limit(db: AsyncSession, tenant_id: int) -> dict:
        """
        Check if tenant has exceeded message limit
        Returns: {exceeded: bool, current: int, limit: int, percentage: float}
        """
        try:
            # Get subscription and plan
            subscription = await BillingService.get_or_create_subscription(db, tenant_id)
            plan_type = PlanType(subscription.plan_type.value)
            plan_config = PLAN_CONFIGS[plan_type]
            limit = plan_config.limits.messages_per_month
            
            # Get global message count
            current = subscription.global_message_count or 0
            percentage = (current / limit * 100) if limit > 0 else 0
            
            return {
                "exceeded": current >= limit,
                "current": current,
                "limit": limit,
                "percentage": percentage,
                "plan": plan_type.value
            }
        except Exception as e:
            logger.error(f"Error checking message limit: {e}")
            return {
                "exceeded": False,
                "current": 0,
                "limit": 0,
                "percentage": 0,
                "plan": "unknown"
            }

    @staticmethod
    async def check_file_upload_limit(db: AsyncSession, tenant_id: int, chatbot_id: str) -> dict:
        """
        Check if tenant/chatbot has exceeded file upload limits
        Returns: {exceeded: bool, current: int, limit: int}
        """
        try:
            # Get subscription and plan
            subscription = await BillingService.get_or_create_subscription(db, tenant_id)
            plan_type = PlanType(subscription.plan_type.value)
            plan_config = PLAN_CONFIGS[plan_type]
            limit = plan_config.limits.knowledge_files
            
            # Count uploaded files for this chatbot
            files_result = await db.execute(
                select(func.count(UploadedFile.id)).where(
                    UploadedFile.knowledge_source_id.in_(
                        select(KnowledgeSource.id).where(
                            and_(
                                KnowledgeSource.chatbot_id == chatbot_id,
                                KnowledgeSource.source_type == "uploaded_file"
                            )
                        )
                    )
                )
            )
            current = files_result.scalar() or 0
            
            return {
                "exceeded": current >= limit,
                "current": current,
                "limit": limit,
                "chatbot_id": str(chatbot_id)
            }
        except Exception as e:
            logger.error(f"Error checking file upload limit: {e}")
            return {
                "exceeded": False,
                "current": 0,
                "limit": 0,
                "chatbot_id": str(chatbot_id)
            }

    @staticmethod
    async def check_conversation_limit(db: AsyncSession, tenant_id: int) -> dict:
        """
        Check if tenant has exceeded conversation limit for the current billing period
        Returns: {exceeded: bool, current: int, limit: int, percentage: float}
        """
        try:
            subscription = await BillingService.get_or_create_subscription(db, tenant_id)
            plan_type = PlanType(subscription.plan_type.value)
            plan_config = PLAN_CONFIGS[plan_type]
            limit = plan_config.limits.conversations_per_month

            current_usage = await BillingService.calculate_current_usage(
                db,
                tenant_id,
                subscription.current_period_start,
                subscription.current_period_end
            )
            current = current_usage.conversations_count
            percentage = (current / limit * 100) if limit > 0 else 0

            return {
                "exceeded": current >= limit,
                "current": current,
                "limit": limit,
                "percentage": percentage,
                "plan": plan_type.value
            }
        except Exception as e:
            logger.error(f"Error checking conversation limit: {e}")
            return {
                "exceeded": False,
                "current": 0,
                "limit": 0,
                "percentage": 0,
                "plan": "unknown"
            }

    @staticmethod
    async def check_storage_limit(db: AsyncSession, tenant_id: int, additional_bytes: int = 0) -> dict:
        """
        Check if tenant would exceed storage limit with an additional upload
        Returns: {exceeded: bool, current_mb: float, projected_mb: float, limit_mb: int, plan: str}
        """
        try:
            subscription = await BillingService.get_or_create_subscription(db, tenant_id)
            plan_type = PlanType(subscription.plan_type.value)
            plan_config = PLAN_CONFIGS[plan_type]
            limit_mb = plan_config.limits.storage_mb

            current_usage = await BillingService.calculate_current_usage(
                db,
                tenant_id,
                subscription.current_period_start,
                subscription.current_period_end
            )
            current_mb = Decimal(current_usage.storage_mb)
            additional_mb = Decimal(additional_bytes) / Decimal(1024 * 1024)
            projected_mb = current_mb + additional_mb

            return {
                "exceeded": projected_mb > Decimal(limit_mb),
                "current_mb": float(current_mb),
                "projected_mb": float(projected_mb),
                "limit_mb": limit_mb,
                "plan": plan_type.value
            }
        except Exception as e:
            logger.error(f"Error checking storage limit: {e}")
            return {
                "exceeded": False,
                "current_mb": 0.0,
                "projected_mb": 0.0,
                "limit_mb": 0,
                "plan": "unknown"
            }
