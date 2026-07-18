# Human Design Engine GA4 property/data-stream verification

Issue: [GRO-3989](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3989)  
Domain: `humandesignengine.com`  
Checked: `2026-07-18T21:26:38Z`

## Current GA4 stream record

The HD Engine repo and live pages already reference this GA4 Measurement ID:

```text
G-Q6TPL08VM7
```

This is the reusable web measurement ID currently embedded in committed HDE pages. No secrets are stored in this document.

## What was verified

A fresh verifier was added at:

```text
scripts/operations/verify_ga4_stream.py
```

It checks:

1. committed repo files for GA4 measurement IDs;
2. selected live `humandesignengine.com` pages for the expected `gtag.js` loader;
3. the public Google `gtag/js?id=G-Q6TPL08VM7` endpoint;
4. whether an OAuth bearer token is available for Google Analytics Admin API proof.

Command:

```bash
python3 scripts/operations/verify_ga4_stream.py --repo .
```

## Fresh proof captured before commit

Manual live probe before adding the verifier:

```text
https://humandesignengine.com/                  HTTP 200  GA4 snippet missing
https://humandesignengine.com/landing-reports.html HTTP 200  G-Q6TPL08VM7 present
https://humandesignengine.com/buy-report.html   HTTP 200  GA4 snippet missing
https://www.googletagmanager.com/gtag/js?id=G-Q6TPL08VM7 HTTP 200
```

Analytics Admin API probe with the available Google API key returned Google's expected OAuth requirement:

```text
HTTP 401
API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal.
service: analyticsadmin.googleapis.com
method: google.analytics.admin.v1beta.AnalyticsAdminService.ListAccountSummaries
```

## Access state

Searches performed before calling this blocked:

- OKF integration docs under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`;
- prior Hermes sessions for GA4 / Google Analytics / Analytics Admin / `humandesignengine`;
- relevant `.env` files under `/home/ubuntu/work` and Hermes profiles, with values redacted.

Known Google auth evidence from `docs/operations/hde-google-auth-via-kai-2026-07-18.md` still applies:

- Kai/AGY can authenticate as `mbgulden@gmail.com` interactively.
- No reusable `gcloud` account or OAuth token with `analytics.edit` / `analytics.readonly` was found for Ned.
- API-key-only access is insufficient for Analytics Admin.

## Verifier result

Fresh run after adding the verifier:

```text
python3 -m py_compile scripts/operations/verify_ga4_stream.py
python3 scripts/operations/verify_ga4_stream.py --repo .
```

Summary:

```text
summary_status=partial
repo_expected_measurement_file_count=146
gtag_js_http=200 bytes=432086
https://humandesignengine.com/                  200 expected_measurement_present=False gtag_loader_present=False
https://humandesignengine.com/landing-reports.html 200 expected_measurement_present=True gtag_loader_present=True
https://humandesignengine.com/buy-report.html   200 expected_measurement_present=False gtag_loader_present=False
https://humandesignengine.com/widget-demo.html  200 expected_measurement_present=True gtag_loader_present=True
https://humandesignengine.com/bodygraph.html    200 expected_measurement_present=True gtag_loader_present=True
admin_verified=False
admin_probe_status=401 UNAUTHENTICATED
```

## Status

🟡 Partial / blocked by Google OAuth scope.

- `G-Q6TPL08VM7` is the current recorded GA4 measurement ID for HDE.
- The tag is present on 146 committed repo files and 3 of 5 sampled live pages, so the stream/tag installation is not zero.
- The live install is not site-wide: the homepage and `/buy-report.html` did not expose the expected snippet in the fresh verifier probe.
- GA4 property/data-stream ownership cannot be proven or mutated through Analytics Admin until a reusable OAuth credential with `analytics.readonly` and preferably `analytics.edit` is available.

## Required next step

Obtain or refresh a non-git OAuth credential for `mbgulden@gmail.com` with at least:

```text
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/analytics.edit
```

Then rerun:

```bash
GOOGLE_OAUTH_TOKEN=<redacted> python3 scripts/operations/verify_ga4_stream.py --repo .
```

Green proof for this issue is: Analytics Admin API confirms the account/property/web data stream for `humandesignengine.com`, and the live tag crawl shows expected coverage or documents intentional exclusions.
