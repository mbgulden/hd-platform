# HDE Human Design Companion head-bot scaling runbook

Date: 2026-07-12

## Current head-bot identity

The HDE public Telegram head bot is:

- Display name: Human Design Companion
- Username: `@Humandesigncompanionbot`
- Token source: `HDE_COACH_BOT_TOKEN` in the staging service environment

Never commit the token. Rotate it if it has been pasted into any durable chat, issue, or log.

## Message flow

```text
Telegram head bot
  -> hde_tenant_router.py
  -> shared DB lookup by telegram_user_id
  -> per-user BotInstance
  -> guest Hermes container /api/message
  -> Telegram reply
```

The head bot stays shared. Each user gets a private account/session/container and a stored guide persona.

## Personal guide naming and first-contact voice

On first `/start <token>`, the router links the paid invitation to the Telegram chat, then asks for one simple working handle in embodied language instead of showing a rigid menu or explaining the product philosophy. Example shape:

```text
✨ Welcome in.

This is a quiet room for real work — no performance required.

What simple name should this space answer to? A custom guide name is perfectly fine.
```

The selected name is stored on `users.guide_name` with `users.guide_name_source` and is sent to the VM orchestrator during provisioning so the guest soul prompt can use that handle inside the private chat.

Telegram will still show the global BotFather display name. The per-user guide name is implemented inside chat copy/persona, not as a unique Telegram bot identity per user.

Guest first contact must follow “show, don’t tell”: do not recite the hard rules, menus, or philosophy to the user. The Soul carries those rules so MiniMax can embody them naturally. Greetings get one warm sentence plus one invitation; birth details are collected only when the guest asks for chart work, and then one field at a time using American-facing dates (`MM/DD/YYYY` or natural language) while converting to ISO only for internal tool calls. Birth-date intake must accept a wide natural net including American numeric dates, ISO for backwards compatibility, month-first English (`June 14, 1990`), and day-first English (`14 June 1990`, including ordinal suffixes like `14th June 1990`). Birth-time intake must keep a wide acceptance net: exact times, unknown, broad dayparts, and calculable natural-light phrases like “around sunrise,” “dawn,” “before sunrise,” “sunset,” or “dusk” should move forward to location collection; once date and place are known, the guest server resolves sunrise/sunset-style phrases to a local HH:MM approximation instead of rejecting the user. Progressive chart prompts and retry prompts should rotate so the guide does not repeat the same line across adjacent turns. `/new`/reset and simple greetings are guarded in the guest server with rotating first-impression prompts so the guide does not recycle the same opening line; prefer simple this/that choices for the first touch because most guests will be Generator/MG sacral-response types, while still staying usable for non-generators.

The guest runtime should now be **LLM-first**, with deterministic code used only for tool/action rails that must actually mutate state or call chart generation. Avoid static menu/help/profile scripts in front of MiniMax; those made the live chat rigid and painful. Keep rails for: journal persistence, chart generation when date/time/place are provided, comparison PDF metadata, durable profile storage, search execution, and media delivery. Personal chart correction should accept a natural one-shot message such as “No, it should be 12/10/1989 at 3:10 PM in Simi Valley, CA,” update/delete the bad generic `my_human_design` profile when appropriate, store the corrected profile under the real person, and generate the chart without forcing a wizard loop. The runtime prompt should use a permission architecture, not a bigger cage: **Constitution** (never fabricate, fake certainty, override body authority, coerce, leak private data, or claim medical/legal/financial authority), **Culture** (Sanctuary voice, warm/direct/not syrupy, one clean question by default, no menu wall/fake intimacy), **Freedoms** (improvise, synthesize, reframe, take the swing when invited, use metaphor, offer experiments, choose the next useful move), and **Tool policy** (the guide narrates; server owns mutations and artifacts). Broad pattern questions such as “what am I missing?” should trigger a real pattern read rather than a setup question, using uncertainty etiquette like “my strongest read is” or “working hypothesis, not verdict.” The guide’s creative tools should be named and described in the runtime prompt so they act like internal handles, not vague vibes: `pattern_read`, `experiment_builder`, `authority_check`, `relationship_mirror`, `time_rectification_explorer`, `thread_memory`, `ritual_or_practice_builder`, and `polyvagal_state_check`. They are prompt-native reasoning moves unless/until a deterministic backend action is required. Polyvagal cues are also part of the journey, not just loading-screen filler: the router uses the somatic cue library while containers wake, and the guide may weave the same micro-practices into replies after lightly reading activation (`sympathetic` wired/urgent/angry), heaviness (`dorsal` numb/frozen/tired), or steadiness (`ventral` clear/curious/grounded). Treat that as a working read, never a diagnosis; offer one simple orientation/breath/body practice, not woo sludge. The first series of conversations should make the purpose clear without turning into a lecture: the guide should explain once that these are optional nervous-system micro-practices used for waiting, activation, heaviness, or authority checks, and ask whether the user wants them woven in lightly or kept practical. If the user declines or ignores the cue, stop offering exercises unless asked. If birth time is missing, the guide must not silently treat `12:00` as better data. The guest should offer three clean paths: explore likely time windows with chart-pattern anchors, build a clearly labeled unknown-time/rough chart, or wait for exact records. Static chart intake should continue shrinking into a slot clipboard: if the user’s initial chart request already includes date/time/location/name, extract and validate those slots, ask only for what is missing, and let the deterministic chart tool execute once required slots are present. If a stored profile already has complete birth details and the user asks to build/rebuild/generate that chart, the guide should operate the system and generate it instead of asking “use those details?” Single-field edits should follow the same rule: if the user gives a corrected date/time/location and the profile has enough slots, persist the edit and rebuild the chart immediately instead of asking “want me to rebuild?” Stored relationship asks such as “compare me and Becca” should do the same: resolve named stored profiles from the people index, use both complete profiles, regenerate missing chart summaries if needed, compare them, and return plural PDFs instead of making the user say “rebuild.” The resolver should not be hardcoded to one couple; requests like “compare Canary Guest and Canary Friend” should use existing stored profiles without restarting Person 1/Person 2 intake. Store birth-field confidence (`exact`, `natural-clue`, `approximate`, `explored`, or `unknown-placeholder`) with the person profile so later readings can calibrate certainty instead of sounding falsely precise. Each generated chart writes `chart_data.json`, `coach_manifest.json`, a durable people profile with `birth_input`, and a latest chart snapshot for backend/coach review; comparison still needs plural `pdf_paths`. Coach-visible continuity events are appended to `/workspace/coach_view/events.jsonl` for chart generation and journal entries.

## Reusable guest workflow canary

Use [`scripts/hde_guest_canary.py`](https://prismatic.growthwebdev.com/workspace-tree?file=scripts/hde_guest_canary.py) for repeatable server-side checks while live Telegram testing is in progress:

```bash
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

The canary exercises the private guest `/api/message` path without Telegram: greeting rotation, progressive personal chart intake, `14 June 1990`, `around sunrise`, strict first-and-last-name capture so random phrases after `for`/`under` do not become fake profiles, richer chart insight output beyond anchor facts, per-person memory, continuity lookup for “Do you remember?” against saved journal plus retained session history, natural single-field edits like `Canary Guest birth time is 7:45 AM`, workflow navigation (`what can you do?`, `what now?`, `explain my chart`), journal write/search, comparison multi-PDF metadata, and the guide permission-architecture contract. The contract check guards the Constitution/Culture/Freedoms split, permission-to-improvise clause, take-the-swing mode, uncertainty etiquette, consentful depth, Graceful Deconditioning + Belief Work, graduation bias toward needing the guide less, no hardcoded guide name, and prompt-native creative tools so future edits do not quietly turn the genie back into a wizard. It backs up and restores `/workspace/people/index.json`, removes canary chart/person folders, clears transient state, and deletes canary journal rows so live guest context is not poisoned. Passing this canary is **focused ad-hoc guest-runtime verification**, not full Telegram proof; the live Telegram media canary still needs a real user message because bots cannot send themselves Telegram updates.

See [`docs/hd-engine/guide-deconditioning-runtime-workflow.md`](https://prismatic.growthwebdev.com/workspace-tree?file=docs/hd-engine/guide-deconditioning-runtime-workflow.md) for the consolidated humandesignengine.com operating reference covering the guide-neutral deconditioning runtime, OKF source map, Telegram/HDE infrastructure, and verification workflow.

Use [`scripts/hde_guest_canary_watchdog.sh`](https://prismatic.growthwebdev.com/workspace-tree?file=scripts/hde_guest_canary_watchdog.sh) for cron/no-agent watchdog mode. It prints nothing on success and emits a concise alert only when the canary fails.

For live Telegram media proof, start [`scripts/hde_telegram_media_watch.py`](https://prismatic.growthwebdev.com/workspace-tree?file=scripts/hde_telegram_media_watch.py) before the tester sends a comparison canary:

```bash
python3 scripts/hde_telegram_media_watch.py --since now --expect-documents 2 --watch-seconds 1200 --pretty
```

Then the tester completes the comparison flow in Telegram. The watcher passes only when router logs show at least two successful document uploads, Redis chat/media pending counts are zero, router metrics are healthy, and no recent router error lines appear. It redacts token-shaped strings in log snippets.

## Coach review consent gate

Coach dashboard APIs must not treat the coach token as sufficient authority to read or mutate client workspaces. `/api/coach/clients`, `/api/coach/review`, and `/api/coach/update_steps` gate access to active premium users with `coach_review_consent=true`, `coach_review_consent_revoked_at is null`, and a non-expired coaching window when `coaching_container_end` is set. The review/update endpoints run this database eligibility check before resolving or reading any `/home/ubuntu/users/...` workspace path.

## Current router backpressure controls

Environment knobs:

| Variable | Default | Purpose |
|---|---:|---|
| `HDE_ROUTER_MAX_CONCURRENT_CHATS` | `1000` | Max in-flight onboarding/chat tasks |
| `HDE_ROUTER_TASK_QUEUE_LIMIT` | `5000` | Drop-protection ceiling for pending tasks |
| `HDE_ROUTER_CHAT_TIMEOUT_SECONDS` | `45` | Per-task timeout before releasing a slot |

The router uses an asyncio semaphore, bounded task queue, HTTP connection pool sized for high fan-in, and a token-bucket rate limiter. When `HDE_REDIS_URL` or `REDIS_URL` is configured, rate buckets are shared through Redis across router processes; otherwise staging falls back to process-local memory. This protects the process from unbounded task explosion during bursts and gives production a horizontal-scaling boundary.

Current staging values:

```text
HDE_REDIS_URL=redis://127.0.0.1:6379/0
HDE_ROUTER_PER_USER_MESSAGES_PER_MINUTE=12
HDE_ROUTER_GLOBAL_MESSAGES_PER_SECOND=150
HDE_ROUTER_MAX_CONCURRENT_CHATS=1000
HDE_ROUTER_TASK_QUEUE_LIMIT=5000
HDE_ROUTER_CHAT_TIMEOUT_SECONDS=45
```

A user who exceeds their per-minute bucket gets a short “one breath” retry message instead of silently piling up model calls.

## Durable Redis job queue

The router now keeps Telegram polling thin and pushes heavy work into a Redis Stream queue when `HDE_ROUTER_USE_REDIS_QUEUE=true`:

```text
Telegram getUpdates
  -> rate-limit check
  -> XADD hde:router:jobs
  -> hde-router consumer group workers
  -> onboarding / guide choice / guest chat forwarding
```

Current staging queue values:

```text
HDE_ROUTER_USE_REDIS_QUEUE=true
HDE_ROUTER_CHAT_JOB_STREAM=hde:router:chat-jobs
HDE_ROUTER_CHAT_JOB_WORKERS=12
HDE_ROUTER_CHAT_JOB_BATCH_SIZE=25
HDE_ROUTER_WAKE_JOB_STREAM=hde:router:wake-jobs
HDE_ROUTER_WAKE_JOB_WORKERS=4
HDE_ROUTER_WAKE_JOB_BATCH_SIZE=10
HDE_ROUTER_JOB_GROUP=hde-router
HDE_ROUTER_JOB_STREAM_MAXLEN=100000
HDE_ROUTER_JOB_IDLE_RECLAIM_MS=60000
```

Why this matters:

- Telegram polling no longer waits for slow guest containers.
- Normal chat jobs are isolated from onboarding/provision work.
- Onboarding/wake jobs have their own worker pool and cannot starve chat delivery.
- Jobs survive router restarts until acked.
- Redis consumer groups let multiple router/worker processes share work later.
- Idle pending jobs can be reclaimed if a worker dies mid-message.

Current split:

| Stream | Purpose | Workers |
|---|---|---:|
| `hde:router:chat-jobs` | normal message routing / guide-name replies | 12 |
| `hde:router:wake-jobs` | `/start` onboarding and provisioning handoff | 4 |
| `hde:router:media-jobs` | Telegram image/PDF uploads from guest containers | 4 |

Chart images and PDF uploads are queued as `media` jobs after the text reply is sent. That keeps chat workers from sitting on Telegram file upload latency.

## Wake-on-chat extraction

When a user messages while their guest container is stopped/suspended/provisioning, the router now:

1. marks the bot instance `waking`,
2. replies with a calm wake message immediately,
3. enqueues a `wake` job on `hde:router:wake-jobs`,
4. lets the wake worker start the container,
5. marks the instance `active`, then
6. re-enqueues the original user message onto `hde:router:chat-jobs`.

That keeps chat workers from sitting on container startup latency. A second user message during wake gets a short “still waking your space” response instead of spawning duplicate wakeups.

## Model/token budget guard

The router now reserves an estimated token cost before forwarding each guest chat turn to a container. Onboarding, guide-name selection, and wake/status messages are not charged; only messages that are about to reach the model path reserve budget.

Current staging defaults:

```text
HDE_BUDGET_ENABLED=true
HDE_BUDGET_CHARS_PER_TOKEN=4
HDE_BUDGET_ESTIMATED_OUTPUT_TOKENS=900
HDE_BUDGET_STANDARD_MONTHLY_TOKENS=450000
HDE_BUDGET_PREMIUM_MONTHLY_TOKENS=1500000
HDE_BUDGET_STANDARD_DAILY_TOKENS=90000
HDE_BUDGET_PREMIUM_DAILY_TOKENS=250000
HDE_BUDGET_GLOBAL_DAILY_TOKENS=2000000
```

This is intentionally conservative because exact downstream MiniMax token accounting is still inside the guest profile/container. When a guest response includes `usage`, `token_usage`, or `model_usage` metadata with `total_tokens` or input/output token counts, the router reconciles the reservation to actual provider usage. Guest agent server templates now emit standardized `usage` and `model_usage` fields on every `/api/message` response, using conservative local token estimates until the Hermes/provider CLI exposes exact MiniMax accounting.

Blocked turns receive a calm limit message instead of making a model call. Rejected turns are rolled back so failed reservations do not consume the user's remaining allowance.

## SQLite to Postgres production move

SQLite is acceptable for staging and early testing. Current staging metadata has been cut over to local self-hosted Postgres on `127.0.0.1:5432/hde`; the SQLite file remains as the preserved source/rollback reference.

Recommended steps:

1. Provision managed Postgres or a local HA Postgres service.
2. Install/confirm `asyncpg` in the service venv.
3. Run a non-production shadow migration first:
   ```bash
   SOURCE_URL="sqlite+aiosqlite:////home/ubuntu/work/hd-platform-staging/staging_database.db"
   EXPORT=/tmp/hde-metadata-export.json
   PYTHONPATH=/home/ubuntu/work/hd-platform-staging \
     /home/ubuntu/work/hd-platform/.venv/bin/python3 \
     scripts/hde_postgres_migration.py export --source-url "$SOURCE_URL" --output "$EXPORT"
   PYTHONPATH=/home/ubuntu/work/hd-platform-staging \
     /home/ubuntu/work/hd-platform/.venv/bin/python3 \
     scripts/hde_postgres_migration.py import --target-url "$POSTGRES_DATABASE_URL" --input "$EXPORT" --replace-target
   PYTHONPATH=/home/ubuntu/work/hd-platform-staging \
     /home/ubuntu/work/hd-platform/.venv/bin/python3 \
     scripts/hde_postgres_migration.py verify --source-url "$SOURCE_URL" --target-url "$POSTGRES_DATABASE_URL"
   ```
4. Add the production `DATABASE_URL=postgresql+asyncpg://...` only in service environment files, never in Git.
5. Restart these against the same Postgres URL:
   - `hde-api.service`
   - `hde_api_staging.service` / production equivalent
   - `hde_router.service`
   - `hde_orchestrator.service`
6. Smoke-test:
   - `select 1`
   - active user count
   - unused invitation lookup
   - `/api/checkout/session` deep link
   - Telegram `/start <token>`
7. Only then cut traffic.

Latest local cutover: PostgreSQL 16 is installed as a system service, listening only on localhost (`127.0.0.1`/`::1`) with database `hde` and app role `hde_app`. The guarded cutover migrated current staging metadata into Postgres and verified row parity: `users=23`, `invitations=32`, `bot_instances=1`, `api_keys=0`, `usage_logs=0`, `mismatches={}`. The HDE `.env` was backed up before `DATABASE_URL` was changed to the local Postgres target, and `hde_api_staging.service`, `hde_router.service`, and `hde_orchestrator_staging.service` were restarted successfully.

Backups: `/home/ubuntu/.hermes/profiles/ned/scripts/hde_postgres_backup.py` writes custom-format `pg_dump` files under `/home/ubuntu/backups/hde-postgres/`, retains 30 days, and has a restore verifier that recreates a temporary DB and counts the HDE metadata tables. Cron jobs: `HDE Postgres daily backup` (`de96b1a3f144`, local delivery via `hde_postgres_backup_daily.py`) and `HDE Postgres backup watchdog` (`7244203a53a0`, Telegram warnings only when stale/missing via `hde_postgres_backup_watchdog.py`).

Post-cutover smoke passed: DB counts present, `/api/checkout/session` produced a deep link for `Humandesigncompanionbot`, Telegram `getMe` safe fields returned ok, services were active, metrics reported `database.backend=postgres`, Redis queues had `pending=0`, and both 1000-user queue-only and mock guest HTTP load harnesses passed. Live canary follow-up fixed onboarding defects: repeated `/start` from a Telegram account previously linked to another test user now reassigns the chat ID instead of raising a duplicate-key “Database connection issue”; guest soul files are written into the per-container compose directory so `/home/pn/.hermes/SOUL.md` is a real Human Design Engine Sanctuary file instead of a Docker-created directory that makes Hermes fall back to the stock persona; the staging router uses `ORCHESTRATOR_URL=http://127.0.0.1:8011` so provisioning hits the staging orchestrator, not the older port-8001 service. Product voice guardrails now frame the product as Human Design Engine Sanctuary — not a fake companion or validation loop — and accept a user-provided working handle such as a custom guide name without identity resistance. Greetings stay low-pressure and do not ask for birth date/time/location unless the user explicitly requests a chart, reading, report, or calculation.

Cutover helper:

```bash
# Dry-run preflight; prints redacted URLs only.
POSTGRES_DATABASE_URL="postgresql+asyncpg://..." \
PYTHONPATH=/home/ubuntu/work/hd-platform-staging \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_postgres_cutover.py --migrate --replace-target --update-env --restart-services

# Real cutover, only after a confirmed maintenance/smoke-test window.
POSTGRES_DATABASE_URL="postgresql+asyncpg://..." \
PYTHONPATH=/home/ubuntu/work/hd-platform-staging \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_postgres_cutover.py --migrate --replace-target --update-env --restart-services --apply
```

The helper refuses non-`postgresql+asyncpg://` targets, redacts connection strings, creates an env backup before writing `DATABASE_URL`, and restarts only the named services when `--apply` is present.

Post-cutover smoke helper:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_postgres_smoke.py --expected-bot Humandesigncompanionbot
```

This smoke test verifies DB `select 1`, user/invitation/bot-instance counts, checkout deep-link generation through `hde_api_staging.service`, expected head-bot username in the deep link, optional safe Telegram `getMe`, and active service states. It prints only safe bot fields and redacted database URLs.

## Queue/rate-control policy for 1000 active users

Minimum production controls:

| Layer | Control |
|---|---|
| Telegram router | async semaphore + bounded queue |
| Per-user fairness | one active model request per user, later messages coalesced or queued |
| Global model budget | Redis-backed global daily token budget |
| Subscription budget | Redis-backed monthly/daily per-user estimated token cap by tier |
| Container wakeups | separate wake queue, capped concurrency |
| Media uploads | separate media queue for images/PDFs |
| Retry storms | exponential backoff; do not retry every user at once |
| Observability | `scripts/hde_router_metrics.py`, p95/p99 load harness, queue depth, DB/container health, rate/budget counters |

Current durable queue boundary is Redis Streams with split chat, wake/provision, and media-upload lanes. The load harness exercises these lanes with isolated Redis streams before any live traffic test.

Run synthetic 1000-user queue proof:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_load_harness.py --users 1000 --messages-per-user 1
```

Run mock guest HTTP proof with local `/api/message` responses, usage metadata reconciliation, wake jobs, and media jobs:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_load_harness.py --users 1000 --messages-per-user 1 --mock-guest-http --guest-ms 25
```

This does not call Telegram, MiniMax, or real guest containers; it proves the durable queue boundary drains burst fan-in and guest-response usage metadata under controlled latency without touching live users.

Router metrics snapshot:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_router_metrics.py --pretty
```

Prometheus text format:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_router_metrics.py --format prometheus
```

Current snapshot reports DB backend/counts, Redis queue length/pending/consumers, rate/budget key counts, and running/healthy guest containers without printing secrets.

## MiniMax capacity planning

Official MiniMax docs observed 2026-07-12:

- Token Plan: Plus $20/mo, Max $50/mo, Ultra $120/mo.
- Token Plan docs describe rolling 5-hour and weekly quota windows; they publish agent-usage guidance rather than exact monthly token quantities: Plus 3-4 agents, Max 4-5 agents, Ultra 6-7 agents.
- Pay-as-you-go LLM pricing:
  - MiniMax-M3 <=512k input: $0.30/M input, $1.20/M output after permanent 50% discount.
  - MiniMax-M3 >512k input: $0.60/M input, $2.40/M output after discount.
  - MiniMax-M2.7: $0.30/M input, $1.20/M output.
  - MiniMax-M2.7-highspeed: $0.60/M input, $2.40/M output.
- Third-party pricing snapshots list M2 around $0.255/M input and $1.02/M output; verify before production billing.
- Public search snapshots list M2.5 standard around $0.15/M input and $1.20/M output; verify in the MiniMax console/API docs before committing pricing.

### Estimated turns/month by plan

Assumption: one normal HDE chat turn is about 3k input + 700 output tokens.

| Model/rate | Cost/turn | $20 Plus | $50 Max | $120 Ultra |
|---|---:|---:|---:|---:|
| M3 / M2.7 standard | $0.00174 | 11,494 | 28,735 | 68,965 |
| M2.5 standard estimate | $0.00129 | 15,503 | 38,759 | 93,023 |
| M2 estimate | $0.00148 | 13,522 | 33,806 | 81,135 |
| M2.7 highspeed | $0.00348 | 5,747 | 14,367 | 34,482 |

At 100 turns/user/month, the current $50 plan roughly covers:

| Model/rate | Users at 100 turns/mo |
|---|---:|
| M3 / M2.7 standard | 287 |
| M2.5 standard estimate | 387 |
| M2 estimate | 338 |
| M2.7 highspeed | 143 |

For 1000 active users at 100 turns/month, expect ~100k turns/month. At normal-turn M3 pricing, that is about $174/month in pure pay-as-you-go equivalent, before caching and retries. Ultra $120 may be close if actual usage is lighter or caching is effective; otherwise use credits/paid overflow and per-user caps.

## Practical launch recommendation

- Keep $50 Max until ~200-300 normal active users.
- Move to Ultra or add credits when sustained monthly turns exceed ~25k-30k.
- For 1000 active chatters, budget for Ultra plus overflow credits, or design product tiers that include message caps.
- Add prompt caching and short context summaries before scaling marketing spend.
