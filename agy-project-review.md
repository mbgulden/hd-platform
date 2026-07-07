# Project Review: Human Design Engine (HDE) Platform

This document reviews the current development and operational state of the **Human Design Engine (HDE) Platform** located at `/home/ubuntu/work/hd-platform/`.

---

## 1. Core Findings & Architecture Status

The project codebase currently contains two parallel system architectures designed to run the application:

### A. Standalone Python Service Architecture (Lean & Functional)
A lightweight setup that runs the application services as native python processes communicating via local files and HTTP APIs.
* **Calculation & PDF Engine:** [reports/server.py](file:///home/ubuntu/work/hd-platform/reports/server.py) runs on port `8081` and handles direct module imports of the [OpenHumanDesignMCP](file:///home/ubuntu/work/OpenHumanDesignMCP) calculation logic. It stores orders locally in a JSON database at `/tmp/hde-reports/orders.json` and renders PDF reports to `/tmp/hde-reports` using the system `wkhtmltopdf` binary.
* **Payment & Checkout Bridge:** [payment/server.py](file:///home/ubuntu/work/hd-platform/payment/server.py) is intended to run on port `8000`. It coordinates Stripe checkout session generation, webhook handling, and affiliate click/conversion/signup tracking via `/tmp/hde-reports/affiliates.json`.
* **Static Web Assets:** Static HTML pages in [docs/](file:///home/ubuntu/work/hd-platform/docs) serve the landing pages, widgets, and developer/affiliate portals.

### B. Docker Compose / FastAPI Architecture (Planned & Incomplete)
A containerized stack orchestrating PostgreSQL, Redis, FastAPI, and Traefik routing.
* **FastAPI Service:** Located in [api/](file:///home/ubuntu/work/hd-platform/api), it relies on [shared/database.py](file:///home/ubuntu/work/hd-platform/shared/database.py) for PostgreSQL ORM modeling (users, subscriptions, usage logs) and [api/middleware.py](file:///home/ubuntu/work/hd-platform/api/middleware.py) for rate-limiting using Lua scripting in Redis.
* **Docker Orchestration:** Described in [docker/docker-compose.yml](file:///home/ubuntu/work/hd-platform/docker/docker-compose.yml).

> [!WARNING]
> The **Docker Compose / FastAPI** architecture is currently **broken and cannot be run** on this host because:
> 1. No `Dockerfile` exists inside the [api/](file:///home/ubuntu/work/hd-platform/api) or [reports/](file:///home/ubuntu/work/hd-platform/reports) directories.
> 2. No container runtime (`docker`, `podman`, etc.) is installed or running on the system.
> 3. No local system instances of PostgreSQL or Redis are installed to support running the FastAPI service natively.
>
> Therefore, **to get to revenue immediately, the Lean Standalone Architecture must be used.**

---

## 2. What's Fully Built & Working

1. **Human Design Calculation Engine:** The [OpenHumanDesignMCP](file:///home/ubuntu/work/OpenHumanDesignMCP) submodule is verified, compiled, and works correctly. All ephemeris data files are resolved locally.
2. **Report Generation Pipeline:**
   * The [reports/server.py](file:///home/ubuntu/work/hd-platform/reports/server.py) server is currently running in the background on port `8081`.
   * It successfully imports the engine, processes natal, transit, and composite calculations, and generates polished PDF reports.
   * `wkhtmltopdf` is installed on the host and works: generating PDF reports (e.g., `/tmp/hde-reports/Test_Transit_transit_1780072068.pdf`) has been verified.
3. **Static Landing Pages & UI Assets:**
   * A Python web server is currently serving static files from [docs/](file:///home/ubuntu/work/hd-platform/docs) on port `8090`.
   * Pages like [landing-reports.html](file:///home/ubuntu/work/hd-platform/docs/landing-reports.html), [buy-report.html](file:///home/ubuntu/work/hd-platform/docs/buy-report.html), [success.html](file:///home/ubuntu/work/hd-platform/docs/success.html), and the affiliate subpages are fully designed and visually rich.
4. **Local Database & JSON State Management:**
   * Simple file-based logs for order records ([orders.json](file:///tmp/hde-reports/orders.json)) work as intended.

---

## 3. What's Incomplete & Broken

1. **Critical Bug in Stripe Payload Encoding:**
   The `_stripe` helper method in [payment/server.py:L295](file:///home/ubuntu/work/hd-platform/payment/server.py#L295) uses `urllib.parse.urlencode(data)` on a nested dictionary payload. Because `urlencode` does not recursively flat-encode dictionaries or lists (e.g., it converts `{"payment_method_types": ["card"]}` into raw strings like `payment_method_types=['card']`), **every request to create a Stripe checkout session fails with an HTTP 400 Bad Request error from Stripe.**
2. **Payment Server is Inactive:**
   The [payment/server.py](file:///home/ubuntu/work/hd-platform/payment/server.py) server is not currently running.
3. **Unconfigured Environment Variables:**
   No `.env` file exists in the [payment/](file:///home/ubuntu/work/hd-platform/payment) directory. The Stripe credentials, SMTP email server options, and the matching shared `HDE_API_KEY` need to be set up.
4. **Missing Production Routing & SSL:**
   The static server and local APIs are only listening on internal localhost ports (`8090` and `8081`). They are not mapped to public domains (`humandesignengine.com` and `api.humandesignengine.com`) with SSL protection.

---

## 4. Top 3 Next Actions to Get to Revenue

To start selling reports and generating revenue, the following three sequential actions must be taken:

### Action 1: Fix the Stripe payload encoding bug in `payment/server.py`
Modify [payment/server.py](file:///home/ubuntu/work/hd-platform/payment/server.py) to recursively format nested dictionaries and arrays into the bracket-notation format expected by the Stripe API (e.g. `line_items[0][price_data][unit_amount]=1900`).

Apply the following code modification:

```diff
     # ── Helpers ──────────────────────────────────────────────────
 
+    def _stripe_encode(self, params, prefix=""):
+        flat = {}
+        if isinstance(params, dict):
+            for k, v in params.items():
+                new_prefix = f"{prefix}[{k}]" if prefix else k
+                flat.update(self._stripe_encode(v, new_prefix))
+        elif isinstance(params, list):
+            for i, v in enumerate(params):
+                new_prefix = f"{prefix}[{i}]"
+                flat.update(self._stripe_encode(v, new_prefix))
+        else:
+            flat[prefix] = params
+        return flat
+
     def _stripe(self, method, path, data=None):
         req = urllib.request.Request(f"https://api.stripe.com{path}", method=method)
         req.add_header("Authorization", f"Bearer {STRIPE_KEY}")
         req.add_header("Content-Type", "application/x-www-form-urlencoded")
         if data:
-            encoded = urllib.parse.urlencode(data).encode()
+            encoded_flat = self._stripe_encode(data)
+            encoded = urllib.parse.urlencode(encoded_flat).encode()
             req.data = encoded
         resp = urllib.request.urlopen(req)
         return json.loads(resp.read())
```

### Action 2: Setup environment variables and start the Payment Server service
1. Copy [payment/.env.template](file:///home/ubuntu/work/hd-platform/payment/.env.template) to `/home/ubuntu/work/hd-platform/payment/.env`.
2. Populate the `.env` file with:
   * A valid Stripe API key (`STRIPE_SECRET_KEY`) and webhook secret (`STRIPE_WEBHOOK_SECRET`).
   * A secure `HDE_API_KEY` (which must match the secret configured in the environment of the reports server).
   * SMTP connection credentials for your email provider (e.g., Mailgun, Resend, or Gmail App Password) to enable PDF delivery.
3. Configure the system service daemon by linking the unit file [hde-payment.service](file:///home/ubuntu/work/hd-platform/payment/hde-payment.service) to systemd, enabling it to run persistently in the background:
   ```bash
   sudo ln -s /home/ubuntu/work/hd-platform/payment/hde-payment.service /etc/systemd/system/hde-payment.service
   sudo systemctl daemon-reload
   sudo systemctl enable hde-payment.service
   sudo systemctl start hde-payment.service
   ```

### Action 3: Configure Nginx as the reverse proxy with Let's Encrypt SSL
Install and configure Nginx to expose the platform to the web:
1. Route the root domain (`humandesignengine.com`) to serve the static landing page assets located in `/home/ubuntu/work/hd-platform/docs/`.
2. Route the api subdomain (`api.humandesignengine.com`) to proxy requests directly to the Payment Server at `http://localhost:8000`.
3. Set up Let's Encrypt SSL certificates for both domains using `certbot`.

Example Nginx Configuration block (`/etc/nginx/sites-available/hd-platform`):
```nginx
# humandesignengine.com (Static site)
server {
    listen 80;
    server_name humandesignengine.com;
    root /home/ubuntu/work/hd-platform/docs;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}

# api.humandesignengine.com (Payment & API router)
server {
    listen 80;
    server_name api.humandesignengine.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
*Run `sudo certbot --nginx -d humandesignengine.com -d api.humandesignengine.com` to apply secure HTTPS redirect rules automatically.*
