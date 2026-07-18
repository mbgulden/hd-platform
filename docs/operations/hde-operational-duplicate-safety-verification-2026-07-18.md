# HDE Operational Duplicate Safety Verification — 2026-07-18

## Purpose

GRO-3985 verifies stray Human Design Engine operational files before cleanup. The rule is intentionally conservative: only delete an external file when it is an exact byte-for-byte duplicate of a canonical `hd-platform` file, it is not referenced by cron/systemd/runtime surfaces, and it lives under an approved safe-delete prefix such as `/tmp/` or `/home/ubuntu/work/artifacts/`.

## Canonical tooling

- Scanner: `scripts/operations/hde_operational_file_inventory.py`
- Default mode: read-only JSON inventory
- Markdown mode: `python3 scripts/operations/hde_operational_file_inventory.py --format markdown`
- Cleanup mode: `python3 scripts/operations/hde_operational_file_inventory.py --delete-safe`

The scanner checks:

1. HDE-related candidate files outside this repo and `hd-platform-staging`.
2. SHA-256 hashes against canonical repository files.
3. Runtime references in cron/systemd/profile script surfaces.
4. Candidate classification and a per-file action recommendation.

## Current cleanup decision

No manual delete list is maintained in this document. Cleanup must come from fresh scanner output. If `safe_delete_candidate_count` is `0`, delete nothing. If non-zero, review the exact output and run `--delete-safe` only for files that still meet all guards in that same run.

## Verification evidence

Fresh run evidence for GRO-3985 is recorded in the task result and can be regenerated with:

```bash
python3 scripts/operations/hde_operational_file_inventory.py --limit 5000 > /tmp/hde-operational-inventory.json
python3 scripts/operations/hde_operational_file_inventory.py --limit 5000 --format markdown > /tmp/hde-operational-inventory.md
python3 -m py_compile scripts/operations/hde_operational_file_inventory.py
```

## Secret and runtime-artifact policy

- Do not commit `.env`, `.env.*`, runtime backups, raw cron output, or generated scanner JSON dumps.
- Commit only the scanner source and the durable summary docs.
- Runtime files referenced by cron/systemd are never deleted by this task.
