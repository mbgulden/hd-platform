# HDE Workspace Cleanup — 2026-07-15

**Status:** ✅ cleaned and documented
**Repo:** `/home/ubuntu/work/hd-platform-staging`
**Branch:** `ned/hde-fresh-launch-report-2026-07-15`
**Head before cleanup report:** `57fba43`

## What this cleanup was for

Make the Human Design Engine staging workspace understandable again after the launch-runtime, coach-gate, and launch-report work. The target state is simple:

- one active HDE staging worktree,
- no secret backups or generated caches sitting in the repo root,
- local branches only for currently relevant work,
- remote review branches preserved,
- docs/reports point people to the right places for app, bot, runtime, launch, and coach-review behavior.

## Execution plan

1. Inventory repo status, local branches, remote branches, worktrees, and untracked artifact sizes.
2. Classify artifacts before deleting anything.
3. Archive ambiguous or useful generated artifacts outside the repo.
4. Move secret-bearing `.env` backups to a private archive without printing values.
5. Remove only reproducible cache (`node_modules/`) from the repo worktree.
6. Delete only local branches that were superseded or already integrated into the current pushed report branch.
7. Leave remote review branches intact.
8. Record the HDE workflow map so the next person knows where to look.

## Archive location

```text
/home/ubuntu/work/_hde_cleanup_archive/20260715T141148Z
```

Archive manifest:

```text
/home/ubuntu/work/_hde_cleanup_archive/20260715T141148Z/manifest.txt
```

## Cleaned artifacts

| Path | Action | Why |
|---|---|---|
| `.env.bak-20260712T213223Z` | moved to private archive | secret-bearing env backup; not repo material |
| `.env.pre-token-rotation-20260712T215915Z.bak` | moved to private archive | secret-bearing env backup; not repo material |
| `docker/data/` | archived outside repo | runtime Redis/state data |
| `.astro/` | archived outside repo | generated local build/cache state |
| `staging_database.db` | archived outside repo | runtime database artifact |
| `docs/podcast/` | archived outside repo | unrelated product media/docs; not part of HDE launch workflow checkpoint |
| `tests/` | archived outside repo | untracked local/generated test artifacts |
| `reports/deconditioning_launch_verification_summary.json` | archived outside repo | stale July 11 RED report, superseded by fresh July 15 report |
| `node_modules/` | removed | reproducible dependency cache, 122 MB |

## Branch cleanup

### Local branches removed

| Branch | Reason |
|---|---|
| `ned/hde-staging-runtime-checkpoint-2026-07-15` | stale local-only checkpoint; superseded by pushed fresh checkpoint; bundle preserved |
| `ned/hde-staging-runtime-checkpoint-2026-07-15-fresh` | pushed and integrated into current launch-report branch |
| `ned/hde-coach-review-consent-gate-2026-07-15` | pushed and integrated into current launch-report branch |

### Local branches retained

| Branch | Purpose |
|---|---|
| `ned/hde-fresh-launch-report-2026-07-15` | current branch; contains runtime checkpoint, coach gate, launch report, and cleanup report |
| `staging` | existing local staging branch |
| `feature/fred-hde-stripe-staging-gro3792` | existing Fred Stripe staging branch; not Ned-owned cleanup target |

### Remote review branches retained

Remote branches were **not** deleted:

- `origin/ned/hde-staging-runtime-checkpoint-2026-07-15-fresh`
- `origin/ned/hde-coach-review-consent-gate-2026-07-15`
- `origin/ned/hde-fresh-launch-report-2026-07-15`

Good. Remote review history stays findable. Local clutter gets out of the way.

## HDE workflow map

### Launch / verification

- Fresh launch report: [`reports/hde_launch_verification_summary_20260715.md`](reports/hde_launch_verification_summary_20260715.md)
- Machine-readable launch evidence: [`reports/hde_launch_verification_summary_20260715.json`](reports/hde_launch_verification_summary_20260715.json)
- This cleanup report: [`reports/hde_workspace_cleanup_20260715.md`](reports/hde_workspace_cleanup_20260715.md)

### Human Design bot / runtime operations

- Head-bot scaling and operations runbook: [`docs/hde-head-bot-scaling-runbook.md`](docs/hde-head-bot-scaling-runbook.md)
- Guide/deconditioning runtime workflow: [`docs/hd-engine/guide-deconditioning-runtime-workflow.md`](docs/hd-engine/guide-deconditioning-runtime-workflow.md)

### Router and queue runtime

- Telegram router: [`scripts/hde_tenant_router.py`](scripts/hde_tenant_router.py)
- Router metrics: [`scripts/hde_router_metrics.py`](scripts/hde_router_metrics.py)
- Job queues: [`scripts/hde_job_queue.py`](scripts/hde_job_queue.py)
- Rate limits: [`scripts/hde_rate_limits.py`](scripts/hde_rate_limits.py)
- Usage budgets: [`scripts/hde_usage_budgets.py`](scripts/hde_usage_budgets.py)

### Proof / canary tools

- Guest runtime canary: [`scripts/hde_guest_canary.py`](scripts/hde_guest_canary.py)
- Telegram media proof watcher: [`scripts/hde_telegram_media_watch.py`](scripts/hde_telegram_media_watch.py)
- Guest canary watchdog wrapper: [`scripts/hde_guest_canary_watchdog.sh`](scripts/hde_guest_canary_watchdog.sh)

### Coach dashboard gate

- Coach review and update-step API gate: [`scripts/vm_orchestrator.py`](scripts/vm_orchestrator.py)
- Consent rule: coach token alone is not enough; review/update paths must require active premium status, consent, no revocation, and non-expired coaching window before workspace read/write.

## Current launch status after cleanup

- Server-side HDE runtime evidence is healthy in the fresh launch report.
- Launch remains 🟡 **YELLOW** until live Telegram media proof completes.
- Watcher session `proc_3e448aceea09` later timed out with 0 document sends; rerun it before marking launch GREEN.
- Required live prompt remains:

```text
Compare me and Becca
```

Bot:

```text
@Humandesigncompanionbot
```

## Safety notes

- No `.env` files were committed.
- No database dumps, Redis dumps, or runtime customer data were committed.
- Secret values were not printed in this report.
- Ambiguous artifacts were archived, not silently destroyed.
- Remote branches were retained for review.
