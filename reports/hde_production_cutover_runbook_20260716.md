# HDE production cutover runbook (20260716)

## Status

This is a HOLD runbook. Do not execute live cutover until the blockers in `hde_staging_to_production_cutover_readiness_20260716.md` are closed.

## Preflight checks

1. Confirm Michael approval for production cutover window.
2. Confirm no live Stripe charge will be made until explicitly approved.
3. Confirm `CLOUDFLARE_API_TOKEN` or Cloudflare owner access is available.
4. Confirm correct branch/owner for `reports/server.py` promotion.
5. Confirm latest source build has `/deconditioning/`, `/privacy/`, `/terms/`, `/success/`.
6. Confirm staging human Telegram `/start` proof is complete.
7. Confirm coach consent fail-closed checks pass.
8. Confirm secrets scan passes for changed/deployed artifacts.

## Backup/snapshot steps

- Save current production Cloudflare Pages/deploy identifier.
- Save current Cloudflare Access policy export or screenshots.
- Save current systemd service mapping for HDE services.
- Preserve current `.env` values privately; do not paste them into reports.
- Preserve current Stripe webhook endpoint config privately.

## Production route deployment

1. Build source: `npm run build`.
2. Deploy `dist/` to the production serving target.
3. Smoke with curl and browser:
   - `https://humandesignengine.com/deconditioning/`
   - `https://humandesignengine.com/privacy/`
   - `https://humandesignengine.com/terms/`
4. Verify title/body markers match intended routes, not homepage fallback.

## Cloudflare/API Access decision

Choose one before cutover:

### Option A -- public-safe API exceptions

- Expose only checkout/session/webhook/public health endpoints.
- Keep admin, coach, private workspace, and customer data paths behind Access.
- Verify unauthenticated checkout works.
- Verify private paths are still gated.

### Option B -- API remains gated

- Prove browser checkout/onboarding uses non-gated staging/production paths and does not require public direct API health.
- Document why `/health` being Access-gated is acceptable.

## Stripe live mode switch

Requires Michael approval before live charge.

1. Confirm live Price IDs are configured.
2. Confirm live mode uses Price IDs only, not test `price_data` fallback.
3. Confirm live webhook endpoint is registered in Stripe.
4. Confirm webhook secret matches service env.
5. Confirm success URL is `https://humandesignengine.com/success/?session_id={CHECKOUT_SESSION_ID}` or equivalent accepted route.
6. Run a dry config proof without printing secrets.
7. Only after approval, run one controlled live charge.

## Service restart order

1. API service.
2. Reports service.
3. Payment service.
4. Router service.
5. Guest container health check.
6. Router queue metrics check.

## Post-cutover smoke tests

- Production route title/body check.
- Production checkout start check.
- Stripe webhook reachability check.
- Success page Telegram CTA check.
- Human Telegram `/start` proof.
- Invitation used/user linked DB proof.
- Chart/report media delivery proof.
- Coach consent fail-closed proof.

## Rollback criteria

Rollback if:

- production route content falls back to homepage,
- checkout cannot create session,
- Stripe webhook fails,
- success page cannot find paid session/invitation,
- Telegram CTA opens wrong bot or `/start` fails,
- report media fails,
- private/coach/admin path becomes public,
- secrets appear in logs/artifacts.

## Rollback steps

1. Revert Cloudflare Pages/deploy target to previous known-good deployment.
2. Restore previous Access policy.
3. Revert any env changes.
4. Restart services in reverse order if local services changed.
5. Disable live traffic/ads/links until smoke returns green.
6. Document exact failure and artifact path.
