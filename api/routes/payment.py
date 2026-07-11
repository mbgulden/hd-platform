"""
Stripe Webhook route — POST /v1/payment/webhook.

Handles checkout.session.completed events, calls the reports server to generate
HD reports, sends confirmation emails, and records affiliate conversions.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response, status
from sqlalchemy import select

from shared.database import User, async_session_factory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

# ── Environment Configuration ──────────────────────────────────────────
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
REPORTS_SERVER = os.environ.get("REPORTS_SERVER", "http://localhost:8081")
HDE_API_KEY = os.environ.get("HDE_API_KEY", "")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "reports@humandesignengine.com")

AFFILIATES_FILE = "/tmp/hde-reports/affiliates.json"
COMMISSION_RATES = {"natal": 5.70, "synastry": 8.70, "transit": 8.70, "bundle": 17.70}


# ── Webhook Signature Verification ─────────────────────────────────────
def verify_stripe_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> bool:
    """
    Verify Stripe webhook signature manually without requiring the stripe library.
    
    Returns True if valid or if secret is empty (bypassed for development), False otherwise.
    """
    if not secret:
        logger.warning("STRIPE_WEBHOOK_SECRET is not set. Bypassing signature check in dev mode.")
        return True
        
    if not sig_header:
        logger.error("Missing Stripe-Signature header.")
        return False

    try:
        # Parse the Stripe-Signature header
        pairs = [pair.split('=') for pair in sig_header.split(',')]
        params = {k.strip(): v.strip() for k, v in pairs if len(v) > 0}
        
        timestamp = params.get('t')
        signature = params.get('v1')
        
        if not timestamp or not signature:
            logger.error("Invalid Stripe-Signature header format.")
            return False
            
        # Check timestamp tolerance to prevent replay attacks
        try:
            ts_val = int(timestamp)
        except ValueError:
            logger.error("Invalid timestamp in Stripe-Signature header.")
            return False
            
        if abs(time.time() - ts_val) > tolerance:
            logger.error(f"Stripe signature timestamp older than tolerance limit ({tolerance}s).")
            return False
            
        # Compute HMAC-SHA256 signature
        signed_payload = f"{timestamp}.".encode('utf-8') + payload
        mac = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256)
        expected_signature = mac.hexdigest()
        
        if hmac.compare_digest(signature, expected_signature):
            return True
            
        logger.error("Stripe signature mismatch.")
        return False
    except Exception as exc:
        logger.exception("Error verifying Stripe webhook signature: %s", exc)
        return False


# ── Affiliate Conversion Tracking ──────────────────────────────────────
def _load_affiliates() -> Dict[str, Any]:
    try:
        with open(AFFILIATES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_affiliates(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(AFFILIATES_FILE), exist_ok=True)
    tmp = AFFILIATES_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, AFFILIATES_FILE)


def _record_affiliate_conversion(ref: str, report: str) -> None:
    """Increment conversion counter and record earnings for the referred affiliate."""
    affiliates = _load_affiliates()
    for code, data in affiliates.items():
        if code == ref:
            data.setdefault('conversions', 0)
            data.setdefault('earnings', 0.0)
            data['conversions'] += 1
            commission = COMMISSION_RATES.get(report, 5.70)
            data['earnings'] += commission
            _save_affiliates(affiliates)
            logger.info("💰 Affiliate %s earned $%.2f from %s report conversion.", data.get('name', '?'), commission, report)
            return


# ── Email Helper ───────────────────────────────────────────────────────
def send_email_direct(to_email: str, name: str, report_type: str, pdf_path: str) -> None:
    """Send the generated report PDF attachment via SMTP (fallback/local delivery)."""
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP credentials missing on API server, skipping local email sending.")
        return

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = f"Your Human Design {report_type.title()} Report is Ready, {name}!"

    body = f"""Hi {name},

Your Human Design {report_type.title()} Report is attached as a PDF.

This report was computed using verified, open-source calculations — the same engine trusted by developers and practitioners worldwide.

If you have any questions about your chart, we're here to help. Just reply to this email.

With gratitude,
The Human Design Engine Team
humandesignengine.com"""

    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=f'{name}_HD_{report_type}_Report.pdf')
        msg.attach(attachment)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


# ── Background Pipeline Handler ────────────────────────────────────────
async def process_checkout_session(session: Dict[str, Any]) -> None:
    """
    Asynchronously handle report generation, DB user creation, email dispatch,
    and affiliate conversion updates.
    """
    metadata = session.get("metadata", {})
    email = metadata.get("email") or session.get("customer_email") or session.get("customer_details", {}).get("email")
    if not email:
        logger.error("No customer email found in Stripe session. Cannot deliver report.")
        return

    name = metadata.get("name", "Friend")
    report_type = metadata.get("report", "natal")
    birthdate = metadata.get("birthdate", "2000-01-01")
    birthtime = metadata.get("birthtime", "12:00")
    location = metadata.get("location", "Unknown")
    timezone = metadata.get("timezone", "UTC")
    partner = metadata.get("partner", "")
    branding = metadata.get("branding") or metadata.get("brand") or ""

    try:
        lat = float(metadata.get("lat", 0.0))
    except (ValueError, TypeError):
        lat = 0.0

    try:
        lon = float(metadata.get("lon", 0.0))
    except (ValueError, TypeError):
        lon = 0.0

    # 1. Track Affiliate Conversion
    ref = metadata.get("ref", "")
    if ref:
        try:
            _record_affiliate_conversion(ref, report_type)
        except Exception as exc:
            logger.error("Failed to record affiliate conversion: %s", exc)

    # 2. Database User Registration
    stripe_customer_id = session.get("customer")
    if async_session_factory is not None:
        try:
            async with async_session_factory() as db_session:
                result = await db_session.execute(select(User).where(User.email == email))
                user = result.scalar_one_or_none()
                if not user:
                    user = User(email=email, stripe_customer_id=stripe_customer_id)
                    db_session.add(user)
                    await db_session.commit()
                    logger.info("Registered user account for %s.", email)
                elif stripe_customer_id and not user.stripe_customer_id:
                    user.stripe_customer_id = stripe_customer_id
                    await db_session.commit()
                    logger.info("Associated Stripe customer ID with existing user %s.", email)
        except Exception as exc:
            logger.warning("Database user registration skipped/failed: %s", exc)

    # 3. Request PDF Generation from Reports Server (with retries)
    reports_to_generate = []
    if report_type == 'bundle':
        reports_to_generate = ['natal', 'transit']
        if partner:
            reports_to_generate.append('relationship')
    elif report_type == 'synastry':
        reports_to_generate = ['relationship']
    else:
        reports_to_generate = [report_type]

    for current_report_type in reports_to_generate:
        pdf_path = None
        payload = {
            "name": name,
            "report": current_report_type,
            "birthdate": birthdate,
            "birthtime": birthtime,
            "lat": lat,
            "lon": lon,
            "location": location,
            "timezone": timezone,
            "partner": partner,
            "branding": branding,
            "email": email  # Pass email so reports server handles its own email delivery if enabled
        }

        max_retries = 5
        retry_delay = 2.0
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info("Requesting PDF generation on %s/api/compute for %s (attempt %d/%d)", REPORTS_SERVER, current_report_type, attempt, max_retries)
                    response = await client.post(
                        f"{REPORTS_SERVER}/api/compute",
                        json=payload,
                        headers={"X-API-Key": HDE_API_KEY}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            pdf_path = result.get("pdf_path")
                            logger.info("PDF generation succeeded for %s: %s", current_report_type, pdf_path)
                            break
                        else:
                            logger.error("Reports server error: %s", result.get("error"))
                    else:
                        logger.error("Reports server responded with code %d: %s", response.status_code, response.text[:200])
                except Exception as exc:
                    logger.warning("Connection to reports server failed on attempt %d: %s", attempt, exc)
                
                if attempt < max_retries:
                    sleep_time = retry_delay * (2 ** (attempt - 1))
                    logger.info("Retrying in %.1f seconds...", sleep_time)
                    await asyncio.sleep(sleep_time)

        # 4. Fallback Email Delivery
        # If report generation succeeded but SMTP is configured locally on the API,
        # attempt local delivery as a backup to make sure the user receives their report.
        if pdf_path and SMTP_USER and SMTP_PASS:
            if os.path.exists(pdf_path):
                try:
                    send_email_direct(email, name, current_report_type, pdf_path)
                    logger.info("Fallback email delivered successfully for %s to %s", current_report_type, email)
                except Exception as exc:
                    logger.exception("Fallback email delivery failed for %s: %s", current_report_type, exc)
            else:
                logger.warning("PDF path %s does not exist on local filesystem. Email bypass/network storage required.", pdf_path)


# ── Router Webhook Endpoint ─────────────────────────────────────────────
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response
) -> Dict[str, Any]:
    """
    FastAPI webhook endpoint to process Stripe notifications.
    Verifies payload signature, and processes session completion asynchronously.
    """
    sig_header = request.headers.get("Stripe-Signature", "")
    body = await request.body()
    
    # Verify signature
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
    logger.info("Received Stripe webhook event: %s", event_type)

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        background_tasks.add_task(process_checkout_session, session)
        logger.info("Enqueued background processing task for completed checkout session.")

    return {"success": True, "event_received": event_type}


# ── Checkout & Session Endpoints ─────────────────────────────────────────
@router.post("/create-checkout")
async def create_checkout(request: Request) -> Dict[str, Any]:
    """Create a Stripe Checkout Session for a report purchase."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    name = data.get('name')
    email = data.get('email')
    report = data.get('report')
    r_lower = (report or '').lower()
    if r_lower == 'natal':
        price = 1900
    elif r_lower == 'synastry':
        price = 2900
    elif r_lower == 'transit':
        price = 2900
    elif r_lower == 'bundle':
        price = 5900
    else:
        price = data.get('price', 1900)

    birthdate = data.get('birthdate')
    birthtime = data.get('birthtime')
    location = data.get('location')
    partner = data.get('partner')
    lat = data.get('lat', '')
    lon = data.get('lon', '')
    timezone = data.get('timezone', 'UTC')
    ref = data.get('ref', '')

    if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY.startswith('${'):
        raise HTTPException(status_code=503, detail="Stripe is not configured.")

    meta = {
        "name": name, "report": report, "birthdate": birthdate,
        "birthtime": birthtime, "location": location,
        "lat": str(lat), "lon": str(lon), "timezone": timezone,
        "partner": partner or "", "email": email,
        "state": data.get('state', '')
    }
    if ref:
        meta["ref"] = ref

    bundle_price_id = os.environ.get("STRIPE_BUNDLE_PRICE_ID", "price_1Pbundleupsell59")

    # Use Stripe price ID for bundle if custom one is provided, otherwise fall back to price_data
    if report == 'bundle' and bundle_price_id and not bundle_price_id.startswith('price_1Pbundleupsell59') and not bundle_price_id.startswith('${'):
        line_items = [{"price": bundle_price_id, "quantity": 1}]
    else:
        line_items = [{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Human Design {report.title() if report else 'Report'} Report" if report != 'bundle' else "Human Design Complete Bundle",
                    "description": f"Personalized HD report for {name}" if report != 'bundle' else f"Complete Natal, Transit, and Relationship reports for {name}"
                },
                "unit_amount": price
            },
            "quantity": 1
        }]

    # Hawaii GET Tax Logic
    if data.get('state') == 'HI':
        tax_amount = int(round(price * 0.04725))
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "Hawaii GET (4.725%)",
                    "description": "Hawaii General Excise Tax"
                },
                "unit_amount": tax_amount
            },
            "quantity": 1
        })

    import urllib.parse
    if report == 'bundle':
        success_url = "https://humandesignengine.com/success.html?session={CHECKOUT_SESSION_ID}"
    else:
        params = {
            "session": "{CHECKOUT_SESSION_ID}",
            "name": name or "",
            "email": email or "",
            "report": report or "",
            "birthdate": birthdate or "",
            "birthtime": birthtime or "",
            "location": location or "",
            "lat": str(lat),
            "lon": str(lon),
            "timezone": timezone,
            "partner": partner or ""
        }
        if ref:
            params["ref"] = ref
        query_string = urllib.parse.urlencode(params)
        success_url = f"https://humandesignengine.com/upsell.html?{query_string}"

    payload = {
        "payment_method_types": ["card"],
        "line_items": line_items,
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": "https://humandesignengine.com/buy-report.html",
        "customer_email": email,
        "metadata": meta
    }

    # Recursive helper to encode nested dicts/lists for Stripe API urlencoded format
    def _stripe_encode(params, prefix=""):
        flat = {}
        if isinstance(params, dict):
            for k, v in params.items():
                new_prefix = f"{prefix}[{k}]" if prefix else k
                flat.update(_stripe_encode(v, new_prefix))
        elif isinstance(params, list):
            for i, v in enumerate(params):
                new_prefix = f"{prefix}[{i}]"
                flat.update(_stripe_encode(v, new_prefix))
        elif params is not None:
            flat[prefix] = params
        return flat

    flat_payload = _stripe_encode(payload)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.stripe.com/v1/checkout/sessions",
                data=flat_payload,
                headers={
                    "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            if response.status_code >= 400:
                logger.error("Stripe error response: %d - %s", response.status_code, response.text)
                raise HTTPException(status_code=502, detail=f"Stripe API error: {response.text[:200]}")
            
            session_data = response.json()
            return {"url": session_data.get("url", "")}
        except Exception as e:
            logger.exception("Failed to create Stripe checkout session")
            raise HTTPException(status_code=502, detail=str(e))


@router.get("/checkout-session")
async def get_checkout_session(session_id: str) -> Dict[str, Any]:
    """Retrieve a Stripe Checkout Session by ID."""
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id parameter")

    if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY.startswith('${'):
        raise HTTPException(status_code=503, detail="Stripe is not configured.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.stripe.com/v1/checkout/sessions/{session_id}",
                headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"}
            )
            if response.status_code >= 400:
                logger.error("Stripe error response: %d - %s", response.status_code, response.text)
                raise HTTPException(status_code=response.status_code, detail=f"Stripe API error: {response.text[:200]}")
            return response.json()
        except Exception as e:
            logger.exception("Failed to retrieve Stripe checkout session")
            raise HTTPException(status_code=500, detail=str(e))

