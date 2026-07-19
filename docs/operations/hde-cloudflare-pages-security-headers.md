# HDE Cloudflare Pages security headers

## Scope

GRO-4005 adds a Cloudflare Pages `_headers` policy for the production static site output. The file lives at `public/_headers` so Astro copies it to `dist/_headers` during `npm run build`.

## Policy intent

The global `/*` rule enables:

- `Strict-Transport-Security` with one-year max age, subdomains, and preload.
- `Content-Security-Policy` with `default-src 'self'`, `object-src 'none'`, and `frame-ancestors 'self'`.
- `Permissions-Policy` denying high-risk browser capabilities by default while keeping Stripe payment surfaces available.
- `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin`.

## Checkout-safe allowances

The CSP intentionally keeps these third-party services available because the launch funnel depends on them:

- Stripe checkout/payment surfaces: `https://checkout.stripe.com`, `https://js.stripe.com`, `https://hooks.stripe.com`, and `https://api.stripe.com`.
- Google Analytics / Google Tag Manager: `https://www.googletagmanager.com`, `https://www.google-analytics.com`, `https://region1.google-analytics.com`, and `https://stats.g.doubleclick.net`.
- Google Fonts: `https://fonts.googleapis.com` and `https://fonts.gstatic.com`.

Inline script/style remains allowed for now because the current static pages and GA snippet use inline JavaScript/CSS. Removing `'unsafe-inline'` should be a separate hardening task after nonces/hashes or externalized scripts are in place.

## Verification checklist

Before marking the task green, verify:

1. `npm run build` succeeds.
2. `dist/_headers` exists and contains HSTS, CSP, Permissions-Policy, and `frame-ancestors`.
3. The built CSP still includes Stripe, Google Analytics/Tag Manager, and Google Fonts allowances.
4. A checkout smoke still reaches an origin/Stripe response rather than failing because a needed domain was omitted.
