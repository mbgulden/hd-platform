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

## 2026-07-18 run summary

_To be filled by the fresh cron run after the script is committed-before-long-verification per the Ned autonomous skeleton._
