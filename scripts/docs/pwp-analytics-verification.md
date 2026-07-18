# PWP analytics verification

`npm run pwp:verify` now includes `node scripts/pwp-analytics-check.mjs` immediately after the Astro build.

The check fails the proof when:

- any route listed in `.pwp/routes.json` renders without a GA4/GTM loader, `window.dataLayer`, and a `gtag('config', 'G-*')`/GTM marker; or
- revenue funnel surfaces render without conversion event hooks:
  - `/buy-report/` must emit `begin_checkout` before the Stripe handoff;
  - `/checkout/pay/` must emit `add_payment_info` or `begin_checkout` before redirect; and
  - `/success/` must emit `purchase` or `generate_lead` after report delivery/onboarding lookup.

Evidence is written to `okf/output/pwp-visual-qa/analytics.json` alongside the existing PWP proof summary. Runtime artifacts under `okf/output/` remain uncommitted.
