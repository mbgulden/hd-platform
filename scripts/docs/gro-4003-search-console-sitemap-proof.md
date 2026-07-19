# GRO-4003 — Search Console sitemap resubmission evidence

Checked: 2026-07-19T03:18Z
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

Google Search Console API authentication is now partially available via local Application Default Credentials, but the Human Design Engine property is not verified for this Google principal yet. The sitemap cannot be submitted until ownership/permission is upgraded.

Evidence gathered before keeping the task blocked:

- Checked `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/` for Search Console/GSC/sitemap integration notes: no matching HDE Search Console ownership runbook found.
- Checked prior sessions for `GRO-4003`, `GRO-3988`, `Search Console`, `hde-google-oauth`, `sitemap`, and `GSC` context.
- Checked relevant `.env*` files without exposing secrets. No ready HDE Search Console property credential artifact exists at `/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json`.
- `/home/ubuntu/.google_oauth_creds.json` still refreshes as `invalid_grant`.
- `/home/ubuntu/.config/gcloud/application_default_credentials.json` refreshes successfully with scopes `webmasters`, `webmasters.readonly`, and `cloud-platform` when the ADC quota project is passed via `x-goog-user-project`.
- `sites.list` succeeds with that token, but it lists existing owned properties only for Active Oahu / related sites; it did not list `humandesignengine.com` before this pass.
- `PUT sites/https%3A%2F%2Fhumandesignengine.com%2F` succeeded with HTTP 204, adding the URL-prefix property to the account as `siteUnverifiedUser`.
- `PUT sites/https%3A%2F%2Fhumandesignengine.com%2F/sitemaps/https%3A%2F%2Fhumandesignengine.com%2Fsitemap.xml` returned HTTP 403: `User does not have sufficient permission for site 'https://humandesignengine.com/'`.
- `GET .../sitemaps` returned the same HTTP 403 permission error.
- URL Inspection API for `https://humandesignengine.com/` returned HTTP 403: `You do not own this site, or the inspected URL is not part of this property.`
- Site Verification token request for a meta-tag token returned HTTP 403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT`; the current token has Search Console/Webmasters scopes but not Site Verification scope.
- Live homepage fetch confirms no existing `google-site-verification` meta tag is present.

Current blocker:

```text
Search Console OAuth works for webmasters API calls, but the Google principal is only
siteUnverifiedUser for https://humandesignengine.com/. Sitemap submit, sitemap
coverage, and URL inspection all return HTTP 403 until ownership verification or
owner-level permission is completed.
```

## Result

The production sitemap is live, parseable, and advertised in `robots.txt`. Search Console resubmission and coverage proof remain blocked because the available Google principal is not a verified owner for `https://humandesignengine.com/`.

This pass improved the state from "no usable Search Console OAuth" to "Search Console OAuth works, property added as unverified, owner verification still required." Do not mark GRO-4003 green/Done until `sites.list` shows `humandesignengine.com` with owner/full permission and sitemap submit + sitemap/URL inspection proof pass.

Related dependency already visible in Linear queue: GRO-3988 — upgrade/obtain OAuth scopes and/or complete Search Console property ownership verification for Human Design Engine.

## Safe next command once ownership is verified

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
