# HDE Staging Style Correction — Emails, Workflows, and PDFs

**Date:** 2026-07-15
**Branch:** `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`
**Status:** 🟡 YELLOW — staging surfaces corrected; paid Telegram `/start` and final human design approval still pending.

## Correction

Michael was right: the visual source of truth is **`staging.humandesignengine.com/deconditioning/`**, not the live-site navy/gold system. Production/live styling should not be used as the reference for this staging launch gate.

## Staging style tokens used

Extracted from the staging page at `https://staging.humandesignengine.com/deconditioning/`:

- `--cream-bg`: `#FAF7F0`
- `--cream-light`: `#FDFBF7`
- `--sage-deep`: `#2F3631`
- `--sage-mid`: `#5F7261`
- `--text-primary`: `#2F3631`
- `--text-secondary`: `#5C625E`
- `--text-muted`: `#808682`
- `--taupe-light`: `#C7BFB5`
- `--card-border`: `rgba(95, 114, 97, .15)`
- `--radius`: `12px`
- `--radius-lg`: `24px`
- Fonts: `Outfit` for body, `Playfair Display` for headings.

## Changed staging surfaces

### Checkout / Telegram handoff email

File: `api/routes/stripe_webhook.py`

- Replaced the previous live-style navy/gold email with the staging cream/sage card system.
- Uses `Outfit` + `Playfair Display`.
- Uses a single clear Telegram CTA.
- Footer points to the staging deconditioning route while this remains a staging gate.

### Report delivery emails

Files:

- `reports/server.py`
- `payment/server.py`

Changes:

- Replaced generic plain-text report email with multipart plain-text + HTML emails.
- Uses the staging cream/sage card system.
- Keeps the PDF attachment behavior intact.
- Copy now matches the staging Sanctuary posture: private reference, read at your own pace, no performance pressure.

### Generated PDF report design

File: `reports/server.py`

Changes:

- Removed the old purple/blue gradient PDF style.
- Replaced PDF CSS with the staging system:
  - cream background,
  - sage-dark cover frame,
  - white cards,
  - sage section accents,
  - Playfair headings,
  - Outfit body text.
- Kept existing report content and PDF generation pipeline intact.

## Workflow scope

No production deploy was performed. The live-site style branch change was reverted in the canonical source branch. This correction applies to the staging workspace and staging branch only.

## Verification summary

Verification was focused/ad-hoc, not full suite green:

- Staging style tokens were extracted from the live staging page via browser-computed CSS.
- Changed Python files compile.
- Fake-SMTP email captures prove the generated emails use staging cream/sage tokens and retain attachments/CTA behavior.
- PDF generation/render/OCR proof confirms a staging-styled report can be generated.
- Secret-shaped strings were scanned and not found in changed artifacts.

## Still not green

- Paid Telegram `/start` human proof is still pending.
- Final human design approval of the staging-styled PDF is still pending.
- Broad launch is not ready until Phase 3 and Phase 4 are both green with live evidence.
