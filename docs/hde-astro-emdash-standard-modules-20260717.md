# HDE Astro/emdash standard module shell — 2026-07-17

## Goal

Put HDE staging on one PWP/emdash shell so future header, footer, navigation, and global theme changes happen once instead of being copied into each page.

## What changed

- `src/layouts/Layout.astro` owns the site chrome:
  - imports `src/components/Nav.astro`
  - imports `src/components/Footer.astro`
  - renders exactly one `body > header.emdash-site-header`
  - renders exactly one `body > footer.emdash-site-footer`
- Astro pages no longer import or render `Nav`/`Footer` individually.
- `src/components/Nav.astro` and `src/components/Footer.astro` carry the shared shell classes used by PWP visual checks.
- `scripts/route-complete-build.mjs` normalizes copied legacy `docs/**/*.html` into the same generated emdash shell contract during postbuild:
  - removes each legacy page's old `<nav>` and final `<footer>` blocks
  - injects one standard emdash header/footer template
  - keeps legacy body content intact
  - keeps the cream/sage theme bridge active
- `docs/hde-light-theme.css` now includes the shared `.emdash-site-header` and `.emdash-site-footer` style contract for generated legacy pages.
- `.pwp/routes.json` now covers Astro pages, legal pages, checkout/success, and representative copied legacy pages.
- `tests/visual/hde-core-pages.spec.ts` now proves the regression class directly:
  - exactly one direct site header
  - exactly one direct site footer
  - expected nav labels
  - expected footer groups
  - no temporary `hde-standard-*` shell classes
  - mobile menu opens visibly

## Verification commands

```bash
npm run build
npm run qa:visual
npm run pwp:verify
```

Use AGY/Gemini semantic QA after deterministic checks:

```bash
export NANO_BANANA_MODEL=gemini-3.1-flash-image-preview
prismatic-engine visual-verify https://<staging-preview>/ --viewport mobile:390x844 --json
```

## Production rule

Do not merge this to production until Michael approves the staging preview. This branch is staging/dev only.
