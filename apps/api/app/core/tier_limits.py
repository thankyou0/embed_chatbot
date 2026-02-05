"""
Tier-based usage limits adapter (deprecated).

This module now derives limits from BillingService.PLAN_CONFIGS to ensure
there is a single source of truth for plan limits.
"""
from enum import Enum
from typing import Dict, Any

from app.schemas.billing import PlanType
from app.services.billing_service import PLAN_CONFIGS


class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


def _get_plan(tier: str):
    tier_enum = UserTier(tier.lower())
    plan_type = PlanType(tier_enum.value)
    return PLAN_CONFIGS[plan_type]


def get_tier_limits(tier: str = "free") -> Dict[str, Any]:
    """Get limits for a specific tier (derived from billing plan configs)."""
    plan = _get_plan(tier)
    limits = plan.limits
    is_paid = plan.name.lower() != "free"

    return {
        "max_chatbots": limits.chatbots,
        "max_knowledge_sources": limits.knowledge_pages,  # legacy mapping
        "max_total_crawled_pages": limits.knowledge_pages,
        "max_file_size_mb": limits.storage_mb,  # legacy mapping
        "max_files": limits.knowledge_files,
        "max_qa_pairs_per_source": limits.knowledge_pages,  # legacy mapping
        "max_messages_per_month": limits.messages_per_month,
        "max_embeddings": limits.api_calls_per_month,  # legacy mapping
        "allow_auto_recrawl": is_paid,
        "allow_analytics": is_paid,
    }


def get_limit(tier: str, limit_key: str) -> Any:
    """Get a specific limit value for a tier (derived from billing configs)."""
    limits = get_tier_limits(tier)
    return limits.get(limit_key)
