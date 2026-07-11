import asyncio
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import User, Invitation, BotInstance, async_session_factory

logger = logging.getLogger(__name__)

# Router prefix is empty since we'll mount it directly on the app router or specify it on mounting.
router = APIRouter(prefix="/api", tags=["stripe-webhooks"])

# ── Environment Configurations ─────────────────────────────────────────
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8001")
ORCHESTRATOR_SHARED_SECRET = os.environ.get("ORCHESTRATOR_SHARED_SECRET", "default_shared_secret")

# ── Stripe Manual Verification Helper ──────────────────────────────────
def verify_stripe_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> bool:
    """
    Verify Stripe webhook signature manually without the stripe package.
    """
    if not secret:
        if os.environ.get("ENVIRONMENT") == "production":
            logger.error("STRIPE_WEBHOOK_SECRET is missing in production environment!")
            return False
        logger.warning("STRIPE_WEBHOOK_SECRET is empty. Signature verification bypassed.")
        return True
    if not sig_header:
        return False
    try:
        pairs = [pair.split('=') for pair in sig_header.split(',')]
        params = {k.strip(): v.strip() for k, v in pairs if len(v) > 0}
        timestamp = params.get('t')
        signature = params.get('v1')
        if not timestamp or not signature:
            return False
        if abs(time.time() - int(timestamp)) > tolerance:
            logger.error("Stripe webhook timestamp older than tolerance threshold.")
            return False
        
        signed_payload = f"{timestamp}.".encode('utf-8') + payload
        mac = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256)
        expected_sig = mac.hexdigest()
        return hmac.compare_digest(signature, expected_sig)
    except Exception as exc:
        logger.exception("Stripe signature validation failed: %s", exc)
        return False

# ── HMAC Shared Secret Signature Generator ─────────────────────────────
def generate_orchestrator_signature(payload: bytes, secret: str) -> str:
    """
    Generate an HMAC SHA-256 signature for internal VM orchestration.
    """
    return hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

# ── Orchestrator Webhook Dispatcher ────────────────────────────────────
async def dispatch_vm_orchestration(user_id: int, action: str, telegram_user_id: Optional[str] = None) -> None:
    """
    HTTP client to securely trigger provisioning/teardown on the VM supervisor.
    """
    payload_dict = {
        "user_id": user_id,
        "telegram_user_id": telegram_user_id,
        "action": action
    }
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    signature = generate_orchestrator_signature(payload_bytes, ORCHESTRATOR_SHARED_SECRET)

    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info("Dispatching orchestration action '%s' to VM supervisor for user %d...", action, user_id)
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/api/orchestrate/provision",
                content=payload_bytes,
                headers=headers
            )
            if resp.status_code == 200:
                logger.info("VM supervisor successfully processed action '%s' for user %d.", action, user_id)
            else:
                logger.error("VM supervisor failed with status %d: %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.exception("Failed to connect to VM supervisor: %s", exc)

def send_premium_signup_notification(email: str, user_id: int, token: str):
    """Log an automated notification to Becca and Michael and dispatch Telegram alerts."""
    logger.info("=== AUTOMATED NOTIFICATION ===")
    logger.info("TO: becca.gulden@gmail.com, mbgulden@gmail.com")
    logger.info("SUBJECT: New Premium Signup: The Sovereign Container")
    logger.info("BODY: A new premium client (%s, User ID: %d) has signed up for the 6-Week Sovereign Container with Becca Gulden. The container has been initialized.", email, user_id)
    logger.info("==============================")
    
    # Send live Telegram message alert to Michael's and Becca's Telegram IDs
    bot_token = os.environ.get("HDE_COACH_BOT_TOKEN")
    alert_ids_str = os.environ.get("ALERT_CHAT_IDS", "")
    alert_ids = [int(cid.strip()) for cid in alert_ids_str.split(",") if cid.strip().isdigit()]
    
    if bot_token and alert_ids:
        text = f"🔔 *New Premium Client!*\n\n{email} has joined the 6-Week Sovereign Container.\n\nOnboarding token: `{token}`"
        for chat_id in alert_ids:
            try:
                import httpx
                # Execute synchronous POST call to dispatch immediately inside webhook handler
                httpx.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "Markdown"
                    },
                    timeout=5.0
                )
            except Exception as e:
                logger.error("Failed to send Telegram signup alert to %d: %s", chat_id, e)


# ── Stripe Webhook Endpoint ────────────────────────────────────────────
@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    PostgreSQL-backed Stripe webhook handler.
    Processes checkout completions and subscription cancellations.
    """
    sig_header = request.headers.get("Stripe-Signature", "")
    body = await request.body()

    if not verify_stripe_signature(body, sig_header, STRIPE_WEBHOOK_SECRET):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature verification failed."
        )

    try:
        event = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload."
        )

    event_type = event.get("type")
    logger.info("Received Stripe webhook: %s", event_type)

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        stripe_customer_id = session.get("customer")
        
        if not email:
            logger.error("Checkout completed without customer email. Aborting user setup.")
            return {"success": False, "error": "No email found in checkout session."}

        # Parse metadata to determine tier
        metadata = session.get("metadata") or {}
        is_premium_tier = (metadata.get("tier") == "premium" or metadata.get("tier") == "sovereign")

        async with async_session_factory() as db_session:
            db_session: AsyncSession
            # 1. Ensure user exists
            result = await db_session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    email=email, 
                    stripe_customer_id=stripe_customer_id, 
                    subscription_status="active",
                    is_premium=is_premium_tier,
                    coaching_container_end=datetime.now(timezone.utc) + timedelta(weeks=6) if is_premium_tier else None
                )
                db_session.add(user)
                await db_session.commit()
                await db_session.refresh(user)
                logger.info("Registered active user profile for: %s (Premium: %s)", email, is_premium_tier)
            else:
                user.subscription_status = "active"
                if stripe_customer_id:
                    user.stripe_customer_id = stripe_customer_id
                if is_premium_tier:
                    user.is_premium = True
                    user.coaching_container_end = datetime.now(timezone.utc) + timedelta(weeks=6)
                
                # If they already have a bot instance, update status to active
                bot_instance_res = await db_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
                bot_instance = bot_instance_res.scalar_one_or_none()
                if bot_instance:
                    bot_instance.status = "active"
                    
                await db_session.commit()
                logger.info("Activated existing user profile for: %s (Premium: %s)", email, is_premium_tier)

            # 2. Generate short-lived Invitation Token
            token = "hde_" + secrets.token_urlsafe(16)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            invitation = Invitation(user_id=user.id, token=token, expires_at=expires_at)
            db_session.add(invitation)
            await db_session.commit()
            
            logger.info("Generated onboarding token: %s (Expires: %s)", token, expires_at)
            print(f"[ONBOARDING DEEP LINK]: https://t.me/HDE_MasterBot?start={token}")

            if is_premium_tier:
                send_premium_signup_notification(email, user.id, token)

    elif event_type == "customer.subscription.deleted":
        subscription = event.get("data", {}).get("object", {})
        stripe_customer_id = subscription.get("customer")

        if not stripe_customer_id:
            logger.error("Subscription deleted event missing customer ID.")
            return {"success": False, "error": "Missing customer ID."}

        async with async_session_factory() as db_session:
            db_session: AsyncSession
            result = await db_session.execute(select(User).where(User.stripe_customer_id == stripe_customer_id))
            user = result.scalar_one_or_none()
            if user:
                user.subscription_status = "inactive"
                await db_session.commit()
                logger.info("Deactivated user subscription for stripe customer: %s", stripe_customer_id)

                # Fetch bot instance if any to suspend
                res_bot = await db_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
                bot_instance = res_bot.scalar_one_or_none()
                tg_id = bot_instance.telegram_user_id if bot_instance else None
                
                if bot_instance:
                    bot_instance.status = "suspended"
                    await db_session.commit()
                    logger.info("Suspended bot instance status in DB for user %d.", user.id)
                
                # Queue container suspension (stop action) instead of deletion
                background_tasks.add_task(dispatch_vm_orchestration, user.id, "stop", tg_id)
            else:
                logger.warning("No user found with customer ID: %s", stripe_customer_id)

    return {"success": True, "event_received": event_type}

# ── Onboarding Deep Link Endpoint ──────────────────────────────────────
@router.get("/checkout/session")
async def get_onboarding_link(email: str) -> Dict[str, Any]:
    """
    Retrieve the Telegram Master Bot link containing the secure invite token for onboarding.
    """
    async with async_session_factory() as db_session:
        db_session: AsyncSession
        result_user = await db_session.execute(select(User).where(User.email == email))
        user = result_user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found.")

        # Find active unused invitation
        result_invite = await db_session.execute(
            select(Invitation)
            .where(Invitation.user_id == user.id)
            .where(Invitation.is_used == False)
            .where(Invitation.expires_at > datetime.now(timezone.utc))
            .order_by(Invitation.created_at.desc())
        )
        invitation = result_invite.scalar_one_or_none()
        if not invitation:
            raise HTTPException(status_code=404, detail="No active invitation found. Please purchase a subscription.")

        deep_link = f"https://t.me/HDE_CoachBot?start={invitation.token}"
        return {
            "email": email,
            "token": invitation.token,
            "deep_link": deep_link,
            "expires_at": invitation.expires_at
        }
