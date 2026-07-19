# Free reading CLS reservation

GRO-4006 reserves first-paint layout space for `/free-human-design-reading-generator/` before `/widget.js` hydrates the embedded Human Design widget.

## Implementation

- The page now ships a server-rendered `.widget-skeleton` inside `.hde-chart-widget`.
- `.widget-reservation` and `.hde-chart-widget` reserve at least `560px` of vertical space on desktop and `600px` on narrow screens.
- The skeleton dimensions mirror the hydrated widget card so the JavaScript replacement does not collapse an empty mount point and then push content downward.

## Verification

Run:

```bash
npm run build
npm run qa:flows -- --project=chromium tests/flows/deconditioning-checkout.spec.ts
```

The flow suite includes a no-JavaScript-hydration regression check that blocks `/widget.js`, verifies the skeleton remains visible, and asserts the widget panel keeps at least `560px` of reserved height.
