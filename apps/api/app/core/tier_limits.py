"""
Tier-based usage limits and quota management
"""
from enum import Enum
from typing import Dict, Any

class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# Tier limits configuration
TIER_LIMITS = {
    UserTier.FREE: {
        'max_chatbots': 1,
        'max_knowledge_sources': 10,
        'max_total_crawled_pages': 300,  # Total pages across all sources
        'max_file_size_mb': 5,
        'max_files': 3,
        'max_qa_pairs_per_source': 10,
        'max_messages_per_month': 100,
        'max_embeddings': 5000,
        'allow_auto_recrawl': False,
        'allow_analytics': False,
    },
    UserTier.PRO: {
        'max_chatbots': 5,
        'max_knowledge_sources': 50,
        'max_total_crawled_pages': 10000,
        'max_file_size_mb': 50,
        'max_files': 100,
        'max_qa_pairs_per_source': 100,
        'max_messages_per_month': 10000,
        'max_embeddings': 100000,
        'allow_auto_recrawl': True,
        'allow_analytics': True,
    },
    UserTier.ENTERPRISE: {
        'max_chatbots': 999999,
        'max_knowledge_sources': 999999,
        'max_total_crawled_pages': 999999,
        'max_file_size_mb': 500,
        'max_files': 999999,
        'max_qa_pairs_per_source': 999999,
        'max_messages_per_month': 999999,
        'max_embeddings': 999999,
        'allow_auto_recrawl': True,
        'allow_analytics': True,
    }
}

def get_tier_limits(tier: str = "free") -> Dict[str, Any]:
    """Get limits for a specific tier"""
    tier_enum = UserTier(tier.lower())
    return TIER_LIMITS[tier_enum]

def get_limit(tier: str, limit_key: str) -> Any:
    """Get a specific limit value for a tier"""
    limits = get_tier_limits(tier)
    return limits.get(limit_key)
