"""
Human Design Engine — Payment & Report Server
Handles Stripe Checkout → Webhook → Reports Server → PDF → Email
Affiliate tracking: signup, stats, and commission tracking
Run: STRIPE_SECRET_KEY=sk_... STRIPE_WEBHOOK_SECRET=whsec_... python3 server.py
"""
import os, json, smtplib, hashlib, hmac, time
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.hde_email_theme import attach_themed_alternative, build_report_email

import printful

STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "reports@humandesignengine.com")
REPORTS_SERVER = os.environ.get("REPORTS_SERVER", "http://localhost:8081")
HDE_API_KEY = os.environ.get("HDE_API_KEY", "")
BELIEF_SERVER_SECRET = os.environ.get("BELIEF_SERVER_SECRET", "")
BELIEF_STANDARD_PRICE_ID = os.environ.get("BELIEF_STANDARD_PRICE_ID", "")
BELIEF_COMPREHENSIVE_PRICE_ID = os.environ.get("BELIEF_COMPREHENSIVE_PRICE_ID", "")
UNCHAINED_DIGITAL_PRICE_ID = os.environ.get("UNCHAINED_DIGITAL_PRICE_ID", "")
UNCHAINED_RETREAT_PRICE_ID = os.environ.get("UNCHAINED_RETREAT_PRICE_ID", "")
PORT = int(os.environ.get("PORT", "8000"))
AFFILIATES_FILE = "/tmp/hde-reports/affiliates.json"
USE_CONFIGURED_PRICE_IDS = bool(STRIPE_KEY) and not STRIPE_KEY.startswith("sk_test_") and not STRIPE_KEY.startswith("__SET_IN_") and not STRIPE_KEY.startswith("***")

# Commission rates per report type (30% of report price)
COMMISSION_RATES = {"natal": 2.70, "synastry": 4.20, "transit": 4.20, "bundle": 8.70}

def _load_affiliates():
    try:
        with open(AFFILIATES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_affiliates(data):
    import os as _os
    _os.makedirs(_os.path.dirname(AFFILIATES_FILE), exist_ok=True)
    tmp = AFFILIATES_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=2)
    _os.replace(tmp, AFFILIATES_FILE)

def _generate_ref_code(email):
    """Generate a unique referral code from email + timestamp"""
    raw = f"{email}:{time.time()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def verify_stripe_signature(payload, sig_header, secret, tolerance=300):
    if not secret:
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
        try:
            ts_val = int(timestamp)
        except ValueError:
            return False
        if abs(time.time() - ts_val) > tolerance:
            return False
        signed_payload = f"{timestamp}.".encode('utf-8') + payload
        mac = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256)
        expected_signature = mac.hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''

        if self.path in ('/checkout', '/create-checkout', '/create-checkout-session', '/api/checkout/create-session'):
            self._handle_checkout(body)
        elif self.path in ('/webhook', '/stripe-webhook', '/api/webhooks/stripe'):
            self._handle_webhook(body)
        elif self.path == '/api/affiliate-signup':
            self._handle_affiliate_signup(body)
        elif self.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        import os
        parsed = urlparse(self.path)
        if parsed.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        elif parsed.path == '/api/affiliate-stats':
            self._handle_affiliate_stats(parsed)
        elif parsed.path in ('/checkout', '/create-checkout', '/create-checkout-session'):
            self._handle_get_checkout_session(parsed)
        elif parsed.path.startswith('/static/'):
            # Serve static component files
            filename = os.path.basename(parsed.path)
            static_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(static_dir, 'static', filename)
            if os.path.isfile(file_path):
                self.send_response(200)
                if filename.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                elif filename.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"HDE Payment Server")

    # ── Stripe Checkout ──────────────────────────────────────────

    def _handle_checkout(self, body):
        # Accept both URL-encoded (from <hd-checkout> web component)
        # and JSON (legacy / direct API callers)
        content_type = self.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            from urllib.parse import parse_qs
            parsed = parse_qs(body.decode('utf-8'), strict_parsing=True)
            # parse_qs returns lists; extract single values
            def v(d, k): return d.get(k, [''])[0]
            data = {
                'name': v(parsed, 'customer_name') or v(parsed, 'name'),
                'email': v(parsed, 'customer_email') or v(parsed, 'email'),
                'report': v(parsed, 'product') or v(parsed, 'report'),
                'birthdate': v(parsed, 'birth_date') or v(parsed, 'birthdate'),
                'birthtime': v(parsed, 'birth_time') or v(parsed, 'birthtime'),
                'location': v(parsed, 'birth_city') or v(parsed, 'location'),
                'partner': v(parsed, 'partner'),
                'state': v(parsed, 'state'),
                'tax_line': v(parsed, 'tax_line'),
                'ref': v(parsed, 'ref'),
                'lat': v(parsed, 'lat'),
                'lon': v(parsed, 'lon'),
                'timezone': v(parsed, 'timezone') or 'UTC',
                'poster_size': v(parsed, 'poster_size'),
                'poster_image_url': v(parsed, 'poster_image_url') or v(parsed, 'mockup_url'),
                'print_file_url': v(parsed, 'print_file_url'),
            }
        else:
            data = json.loads(body)
            # FastAPI/Pages checkout callers send customer data under metadata
            # with product_name/price_cents at top level. Normalize that shape so
            # /api/checkout/create-session can be routed here and still create a
            # real Stripe Checkout session instead of the old mock fallback.
            if isinstance(data.get('metadata'), dict):
                meta_in = data.get('metadata') or {}
                normalized = dict(meta_in)
                normalized.setdefault('email', data.get('email', ''))
                normalized.setdefault('price', data.get('price_cents', 900))
                normalized.setdefault('product_name', data.get('product_name', ''))
                normalized.setdefault('product_description', data.get('product_description', ''))
                data = normalized

        name = data.get('name', '')
        email = data.get('email', '')
        report = data.get('report', 'natal')
        birthdate = data.get('birthdate', '')
        birthtime = data.get('birthtime', '')
        location = data.get('location', '')
        partner = data.get('partner', '')
        state = data.get('state', '').upper()
        tax_line = data.get('tax_line', '').lower() == 'true'
        lat = data.get('lat', '')
        lon = data.get('lon', '')
        timezone = data.get('timezone', 'UTC')
        ref = data.get('ref', '')

        # Align field names for metadata
        meta = {
            "name": name, "report": report, "birthdate": birthdate,
            "birthtime": birthtime, "location": location,
            "lat": str(lat), "lon": str(lon), "timezone": timezone,
            "partner": partner or "", "email": email
        }
        if ref:
            meta["ref"] = ref
        r_lower = (report or '').lower()
        is_poster = r_lower in {'poster', 'print-poster', 'poster-print'}
        if is_poster:
            poster_size = str(data.get('poster_size') or '24x36')
            meta.update({
                "product_type": "print",
                "poster_size": poster_size,
                "poster_image_url": data.get('poster_image_url', ''),
                "print_file_url": data.get('print_file_url', ''),
                "printful_sku": printful.poster_sku(poster_size),
            })

        if r_lower == 'natal':
            price = 900; price_id = None
            product_name = "Human Design Natal Report"
            product_desc = f"Personalized HD Natal report for {name}"
        elif r_lower == 'synastry':
            price = 1400; price_id = None
            product_name = "Human Design Synastry Report"
            product_desc = f"Personalized HD Synastry report for {name}"
        elif r_lower == 'transit':
            price = 1400; price_id = None
            product_name = "Human Design Transit Report"
            product_desc = f"Personalized HD Transit report for {name}"
        elif r_lower == 'bundle':
            price = 2900; price_id = None
            product_name = "Human Design Complete Bundle"
            product_desc = f"Complete Natal, Transit, and Relationship reports for {name}"
        elif r_lower == 'belief-standard':
            price = 1900; price_id = BELIEF_STANDARD_PRICE_ID
            product_name = "Belief Standard Workbook"
            product_desc = "Standard Deconditioning Workbook: 300-500 belief pairs, PDF delivered via email"
        elif r_lower == 'belief-comprehensive':
            price = 2900; price_id = BELIEF_COMPREHENSIVE_PRICE_ID
            product_name = "Belief Comprehensive Workbook"
            product_desc = "Comprehensive Deconditioning Workbook: 800-1,200+ belief pairs, full PDF delivered via email"
        elif r_lower == 'unchained-digital':
            price = 99700; price_id = UNCHAINED_DIGITAL_PRICE_ID
            product_name = "Unchained Wholeness Digital"
            product_desc = "Full 8-week personalized deconditioning program"
        elif r_lower == 'unchained-retreat':
            price = 599700; price_id = UNCHAINED_RETREAT_PRICE_ID
            product_name = "Unchained Wholeness + Hawaii Retreat"
            product_desc = "Full program + all-inclusive 5-day Hawaii retreat"
        elif is_poster:
            poster_size = str(data.get('poster_size') or '24x36')
            poster_price_key = printful.poster_sku(poster_size).replace('poster_', '', 1)
            poster_prices = {'12x18': 3900, '18x24': 4900, '24x36': 7900}
            price = poster_prices.get(poster_price_key, 7900); price_id = None
            product_name = f"Human Design Poster Print {poster_size}"
            product_desc = f"Printed Human Design poster for {name}"
        else:
            price = int(data.get('price', 900)); price_id = None
            product_name = f"Human Design {report.title()} Report"
            product_desc = f"Personalized HD report for {name}"

        # Build line_items — use Stripe price IDs only in live mode. Staging/test
        # keys cannot use live Price IDs, so fall back to price_data to keep every
        # checkout form testable and priced exactly as the site displays.
        if price_id and USE_CONFIGURED_PRICE_IDS:
            line_items = [{"price": price_id, "quantity": 1}]
        else:
            product_data: dict[str, object] = {"name": product_name, "description": product_desc}
            if is_poster and data.get('poster_image_url'):
                product_data["images"] = [str(data.get('poster_image_url'))]
            line_items = [{
                "price_data": {
                    "currency": "usd",
                    "product_data": product_data,
                    "unit_amount": price
                },
                "quantity": 1
            }]

        # Hawaii GET (4.725%) — added as separate line item (not for digital belief/unchained products)
        if (state == 'HI' or tax_line) and r_lower not in ('belief-standard', 'belief-comprehensive', 'unchained-digital', 'unchained-retreat'):
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Hawaii General Excise Tax (4.725%)",
                        "description": f"Hawaii GET for Oahu-based customer"
                    },
                    "unit_amount": int(price * 0.04725)
                },
                "quantity": 1
            })

        # Success URL
        if r_lower == 'bundle' or is_poster:
            success_url = "https://humandesignengine.com/success.html?session_id={CHECKOUT_SESSION_ID}"
        else:
            import urllib.parse
            success_params = {
                "session_id": "{CHECKOUT_SESSION_ID}",
                "name": name or "",
                "email": email or "",
                "report": report or "",
                "birthdate": birthdate or "",
                "birthtime": birthtime or "",
                "location": location or "",
                "partner": partner or ""
            }
            if ref:
                success_params["ref"] = ref
            success_url = f"https://humandesignengine.com/upsell.html?{urllib.parse.urlencode(success_params)}"

        stripe_payload = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": "https://humandesignengine.com/buy-report.html",
            "customer_email": email,
            "metadata": meta
        }
        if is_poster:
            stripe_payload["shipping_address_collection"] = {"allowed_countries": ["US", "CA"]}
            stripe_payload["phone_number_collection"] = {"enabled": True}

        session = self._stripe("POST", "/v1/checkout/sessions", stripe_payload)
        self._json({"url": session.get("url", "")})

    # ── Webhook (Stripe → Report generation) ──────────────────────

    def _handle_webhook(self, body):
        sig = self.headers.get('Stripe-Signature', '')
        # Verify webhook signature using our custom signature verifier
        if STRIPE_WEBHOOK_SECRET:
            if not verify_stripe_signature(body, sig, STRIPE_WEBHOOK_SECRET):
                self.send_response(400); self.end_headers(); return

        event = json.loads(body)
        if event.get('type') == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            if printful.is_print_order(metadata):
                try:
                    result = printful.create_order(session)
                    order_id = (result.get('result') or result).get('id') if isinstance(result, dict) else None
                    print(f"✅ Printful poster order submitted for {metadata.get('email', '')}: {order_id or 'draft created'}")
                except Exception as e:
                    print(f"❌ Failed to submit Printful poster order: {e}")
                    self._json({"received": False, "error": "printful_order_failed"}, 500)
                    return
            else:
                self._generate_and_send(metadata)

            # Track affiliate conversion
            ref = metadata.get('ref', '')
            report = metadata.get('report', 'natal')
            if ref:
                self._record_affiliate_conversion(ref, report)

        self._json({"received": True})

    def _record_affiliate_conversion(self, ref, report):
        """Increment affiliate conversion counter and earnings"""
        affiliates = _load_affiliates()
        for code, data in affiliates.items():
            if code == ref:
                data.setdefault('conversions', 0)
                data.setdefault('earnings', 0.0)
                data['conversions'] += 1
                commission = COMMISSION_RATES.get(report, 5.70)
                data['earnings'] += commission
                _save_affiliates(affiliates)
                print(f"💰 Affiliate {data.get('name','?')} earned ${commission:.2f} from {report} report")
                return
        # If ref not found, it might be an old tracking link; silently ignore

    # ── Affiliate Signup ─────────────────────────────────────────

    def _handle_affiliate_signup(self, body):
        data = json.loads(body)
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        website = (data.get('website') or '').strip()

        if not name or not email:
            self._json({"error": "Name and email required"}, 400)
            return

        affiliates = _load_affiliates()

        # Check if email already registered
        for code, info in affiliates.items():
            if info.get('email') == email:
                self._json({"code": code, "existing": True})
                return

        code = _generate_ref_code(email)
        affiliates[code] = {
            "name": name,
            "email": email,
            "website": website,
            "clicks": 0,
            "conversions": 0,
            "earnings": 0.0,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        _save_affiliates(affiliates)
        print(f"🆕 Affiliate signed up: {name} <{email}> code={code}")
        self._json({"code": code, "existing": False})

    # ── Affiliate Stats ──────────────────────────────────────────

    def _handle_affiliate_stats(self, parsed):
        params = parse_qs(parsed.query)
        code = (params.get('code', [''])[0]).strip()

        if not code:
            self._json({"error": "Missing code parameter"}, 400)
            return

        affiliates = _load_affiliates()
        if code not in affiliates:
            self._json({"error": "Referral code not found"}, 404)
            return

        info = affiliates[code]
        self._json({
            "code": code,
            "name": info.get("name", ""),
            "email": info.get("email", ""),
            "website": info.get("website", ""),
            "clicks": info.get("clicks", 0),
            "conversions": info.get("conversions", 0),
            "earnings": info.get("earnings", 0.0)
        })

    def _handle_get_checkout_session(self, parsed):
        params = parse_qs(parsed.query)
        session_id = (params.get('session_id', [''])[0]).strip()
        if not session_id:
            self._json({"error": "Missing session_id parameter"}, 400)
            return
        if not STRIPE_KEY:
            self._json({"error": "Stripe is not configured."}, 503)
            return
        try:
            session = self._stripe("GET", f"/v1/checkout/sessions/{session_id}")
            self._json(session)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    # ── Report Generation & Email ─────────────────────────────────

    def _generate_and_send(self, meta):
        """Compute chart → generate PDF/Workbook → email to customer"""
        name = meta.get('name', 'Friend'); email = meta.get('email', '')
        report = meta.get('report', 'natal')
        birthdate = meta.get('birthdate', '2000-01-01')
        birthtime = meta.get('birthtime', '12:00')
        location = meta.get('location', 'Unknown')

        # Guard against empty values for coordinates
        lat_val = meta.get('lat', '0')
        lon_val = meta.get('lon', '0')
        lat = float(lat_val) if lat_val else 0.0
        lon = float(lon_val) if lon_val else 0.0
        timezone = meta.get('timezone', 'UTC')
        partner = meta.get('partner', '')

        if report in ('unchained-digital', 'unchained-retreat'):
            try:
                self._email_unchained_welcome(email, name, report)
                print(f"✅ Unchained welcome email sent to {email}")
            except Exception as e:
                print(f"❌ Failed to send Unchained welcome: {e}")
        elif report in ('standard', 'comprehensive', 'belief-standard', 'belief-comprehensive'):
            try:
                tier = 'standard' if 'standard' in report else 'comprehensive'
                res = self._call_belief_server(name, tier, birthdate, birthtime, lat, lon, location, timezone)
                markdown = res.get('markdown', '')
                import os
                os.makedirs("/tmp/hde-reports", exist_ok=True)
                md_path = f"/tmp/hde-reports/{name}_Belief_Workbook.md"
                with open(md_path, 'w') as f:
                    f.write(markdown)
                self._email_markdown_workbook(email, name, tier, md_path)
                print(f"✅ Belief workbook sent to {email}")
            except Exception as e:
                print(f"❌ Failed: {e}")
        else:
            try:
                pdf_path = self._compute_and_render(name, report, birthdate, birthtime,
                                                     lat, lon, location, timezone, partner)
                self._email_report(email, name, report, pdf_path)
                print(f"✅ Report sent to {email}")
            except Exception as e:
                print(f"❌ Failed: {e}")

    def _call_belief_server(self, name, tier, birthdate, birthtime, lat, lon, location, timezone):
        """Call belief server to generate workbook"""
        # Parse birthdate
        try:
            from datetime import datetime
            dt = datetime.strptime(birthdate, "%Y-%m-%d")
            year = dt.year
            month = dt.month
            day = dt.day
        except Exception:
            year = 2000; month = 1; day = 1

        try:
            tm = datetime.strptime(birthtime, "%H:%M")
            hour = tm.hour
            minute = tm.minute
        except Exception:
            hour = 12; minute = 0

        payload = json.dumps({
            "name": name,
            "tier": tier,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "latitude": lat,
            "longitude": lon,
            "timezone": timezone
        }).encode('utf-8')

        req = urllib.request.Request("http://localhost:8092/generate", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Belief-Secret", BELIEF_SERVER_SECRET)

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"❌ Failed to call belief server: {e}")
            raise

    def _email_unchained_welcome(self, to_email, name, report):
        """Send the Unchained Wholeness welcome email"""
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email

        is_retreat = (report == 'unchained-retreat')
        tier_name = "Unchained Wholeness + Hawaii Retreat" if is_retreat else "Unchained Wholeness Digital"
        msg['Subject'] = f"Welcome to {tier_name}, {name}!"

        import datetime
        today = datetime.date.today()
        next_monday = today + datetime.timedelta(days=(7 - today.weekday()) % 7 or 7)
        start_date_str = next_monday.strftime("%A, %B %d, %Y")

        retreat_details = ""
        if is_retreat:
            retreat_details = f"""
========================================================================
🏝️ HAWAII RETREAT COORDINATION
========================================================================
As a Hawaii Retreat tier participant, your package includes our all-inclusive
5-day 'Aina Alignment Eco-Immersion in beautiful Hawaii.

Please visit your Retreat Logistics Hub to book your dates and review pre-travel info:
👉 https://humandesignengine.com/unchained-wholeness/retreat-logistics.html

Becca will also contact you personally to coordinate your travel arrangements.
"""

        body = f"""Hi {name},

Welcome to {tier_name}! You have taken a monumental step toward breaking your conditioning and reclaiming your true Human Design sovereignty.

Here is what you need to know as we prepare to begin your 8-week journey:

1. PROGRAM START DATE
Your cohort officially starts on {start_date_str}.
Starting that morning, you will receive your daily deconditioning emails containing your morning, afternoon, and evening somatic and nervous system regulation plans.

2. VIRTUAL COACHING WITH BECCA (4 Sessions)
You have 4 private coaching sessions included in your program. These sessions combine root-level inquiry, somatic release, and custom belief mapping.
Please book your first session with Becca here:
👉 https://cal.com/becca-hde/coaching
{retreat_details}
3. 8-WEEK PERSONALIZED JOURNEY
Every single day for the next 56 days, you will receive a guided drip email containing somatic movement exercises, traditional Chinese medicine organ resets, and vagus nerve stimulation practices designed to return you to alignment.

Prepare your space, open your mind, and get ready to dismantle the structures that have held you back.

With gratitude and respect,

Michael & Becca
The Human Design Engine Team
https://humandesignengine.com
"""

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

    def _email_markdown_workbook(self, to_email, name, report, md_path):
        """Send the markdown workbook via email"""
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = f"Your Belief Deprogrammer {report.title()} Workbook is Ready, {name}!"

        body = f"""Hi {name},

Your personalized Belief Deprogrammer {report.title()} Workbook is attached as a Markdown file.

You can open this file in any text editor or markdown viewer.

With gratitude,
The Human Design Engine Team
humandesignengine.com"""

        msg.attach(MIMEText(body, 'plain'))

        with open(md_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='octet-stream')
            attachment.add_header('Content-Disposition', 'attachment',
                                   filename=f'{name}_Belief_{report}_Workbook.md')
            msg.attach(attachment)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)


    def _compute_and_render(self, name, report, birthdate, birthtime,
                             lat, lon, location, timezone, partner):
        """POST to reports server, get back rendered PDF path"""
        payload = json.dumps({
            "name": name, "report": report,
            "birthdate": birthdate, "birthtime": birthtime,
            "lat": lat, "lon": lon,
            "location": location, "timezone": timezone,
            "partner": partner
        }).encode()

        req = urllib.request.Request(f"{REPORTS_SERVER}/api/compute",
                                      data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-API-Key", HDE_API_KEY)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())

        if not result.get("success"):
            raise RuntimeError(f"Reports server error: {result}")

        return result["pdf_path"]

    def _email_report(self, to_email, name, report, pdf_path):
        """Send the PDF report via email"""
        msg = MIMEMultipart('mixed')
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        subject, body, html = build_report_email(name, report)
        msg['Subject'] = subject
        attach_themed_alternative(msg, body, html)

        with open(pdf_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment',
                                   filename=f'{name}_HD_{report}_Report.pdf')
            msg.attach(attachment)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

    # ── Helpers ──────────────────────────────────────────────────

    def _stripe_encode(self, params, prefix=""):
        flat = {}
        if isinstance(params, dict):
            for k, v in params.items():
                new_prefix = f"{prefix}[{k}]" if prefix else k
                flat.update(self._stripe_encode(v, new_prefix))
        elif isinstance(params, list):
            for i, v in enumerate(params):
                new_prefix = f"{prefix}[{i}]"
                flat.update(self._stripe_encode(v, new_prefix))
        elif params is not None:
            flat[prefix] = params
        return flat

    def _stripe(self, method, path, data=None):
        # Stripe API requires application/x-www-form-urlencoded
        import urllib.parse
        if data and method == "POST":
            encoded_flat = self._stripe_encode(data)
            encoded = urllib.parse.urlencode(encoded_flat).encode()
        else:
            encoded = None

        req = urllib.request.Request(
            f"https://api.stripe.com{path}",
            data=encoded,
            method=method,
            headers={
                "Authorization": f"Bearer {STRIPE_KEY}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            import sys
            print(f"[stripe] HTTP {e.code}: {body[:500]}", file=sys.stderr, flush=True)
            raise

    def _json(self, data, status=200):
        self.send_response(status); self._cors()
        self.send_header('Content-Type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Stripe-Signature')

    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")

if __name__ == '__main__':
    print(f"🚀 HDE Payment Server on port {PORT}")
    print(f"   Stripe: {'configured' if STRIPE_KEY else '⚠️  MISSING STRIPE_SECRET_KEY'}")
    print(f"   SMTP: {'configured' if SMTP_USER else '⚠️  MISSING SMTP (email disabled)'}")
    print(f"   Reports: {REPORTS_SERVER}")
    print(f"   Affiliates: {AFFILIATES_FILE}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
