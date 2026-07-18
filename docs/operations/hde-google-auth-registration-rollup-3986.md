# HDE Google authentication and registration rollup — GRO-3986

Date: 2026-07-18
Issue: GRO-3986
Status: **partial / not green**
Owner: Ned

## Decision

Do **not** mark the HDE Google authentication category green yet.

The parent epic is correctly in Ned's observability/revenue lane, but it depends on Google OAuth scopes that are not available to autonomous agents without a human browser consent step. The dependency work is already split and partially executed through child issues; this document records the current proof so the epic can stop pretending the category is green.

## Child issue state

| Child | Purpose | Current state | Evidence |
|---|---|---:|---|
| GRO-3987 | Use Kai-authenticated AGY account to establish Google registration path | Done | Kai AGY auth proven for `mbgulden@gmail.com`; generated scoped consent URL without printing tokens. |
| GRO-3988 | Upgrade/obtain OAuth scopes for Analytics Admin, Tag Manager, Search Console | In Progress | Active blocker: no reusable token with `analytics.*`, `tagmanager.*`, `webmasters`, and `siteverification` scopes found after OKF/session/env search. |
| GRO-3989 | Register/verify GA4 property and stream | In Review | GA4 Measurement ID `G-Q6TPL08VM7` recorded; public gtag endpoint HTTP 200; live snippet is partial; Analytics Admin ownership proof blocked by OAuth. |
| GRO-3990 | Create/verify GTM container | Todo | Must wait for Tag Manager OAuth scopes. |
| GRO-3991 | Register Search Console property and submit sitemap | In Review + needs human review | `robots.txt` and `sitemap.xml` are live; sitemap parsed with 171 URLs; Search Console API rejects API-key-only access; OAuth required. |

## Live/repo proof collected so far

- `https://humandesignengine.com/robots.txt` returns HTTP 200 and advertises the sitemap.
- `https://humandesignengine.com/sitemap.xml` returns HTTP 200 and contains 171 URLs.
- `https://www.googletagmanager.com/gtag/js?id=G-Q6TPL08VM7` returns HTTP 200.
- GA4 Measurement ID `G-Q6TPL08VM7` is present in the committed static surface, but not yet uniformly installed across every high-value page.
- API-key-only calls to Analytics Admin / Search Console are expected to fail with `401 UNAUTHENTICATED`; those APIs require OAuth, not API keys.

## Credential search performed before declaring blocker

Required searches were performed before calling this blocked:

- OKF integration docs under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`
- Prior Hermes sessions for GRO-3986 through GRO-3991 and `humandesignengine.com` Google registration work
- Relevant `.env` files under `/home/ubuntu/work/*` and Hermes profiles

Findings:

- Linear API key is available and working.
- Google API key entries exist in profile/env files, but API keys cannot satisfy Analytics Admin, Tag Manager, Search Console, or Site Verification proof.
- Existing Google OAuth material found in reusable workspaces does not expose the required scopes for this registration category.
- No token is committed here. No token value should be added to git.

## Human action required

Open the generated Google OAuth consent URL while signed in as `mbgulden@gmail.com`, approve the scopes, then return the full failed localhost redirect URL/code to Ned. The exchange can be done without printing tokens.

Required scopes:

- `https://www.googleapis.com/auth/analytics.edit`
- `https://www.googleapis.com/auth/analytics.readonly`
- `https://www.googleapis.com/auth/tagmanager.edit.containers`
- `https://www.googleapis.com/auth/tagmanager.manage.accounts`
- `https://www.googleapis.com/auth/tagmanager.readonly`
- `https://www.googleapis.com/auth/webmasters`
- `https://www.googleapis.com/auth/siteverification`

## Next execution order after consent

1. Exchange OAuth code without printing tokens.
2. Verify granted scopes.
3. Complete Analytics Admin proof for GA4.
4. Create/verify GTM account/container for `humandesignengine.com`.
5. Register/verify Search Console property and submit `https://humandesignengine.com/sitemap.xml`.
6. Re-run production proof and only then mark GRO-3986 green/Done.

## Verification for this rollup

This rollup is documentation/control-plane work. Verification should confirm:

- the document is present in `docs/operations/`;
- the branch builds;
- no secret-like token values were added;
- the parent epic remains not-green until child proof closes.
