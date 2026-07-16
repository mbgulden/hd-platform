# HDE Coach Portal — Cloudflare Access exposure

The staging coach portal is exposed at:

```text
https://staging.humandesignengine.com/coach/dashboard
```

## Auth model

The public route is intended to sit behind the existing Cloudflare Access policy for Michael and Becca:

- `mbgulden@gmail.com`
- `Becca.gulden@gmail.com` / `becca.gulden@gmail.com`

The origin Nginx route serves the `/coach/dashboard` HTML shell so the portal page is visible at the expected staging URL. Customer data APIs are still protected by backend auth: a valid Cloudflare Access authenticated email header or the legacy `COACH_ACCESS_TOKEN`.

The app supports the legacy `COACH_ACCESS_TOKEN` for local/internal troubleshooting, but the staging UI first attempts Cloudflare Access session auth and only shows the token prompt if no Access session is present.

## Backend paths

- Dashboard HTML: `/coach/dashboard` → `hde_orchestrator_staging.service` on `127.0.0.1:8011`
- Client list: `/api/coach/clients`
- Client review: `/api/coach/review`
- Step updates: `/api/coach/update_steps`

All coach data APIs still enforce the customer consent gate before reading or writing client workspace files.

## Verification checklist

1. `python3 -m py_compile scripts/vm_orchestrator.py`
2. Local dashboard returns `200` from `http://127.0.0.1:8011/coach/dashboard`.
3. Local Cloudflare-header simulation for `/api/coach/session` returns `method=cloudflare_access` for an allowed email.
4. Public unauthenticated `/coach/dashboard` should return the HTML shell `200`; public unauthenticated `/api/coach/session` should return `401` and must not expose client data.
5. After authenticating through Cloudflare Access, allowed emails should reach the dashboard and client APIs without entering the legacy token.
