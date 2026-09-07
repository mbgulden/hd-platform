# HDE Phase 1 + Phase 2 Staging Funnel Fix — 2026-07-15

**Status:** 🟢 GREEN for controlled staging traffic
**Branch:** `ned/hde-phase1-phase2-staging-funnel-2026-07-15`
**Canonical workflow source:** `https://staging.humandesignengine.com/deconditioning/`

## Scope

Michael asked to fix Phase 1 and Phase 2 first:

1. **Phase 1 — live route correctness** for the staging deconditioning/public pages.
2. **Phase 2 — checkout/payment handoff** from the staging deconditioning route.
3. Rerun PWP and bot PDF visual QA before broad paid traffic.

## Changes made

### Phase 1 — route correctness

- Rebuilt the HDE frontend static site.
- Synced the fresh build output into the staging checkout.
- Verified these staging public routes return distinct intended pages instead of homepage fallback:
  - `/deconditioning/`
  - `/checkout/pay/`
  - `/success/`
  - `/privacy/`
  - `/terms/`
  - `/academy/`
- Fixed PWP link-check handling for API routes so static link QA does not treat backend JSON endpoints as missing static pages.
- Updated academy JSON API links to the `/api/v1/academy` route shape.

### Phase 2 — checkout/payment handoff

- Updated the deconditioning checkout client so staging intentionally omits live Stripe Price IDs and lets the staging API create Stripe test checkout sessions from `price_data`.
- Preserved live Price ID behavior for non-staging hosts.
- Wired the staging API to expose the Stripe checkout/session routes under `/api/checkout/*`.
- Restarted `hde_api_staging.service` after deploying the API route.
- Verified a real browser flow from `https://staging.humandesignengine.com/deconditioning/` redirects to `https://checkout.stripe.com/`.

## Verification evidence

| Check | Result |
|---|---:|
| `npm run build` | ✅ pass |
| `npm run pwp:verify` | ✅ pass |
| PWP visual screenshots | ✅ 36 passed |
| PWP axe accessibility | ✅ 12 passed |
| PWP local flow tests | ✅ 6 passed, 4 staging-only skipped locally |
| PWP Lighthouse | ✅ pass, reports written under `okf/output/pwp-visual-qa/lighthouse` |
| PWP link check | ✅ 124 checked, 0 broken |
| Staging process flow with `PWP_STAGING_URL=https://staging.humandesignengine.com` | ✅ 10 passed |
| API Python compile | ✅ pass for `api/main.py`, `api/routes/stripe_webhook.py`, route modules |
| Staging API `/ping` | ✅ `200`, status ok |
| Staging API `/api/checkout/create-session` method exposure | ✅ `405` on GET, proving route is mounted and POST-only |
| Staging checkout POST | ✅ `200`, Stripe checkout URL returned |
| Browser checkout redirect from deconditioning page | ✅ reached `https://checkout.stripe.com/` |
| Router metrics | ✅ status ok; Redis chat/media/wake pending all `0` |
| Bot PDF render proof | ✅ PDF page rendered to PNG, 1275×1650, 3-page PDF, 162519-byte first-page PNG |

## Route smoke results

| Route | HTTP | Page title / marker |
|---|---:|---|
| `/deconditioning/` | 200 | `Somatic Sanctuary & Deconditioning Container` |
| `/checkout/pay/` | 200 | `Secure Checkout` |
| `/success/` | 200 | `Registration Successful` |
| `/privacy/` | 200 | `Privacy Policy` |
| `/terms/` | 200 | `Terms of Service` |
| `/academy/` | 200 | `HD Academy — Human Design Education` |

## Important caveat

This is green for controlled staging traffic. It does **not** mean broad paid production traffic should begin automatically.

Before broad paid traffic:

1. Run one real Stripe test-mode completion through checkout success, not only session creation.
2. Confirm webhook-driven user/invitation creation from Stripe event to Telegram deep link.
3. Have a real tester open Telegram from the success page and confirm bot conversation plus PDF delivery.
4. Keep router metrics/queue watchdog visible during the first external cohort.

## Artifacts

- PWP evidence: `okf/output/pwp-visual-qa/`
- PDF render proof: `/tmp/hde-pdf-proof/michael_report_page1_phase12.png`
- Staging metrics snapshot: `/tmp/hde_phase12_metrics.json`
