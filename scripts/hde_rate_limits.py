"""Rate and budget controls for the HDE Telegram head-bot router.

The router must survive bursty fan-in from a shared public Telegram bot.  This
module gives it a small, dependency-light token bucket with a Redis backend when
`HDE_REDIS_URL`/`REDIS_URL` is configured, and a process-local fallback for
staging/dev.  The fallback is not a distributed production control; it keeps the
service bounded when Redis is absent.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger("hde-rate-limits")


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int
    key: str
    remaining: int
    backend: str


class _RedisLike(Protocol):
    async def eval(self, script: str, numkeys: int, *args): ...

    async def ping(self) -> bool: ...


class InMemoryTokenBucket:
    """Process-local token bucket for staging/dev and Redis outages."""

    def __init__(self) -> None:
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def consume(self, key: str, capacity: int, refill_per_second: float, cost: int = 1) -> RateLimitDecision:
        now = time.monotonic()
        async with self._lock:
            tokens, updated_at = self._buckets.get(key, (float(capacity), now))
            elapsed = max(0.0, now - updated_at)
            tokens = min(float(capacity), tokens + elapsed * refill_per_second)
            if tokens >= cost:
                tokens -= cost
                self._buckets[key] = (tokens, now)
                return RateLimitDecision(True, 0, key, int(tokens), "memory")
            retry_after = int(max(1, (cost - tokens) / refill_per_second)) if refill_per_second > 0 else 60
            self._buckets[key] = (tokens, now)
            return RateLimitDecision(False, retry_after, key, int(tokens), "memory")


class RedisTokenBucket:
    """Redis-backed token bucket shared across router processes."""

    _SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])
local now = tonumber(ARGV[4])
local ttl = tonumber(ARGV[5])
local current = redis.call('HMGET', key, 'tokens', 'updated_at')
local tokens = tonumber(current[1])
local updated_at = tonumber(current[2])
if tokens == nil then tokens = capacity end
if updated_at == nil then updated_at = now end
local elapsed = math.max(0, now - updated_at)
tokens = math.min(capacity, tokens + elapsed * refill)
local allowed = 0
local retry_after = 0
if tokens >= cost then
  allowed = 1
  tokens = tokens - cost
else
  if refill > 0 then
    retry_after = math.max(1, math.ceil((cost - tokens) / refill))
  else
    retry_after = ttl
  end
end
redis.call('HMSET', key, 'tokens', tokens, 'updated_at', now)
redis.call('EXPIRE', key, ttl)
return {allowed, retry_after, math.floor(tokens)}
"""

    def __init__(self, client: _RedisLike) -> None:
        self.client = client

    async def consume(self, key: str, capacity: int, refill_per_second: float, cost: int = 1) -> RateLimitDecision:
        ttl = max(60, int((capacity / max(refill_per_second, 0.0001)) * 2))
        result = await self.client.eval(
            self._SCRIPT,
            1,
            key,
            capacity,
            refill_per_second,
            cost,
            time.time(),
            ttl,
        )
        allowed, retry_after, remaining = result or (0, ttl, 0)
        return RateLimitDecision(bool(int(allowed)), int(retry_after), key, int(remaining), "redis")


class HeadBotRateLimiter:
    def __init__(
        self,
        *,
        per_user_per_minute: int,
        global_per_second: int,
        backend: InMemoryTokenBucket | RedisTokenBucket,
    ) -> None:
        self.per_user_per_minute = max(1, per_user_per_minute)
        self.global_per_second = max(1, global_per_second)
        self.backend = backend

    async def check_chat(self, chat_id: int) -> RateLimitDecision:
        global_decision = await self.backend.consume(
            "hde:rate:global:chat",
            capacity=self.global_per_second,
            refill_per_second=float(self.global_per_second),
        )
        if not global_decision.allowed:
            return global_decision
        return await self.backend.consume(
            f"hde:rate:user:{chat_id}",
            capacity=self.per_user_per_minute,
            refill_per_second=self.per_user_per_minute / 60.0,
        )


async def create_rate_limiter_from_env() -> HeadBotRateLimiter:
    per_user = int(os.getenv("HDE_ROUTER_PER_USER_MESSAGES_PER_MINUTE", "12"))
    global_rps = int(os.getenv("HDE_ROUTER_GLOBAL_MESSAGES_PER_SECOND", "150"))
    redis_url = os.getenv("HDE_REDIS_URL") or os.getenv("REDIS_URL")

    backend: InMemoryTokenBucket | RedisTokenBucket
    if redis_url:
        try:
            from redis.asyncio import Redis  # type: ignore

            client = Redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            backend = RedisTokenBucket(client)
            logger.info("Using Redis-backed HDE rate limiter")
        except Exception as exc:
            logger.warning("Redis rate limiter unavailable; falling back to memory: %s", exc)
            backend = InMemoryTokenBucket()
    else:
        backend = InMemoryTokenBucket()
        logger.info("Using in-memory HDE rate limiter; configure HDE_REDIS_URL for production")

    return HeadBotRateLimiter(
        per_user_per_minute=per_user,
        global_per_second=global_rps,
        backend=backend,
    )
