# HDE checkout funnel events (GRO-3994)

The report checkout flow now emits GA4-compatible browser events while also pushing the same payloads to `window.dataLayer` and dispatching `hde:<event>` `CustomEvent`s for QA.

## Report checkout page

Emitted from `/buy-report/`:

- `checkout_report_selected` — user selects a report card. Payload includes `funnel=report_checkout`, `report`, `product_name`, `value`, and `currency=USD`.
- `checkout_cta_clicked` — user clicks the secure checkout CTA.
- `checkout_error` — validation, API, missing redirect URL, or transient payment-server error. Payload includes `error_message`.
- `checkout_session_create_started` — checkout API request is about to be sent. Payload includes product/value and referral presence.
- `checkout_session_created` — checkout API returns a Stripe redirect URL. Payload includes `checkout_session_id` when the API returns it and `stripe_redirect_host`.
- `checkout_stripe_redirect` — browser is about to leave for Stripe Checkout.

## Success page

Emitted from `/success`:

- `checkout_success_page_view` — success page opened. Payload includes lookup type and whether a session id was present.
- `checkout_purchase_confirmed` — `/api/checkout/session` lookup succeeded, confirming the purchase/session for report delivery or Telegram onboarding. Payload includes session id, lookup type, `report`, deep-link presence, and premium flag when available.
- `checkout_success_lookup_error` — session/email lookup failed and the fallback email form is shown.

## Backend contract

`payment/server.py` now returns `session_id` alongside `url` from checkout session creation so frontend analytics can tie session creation to the later success-page lookup without logging secrets.

## Verification

Focused Playwright coverage lives in `tests/flows/deconditioning-checkout.spec.ts` and asserts the report selection → CTA → session creation → Stripe redirect sequence plus success-page purchase confirmation payload.
