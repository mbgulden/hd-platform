# HDE canonical analytics loader (GRO-3993)

This repo uses one canonical GA4 loader for the static site:

- Measurement ID: `G-Q6TPL08VM7`
- Astro pages receive the loader from `src/layouts/Layout.astro`.
- Legacy/static HTML copied into `dist/` is normalized by `scripts/route-complete-build.mjs` during `npm run postbuild`.

The postbuild normalizer removes prior inline GA4 snippets that load `https://www.googletagmanager.com/gtag/js` and injects the canonical block before `</head>`. That keeps sitemap pages consistently tagged without editing generated legacy content in place.

Verification used for this change:

```bash
npm run build
node - <<'NODE'
// scans dist HTML for missing or duplicate canonical analytics loaders
NODE
```
