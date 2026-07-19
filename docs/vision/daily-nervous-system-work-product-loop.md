---
type: Product loop specification
title: Daily Nervous-System Work Product Loop
resource: /home/ubuntu/work/hd-platform/docs/vision/daily-nervous-system-work-product-loop.md
tags: [hde, north-star, daily-work, nervous-system, product-loop]
timestamp: 2026-07-19T00:00:00Z
linear_issue: GRO-4011
git_repo: mbgulden/hd-platform
git_path: docs/vision/daily-nervous-system-work-product-loop.md
status: implementation-ready
---

# Daily nervous-system work product loop

## Purpose

Human Design Engine's North Star says the product must help people **understand their design → regulate through daily embodied action → keep becoming the highest-integrity version of themselves**. A report is only a map. The daily product must ship an actual work product the user can complete, recover from, and learn from.

The canonical machine-readable model now lives at [`scripts/nervous_system_work_product_loop.py`](../../scripts/nervous_system_work_product_loop.py). It is dependency-free and validates the loop, work products, telemetry coverage, and privacy guardrails:

```bash
python3 scripts/nervous_system_work_product_loop.py --validate
python3 scripts/nervous_system_work_product_loop.py --format json
python3 scripts/nervous_system_work_product_loop.py --format markdown
```

## The loop

1. **Understand design** — receive today's design/transit map with one active theme, authority reminder, body cue, and conditioning risk.
2. **Choose action** — pick exactly one body-level practice or relational experiment sized to today's regulation capacity.
3. **Daily practice** — attempt, partially complete, skip, or save the practice without shame-based streak pressure.
4. **Reflect** — record before/after nervous-system state and behavior deltas in under 60 seconds.
5. **Become** — capture weekly-visible evidence: self-trust, decision follow-through, relationship repair, or regulated action.

## User work products

| Phase | Work product | User question | Completion signal |
|---|---|---|---|
| `understand` | `today_design_map` | What does my design/transit map say is alive today? | User can name the day's theme and sees one authority-specific caution. |
| `choose` | `one_body_level_action` | What is the smallest honest action I can take from this map? | User chooses one action or consciously saves/skips. |
| `practice` | `daily_embodied_practice` | Did I try the action in my actual body or relationship? | Completed, partial, skipped, and recovery states are all valid data. |
| `reflect` | `structured_regulation_reflection` | What changed in my body, choice, or relationship after the practice? | Structured regulation/behavior deltas exist even when raw journaling is skipped. |
| `become` | `becoming_evidence_signal` | What evidence says this is changing how I live? | Outcome signal points to behavior/life change, not content consumption alone. |

## Telemetry event catalog

All events use the `hde_` prefix. They explicitly avoid raw birth data, API keys, payment identifiers, and raw journal body text.

| Event | Phase | Type | Required properties | Success signal |
|---|---|---|---|---|
| `hde_design_map_understood` | `understand` | activation | `user_id`, `anonymous_id`, `target_date`, `chart_type`, `authority` | User entered the daily loop from the map surface. |
| `hde_daily_action_chosen` | `choose` | commitment | `user_id`, `target_date`, `action_id`, `choice_state` | The map became a concrete action instead of passive reading. |
| `hde_embodied_practice_attempted` | `practice` | engagement | `user_id`, `practice_id`, `target_date`, `completion_state` | Daily work is measurable without shame-copy streak gaming. |
| `hde_regulation_reflection_submitted` | `reflect` | reflection | `user_id`, `practice_id`, `target_date`, `nervous_system_before`, `nervous_system_after` | HDE measures regulation and behavior deltas, not just opens/clicks. |
| `hde_becoming_evidence_recorded` | `become` | outcome | `user_id`, `target_date`, `signal_category`, `signal_value` | Product fit is tied to life-change evidence rather than report consumption. |
| `hde_recovery_prompt_shown` | `practice` | safety | `user_id`, `target_date`, `trigger`, `copy_variant` | The product protects the user's nervous system while preserving return momentum. |

## Dashboard metrics

- `daily_map_to_action_choice_rate`
- `action_choice_to_practice_attempt_rate`
- `practice_completion_or_recovery_rate`
- `median_reflection_time_seconds`
- `average_nervous_system_delta`
- `weekly_becoming_evidence_count`
- `self_trust_delta_trend`
- `relationship_repair_signal_rate`
- `missed_day_recovery_return_rate`

## Safety rules

- Do not use shame-based streak pressure. Recovery is a first-class product state.
- Do not store raw journal text by default. Capture structured regulation and behavior scores; raw text must be explicit opt-in.
- Do not put `birth_date`, `birth_time`, raw birth data, API keys, secrets, or payment identifiers in telemetry.
- Do not call production green until live proof covers the loop behavior, not just page generation or report purchase.
- Do not treat a report purchase as transformation. Green means the user has a path from map to action to evidence.

## Implementation handoff

The script is now the source of truth for product planning, QA, analytics schema work, and future UI/API wiring. The next implementation step is to wire these events and work-product states into the application once the analytics/storage adapter is selected.
