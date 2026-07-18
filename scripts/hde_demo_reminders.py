#!/usr/bin/env python3
"""HDE Sanctuary demo reminder sender.

Runs idempotently. Sends day-7/day-12/expiry/pre-deletion reminders when a
user has a linked Telegram chat. Email fallback is intentionally dry-run by
default until SMTP/customer-mail policy is approved.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from shared.database import User, async_session_factory  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("hde-demo-reminders")

STATE_FILE = Path(os.getenv("HDE_DEMO_REMINDER_STATE_FILE", "/home/ubuntu/work/hd-platform-staging/.runtime/demo_reminders_sent.json"))
BOT_TOKEN = os.getenv("HDE_COACH_BOT_TOKEN", "")
DRY_RUN = os.getenv("HDE_DEMO_REMINDER_DRY_RUN", "0").lower() in {"1", "true", "yes", "on"}
UPGRADE_URL = os.getenv("HDE_DEMO_UPGRADE_URL", "https://staging.humandesignengine.com/deconditioning/")


def aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def load_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"sent": {}}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_FILE)


def reminder_for(user: User, now: datetime) -> tuple[str, str] | None:
    expires = aware(getattr(user, "trial_expires_at", None))
    if not expires:
        return None
    days_left = int((expires - now).total_seconds() // 86400)
    access_status = (getattr(user, "access_status", "") or "").lower()
    if access_status == "demo":
        if days_left == 7:
            return "day7", "You have about 7 days left in your Human Design Sanctuary demo. Bring one real-life pattern and let the room work with you."
        if days_left == 2:
            return "day12", f"Your Sanctuary demo has about 2 days left. If you want to keep this same space, upgrade here: {UPGRADE_URL}"
        if days_left <= 0:
            return "expiry", f"Your 14-day Sanctuary demo ends today. Your space pauses instead of disappearing. Upgrade to keep going: {UPGRADE_URL}"
    if access_status == "expired_demo":
        deletion_at = aware(getattr(user, "deletion_scheduled_at", None))
        if deletion_at is not None:
            deletion_days_left = int((deletion_at - now).total_seconds() // 86400)
            if deletion_days_left == 7:
                return "predelete7", f"Your paused Sanctuary demo workspace is scheduled for deletion in about 7 days. Upgrade if you want to keep this space: {UPGRADE_URL}"
    return None


async def send_telegram(chat_id: str, text: str) -> bool:
    if not BOT_TOKEN:
        logger.warning("Telegram reminder skipped; HDE_COACH_BOT_TOKEN missing")
        return False
    if DRY_RUN:
        logger.info("DRY_RUN Telegram reminder chat_id=%s text=%s", chat_id, text[:120])
        return True
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
        if resp.status_code != 200:
            logger.error("Telegram reminder failed chat_id=%s status=%s body=%s", chat_id, resp.status_code, resp.text[:300])
            return False
        return True


async def run() -> int:
    now = datetime.now(timezone.utc)
    state = load_state()
    sent = state.setdefault("sent", {})
    considered = delivered = skipped = 0
    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .where(User.access_status.in_(["demo", "expired_demo"]))
            .options(selectinload(User.bot_instance))
        )
        users = result.scalars().all()
        for user in users:
            reminder = reminder_for(user, now)
            if not reminder:
                continue
            considered += 1
            key, text = reminder
            state_key = f"{user.id}:{key}"
            if sent.get(state_key):
                skipped += 1
                continue
            chat_id = getattr(getattr(user, "bot_instance", None), "telegram_user_id", None)
            if not chat_id:
                logger.info("reminder %s skipped user_id=%s no telegram link", key, user.id)
                skipped += 1
                continue
            if await send_telegram(str(chat_id), text):
                sent[state_key] = now.isoformat()
                delivered += 1
    save_state(state)
    logger.info("summary considered=%s delivered=%s skipped=%s dry_run=%s", considered, delivered, skipped, DRY_RUN)
    print(json.dumps({"considered": considered, "delivered": delivered, "skipped": skipped, "dry_run": DRY_RUN}))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
