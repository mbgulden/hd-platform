# GRO-4003 — Search Console sitemap resubmission evidence

Checked: 2026-07-18T23:37:21Z
Agent: Ned

## Scope

Task: resubmit `https://humandesignengine.com/sitemap.xml` in Google Search Console and record coverage/indexing proof for Human Design Engine.

## Live sitemap/robots verification

Fresh live checks passed before attempting Google Search Console submission:

```text
GET https://humandesignengine.com/sitemap.xml -> HTTP 200
Content-Type: application/xml
Bytes: 14831
SHA-256: 73a6e025a0bf942c389698db973dcd1d8fdf908d7791851cb02deccd0768a01b
Parsed URL count: 171

GET https://humandesignengine.com/robots.txt -> HTTP 200
Body:
User-agent: *
Allow: /
Sitemap: https://humandesignengine.com/sitemap.xml
```

First sitemap URLs parsed from the live document:

```text
https://humandesignengine.com/
https://humandesignengine.com/affiliates.html
https://humandesignengine.com/affiliates/dashboard.html
https://humandesignengine.com/affiliates/signup.html
https://humandesignengine.com/api/
```

## Search Console submission attempt

Google Search Console API submission could not be completed with the currently available local credentials.

Evidence gathered before declaring the task blocked:

- Checked `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/` for Search Console/GSC/sitemap integration notes: no matching integration runbook found.
- Checked prior sessions for `GRO-4003`, `Search Console`, `sitemap`, and `GSC` context.
- Checked relevant environment files without exposing secrets:
  - `/home/ubuntu/work/hd-platform/.env` has no Search Console/Google OAuth credential entries.
  - `/home/ubuntu/work/agentic-swarm-ops/.env` contains placeholder-style `GOOGLE_API_KEY` / `GOOGLE_OAUTH_TOKEN` entries; tokeninfo returned `invalid_token`.
  - `/home/ubuntu/.google_oauth_creds.json` exists with OAuth client metadata and a refresh token, but refresh returned `invalid_grant`.
- Checked `gcloud auth list --format=json`: no authenticated accounts.
- Direct `GET https://www.googleapis.com/webmasters/v3/sites` with the locally available OAuth token returned HTTP 401 `UNAUTHENTICATED` / `Invalid Credentials`.

Current blocker:

```text
POST https://oauth2.googleapis.com/token -> HTTP 400
error: invalid_grant
error_description: Bad Request
```

## Result

The production sitemap is live, parseable, and advertised in `robots.txt`. Search Console resubmission and coverage proof remain blocked until a valid Google OAuth token/refresh token with Search Console (`webmasters`) access is available.

Related dependency already visible in Linear queue: GRO-3988 — upgrade/obtain OAuth scopes for Analytics Admin, Tag Manager, Search Console.

## Safe next command once credentials are refreshed

With a valid access token in the shell:

```bash
ACCESS_TOKEN='<valid-search-console-oauth-token>'
SITE_URL='sc-domain:humandesignengine.com' # or the exact URL-prefix property shown by sites.list
SITEMAP_URL='https://humandesignengine.com/sitemap.xml'
ENCODED_SITE_URL=$(python3 - <<'PY'
import urllib.parse
print(urllib.parse.quote('sc-domain:humandesignengine.com', safe=''))
PY
)
ENCODED_SITEMAP_URL=$(python3 - <<'PY'
import urllib.parse
print(urllib.parse.quote('https://humandesignengine.com/sitemap.xml', safe=''))
PY
)
curl -X PUT \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://www.googleapis.com/webmasters/v3/sites/${ENCODED_SITE_URL}/sitemaps/${ENCODED_SITEMAP_URL}"
```

Then verify with:

```bash
curl -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://www.googleapis.com/webmasters/v3/sites/${ENCODED_SITE_URL}/sitemaps/${ENCODED_SITEMAP_URL}"
```
