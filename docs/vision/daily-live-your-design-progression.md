---
type: Product instrumentation spec
title: Daily Live Your Design Progression
resource: /home/ubuntu/work/hd-platform/docs/vision/daily-live-your-design-progression.md
tags: [hde, north-star, daily-work, instrumentation, nervous-system]
timestamp: 2026-07-19T00:00:00Z
linear_issue: GRO-4014
git_repo: mbgulden/hd-platform
git_path: docs/vision/daily-live-your-design-progression.md
status: implementation-ready
---

# Daily “Live Your Design” progression

## Purpose

Human Design Engine cannot stop at chart reports. The daily loop must move a user from **map → embodied action → reflection → outcome evidence** without turning nervous-system work into shame-based streak theater.

The canonical machine-readable model now lives at [`scripts/live_your_design_progression.py`](../../scripts/live_your_design_progression.py). It emits JSON or Markdown and validates the event catalog with no external dependencies:

```bash
python3 scripts/live_your_design_progression.py --validate
python3 scripts/live_your_design_progression.py --format json
python3 scripts/live_your_design_progression.py --format markdown
```

## Daily loop

1. **Understand today’s transit/design theme** — open the briefing and see the active gates/theme.
2. **Choose one body-level practice or relational experiment** — make the next action concrete.
3. **Complete, skip, or save without shame pressure** — streaks are recovery-aware, not coercive.
4. **Reflect on nervous-system state and behavior** — collect structured deltas, not raw journal text by default.
5. **Record life-change evidence** — self-trust, decision follow-through, relationship repair, or regulation signal.

## Content surfaces

| Surface | Role | Primary event | Notes |
|---|---|---|---|
| `daily_transit_briefing` | Explains the day’s conditioning and invites one real-life experiment. | `hde_daily_briefing_viewed` | Connects existing transit work to practice selection. |
| `embodied_practice_card` | Gives one small action, body cue, duration, and optional relationship variant. | `hde_practice_started` | Converts report insight into behavior. |
| `practice_completion` | Records completed/skipped/saved state plus recovery copy. | `hde_practice_completed` | Streaks measure return and recovery, not perfection. |
| `daily_reflection` | Captures before/after regulation and decision/relationship deltas. | `hde_reflection_submitted` | Structured scores only unless raw text storage is explicit opt-in. |
| `life_change_signal` | Captures evidence that the practice is becoming a lived pattern. | `hde_outcome_signal_recorded` | Separates content consumption from actual product fit. |

## Instrumentation event catalog

All event names use the `hde_` prefix and avoid secrets, raw birth data, and raw journal body text.

| Event | Signal type | Required properties | Success signal |
|---|---|---|---|
| `hde_daily_briefing_viewed` | activation | `user_id`, `anonymous_id`, `target_date`, `chart_type`, `active_gate_count` | Daily work loop started. |
| `hde_practice_started` | engagement | `user_id`, `practice_id`, `surface`, `target_date`, `suggested_duration_minutes` | Map converted into action attempt. |
| `hde_practice_completed` | engagement | `user_id`, `practice_id`, `completion_state`, `target_date` | Completion/recovery loop is measurable. |
| `hde_reflection_submitted` | reflection | `user_id`, `reflection_prompt_id`, `target_date`, `nervous_system_before`, `nervous_system_after` | Regulation and behavior deltas are measurable. |
| `hde_outcome_signal_recorded` | outcome | `user_id`, `signal_category`, `target_date`, `signal_value` | Life-change evidence exists. |
| `hde_safety_recovery_prompt_shown` | safety | `user_id`, `trigger`, `target_date`, `copy_variant` | Product protects regulation instead of optimizing only streak pressure. |

## Dashboard metrics

- `daily_briefing_view_rate`
- `briefing_to_practice_start_rate`
- `practice_completion_or_recovery_rate`
- `reflection_submission_rate`
- `average_nervous_system_delta`
- `weekly_outcome_signal_count`
- `relationship_variant_usage_rate`
- `missed_day_recovery_rate`

## Privacy and safety guardrails

- Do not instrument `birth_time`, `birth_date`, raw `journal_text`, API keys, or secrets.
- Store structured reflection scores by default; raw reflection text requires explicit opt-in.
- Missed-day recovery copy is a first-class event so the product can measure supportive return without coercive streak language.
- Outcome signals should be aggregateable enough for analytics while still respecting sensitive personal context.

## Implementation handoff

Next implementation step is to wire the catalog into the application telemetry adapter when the analytics provider is available. Until then, this script is the source of truth for product planning, QA, and future API/schema work.
