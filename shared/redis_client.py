"""
Shared async Redis client for HD Platform.

Provides a process-wide lazy connection that is used by both the
rate limiter (middleware) and the FastAPI lifespan events.
"""

import os
from typing import Optional

import redis.asyncio as aioredis

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Return (or create) a process-wide shared Redis connection."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis
