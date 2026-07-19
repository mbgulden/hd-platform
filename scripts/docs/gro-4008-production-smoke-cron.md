# GRO-4008 — Production checkout/report smoke cron

`npm run smoke:production` is the live-safe production smoke for checkout and report delivery. It is designed for cron and CI probes: create an unpaid Stripe Checkout Session, prove it is not paid/complete, expire it when possible, then verify the public report-download path is routable.

The smoke **never completes payment**. It does not submit a card number, does not call the webhook, and does not grant a paid report entitlement. If a session ever reports `paid` or `complete`, the script exits non-zero as a safety violation. Yes, the one thing a smoke test should not do is buy the product at 3am.

## Commands

```bash
npm run verify:production-smoke
npm run smoke:production
```

`verify:production-smoke` is static and safe for pull requests. `smoke:production` is the live cron target.

## Required environment

- `STRIPE_SECRET_KEY` — required for direct Stripe mode and for retrieving/expiring a session created by the public checkout endpoint.

Recommended production cron environment:

- `HDE_SMOKE_BASE_URL=https://humandesignengine.com`
- `HDE_SMOKE_CHECKOUT_ENDPOINT=/api/checkout/create-session`
- `HDE_SMOKE_REPORT_PROBE_PATH=/api/reports/download/__hde_smoke_probe__.pdf`
- `HDE_SMOKE_ALLOW_REPORT_404=true`
- `HDE_SMOKE_EXPIRE_SESSION=true`

Optional fixture mode:

- `HDE_SMOKE_REPORT_URL=https://humandesignengine.com/api/reports/download/<known-smoke-fixture>.pdf`

When `HDE_SMOKE_REPORT_URL` is set, the smoke checks that exact report download URL. Without a fixture, the default synthetic path may return 404; **404 is acceptable** because it proves the public delivery route is reachable and not trapped behind auth. 401/403 is always a failure.

Direct Stripe fallback mode:

- `HDE_SMOKE_DIRECT_STRIPE=true`

This bypasses the public checkout API and creates the unpaid Checkout Session directly through Stripe. Use it when the API route is down and the goal is to isolate Stripe configuration from app routing.

## Cron example

```cron
*/15 * * * * cd /home/ubuntu/work/hd-platform && set -a && . /home/ubuntu/work/hd-platform/.env && set +a && npm run smoke:production >> /var/log/hde-production-smoke.log 2>&1
```

Do not commit `.env`, log files, session JSON, or any backup containing live keys. The script redacts the Stripe key in JSON output; the shell still owns stdout/stderr hygiene.

## Expected JSON evidence

A passing run emits JSON with:

- `ok: true`
- checkout endpoint and Stripe session id (or a note if the public API hides it)
- Stripe status/payment status, which must remain unpaid/open or expired after cleanup
- report delivery probe URL/status/content type
- cleanup status for session expiration

A failing run emits `ok: false` and exits non-zero. Cron should alert on any non-zero exit, especially payment safety violations or report delivery returning 401/403.
