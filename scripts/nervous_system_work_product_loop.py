#!/usr/bin/env python3
"""Canonical daily nervous-system work product loop for Human Design Engine.

The loop translates the North Star sentence into a shippable product contract:
understand design -> choose action -> daily practice -> reflect -> become.
It is intentionally dependency-free so product, analytics, QA, and agent work can
share one source of truth before a database-backed implementation exists.

Usage:
    python3 scripts/nervous_system_work_product_loop.py --validate
    python3 scripts/nervous_system_work_product_loop.py --format json
    python3 scripts/nervous_system_work_product_loop.py --format markdown
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

LoopPhase = Literal["understand", "choose", "practice", "reflect", "become"]
WorkProductType = Literal["map", "action", "practice", "reflection", "evidence"]
TelemetryType = Literal["activation", "commitment", "engagement", "reflection", "outcome", "safety"]

FORBIDDEN_FIELDS = {
    "api_key",
    "birth_date",
    "birth_time",
    "journal_text",
    "raw_birth_data",
    "secret",
    "stripe_customer_id",
}


@dataclass(frozen=True)
class WorkProduct:
    """Concrete artifact the user receives or creates at one loop phase."""

    key: str
    phase: LoopPhase
    product_type: WorkProductType
    user_question: str
    output: str
    required_inputs: list[str]
    completion_criteria: list[str]
    safety_copy: str
    next_step: str


@dataclass(frozen=True)
class TelemetryEvent:
    """Privacy-preserving analytics contract for the loop."""

    name: str
    telemetry_type: TelemetryType
    phase: LoopPhase
    when: str
    required_properties: list[str]
    optional_properties: list[str] = field(default_factory=list)
    success_signal: str = ""
    privacy_note: str = "Structured signals only; no raw journal body, birth data, or secrets."


@dataclass(frozen=True)
class NervousSystemLoop:
    """End-to-end HDE daily work product contract."""

    version: str
    north_star: str
    promise: str
    phases: list[LoopPhase]
    work_products: list[WorkProduct]
    telemetry_events: list[TelemetryEvent]
    dashboard_metrics: list[str]
    non_goals: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


LOOP = NervousSystemLoop(
    version="2026-07-19.gro-4011",
    north_star=(
        "Human Design Engine helps people understand their design, regulate their nervous system "
        "through daily embodied action, and keep becoming the highest-integrity version of themselves."
    ),
    promise=(
        "Reports are maps. The product's daily work product is a completed regulation loop: "
        "a design insight, one chosen embodied action, a practice attempt, structured reflection, "
        "and a life-change evidence signal that informs tomorrow."
    ),
    phases=["understand", "choose", "practice", "reflect", "become"],
    work_products=[
        WorkProduct(
            key="today_design_map",
            phase="understand",
            product_type="map",
            user_question="What does my design/transit map say is alive today?",
            output="A short daily map: active theme, authority reminder, body cue, and one conditioning risk.",
            required_inputs=["user_id", "target_date", "chart_type", "authority", "active_gates"],
            completion_criteria=[
                "User can name the day's theme in one sentence.",
                "User sees one authority-specific caution before acting.",
            ],
            safety_copy="This is a map, not a verdict. Let your body test it before believing it.",
            next_step="Offer three action candidates ranked by regulation load.",
        ),
        WorkProduct(
            key="one_body_level_action",
            phase="choose",
            product_type="action",
            user_question="What is the smallest honest action I can take from this map?",
            output="One selected action card with duration, friction level, relationship variant, and skip-safe alternative.",
            required_inputs=["user_id", "target_date", "practice_candidates", "regulation_capacity"],
            completion_criteria=[
                "User chooses exactly one practice or consciously saves/skips.",
                "Practice can be completed in 2-15 minutes without buying anything else.",
            ],
            safety_copy="Choose the action your nervous system can actually metabolize today.",
            next_step="Start a timer or mark the selected practice as today's work.",
        ),
        WorkProduct(
            key="daily_embodied_practice",
            phase="practice",
            product_type="practice",
            user_question="Did I try the action in my actual body or relationship?",
            output="Practice attempt state: completed, partial, skipped, or saved, with recovery prompt when needed.",
            required_inputs=["user_id", "practice_id", "target_date", "completion_state"],
            completion_criteria=[
                "Completion, partial completion, and recovery are all valid states.",
                "A missed day creates a return path instead of shame copy.",
            ],
            safety_copy="A partial attempt still counts as data. Return beats perfection.",
            next_step="Open a short structured reflection tied to body state and behavior.",
        ),
        WorkProduct(
            key="structured_regulation_reflection",
            phase="reflect",
            product_type="reflection",
            user_question="What changed in my body, choice, or relationship after the practice?",
            output="Before/after regulation score plus decision, self-trust, and relationship deltas; raw text is opt-in only.",
            required_inputs=[
                "user_id",
                "practice_id",
                "target_date",
                "nervous_system_before",
                "nervous_system_after",
            ],
            completion_criteria=[
                "Reflection can be completed in under 60 seconds.",
                "Structured scores exist even when raw journaling is skipped.",
            ],
            safety_copy="You are collecting evidence, not grading your healing.",
            next_step="Record an outcome signal and tune tomorrow's difficulty.",
        ),
        WorkProduct(
            key="becoming_evidence_signal",
            phase="become",
            product_type="evidence",
            user_question="What evidence says this is changing how I live?",
            output="A weekly-visible signal: self-trust, decision follow-through, relationship repair, or regulated action.",
            required_inputs=["user_id", "target_date", "signal_category", "signal_value"],
            completion_criteria=[
                "Signal is aggregateable for product learning.",
                "Signal points to behavior/life change, not only content consumption.",
            ],
            safety_copy="Becoming is a trend line. One data point is enough for today.",
            next_step="Use the signal to personalize tomorrow's map and invite a shared practice when appropriate.",
        ),
    ],
    telemetry_events=[
        TelemetryEvent(
            name="hde_design_map_understood",
            telemetry_type="activation",
            phase="understand",
            when="User views or acknowledges today's design/transit map.",
            required_properties=["user_id", "anonymous_id", "target_date", "chart_type", "authority"],
            optional_properties=["profile", "active_gate_count", "top_gate", "timezone"],
            success_signal="The user has entered the daily work loop from the map surface.",
        ),
        TelemetryEvent(
            name="hde_daily_action_chosen",
            telemetry_type="commitment",
            phase="choose",
            when="User selects, saves, or intentionally skips one body-level action.",
            required_properties=["user_id", "target_date", "action_id", "choice_state"],
            optional_properties=["regulation_capacity", "relationship_context", "duration_minutes"],
            success_signal="The map became a concrete next action instead of passive reading.",
        ),
        TelemetryEvent(
            name="hde_embodied_practice_attempted",
            telemetry_type="engagement",
            phase="practice",
            when="User completes, partially completes, skips, or saves the daily practice.",
            required_properties=["user_id", "practice_id", "target_date", "completion_state"],
            optional_properties=["duration_minutes", "friction_reason", "recovery_mode", "streak_count"],
            success_signal="Daily work is measurable without turning streaks into shame pressure.",
        ),
        TelemetryEvent(
            name="hde_regulation_reflection_submitted",
            telemetry_type="reflection",
            phase="reflect",
            when="User submits structured reflection after a practice attempt.",
            required_properties=[
                "user_id",
                "practice_id",
                "target_date",
                "nervous_system_before",
                "nervous_system_after",
            ],
            optional_properties=["decision_clarity_delta", "self_trust_delta", "relationship_signal", "raw_text_stored"],
            success_signal="HDE can measure regulation and behavior deltas, not just opens/clicks.",
            privacy_note="Raw reflection text is opt-in; default instrumentation stores structured scores only.",
        ),
        TelemetryEvent(
            name="hde_becoming_evidence_recorded",
            telemetry_type="outcome",
            phase="become",
            when="User records a lived result or weekly evidence of becoming.",
            required_properties=["user_id", "target_date", "signal_category", "signal_value"],
            optional_properties=["practice_id", "week_start", "share_intent", "notes_redacted"],
            success_signal="Product fit is tied to life-change evidence rather than report consumption alone.",
        ),
        TelemetryEvent(
            name="hde_recovery_prompt_shown",
            telemetry_type="safety",
            phase="practice",
            when="Missed-day, distress, or low-capacity state triggers recovery copy.",
            required_properties=["user_id", "target_date", "trigger", "copy_variant"],
            optional_properties=["previous_streak_count", "completion_state", "nervous_system_after"],
            success_signal="The product protects the user's nervous system while preserving return momentum.",
        ),
    ],
    dashboard_metrics=[
        "daily_map_to_action_choice_rate",
        "action_choice_to_practice_attempt_rate",
        "practice_completion_or_recovery_rate",
        "median_reflection_time_seconds",
        "average_nervous_system_delta",
        "weekly_becoming_evidence_count",
        "self_trust_delta_trend",
        "relationship_repair_signal_rate",
        "missed_day_recovery_return_rate",
    ],
    non_goals=[
        "No shame-based streak pressure.",
        "No raw journal text, birth data, API keys, or payment identifiers in telemetry.",
        "No claim that a report purchase equals transformation.",
        "No production-green status until live proof covers the loop behavior.",
    ],
)


def validate_loop(loop: NervousSystemLoop = LOOP) -> list[str]:
    """Return validation errors for loop ordering, event wiring, and privacy."""

    errors: list[str] = []
    if loop.phases != ["understand", "choose", "practice", "reflect", "become"]:
        errors.append(f"phases must preserve map-to-becoming order: {loop.phases}")

    work_keys = [product.key for product in loop.work_products]
    duplicate_work = sorted({key for key in work_keys if work_keys.count(key) > 1})
    if duplicate_work:
        errors.append(f"duplicate work product keys: {duplicate_work}")

    product_phases = [product.phase for product in loop.work_products]
    if product_phases != loop.phases:
        errors.append(f"work product phases must map one-to-one to loop phases: {product_phases}")

    event_names = [event.name for event in loop.telemetry_events]
    duplicate_events = sorted({name for name in event_names if event_names.count(name) > 1})
    if duplicate_events:
        errors.append(f"duplicate event names: {duplicate_events}")

    event_phases = {event.phase for event in loop.telemetry_events}
    missing_event_phases = set(loop.phases) - event_phases
    if missing_event_phases:
        errors.append(f"missing telemetry coverage for phases: {sorted(missing_event_phases)}")

    for product in loop.work_products:
        if not product.required_inputs:
            errors.append(f"work product {product.key} has no required inputs")
        if not product.completion_criteria:
            errors.append(f"work product {product.key} has no completion criteria")
        leaked_inputs = FORBIDDEN_FIELDS.intersection(product.required_inputs)
        if leaked_inputs:
            errors.append(f"work product {product.key} includes forbidden inputs: {sorted(leaked_inputs)}")

    for event in loop.telemetry_events:
        if not event.name.startswith("hde_"):
            errors.append(f"event must use hde_ prefix: {event.name}")
        if not event.required_properties:
            errors.append(f"event has no required properties: {event.name}")
        leaked = FORBIDDEN_FIELDS.intersection(event.required_properties + event.optional_properties)
        if leaked:
            errors.append(f"event {event.name} includes forbidden telemetry field(s): {sorted(leaked)}")
        if event.phase not in loop.phases:
            errors.append(f"event {event.name} uses unknown phase: {event.phase}")

    return errors


def render_markdown(loop: NervousSystemLoop = LOOP) -> str:
    """Render the loop as a compact Markdown handoff artifact."""

    lines = [
        f"# Daily Nervous-System Work Product Loop ({loop.version})",
        "",
        loop.north_star,
        "",
        f"**Promise:** {loop.promise}",
        "",
        "## Loop phases",
    ]
    lines.extend(f"{idx}. `{phase}`" for idx, phase in enumerate(loop.phases, 1))
    lines.append("")

    lines.append("## User work products")
    for product in loop.work_products:
        lines.extend(
            [
                f"### {product.key}",
                f"- Phase: `{product.phase}`",
                f"- Type: `{product.product_type}`",
                f"- User question: {product.user_question}",
                f"- Output: {product.output}",
                f"- Required inputs: {', '.join(f'`{item}`' for item in product.required_inputs)}",
                f"- Completion criteria: {'; '.join(product.completion_criteria)}",
                f"- Safety copy: {product.safety_copy}",
                f"- Next step: {product.next_step}",
                "",
            ]
        )

    lines.append("## Telemetry events")
    for event in loop.telemetry_events:
        lines.extend(
            [
                f"### `{event.name}`",
                f"- Type: `{event.telemetry_type}`",
                f"- Phase: `{event.phase}`",
                f"- When: {event.when}",
                f"- Required properties: {', '.join(f'`{field}`' for field in event.required_properties)}",
                f"- Optional properties: {', '.join(f'`{field}`' for field in event.optional_properties) or '_none_'}",
                f"- Success signal: {event.success_signal}",
                f"- Privacy note: {event.privacy_note}",
                "",
            ]
        )

    lines.extend(["## Dashboard metrics", *[f"- `{metric}`" for metric in loop.dashboard_metrics], ""])
    lines.extend(["## Non-goals", *[f"- {item}" for item in loop.non_goals], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--validate", action="store_true", help="Validate and exit non-zero on errors.")
    args = parser.parse_args()

    errors = validate_loop()
    if args.validate:
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "ok": True,
                    "version": LOOP.version,
                    "work_products": len(LOOP.work_products),
                    "telemetry_events": len(LOOP.telemetry_events),
                    "metrics": len(LOOP.dashboard_metrics),
                },
                indent=2,
            )
        )
        return 0

    if errors:
        raise SystemExit("Invalid nervous-system loop: " + "; ".join(errors))

    if args.format == "markdown":
        print(render_markdown())
    else:
        print(json.dumps(LOOP.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
