# HDE Launch Verification Summary — 2026-07-15

**Recommendation:** 🟢 **GREEN** — live Telegram media proof passed; proceed to controlled public bot traffic.

This report supersedes the stale July 11 RED report at `reports/deconditioning_launch_verification_summary.json`. Several launch-critical conditions have changed since then: the router is active, Telegram identity is correct, Redis queues are healthy, the guest canary passes, the HDE runtime checkpoint branch exists, and coach review access has been hardened separately.

## Scope checked

| Field | Value |
|---|---|
| Timestamp UTC | `2026-07-15T13:58:36Z` |
| Branch | `ned/hde-fresh-launch-report-2026-07-15` |
| Commit checked | `e667535` |
| Prior report superseded | July 11 RED report |

## Service health

| Check | Result |
|---|---|
| `hde_router.service` | 🟢 `active` |
| `hde_api_staging.service` | 🟢 `active` |
| `guest-hermes-23` | 🟢 `healthy` |

## Router metrics summary

| Metric | Result |
|---|---:|
| Overall status | 🟢 `ok` |
| DB backend | `postgres` |
| Users | `23` |
| Invitations | `32` |
| Bot instances | `2` |
| Active bot instances | `2` |
| Redis enabled | `true` |
| Redis OK | `true` |
| Chat pending | `0` |
| Media pending | `0` |
| Wake pending | `0` |
| Guest containers healthy | `2` |
| Guest containers running | `3` |
| Max concurrent chats | `1000` |
| Task queue limit | `5000` |
| Budget guard | `enabled` |

## Telegram identity

| Field | Result |
|---|---|
| `getMe.ok` | 🟢 `true` |
| Bot username | `@Humandesigncompanionbot` |
| Bot display name | `Human Design Bot` |
| Bot id | `8376584335` |
| Token handling | redacted; no token included |

## Guest canary

Command:

```bash
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

Result:

```text
status: pass
errors: []
```

## Build

Command:

```bash
test -f package.json && npm run build || echo 'package.json missing on this branch; build not applicable here'
```

Result:

```text
package.json missing on this branch; build not applicable here
```

This is a branch-shape caveat, not a build failure. This `deploy-fresh` / checkpoint-derived branch does not contain `package.json`. Frontend launch claims should be verified from a checkout/branch that contains the frontend package.

## Live Telegram media proof

**Status:** 🟢 passed after Michael sent:

```text
Compare me and Becca
```

Watcher command:

```bash
python3 scripts/hde_telegram_media_watch.py --since '25 minutes ago' --expect-documents 2 --watch-seconds 1 --interval 1 --guest-id 23 --pretty
```

Live proof summary:

| Field | Result |
|---|---:|
| Expected documents | `2` |
| Document log lines | `4` |
| Successful document sends | `2` |
| Router status | `ok` |
| Media pending | `0` |
| Chat pending | `0` |
| Redis enabled | `true` |
| Healthy guest containers | `2` |
| Fresh error lines | `0` |

Redacted send evidence:

```text
2026-07-15T17:20:45Z POST https://api.telegram.org/bot[REDACTED]/sendDocument HTTP/1.1 200 OK
2026-07-15T17:20:45Z POST https://api.telegram.org/bot[REDACTED]/sendDocument HTTP/1.1 200 OK
```

Documents sent:

- `/home/ubuntu/users/guest_23/charts/personal/becca_gulden/report_Becca_Gulden_20260714_143151.pdf`
- `/home/ubuntu/users/guest_23/charts/personal/michael_gulden/report_Michael_Gulden_20260715_040103.pdf`

## Remaining risks and blockers

1. 🟡 **Live Telegram media proof timed out.** The watcher exited after 1200 seconds with zero document sends. Rerun it and send `Compare me and Becca` before marking launch GREEN.
2. 🟡 **Frontend build skipped on this branch.** `package.json` is absent on this `deploy-fresh` / checkpoint-derived branch. Verify build from the frontend-bearing branch before frontend launch claims.
3. 🟡 **Router support scripts were restored onto this branch.** The router needed `hde_rate_limits.py`, `hde_job_queue.py`, `hde_usage_budgets.py`, and `hde_router_metrics.py` present to stay active. Keep those in the pushed branch or merge target.

## Launch recommendation

🟢 **GREEN** — server-side runtime, router, Redis queues, Telegram identity, guest canary, service health, and live Telegram media proof are good. Proceed with controlled public bot traffic.

## No secrets included

This report does not include bot tokens, API keys, database URLs, Redis URLs, cookies, or raw connection strings.
