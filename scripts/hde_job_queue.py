"""Redis-backed durable queue for HDE Telegram head-bot jobs.

Telegram polling must stay thin.  Heavy work — onboarding, guide choice,
container wakeups, and guest chat forwarding — belongs behind a durable queue so
bursts survive router restarts and slow containers do not block `getUpdates`.

Uses Redis Streams when `HDE_REDIS_URL`/`REDIS_URL` is configured.  The router
falls back to direct in-process tasks when Redis is unavailable so staging stays
usable, but production should keep Redis enabled.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal, Optional

logger = logging.getLogger("hde-job-queue")

JobKind = Literal["start", "wake", "chat", "media"]
JobHandler = Callable[[JobKind, int, str], Awaitable[None]]


@dataclass(frozen=True)
class QueueConfig:
    stream: str = "hde:router:chat-jobs"
    group: str = "hde-router"
    consumer: str = f"{socket.gethostname()}-{os.getpid()}"
    maxlen: int = 100_000
    block_ms: int = 2_000
    batch_size: int = 25
    worker_count: int = 12
    idle_reclaim_ms: int = 60_000

    @classmethod
    def from_env(cls, kind: JobKind | None = None) -> "QueueConfig":
        if kind in {"start", "wake"}:
            default_stream = "hde:router:wake-jobs"
            prefix = "HDE_ROUTER_WAKE_JOB"
        elif kind == "media":
            default_stream = "hde:router:media-jobs"
            prefix = "HDE_ROUTER_MEDIA_JOB"
        else:
            default_stream = "hde:router:chat-jobs"
            prefix = "HDE_ROUTER_CHAT_JOB"
        legacy_stream = os.getenv("HDE_ROUTER_JOB_STREAM")
        legacy_workers = os.getenv("HDE_ROUTER_JOB_WORKERS")
        return cls(
            stream=os.getenv(f"{prefix}_STREAM", legacy_stream or default_stream),
            group=os.getenv(f"{prefix}_GROUP", os.getenv("HDE_ROUTER_JOB_GROUP", "hde-router")),
            consumer=os.getenv(f"{prefix}_CONSUMER", os.getenv("HDE_ROUTER_JOB_CONSUMER", f"{socket.gethostname()}-{os.getpid()}")),
            maxlen=int(os.getenv(f"{prefix}_STREAM_MAXLEN", os.getenv("HDE_ROUTER_JOB_STREAM_MAXLEN", "100000"))),
            block_ms=int(os.getenv(f"{prefix}_BLOCK_MS", os.getenv("HDE_ROUTER_JOB_BLOCK_MS", "2000"))),
            batch_size=int(os.getenv(f"{prefix}_BATCH_SIZE", os.getenv("HDE_ROUTER_JOB_BATCH_SIZE", "25"))),
            worker_count=int(os.getenv(f"{prefix}_WORKERS", legacy_workers or ("4" if kind in {"start", "wake", "media"} else "12"))),
            idle_reclaim_ms=int(os.getenv(f"{prefix}_IDLE_RECLAIM_MS", os.getenv("HDE_ROUTER_JOB_IDLE_RECLAIM_MS", "60000"))),
        )


class RedisJobQueue:
    def __init__(self, redis_client, config: QueueConfig, accepted_kinds: set[JobKind] | None = None) -> None:
        self.redis = redis_client
        self.config = config
        self.accepted_kinds = accepted_kinds or {"start", "chat", "media"}
        self._stop = asyncio.Event()
        self._workers: list[asyncio.Task] = []

    @classmethod
    async def from_env(cls) -> Optional["RedisJobQueue"]:
        redis_url = os.getenv("HDE_REDIS_URL") or os.getenv("REDIS_URL")
        use_queue = os.getenv("HDE_ROUTER_USE_REDIS_QUEUE", "true").lower() not in {"0", "false", "no"}
        if not redis_url or not use_queue:
            logger.info("Redis job queue disabled; router will use in-process tasks")
            return None
        try:
            from redis.asyncio import Redis  # type: ignore

            client = Redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            queue = cls(client, QueueConfig.from_env())
            await queue.ensure_group()
            logger.info(
                "Using Redis Streams queue %s group=%s workers=%d",
                queue.config.stream,
                queue.config.group,
                queue.config.worker_count,
            )
            return queue
        except Exception as exc:
            logger.warning("Redis job queue unavailable; falling back to in-process tasks: %s", exc)
            return None

    async def ensure_group(self) -> None:
        try:
            await self.redis.xgroup_create(self.config.stream, self.config.group, id="0", mkstream=True)
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def enqueue(self, kind: JobKind, chat_id: int, text: str) -> str:
        payload = {
            "kind": kind,
            "chat_id": str(chat_id),
            "text": text,
        }
        message_id = await self.redis.xadd(
            self.config.stream,
            payload,
            maxlen=self.config.maxlen,
            approximate=True,
        )
        return str(message_id)

    def start_workers(self, handler: JobHandler) -> None:
        for index in range(self.config.worker_count):
            task = asyncio.create_task(self._worker_loop(handler, index), name=f"hde-queue-worker-{index}")
            self._workers.append(task)

    async def stop_workers(self) -> None:
        self._stop.set()
        for task in self._workers:
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def pending_count(self) -> int:
        try:
            summary = await self.redis.xpending(self.config.stream, self.config.group)
            return int(summary.get("pending", 0)) if isinstance(summary, dict) else 0
        except Exception:
            return 0

    async def _worker_loop(self, handler: JobHandler, index: int) -> None:
        consumer = f"{self.config.consumer}-{index}"
        while not self._stop.is_set():
            try:
                await self._reclaim_idle(handler, consumer)
                response = await self.redis.xreadgroup(
                    self.config.group,
                    consumer,
                    {self.config.stream: ">"},
                    count=self.config.batch_size,
                    block=self.config.block_ms,
                )
                if not response:
                    continue
                for _stream_name, messages in response:
                    for message_id, fields in messages:
                        await self._handle_message(handler, message_id, fields)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("Queue worker %s failed loop: %s", consumer, exc)
                await asyncio.sleep(1)

    async def _reclaim_idle(self, handler: JobHandler, consumer: str) -> None:
        try:
            result = await self.redis.xautoclaim(
                self.config.stream,
                self.config.group,
                consumer,
                min_idle_time=self.config.idle_reclaim_ms,
                start_id="0-0",
                count=min(self.config.batch_size, 10),
            )
            messages = result[1] if isinstance(result, (list, tuple)) and len(result) > 1 else []
            for message_id, fields in messages:
                await self._handle_message(handler, message_id, fields)
        except Exception as exc:
            # Redis < 6.2 or transient failures should not kill normal reads.
            logger.debug("Idle queue reclaim skipped: %s", exc)

    async def _handle_message(self, handler: JobHandler, message_id: str, fields: dict) -> None:
        try:
            kind = fields.get("kind")
            chat_id = int(fields.get("chat_id", "0"))
            text = fields.get("text", "")
            if kind not in self.accepted_kinds or not chat_id:
                raise ValueError(f"invalid queue payload {fields!r}")
            await handler(kind, chat_id, text)  # type: ignore[arg-type]
            await self.redis.xack(self.config.stream, self.config.group, message_id)
        except Exception as exc:
            logger.exception("Queue job %s failed and remains pending for retry: %s", message_id, exc)


class RedisJobQueueSet:
    """Two-stream router queue: chat jobs cannot starve wake/provision jobs."""

    def __init__(self, queues: dict[JobKind, RedisJobQueue]) -> None:
        self.queues = queues

    @classmethod
    async def from_env(cls) -> Optional["RedisJobQueueSet"]:
        redis_url = os.getenv("HDE_REDIS_URL") or os.getenv("REDIS_URL")
        use_queue = os.getenv("HDE_ROUTER_USE_REDIS_QUEUE", "true").lower() not in {"0", "false", "no"}
        if not redis_url or not use_queue:
            logger.info("Redis split job queues disabled; router will use in-process tasks")
            return None
        try:
            from redis.asyncio import Redis  # type: ignore

            client = Redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            queues: dict[JobKind, RedisJobQueue] = {
                "start": RedisJobQueue(client, QueueConfig.from_env("start"), {"start", "wake"}),
                "chat": RedisJobQueue(client, QueueConfig.from_env("chat"), {"chat"}),
                "media": RedisJobQueue(client, QueueConfig.from_env("media"), {"media"}),
            }
            for queue in queues.values():
                await queue.ensure_group()
            logger.info(
                "Using Redis split queues chat=%s/%dw wake=%s/%dw media=%s/%dw",
                queues["chat"].config.stream,
                queues["chat"].config.worker_count,
                queues["start"].config.stream,
                queues["start"].config.worker_count,
                queues["media"].config.stream,
                queues["media"].config.worker_count,
            )
            return cls(queues)
        except Exception as exc:
            logger.warning("Redis split job queues unavailable; falling back to in-process tasks: %s", exc)
            return None

    async def enqueue(self, kind: JobKind, chat_id: int, text: str) -> str:
        queue_key: JobKind = "start" if kind == "wake" else kind
        return await self.queues[queue_key].enqueue(kind, chat_id, text)

    def start_workers(self, handler: JobHandler) -> None:
        for queue in self.queues.values():
            queue.start_workers(handler)

    async def stop_workers(self) -> None:
        await asyncio.gather(*(queue.stop_workers() for queue in self.queues.values()), return_exceptions=True)

    async def pending_count(self) -> int:
        counts = await asyncio.gather(*(queue.pending_count() for queue in self.queues.values()), return_exceptions=True)
        return sum(count for count in counts if isinstance(count, int))

    def streams(self) -> dict[str, str]:
        return {kind: queue.config.stream for kind, queue in self.queues.items()}


async def encode_queue_depth(queue: Optional[RedisJobQueue | RedisJobQueueSet]) -> str:
    if queue is None:
        return json.dumps({"enabled": False})
    payload = {"enabled": True, "pending": await queue.pending_count()}
    if isinstance(queue, RedisJobQueueSet):
        payload["streams"] = queue.streams()
    else:
        payload["stream"] = queue.config.stream
    return json.dumps(payload)
