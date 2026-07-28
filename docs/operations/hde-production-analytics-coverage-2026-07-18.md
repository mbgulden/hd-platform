# HDE Production Analytics Coverage — 2026-07-18

Live verification target for [GRO-3997](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3997): crawl every production sitemap URL and confirm that analytics tags/events are present without duplicate snippets.

## Canonical command

```bash
HDE_PRODUCTION_URL=https://humandesignengine.com \
HDE_ANALYTICS_OUTPUT=/tmp/hde-live-analytics-coverage.json \
node scripts/live-analytics-coverage.mjs
```

The script fetches `https://humandesignengine.com/sitemap.xml`, crawls every `<loc>`, and checks:

- HTTP success for each sitemap URL.
- GA4 loader/config coverage for expected property `G-Q6TPL08VM7`.
- duplicate GA4 snippets (`gtag/js` or `gtag('config')` repeated on the same page).
- duplicate GTM container snippets.
- funnel event hooks on critical revenue routes:
  - `/buy-report/` → `begin_checkout`
  - `/checkout/pay/` → `add_payment_info`
  - `/success/` → `purchase`

## Evidence handling

The full crawl output is intentionally written to `/tmp/hde-live-analytics-coverage.json` so runtime proof does not pollute the repository. Commit only this script/doc pair unless a follow-up task deliberately updates production analytics implementation.

## Green criteria

`ok=true` from the script is required before the analytics coverage work can be called green. If the script exits nonzero, summarize the JSON counts and keep the Linear issue out of Done until the deployed production site is fixed and re-crawled.

## 2026-07-18 live production run summary

Command run from branch `ned/GRO-3997` at `2026-07-18T20:10:09Z`:

```bash
HDE_PRODUCTION_URL=https://humandesignengine.com \
HDE_ANALYTICS_OUTPUT=/tmp/hde-live-analytics-coverage.json \
node scripts/live-analytics-coverage.mjs
```

Result: **red / not green** (`ok=false`, exit `1`).

Counts:

| Check | Result |
|---|---:|
| Sitemap URLs crawled | 171 |
| Non-200 / fetch failures | 1 |
| Pages missing expected GA4 `G-Q6TPL08VM7` | 36 |
| Pages with duplicate GA4 snippet | 0 |
| Pages with duplicate GTM snippet | 0 |
| GTM containers detected | 0 |
| Funnel event routes checked | 3 |
| Funnel event routes missing expected event | 3 |

Primary failures:

- `/`, `/buy-report/`, `/checkout/pay/`, `/deconditioning/`, `/docs/`, `/free-human-design-reading-generator/`, generated Human Design index pages, and operational pages lack the expected GA4 loader/config on live production.
- `/buy-report/` has no `begin_checkout` event hook on live production.
- `/checkout/pay/` has no `add_payment_info` event hook on live production.
- `/success/` has no `purchase` event hook on live production.
- No GTM container is deployed on any crawled sitemap URL.
- `/affiliates.html` still fails the crawler fetch path, matching the known sitemap/redirect-loop issue.

Non-failures:

- The live crawl did **not** find duplicate GA4 snippets.
- The live crawl did **not** find duplicate GTM snippets.

Interpretation: production analytics coverage is verified and currently failing. Do not mark the analytics surface green until the site-wide analytics/event implementation is deployed to production and this script returns `ok=true` against the live site.
