# HDE Tenant Router — Runtime Reference

Canonical location: `scripts/hde_tenant_router.py` (this file first lands on `main` via this PR; it previously lived only on the staging line `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`).

The tenant router is the Telegram message proxy for the HDE guest-fleet runtime: it resolves a chat → `bot_instances` row → guest container URL and forwards user turns to the guest `hermes -z` LLM process.

## Timeout chain (why the numbers are what they are)

The guest containers run a ~27B local model that can take **60–120s/turn** under GPU contention (14k-token guest prompts). The old hardcoded `35.0` in the router's `client.post(..., timeout=...)` aborted every real turn with "took too long".

| Layer | Knobs | Default | Note |
|---|---|---|---|
| Router → guest POST | `HDE_GUEST_TURN_TIMEOUT_SECONDS` | `180` | Must exceed worst-case guest turn. Added in this PR (GRO-4824 item 3, timeout alignment). |
| Router chat cap | `HDE_ROUTER_CHAT_TIMEOUT_SECONDS` | `45` | Per-chat activity cap, not per-LLM-turn. |
| Guest `hermes -z` | `timeout=120` in `guest_agent_server.py` | 120 | Must be < router POST timeout (180). |

Invariant: **guest hermes cap (120) < router POST cap (180)**. If you lower the router cap, lower the guest cap first.

## Other runtime knobs

| Env var | Default | Purpose |
|---|---|---|
| `HDE_ONBOARDING_BOT_USERNAME` | `Humandesigncompanionbot` | Bot identity advertised during onboarding (was `HDE_CoachBot`). |
| `HDE_ORCHESTRATOR_SHARED_SECRET` | `default_shared_secret` | HMAC secret for orchestrator calls — **set a real value in prod**. |
| `HDE_ROUTER_MAX_CONCURRENT_CHATS` | `1000` | Semaphore size for concurrent chats. |
| `HDE_ROUTER_TASK_QUEUE_LIMIT` | `5000` | Bounded task queue size. |
| `DEFAULT_HOST_NODE_IP` | `127.0.0.1` | Base host for `ORCHESTRATOR_URL` (`:8001`). |

## Behavior notes

- **Welcome rotation**: `guide_choice_prompt(chat_id)` draws from a 4-entry pool and never repeats the same opener back-to-back for a given chat (`_WELCOME_LAST` dict, in-memory).
- **Guide-ready message** now asks for a preferred name + optional birth details (date/time/place) to build the chart immediately.
- **Beta testing note**: the staging test consent message names Michael (human) and Ned (AI) reviewers.

## Rebind guard (GRO-4823)

A Telegram chat binds to exactly one HDE account via `bot_instances.telegram_user_id`. The old claim path
(`process_start_token`) *silently stole* that binding when a different account signed in from the same phone: it
NULLed the prior row and rebound to the new user with no check on who the prior owner was. That left the owner's
phone bound to a 14-day demo, so every reply came from the demo's seeded chart (GRO-4823).

The decision now lives in `scripts/hde_rebind_guard.py` (stdlib-only, unit-tested in `tests/test_rebind_guard.py`):

| Prior owner | New sign-in | Outcome |
|---|---|---|
| unbound (no prior row) | any | allow (first bind) |
| same user | any | allow (self re-claim) |
| **protected** (`access_status == "paid"`, or `is_premium`) | different user | **refuse** — ERROR log `REBIND REFUSED`, prior owner untouched, user told the phone is already linked |
| non-protected (demo / expired_demo / inactive) | different user | allow, but WARNING log `REBIND ALERT` with before/after identity |

Schema backstop: `ix_bot_instances_telegram_user_id` is a **unique** index (Postgres treats NULLs as distinct, so
unbound rows never collide) — it enforces at-most-one *live* binding per chat. The guard covers the one case that
constraint cannot catch: an *intentional* NULL-then-rebind sequence. No DDL was added for this fix; the index
already exists on `main` and in prod (verified 2026-08-21).

Log lines are PII-safe: they carry user ids + `access_status`/`is_premium` only — never email or phone.

## Dependencies

`hde_tenant_router.py` imports (all land in this PR unless already on `main`):
- `scripts/hde_rate_limits.py` (new)
- `scripts/hde_job_queue.py` (new)
- `scripts/hde_usage_budgets.py` (new)
- `shared/database.py` — `User`, `Invitation`, `BotInstance`, `async_session_factory` (already on `main`)
- Redis is optional at runtime — the three modules import `redis.asyncio` lazily inside functions.
