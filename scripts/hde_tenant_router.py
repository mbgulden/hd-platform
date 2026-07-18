import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Ensure the shared path is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.database import User, Invitation, BotInstance, async_session_factory
from hde_rate_limits import HeadBotRateLimiter, create_rate_limiter_from_env
from hde_job_queue import JobKind, RedisJobQueueSet
from hde_usage_budgets import UsageBudgetGuard, budget_exceeded_message

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hde-tenant-router")

# ── Environment Configurations ─────────────────────────────────────────
COACH_BOT_TOKEN = os.getenv("HDE_COACH_BOT_TOKEN", "mock_coach_bot_token")
ONBOARDING_BOT_USERNAME = os.getenv("HDE_ONBOARDING_BOT_USERNAME", "HDE_CoachBot").lstrip("@")
ORCHESTRATOR_SHARED_SECRET = os.getenv("ORCHESTRATOR_SHARED_SECRET", "default_shared_secret")
DEFAULT_HOST_NODE_IP = os.getenv("DEFAULT_HOST_NODE_IP", "127.0.0.1")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", f"http://{DEFAULT_HOST_NODE_IP}:8001").rstrip("/")
IP_CACHE = {}
GUIDE_PRESETS = {"1": "Ember", "2": "Mira", "ember": "Ember", "mira": "Mira"}
GUIDE_NAME_MAX_CHARS = int(os.getenv("HDE_GUIDE_NAME_MAX_CHARS", "40"))
ROUTER_MAX_CONCURRENT_CHATS = int(os.getenv("HDE_ROUTER_MAX_CONCURRENT_CHATS", "1000"))
ROUTER_TASK_QUEUE_LIMIT = int(os.getenv("HDE_ROUTER_TASK_QUEUE_LIMIT", "5000"))
ROUTER_CHAT_TIMEOUT_SECONDS = float(os.getenv("HDE_ROUTER_CHAT_TIMEOUT_SECONDS", "45"))
ROUTER_SEMAPHORE: asyncio.Semaphore | None = None
ACTIVE_TASKS: set[asyncio.Task] = set()
RATE_LIMITER: HeadBotRateLimiter | None = None
JOB_QUEUE: RedisJobQueueSet | None = None
BUDGET_GUARD: UsageBudgetGuard | None = None


cues_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "somatic_cues.json")
if not os.path.exists(cues_path):
    cues_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "somatic_cues.json")
if not os.path.exists(cues_path):
    cues_path = "/home/ubuntu/work/hd-platform/scripts/somatic_cues.json"

try:
    with open(cues_path, "r", encoding="utf-8") as f:
        SOMATIC_CUES = json.load(f)
    logger.info("Successfully loaded 360 somatic cues from %s", cues_path)
except Exception as e:
    logger.error("Failed to load somatic_cues.json: %s. Using simple fallback.", e)
    SOMATIC_CUES = {
        "ventral": ["Welcome back. Take a slow, deep breath. Activating space..."],
        "sympathetic": ["Welcome. Drop your shoulders and take a slow exhale. Activating..."],
        "dorsal": ["Welcome. Look around and find three shapes. Activating..."]
    }

def infer_polyvagal_state(text: str) -> str:
    """Infer a light nervous-system state for choosing a waiting cue.

    This is not diagnosis. It only turns container wake latency into a useful
    regulation moment instead of dead air.
    """
    raw = (text or "").lower()
    if re.search(r"\b(overwhelm|panic|anxious|anxiety|racing|urgent|mad|angry|fight|stressed|spinning|wired|activated|too much)\b", raw):
        return "sympathetic"
    if re.search(r"\b(numb|blank|freeze|frozen|tired|exhausted|hopeless|heavy|stuck|dissociated|dissociate)\b", raw):
        return "dorsal"
    if re.search(r"\b(calm|clear|okay|ready|curious|steady|grounded|present|settled)\b", raw):
        return "ventral"
    return "mixed"


def clean_polyvagal_cue(cue: str, guide_name: str = "your space") -> str:
    """Remove generator artifacts and make wake cues feel like Sanctuary copy."""
    cleaned = re.sub(r"\s*i=\d+\.", ".", cue or "")
    cleaned = re.sub(
        r"\b(Initializing coach|Preparing bot|Preparing sanctuary|Aligning energy|Activating sanctuary|Activating space|Activating|Opening reflection space|Opening your space|Waking up your space)\.\.\.",
        f"Opening {guide_name}...",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(
        r"\b(Initializing coach|Preparing bot|Preparing sanctuary|Aligning energy|Activating sanctuary|Activating space|Activating|Opening reflection space|Opening your space|Waking up your space)\.",
        f"Opening {guide_name}.",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    while ".." in cleaned:
        cleaned = cleaned.replace("..", ".")
    if not cleaned:
        cleaned = f"Your space is waking. Let your eyes land on one steady object while it opens."
    return cleaned


def get_polyvagal_cue(text: str = "", guide_name: str = "your space") -> str:
    """Select a nervous-system waiting cue from the cue database."""
    import random
    state = infer_polyvagal_state(text)
    category = state if state in SOMATIC_CUES else random.choice(["ventral", "sympathetic", "dorsal"])
    cue = random.choice(SOMATIC_CUES.get(category, ["Welcome back. Take a slow, deep breath. Opening your space..."]))
    return clean_polyvagal_cue(cue, guide_name)


def as_aware_utc(value: datetime) -> datetime:
    """Normalize DB datetimes for SQLite/Postgres parity before comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def user_access_state(user: Optional[User]) -> dict:
    """Return bot access status, including demo trial countdown handling."""
    if not user:
        return {"allowed": False, "kind": "missing", "message": "❌ *Error:* Account not found."}

    now = datetime.now(timezone.utc)
    access_status = (getattr(user, "access_status", None) or "paid").lower()
    trial_expires_at = getattr(user, "trial_expires_at", None)

    if access_status == "demo":
        if trial_expires_at:
            expires = as_aware_utc(trial_expires_at)
            if expires <= now:
                return {
                    "allowed": False,
                    "kind": "demo_expired",
                    "message": "Your 14-day Sanctuary demo has ended. Your private space is paused, not deleted. Upgrade to keep going: https://humandesignengine.com/deconditioning/",
                }
            seconds_left = int((expires - now).total_seconds())
            days_left = max(0, (seconds_left + 86399) // 86400)
            return {"allowed": True, "kind": "demo", "days_left": days_left, "expires_at": expires}
        return {"allowed": True, "kind": "demo", "days_left": None, "expires_at": None}

    if getattr(user, "subscription_status", None) == "active":
        return {"allowed": True, "kind": "paid"}

    return {
        "allowed": False,
        "kind": "inactive",
        "message": "Your Sanctuary access is currently inactive. Your space is paused, not deleted. Upgrade/reactivate here: https://humandesignengine.com/deconditioning/",
    }


async def mark_access_paused(bot_instance: BotInstance, kind: str) -> None:
    async with async_session_factory() as pause_session:
        res = await pause_session.execute(select(BotInstance).where(BotInstance.id == bot_instance.id).options(selectinload(BotInstance.user)))
        db_bot = res.scalar_one_or_none()
        if not db_bot:
            return
        db_bot.status = "suspended"
        if db_bot.user:
            now = datetime.now(timezone.utc)
            db_bot.user.subscription_status = "inactive"
            db_bot.user.access_status = "expired_demo" if kind == "demo_expired" else (db_bot.user.access_status or "inactive")
            db_bot.user.deactivated_at = db_bot.user.deactivated_at or now
            db_bot.user.deletion_scheduled_at = db_bot.user.deletion_scheduled_at or (now + timedelta(days=30))
        await pause_session.commit()


# ── HMAC Signature Helper ──────────────────────────────────────────────

def generate_hmac_signature(payload: bytes, secret: str) -> str:
    """Generate SHA-256 HMAC signature of the payload bytes."""
    return hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

async def get_container_ip(container_name: str) -> Optional[str]:
    """Retrieve container IP on the hde_private_net network via docker inspect."""
    if container_name in IP_CACHE:
        logger.info("IP cache hit for container %s: %s", container_name, IP_CACHE[container_name])
        return IP_CACHE[container_name]

    for cmd in (
        ("docker", "inspect", "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name),
        ("sudo", "docker", "inspect", "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name),
    ):
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                ip = stdout.decode().strip()
                if ip:
                    IP_CACHE[container_name] = ip
                    return ip
        except Exception as e:
            logger.error("Failed to get container IP for %s using %s: %s", container_name, cmd[0], e)
    return None

# ── Telegram Send Message Helpers ──────────────────────────────────────
async def send_telegram_message(client: httpx.AsyncClient, chat_id: int, text: str) -> None:
    """Send a Telegram message; fall back to plain text when Markdown parsing chokes."""
    url = f"https://api.telegram.org/bot{COACH_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        resp = await client.post(url, json=payload, timeout=10.0)
        if resp.status_code == 200:
            return
        body = resp.text or ""
        if "can't parse entities" in body.lower() or "parse" in body.lower():
            logger.warning("Telegram Markdown parse failed for %d; retrying plain text.", chat_id)
            plain = await client.post(url, json={"chat_id": chat_id, "text": text}, timeout=10.0)
            if plain.status_code != 200:
                logger.error("Failed to deliver plain Telegram message to %d: %s", chat_id, plain.text)
            return
        logger.error("Failed to deliver Telegram message to %d: %s", chat_id, body)
    except Exception as exc:
        logger.exception("Failed to connect to Telegram API: %s", exc)

async def send_telegram_photo(client: httpx.AsyncClient, chat_id: int, file_path: str) -> None:
    """Helper to send a photo file to a Telegram user."""
    url = f"https://api.telegram.org/bot{COACH_BOT_TOKEN}/sendPhoto"
    try:
        with open(file_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id}
            resp = await client.post(url, data=data, files=files, timeout=30.0)
            if resp.status_code != 200:
                logger.error("Failed to send photo to %d: %s", chat_id, resp.text)
            else:
                logger.info("Sent photo %s to chat %d", file_path, chat_id)
    except Exception as exc:
        logger.exception("Failed to send photo to Telegram: %s", exc)

async def send_telegram_document(client: httpx.AsyncClient, chat_id: int, file_path: str) -> None:
    """Helper to send a document file to a Telegram user."""
    url = f"https://api.telegram.org/bot{COACH_BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id}
            resp = await client.post(url, data=data, files=files, timeout=30.0)
            if resp.status_code != 200:
                logger.error("Failed to send document to %d: %s", chat_id, resp.text)
            else:
                logger.info("Sent document %s to chat %d", file_path, chat_id)
    except Exception as exc:
        logger.exception("Failed to send document to Telegram: %s", exc)

# ── Dynamic Container Activation Hook ───────────────────────────────
async def start_stopped_container(client: httpx.AsyncClient, bot_instance: BotInstance) -> bool:
    """Trigger the VM orchestrator start action via HMAC-signed payload."""
    target_url = f"{ORCHESTRATOR_URL}/api/orchestrate/provision"
    
    payload_dict = {
        "user_id": bot_instance.user_id,
        "action": "start"
    }
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    signature = generate_hmac_signature(payload_bytes, ORCHESTRATOR_SHARED_SECRET)
    headers = {"Content-Type": "application/json", "X-Signature": signature}
    
    try:
        logger.info("Waking up container for user %d on %s...", bot_instance.user_id, target_url)
        resp = await client.post(target_url, content=payload_bytes, headers=headers, timeout=15.0)
        if resp.status_code == 200:
            logger.info("Wakeup start trigger completed for user %d.", bot_instance.user_id)
            return True
        logger.error("Wakeup start request failed: %s", resp.text)
    except Exception as exc:
        logger.exception("Failed to communicate with orchestrator to start container: %s", exc)
    return False

def normalize_guide_name(text: str) -> tuple[str | None, str | None]:
    """Return (guide_name, source) for Ember/Mira/custom onboarding choices."""
    raw = (text or "").strip()
    if not raw:
        return None, None
    key = raw.lower().strip("./! ")
    if key in GUIDE_PRESETS:
        return GUIDE_PRESETS[key], "preset"
    for preset_key, preset_name in GUIDE_PRESETS.items():
        if re.fullmatch(rf"(?:let'?s\s+)?(?:do|use|pick|choose|go\s+with)\s+{re.escape(preset_key)}", key):
            return preset_name, "preset"
    if key in {"3", "custom", "choose", "choose my own", "fill in the blank"}:
        return None, "custom_prompt"
    clean = " ".join(raw.replace("\n", " ").split())[:GUIDE_NAME_MAX_CHARS].strip(" .,;:!?@#")
    # Avoid turning normal chat/questions into a guide name when the user has
    # not explicitly chosen custom naming.  Names should be short labels, not
    # full sentences like "what can you do?".
    if "?" in raw or len(clean.split()) > 3:
        return None, None
    if len(clean) < 2:
        return None, None
    return clean, "custom"

def guide_choice_prompt() -> str:
    return (
        "✨ *Welcome in.*\n\n"
        "This is a quiet room for honest work — no performance required.\n\n"
        "What simple name should this space answer to? `George` is perfectly fine."
    )

def guide_ready_message(name: str) -> str:
    label = name or "the Sanctuary"
    return (
        f"✨ *{label} is open.*\n\n"
        "Bring me one honest sentence, and we’ll start there."
    )

async def provision_bot_instance(client: httpx.AsyncClient, chat_id: int, user: User, bot_instance: BotInstance) -> None:
    guide_name = user.guide_name or "the Sanctuary"
    await send_telegram_message(client, chat_id, f"🔑 *Auth successful.* Opening {guide_name}. This takes about 10 seconds...")

    api_success = False
    trial_expires_at = getattr(user, "trial_expires_at", None)
    payload_dict = {
        "user_id": user.id,
        "telegram_user_id": str(chat_id),
        "guide_name": user.guide_name or "Ember",
        "guide_name_source": user.guide_name_source or "default",
        "access_status": getattr(user, "access_status", None) or "paid",
        "trial_expires_at": trial_expires_at.isoformat() if trial_expires_at else None,
        "action": "provision"
    }
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    signature = generate_hmac_signature(payload_bytes, ORCHESTRATOR_SHARED_SECRET)
    headers = {"Content-Type": "application/json", "X-Signature": signature}

    try:
        target_url = f"{ORCHESTRATOR_URL}/api/orchestrate/provision"
        logger.info("Triggering VM container provisioning on %s...", target_url)
        resp = await client.post(target_url, content=payload_bytes, headers=headers, timeout=float(os.getenv("HDE_ORCHESTRATOR_PROVISION_TIMEOUT_SECONDS", "180")))
        if resp.status_code == 200:
            api_success = True
            logger.info("VM container provisioned successfully for user %d.", user.id)
        else:
            logger.error("VM Orchestrator responded with error %d: %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.exception("VM Orchestrator connection failed: %s", exc)

    async with async_session_factory() as rollback_session:
        rollback_session: AsyncSession
        try:
            db_bot_res = await rollback_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
            db_bot = db_bot_res.scalar_one()
            if api_success:
                db_bot.status = "active"
                await rollback_session.commit()
                await send_telegram_message(client, chat_id, guide_ready_message(guide_name))
            else:
                db_bot.status = "error"
                await rollback_session.commit()
                await send_telegram_message(client, chat_id, "⚠️ *Setup Failed:* We could not open your sanctuary space. Please contact support.")
        except Exception as roll_exc:
            logger.exception("Failed to update provisioning status: %s", roll_exc)
            await rollback_session.rollback()

# ── Onboarding Command Processor ───────────────────────────────────────
async def process_start_token(client: httpx.AsyncClient, chat_id: int, token: str) -> None:
    """Validate invite token, update user DB profile, trigger orchestration."""
    async with async_session_factory() as db_session:
        db_session: AsyncSession
        try:
            logger.info("Validating invitation token '%s' for chat_id %d...", token, chat_id)
            result = await db_session.execute(
                select(Invitation)
                .where(Invitation.token == token)
                .options(selectinload(Invitation.user))
            )
            invitation: Optional[Invitation] = result.scalar_one_or_none()

            if not invitation:
                await send_telegram_message(client, chat_id, "❌ *Error:* Invalid onboarding link.")
                return
            if invitation.is_used:
                await send_telegram_message(client, chat_id, "❌ *Error:* This invitation has already been used.")
                return
            # Do not time out paid onboarding links. The active subscription check is
            # the gate; overwhelmed users should be able to return whenever they can.

            user = invitation.user
            access = user_access_state(user)
            if not access["allowed"]:
                await send_telegram_message(client, chat_id, access["message"])
                return

            chat_id_str = str(chat_id)
            result_existing_chat = await db_session.execute(
                select(BotInstance).where(BotInstance.telegram_user_id == chat_id_str)
            )
            existing_chat_bot: Optional[BotInstance] = result_existing_chat.scalar_one_or_none()

            result_bot = await db_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
            bot_instance: Optional[BotInstance] = result_bot.scalar_one_or_none()

            if existing_chat_bot and existing_chat_bot.user_id != user.id:
                logger.info(
                    "Reassigning Telegram chat_id %d from User ID %d to User ID %d.",
                    chat_id,
                    existing_chat_bot.user_id,
                    user.id,
                )
                existing_chat_bot.telegram_user_id = None

            if not bot_instance:
                container_name = f"guest-hermes-{user.id}"
                workspace_path = f"/home/ubuntu/users/guest_{user.id}"
                bot_instance = BotInstance(
                    user_id=user.id,
                    telegram_user_id=chat_id_str,
                    container_name=container_name,
                    workspace_path=workspace_path,
                    status="provisioning",
                    host_node_ip=DEFAULT_HOST_NODE_IP,
                    api_key_limits={"openrouter_monthly_cap": 10.0}
                )
                db_session.add(bot_instance)
            else:
                bot_instance.telegram_user_id = chat_id_str
                bot_instance.status = "awaiting_guide_choice"

            bot_instance.status = "awaiting_guide_choice"
            invitation.is_used = True
            await db_session.commit()
            await db_session.refresh(bot_instance)
            logger.info("Associated Telegram ID %d with User ID %d.", chat_id, user.id)

        except Exception as exc:
            logger.exception("Database transaction failed during initialization: %s", exc)
            await db_session.rollback()
            await send_telegram_message(client, chat_id, "❌ *Error:* Database connection issue. Please try again.")
            return

        if access.get("kind") == "demo":
            days_left = access.get("days_left")
            countdown = f" You have {days_left} day{'s' if days_left != 1 else ''} left in the demo." if days_left is not None else ""
            await send_telegram_message(
                client,
                chat_id,
                "🌿 *Demo access active.* This is your 14-day Sanctuary test space." + countdown + " If you upgrade before it ends, this same container continues."
            )

        await send_telegram_message(
            client,
            chat_id,
            "🧪 *Family/staging test note:* Michael and Ned may review this test conversation, generated chart artifacts, stuck states, and feedback to improve the Sanctuary bot experience. This applies to this staging test round and is separate from production customer privacy."
        )
        await send_telegram_message(client, chat_id, guide_choice_prompt())

# ── Message Proxy Router Loop ────────────────────────────────────────
def extract_usage_tokens(data: dict) -> int | None:
    """Extract provider token usage from common guest response shapes."""
    usage = data.get("usage") or data.get("token_usage") or data.get("model_usage")
    if not isinstance(usage, dict):
        return None
    for key in ("total_tokens", "total", "tokens"):
        value = usage.get(key)
        if isinstance(value, int) and value >= 0:
            return value
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    if isinstance(input_tokens, int) or isinstance(output_tokens, int):
        return max(0, int(input_tokens or 0)) + max(0, int(output_tokens or 0))
    return None


def resolve_guest_file(workspace_path: str, guest_path: str | None) -> str | None:
    """Resolve a guest /workspace path to a host path under that user's workspace."""
    if not guest_path:
        return None
    rel_path = str(guest_path).replace("/workspace/", "", 1).lstrip("/")
    parts = [p for p in rel_path.split("/") if p and p not in {".", ".."}]
    if not parts:
        return None
    host_path = os.path.abspath(os.path.join(workspace_path, *parts))
    workspace_root = os.path.abspath(workspace_path)
    if not host_path.startswith(workspace_root + os.sep):
        logger.warning("Rejected media path outside workspace: %s", guest_path)
        return None
    return host_path


async def enqueue_media_upload(client: httpx.AsyncClient, chat_id: int, workspace_path: str, data: dict) -> None:
    """Queue chart image/PDF uploads so chat workers are not blocked by Telegram file IO."""
    media_items: list[tuple[str, str | None]] = []
    for image_path in data.get("image_paths") or []:
        media_items.append(("photo", image_path))
    if data.get("image_path"):
        media_items.append(("photo", data.get("image_path")))
    for pdf_path in data.get("pdf_paths") or []:
        media_items.append(("document", pdf_path))
    if data.get("pdf_path"):
        media_items.append(("document", data.get("pdf_path")))

    seen: set[tuple[str, str]] = set()
    for kind, guest_path in media_items:
        host_path = resolve_guest_file(workspace_path, guest_path)
        if not host_path or not os.path.exists(host_path):
            continue
        key = (kind, host_path)
        if key in seen:
            continue
        seen.add(key)
        payload = json.dumps({"kind": kind, "path": host_path})
        await enqueue_or_run(client, "media", chat_id, payload)


async def process_media_upload(client: httpx.AsyncClient, chat_id: int, payload_text: str) -> None:
    """Send a queued media artifact to Telegram."""
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        logger.error("Invalid media queue payload for chat %d", chat_id)
        return
    kind = payload.get("kind")
    file_path = payload.get("path")
    if kind not in {"photo", "document"} or not isinstance(file_path, str):
        logger.error("Invalid media upload payload: %r", payload)
        return
    if not os.path.exists(file_path):
        logger.warning("Queued media file missing before upload: %s", file_path)
        return
    if kind == "photo":
        await send_telegram_photo(client, chat_id, file_path)
    else:
        await send_telegram_document(client, chat_id, file_path)


async def handle_user_chat(client: httpx.AsyncClient, chat_id: int, text: str) -> None:
    """Lookup user container, handle wakeup transitions, and forward chat message."""
    async with async_session_factory() as db_session:
        db_session: AsyncSession
        result = await db_session.execute(
            select(BotInstance)
            .where(BotInstance.telegram_user_id == str(chat_id))
            .options(selectinload(BotInstance.user))
        )
        bot_instance: Optional[BotInstance] = result.scalar_one_or_none()

    if not bot_instance:
        await send_telegram_message(client, chat_id, "Welcome! Please onboard using the link provided after your humandesignengine.com checkout.")
        return

    access = user_access_state(bot_instance.user)
    if not access["allowed"]:
        await mark_access_paused(bot_instance, access.get("kind", "inactive"))
        await send_telegram_message(client, chat_id, access["message"])
        return

    if bot_instance.status == "awaiting_guide_choice":
        guide_name, source = normalize_guide_name(text)
        if source == "custom_prompt":
            await send_telegram_message(client, chat_id, "Beautiful. What name would feel comfortable for your guide?")
            return
        if not guide_name:
            await send_telegram_message(client, chat_id, guide_choice_prompt())
            return
        async with async_session_factory() as guide_session:
            guide_res = await guide_session.execute(
                select(BotInstance).where(BotInstance.id == bot_instance.id).options(selectinload(BotInstance.user))
            )
            db_bot = guide_res.scalar_one()
            db_bot.user.guide_name = guide_name
            db_bot.user.guide_name_source = source or "custom"
            db_bot.status = "provisioning"
            await guide_session.commit()
            await guide_session.refresh(db_bot)
            user = db_bot.user
        await provision_bot_instance(client, chat_id, user, bot_instance)
        return

    # If the container is asleep/provisioning, hand wakeup to the wake queue so
    # normal chat workers do not sit on startup latency.  The wake job will
    # re-enqueue this message after the container is marked active.
    if bot_instance.status in ("stopped", "suspended", "provisioning"):
        async with async_session_factory() as status_session:
            status_session: AsyncSession
            res = await status_session.execute(select(BotInstance).where(BotInstance.id == bot_instance.id))
            db_bot = res.scalar_one()
            db_bot.status = "waking"
            db_bot.updated_at = datetime.now(timezone.utc)
            await status_session.commit()
        await send_telegram_message(client, chat_id, get_polyvagal_cue(text, bot_instance.user.guide_name or "your space"))
        await enqueue_or_run(client, "wake", chat_id, text)
        return

    if bot_instance.status == "waking":
        await send_telegram_message(client, chat_id, "🟡 *Still waking your space.* " + get_polyvagal_cue(text, bot_instance.user.guide_name or "your space"))
        return

    # Update last request activity timestamp (for hibernation scale-to-zero tracker)
    async with async_session_factory() as activity_session:
        activity_session: AsyncSession
        res = await activity_session.execute(select(BotInstance).where(BotInstance.id == bot_instance.id))
        db_bot = res.scalar_one()
        db_bot.updated_at = datetime.now(timezone.utc)
        await activity_session.commit()

    budget_decision = None
    if BUDGET_GUARD is not None:
        budget_decision = await BUDGET_GUARD.reserve_chat_turn(
            bot_instance.user_id,
            text,
            is_premium=bool(bot_instance.user and bot_instance.user.is_premium),
        )
        if not budget_decision.allowed:
            logger.warning(
                "Budget guard blocked user %d reason=%s monthly_used=%d/%d daily_used=%d/%d",
                bot_instance.user_id,
                budget_decision.reason,
                budget_decision.monthly_used,
                budget_decision.monthly_limit,
                budget_decision.daily_used,
                budget_decision.daily_limit,
            )
            await send_telegram_message(client, chat_id, budget_exceeded_message(budget_decision))
            return

    # Forward message to internal container DNS name
    guest_url = f"http://guest-hermes-{bot_instance.user_id}:8000/api/message"
    container_name = f"guest-hermes-{bot_instance.user_id}"
    container_ip = await get_container_ip(container_name)
    if not container_ip:
        logger.error("Could not resolve IP for container: %s", container_name)
        await send_telegram_message(client, chat_id, "⚠️ *Error:* Your reflection space container could not be found. Please try again.")
        return

    resolved_url = guest_url.replace(container_name, container_ip)
    logger.info("Forwarding message for User %d to %s (resolved from %s)...", bot_instance.user_id, resolved_url, guest_url)
    
    try:
        resp = await client.post(resolved_url, json={"text": text}, timeout=35.0)
        if resp.status_code == 200:
            data = resp.json()
            if BUDGET_GUARD is not None and budget_decision is not None:
                await BUDGET_GUARD.reconcile_chat_turn(budget_decision, extract_usage_tokens(data))
            reply_text = data.get("response", "")
            
            # Send text reply
            if reply_text:
                await send_telegram_message(client, chat_id, reply_text)
                
            # Queue host-assisted file uploads (chart images/PDFs) so chat workers stay fast.
            await enqueue_media_upload(client, chat_id, bot_instance.workspace_path, data)
        else:
            logger.error("Guest agent server returned error %d: %s", resp.status_code, resp.text)
            await send_telegram_message(client, chat_id, "⚠️ *Error:* Your coach container returned an execution error. Please try again.")
    except httpx.ConnectError:
        # Invalidate IP Cache on connection failure
        if container_name in IP_CACHE:
            del IP_CACHE[container_name]
            logger.info("Cleared cached IP for container %s due to ConnectError.", container_name)
            
        logger.warning("Connection refused to %s. Container might be booting or restarted. Resolving new IP...", resolved_url)
        await send_telegram_message(client, chat_id, "🧘 *Aligning energy...* Retrying connection to your container...")
        await asyncio.sleep(4.0)
        
        # Resolve new IP dynamically
        new_ip = await get_container_ip(container_name)
        if not new_ip:
            await send_telegram_message(client, chat_id, "❌ *Timeout:* Sanctuary container took too long to activate. Please try again.")
            return
        new_resolved_url = guest_url.replace(container_name, new_ip)
        
        try:
            resp = await client.post(new_resolved_url, json={"text": text}, timeout=35.0)
            if resp.status_code == 200:
                data = resp.json()
                if BUDGET_GUARD is not None and budget_decision is not None:
                    await BUDGET_GUARD.reconcile_chat_turn(budget_decision, extract_usage_tokens(data))
                reply_text = data.get("response", "")
                if reply_text:
                    await send_telegram_message(client, chat_id, reply_text)
                await enqueue_media_upload(client, chat_id, bot_instance.workspace_path, data)
            else:
                await send_telegram_message(client, chat_id, "⚠️ *Connection error:* Sanctuary container did not respond. Please try again.")
        except Exception as e:
            logger.exception("Retry failed: %s", e)
            await send_telegram_message(client, chat_id, "❌ *Timeout:* Sanctuary container took too long to activate. Please try again.")
    except Exception as exc:
        # Invalidate IP Cache on generic exception / timeout
        if container_name in IP_CACHE:
            del IP_CACHE[container_name]
            logger.info("Cleared cached IP for container %s due to timeout/exception.", container_name)
            
        logger.exception("Proxy request failed: %s", exc)
        await send_telegram_message(client, chat_id, "⚠️ *Connection timeout:* Sanctuary container took too long to process. Please try again.")



async def wake_container_for_chat(client: httpx.AsyncClient, chat_id: int, original_text: str) -> None:
    """Wake a sleeping guest container without occupying the normal chat queue."""
    async with async_session_factory() as db_session:
        db_session: AsyncSession
        res = await db_session.execute(
            select(BotInstance).where(BotInstance.telegram_user_id == str(chat_id))
        )
        bot_instance: Optional[BotInstance] = res.scalar_one_or_none()

    if not bot_instance:
        return

    woken = await start_stopped_container(client, bot_instance)
    if not woken:
        async with async_session_factory() as status_session:
            res = await status_session.execute(select(BotInstance).where(BotInstance.id == bot_instance.id))
            db_bot = res.scalar_one()
            db_bot.status = "error"
            db_bot.updated_at = datetime.now(timezone.utc)
            await status_session.commit()
        await send_telegram_message(client, chat_id, "❌ *Error:* Sanctuary container failed to activate. Please try again.")
        return

    async with async_session_factory() as status_session:
        status_session: AsyncSession
        res = await status_session.execute(select(BotInstance).where(BotInstance.id == bot_instance.id))
        db_bot = res.scalar_one()
        db_bot.status = "active"
        db_bot.updated_at = datetime.now(timezone.utc)
        await status_session.commit()

    await asyncio.sleep(5.0)  # wait for uvicorn to boot after orchestrator start
    await enqueue_or_run(client, "chat", chat_id, original_text)

# ── Main Telegram Polling Daemon ──────────────────────────────────────
async def handle_update(client: httpx.AsyncClient, update: dict) -> None:
    """Parse incoming update messages."""
    if "message" not in update:
        return
    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        return

    if RATE_LIMITER is not None:
        decision = await RATE_LIMITER.check_chat(chat_id)
        if not decision.allowed:
            await send_telegram_message(
                client,
                chat_id,
                f"🟡 *One breath.* You are sending messages faster than this space can integrate. Try again in about {decision.retry_after_seconds}s."
            )
            return

    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            token = parts[1].strip()
            await enqueue_or_run(client, "start", chat_id, token)
        else:
            await send_telegram_message(client, chat_id, "✨ *Welcome!* Please purchase a subscription at humandesignengine.com to enter your coaching sanctuary.")
    else:
        await enqueue_or_run(client, "chat", chat_id, text)


async def process_queued_job(client: httpx.AsyncClient, kind: JobKind, chat_id: int, text: str) -> None:
    if kind == "start":
        await process_start_token(client, chat_id, text)
    elif kind == "wake":
        await wake_container_for_chat(client, chat_id, text)
    elif kind == "media":
        await process_media_upload(client, chat_id, text)
    else:
        await handle_user_chat(client, chat_id, text)


async def enqueue_or_run(client: httpx.AsyncClient, kind: JobKind, chat_id: int, text: str) -> None:
    if JOB_QUEUE is not None:
        await JOB_QUEUE.enqueue(kind, chat_id, text)
        return
    if kind == "start":
        create_limited_task(process_start_token(client, chat_id, text))
    elif kind == "wake":
        create_limited_task(wake_container_for_chat(client, chat_id, text))
    elif kind == "media":
        create_limited_task(process_media_upload(client, chat_id, text))
    else:
        create_limited_task(handle_user_chat(client, chat_id, text))

def create_limited_task(coro) -> None:
    global ROUTER_SEMAPHORE
    if ROUTER_SEMAPHORE is None:
        ROUTER_SEMAPHORE = asyncio.Semaphore(ROUTER_MAX_CONCURRENT_CHATS)
    if len(ACTIVE_TASKS) >= ROUTER_TASK_QUEUE_LIMIT:
        logger.warning("Router task queue full; dropping update to protect service health.")
        coro.close()
        return

    async def runner():
        try:
            async with ROUTER_SEMAPHORE:
                await asyncio.wait_for(coro, timeout=ROUTER_CHAT_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("Router task exceeded %.1fs timeout", ROUTER_CHAT_TIMEOUT_SECONDS)
        except Exception as exc:
            logger.exception("Router background task failed: %s", exc)

    task = asyncio.create_task(runner())
    ACTIVE_TASKS.add(task)
    task.add_done_callback(ACTIVE_TASKS.discard)


async def main() -> None:
    global RATE_LIMITER, JOB_QUEUE, BUDGET_GUARD
    RATE_LIMITER = await create_rate_limiter_from_env()
    BUDGET_GUARD = await UsageBudgetGuard.from_env()
    JOB_QUEUE = await RedisJobQueueSet.from_env()

    if not COACH_BOT_TOKEN or COACH_BOT_TOKEN == "mock_coach_bot_token":
        logger.error("HDE_COACH_BOT_TOKEN is not set. Exiting.")
        sys.exit(1)

    logger.info("Starting HDE Multi-Tenant Single Bot Proxy Router Daemon for @%s...", ONBOARDING_BOT_USERNAME)
    offset = 0
    
    # Establish persistent async client connection pool sized for bursty Telegram fan-in.
    async with httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=200, max_connections=1200)) as client:
        if JOB_QUEUE is not None:
            JOB_QUEUE.start_workers(lambda kind, chat_id, text: process_queued_job(client, kind, chat_id, text))
        while True:
            url = f"https://api.telegram.org/bot{COACH_BOT_TOKEN}/getUpdates"
            try:
                resp = await client.get(url, params={"offset": offset, "timeout": 20}, timeout=25.0)
                if resp.status_code == 200:
                    updates = resp.json().get("result", [])
                    for update in updates:
                        offset = update["update_id"] + 1
                        await handle_update(client, update)
                else:
                    logger.error("Telegram getUpdates returned status %d: %s", resp.status_code, resp.text)
                    await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("Poller task cancelled. Exiting.")
                if JOB_QUEUE is not None:
                    await JOB_QUEUE.stop_workers()
                break
            except Exception as exc:
                logger.error("Polling error encountered: %s", exc)
                await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon interrupted manually. Exiting.")
