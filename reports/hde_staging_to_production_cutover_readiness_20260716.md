# HDE staging -> production cutover readiness (20260716)

## Recommendation

# [HOLD] HOLD -- do not cut over

Production is not approval-ready. Staging has strong local/source and PWP evidence, but production routing and API Access remain hard blockers.

## Evidence summary

| Gate | Result | Evidence |
|---|---:|---|
| Source frontend build | PASS | `npm run build` built 10 Astro pages including `/deconditioning/`, `/privacy/`, `/terms/`, `/success/`. |
| PWP visual/a11y/flow/lighthouse/link proof | PASS | `npm run pwp:verify`: visual 36 passed; a11y 12 passed; local flows 6 passed/4 staging-gated skipped; Lighthouse passed; links 124 checked/0 broken. |
| Staging checkout/browser process flow | PASS | `PWP_STAGING_URL=https://staging.humandesignengine.com npm run qa:flows -- --reporter=list`: 10 passed. |
| Focused route/API ad-hoc verifier | PASS | `/tmp/hermes-verify-hde-cutover-route-api-repeat-*.py`, removed after run. Proof: `/tmp/hde-cutover-route-api-proof-repeat/route_api_verification.json`. |
| Production route content | FAIL | `/deconditioning/`, `/privacy/`, and `/terms/` return HTTP 200 with homepage title, not intended page content. |
| Public API / Cloudflare Access | FAIL | `https://api.humandesignengine.com/health` redirects to Cloudflare Access sign-in. |
| Deploy ability | BLOCKED | `CLOUDFLARE_API_TOKEN` not set; Wrangler cannot list/deploy projects non-interactively. |
| Human Telegram paid onboarding proof | PENDING | Real tester has not completed success CTA -> Telegram `/start` -> invitation used/user linked/media proof in this run. |

## Service -> checkout mapping

| Service | Status | WorkingDirectory | ExecStart path | Assessment |
|---|---:|---|---|---|
| `hde_api_staging.service` | active | `/home/ubuntu/work/hd-platform-staging` | `/home/ubuntu/work/hd-platform/.venv/bin/python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8010` | staging checkout/api code path |
| `hde_router.service` | active | `/home/ubuntu/work/hd-platform-staging` | `/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_tenant_router.py` | staging router code path |
| `hde-reports.service` | active | `/home/ubuntu/work/hd-platform` | `/usr/bin/python3 /home/ubuntu/work/hd-platform/reports/server.py` | source/live checkout, not staging checkout |
| `hde-payment.service` | active | `/home/ubuntu/work/hd-platform` | `/usr/bin/python3 /home/ubuntu/work/hd-platform/payment/server.py` | source/live checkout, not staging checkout |


## Production route fallback evidence

- `https://humandesignengine.com/deconditioning/` -> HTTP 200, title `Human Design Engine -- The Engine Behind Every Chart`, homepage fallback.
- `https://humandesignengine.com/privacy/` -> HTTP 200, title `Human Design Engine -- The Engine Behind Every Chart`, homepage fallback.
- `https://humandesignengine.com/terms/` -> HTTP 200, title `Human Design Engine -- The Engine Behind Every Chart`, homepage fallback.

HTTP 200 is not proof here. The body/title content is wrong.

## Cloudflare Access behavior

`https://api.humandesignengine.com/health` currently redirects to Cloudflare Access sign-in. This must be treated as unresolved until one of these is implemented and verified:

- Option A: expose only required public-safe API paths such as checkout/session/webhook/public health while keeping private/admin/coach paths gated.
- Option B: keep API gated and prove unauthenticated browser checkout/onboarding never needs Access-gated production API routes.

No admin, coach, private workspace, or customer data paths should be opened publicly.

## Stripe readiness without live charge

- Test/staging checkout flow passed via PWP staging process flow.
- Code path supports test-mode `price_data` and live-mode configured Price IDs.
- Live charge was not attempted and must not be attempted without Michael's explicit approval.
- Live mode still needs a final environment/webhook/Price ID proof after Cloudflare routing is resolved.

## Report-server preservation

Critical local source commit is still the preservation concern:

`420979e -- [Ned] Serve augmented HDE natal reports to bot (#NO-ISSUE)`

It is live locally, but must be promoted/cherry-picked by the correct lane owner so augmented `chart_overrides`, full natal field standard, and planet/gate activation map survive clean redeploy.

## Blockers

### CRITICAL: production-route-fallback

- Evidence: https://humandesignengine.com/deconditioning/, /privacy/, and /terms return HTTP 200 with homepage title instead of intended route content.
- Impact: Production cutover would expose wrong content while health checks appear green.
- Next fix: Deploy freshly built dist/ to the production host/Cloudflare Pages target and re-smoke route title/body content.

### CRITICAL: cloudflare-access-api

- Evidence: https://api.humandesignengine.com/health redirects to Cloudflare Access sign-in.
- Impact: Public checkout/API browser paths may fail unless intentionally routed through staging host or a public-safe API path.
- Next fix: Choose Option A public-safe API exceptions or Option B keep API gated and prove browser checkout does not need it.

### CRITICAL: cloudflare-deploy-token-missing

- Evidence: wrangler reported CLOUDFLARE_API_TOKEN is required and not set.
- Impact: Ned cannot deploy production route fix or inspect Pages projects non-interactively.
- Next fix: Provide Cloudflare token/owner or route deploy to Cloudflare owner.

### CRITICAL: human-telegram-proof-pending

- Evidence: Staging process flow is server/browser verified, but no real tester has tapped Telegram CTA and sent /start in this run.
- Impact: Cannot prove paid onboarding works end-to-end for a human.
- Next fix: Run controlled Stripe test purchase, tap success-page Telegram CTA, send /start, verify invitation used/user linked/media delivered.

### WARNING: report-server-lane-preservation

- Evidence: Local source report-server commit 420979e is live but was blocked from push by lane guard.
- Impact: A clean redeploy may revert augmented report/chart_overrides behavior.
- Next fix: Correct lane owner must promote/cherry-pick 420979e or equivalent.

### WARNING: service-split

- Evidence: API/router run from hd-platform-staging; reports/payment run from hd-platform.
- Impact: Staging behavior can drift from source/live services.
- Next fix: Create dedicated staging reports/payment services or intentionally promote source path as the staging runtime.


## Final answer

# [HOLD] HOLD -- do not cut over

Production cutover is blocked by route fallback, unresolved Cloudflare Access/API behavior, missing Cloudflare deploy capability, and pending human Telegram paid-onboarding proof.
