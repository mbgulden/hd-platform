# Human Design Engine Sanctuary Demo Flow

## Status model

| Status | Meaning | Bot/container behavior |
|---|---|---|
| `paid` | Normal paid Sanctuary member | Full access while `subscription_status=active` |
| `demo` | Semi-public 14-day tester | Bot access allowed until `trial_expires_at`; bot prompt receives demo context |
| `expired_demo` | Demo has ended without upgrade | Bot pauses access; workspace/container retained until `deletion_scheduled_at` |
| `inactive` | Paid subscription inactive/canceled | Bot pauses access; workspace/container retained through grace window |

## Public/semi-public routes

| Route | Purpose | Indexing |
|---|---|---|
| `/deconditioning/` | Normal paid Sanctuary landing page | public |
| `/sanctuary-demo/` | Semi-public free 14-day tester page | `noindex,nofollow` + robots disallow |

## Demo funnel

```text
/sanctuary-demo/
→ POST /api/demo/start with email/name/invite_code
→ user.access_status=demo
→ user.trial_expires_at=now+14 days
→ invitation token created
→ tester clicks Telegram deep link
→ head bot validates demo status/countdown
→ VM orchestrator provisions user container with GUEST_ACCESS_STATUS + GUEST_TRIAL_EXPIRES_AT
→ guest bot prompt knows it is a demo account
```

## Upgrade funnel

```text
/deconditioning/ paid checkout
→ Stripe webhook/process_successful_checkout
→ user.access_status=paid
→ user.subscription_status=active
→ user.trial_expires_at/deactivated_at/deletion_scheduled_at cleared
→ existing bot_instance.status=active
→ same Sanctuary container continues
```

## Expiry/deletion lifecycle

Run `scripts/hde_trial_lifecycle.py` at least daily.

```text
If access_status=demo and trial_expires_at <= now:
  access_status=expired_demo
  subscription_status=inactive
  bot_instance.status=suspended
  orchestrator action=stop
  deletion_scheduled_at=now+30 days

If access_status=expired_demo and deletion_scheduled_at <= now:
  bot_instance.status=deprovisioning
  orchestrator action=deprovision
```

Important: `deprovision` still deletes the container/workspace. It should only run after the retention window or explicit admin action.

## Nice-to-have management/governance checklist

- Add admin dashboard filters for `demo`, `expired_demo`, `deletion_scheduled_at`, and `trial_expires_at`.
- Send reminder emails/messages at day 7, day 12, expiry, and 7 days before deletion.
- Add `HDE_DEMO_INVITE_CODE` in production if the page should be semi-public but gated.
- Rate-limit `/api/demo/start` by IP/email to prevent bot/container abuse. Implemented as an in-process guard (`HDE_DEMO_RATE_LIMIT_WINDOW_SECONDS`, `HDE_DEMO_RATE_LIMIT_MAX_ATTEMPTS`) and should be backed by edge/WAF limiting before production.
- Active demo repeat signups do **not** extend the countdown; they create a fresh invite to the same existing trial expiry. This prevents the obvious “keep refreshing 14 days forever” hole. Because apparently people on the internet do that sort of thing.
- Add analytics events: `demo_page_view`, `demo_signup_created`, `demo_telegram_started`, `demo_chart_generated`, `demo_upgrade_clicked`, `demo_expired`, `demo_reactivated_paid`.
- Keep `/sanctuary-demo/` out of sitemap; page includes `noindex,nofollow` and robots disallow.
- Show operators a weekly demo cohort report: signups, activated Telegram containers, chart generation, trial expiry, paid conversions, stuck onboarding.
- Add a visible “Upgrade and keep this space” CTA in the bot when a user asks about status, trial, upgrade, or expiry.
