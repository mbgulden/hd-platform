# GRO-4009 Final PWP + Lighthouse + API Proof Report

Status: **NOT GREEN**
Generated: 2026-07-19T01:03:49.886Z

## Commands

- `npm run pwp:verify` → exit 0
- `npm run smoke:production` → exit 1

## PWP proof

- Summary: `okf/output/pwp-visual-qa/summary.json`
- PWP ok: `true`
- Steps: build=exit 0, visual=exit 0, a11y=exit 0, flows=exit 0, lighthouse=exit 0, links=exit 0

## Lighthouse proof

- Output directory: `okf/output/pwp-visual-qa/lighthouse`
- Report artifacts: `localhost--2026_07_19_00_59_32.report.html`, `localhost--2026_07_19_00_59_32.report.json`, `localhost--2026_07_19_01_02_50.report.html`, `localhost--2026_07_19_01_02_50.report.json`, `localhost-buy_report_-2026_07_19_00_59_57.report.html`, `localhost-buy_report_-2026_07_19_00_59_57.report.json`, `localhost-buy_report_-2026_07_19_01_03_14.report.html`, `localhost-buy_report_-2026_07_19_01_03_14.report.json`, `localhost-free_human_design_reading_generator_-2026_07_19_00_59_46.report.html`, `localhost-free_human_design_reading_generator_-2026_07_19_00_59_46.report.json`, `localhost-free_human_design_reading_generator_-2026_07_19_01_03_02.report.html`, `localhost-free_human_design_reading_generator_-2026_07_19_01_03_02.report.json`, `localhost-human_design_gates_-2026_07_19_01_00_09.report.html`, `localhost-human_design_gates_-2026_07_19_01_00_09.report.json`, `localhost-human_design_gates_-2026_07_19_01_03_25.report.html`, `localhost-human_design_gates_-2026_07_19_01_03_25.report.json`, `localhost-human_design_gates_gate_1_html-2026_07_19_01_00_21.report.html`, `localhost-human_design_gates_gate_1_html-2026_07_19_01_00_21.report.json`, `localhost-human_design_gates_gate_1_html-2026_07_19_01_03_38.report.html`, `localhost-human_design_gates_gate_1_html-2026_07_19_01_03_38.report.json`, `manifest.json`
- Reports present: `true`

## Production API proof

- Smoke ok: `false` — report delivery probe failed: HTTP 200 content-type=text/html; charset=utf-8 url=https://humandesignengine.com/api/reports/download/__hde_smoke_probe__.pdf
- Checkout endpoint: `https://humandesignengine.com/api/checkout/create-session`
- Stripe session safety: unavailable
- Report delivery: unavailable
- Cleanup: expired

## Notes

- Secrets are redacted. The smoke creates an unpaid checkout session only and attempts to expire it.
- This report is intentionally not marked green unless PWP, Lighthouse artifacts, and the live-safe API smoke all pass in the same run.

