# HD Platform REST API — Reference

**Base URL (production):** `https://api.humandesignengine.com`
**Base URL (staging):** `https://api-staging.humandesignengine.com`
**API version:** v1
**Spec source:** `api/openapi.yaml` (canonical)
**OpenAPI 3.0 mirror:** `api/rapidapi-openapi.yaml` (RapidAPI listing)
**Interactive docs (auto-generated):** `GET /docs` (Swagger UI), `GET /redoc` (ReDoc)

---

## Authentication

All `/v1/*` chart endpoints accept either:

| Mode | Header | Use case |
|------|--------|----------|
| **API key (authenticated)** | `X-API-Key: hd_<32-char-key>` | Registered free/pro/enterprise users |
| **No-auth (rate-limited)** | none | Single-use trial calls (3/day per IP) |

Authenticated requests count against the key's tier rate limit.
No-auth requests use a global IP-based bucket.

API key lifecycle is managed through `/v1/keys/*`:

```
POST   /v1/keys/register  → creates a new key (returns the key in plaintext once)
GET    /v1/keys/status    → returns tier, rate_limit, usage_count, created_at
DELETE /v1/keys/revoke    → revokes the supplied key
```

---

## Rate limits (per tier)

| Tier | Rate limit | Notes |
|------|-----------|-------|
| `free` | 100 req/min | Default on register |
| `pro` | 1000 req/min | Manual upgrade |
| `enterprise` | 10000 req/min | Contact sales |

When exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

---

## Response envelope (v1 standard)

Every successful chart response uses this wrapper:

```json
{
  "success": true,
  "endpoint": "/v1/natal",
  "data": { /* endpoint-specific payload */ },
  "error": null
}
```

On failure:

```json
{
  "success": false,
  "endpoint": "/v1/natal",
  "data": null,
  "error": "Human-readable message"
}
```

---

## Endpoints

### `POST /v1/natal` — Natal chart calculation

Calculate the full natal (birth) chart for a person.

**Auth:** API key OR no-auth (3/day per IP)
**Rate limit:** Per-tier
**Status code:** `200` (success), `400` (validation), `401` (bad key), `429` (rate limit), `502` (downstream failure)

**Request body:**

```json
{
  "name": "Jane Doe",
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "location": "Honolulu, HI",
  "lat": 21.3099,
  "lon": -157.8581,
  "timezone": "Pacific/Honolulu"
}
```

| Field | Type | Required | Validation | Notes |
|-------|------|----------|-----------|-------|
| `name` | string | ✅ | 1–255 chars | Person or entity label |
| `year` | int | ✅ | 1900–2100 | |
| `month` | int | ✅ | 1–12 | |
| `day` | int | ✅ | 1–31 | |
| `hour` | int | ✅ | 0–23 | |
| `minute` | int | ❌ (default 0) | 0–59 | |
| `location` | string | ❌ | ≤500 chars | Display label |
| `lat` | float | ❌ | -90 to 90 | If present, `lon` must also be present |
| `lon` | float | ❌ | -180 to 180 | |
| `timezone` | string | ❌ | IANA tz name | e.g. `Pacific/Honolulu`, `UTC` |

**Response `data` payload (truncated):**

```json
{
  "type": "Generator",
  "strategy": "To Respond",
  "authority": "Sacral",
  "profile": "3/5",
  "incarnation_cross": "Right Angle Cross of Eden",
  "definition": "Single",
  "centers": { "head": { "defined": true }, "ajna": { "defined": false }, "...": {} },
  "channels": [ { "id": "34-20", "name": "Channel of Charisma", "activated": true }, ... ],
  "gates": [ { "number": 1, "planet": "Sun", "line": 3, "color": 1, "tone": 1, "base": 1 }, ... ],
  "personality_planets": { "sun": { "gate": 1, "line": 3, "longitude": 123.45 }, "...": {} },
  "design_planets": { "sun": { "gate": 43, "line": 1, "longitude": 88.21 }, "...": {} }
}
```

**Code example (Python):**

```python
import requests

resp = requests.post(
    "https://api.humandesignengine.com/v1/natal",
    headers={"X-API-Key": "hd_YOUR_KEY_HERE"},
    json={
        "name": "Jane Doe",
        "year": 1990, "month": 6, "day": 15,
        "hour": 14, "minute": 30,
        "lat": 21.3099, "lon": -157.8581,
        "timezone": "Pacific/Honolulu",
    },
    timeout=10,
)
resp.raise_for_status()
chart = resp.json()["data"]
print(chart["type"], chart["profile"])
```

**Code example (curl):**

```bash
curl -X POST https://api.humandesignengine.com/v1/natal \
  -H "X-API-Key: hd_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "year": 1990, "month": 6, "day": 15,
    "hour": 14, "minute": 30,
    "lat": 21.3099, "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
  }'
```

---

### `POST /v1/natal/noauth` — Natal chart (no API key)

Same request/response as `POST /v1/natal` but does not require an API key.
Rate-limited to 3 requests/day per source IP. Use for landing-page free chart calculators.

---

### `POST /v1/transits` — Planetary transits

Calculate current planetary transits relative to a natal chart. Optionally projects to a target date.

**Auth:** API key required (no no-auth variant)
**Status code:** `200` (success), `400`, `401`, `429`, `502`

**Request body:**

```json
{
  "name": "Jane Doe",
  "year": 1990, "month": 6, "day": 15,
  "hour": 14, "minute": 30,
  "lat": 21.3099, "lon": -157.8581,
  "timezone": "Pacific/Honolulu",
  "target_date": "2026-06-20"
}
```

`target_date` is optional `YYYY-MM-DD`. If omitted, returns transits for "now".

**Response `data` payload (truncated):**

```json
{
  "transits": [
    {
      "transit_planet": "Sun",
      "natal_planet": "Moon",
      "aspect": "trine",
      "orb": 1.2,
      "exact_date": "2026-06-21T08:00:00Z",
      "gate": 12,
      "line": 4,
      "channel": { "id": "12-22", "name": "Channel of Openness" }
    }
  ],
  "active_channels": [...],
  "target_date": "2026-06-20"
}
```

**Code example (Python):**

```python
import requests
from datetime import date

resp = requests.post(
    "https://api.humandesignengine.com/v1/transits",
    headers={"X-API-Key": "hd_YOUR_KEY_HERE"},
    json={
        "name": "Jane Doe",
        "year": 1990, "month": 6, "day": 15,
        "hour": 14, "minute": 30,
        "lat": 21.3099, "lon": -157.8581,
        "timezone": "Pacific/Honolulu",
        "target_date": date.today().isoformat(),
    },
)
resp.raise_for_status()
print(len(resp.json()["data"]["transits"]), "active transits")
```

---

### `POST /v1/bodygraph` — Bodygraph rendering data

Returns the structured data needed to render an SVG/Canvas bodygraph: centers (defined/undefined), channels, gates, and type-specific overlays.

**Auth:** API key OR no-auth
**Status code:** `200`, `400`, `401`, `429`, `502`

**Request body:** Same as natal chart.

**Response `data` payload (truncated):**

```json
{
  "type": "Generator",
  "profile": "3/5",
  "centers": [
    { "id": "head", "defined": true, "x": 220, "y": 40 },
    { "id": "ajna", "defined": false, "x": 220, "y": 130 },
    { "id": "throat", "defined": true, "x": 220, "y": 220 },
    { "id": "g", "defined": false, "x": 80, "y": 310 },
    { "id": "heart", "defined": true, "x": 220, "y": 310 },
    { "id": "solar_plexus", "defined": false, "x": 360, "y": 310 },
    { "id": "sacral", "defined": true, "x": 220, "y": 410 },
    { "id": "root", "defined": false, "x": 220, "y": 500 },
    { "id": "spleen", "defined": true, "x": 80, "y": 410 }
  ],
  "channels": [
    { "id": "34-20", "name": "Channel of Charisma", "active": true, "from": "sacral", "to": "throat" }
  ],
  "gates": [
    { "number": 34, "planet": "Sun", "line": 3, "center": "sacral" }
  ],
  "type_overlay": { "color": "#ff8800", "label": "Generator" }
}
```

The `x`/`y` coordinates are normalized to a 440×540 viewport. Use them to position SVG groups directly.

---

### `POST /v1/bodygraph/noauth` — Bodygraph (no API key)

Same as `POST /v1/bodygraph` but no API key required. 3/day per IP.

---

### `POST /v1/synastry` — Relationship (synastry) chart

Calculate compatibility between two people: shared channels, electromagnetic connections, and composite type.

**Auth:** API key required
**Status code:** `200`, `400`, `401`, `429`, `502`

**Request body:**

```json
{
  "person_a": {
    "name": "Jane Doe",
    "year": 1990, "month": 6, "day": 15,
    "hour": 14, "minute": 30,
    "lat": 21.3099, "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
  },
  "person_b": {
    "name": "John Smith",
    "year": 1988, "month": 3, "day": 22,
    "hour": 8, "minute": 15,
    "lat": 40.7128, "lon": -74.0060,
    "timezone": "America/New_York"
  }
}
```

**Response `data` payload (truncated):**

```json
{
  "person_a": { "name": "Jane Doe", "type": "Generator", "profile": "3/5" },
  "person_b": { "name": "John Smith", "type": "Projector", "profile": "6/2" },
  "shared_channels": [
    { "id": "34-20", "name": "Channel of Charisma", "type": "electromagnetic", "a_activates": true, "b_activates": true }
  ],
  "composite_type": "MG (Mutual Reception)",
  "compatibility_score": 0.78,
  "relationship_field": "compromise"
}
```

---

### `POST /v1/payment/create-checkout` — Stripe checkout session

Create a Stripe Checkout Session for a single-report purchase ($9.99). Returns the session URL to redirect the buyer to.

**Auth:** None (session-bound by Stripe)
**Status code:** `200`, `400`, `503` (Stripe not configured)

**Request body:**

```json
{
  "name": "Jane Doe",
  "year": 1990, "month": 6, "day": 15,
  "hour": 14, "minute": 30,
  "lat": 21.3099, "lon": -157.8581,
  "timezone": "Pacific/Honolulu",
  "email": "jane@example.com",
  "report_type": "full"
}
```

`report_type` is one of `full` ($9.99) or `compatibility` ($14.99).

**Response:**

```json
{
  "session_id": "cs_test_a1b2c3...",
  "url": "https://checkout.stripe.com/c/pay/cs_test_a1b2c3..."
}
```

Redirect the buyer's browser to `url`. On success, Stripe redirects back to `success_url` and triggers `POST /v1/payment/webhook`.

---

### `POST /v1/payment/webhook` — Stripe webhook receiver

Internal endpoint called by Stripe. **Do not call directly.** Verifies signature and triggers report generation + email delivery via background task.

**Auth:** Stripe signature (`Stripe-Signature` header)
**Status code:** `200` (acked), `400` (bad signature)

---

### `GET /v1/payment/checkout-session` — Retrieve checkout session

**Auth:** None
**Status code:** `200`, `400`, `503`

**Query params:** `session_id` (Stripe `cs_*` ID)

**Response:** Full Stripe Checkout Session object (for status display on `success.html`).

---

### `POST /v1/keys/register` — Create a new API key

**Auth:** None (free tier is self-serve; pro/enterprise require admin)
**Status code:** `201` (created), `400` (bad email)

**Request body:**

```json
{
  "email": "developer@example.com",
  "name": "Acme Mobile App",
  "tier": "free"
}
```

**Response:**

```json
{
  "success": true,
  "api_key": "hd_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "key_prefix": "hd_a1b2c3d",
  "tier": "free",
  "rate_limit": 100
}
```

⚠️ **The `api_key` is returned ONCE.** Store it securely. The `key_prefix` is safe to display in your UI for identification.

---

### `GET /v1/keys/status` — Inspect an API key

**Auth:** `X-API-Key: <your-key>` header
**Status code:** `200`, `401`, `503`

**Response:**

```json
{
  "success": true,
  "tier": "free",
  "rate_limit": 100,
  "name": "Acme Mobile App",
  "created_at": "2026-06-01T12:34:56Z",
  "usage_count": 4231
}
```

---

### `DELETE /v1/keys/revoke` — Revoke an API key

**Auth:** `X-API-Key: <your-key>` header
**Status code:** `200`, `401`

**Response:**

```json
{ "success": true, "message": "Key revoked" }
```

---

## Health & metadata

| Endpoint | Purpose |
|----------|---------|
| `GET /ping` | Liveness probe — returns `{"ping": "pong"}` |
| `GET /health` | DB + Redis health check |
| `GET /` | Service info (name, version, build sha) |
| `GET /docs` | Interactive Swagger UI |
| `GET /redoc` | ReDoc-rendered OpenAPI spec |
| `GET /openapi.json` | Machine-readable OpenAPI 3.0 spec |

---

## Error codes (v1 standard)

| HTTP | `success` | When |
|------|-----------|------|
| 200 | `true` | Normal response |
| 201 | `true` | Resource created (key register) |
| 400 | `false` | Validation failure (bad date, missing field) |
| 401 | `false` | Missing/invalid API key |
| 429 | `false` | Rate limit exceeded (check `Retry-After` header) |
| 502 | `false` | Downstream service failure (compute engine, geocoder) |
| 503 | `false` | Service not configured (e.g. Stripe keys missing) |

When `success: false`, the `error` field contains a human-readable message safe to show to end users.

---

## End-to-end flow: Free chart → Paid report

```python
import requests

API = "https://api.humandesignengine.com"
KEY = "hd_YOUR_KEY_HERE"
H = {"X-API-Key": KEY, "Content-Type": "application/json"}

birth = {
    "name": "Jane Doe",
    "year": 1990, "month": 6, "day": 15,
    "hour": 14, "minute": 30,
    "lat": 21.3099, "lon": -157.8581,
    "timezone": "Pacific/Honolulu",
}

# 1. Free chart (no API key)
free = requests.post(f"{API}/v1/natal/noauth", json=birth).json()
print("Type:", free["data"]["type"])

# 2. Show bodygraph (no API key)
bg = requests.post(f"{API}/v1/bodygraph/noauth", json=birth).json()
render_bodygraph_svg(bg["data"])

# 3. User clicks "Buy full report" → create checkout session
checkout = requests.post(f"{API}/v1/payment/create-checkout", json={
    **birth, "email": "jane@example.com", "report_type": "full",
}).json()
redirect_to(checkout["url"])

# 4. After Stripe redirects back, webhook fires server-side → email delivery
#    (handled automatically by the platform)
```

---

## Embedding the chart calculator on your site

The fastest path to a working "free chart" widget:

```html
<script src="https://humandesignengine.com/widget.js"></script>
<div id="hd-chart-calc"></div>
<script>
  HDChartCalc.init({
    containerId: "hd-chart-calc",
    apiBase: "https://api.humandesignengine.com",
    onResult: (chart) => console.log(chart),
    paywallMessage: "Unlock your full report for $9.99",
  });
</script>
```

See `docs/widget-demo.html` for a working example.

---

## Versioning & changelog

- **v1** (current) — Initial stable release. All `/v1/*` paths.
- Breaking changes will be released under `/v2/*` with a 6-month deprecation window for `/v1`.

See `CHANGELOG.md` for per-version notes.

---

## Support

- **Email:** api@humandesignengine.com
- **Docs:** https://humandesignengine.com/docs
- **OpenAPI spec:** https://api.humandesignengine.com/openapi.json
- **Status page:** https://status.humandesignengine.com
