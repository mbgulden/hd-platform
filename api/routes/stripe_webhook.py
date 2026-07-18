import asyncio
import hashlib
import hmac
import json
import logging
import os
import secrets
import smtplib
import stripe
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from pydantic import BaseModel
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import User, Invitation, BotInstance, async_session_factory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["stripe-webhooks"])

# ── Environment Configurations ─────────────────────────────────────────
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8001")
ORCHESTRATOR_SHARED_SECRET = os.environ.get("ORCHESTRATOR_SHARED_SECRET", "default_shared_secret")
ONBOARDING_BOT_USERNAME = os.environ.get("HDE_ONBOARDING_BOT_USERNAME", "HDE_CoachBot").lstrip("@")
DEMO_TRIAL_DAYS = int(os.environ.get("HDE_DEMO_TRIAL_DAYS", "14"))
DEMO_RETENTION_DAYS = int(os.environ.get("HDE_DEMO_RETENTION_DAYS", "30"))
DEMO_RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("HDE_DEMO_RATE_LIMIT_WINDOW_SECONDS", "3600"))
DEMO_RATE_LIMIT_MAX_ATTEMPTS = int(os.environ.get("HDE_DEMO_RATE_LIMIT_MAX_ATTEMPTS", "5"))
DEMO_SIGNUP_ATTEMPTS: Dict[str, list[float]] = {}


def truthy(value: Any) -> bool:
    return str(value or "").lower() in ("1", "true", "yes", "on")


def is_demo_checkout(metadata: Dict[str, str]) -> bool:
    return (
        metadata.get("access_status") == "demo"
        or metadata.get("product") in {"sanctuary-demo", "demo", "hde-sanctuary-demo"}
        or truthy(metadata.get("demo_trial"))
    )


def check_demo_rate_limit(email: str, client_ip: str) -> None:
    """Tiny in-process abuse guard for the semi-public demo endpoint."""
    now = time.time()
    keys = {f"email:{email}", f"ip:{client_ip}" if client_ip else "ip:unknown"}
    cutoff = now - DEMO_RATE_LIMIT_WINDOW_SECONDS
    for key in keys:
        attempts = [ts for ts in DEMO_SIGNUP_ATTEMPTS.get(key, []) if ts >= cutoff]
        if len(attempts) >= DEMO_RATE_LIMIT_MAX_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Too many demo signup attempts. Try again later.")
        attempts.append(now)
        DEMO_SIGNUP_ATTEMPTS[key] = attempts


# In-memory session store for mock checkouts
# session_id -> { "email": email, "name": name, "is_premium": is_premium }
MOCK_SESSIONS: Dict[str, Dict[str, Any]] = {}

# ── Stripe Manual Verification Helper ──────────────────────────────────
def verify_stripe_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> bool:
    """
    Verify Stripe webhook signature manually without the stripe package.
    """
    if not secret or secret.startswith("__SET_IN_"):
        if os.environ.get("ENVIRONMENT") == "production":
            logger.error("STRIPE_WEBHOOK_SECRET is missing or placeholder in production!")
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

    bot_token = os.environ.get("HDE_COACH_BOT_TOKEN")
    alert_ids_str = os.environ.get("ALERT_CHAT_IDS", "")
    alert_ids = [int(cid.strip()) for cid in alert_ids_str.split(",") if cid.strip().isdigit()]

    if bot_token and alert_ids:
        text = f"🔔 *New Premium Client!*\n\n{email} has joined the 6-Week Sovereign Container.\n\nOnboarding token: `{token}`"
        for chat_id in alert_ids:
            try:
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

def send_customer_onboarding_email(email: str, deep_link: str, is_premium: bool) -> bool:
    """Email the customer their one-step onboarding link so they can resume later."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_email = os.environ.get("FROM_EMAIL", "support@humandesignengine.com")

    if not smtp_user or not smtp_pass:
        logger.warning("Customer onboarding email skipped for %s: SMTP credentials incomplete.", email)
        return False

    subject = "Your next step: open your Human Design sanctuary"
    body = f"""SOMATIC EXPERIMENT STATION

You’re in.
Nothing else to figure out right now. Your next step is simple.

Open your private Telegram sanctuary
{deep_link}

This link does not expire. If you get interrupted, overwhelmed, distracted, or need to
come back later, use this email and pick up right here.

If anything feels confusing, reply to this email and we’ll help.

Human Design Engine
Your private Human Design sanctuary
staging.humandesignengine.com/deconditioning
"""
    safe_deep_link = escape(deep_link, quote=True)
    html = f"""<!doctype html>
<html lang=\"en\">
  <body style=\"margin:0;padding:0;background:#fbf7ed;color:#14213d;font-family:Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\">
    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:linear-gradient(135deg,#fffdf8,#f5ead5);padding:32px 16px;\">
      <tr>
        <td align=\"center\">
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:640px;background:#fffdf8;border:1px solid #eadfca;border-radius:28px;overflow:hidden;box-shadow:0 24px 70px rgba(20,33,61,.10);\">
            <tr>
              <td style=\"padding:28px 32px 12px;\">
                <div style=\"font-weight:800;letter-spacing:.02em;font-size:18px;color:#14213d;\">Human Design<span style=\"color:#c9a84c;\">Engine</span></div>
                <div style=\"margin-top:24px;color:#557c55;font-weight:800;text-transform:uppercase;letter-spacing:.12em;font-size:12px;\">Somatic Experiment Station</div>
                <h1 style=\"margin:14px 0 12px;font-family:Georgia, 'Times New Roman', serif;font-size:42px;line-height:.98;color:#14213d;font-weight:500;\">You’re in.</h1>
                <p style=\"margin:0;color:#5f6b7a;font-size:18px;line-height:1.6;\">Nothing else to figure out right now. Your next step is simple.</p>
              </td>
            </tr>
            <tr>
              <td style=\"padding:16px 32px 8px;\">
                <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#ffffff;border:1px solid #eadfca;border-radius:22px;\">
                  <tr>
                    <td style=\"padding:24px;\">
                      <p style=\"margin:0 0 16px;color:#14213d;font-size:17px;line-height:1.55;font-weight:700;\">Open your private Telegram sanctuary</p>
                      <a href=\"{safe_deep_link}\" style=\"display:inline-block;background:#14213d;color:#ffffff;text-decoration:none;border-radius:999px;padding:15px 24px;font-weight:800;font-size:16px;\">Continue in Telegram</a>
                      <p style=\"margin:18px 0 0;color:#5f6b7a;font-size:14px;line-height:1.55;word-break:break-word;\">If the button does not open, copy this link:<br><a href=\"{safe_deep_link}\" style=\"color:#557c55;\">{safe_deep_link}</a></p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style=\"padding:20px 32px 30px;\">
                <p style=\"margin:0 0 16px;color:#5f6b7a;font-size:16px;line-height:1.65;\">This link does not expire. If you get interrupted, overwhelmed, distracted, or need to come back later, use this email and pick up right here.</p>
                <p style=\"margin:0;color:#5f6b7a;font-size:16px;line-height:1.65;\">If anything feels confusing, reply to this email and we’ll help.</p>
                <div style=\"height:1px;background:#eadfca;margin:26px 0 18px;\"></div>
                <p style=\"margin:0;color:#14213d;font-weight:800;font-size:15px;\">Human Design Engine</p>
                <p style=\"margin:5px 0 0;color:#5f6b7a;font-size:14px;\">Your private Human Design sanctuary</p>
                <p style=\"margin:5px 0 0;color:#8f4f4f;font-size:13px;\">staging.humandesignengine.com/deconditioning</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    msg["From"] = from_email
    msg["To"] = email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("Customer onboarding email sent to %s", email)
        return True
    except Exception as exc:
        logger.exception("Customer onboarding email failed for %s: %s", email, exc)
        return False


# ── Shared Onboarding Processor ────────────────--------------------------
async def process_successful_checkout(
    email: str,
    stripe_customer_id: Optional[str],
    metadata: dict,
    background_tasks: BackgroundTasks
):
    """
    Creates user, sets premium status if applicable, generates onboarding token,
    and handles notification dispatch.
    """
    is_premium_tier = (metadata.get("tier") == "premium" or metadata.get("tier") == "sovereign" or metadata.get("product") == "sovereign")
    is_demo_tier = is_demo_checkout(metadata)
    now = datetime.now(timezone.utc)
    demo_trial_expires_at = now + timedelta(days=DEMO_TRIAL_DAYS) if is_demo_tier else None
    family_test_consent = truthy(metadata.get("family_test_review_consent"))
    consent_value = truthy(metadata.get("coach_review_consent"))
    # Sovereign/premium uses consent for coach access. Staging family tests also
    # capture explicit improvement-review consent even when the tester chose the
    # Solo package, so the monitor can distinguish consented test rows from
    # ordinary private bot-only customers.
    consent_granted = bool(consent_value and (is_premium_tier or family_test_consent))
    consent_source = metadata.get("coach_review_consent_source") or ("staging_family_test_checkout" if family_test_consent else "checkout")

    async with async_session_factory() as db_session:
        db_session: AsyncSession
        result = await db_session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email=email,
                stripe_customer_id=stripe_customer_id,
                subscription_status="active",
                access_status="demo" if is_demo_tier else "paid",
                trial_expires_at=demo_trial_expires_at,
                deactivated_at=None,
                deletion_scheduled_at=None,
                is_premium=is_premium_tier,
                coach_review_consent=consent_granted,
                coach_review_consent_at=now if consent_granted else None,
                coach_review_consent_source=consent_source if consent_granted else None,
                coach_review_consent_revoked_at=None,
                coaching_container_end=now + timedelta(weeks=6) if is_premium_tier else None
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            logger.info("Registered active user profile for: %s (Premium: %s)", email, is_premium_tier)
        else:
            user.subscription_status = "active"
            user.access_status = "demo" if is_demo_tier else "paid"
            user.trial_expires_at = demo_trial_expires_at if is_demo_tier else None
            user.deactivated_at = None
            user.deletion_scheduled_at = None
            if stripe_customer_id:
                user.stripe_customer_id = stripe_customer_id
            if is_premium_tier:
                user.is_premium = True
                user.coaching_container_end = now + timedelta(weeks=6)
                if consent_granted:
                    user.coach_review_consent = True
                    user.coach_review_consent_at = now
                    user.coach_review_consent_source = consent_source
                    user.coach_review_consent_revoked_at = None

            bot_instance_res = await db_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
            bot_instance = bot_instance_res.scalar_one_or_none()
            if bot_instance:
                if is_demo_tier:
                    bot_instance.status = "active"
                else:
                    # Paid upgrade should preserve the existing space. If the
                    # demo/inactive container was paused, leave it in a wakeable
                    # stopped state instead of pretending the Docker container is
                    # already active; the router will start it on the next chat.
                    bot_instance.status = "stopped" if bot_instance.status in {"suspended", "stopped", "deprovisioning", "error"} else "active"

            await db_session.commit()
            logger.info("Activated existing user profile for: %s (Premium: %s)", email, is_premium_tier)

        token = "hde_" + secrets.token_urlsafe(16)
        # Paid onboarding links should not punish slow, overwhelmed, or neurodivergent users.
        # Keep a far-future timestamp only because the DB column is non-null.
        expires_at = datetime.now(timezone.utc) + timedelta(days=3650)
        invitation = Invitation(user_id=user.id, token=token, expires_at=expires_at)
        db_session.add(invitation)
        await db_session.commit()

        deep_link = f"https://t.me/{ONBOARDING_BOT_USERNAME}?start={token}"
        logger.info("Generated durable onboarding token: %s", token)
        print(f"[ONBOARDING DEEP LINK]: {deep_link}")
        background_tasks.add_task(send_customer_onboarding_email, email, deep_link, is_premium_tier)

        if is_premium_tier:
            send_premium_signup_notification(email, user.id, token)


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
        metadata = session.get("metadata") or {}

        # Route dynamically to PDF Report Generation if metadata indicates a report
        report_type = metadata.get("report")
        if report_type in ("natal", "synastry", "transit", "bundle", "belief-standard", "belief-comprehensive", "poster"):
            from .payment import process_checkout_session
            background_tasks.add_task(process_checkout_session, session)
            logger.info("Report checkout detected. Dispatched process_checkout_session for report: %s", report_type)
        else:
            if not email:
                logger.error("Checkout completed without customer email. Aborting user setup.")
                return {"success": False, "error": "No email found in checkout session."}
            await process_successful_checkout(email, stripe_customer_id, metadata, background_tasks)

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
                now = datetime.now(timezone.utc)
                user.subscription_status = "inactive"
                user.deactivated_at = now
                user.deletion_scheduled_at = now + timedelta(days=DEMO_RETENTION_DAYS)
                await db_session.commit()
                logger.info("Deactivated user subscription for stripe customer: %s; deletion scheduled after retention window", stripe_customer_id)

                bot_instance_res = await db_session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
                bot_instance = bot_instance_res.scalar_one_or_none()
                tg_id = bot_instance.telegram_user_id if bot_instance else None

                if bot_instance:
                    bot_instance.status = "suspended"
                    await db_session.commit()
                    logger.info("Suspended bot instance status in DB for user %d.", user.id)

                background_tasks.add_task(dispatch_vm_orchestration, user.id, "stop", tg_id)
            else:
                logger.warning("No user found with customer ID: %s", stripe_customer_id)

    return {"success": True, "event_received": event_type}


# ── Create Stripe Checkout Session ─────────────────────────────────────
class CreateSessionRequest(BaseModel):
    email: str
    product_name: str
    product_description: Optional[str] = None
    price_cents: int
    price_id: Optional[str] = None
    recurring_price_id: Optional[str] = None
    subscription_trial_days: Optional[int] = None
    is_subscription: bool = False
    metadata: Optional[Dict[str, str]] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

@router.post("/checkout/create-session")
async def create_stripe_session(
    body: CreateSessionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")

    # Intercept placeholder credentials for development/testing
    if not stripe_key or stripe_key.startswith("__SET_IN_") or stripe_key.startswith("sk_live_REPLACE"):
        logger.warning("Stripe key is placeholder. Running in Mock Checkout Mode.")
        session_id = "cs_test_mock_" + secrets.token_urlsafe(16)

        is_premium_tier = (body.metadata or {}).get("tier") == "premium" or (body.metadata or {}).get("tier") == "sovereign" or (body.metadata or {}).get("product") == "sovereign"
        is_demo_tier = is_demo_checkout(body.metadata or {})

        MOCK_SESSIONS[session_id] = {
            "email": body.email,
            "name": (body.metadata or {}).get("name") or "Friend",
            "is_premium": is_premium_tier,
            "is_demo": is_demo_tier,
        }

        # Check if this is a report purchase
        report_type = (body.metadata or {}).get("report")
        if report_type in ("natal", "synastry", "transit", "bundle", "belief-standard", "belief-comprehensive", "poster"):
            mock_session = {
                "id": session_id,
                "customer": "cus_mock_" + secrets.token_urlsafe(8),
                "customer_email": body.email,
                "metadata": body.metadata or {}
            }
            from .payment import process_checkout_session
            background_tasks.add_task(process_checkout_session, mock_session)
            logger.info("Mock report checkout simulated for: %s", report_type)
        else:
            background_tasks.add_task(
                process_successful_checkout,
                body.email,
                "cus_mock_" + secrets.token_urlsafe(8),
                body.metadata or {},
                background_tasks
            )

        import urllib.parse
        success_target = body.success_url or "/success?session_id={CHECKOUT_SESSION_ID}"
        checkout_pay_url = (
            f"/checkout/pay"
            f"?session_id={session_id}"
            f"&product={urllib.parse.quote(body.product_name)}"
            f"&desc={urllib.parse.quote(body.product_description or '')}"
            f"&price={body.price_cents}"
            f"&success_url={urllib.parse.quote(success_target)}"
        )
        return {"url": checkout_pay_url}

    stripe.api_key = stripe_key

    # Use configured Stripe Price IDs only with live-mode keys. Staging runs
    # against Stripe test keys, so live Price IDs would produce a 400 and break
    # the deconditioning checkout smoke. In test mode, build price_data instead.
    use_configured_price_ids = not stripe_key.startswith("sk_test_")
    line_items = []
    if use_configured_price_ids and body.price_id:
        line_items.append({"price": body.price_id, "quantity": 1})
    if use_configured_price_ids and body.recurring_price_id:
        line_items.append({"price": body.recurring_price_id, "quantity": 1})
    if not line_items:
        price_data = {
            "currency": "usd",
            "product_data": {
                "name": body.product_name,
                "description": body.product_description or "",
            },
            "unit_amount": body.price_cents,
        }
        if body.is_subscription:
            price_data["recurring"] = {"interval": "month"}
        line_items = [{"price_data": price_data, "quantity": 1}]
    try:
        session_kwargs = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "subscription" if body.is_subscription else "payment",
            "success_url": body.success_url or "https://humandesignengine.com/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": body.cancel_url or "https://humandesignengine.com/",
            "customer_email": body.email,
            "metadata": body.metadata or {},
        }
        if body.is_subscription and (body.subscription_trial_days or is_demo_checkout(body.metadata or {})):
            session_kwargs["subscription_data"] = {
                "trial_period_days": body.subscription_trial_days or DEMO_TRIAL_DAYS,
                "metadata": body.metadata or {},
            }
        session = stripe.checkout.Session.create(**session_kwargs)
        return {"url": session.url}
    except Exception as e:
        logger.exception("Failed to create Stripe session")
        raise HTTPException(status_code=502, detail=str(e))


# ── Semi-public Sanctuary Demo Signup ─────────────────────────────────
class CreateDemoRequest(BaseModel):
    email: str
    name: Optional[str] = None
    invite_code: Optional[str] = None
    source: Optional[str] = None


@router.post("/demo/start")
async def create_demo_access(
    body: CreateDemoRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Create or refresh a 14-day semi-public Sanctuary demo account."""
    required_code = os.environ.get("HDE_DEMO_INVITE_CODE", "").strip()
    supplied_code = str(body.invite_code or "")
    invite_code_valid = bool(required_code and hmac.compare_digest(supplied_code, required_code))
    if required_code and not invite_code_valid:
        raise HTTPException(status_code=403, detail="Invalid demo invite code.")

    email = (body.email or "").strip().lower()
    if not email or "@" not in email or len(email) > 255:
        raise HTTPException(status_code=400, detail="Valid email is required.")
    client_ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")).split(",")[0].strip()
    check_demo_rate_limit(email, client_ip)

    now = datetime.now(timezone.utc)
    requested_trial_expires_at = now + timedelta(days=DEMO_TRIAL_DAYS)

    async with async_session_factory() as db_session:
        db_session: AsyncSession
        result = await db_session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and (user.access_status or "paid") == "paid" and user.subscription_status == "active":
            raise HTTPException(status_code=409, detail="This email already has paid Sanctuary access. Use the normal onboarding link or contact support.")
        if user and (user.access_status or "") in {"expired_demo", "deleted_demo"} and not invite_code_valid:
            raise HTTPException(
                status_code=409,
                detail="This email has already used a demo. Ask for a renewal invite code or use the paid Sanctuary path.",
            )
        if user and (user.access_status or "") == "demo" and user.trial_expires_at:
            current_expiry = user.trial_expires_at
            if current_expiry.tzinfo is None:
                current_expiry = current_expiry.replace(tzinfo=timezone.utc)
            if current_expiry > now:
                trial_expires_at = current_expiry
            else:
                trial_expires_at = requested_trial_expires_at
        else:
            trial_expires_at = requested_trial_expires_at
        if not user:
            user = User(
                email=email,
                stripe_customer_id="demo_" + secrets.token_urlsafe(12),
                subscription_status="active",
                access_status="demo",
                trial_expires_at=trial_expires_at,
                deactivated_at=None,
                deletion_scheduled_at=None,
                demo_started_at=now,
                demo_renewal_count=0,
                demo_last_source=(body.source or "sanctuary-demo-page")[:100],
                demo_deleted_at=None,
                is_premium=False,
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
        else:
            was_expired_or_deleted = (user.access_status or "") in {"expired_demo", "deleted_demo"}
            user.subscription_status = "active"
            user.access_status = "demo"
            user.trial_expires_at = trial_expires_at
            user.deactivated_at = None
            user.deletion_scheduled_at = None
            user.demo_started_at = user.demo_started_at or now
            user.demo_last_source = (body.source or "sanctuary-demo-page")[:100]
            user.demo_deleted_at = None
            if was_expired_or_deleted:
                user.demo_renewal_count = int(user.demo_renewal_count or 0) + 1
            await db_session.commit()
            await db_session.refresh(user)

        token = "hde_demo_" + secrets.token_urlsafe(16)
        invitation = Invitation(user_id=user.id, token=token, expires_at=now + timedelta(days=DEMO_TRIAL_DAYS))
        db_session.add(invitation)
        await db_session.commit()

    deep_link = f"https://t.me/{ONBOARDING_BOT_USERNAME}?start={token}"
    background_tasks.add_task(send_customer_onboarding_email, email, deep_link, False)
    return {
        "success": True,
        "access_status": "demo",
        "trial_days": DEMO_TRIAL_DAYS,
        "trial_expires_at": trial_expires_at.isoformat(),
        "deletion_grace_days": DEMO_RETENTION_DAYS,
        "deep_link": deep_link,
    }


# ── Onboarding Deep Link Endpoint ──────────────────────────────────────
@router.get("/checkout/session")
async def get_onboarding_link(
    email: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve the Telegram Master Bot link containing the secure invite token for onboarding.
    Accepts email or session_id. Returns client name and subscription tier status.
    """
    resolved_email = email
    resolved_name = "Friend"
    is_premium = False

    if session_id:
        if session_id.startswith("cs_test_mock_"):
            mock_data = MOCK_SESSIONS.get(session_id) or {}
            resolved_email = mock_data.get("email")
            resolved_name = mock_data.get("name", "Friend")
            is_premium = mock_data.get("is_premium", False)
        else:
            stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
            if not stripe_key or stripe_key.startswith("__SET_IN_") or stripe_key.startswith("sk_live_REPLACE"):
                raise HTTPException(status_code=503, detail="Stripe is not configured.")
            stripe.api_key = stripe_key
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                customer_details = getattr(session, "customer_details", None) or {}
                metadata = getattr(session, "metadata", None) or {}
                resolved_email = (
                    getattr(session, "customer_email", None)
                    or getattr(customer_details, "email", None)
                    or (customer_details.get("email") if isinstance(customer_details, dict) else None)
                )
                resolved_name = (
                    getattr(customer_details, "name", None)
                    or (customer_details.get("name") if isinstance(customer_details, dict) else None)
                    or "Friend"
                )
                metadata_get = metadata.get if hasattr(metadata, "get") else lambda key, default=None: getattr(metadata, key, default)
                is_premium = (metadata_get("tier") == "premium" or metadata_get("tier") == "sovereign" or metadata_get("product") == "sovereign")
            except Exception as e:
                logger.error("Failed to retrieve Stripe session: %s", e)
                raise HTTPException(status_code=400, detail="Invalid checkout session.")

    if not resolved_email:
        raise HTTPException(status_code=400, detail="Missing email or session_id parameter.")

    async with async_session_factory() as db_session:
        db_session: AsyncSession
        result_user = await db_session.execute(select(User).where(User.email == resolved_email))
        user = result_user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found.")

        # Find latest unused invitation. Do not time out paid onboarding links;
        # users may return days/weeks later and still deserve one clear next step.
        result_invite = await db_session.execute(
            select(Invitation)
            .where(Invitation.user_id == user.id)
            .where(Invitation.is_used == False)
            .order_by(Invitation.created_at.desc())
        )
        invitation = result_invite.scalars().first()

        # If user is a standard PDF report purchaser and has no invitation, return success details without bot token
        if not invitation:
            return {
                "email": resolved_email,
                "name": resolved_name,
                "is_premium": is_premium or user.is_premium,
                "token": None,
                "deep_link": None,
                "expires_at": None,
                "coach_review_consent": bool(getattr(user, "coach_review_consent", False))
            }

        deep_link = f"https://t.me/{ONBOARDING_BOT_USERNAME}?start={invitation.token}"
        return {
            "email": resolved_email,
            "name": resolved_name,
            "token": invitation.token,
            "deep_link": deep_link,
            "expires_at": invitation.expires_at,
            "is_premium": is_premium or user.is_premium,
            "coach_review_consent": bool(getattr(user, "coach_review_consent", False))
        }
