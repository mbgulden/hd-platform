"""
Human Design Engine — Payment & Report Server
Handles Stripe Checkout → Webhook → Reports Server → PDF → Email
Affiliate tracking: signup, stats, and commission tracking
Run: STRIPE_SECRET_KEY=sk_... STRIPE_WEBHOOK_SECRET=whsec_... python3 server.py
"""
import os, json, smtplib, hashlib, hmac, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request

STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "reports@humandesignengine.com")
REPORTS_SERVER = os.environ.get("REPORTS_SERVER", "http://localhost:8081")
HDE_API_KEY = os.environ.get("HDE_API_KEY", "")
PORT = int(os.environ.get("PORT", "8000"))
AFFILIATES_FILE = "/tmp/hde-reports/affiliates.json"

# Commission rates per report type (30% of report price)
COMMISSION_RATES = {"natal": 5.70, "synastry": 8.70, "transit": 8.70, "bundle": 17.70}

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

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''

        if self.path == '/create-checkout':
            self._handle_checkout(body)
        elif self.path == '/webhook':
            self._handle_webhook(body)
        elif self.path == '/api/affiliate-signup':
            self._handle_affiliate_signup(body)
        elif self.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if self.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        elif parsed.path == '/api/affiliate-stats':
            self._handle_affiliate_stats(parsed)
        else:
            self.send_response(200); self.end_headers()
            self.wfile.write(b"HDE Payment Server")

    # ── Stripe Checkout ──────────────────────────────────────────

    def _handle_checkout(self, body):
        data = json.loads(body)
        name = data.get('name'); email = data.get('email')
        report = data.get('report'); price = data.get('price', 1900)
        birthdate = data.get('birthdate'); birthtime = data.get('birthtime')
        location = data.get('location'); partner = data.get('partner')
        lat = data.get('lat', ''); lon = data.get('lon', '')
        timezone = data.get('timezone', 'UTC')
        ref = data.get('ref', '')

        meta = {"name": name, "report": report, "birthdate": birthdate,
                "birthtime": birthtime, "location": location,
                "lat": str(lat), "lon": str(lon), "timezone": timezone,
                "partner": partner or "", "email": email}
        if ref:
            meta["ref"] = ref

        session = self._stripe("POST", "/v1/checkout/sessions", {
            "payment_method_types": ["card"],
            "line_items": [{"price_data": {
                "currency": "usd",
                "product_data": {"name": f"Human Design {report.title()} Report",
                                 "description": f"Personalized HD report for {name}"},
                "unit_amount": price
            }, "quantity": 1}],
            "mode": "payment",
            "success_url": "https://humandesignengine.com/success?session={CHECKOUT_SESSION_ID}",
            "cancel_url": "https://humandesignengine.com/buy-report.html",
            "customer_email": email,
            "metadata": meta
        })
        self._json({"url": session.get("url", "")})

    # ── Webhook (Stripe → Report generation) ──────────────────────

    def _handle_webhook(self, body):
        sig = self.headers.get('Stripe-Signature', '')
        # Verify webhook signature
        if STRIPE_WEBHOOK_SECRET:
            try:
                import stripe
                stripe.Webhook.construct_event(body, sig, STRIPE_WEBHOOK_SECRET)
            except Exception:
                self.send_response(400); self.end_headers(); return

        event = json.loads(body)
        if event.get('type') == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
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

    # ── Report Generation & Email ─────────────────────────────────

    def _generate_and_send(self, meta):
        """Compute chart → generate PDF → email to customer"""
        name = meta.get('name', 'Friend'); email = meta.get('email', '')
        report = meta.get('report', 'natal')
        birthdate = meta.get('birthdate', '2000-01-01')
        birthtime = meta.get('birthtime', '12:00')
        location = meta.get('location', 'Unknown')
        lat = float(meta.get('lat', 0)); lon = float(meta.get('lon', 0))
        timezone = meta.get('timezone', 'UTC')
        partner = meta.get('partner', '')

        try:
            pdf_path = self._compute_and_render(name, report, birthdate, birthtime,
                                                 lat, lon, location, timezone, partner)
            self._email_report(email, name, report, pdf_path)
            print(f"✅ Report sent to {email}")
        except Exception as e:
            print(f"❌ Failed: {e}")

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
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = f"Your Human Design {report.title()} Report is Ready, {name}!"

        body = f"""Hi {name},

Your Human Design {report.title()} Report is attached as a PDF.

This report was computed using verified, open-source calculations — the same engine trusted by developers and practitioners worldwide.

If you have any questions about your chart, we're here to help. Just reply to this email.

With gratitude,
The Human Design Engine Team
humandesignengine.com"""

        msg.attach(MIMEText(body, 'plain'))

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

    def _stripe(self, method, path, data=None):
        req = urllib.request.Request(f"https://api.stripe.com{path}", method=method)
        req.add_header("Authorization", f"Bearer {STRIPE_KEY}")
        req.add_header("Content-Type", "application/json")
        if data:
            req.data = json.dumps(data).encode()
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())

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
