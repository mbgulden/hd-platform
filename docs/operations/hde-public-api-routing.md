# HDE public API routing policy

GRO-4007 separates uptime/revenue routes from operator diagnostics so Cloudflare Access policy changes do not block checkout or report delivery.

## Public routes

These routes must not require a Cloudflare Access login:

- `GET /ping` — basic service liveness.
- `GET /api/health` — public uptime-safe FastAPI health probe.
- `POST /api/checkout/create-session` — checkout creation from product pages.
- `GET /api/checkout/session` — success-page checkout/session lookup.
- `POST /api/public/compute-chart` — embeddable/free chart computation.
- `GET|POST /api/public/bodygraph` — embeddable bodygraph rendering.
- `GET /api/public/catalog` — product catalog/pricing.
- `POST /api/public/capture-lead` — lead capture from the public widget.
- `GET /api/reports/download/{filename}` — report delivery after purchase.

API-key protected compute routes such as `POST /api/compute` and `POST /api/compute-chart` are not public; they remain protected by `X-API-Key`.

## Protected diagnostics

These FastAPI endpoints expose runtime inventory and must stay behind Cloudflare Access service-token headers or an operator bearer token:

- `GET /api/diagnostics/routes`

FastAPI diagnostics fail closed: if neither `HDE_DIAGNOSTIC_TOKEN` nor `CF_ACCESS_CLIENT_ID` + `CF_ACCESS_CLIENT_SECRET` is configured, diagnostic calls return `503` instead of becoming public. Wrong credentials return `403`.

The standalone reports server was left in-place to avoid closing the existing paid report delivery surface; the verifier asserts its public report download and public chart/bodygraph/lead endpoints remain present.

## Verification

Run:

```bash
python3 scripts/verify_hde_public_api_routing.py
python3 -m pytest tests/test_public_api_routing.py -q
```

The verifier is intentionally static so it can run in CI/Hermes without live Stripe, Redis, SQLAlchemy, or engine credentials.
