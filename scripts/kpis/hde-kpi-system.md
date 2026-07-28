# HDE KPI System — design (canonical)

> **Status:** Draft 1 — 2026-07-28 · owner: `agent:ned` · lane: `scripts/` (writes `scripts/kpis/*`).
>
> **Single source of definitions:** `scripts/kpis/kpi-collections.json`. This document mirrors the JSON for human readers; treat the JSON as authoritative.

## Goal

Track every conversion event and site-hygiene indicator across `humandesignengine.com`, including the Sanctuary and Stripe-card checkout paths, surface them in a Google Sheet + emailed reports + a PWP dashboard section, and capture Stripe purchases as the source of truth for revenue.

## Surfaces

| Surface | Purpose | Owner | Cadence |
|---|---|---|---|
| Google Sheet `HDE_KPI_SHEET_ID` | Real-time append, pivots, targets | ned | `cron` every 6h |
| Emailed HTML reports (daily / weekly / monthly) | Attention-free summary | ned | daily 06:30 PT, weekly Mon 07:00, monthly day-1 07:00 |
| `humandesignengine.com/pwp/kpi-dashboard.html` | PWP dashboard section, gated | ned | rendered daily |

All surfaces read from the same canonical KPI definitions in `scripts/kpis/kpi-collections.json`.

## KPI collections (overview)

1. **`funnel_top`** — free-reading engagement (`hde_chart_generated`, `hde_nervous_system_practice_*`).
2. **`funnel_sanctuary`** — Sanctuary deconditioning (`hde_daily_work_cta_clicked`, `hde_sanctuary_checkout_submitted`) → Stripe checkout → Sanctuary purchases.
3. **`funnel_buy_report`** — `natal / synastry / transit / bundle` purchases through `/buy-report/` → `/checkout/pay/` → `/success/`.
4. **`delivery_onboarding`** — success page → Telegram deep link → bot onboarding → PDF.
5. **`aggregates_growth`** — site-wide DAU/WAU/engaged sessions, weekly gross/net revenue, ARR proxy, churn.
6. **`site_hygiene`** — sitemap GA-coverage, duplicate-snippet rate, last successful `npm run build`.

Each metric declares a `source` (ga4 / stripe / telegram / internal / derived), the canonical event name or formula, and an optional `filter` (Stripe metadata, GA4 page filter).

## How the metrics are computed

### GA4 metrics

- Pulled via the [GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1) using the metrics/dimensions from `kpi-collections.json`.
- Property `G-Q6TPL08VM7` (HDE production). Service-account JSON at `HDE_GOOGLE_SERVICE_ACCOUNT_JSON`.
- All GA4 event names from the canonical script are listed under `globally_required.expected_dataLayer_event_set` so the email report surfaces coverage at glance.

### Stripe metrics

- Pulled via the Stripe SDK over the past 24h / 7d / 30d, scoped to `metadata.funnel` and `event` fields.
- Server-side webhook handler (`api/routes/stripe_webhook.py`) already emits `checkout.session.completed` and `customer.subscription.deleted`. The KPI runner treats Stripe as the source of truth for `*purchase_total` and `*revenue_usd`.
- Stripe sessions created server-side carry `metadata.funnel`; KPI metrics use those filters cleanly.

### Telegram / bot

- `deep_link_clicked_total`: deep-link `/start <token>` activations logged by `Humandesigncompanionbot`, surfaced via the Prismatic Engine's existing inter-agent dispatch.
- `deep_link_to_pdf_total`: `report.pdf.generated` event from the report-generation queue.

### Derived

- `practice_completion_rate = completed / started`, formatted as percent.
- `weekly_arr_usd = weekly_subscription_revenue * 52 / 12` only when `is_subscription == true` for that period.
- `buy_report_conversion_rate = purchases / buy_report_page_view`.

## Email reports

### Layout (HTML, plain-text fallback)

```text
[HDE KPI] Daily — 2026-07-28 06:30 PT

Yesterday's numbers, ranked by relative movement vs prior 7 days.

— Funnel (report purchase) —
buy_report_page_view           412   (▲ 6%)
checkout_cta_clicked            187   (▲ 11%)
checkout_session_created        142   (▲ 9%)
checkout_purchase_confirmed      91   (▲ 22%)
buy_report_revenue_usd      $7,360   (▲ 28%)

Conversion buy_report → purchase: 22.1% (▲ 3 pts)

— Sanctuary —
sanctuary_page_view             208   (▲ 1%)
hde_daily_work_cta_clicked       71   (▼ 4%)
hde_sanctuary_checkout_submitted 38   (▼ 2%)
sanctuary_purchase_total         11   (▲ 10%)
sanctuary_revenue_usd        $1,485   (▲ 12%)

— Free reading / daily work —
free_chart_generated_total      930   (▲ 14%)
practice_completed_total         312   (▲ 8%)
practice_completion_rate        33.5% (▲ 1 pt)

— Onboarding delivery —
success_page_view_total         117   (▲ 12%)
deep_link_clicked_total          96
deep_link_to_pdf_total           83

— Site hygiene —
sitemap_coverage_pct           99.4% (1 page fetch-failed, /affiliates.html)
build_status                   pass (2026-07-28 01:18 UTC)

[Open Google Sheet ↗](HDE_KPI_SHEET_URL)  •  [Open dashboard ↗](dashboard_url)
```

### Send & storage

- Transporter: `nodemailer` over SendGrid SMTP relay (`HDE_SENDGRID_API_KEY`).
- From: `bi@humandesignengine.com`. To: `mbgulden@gmail.com`.
- Subject prefix from `kpi-collections.json`.
- Each run also writes the rendered HTML + JSON payload to `/home/ubuntu/.hermes/profiles/ned/reports/kpi/<kind>/<window>.html` for archive.

### Daily / weekly / monthly cadence

| Cadence | Time (PT) | Window | Skip conditions |
|---|---|---|---|
| Daily | 06:30 | last 24h UTC | `skip_if_no_new_events` toggled off — emits even when zero |
| Weekly | Mon 07:00 | last 7d UTC | always emits |
| Monthly | 1st 07:00 | previous calendar month UTC | always emits |

## Google Sheet layout

```
HDE_KPI_SHEET_ID (env)
┌──────────┬───────────────────────────────────────────────────────────────────┐
│ Daily    │ columns: date, collection_id, metric_id, value, delta_pct         │
├──────────┼───────────────────────────────────────────────────────────────────┤
│ Weekly   │ columns: week_start, collection_id, metric_id, value, delta_pct   │
├──────────┼───────────────────────────────────────────────────────────────────┤
│ Monthly  │ columns: month_start, collection_id, metric_id, value, delta_pct   │
├──────────┼───────────────────────────────────────────────────────────────────┤
│ Targets  │ static sheet: metric, target_value, owner                         │
├──────────┼───────────────────────────────────────────────────────────────────┤
│ Raw      │ append-only event log: stripe_event_id, event_type, customer,     │
│          │  amount_usd, funnel, created_at                                    │
└──────────┴───────────────────────────────────────────────────────────────────┘
```

- Real-time appends for Stripe events (server webhook pushes a row to the `Raw` tab whenever a Stripe checkout completes).
- GA4 metrics back-fill every 6 hours via the `cron` job.

## PWP dashboard section

`humandesignengine.com/pwp/kpi-dashboard.html` is rendered by Cloudflare Pages once per day from `scripts/kpis/render-dashboard.mjs`. The page:

- Top section: KPI collection cards (6 sections, one per collection).
- Body: Bump charts for each KPI vs the prior 7 days, sourced from the Google Sheet via `=IMPORTDATA()` formulas (no live API calls).
- Bottom: targets sheet snapshot (current vs target).

The page is intentionally lightweight (no JS-heavy rendering) so it works on the family test device without crashing.

## Authoritative KPI definitions

The canonical definitions live at `scripts/kpis/kpi-collections.json`. Every script reads from there. The design is intentionally narrow: one definition file, multiple surfaces pointing at it.

See also:

- `scripts/kpis/build-report.mjs` — aggregates GA4 + Stripe + telegram metrics, emits HTML + JSON.
- `scripts/kpis/sync-sheet.mjs` — appends a day's worth of metrics to the Google Sheet.
- `scripts/kpis/render-dashboard.mjs` — renders the PWP dashboard page.
- `scripts/kpis/send-email.mjs` — emails the rendered HTML report via SendGrid.
- `scripts/kpis/cli.mjs` — single CLI that wires the four scripts: `node scripts/kpis/cli.mjs daily`.
- `scripts/kpis/stripe-webhook-to-sheet.mjs` — Stripe webhook proxy that appends to the `Raw` tab.
- `scripts/live-analytics-coverage.mjs` — inputs the site-hygiene KPIs.

## Linear mapping

| Collection | Owned by | Linked Linear issues |
|---|---|---|
| funnel_buy_report | ned | GRO-3992 (analytics parent), GRO-3994 (events), GRO-3997 (coverage), GRO-4009 (proof report) |
| funnel_sanctuary | ned | GRO-4010 (North Star) |
| funnel_top | ned | GRO-4011 (daily-work loop), GRO-4015 (family validate) |
| delivery_onboarding | ned | GRO-4008 (production smoke cron) |
| aggregates_growth | ned | GRO-4004 (security & reliability parent) |
| site_hygiene | ned | GRO-3997 (live analytics coverage) |

## Open questions for Michael

1. Should `/success/` accept Sanctuary session_ids or should a separate `/sanctuary/success/` page be wanted (so the funnel attribution stays clean)?
2. SendGrid API key — can you paste into `/home/ubuntu/.hermes/profiles/ned/.env` as `HDE_SENDGRID_API_KEY`?
3. Service-account JSON for Google Sheets — same path, as `HDE_GOOGLE_SERVICE_ACCOUNT_JSON`?
4. Telegram bot dispatch exposes `deep_link_clicked_total` via Prismatic Engine / TeamCity. Is that wired yet (Kai owns), or should we aggregate at week+lag?
5. The date range used for the Google Sheet's "Daily" tab — should it be PT or UTC?

These are recorded as comments on GRO-4010 / GRO-4004 and as questions in the email reports under a "questions" footer for the next 2 cycles.
