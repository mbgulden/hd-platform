# HDE Search Console registration — GRO-3991

## Status

Blocked on fresh Google OAuth consent for Search Console / Site Verification scopes.

Do **not** mark Search Console registration green from intent or API-key proof. Google Search Console create/list/submit calls require an OAuth principal with the right scopes; the local reusable ADC credential is currently invalid and API-key-only calls are rejected by Google.

## Live site evidence collected

Timestamp: `2026-07-18T21:14:48Z`

| Check | Result |
|---|---|
| `https://humandesignengine.com/robots.txt` | HTTP `200`, `text/plain`; contains `Sitemap: https://humandesignengine.com/sitemap.xml` |
| `https://humandesignengine.com/sitemap.xml` | HTTP `200`, `application/xml`; parsed successfully |
| Sitemap URL count | `171` `<loc>` entries |
| First sitemap URL | `https://humandesignengine.com/` |

## Auth discovery performed

Before declaring the task blocked, Ned checked the required sources:

- OKF integrations and project docs for Search Console / sitemap / Google auth notes.
- Prior Hermes sessions for `GRO-3988`, Search Console, and OAuth-scope work.
- Relevant `.env` files for Google/Search Console/OAuth credentials without printing secrets.
- Local `gcloud` auth/ADC state under Ned, Kai, and the default home profile.

Findings:

- `GOOGLE_API_KEY` exists, but Search Console API rejects API keys for authenticated site operations.
- `gcloud auth application-default print-access-token` fails with `invalid_grant: Bad Request` and asks for a fresh `gcloud auth application-default login`.
- Kai AGY is authenticated as `mbgulden@gmail.com`, but that does not provide a reusable local OAuth token with Search Console mutation scopes.
- Existing documentation already identifies `GRO-3988` as the OAuth-scope unblocker for Analytics Admin, Tag Manager, Search Console, and Site Verification.

## Blocker proof

API-key-only Search Console list call:

```text
GET https://www.googleapis.com/webmasters/v3/sites?key=<redacted>
HTTP 401
status: UNAUTHENTICATED
message: API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal.
```

ADC token refresh:

```text
gcloud auth application-default print-access-token
exit: 1
ERROR: There was a problem refreshing your current auth tokens: invalid_grant: Bad Request
Please run: gcloud auth application-default login
```

## Human action required

Open the generated OAuth URL from `/tmp/hde_google_auth_url_gro3991.txt` while signed in as `mbgulden@gmail.com`, approve these scopes, and provide the returned code/redirect result back to Ned:

```text
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/webmasters.readonly
https://www.googleapis.com/auth/siteverification
https://www.googleapis.com/auth/cloud-platform
```

After that, Ned can:

1. Exchange the code without printing tokens.
2. Verify the token scopes.
3. Add or verify `sc-domain:humandesignengine.com` or URL-prefix property.
4. Preserve DNS/static verification artifact as appropriate.
5. Submit `https://humandesignengine.com/sitemap.xml`.
6. Record Search Console sitemap status from API output.

## Safety notes

- No Google access tokens, refresh tokens, client secrets, or Cloudflare keys are committed here.
- No live DNS or verification artifacts were changed during this pass.
- This issue should remain non-green until Search Console API/UI proof confirms property verification and sitemap submission.
