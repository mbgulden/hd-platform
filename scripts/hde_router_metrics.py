#!/usr/bin/env python3
"""Operational metrics snapshot for the HDE Telegram head-bot router.

Reads the same `.env` values as staging, then reports DB counts, Redis queue depth,
rate/budget counter state, and running guest container count without printing
secrets. Intended for cron/watchdog use and pre-canary checks.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


load_env(ROOT / ".env")

from shared.database import BotInstance, Invitation, User, async_session_factory  # noqa: E402

STREAM_ENV = {
    "chat": ("HDE_ROUTER_CHAT_JOB_STREAM", "hde:router:chat-jobs", "HDE_ROUTER_CHAT_JOB_GROUP", "hde-router"),
    "wake": ("HDE_ROUTER_WAKE_JOB_STREAM", "hde:router:wake-jobs", "HDE_ROUTER_WAKE_JOB_GROUP", "hde-router"),
    "media": ("HDE_ROUTER_MEDIA_JOB_STREAM", "hde:router:media-jobs", "HDE_ROUTER_MEDIA_JOB_GROUP", "hde-router"),
}


async def db_metrics() -> dict[str, Any]:
    async with async_session_factory() as session:
        users = int((await session.execute(select(func.count()).select_from(User))).scalar_one())
        invitations = int((await session.execute(select(func.count()).select_from(Invitation))).scalar_one())
        bot_instances = int((await session.execute(select(func.count()).select_from(BotInstance))).scalar_one())
        active_instances = int((await session.execute(select(func.count()).select_from(BotInstance).where(BotInstance.status == "active"))).scalar_one())
    return {
        "users": users,
        "invitations": invitations,
        "bot_instances": bot_instances,
        "active_bot_instances": active_instances,
        "backend": "postgres" if (os.getenv("DATABASE_URL") or "").startswith("postgresql") else "sqlite",
    }


async def redis_metrics() -> dict[str, Any]:
    redis_url = os.getenv("HDE_REDIS_URL") or os.getenv("REDIS_URL")
    if not redis_url:
        return {"enabled": False, "ok": False, "reason": "redis_url_missing"}
    from redis.asyncio import Redis  # type: ignore

    client = Redis.from_url(redis_url, decode_responses=True)
    try:
        await client.ping()
        queues: dict[str, Any] = {}
        for lane, (stream_env, default_stream, group_env, default_group) in STREAM_ENV.items():
            stream = os.getenv(stream_env, default_stream)
            group = os.getenv(group_env, default_group)
            length = int(await client.xlen(stream))
            pending = 0
            consumers = 0
            try:
                pending_info = await client.xpending(stream, group)
                if isinstance(pending_info, dict):
                    pending = int(pending_info.get("pending", 0) or 0)
            except Exception:
                pending = 0
            try:
                consumer_info = await client.xinfo_consumers(stream, group)
                consumers = len(consumer_info or [])
            except Exception:
                consumers = 0
            queues[lane] = {"stream": stream, "group": group, "length": length, "pending": pending, "consumers": consumers}
        key_counts = {
            "rate_keys": await scan_count(client, "hde:rate:*"),
            "budget_user_keys": await scan_count(client, "hde:budget:user:*"),
            "budget_global_keys": await scan_count(client, "hde:budget:global:*"),
        }
        return {"enabled": True, "ok": True, "queues": queues, **key_counts}
    finally:
        await client.aclose()


async def scan_count(client, pattern: str) -> int:
    count = 0
    async for _ in client.scan_iter(pattern):
        count += 1
    return count


def docker_metrics() -> dict[str, Any]:
    commands = [
        ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        ["sudo", "-n", "docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
    ]
    proc = None
    errors: list[str] = []
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
        except Exception as exc:
            errors.append(str(exc))
            continue
        if proc.returncode == 0:
            break
        errors.append(proc.stderr.strip()[:300])
    if proc is None or proc.returncode != 0:
        return {"ok": False, "reason": "; ".join(error for error in errors if error)[:500]}
    guest_rows = [line for line in proc.stdout.splitlines() if line.startswith("guest-hermes")]
    healthy = sum(1 for line in guest_rows if "healthy" in line.lower())
    return {"ok": True, "guest_containers_running": len(guest_rows), "guest_containers_healthy": healthy}


async def collect_metrics() -> dict[str, Any]:
    load_env(ROOT / ".env")
    payload = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "router": {
            "max_concurrent_chats": int(os.getenv("HDE_ROUTER_MAX_CONCURRENT_CHATS", "1000")),
            "task_queue_limit": int(os.getenv("HDE_ROUTER_TASK_QUEUE_LIMIT", "5000")),
            "chat_timeout_seconds": float(os.getenv("HDE_ROUTER_CHAT_TIMEOUT_SECONDS", "45")),
            "redis_queue_enabled": os.getenv("HDE_ROUTER_USE_REDIS_QUEUE", "true").lower() not in {"0", "false", "no"},
            "budget_enabled": os.getenv("HDE_BUDGET_ENABLED", "true").lower() not in {"0", "false", "no"},
        },
    }
    results = await asyncio.gather(db_metrics(), redis_metrics(), asyncio.to_thread(docker_metrics), return_exceptions=True)
    for key, value in zip(("database", "redis", "docker"), results):
        if isinstance(value, Exception):
            payload[key] = {"ok": False, "reason": str(value)}
            payload["status"] = "warn"
        else:
            payload[key] = value
            if isinstance(value, dict) and value.get("ok") is False:
                payload["status"] = "warn"
    redis_payload = payload.get("redis") or {}
    for queue in (redis_payload.get("queues") or {}).values():
        if queue.get("pending", 0) > 0:
            payload["status"] = "warn"
    return payload


def to_prometheus(metrics: dict[str, Any]) -> str:
    lines = []
    db = metrics.get("database", {})
    for name in ("users", "invitations", "bot_instances", "active_bot_instances"):
        lines.append(f"hde_{name} {int(db.get(name, 0) or 0)}")
    redis = metrics.get("redis", {})
    for lane, queue in (redis.get("queues") or {}).items():
        lines.append(f'hde_queue_length{{lane="{lane}"}} {int(queue.get("length", 0) or 0)}')
        lines.append(f'hde_queue_pending{{lane="{lane}"}} {int(queue.get("pending", 0) or 0)}')
        lines.append(f'hde_queue_consumers{{lane="{lane}"}} {int(queue.get("consumers", 0) or 0)}')
    docker = metrics.get("docker", {})
    lines.append(f"hde_guest_containers_running {int(docker.get('guest_containers_running', 0) or 0)}")
    lines.append(f"hde_guest_containers_healthy {int(docker.get('guest_containers_healthy', 0) or 0)}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HDE router metrics snapshot")
    parser.add_argument("--format", choices=["json", "prometheus"], default="json")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    metrics = asyncio.run(collect_metrics())
    if args.format == "prometheus":
        print(to_prometheus(metrics), end="")
        return
    print(json.dumps(metrics, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
