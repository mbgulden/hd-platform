# Human Design Engine Sanctuary Demo Flow

## Status model

| Status | Meaning | Bot/container behavior |
|---|---|---|
| `paid` | Normal paid Sanctuary member | Full access while `subscription_status=active` |
| `demo` | Semi-public 14-day tester | Bot access allowed until `trial_expires_at`; bot prompt receives demo context |
| `expired_demo` | Demo has ended without upgrade | Bot pauses access; workspace/container retained until `deletion_scheduled_at` |
| `deleted_demo` | Retention elapsed and demo workspace deprovision was requested | Container/workspace deprovisioned; demo PII anonymized; non-PII audit row retained |
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
→ user.demo_started_at set on first demo
→ user.demo_renewal_count only increments for invite-code renewals after expiry
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
  access_status=deleted_demo
  subscription_status=inactive
  email=deleted+demo+<user_id>@humandesignengine.local unless hard-delete policy is approved
  stripe_customer_id=NULL
  bot_instance.status=deprovisioned
  bot_instance.telegram_user_id=NULL
  invitations marked used/expired
```

Important: `deprovision` deletes the container/workspace. User PII is anonymized after the deprovision request by default (`HDE_DEMO_ANONYMIZE_PII=1`). This keeps a non-PII audit row without retaining tester email/Telegram linkage forever. Hard-delete can replace this later if compliance policy says so.

## Production gates

Blocking before broad production launch:

1. `scripts/hde_trial_lifecycle.py` must be scheduled at least daily with `HDE_TRIAL_LIFECYCLE_DRY_RUN=0`. Tracked templates live in `deploy/systemd/hde_demo_trial_lifecycle_staging.service` and `.timer`; staging timer is expected to be active.
2. One real Telegram click-through from `/sanctuary-demo/` must prove the `hde_demo_` deep link is accepted by the router.
3. One real container provisioning test must prove the demo account gets a private guide space and demo prompt context.
4. One paid-upgrade continuity test must prove the same paused/demo space wakes instead of losing continuity. Do not complete live Stripe payment without explicit approval.
5. Add Cloudflare/WAF or equivalent edge rate limiting before making the door public; in-process rate limiting is a seatbelt, not a roll cage. Staging evidence is recorded in `.runtime/demo_edge_rate_limit.json` after the Cloudflare rule is verified.
6. Reminder messaging must be implemented or explicitly deferred: day 7, day 12, expiry, and pre-deletion warning. Staging uses `scripts/hde_demo_reminders.py` plus `hde_demo_reminders_staging.timer`.

Run `scripts/hde_demo_production_gate.py` before production. It intentionally returns `BLOCKED` until live/human proof artifacts are present, while machine-checkable timer/rate-limit/reminder gates can pass from installed staging evidence.

## Nice-to-have management/governance checklist

- Customer onboarding email copy follows the “Somatic Experiment Station” style from the reference email/PDF: quiet “You’re in,” one simple next step, durable Telegram sanctuary link, and HDE sanctuary footer.
- Add admin dashboard filters for `demo`, `expired_demo`, `deletion_scheduled_at`, and `trial_expires_at`.
- Send reminder emails/messages at day 7, day 12, expiry, and 7 days before deletion.
- Add `HDE_DEMO_INVITE_CODE` in production if the page should be semi-public but gated.
- Rate-limit `/api/demo/start` by IP/email to prevent bot/container abuse. Implemented as an in-process guard (`HDE_DEMO_RATE_LIMIT_WINDOW_SECONDS`, `HDE_DEMO_RATE_LIMIT_MAX_ATTEMPTS`) and should be backed by edge/WAF limiting before production.
- Active demo repeat signups do **not** extend the countdown; they create a fresh invite to the same existing trial expiry. This prevents the obvious “keep refreshing 14 days forever” hole. Because apparently people on the internet do that sort of thing.
- Expired/deleted demo emails cannot self-serve a new 14-day demo through the public endpoint. Renewal requires a valid `HDE_DEMO_INVITE_CODE` or an admin path.
- Add analytics events: `demo_page_view`, `demo_signup_created`, `demo_telegram_started`, `demo_chart_generated`, `demo_upgrade_clicked`, `demo_expired`, `demo_reactivated_paid`.
- Keep `/sanctuary-demo/` out of sitemap; page includes `noindex,nofollow` and robots disallow.
- Show operators a weekly demo cohort report: signups, activated Telegram containers, chart generation, trial expiry, paid conversions, stuck onboarding.
- Add a visible “Upgrade and keep this space” CTA in the bot when a user asks about status, trial, upgrade, or expiry.
