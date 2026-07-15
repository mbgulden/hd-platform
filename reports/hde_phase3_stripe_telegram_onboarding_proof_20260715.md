# HDE Phase 3 — Stripe → Webhook → Invitation → Telegram Onboarding Proof

**Date:** 2026-07-15
**Branch:** `ned/hde-phase3-stripe-telegram-proof-2026-07-15`
**Status:** 🟡 **YELLOW**
**Canonical workflow source:** `https://staging.humandesignengine.com/deconditioning/`

## Result

Phase 3 is **partially proven**:

- ✅ Real Stripe test-mode checkout was completed through the Stripe-hosted checkout page.
- ✅ Stripe session status is `complete` and payment status is `paid`.
- ✅ Webhook handler received `checkout.session.completed` events.
- ✅ A staging webhook blocker was found and fixed: the staging `User` model was missing coach-review consent fields used by checkout processing.
- ✅ A signed replay of the completed Stripe test session exercised the same staging webhook endpoint and returned success.
- ✅ User state and invitation state were created.
- ✅ `/api/checkout/session?session_id=...` resolves to a Telegram deep link.
- ✅ Router metrics remained clean.
- 🟡 Human Telegram tap/start proof is still pending.

This is **not GREEN** yet because the final Telegram handoff needs a real tester to tap the deep link and send `/start` so invitation usage and BotInstance creation can be observed.

## Evidence

### Stripe checkout completion

| Item | Result |
|---|---:|
| Stripe mode | test |
| Checkout method | Playwright automation against Stripe-hosted checkout |
| Test card | Stripe `4242` test card |
| Checkout session status | `complete` |
| Payment status | `paid` |
| Mode | `subscription` |
| Customer present | yes |
| Subscription present | yes |
| Session ID | `[REDACTED]` |
| Customer email | `[REDACTED_PHASE3_TEST_EMAIL]` |

### Webhook proof

Initial automatic webhook attempts showed the correct event but failed before user creation:

```text
Received Stripe webhook: checkout.session.completed
POST /api/webhooks/stripe -> 500
TypeError: 'coach_review_consent' is an invalid keyword argument for User
```

Fix applied:

- Added `coach_review_consent` fields to staging `shared.database.User`.
- Added idempotent `ALTER TABLE` entries in `init_db()` for those consent columns.
- Restarted `hde_api_staging.service` and verified `/ping` returned OK.

After the fix, a signed replay using the real completed test session exercised the same webhook endpoint:

```json
{
  "http": 200,
  "body": {"success": true, "event_received": "checkout.session.completed"}
}
```

### Database state after webhook replay

| State | Result |
|---|---:|
| User exists | ✅ yes |
| `subscription_status` | `active` |
| Stripe customer ID present | ✅ yes |
| Coach review consent | `false` |
| Invitation count | `1` |
| Invitation token present | ✅ yes |
| Invitation used | `false` |
| BotInstance exists before Telegram `/start` | no — expected until tester taps Telegram link |

### Success/session resolution

`/api/checkout/session?session_id=...` returned `200` and produced one deep link:

```text
https://t.me/Humandesigncompanionbot?start=[REDACTED]
```

Returned fields included:

- `deep_link`
- `token`
- `expires_at`
- `is_premium`
- `coach_review_consent`

### Router metrics after proof

| Metric | Result |
|---|---:|
| status | `ok` |
| Redis OK | ✅ true |
| healthy guest containers | `2` |
| chat pending | `0` |
| media pending | `0` |
| wake pending | `0` |

### Services

| Service | Result |
|---|---:|
| `hde_api_staging.service` | 🟢 active |
| `hde_router.service` | 🟢 active |
| `hde-payment.service` | 🟢 active |
| `guest-hermes-23` | 🟢 running healthy |

## Remaining risks

1. **Telegram handoff is not human-proven yet.** A real tester must tap the success-page deep link and send `/start`.
2. **Fresh automatic Stripe webhook after the fix should be observed.** The exact handler path was proven with a signed replay, but the automatic webhook delivery that occurred before the fix returned `500`.
3. **Solo paid status semantics need confirmation.** Solo checkout currently creates `subscription_status=active` and an onboarding invitation, while `is_premium=false` under current metadata rules. That may be intended for Solo Sanctuary, but it should be confirmed before broad paid traffic.

## Recommendation

🟡 **YELLOW:** proceed to one controlled human Telegram tester for final Phase 3 proof. Do not open broad paid traffic yet.

## Next gate

Have Michael or an internal tester open the redacted deep link from the success page, send `/start`, then verify:

- invitation `is_used=true`,
- `BotInstance` exists for the paid user,
- router logs show successful onboarding prompt delivery,
- router metrics remain pending `0/0/0`.
