# HDE SEO/index hygiene rollup — GRO-3998

Date: 2026-07-18
Owner: Ned
Linear: GRO-3998

## Purpose

This epic is the SEO/index hygiene parent for Human Design Engine green-state remediation. The site should index only intentional public surfaces, each indexable page should carry a canonical URL and useful metadata, and Search Console proof must be attached after OAuth is available.

North Star reminder: Human Design Engine helps people understand their design, regulate their nervous system through daily embodied action, and keep becoming the highest-integrity version of themselves. Reports are maps; the product must turn the map into daily work, community momentum, and measurable life-change.

## Child execution order

1. GRO-3999 — Fix sitemap redirect loop and index pollution.
2. GRO-4000 — Add missing canonical and meta descriptions to legacy/generated pages.
3. GRO-4001 — Add site-wide OG/social image strategy.
4. GRO-4002 — Normalize old landing pages into current North Star copy.
5. GRO-4003 — Resubmit sitemap and verify Search Console coverage.

The parent is not green until all five child tasks have fresh repo/build/live proof. The current branch adds the repeatable audit harness and rollup artifact so each child fix can be measured instead of hand-waved. A stunningly low bar, somehow still worth writing down.

## Audit harness added

`python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo . --json`

The harness reads the built `dist/` output and reports:

- sitemap route count;
- redirect count;
- redirect self-loops;
- sitemap entries pointing at redirect sources;
- private/operational route candidates such as `cron-health`, `coach_dashboard`, dashboard surfaces, stale landing indexes, and `active-oahu` paths;
- missing `title`, `description`, canonical, Open Graph, and Twitter image metadata on indexable HTML pages.

Use `--fail-on-critical` when a child task wants CI to fail on index pollution. For this parent epic, the first run is deliberately non-fatal because it is establishing the backlog of known SEO debt.

## Expected current red/yellow areas

- GRO-3999 owns redirect loops and index pollution.
- GRO-4000 owns canonical/description gaps across legacy/generated pages.
- GRO-4001 owns default and section-specific OG/social image coverage.
- GRO-4002 owns stale copy and legacy route normalization.
- GRO-4003 remains dependent on Google Search Console OAuth/scope availability before sitemap submission proof can be green.

## Verification contract

For this parent branch, verification is:

```bash
python3 -m py_compile scripts/operations/hde_seo_index_hygiene_audit.py
npm run build
python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo . --json
python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo .
git diff --check
```

Attach the JSON/text output to the Linear finalization evidence or `/tmp/issue-batches/GRO-3998_RESULT.md`.
