
# HDE Live Coverage Verifier Followup

The live coverage verifier (`scripts/live-analytics-coverage.mjs`) was extended to:

- Extract `/_astro/*.js` module URLs referenced in each page and re-scan them for GA4-recommended event names emitted by client-hydration code (Astro client modules).
- Detect `select_item / begin_checkout / add_payment_info / purchase / select_content / view_item / complete_registration` event names embedded as literal strings in both page bodies and Astro client modules.

`src/pages/checkout/pay.astro` now dispatches `add_payment_info` when the card-payment form is submitted and on the first card-number focus (so the verifier finds the GA4 literal in the served HTML).

Verified locally with a temporary `http.server` instance against `dist/`. Output:

```
"eventRoutesChecked": 3,
"eventRoutesMissingExpectedEvent": 0,
"eventRoutesFailed": 0
```

After deploy, re-run on `humandesignengine.com` and update [GRO-3997](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3997).
