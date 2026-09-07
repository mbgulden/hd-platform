# HDE family-test runbook (20260716)

## Status

Use this only for controlled staging testers after one owner/tester completes the Telegram `/start` proof. Do not send public/live traffic here.

## Staging URL

`https://staging.humandesignengine.com/deconditioning/`

## Golden path for tester

1. Open the staging URL.
2. Read the Somatic Sanctuary page enough to know what is being offered.
3. Choose Solo Sanctuary unless Michael gives another tier.
4. Enter the test email Michael assigns.
5. Complete Stripe test checkout only. Do not use a live card.
6. Confirm the browser lands on `/success/?session_id=...`.
7. Confirm there is one clear `Open Telegram` CTA.
8. Tap `Open Telegram`.
9. In Telegram, send `/start`.
10. Confirm the bot replies with Sanctuary-style onboarding, not generic companion/menu sludge.
11. Ask for/rebuild a chart.
12. Confirm report/chart media arrives and opens.

## Feedback to capture

- Screenshot of the checkout start page.
- Screenshot of success page with Telegram CTA.
- Screenshot of Telegram `/start` response.
- Screenshot or file proof that chart/report media arrived.
- Any exact copy that felt confusing, too generic, broken, or off-brand.
- Any place where the tester did not know the next step.

## Backend checks Ned/operator must run after tester `/start`

- Invitation is marked used.
- Telegram user is linked to the paid staging user.
- Guest bot/container is healthy.
- Router queues pending count is 0.
- Telegram media delivery logs show successful document/image sends.
- Stripe session/customer/token values are redacted in any report.

## Stop criteria

Stop the family test if:

- success page has no Telegram CTA,
- Telegram CTA opens wrong bot,
- `/start` does not link the paid invitation,
- bot gives generic/broken onboarding,
- report media fails to deliver,
- any private/admin/coach path is exposed publicly,
- any credential-shaped value appears in logs or reports.

## Known caveats before public launch

- Production route fallback is still blocked.
- Production API Access behavior is unresolved.
- Report-server source fix must be promoted by the correct lane owner.
- Live Stripe charge is not approved or proven.
