# HDE launch runtime and checkout cleanup — 2026-07-17

## Scope

This checkpoint separates the non-theme launch/runtime changes from the light-theme and PWP verification commit.

## Runtime changes

- Academy course payloads can expose an optional `checkout_url` for paid/course surfaces.
- User records can store coach-review consent metadata, and the database initializer backfills those consent columns when absent.
- Invitation expiry now defaults to a long-lived tester/launch window instead of a 24-hour expiry.

## Checkout changes

- Poster checkout accepts `poster`, `print-poster`, and `poster-print` aliases.
- Poster checkout carries `poster_size`, mockup/poster image URL, and print-file URL through the frontend form and payment server metadata.
- Poster products collect shipping and phone information for Printful fulfilment.
- The checkout success page now handles email/report delivery sessions that do not have a Telegram deep link.

## Launch surface changes

- Primary navigation points users to the free reading generator, report purchase page, Sanctuary, API docs, learning pages, and coaching.
- Homepage CTAs and pricing links point at canonical route-complete paths.
- The homepage mounts the current `.hde-chart-widget` rather than the older `<hd-bodygraph>` tag.

## Verification

Run before commit:

```bash
python3 -m py_compile api/routes/academy.py payment/server.py shared/database.py
npm run build
npm run pwp:verify
```

The PWP suite verifies the theme/route surfaces; focused Python compilation covers the runtime files changed in this checkpoint.
