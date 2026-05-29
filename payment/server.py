"""
Human Design Engine — Payment & Report Server
Handles Stripe Checkout → Webhook → MCP Compute → PDF → Email
Run: STRIPE_SECRET_KEY=sk_... STRIPE_WEBHOOK_SECRET=whsec_... python3 server.py
"""
import os, json, subprocess, smtplib, hashlib, hmac, time
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
MCP_SERVER = os.environ.get("MCP_SERVER", "http://localhost:8765")
PORT = int(os.environ.get("PORT", "8000"))

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
        elif self.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        if self.path == '/api/ping':
            self._json({"status": "ok", "service": "hde-payment-server"})
        else:
            self.send_response(200); self.end_headers()
            self.wfile.write(b"HDE Payment Server")

    def _handle_checkout(self, body):
        data = json.loads(body)
        name = data.get('name'); email = data.get('email')
        report = data.get('report'); price = data.get('price', 1900)
        birthdate = data.get('birthdate'); birthtime = data.get('birthtime')
        location = data.get('location'); partner = data.get('partner')

        session = self._stripe("POST", "/v1/checkout/sessions", {
            "payment_method_types": ["card"],
            "line_items": [{"price_data": {
                "currency": "usd",
                "product_data": {"name": f"Human Design {report.title()} Report", "description": f"Personalized HD report for {name}"},
                "unit_amount": price
            }, "quantity": 1}],
            "mode": "payment",
            "success_url": f"https://humandesignengine.com/success?session={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"https://humandesignengine.com/buy-report.html",
            "customer_email": email,
            "metadata": {"name": name, "report": report, "birthdate": birthdate, "birthtime": birthtime, "location": location, "partner": partner or "", "email": email}
        })
        self._json({"url": session.get("url", "")})

    def _handle_webhook(self, body):
        sig = self.headers.get('Stripe-Signature', '')
        # Verify webhook signature
        if STRIPE_WEBHOOK_SECRET:
            try:
                import stripe; stripe.Webhook.construct_event(body, sig, STRIPE_WEBHOOK_SECRET)
            except:
                self.send_response(400); self.end_headers(); return

        event = json.loads(body)
        if event.get('type') == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            self._generate_and_send(metadata)

        self._json({"received": True})

    def _generate_and_send(self, meta):
        """Compute chart → generate PDF → email to customer"""
        name = meta.get('name', 'Friend'); email = meta.get('email', '')
        report = meta.get('report', 'natal')
        birthdate = meta.get('birthdate', '2000-01-01'); birthtime = meta.get('birthtime', '12:00')
        location = meta.get('location', 'Unknown')
        partner = meta.get('partner', '')

        try:
            pdf_path = self._compute_and_render(name, report, birthdate, birthtime, location, partner)
            self._email_report(email, name, report, pdf_path)
            print(f"✅ Report sent to {email}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    def _compute_and_render(self, name, report, birthdate, birthtime, location, partner):
        """Call MCP engine, generate PDF"""
        y, m, d = birthdate.split('-')
        h, mi = birthtime.split(':')
        dh = int(h) + int(mi) / 60

        # Call MCP server
        params = urllib.parse.urlencode({"name": name, "year": y, "month": m, "day": d, "hour": dh, "location": location})
        resp = urllib.request.urlopen(f"{MCP_SERVER}/tools/calculate_chart?{params}")
        chart = json.loads(resp.read())

        # Generate markdown report
        md = self._format_report(chart, name, report, partner)

        # Convert to PDF
        os.makedirs("/tmp/hde-reports", exist_ok=True)
        md_path = f"/tmp/hde-reports/{name.replace(' ','_')}_{report}.md"
        pdf_path = f"/tmp/hde-reports/{name.replace(' ','_')}_{report}.pdf"
        with open(md_path, 'w') as f: f.write(md)
        subprocess.run(["pandoc", md_path, "-o", pdf_path, "--pdf-engine=wkhtmltopdf", f"--metadata=title=Human Design {report.title()} Report"], check=True)
        return pdf_path

    def _format_report(self, chart, name, report, partner):
        """Generate a beautiful markdown report"""
        c = chart.get('result', chart)
        centers = c.get('defined_centers', []); undef = c.get('undefined_centers', [])
        channels = c.get('defined_channels', [])
        cross = c.get('incarnation_cross', {}); vars_data = c.get('variables', {})

        return f"""---
title: "Your Human Design {report.title()} Report"
author: "Human Design Engine"
date: "{time.strftime('%B %d, %Y')}"
---

# 🌱 {name}'s Human Design {report.title()}

*Computed by [Human Design Engine](https://humandesignengine.com) — verified open-source calculations*

---

## 🎯 Your Design at a Glance

| Aspect | Your Design |
|--------|-------------|
| **Type** | {c.get('hd_type', c.get('type', 'Unknown'))} |
| **Profile** | {c.get('profile', 'Unknown')} |
| **Decision-Making Style** | {c.get('authority', 'Unknown')} |
| **Strategy** | {c.get('strategy', 'Unknown')} |
| **Definition** | {c.get('definition', 'Unknown')} |
| **Life Theme** | {cross.get('name', 'Unknown')} |

## 🔮 Your Defined Centers ({len(centers)}/9)

Your defined centers are where you carry consistent, reliable energy. These are your natural gifts:

{chr(10).join(f'- **{c}**' for c in centers) if centers else '- None defined (Reflector)'}

## 🌊 Your Open Centers ({len(undef)}/9)

Your undefined centers are where you're open to influence and deeply perceptive:

{chr(10).join(f'- **{c}**' for c in undef) if undef else '- All centers defined'}

## 🔗 Your Channels ({len(channels)})

Channels are the energetic pathways that define your centers. Each represents a specific theme in your life:

{chr(10).join(f'- {ch}' for ch in channels) if channels else '- No channels defined'}

## 🧬 Your Variables

| Transformation | Your Configuration |
|----------------|-------------------|
| Digestion | {vars_data.get('digestion', 'Unknown')} |
| Environment | {vars_data.get('environment', 'Unknown')} |
| Perspective | {vars_data.get('perspective', 'Unknown')} |
| Motivation | {vars_data.get('motivation', 'Unknown')} |

## ✨ Living Your Design

Your **{c.get('authority', 'inner wisdom')}** is your internal compass. When you make decisions through this, you feel **{c.get('signature', 'aligned')}**. When you override it, you feel **{c.get('not_self_theme', 'off-track')}**.

**Today's experiment:** Notice one decision — even a small one — and wait for your {c.get('authority', 'inner wisdom')} to give you clarity before acting.

---

*Report generated by Human Design Engine. Verified calculations powered by OpenHumanDesignMCP (AGPLv3).*
*[humandesignengine.com](https://humandesignengine.com) · [github.com/mbgulden/OpenHumanDesignMCP](https://github.com/mbgulden/OpenHumanDesignMCP)*
"""

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
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{name}_HD_{report}_Report.pdf')
            msg.attach(attachment)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

    def _stripe(self, method, path, data=None):
        req = urllib.request.Request(f"https://api.stripe.com{path}", method=method)
        req.add_header("Authorization", f"Bearer {STRIPE_KEY}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        if data:
            encoded = urllib.parse.urlencode(data).encode()
            req.data = encoded
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())

    def _json(self, data):
        self.send_response(200); self._cors()
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
    print(f"   MCP: {MCP_SERVER}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
