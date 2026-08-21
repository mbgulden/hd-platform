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

## Dependencies

`hde_tenant_router.py` imports (all land in this PR unless already on `main`):
- `scripts/hde_rate_limits.py` (new)
- `scripts/hde_job_queue.py` (new)
- `scripts/hde_usage_budgets.py` (new)
- `shared/database.py` — `User`, `Invitation`, `BotInstance`, `async_session_factory` (already on `main`)
- Redis is optional at runtime — the three modules import `redis.asyncio` lazily inside functions.
