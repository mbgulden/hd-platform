#!/usr/bin/env python3
"""Human Design Engine demo-trial lifecycle manager.

Run from cron/systemd at least daily.

Rules:
- demo users get active bot access until `users.trial_expires_at`.
- after expiry, bot is paused/stopped and the account is marked `expired_demo`.
- workspace/container deletion is delayed until `users.deletion_scheduled_at`
  (default: 30 days after deactivation), so upgrade/reactivation can restore the
  same container instead of deleting immediately.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload

sys.path.append(str(Path(__file__).resolve().parents[1]))
from shared.database import BotInstance, User, async_session_factory  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("hde-trial-lifecycle")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8001").rstrip("/")
ORCHESTRATOR_SHARED_SECRET = os.getenv("ORCHESTRATOR_SHARED_SECRET", "default_shared_secret")
DEMO_RETENTION_DAYS = int(os.getenv("HDE_DEMO_RETENTION_DAYS", "30"))
DRY_RUN = os.getenv("HDE_TRIAL_LIFECYCLE_DRY_RUN", "0").lower() in {"1", "true", "yes", "on"}


def aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def sign(payload: bytes) -> str:
    return hmac.new(ORCHESTRATOR_SHARED_SECRET.encode("utf-8"), payload, hashlib.sha256).hexdigest()


async def orchestrate(user_id: int, action: str, telegram_user_id: str | None = None) -> None:
    payload: dict[str, Any] = {"user_id": user_id, "action": action, "telegram_user_id": telegram_user_id}
    body = json.dumps(payload).encode("utf-8")
    if DRY_RUN:
        logger.info("DRY_RUN orchestrate user_id=%s action=%s", user_id, action)
        return
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{ORCHESTRATOR_URL}/api/orchestrate/provision",
            content=body,
            headers={"Content-Type": "application/json", "X-Signature": sign(body)},
        )
        if resp.status_code != 200:
            logger.error("orchestrator action=%s user_id=%s failed: HTTP %s %s", action, user_id, resp.status_code, resp.text[:500])
        else:
            logger.info("orchestrator action=%s user_id=%s ok", action, user_id)


async def run() -> int:
    now = datetime.now(timezone.utc)
    expired_count = 0
    purged_count = 0

    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .where(User.access_status == "demo")
            .options(selectinload(User.bot_instance))
        )
        demo_users = result.scalars().all()

        for user in demo_users:
            trial_expires_at = aware(user.trial_expires_at)
            if not trial_expires_at or trial_expires_at > now:
                continue
            user.access_status = "expired_demo"
            user.subscription_status = "inactive"
            user.deactivated_at = user.deactivated_at or now
            user.deletion_scheduled_at = user.deletion_scheduled_at or (now + timedelta(days=DEMO_RETENTION_DAYS))
            if user.bot_instance:
                user.bot_instance.status = "suspended"
            expired_count += 1
            logger.info("expired demo user_id=%s deletion_scheduled_at=%s", user.id, user.deletion_scheduled_at)
            await orchestrate(user.id, "stop", user.bot_instance.telegram_user_id if user.bot_instance else None)

        result = await session.execute(
            select(User)
            .where(User.access_status == "expired_demo")
            .options(selectinload(User.bot_instance))
        )
        expired_users = result.scalars().all()
        for user in expired_users:
            deletion_scheduled_at = aware(user.deletion_scheduled_at)
            if not deletion_scheduled_at or deletion_scheduled_at > now:
                continue
            if user.bot_instance:
                user.bot_instance.status = "deprovisioning"
            purged_count += 1
            logger.info("retention elapsed; deprovisioning user_id=%s", user.id)
            await orchestrate(user.id, "deprovision", user.bot_instance.telegram_user_id if user.bot_instance else None)

        if not DRY_RUN:
            await session.commit()
        else:
            await session.rollback()

    logger.info("summary expired=%s purged=%s dry_run=%s", expired_count, purged_count, DRY_RUN)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
