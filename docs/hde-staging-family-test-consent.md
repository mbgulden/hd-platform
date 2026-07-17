# HDE staging family-test consent

## Purpose

Family testing is operationally different from production use. Testers need to know that Michael and Ned may review staging conversations and generated artifacts to improve the Sanctuary bot experience.

## Implemented surfaces

- `/deconditioning/` checkout modal shows explicit staging/family-test review consent and sends metadata:
  - `coach_review_consent=true` when checked
  - `coach_review_consent_source=staging_family_test_checkout`
  - `family_test_review_consent=true`
- `/success` repeats the family/staging review notice before the Telegram link lookup.
- The Telegram onboarding router sends a staging/family-test review notice before guide selection.
- The family-test monitor remains metadata/stuck-state first; transcript content is not dumped by default.

## Privacy boundary

This staging test consent is for family/beta improvement only. Production customer privacy remains separate. Coach portal APIs still require active premium status, active coach-review consent, no revoked consent timestamp, and an active coaching window before reading or mutating client workspace files.

## Verification expectation

Focused verification should confirm the public staging HTML contains the consent copy/metadata keys, the router compiles, the monitor output remains metadata-only, and coach APIs remain gated.
