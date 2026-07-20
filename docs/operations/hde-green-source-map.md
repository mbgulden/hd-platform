# HDE Green Dashboard / Report Source Map

This file tells future agents where the evidence lives for HDE green-state work.

Latest refresh: `2026-07-20T01:31:21Z`. GRO-3992 was redispatched from Backlog even though branch/PR evidence already exists; use this map to restore review state and keep the epic out of Done until production proof is green.

## Canonical repo and runtime surfaces

| Surface | Path / URL | Use |
|---|---|---|
| Canonical repo | `/home/ubuntu/work/hd-platform` | Source of truth for HDE code, docs, operations scripts, and verification helpers. |
| Staging runtime | `/home/ubuntu/work/hd-platform-staging` | VM-backed family-test/staging surface; contains runtime backups. |
| Production site | `https://humandesignengine.com/` | Canonical public surface. Production deploys require explicit permission. |
| API origin | `https://api.humandesignengine.com/` | Payment/API origin; some routes intentionally behind Cloudflare Access. |
| Reports origin | `https://reports.humandesignengine.com/` | Report delivery; public report paths must bypass Access. |

## Linear plan tree

Parent epics created 2026-07-18 in HD Engine Core:

| Epic | Category | Current source/evidence |
|---|---|---|
| GRO-3976 | North Star OKF and governance | `docs/operations/hde-green-state-rubric.md` when merged from governance branch |
| GRO-3980 | Operational file consolidation | `docs/operations/hde-stray-operational-file-inventory-2026-07-18.md` when merged from governance branch |
| GRO-3986 | Google authentication via Kai and registration | `docs/operations/hde-google-auth-via-kai-2026-07-18.md` when merged from governance branch |
| GRO-3992 | Site-wide analytics and conversion instrumentation | `docs/operations/hde-analytics-instrumentation-epic-3992.md` |
| GRO-3998 | SEO/index hygiene cleanup | Pending child proof |
| GRO-4004 | Security, performance, and operational reliability | Pending child proof |
| GRO-4010 | North Star daily work product progression | Pending child proof |

## Analytics/conversion child branches

| Child | Branch / PR | Purpose |
|---|---|---|
| GRO-3993 | `ned/GRO-3993` / PR #23 | Install canonical GA4/GTM loader; Linear currently Backlog/`dispatch:ready` |
| GRO-3994 | `ned/GRO-3994` / PR #22 | Instrument checkout funnel events; Linear currently Backlog/`dispatch:ready` |
| GRO-3995 | `ned/GRO-3995` / PR #21 | Instrument free-reading and Sanctuary daily-work events; Linear currently Backlog/`dispatch:ready` + human review |
| GRO-3996 | `feature/gro-3996` | Add analytics assertions to PWP proof; Linear currently Backlog/`dispatch:ready` + human review |
| GRO-3997 | `ned/GRO-3997` / PR #20 | Live production analytics coverage verifier; Linear currently Done while PR remains open |

## Local verification commands

```bash
python3 -m py_compile scripts/operations/*.py
python3 scripts/operations/hde_operational_file_inventory.py --limit 5000
npm run build
PWP_STAGING_URL=https://humandesignengine.com npm run pwp:verify
node scripts/live-analytics-coverage.mjs --base-url https://humandesignengine.com --require-ok
```

## Known proof artifacts

| Artifact | Meaning |
|---|---|
| `okf/output/pwp-visual-qa/` | Local PWP Lighthouse/screenshots/link proof from the worktree where verification ran. |
| `/tmp/hde_ops_inventory.json` | First-pass stray operational file inventory generated 2026-07-18. Runtime temp, summarized in docs. |
| `/tmp/hde_green_plan_linear_result.json` | Linear tree creation verification result. Runtime temp, not canonical. |
| `docs/operations/hde-analytics-instrumentation-epic-3992.md` | Current analytics epic status, blockers, and green gates. |
| `docs/operations/hde-stray-operational-file-inventory-2026-07-18.md` | Canonical summary of stray operational file candidates when merged. |
| `docs/operations/hde-launch-audit-2026-07-18.md` | Canonical launch audit summary when merged. |
| `docs/operations/hde-google-auth-via-kai-2026-07-18.md` | Canonical Google auth/Kai evidence and next steps when merged. |

## Green report process

1. Run source-map checks above.
2. Query Linear epics and child state counts.
3. Run production route/tag crawl.
4. Run PWP proof with production URL.
5. Run live-safe checkout smoke; never complete payment.
6. Query GA/GTM/GSC only with authorized OAuth/admin credentials.
7. Publish a green report only when every category in `hde-green-state-rubric.md` is green.
