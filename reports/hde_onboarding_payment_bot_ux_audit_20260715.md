# HDE Onboarding, Payment, Bot Routing, and UX/UI Readiness Audit — 2026-07-15

**Status:** 🟡 **YELLOW**
**Branch:** `ned/hde-onboarding-payment-ux-audit-2026-07-15`
**Scope:** public website → payment → success page → Telegram onboarding → guest container → conversation/PDF delivery → PWP + PDF visual QA.

## Executive read

Bot runtime is **green**. Public onboarding/payment readiness is **not** green yet.

The dangerous part is not the Telegram bot anymore. The dangerous part is the public funnel in front of it:

- Several live website routes return homepage content instead of their intended product/legal pages.
- Public root-domain `/api/*` paths return static homepage HTML, not JSON/API responses.
- `api.humandesignengine.com` and `reports.humandesignengine.com` are behind Cloudflare Access, which blocks public checkout/API use unless that is intentional.
- `hde-payment.service` is active, but a local checkout smoke hit Stripe `401` with an invalid placeholder key and returned an empty reply instead of a controlled JSON error.
- PWP visual QA harness exists, but browser execution is currently blocked because Playwright Chromium is missing in Ned's profile cache.
- Bot-generated PDFs are valid 3-page `wkhtmltopdf` PDFs, but `pdftotext` extracts almost no usable text, so PDF visual/accessibility/brand QA needs a real pass before broad polish claims.

Usual launch story: backend finally behaves, frontend quietly walks into traffic. Charming.

## Current evidence

### Bot runtime / routing

| Check | Result |
|---|---|
| `hde_router.service` | `active` |
| `hde_api_staging.service` | `active` |
| `guest-hermes-23` | `healthy` |
| Router metrics | `ok` |
| Redis chat/media/wake pending | `0 / 0 / 0` |
| Guest canary | `pass` |
| Live Telegram media proof | `pass`, 2 successful document sends |
| Controlled traffic report | [`hde_controlled_public_bot_traffic_20260715.md`](hde_controlled_public_bot_traffic_20260715.md) |

### Live website route smoke

| URL | Result | Concern |
|---|---|---|
| `https://humandesignengine.com/` | `200`, homepage title correct | OK |
| `https://humandesignengine.com/deconditioning/` | `200`, homepage title/content | wrong route content |
| `https://humandesignengine.com/privacy/` | `200`, homepage title/content | wrong route content |
| `https://humandesignengine.com/terms/` | `200`, homepage title/content | wrong route content |
| `https://humandesignengine.com/academy/` | `200`, homepage title/content | wrong route content |
| `https://humandesignengine.com/success/` | `200`, `Sanctuary Awaits — Human Design Engine`, contains Open Telegram | OK-ish, needs paid-user flow proof |

### Public API/payment routing smoke

| Check | Result | Concern |
|---|---|---|
| `http://127.0.0.1:8002/api/ping` | `200`, `hde-payment-server` | local payment server alive |
| Local `POST /create-checkout` | empty reply | Stripe returned `401` invalid placeholder key; server did not return controlled JSON error |
| `https://humandesignengine.com/api/ping` | `200` homepage HTML | root-domain API paths fall through to static site |
| `https://humandesignengine.com/api/checkout/create-session` | `200` homepage HTML | frontend/API route mismatch |
| `https://api.humandesignengine.com/*` | Cloudflare Access sign-in HTML | blocks public checkout/API unless intended |
| `https://reports.humandesignengine.com/` | Cloudflare Access sign-in HTML | not public report endpoint |

### PWP visual QA / build

| Command | Result |
|---|---|
| `npm run build` in `/home/ubuntu/work/hd-platform` | ✅ passed; 10 pages built, route-complete generated redirects |
| `npm run pwp:verify` | 🔴 blocked/failing: Playwright Chromium executable missing |
| `PWP_STAGING_URL=https://humandesignengine.com npm run qa:flows -- --reporter=list` | 🔴 browser tests blocked by missing Chromium; staging checkout API test also returned non-OK |

Required next setup:

```bash
cd /home/ubuntu/work/hd-platform
npx playwright install chromium
npm run pwp:verify
PWP_STAGING_URL=<correct public/staging app base> npm run qa:flows -- --reporter=list
```

### Bot PDF generation visual readiness

Sample live-proof PDFs:

- `/home/ubuntu/users/guest_23/charts/personal/becca_gulden/report_Becca_Gulden_20260714_143151.pdf`
- `/home/ubuntu/users/guest_23/charts/personal/michael_gulden/report_Michael_Gulden_20260715_040103.pdf`

Evidence:

| Check | Result |
|---|---|
| PDF creator | `wkhtmltopdf 0.12.6` |
| Pages | `3` |
| Page size | letter, `612 x 792 pts` |
| Encrypted | no |
| Text extraction | almost empty (`pdftotext` returned symbol/control output) |
| PNG render | `/tmp/hde-pdf-proof/michael_report_page1.png`, `1275 x 1650` |

Implication: PDFs are being generated and delivered, but they still need a dedicated visual/brand/accessibility proof pass. If the PDF is image-heavy, it may look fine and still be inaccessible/search-unfriendly. Both can be true. Annoying, but normal.

## Primary risks

1. **Public route mismatch** — users may click product/legal/academy links and see the homepage.
2. **Checkout not robust** — invalid Stripe key currently produces server exception/empty reply instead of controlled UX.
3. **API access ambiguity** — public root API routes fall through to static site, while API subdomain is Access-protected.
4. **Post-payment handoff not fully proven from website** — bot is proven, but website payment → success → Telegram invite needs an end-to-end proof.
5. **PWP not runnable yet in current environment** — visual QA exists but lacks browser install.
6. **PDF brand/accessibility unproven** — generated PDFs exist and deliver, but visual consistency and accessible text are not yet verified.

## Phased execution plan

### Phase 0 — Freeze and map the funnel

**Goal:** define the canonical public journey and avoid broad traffic through broken routes.

Tasks:

- Define canonical URLs:
  - landing
  - product/deconditioning
  - checkout/API base
  - success page
  - Telegram invite/open link
  - bot `/start` flow
- Decide whether `api.humandesignengine.com` is public, Access-protected, or split public/private.
- Keep current rollout at controlled/internal traffic until payment route is fixed.

**Exit gate:** one approved route map; no public CTAs pointing at broken/misrouted checkout routes.

### Phase 1 — Website and route correctness

**Goal:** make `humandesignengine.com` route users to the intended pages consistently.

Tasks:

- Fix static deployment/Cloudflare/Nginx route behavior for:
  - `/deconditioning/`
  - `/privacy/`
  - `/terms/`
  - `/academy/`
- Confirm route-complete output matches the live Cloudflare deployment.
- Add route smoke checks to the launch checklist/watchdog.

**Exit gate:** `curl` and Playwright confirm every public route returns expected title/required text, not homepage fallback.

### Phase 2 — Payment and post-payment onboarding hardening

**Goal:** successful payments create exactly one usable Telegram next step; failed payments fail cleanly.

Tasks:

- Fix Stripe environment/key deployment, or intentionally switch to Stripe Payment Links/test mode for validation.
- Handle Stripe `4xx/5xx` errors as JSON responses; no empty replies.
- Align frontend checkout endpoint with the actual public API route.
- Verify webhook behavior creates/updates:
  - user
  - premium/subscription status
  - invitation token
  - success page lookup
  - Telegram link
- Run no-charge/test-mode checkout session and webhook simulation.

**Exit gate:** PWP staging checkout creates Stripe URL, webhook smoke creates invitation, success page shows one Open Telegram CTA.

### Phase 3 — Bot container and conversation routing robustness

**Goal:** paid/onboarded users land in the right container and right conversation rail.

Tasks:

- Verify Telegram identity/token sources across systemd/env/router without printing tokens.
- Verify `/start` cases:
  - invalid token
  - used token
  - inactive subscription
  - active subscription
  - duplicate Telegram user
- Verify orchestrator provisioning idempotency and duplicate `BotInstance` handling.
- Verify guest container config:
  - MiniMax provider/config intact
  - guide-neutral Soul mounted
  - skills mounted
  - workspace paths mounted
  - PDF/media paths returned as plural where needed
- Keep comparison/PDF live watcher in the cohort-monitoring checklist.

**Exit gate:** server-side canary + one real Telegram onboarding canary pass with queues drained and no duplicate container/user confusion.

### Phase 4 — UX/UI and brand visual readiness

**Goal:** prove the website, checkout, success page, Telegram handoff, and generated PDFs look like one coherent Human Design Engine product.

Tasks:

- Install/fix Playwright Chromium in Ned/PWP environment:

```bash
cd /home/ubuntu/work/hd-platform
npx playwright install chromium
```

- Run deterministic PWP gates:

```bash
npm run build
npm run qa:update-screenshots
npm run pwp:verify
```

- Run staging flow proof with the corrected public/staging base:

```bash
PWP_STAGING_URL=<correct-base-url> npm run qa:flows -- --reporter=list
```

- Extend PWP routes for the actual funnel:
  - `/`
  - `/deconditioning/`
  - `/checkout/pay/`
  - `/success/`
  - `/privacy/`
  - `/terms/`
  - `/academy/`
- Add screenshot review criteria:
  - navy/gold HDE palette
  - premium/Sanctuary feel
  - no generic SaaS sludge
  - mobile CTA clarity
  - payment trust cues
  - legal links visible
  - one next step after payment
- Add bot PDF visual baselines:

```bash
pdftoppm -png -f 1 -singlefile <report.pdf> /tmp/hde-pdf-proof/<name>_page1
```

- Review PDF pages for:
  - HDE palette consistency
  - typography
  - readable chart/bodygraph scale
  - no clipped text
  - no placeholder assets
  - consistent product naming
  - accessible text layer or explicit remediation plan

**Exit gate:** PWP visual/a11y/flow checks pass or have approved diffs; PDF visual baselines accepted; brand inconsistencies fixed or tracked.

### Phase 5 — Controlled rollout and monitoring

**Goal:** expand from internal proof to 3–5 external users without losing rollback ability.

Tasks:

- Invite Phase 0 internal testers.
- Monitor:
  - router metrics
  - Redis pending queues
  - media sends
  - payment/webhook logs
  - success page handoff
  - backup freshness
  - token/model spend
- Invite 3–5 external users only after internal pass.
- Record cohort report and issues.

**Exit gate:** no sustained Redis backlog, failed Telegram sends, unhealthy containers, restart loops, onboarding errors, payment failures, or spend spikes.

## Recommended ownership split

| Lane | Work |
|---|---|
| Ned | runtime health, bot routing, watchdogs, deployment evidence, reports |
| Fred/frontend lane | website route/deploy mismatch, PWP test harness, UX/UI implementation |
| Payment/API lane | Stripe env, checkout endpoint, webhook/invitation path |
| Design/brand lane | PDF and website brand visual acceptance |

## Immediate next action

Fix **Phase 1 + Phase 2** before sending paid public traffic:

1. Correct public route deployment so `/deconditioning/`, `/privacy/`, `/terms/`, and `/academy/` do not serve homepage content.
2. Fix payment checkout configuration/error handling so checkout returns either a Stripe URL or a controlled JSON error.
3. Then rerun PWP visual/flow checks with Chromium installed.
