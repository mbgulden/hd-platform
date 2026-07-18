# HDE GTM container verification — GRO-3990

Date: 2026-07-18
Issue: GRO-3990
Status: **partial / not green**
Owner: Ned

## Decision

Do **not** mark the GTM work green yet.

The repository and live site currently show GA4 `G-Q6TPL08VM7` on legacy/static surfaces, but no `GTM-...` container ID is present in the committed HD Engine repo or sampled production pages. Creating or verifying the Google Tag Manager account/container requires Google OAuth with Tag Manager scopes; API-key-only access is not sufficient.

## What this pass added

- `scripts/operations/verify_gtm_container.py` — read-only verifier for repo/live GTM and GA4 coverage.
- This operations note documenting the current partial state and the OAuth blocker.

## Current evidence

- Known GA4 Measurement ID: `G-Q6TPL08VM7`.
- Public GA4 loader endpoint returns HTTP 200 for `https://www.googletagmanager.com/gtag/js?id=G-Q6TPL08VM7`.
- No committed `GTM-...` container ID was found by the verifier in this pass.
- Sampled production pages do not expose a GTM container ID.
- Tag Manager Admin API account listing is not publicly available and requires OAuth bearer credentials.

## Credential search performed before declaring partial/blocker state

Required searches were completed before documenting this as OAuth-blocked:

- OKF integration docs under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`.
- Prior Hermes sessions for HDE Google/GTM/GA4 registration work.
- Relevant `.env*` files under `/home/ubuntu/work` and Hermes profile directories, with values redacted.

Findings:

- Existing public/API-key Google material does not provide Tag Manager account/container permissions.
- No reusable OAuth token with `tagmanager.*` scopes was found in the checked local sources.
- Related parent/child work already records the required human browser consent step in GRO-3986/GRO-3988.

## Required green path

After OAuth consent is available for `mbgulden@gmail.com`:

1. Exchange the OAuth code locally without printing tokens.
2. Verify granted scopes include:
   - `https://www.googleapis.com/auth/tagmanager.readonly`
   - `https://www.googleapis.com/auth/tagmanager.edit.containers`
   - `https://www.googleapis.com/auth/tagmanager.manage.accounts`
3. Query Tag Manager accounts and reuse an appropriate GrowthWeb/HDE account when present.
4. Create or verify a web container for `humandesignengine.com`.
5. Add a GA4 config tag for `G-Q6TPL08VM7`.
6. Add minimal conversion events for report checkout and report/free-reading funnel actions.
7. Publish the container.
8. Install/verify the `GTM-...` container site-wide or explicitly document any intentionally excluded surfaces.
9. Re-run `scripts/operations/verify_gtm_container.py --repo .` and a production tag proof.

## Verification command

```bash
python3 scripts/operations/verify_gtm_container.py --repo .
```

Expected current status is `partial` until a real GTM container ID and Tag Manager API proof exist.
