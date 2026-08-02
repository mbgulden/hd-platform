# HDE Google OAuth Scope Flow — 2026-07-19

## Issue

[GRO-3988](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3988) requires a reusable Google OAuth principal for:

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/tagmanager.edit.containers
https://www.googleapis.com/auth/tagmanager.manage.accounts
https://www.googleapis.com/auth/tagmanager.readonly
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/siteverification
```

API-key-only calls are not sufficient for Analytics Admin, Tag Manager, Search Console, or Site Verification mutation.

## Artifact added

Ned added [google-oauth-scope-flow.py](https://prismatic.growthwebdev.com/workspace-tree?file=scripts/google-oauth-scope-flow.py) to make the consent/exchange/verify process repeatable without exposing tokens.

The script can:

1. Generate a Google consent URL for the exact required scopes.
2. Exchange Michael's returned `code=` or failed `http://localhost/?code=...` redirect into an `authorized_user` credential.
3. Save that credential outside git at:

```text
/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json
```

4. Verify the stored credential's granted scopes without printing access tokens, refresh tokens, or client secrets.

## Command shape

```bash
cd /home/ubuntu/work/hd-platform
python3 scripts/google-oauth-scope-flow.py url
python3 scripts/google-oauth-scope-flow.py exchange --code '<returned-code-or-localhost-redirect-url>'
python3 scripts/google-oauth-scope-flow.py verify
```

The default OAuth client-secrets file is read from outside the repository:

```text
/home/ubuntu/mounts/synology-photo/Antigravity/credentials.json
```

Override paths when needed:

```bash
HDE_GOOGLE_OAUTH_CLIENT_SECRETS=/secure/path/client_secret.json \
HDE_GOOGLE_OAUTH_TOKEN_PATH=/secure/path/hde-google-oauth.json \
python3 scripts/google-oauth-scope-flow.py url
```

## Fresh verification evidence

Ned checked the OKF integrations directory, prior session history, relevant `.env` files, and reusable Google credential files before declaring this blocked.

Existing reusable Google credentials are not sufficient for full GA/GTM/GSC mutation:

| Credential checked | Result |
| --- | --- |
| `/home/ubuntu/.hermes/profiles/orchestrator/home/.config/gcloud/application_default_credentials.json` | Refresh works as `mbgulden@gmail.com`, but it has none of the required GA/GTM/GSC scopes. Analytics Admin, Tag Manager, Search Console, and Site Verification probes returned `403 insufficient authentication scopes`. |
| `/home/ubuntu/.config/gcloud/application_default_credentials.json` | Refresh works and includes `webmasters`, but it is missing `analytics.edit`, `analytics.readonly`, all Tag Manager scopes, and `siteverification`. GA/GTM/Site Verification probes returned insufficient-scope 403s; Search Console also rejects this local ADC shape for the API path used here. |
| MCP Drive credentials under `/home/ubuntu/.config/mcp-gdrive/` | Existing token documents are Drive/userinfo oriented, not reusable authorized-user client-secret credentials for this GA/GTM/GSC flow. |
| HD Platform `.env` and profile `.env` files | No existing GA/GTM/GSC OAuth client/token variable was present. Only generic Google login/API-key material appeared; values were redacted during inspection. |

## Current status

🟡 Blocked on human Google OAuth consent.

Michael needs to run/open the generated consent URL and provide the returned code or failed localhost redirect URL back to Ned. After that, Ned can run the `exchange` and `verify` commands and only then proceed with Analytics Admin, Tag Manager, Search Console, and Site Verification API work.

Do not mark GA/GTM/GSC access green until the script's `verify` command reports no missing required scopes and live API probes succeed.
