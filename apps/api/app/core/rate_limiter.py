"""
Distributed rate limiter with Redis backend and in-memory fallback.

When Redis is available:
  - Uses atomic Lua script (INCR + EXPIRE in one round-trip)
  - Shared across all uvicorn workers → accurate limits

When Redis is unavailable:
  - Falls back to in-memory per-worker limiting
  - Effective limit = configured_limit * num_workers (acceptable for dev)
"""

import time
from collections import defaultdict
from typing import Optional

from fastapi import HTTPException, Request

from app.core.redis_client import get_redis, is_redis_available
from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------- Configuration ----------
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # per window

# ---------- In-memory fallback ----------
_memory_limits: dict[str, list[float]] = defaultdict(list)

# ---------- Lua script for atomic rate limiting ----------
# KEYS[1] = rate limit key
# ARGV[1] = window in seconds
# Returns: current count after increment
_RATE_LIMIT_LUA = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


async def _check_rate_limit_redis(key: str) -> int:
    """
    Increment and check rate limit using Redis.
    Returns the current request count.
    Raises HTTPException(429) if limit exceeded.
    """
    redis = await get_redis()
    if redis is None:
        # Redis became unavailable mid-request, fall back
        return _check_rate_limit_memory(key)

    try:
        count = await redis.eval(
            _RATE_LIMIT_LUA,
            1,  # number of keys
            key,
            RATE_LIMIT_WINDOW,
        )
        return int(count)
    except Exception as e:
        logger.warning(f"Redis rate limit error: {e} — falling back to memory")
        return _check_rate_limit_memory(key)


def _check_rate_limit_memory(key: str) -> int:
    """In-memory fallback rate limiter (per-worker)."""
    now = time.time()
    # Purge expired timestamps
    _memory_limits[key] = [t for t in _memory_limits[key] if now - t < RATE_LIMIT_WINDOW]
    _memory_limits[key].append(now)
    return len(_memory_limits[key])


async def check_rate_limit(request: Request, chatbot_id: Optional[str] = None):
    """
    Check rate limit for the incoming request.
    
    Rate limits by IP. When chatbot_id is provided, limits are per IP+chatbot
    so that one chatbot's traffic doesn't lock out another chatbot's users
    sharing the same IP.
    
    Raises HTTPException(429) if limit exceeded.
    """
    ip = request.client.host if request.client else "unknown"

    # Build key: rate_limit:{ip} or rate_limit:{ip}:{chatbot_id}
    if chatbot_id:
        key = f"rate_limit:{ip}:{chatbot_id}"
    else:
        key = f"rate_limit:{ip}"

    if is_redis_available():
        count = await _check_rate_limit_redis(key)
    else:
        count = _check_rate_limit_memory(key)

    if count > RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded: {key} ({count} requests)")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute.",
        )
