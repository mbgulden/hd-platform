# HDE Operational File Consolidation Epic — GRO-3980

Status snapshot for the Human Design Engine operational file consolidation epic.

## Current state

This epic is **not production-green yet**. The child tasks have produced the consolidation inventory and governance evidence, but the final duplicate cleanup verifier is still in review and has not been merged into the canonical branch.

| Child | Scope | Linear state | Durable evidence | Green gate |
|---|---|---:|---|---|
| GRO-3981 | Inventory stray HDE operational files outside `hd-platform` | Done | Stray-file inventory produced and summarized for operations review | Inventory exists and identifies candidates without deleting runtime-only files |
| GRO-3982 | Move reusable HDE cron/watchdog scripts into `hd-platform/scripts/operations` | Done | Operations script consolidation completed in child branch history | Reusable scripts live under tracked operations path |
| GRO-3983 | Move HDE launch/audit/deploy reports into `hd-platform/docs/operations` | Done | Launch/audit/deploy report consolidation completed in child branch history | Reports live under tracked operations path |
| GRO-3984 | Add operational file governance README and `.gitignore` rules | Done | Governance rules completed in child branch history | Runtime output stays ignored; durable evidence stays documented |
| GRO-3985 | Verify consolidated operations files and remove only safe duplicates | In Review | `ned/GRO-3985`, PR #28, duplicate-safety docs | Merge PR #28 or equivalent duplicate-safety verifier with passing Pages check |

## Parent acceptance decision

GRO-3980 should move to **In Review**, not Done, until the in-review child is merged and the final duplicate-safety proof is available from the canonical branch.

The known child PR at the time of this parent snapshot is:

- <https://github.com/mbgulden/hd-platform/pull/28> — `[Ned] Verify HDE operational duplicate cleanup (#GRO-3985)`

Observed PR-check state from this run:

- Cloudflare Pages: passing
- Workers Builds: failing on the stale `hd-platform` Workers build path already seen on sibling HDE PRs; this is not the Pages deployment path, but it still means the PR is not fully clean by GitHub status.

## Operational consolidation green definition

The category is green only after all of these are true with fresh evidence:

1. Stray operational files outside `hd-platform` are inventoried.
2. Reusable scripts are tracked under `scripts/operations/` or explicitly left out with reason.
3. Durable reports/runbooks are tracked under `docs/operations/`.
4. Runtime-only/generated/temp files are ignored, not committed.
5. Duplicate cleanup is safety-verified before any deletion.
6. The final verifier/report branch is merged or otherwise present in the canonical branch used for deployment/review.

## Verification commands for future refresh

```bash
git ls-files docs/operations scripts/operations
python3 -m py_compile scripts/operations/*.py
npm run build
```

If `scripts/operations/` is absent in a branch, that branch has not yet received the child consolidation output and must not be treated as green.

## Operator note

Do not mark the parent Done just because the plan tree is mostly complete. Parent Done requires merged child evidence, not intent. The robots have enough optimism already.
