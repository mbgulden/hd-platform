"""
FastAPI middleware: API-key authentication & Redis-backed rate limiting.

Provides the ``require_api_key`` FastAPI dependency that:
1. Extracts the ``X-API-Key`` header from each request.
2. Looks up the key hash in the PostgreSQL ``api_keys`` table.
3. Enforces a per-tier token-bucket rate limit via Redis.
4. Attaches the matched APIKey model to the request for downstream use.
5. Logs usage into the ``usage_logs`` table.
"""

import hashlib
import logging
from typing import Optional

from fastapi import Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import APIKey, UsageLog, async_session_factory
from shared.redis_client import get_redis

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _hash_key(raw_key: str) -> str:
    """SHA-256 hex digest of a raw API key string."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Rate limiting (token bucket via Redis)
# ---------------------------------------------------------------------------


async def _check_rate_limit(api_key: APIKey) -> bool:
    """
    Token-bucket rate limiter backed by Redis.

    Bucket key per API key (hashed), capacity = rate_limit, refill = rate_limit per minute.
    Returns ``True`` if the request is allowed, ``False`` otherwise.
    """
    redis = await get_redis()
    bucket_key = f"rate_limit:{api_key.key_hash}"
    rate = api_key.rate_limit

    # redis.time() returns a list: [unix_seconds, microseconds]
    time_parts = await redis.time()
    now_sec: int = int(time_parts[0]) if isinstance(time_parts, list) else int(time_parts)

    lua_script = """
    local key = KEYS[1]
    local rate = tonumber(ARGV[1])
    local now = tonumber(ARGV[2])

    -- Retrieve or initialize bucket state: {"tokens": N, "last": timestamp}
    local state = redis.call("GET", key)
    local tokens = rate
    local last = now

    if state then
        local decoded = cjson.decode(state)
        tokens = decoded["tokens"]
        last = decoded["last"]

        -- Refill tokens based on elapsed time (60s window)
        local elapsed = now - last
        if elapsed > 0 then
            tokens = math.min(rate, tokens + (elapsed / 60) * rate)
            last = now
        end
    end

    if tokens >= 1 then
        tokens = tokens - 1
        redis.call("SET", key, cjson.encode({tokens = tokens, last = last}), "EX", 120)
        return 1
    else
        return 0
    end
    """
    allowed = await redis.eval(lua_script, 1, bucket_key, str(rate), str(now_sec))
    return bool(allowed)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


async def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """
    FastAPI dependency that validates the ``X-API-Key`` header.

    Raises ``401 Unauthorized`` when the key is missing, invalid, or
    the user has exceeded their rate limit.

    Returns the raw API key string so route handlers can access it.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    key_hash = _hash_key(x_api_key)

    async with async_session_factory() as session:
        session: AsyncSession
        result = await session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash)
        )
        api_key: Optional[APIKey] = result.scalar_one_or_none()

        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Enforce rate limit
        if not await _check_rate_limit(api_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded (tier: {api_key.tier}, {api_key.rate_limit}/min)",
            )

        # Log usage
        usage = UsageLog(
            api_key_id=api_key.id,
            endpoint=request.url.path,
        )
        session.add(usage)
        await session.commit()

    # Attach to request state for downstream middleware / routes
    request.state.api_key = api_key

    return x_api_key
