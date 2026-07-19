#!/usr/bin/env python3
"""Daily "live your design" progression model and event catalog.

This script is intentionally dependency-free so product, analytics, and agent work can
share one canonical artifact before a database or warehouse-backed implementation
exists. It emits the content surfaces and instrumentation events that turn static
Human Design reports into daily practice loops.

Usage:
    python3 scripts/live_your_design_progression.py --format json
    python3 scripts/live_your_design_progression.py --format markdown
    python3 scripts/live_your_design_progression.py --validate
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SignalType = Literal["activation", "engagement", "reflection", "outcome", "safety"]
SurfaceType = Literal["transit_briefing", "practice", "reflection", "streak", "outcome_signal"]


@dataclass(frozen=True)
class EventSpec:
    """Analytics event contract for the daily progression loop."""

    name: str
    signal_type: SignalType
    when: str
    required_properties: list[str]
    optional_properties: list[str] = field(default_factory=list)
    success_signal: str = ""
    privacy_note: str = "No birth data, journal body text, or secrets are captured."


@dataclass(frozen=True)
class ContentSurface:
    """Product content surface that advances the user through the daily loop."""

    key: str
    surface_type: SurfaceType
    user_question: str
    content_fields: list[str]
    primary_event: str
    next_action: str


@dataclass(frozen=True)
class ProgressionModel:
    """Canonical model for daily Human Design embodiment progression."""

    version: str
    north_star: str
    loop_steps: list[str]
    content_surfaces: list[ContentSurface]
    events: list[EventSpec]
    dashboard_metrics: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


MODEL = ProgressionModel(
    version="2026-07-19.gro-4014",
    north_star=(
        "Reports are maps; HDE turns the map into daily embodied action, "
        "nervous-system regulation, reflection, and measurable life-change."
    ),
    loop_steps=[
        "Understand today's transit/design theme",
        "Choose one body-level practice or relational experiment",
        "Complete the practice without performative streak pressure",
        "Reflect on nervous-system state and real-world behavior",
        "Record an outcome signal that can guide tomorrow's prompt",
    ],
    content_surfaces=[
        ContentSurface(
            key="daily_transit_briefing",
            surface_type="transit_briefing",
            user_question="What energy is conditioning me today, and what should I try in real life?",
            content_fields=[
                "target_date",
                "active_gates",
                "theme_summary",
                "authority_specific_caution",
                "one_sentence_practice_invite",
            ],
            primary_event="hde_daily_briefing_viewed",
            next_action="Offer one practice card matched to authority, type, and strongest transit theme.",
        ),
        ContentSurface(
            key="embodied_practice_card",
            surface_type="practice",
            user_question="What is the smallest honest action I can take today?",
            content_fields=[
                "practice_id",
                "practice_title",
                "body_cue",
                "suggested_duration_minutes",
                "relationship_variant",
                "completion_prompt",
            ],
            primary_event="hde_practice_started",
            next_action="Let the user complete, skip, or save the practice without shame language.",
        ),
        ContentSurface(
            key="practice_completion",
            surface_type="streak",
            user_question="Did I act from the map today?",
            content_fields=[
                "practice_id",
                "completion_state",
                "friction_reason",
                "streak_count",
                "recovery_copy",
            ],
            primary_event="hde_practice_completed",
            next_action="Update streak/recovery state and open a short reflection.",
        ),
        ContentSurface(
            key="daily_reflection",
            surface_type="reflection",
            user_question="What changed in my body, choice, or relationship after the practice?",
            content_fields=[
                "reflection_prompt_id",
                "nervous_system_before",
                "nervous_system_after",
                "decision_clarity_delta",
                "relationship_signal",
            ],
            primary_event="hde_reflection_submitted",
            next_action="Extract structured signals only; do not store raw journal text by default.",
        ),
        ContentSurface(
            key="life_change_signal",
            surface_type="outcome_signal",
            user_question="What evidence says this is becoming a lived pattern?",
            content_fields=[
                "signal_id",
                "signal_category",
                "self_trust_delta",
                "relationship_repair_delta",
                "decision_followthrough_delta",
                "notes_redacted",
            ],
            primary_event="hde_outcome_signal_recorded",
            next_action="Use aggregate trends to choose tomorrow's practice difficulty and theme.",
        ),
    ],
    events=[
        EventSpec(
            name="hde_daily_briefing_viewed",
            signal_type="activation",
            when="User opens the daily transit/design briefing.",
            required_properties=["user_id", "anonymous_id", "target_date", "chart_type", "active_gate_count"],
            optional_properties=["top_gate", "authority", "profile", "source", "timezone"],
            success_signal="Daily work loop started, not merely report purchased.",
        ),
        EventSpec(
            name="hde_practice_started",
            signal_type="engagement",
            when="User starts an embodied practice or relational experiment from a briefing/report.",
            required_properties=["user_id", "practice_id", "surface", "target_date", "suggested_duration_minutes"],
            optional_properties=["authority", "type", "top_gate", "relationship_context"],
            success_signal="Map converted into an action attempt.",
        ),
        EventSpec(
            name="hde_practice_completed",
            signal_type="engagement",
            when="User marks the practice complete, skipped, or saved for later.",
            required_properties=["user_id", "practice_id", "completion_state", "target_date"],
            optional_properties=["duration_minutes", "friction_reason", "streak_count", "recovery_mode"],
            success_signal="Completion and recovery loops can be measured without shame-copy streak gaming.",
        ),
        EventSpec(
            name="hde_reflection_submitted",
            signal_type="reflection",
            when="User submits structured reflection after a practice.",
            required_properties=[
                "user_id",
                "reflection_prompt_id",
                "target_date",
                "nervous_system_before",
                "nervous_system_after",
            ],
            optional_properties=["decision_clarity_delta", "relationship_signal", "raw_text_stored"],
            success_signal="Nervous-system and behavior deltas are available for product learning.",
            privacy_note="Default instrumentation stores structured scores only; raw reflection text must be explicit opt-in.",
        ),
        EventSpec(
            name="hde_outcome_signal_recorded",
            signal_type="outcome",
            when="User records a lived result such as better decision follow-through, self-trust, or repair.",
            required_properties=["user_id", "signal_category", "target_date", "signal_value"],
            optional_properties=["practice_id", "streak_count", "share_intent", "notes_redacted"],
            success_signal="HDE can distinguish static content consumption from life-change evidence.",
        ),
        EventSpec(
            name="hde_safety_recovery_prompt_shown",
            signal_type="safety",
            when="A missed day, distress score, or low-regulation response triggers non-shaming recovery copy.",
            required_properties=["user_id", "trigger", "target_date", "copy_variant"],
            optional_properties=["previous_streak_count", "nervous_system_after"],
            success_signal="The product protects regulation instead of optimizing only for streak pressure.",
        ),
    ],
    dashboard_metrics=[
        "daily_briefing_view_rate",
        "briefing_to_practice_start_rate",
        "practice_completion_or_recovery_rate",
        "reflection_submission_rate",
        "average_nervous_system_delta",
        "weekly_outcome_signal_count",
        "relationship_variant_usage_rate",
        "missed_day_recovery_rate",
    ],
)


def validate_model(model: ProgressionModel = MODEL) -> list[str]:
    """Return validation errors for event/surface wiring."""

    errors: list[str] = []
    event_names = {event.name for event in model.events}
    surface_events = {surface.primary_event for surface in model.content_surfaces}

    missing_surface_events = surface_events - event_names
    if missing_surface_events:
        errors.append(f"surface primary_event missing from event catalog: {sorted(missing_surface_events)}")

    duplicate_events = sorted({name for name in event_names if [e.name for e in model.events].count(name) > 1})
    if duplicate_events:
        errors.append(f"duplicate event names: {duplicate_events}")

    for event in model.events:
        if not event.name.startswith("hde_"):
            errors.append(f"event must use hde_ prefix: {event.name}")
        if not event.required_properties:
            errors.append(f"event has no required properties: {event.name}")
        forbidden = {"birth_time", "birth_date", "journal_text", "api_key", "secret"}
        leaked = forbidden.intersection(event.required_properties + event.optional_properties)
        if leaked:
            errors.append(f"event {event.name} includes forbidden property/properties: {sorted(leaked)}")

    return errors


def render_markdown(model: ProgressionModel = MODEL) -> str:
    """Render the model as a compact markdown spec for docs and Linear evidence."""

    lines = [
        f"# Daily Live Your Design Progression Model ({model.version})",
        "",
        model.north_star,
        "",
        "## Loop steps",
        *[f"{idx}. {step}" for idx, step in enumerate(model.loop_steps, 1)],
        "",
        "## Content surfaces",
    ]
    for surface in model.content_surfaces:
        lines.extend(
            [
                f"### {surface.key}",
                f"- Type: `{surface.surface_type}`",
                f"- User question: {surface.user_question}",
                f"- Primary event: `{surface.primary_event}`",
                f"- Fields: {', '.join(f'`{field}`' for field in surface.content_fields)}",
                f"- Next action: {surface.next_action}",
                "",
            ]
        )

    lines.append("## Instrumentation events")
    for event in model.events:
        lines.extend(
            [
                f"### `{event.name}`",
                f"- Signal type: `{event.signal_type}`",
                f"- When: {event.when}",
                f"- Required properties: {', '.join(f'`{field}`' for field in event.required_properties)}",
                f"- Optional properties: {', '.join(f'`{field}`' for field in event.optional_properties) or '_none_'}",
                f"- Success signal: {event.success_signal}",
                f"- Privacy note: {event.privacy_note}",
                "",
            ]
        )

    lines.extend(["## Dashboard metrics", *[f"- `{metric}`" for metric in model.dashboard_metrics], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--validate", action="store_true", help="Validate the model and exit non-zero on errors.")
    args = parser.parse_args()

    errors = validate_model()
    if args.validate:
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"ok": True, "version": MODEL.version, "events": len(MODEL.events)}, indent=2))
        return 0

    if errors:
        raise SystemExit("Invalid progression model: " + "; ".join(errors))

    if args.format == "markdown":
        print(render_markdown())
    else:
        print(json.dumps(MODEL.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
