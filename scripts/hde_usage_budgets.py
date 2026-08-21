"""Per-user model/token budget guard for HDE guest chat.

Rate limits protect router health.  Budgets protect model spend.  The router
cannot see exact downstream MiniMax token accounting from guest containers yet,
so this guard reserves a conservative estimated token cost before forwarding a
chat turn.  It uses Redis counters when available and a process-local fallback
for staging/dev.
"""

from __future__ import annotations

import asyncio
import calendar
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger("hde-usage-budgets")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class BudgetDecision:
    allowed: bool
    reason: str
    estimated_tokens: int
    monthly_used: int
    monthly_limit: int
    daily_used: int
    daily_limit: int
    backend: str
    user_id: int = 0
    is_premium: bool = False

    @property
    def remaining_monthly_tokens(self) -> int:
        return max(0, self.monthly_limit - self.monthly_used)


@dataclass(frozen=True)
class BudgetLimits:
    monthly_tokens: int
    daily_tokens: int


class UsageBudgetGuard:
    def __init__(self, redis_client=None) -> None:
        self.redis = redis_client
        self._lock = asyncio.Lock()
        self._memory: dict[str, tuple[int, datetime]] = {}
        self.enabled = os.getenv("HDE_BUDGET_ENABLED", "true").lower() not in {"0", "false", "no"}
        self.chars_per_token = max(1, _env_int("HDE_BUDGET_CHARS_PER_TOKEN", 4))
        self.estimated_output_tokens = _env_int("HDE_BUDGET_ESTIMATED_OUTPUT_TOKENS", 900)
        self.standard_monthly_tokens = _env_int("HDE_BUDGET_STANDARD_MONTHLY_TOKENS", 450_000)
        self.premium_monthly_tokens = _env_int("HDE_BUDGET_PREMIUM_MONTHLY_TOKENS", 1_500_000)
        self.standard_daily_tokens = _env_int("HDE_BUDGET_STANDARD_DAILY_TOKENS", 90_000)
        self.premium_daily_tokens = _env_int("HDE_BUDGET_PREMIUM_DAILY_TOKENS", 250_000)
        self.global_daily_tokens = _env_int("HDE_BUDGET_GLOBAL_DAILY_TOKENS", 2_000_000)

    @classmethod
    async def from_env(cls) -> Optional["UsageBudgetGuard"]:
        if os.getenv("HDE_BUDGET_ENABLED", "true").lower() in {"0", "false", "no"}:
            logger.info("HDE usage budget guard disabled")
            return None
        redis_url = os.getenv("HDE_REDIS_URL") or os.getenv("REDIS_URL")
        if redis_url:
            try:
                from redis.asyncio import Redis  # type: ignore

                client = Redis.from_url(redis_url, decode_responses=True)
                await client.ping()
                logger.info("Using Redis-backed HDE usage budget guard")
                return cls(client)
            except Exception as exc:
                logger.warning("Redis usage budget unavailable; falling back to memory counters: %s", exc)
        return cls(None)

    def estimate_tokens(self, text: str) -> int:
        input_tokens = max(1, (len(text or "") + self.chars_per_token - 1) // self.chars_per_token)
        return input_tokens + self.estimated_output_tokens

    def limits_for_user(self, is_premium: bool) -> BudgetLimits:
        if is_premium:
            return BudgetLimits(self.premium_monthly_tokens, self.premium_daily_tokens)
        return BudgetLimits(self.standard_monthly_tokens, self.standard_daily_tokens)

    async def reserve_chat_turn(self, user_id: int, text: str, *, is_premium: bool = False) -> BudgetDecision:
        if not self.enabled:
            limits = self.limits_for_user(is_premium)
            return BudgetDecision(True, "disabled", 0, 0, limits.monthly_tokens, 0, limits.daily_tokens, self.backend, user_id, is_premium)
        estimated = self.estimate_tokens(text)
        limits = self.limits_for_user(is_premium)
        if self.redis is not None:
            return await self._reserve_redis(user_id, estimated, limits)
        return await self._reserve_memory(user_id, estimated, limits)

    @property
    def backend(self) -> str:
        return "redis" if self.redis is not None else "memory"

    def _month_key(self, user_id: int) -> str:
        return f"hde:budget:user:{user_id}:{datetime.now(timezone.utc):%Y-%m}"

    def _day_key(self, user_id: int) -> str:
        return f"hde:budget:user:{user_id}:{datetime.now(timezone.utc):%Y-%m-%d}"

    def _global_day_key(self) -> str:
        return f"hde:budget:global:{datetime.now(timezone.utc):%Y-%m-%d}"

    def _month_ttl_seconds(self) -> int:
        now = datetime.now(timezone.utc)
        last_day = calendar.monthrange(now.year, now.month)[1]
        expires = datetime(now.year, now.month, last_day, 23, 59, 59, tzinfo=timezone.utc) + timedelta(days=2)
        return max(60, int((expires - now).total_seconds()))

    def _day_ttl_seconds(self) -> int:
        now = datetime.now(timezone.utc)
        tomorrow = datetime(now.year, now.month, now.day, tzinfo=timezone.utc) + timedelta(days=2)
        return max(60, int((tomorrow - now).total_seconds()))

    async def _reserve_redis(self, user_id: int, estimated: int, limits: BudgetLimits) -> BudgetDecision:
        assert self.redis is not None
        month_key = self._month_key(user_id)
        day_key = self._day_key(user_id)
        global_key = self._global_day_key()
        pipe = self.redis.pipeline(transaction=True)
        pipe.incrby(month_key, estimated)
        pipe.incrby(day_key, estimated)
        pipe.incrby(global_key, estimated)
        pipe.expire(month_key, self._month_ttl_seconds())
        pipe.expire(day_key, self._day_ttl_seconds())
        pipe.expire(global_key, self._day_ttl_seconds())
        result = await pipe.execute()
        monthly_used = int(result[0])
        daily_used = int(result[1])
        global_used = int(result[2])
        reason = "ok"
        allowed = True
        if monthly_used > limits.monthly_tokens:
            reason = "monthly_budget_exceeded"
            allowed = False
        elif daily_used > limits.daily_tokens:
            reason = "daily_budget_exceeded"
            allowed = False
        elif global_used > self.global_daily_tokens:
            reason = "global_budget_exceeded"
            allowed = False
        if not allowed:
            # Best-effort rollback so rejected turns do not consume budget.
            rollback = self.redis.pipeline(transaction=False)
            rollback.decrby(month_key, estimated)
            rollback.decrby(day_key, estimated)
            rollback.decrby(global_key, estimated)
            await rollback.execute()
            monthly_used -= estimated
            daily_used -= estimated
        return BudgetDecision(allowed, reason, estimated, monthly_used, limits.monthly_tokens, daily_used, limits.daily_tokens, "redis", user_id, limits.monthly_tokens == self.premium_monthly_tokens)

    async def reconcile_chat_turn(self, decision: BudgetDecision, actual_tokens: Optional[int]) -> None:
        """Adjust reserved budget to actual provider usage when a guest reports it.

        The router reserves an estimate before forwarding.  If the guest returns
        exact model usage, this method applies the delta so Redis becomes a
        spend ledger instead of a pure estimate bucket.
        """
        if not decision.allowed or not actual_tokens or actual_tokens < 0:
            return
        delta = int(actual_tokens) - int(decision.estimated_tokens)
        if delta == 0:
            return
        if self.redis is not None:
            assert self.redis is not None
            pipe = self.redis.pipeline(transaction=False)
            pipe.incrby(self._month_key(decision.user_id), delta)
            pipe.incrby(self._day_key(decision.user_id), delta)
            pipe.incrby(self._global_day_key(), delta)
            await pipe.execute()
            logger.info(
                "Reconciled HDE usage for user %d estimated=%d actual=%d delta=%+d",
                decision.user_id,
                decision.estimated_tokens,
                actual_tokens,
                delta,
            )
            return
        async with self._lock:
            now = datetime.now(timezone.utc)
            for key in (self._month_key(decision.user_id), self._day_key(decision.user_id), self._global_day_key()):
                used, expires = self._memory.get(key, (0, now + timedelta(days=2)))
                self._memory[key] = (max(0, used + delta), expires)

    async def _reserve_memory(self, user_id: int, estimated: int, limits: BudgetLimits) -> BudgetDecision:
        async with self._lock:
            now = datetime.now(timezone.utc)
            month_key = self._month_key(user_id)
            day_key = self._day_key(user_id)
            global_key = self._global_day_key()
            self._memory = {k: v for k, v in self._memory.items() if v[1] > now}
            month_used = self._memory.get(month_key, (0, now + timedelta(days=32)))[0] + estimated
            day_used = self._memory.get(day_key, (0, now + timedelta(days=2)))[0] + estimated
            global_used = self._memory.get(global_key, (0, now + timedelta(days=2)))[0] + estimated
            reason = "ok"
            allowed = True
            if month_used > limits.monthly_tokens:
                reason = "monthly_budget_exceeded"
                allowed = False
            elif day_used > limits.daily_tokens:
                reason = "daily_budget_exceeded"
                allowed = False
            elif global_used > self.global_daily_tokens:
                reason = "global_budget_exceeded"
                allowed = False
            if allowed:
                self._memory[month_key] = (month_used, now + timedelta(seconds=self._month_ttl_seconds()))
                self._memory[day_key] = (day_used, now + timedelta(seconds=self._day_ttl_seconds()))
                self._memory[global_key] = (global_used, now + timedelta(seconds=self._day_ttl_seconds()))
            else:
                month_used -= estimated
                day_used -= estimated
            return BudgetDecision(allowed, reason, estimated, month_used, limits.monthly_tokens, day_used, limits.daily_tokens, "memory", user_id, limits.monthly_tokens == self.premium_monthly_tokens)


def budget_exceeded_message(decision: BudgetDecision) -> str:
    if decision.reason == "global_budget_exceeded":
        return "🟡 *Heavy traffic pause.* The shared model budget is cooling down. Please try again later."
    if decision.reason == "daily_budget_exceeded":
        return "🟡 *Daily reflection limit reached.* Your space is protected for today. Come back tomorrow, or upgrade when that option is available."
    return "🟡 *Monthly reflection limit reached.* Your Human Design Companion budget is used for this cycle."
