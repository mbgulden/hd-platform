# HDE Phase 1 + Phase 2 Staging Funnel Fix — 2026-07-15

Canonical customer workflow starts at `https://staging.humandesignengine.com/deconditioning/`.

## Fixed

- Staging deconditioning checkout now uses the staging origin for `success_url` and `cancel_url`.
- Staging intentionally omits live Stripe Price IDs so the staging API can create Stripe test checkout sessions from `price_data`.
- Non-staging hosts keep live Price ID behavior.
- Deconditioning flow test covers staging checkout session creation and paid-user success page Telegram handoff.
- PWP link check skips backend API routes and academy links now point at `/api/v1/academy`.

## Verification

- `npm run build` — pass.
- `npm run pwp:verify` — pass.
- `PWP_STAGING_URL=https://staging.humandesignengine.com npm run qa:flows -- --reporter=list` — 10 passed.
- Browser smoke from staging `/deconditioning/` reached `https://checkout.stripe.com/`.
- Bot PDF render proof produced `/tmp/hde-pdf-proof/michael_report_page1_phase12.png` from a 3-page generated PDF.

## Gate before broad paid traffic

Controlled staging traffic is green. Before broad paid production traffic, complete one real Stripe test-mode payment completion through webhook → user/invitation creation → success page → Telegram bot conversation/PDF delivery.
