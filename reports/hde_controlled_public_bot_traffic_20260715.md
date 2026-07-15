# HDE Controlled Public Bot Traffic — 2026-07-15

**Recommendation:** 🟢 **PROCEED** — all controlled-traffic gates are green. Start with Michael/internal testers, then 3–5 external users. Do not jump straight to broad public traffic. Tempting fate is not a rollout plan.

## Launch baseline

The fresh HDE launch report is already GREEN after live Telegram proof.

| Item | Result |
|---|---|
| Launch report | `reports/hde_launch_verification_summary_20260715.md` |
| Launch report JSON | `reports/hde_launch_verification_summary_20260715.json` |
| Latest GREEN commit | `f153b59` — `[Ned] Mark HDE launch report green after live proof (#NO-ISSUE)` |
| Live Telegram proof | `pass` |
| Successful document sends | `2` |
| Bot | `@Humandesigncompanionbot` |

## Current pre-check evidence

| Gate | Result |
|---|---|
| Branch | `ned/hde-controlled-public-traffic-2026-07-15` |
| Base commit checked | `f153b59` |
| `hde_router.service` | `active` |
| `hde_api_staging.service` | `active` |
| `guest-hermes-23` | `healthy` |
| Router metrics | `ok` |
| Redis enabled | `true` |
| Redis OK | `true` |
| Chat pending | `0` |
| Media pending | `0` |
| Wake pending | `0` |
| Chat consumers | `228` |
| Media consumers | `60` |
| Wake consumers | `76` |
| Healthy guest containers | `2` |
| Running guest containers | `3` |
| DB backend | `postgres` |
| Users | `23` |
| Invitations | `32` |
| Bot instances | `2` |
| Active bot instances | `2` |
| Guest canary | `pass`, `errors: []` |
| Fresh critical router errors, 30m | `0` |

## Telegram identity

Safe `getMe` fields only; token was not printed.

| Field | Result |
|---|---|
| ok | `true` |
| id | `8376584335` |
| username | `Humandesigncompanionbot` |
| first_name | `Human Design Bot` |

## Watchdogs and backups

| Job | ID | Enabled | Last status | Schedule | Delivery |
|---|---|---:|---|---|---|
| HDE head-bot router watchdog | `ab9ff7e5e197` | ✅ | `ok` | `every 5m` | `origin` |
| HDE Postgres daily backup | `de96b1a3f144` | ✅ | `ok` | `0 3 * * *` | `local` |
| HDE Postgres backup watchdog | `7244203a53a0` | ✅ | `ok` | `every 360m` | `origin` |

Latest backup evidence:

| Field | Result |
|---|---|
| latest backup | `hde-postgres-20260715T030008Z.dump` |
| mtime UTC | `2026-07-15T03:00:08.608511+00:00` |
| size bytes | `18555` |

## Controlled traffic posture

### Phase 0 — internal

- Michael/internal testers only.
- Exercise ordinary chat, chart recall, comparison, and document generation.
- Watch router logs and Redis pending counts during the session window.

### Phase 1 — small external cohort

- Invite **3–5 external users**.
- Keep entry points controlled; do not broadcast broadly yet.
- Require no sustained backlog, failed sends, unhealthy containers, restart loops, onboarding failures, or spend anomalies before moving forward.

### Phase 2 — broader traffic

- Only after Phase 1 completes cleanly.
- Keep watchdogs active.
- Increase traffic in small batches, not a single cliff-dive. Servers dislike drama.

## Proceed gates

Proceed only while all are true:

- [x] Router service active.
- [x] API service active.
- [x] Guest container healthy.
- [x] Router metrics `status: ok`.
- [x] Redis pending queues are `0` or clearly draining.
- [x] Telegram identity is `@Humandesigncompanionbot`.
- [x] Guest canary passes.
- [x] Launch report is GREEN.
- [x] Watchdogs/backups enabled and quiet.
- [x] No fresh critical router errors.

## Hold conditions

Hold traffic if any occur:

- Router/API service down or restart-looping.
- Guest container unhealthy.
- Redis pending backlog grows and does not drain.
- Telegram sends fail.
- Wrong Telegram identity/token appears wired.
- DB connection errors.
- Onboarding/invitation errors for test users.
- Backup watchdog reports stale/missing backups.
- Unexpected token/model spend spike.

## Rollback criteria

If controlled traffic causes instability:

1. Stop adding new users/invitations.
2. Keep existing user sessions available if safe.
3. Capture redacted router logs and router metrics.
4. Pause/disable public entry links rather than deleting data.
5. Do **not** rotate bot tokens or restart broad infrastructure without explicit approval unless the service is already down and the safe fix is narrow/documented.

## Monitoring commands

Run these during the first cohort window:

```bash
systemctl is-active hde_router.service
systemctl is-active hde_api_staging.service || true
sudo docker inspect -f '{{.State.Health.Status}}' guest-hermes-23
/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_router_metrics.py --pretty
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

Router logs with token redaction:

```bash
journalctl -u hde_router.service --since '30 minutes ago' --no-pager \
  | sed -E 's/[0-9]+:[A-Za-z0-9_-]+/[REDACTED_TOKEN]/g; s#bot[0-9]+:[A-Za-z0-9_-]+#bot[REDACTED]#g'
```

For document-generating flows, rerun the media watcher around live traffic:

```bash
/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_telegram_media_watch.py \
  --since '10 minutes ago' \
  --expect-documents 2 \
  --watch-seconds 300 \
  --interval 10 \
  --guest-id 23 \
  --pretty
```

## Remaining risks

1. **Cohort discipline.** This is green for controlled traffic, not a license to carpet-bomb the public link.
2. **Frontend build caveat.** This checkout lacks `package.json`; verify any frontend-bearing branch separately before frontend launch claims.
3. **Cost envelope.** Runtime gates are healthy, but first external users should still be watched for token/model spend spikes.
4. **Human workflow.** If users report confusion, capture examples before changing prompts. Anecdotes are logs with feelings.

## Recommendation

🟢 **PROCEED** with Phase 0 and Phase 1 controlled public bot traffic.

Do not broaden past the first 3–5 external users until the monitoring window stays clean.
