# HDE analytics events

GRO-3995 adds a browser-side event contract for the free-reading and Sanctuary daily-work funnel. Events are intentionally PII-safe: birth data, names, emails, and chart payloads are not emitted.

## Dispatch behavior

`public/widget.js` and `public/widget.src.js` expose `window.HDEWidget.trackEvent(eventName, params)`. Each call:

1. Dispatches `window` `CustomEvent("hde:analytics")` for local listeners/tests.
2. Pushes `{ event, ...params }` to `window.dataLayer` when Google Tag Manager is present.
3. Calls `gtag("event", eventName, params)` when GA4 is present.
4. Calls optional `window.hdeTrackEvent(eventName, params)` for future server-side collectors.

## Event names

| Event | Trigger | Notes |
| --- | --- | --- |
| `hde_chart_generated` | Free chart API returns a successful chart | Emits non-PII chart classification fields only: `chart_type`, `authority`, `profile`, `defined_centers_count`. |
| `hde_daily_work_cta_clicked` | Free-reading result CTA or Sanctuary package CTA clicked | Emits CTA/package identifiers only. |
| `hde_transit_prompt_viewed` | Free-reading result renders the daily embodied experiment prompt | Indicates the user saw the daily-work prompt after a chart. |
| `hde_nervous_system_practice_started` | User clicks **Start practice** in the free-reading result | Measures daily work start. |
| `hde_nervous_system_practice_completed` | User clicks **Mark complete** in the free-reading result | Measures daily work completion intent. |
| `hde_sanctuary_checkout_submitted` | Sanctuary checkout modal submits | Emits package/staging metadata only. |

## Verification

A local verifier can stub `window.dataLayer`, `window.gtag`, and `window.hdeTrackEvent`, load `/widget.js`, submit the widget form with a mocked successful chart response, then assert all five free-reading event names are observed without PII fields.
