# HDE standard shell for legacy reference pages — 2026-07-17

## Scope

Adds the standard Human Design Engine website header and footer to legacy/static surfaces that are not rendered through the Astro layout.

Covered route families:

- `/human-design/profiles/` and sub-pages
- `/human-design/types/` and sub-pages
- `/human-design/centers/` and sub-pages
- `/human-design/channels/` and sub-pages
- `/human-design/gates/` and sub-pages
- `/hd-engine/free-tools/type-quiz.html`
- `/hd-engine/free-tools/gate-lookup.html`
- `/bodygraph.html`
- `/free-human-design-reading-generator/`

## Implementation

- `scripts/route-complete-build.mjs` injects a standard header/footer shell into targeted legacy pages during postbuild normalization.
- `docs/hde-light-theme.css` contains the shell styles and legacy free-tool contrast fixes.
- `src/layouts/Layout.astro` now includes the shared Astro `Nav` and `Footer` components so Astro pages such as the free reading generator use the same shell.
- `.pwp/routes.json` includes representative routes for visual/a11y/link coverage.

## Verification

- `npm run pwp:verify` passed after the change.
- Live staging Playwright check confirmed the standard shell on the listed route families, representative sub-pages, Cloudflare alias, and direct deployment URL.
