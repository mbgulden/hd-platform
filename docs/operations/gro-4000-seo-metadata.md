# GRO-4000 — Legacy/generated page SEO metadata

## Scope

GRO-4000 closes missing `<meta name="description">` and `<link rel="canonical">` gaps on tracked legacy/generated HTML pages in `hd-platform`.

The update covers:

- copied legacy docs under `docs/`
- legacy landing aliases under `landing/`
- static public aliases under `public/`
- `playground/index.html`
- `product-catalog.html`

No secrets, runtime backups, `content/`, `assets/`, `designs/`, `research/`, or `active-oahu/` files are part of this change.

## Verification

Run from the repo root:

```bash
python3 scripts/verify_seo_metadata.py --root .
npm run build
python3 scripts/verify_seo_metadata.py --root . --include-dist
```

- Updated `scripts/route-complete-build.mjs` so built redirect pages emit absolute canonical URLs and descriptions.
- Added `wrangler.jsonc` static asset directory mapping so the Cloudflare Workers Builds check can dry-run the same `dist` output instead of failing without an entry point.

The verifier scans tracked HTML files, and optionally built `dist/**/*.html`, and fails if any page with a `<head>` lacks a 40+ character meta description or a `https://humandesignengine.com/...` canonical URL.
