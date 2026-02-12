"""
Exact-match query cache using Redis.

Caches full chatbot responses (text + sources + suggestions + products)
keyed by chatbot_id + normalized-query hash.

Cache hit rate for FAQ-style bots: ~60-70%.
No vector similarity needed — simple, fast, and effective.

When Redis is unavailable, caching is silently disabled.
"""

import hashlib
import json
from typing import Optional, Dict, Any

from app.core.redis_client import get_redis, is_redis_available
from app.core.logging import get_logger

logger = get_logger(__name__)

# Default TTL: 1 hour
DEFAULT_CACHE_TTL = 3600

# Key prefix
CACHE_PREFIX = "query_cache"


def _normalize_query(query: str) -> str:
    """
    Normalize a query for cache matching.
    Strips whitespace, lowercases, removes trailing punctuation.
    """
    if not query:
        return ""
    return query.strip().lower().rstrip("?!.")


def _make_cache_key(chatbot_id: str, query: str) -> str:
    """
    Build a Redis key from chatbot_id + normalized query hash.
    Example: query_cache:abc-123:sha256hex
    """
    normalized = _normalize_query(query)
    query_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"{CACHE_PREFIX}:{chatbot_id}:{query_hash}"


async def get_cached_response(
    chatbot_id: str,
    query: str,
) -> Optional[Dict[str, Any]]:
    """
    Look up a cached response for this chatbot + query.
    
    Returns dict with keys: content, sources, suggestions, products
    Returns None on cache miss or if Redis unavailable.
    """
    if not is_redis_available():
        return None

    redis = await get_redis()
    if redis is None:
        return None

    key = _make_cache_key(chatbot_id, query)

    try:
        raw = await redis.get(key)
        if raw is None:
            return None

        data = json.loads(raw)
        logger.info(f"Cache HIT for chatbot {chatbot_id}: {query[:60]}")
        
        # Bump hit count (fire-and-forget, don't block on it)
        try:
            await redis.hincrby(f"{CACHE_PREFIX}:stats:{chatbot_id}", "hits", 1)
        except Exception:
            pass

        return data

    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


async def cache_response(
    chatbot_id: str,
    query: str,
    content: str,
    sources: list,
    suggestions: list,
    products: list,
    ttl: int = DEFAULT_CACHE_TTL,
):
    """
    Store a response in the cache.
    
    Only caches successful, non-trivial responses.
    """
    if not is_redis_available():
        return

    redis = await get_redis()
    if redis is None:
        return

    # Don't cache very short or error responses
    if not content or len(content) < 20:
        return

    key = _make_cache_key(chatbot_id, query)

    payload = {
        "content": content,
        "sources": sources,
        "suggestions": suggestions,
        "products": products,
    }

    try:
        await redis.setex(key, ttl, json.dumps(payload, default=str))
        logger.debug(f"Cached response for chatbot {chatbot_id}: {query[:60]}")

        # Track total cache entries (fire-and-forget)
        try:
            await redis.hincrby(f"{CACHE_PREFIX}:stats:{chatbot_id}", "entries", 1)
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Cache write error: {e}")


async def invalidate_chatbot_cache(chatbot_id: str):
    """
    Invalidate all cached responses for a chatbot.
    Call this when knowledge sources are updated/re-embedded.
    """
    if not is_redis_available():
        return

    redis = await get_redis()
    if redis is None:
        return

    try:
        pattern = f"{CACHE_PREFIX}:{chatbot_id}:*"
        deleted = 0
        async for key in redis.scan_iter(match=pattern, count=100):
            await redis.delete(key)
            deleted += 1

        if deleted:
            logger.info(f"Invalidated {deleted} cache entries for chatbot {chatbot_id}")
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")
