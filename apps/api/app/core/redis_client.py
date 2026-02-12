"""
Redis client with graceful degradation.

If Redis is unavailable, the app continues to function:
- Rate limiting falls back to in-memory (per-worker)
- Query caching is simply disabled

Uses redis-py (redis.asyncio) — the modern async Redis client.
"""

import redis.asyncio as aioredis
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_pool: Optional[aioredis.Redis] = None
_redis_available: bool = False


async def init_redis() -> bool:
    """
    Initialize the Redis connection pool.
    Call during app startup (lifespan).
    Returns True if Redis connected successfully.
    """
    global _redis_pool, _redis_available

    if not settings.REDIS_URL:
        logger.info("REDIS_URL not configured — Redis features disabled (in-memory rate limiting)")
        _redis_available = False
        return False

    try:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Test the connection
        await _redis_pool.ping()
        _redis_available = True
        logger.info("Redis connected successfully")
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} — falling back to in-memory")
        _redis_pool = None
        _redis_available = False
        return False


async def close_redis():
    """Close the Redis connection pool. Call during app shutdown."""
    global _redis_pool, _redis_available
    if _redis_pool:
        try:
            await _redis_pool.aclose()
        except Exception:
            pass
        _redis_pool = None
        _redis_available = False
        logger.info("Redis connection closed")


def is_redis_available() -> bool:
    """Check if Redis is available without making a network call."""
    return _redis_available


async def get_redis() -> Optional[aioredis.Redis]:
    """
    Get the Redis client instance.
    Returns None if Redis is not available.
    """
    if not _redis_available or not _redis_pool:
        return None

    try:
        await _redis_pool.ping()
        return _redis_pool
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return None
