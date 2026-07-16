"""
Bodygraph endpoint — POST /v1/bodygraph.

Computes a natal chart and returns a structured bodygraph-payload
suitable for rendering an interactive SVG bodygraph.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator

from shared.mcp_client import compute_natal_chart
from ..middleware import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bodygraph", tags=["bodygraph"])

# ── Engine reference data ────────────────────────────────────────────
import sys, os
ENGINE_PATH = os.environ.get(
    "ENGINE_PATH", "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src"
)
sys.path.insert(0, ENGINE_PATH)

from matrix_mapper import GATE_NAMES, GATE_CENTER, CHANNELS

CENTER_COLORS = {
    "Head": "#f7dc6f",
    "Ajna": "#5dade2",
    "Throat": "#58d68d",
    "G": "#f0b27a",
    "Heart": "#ec7063",
    "Sacral": "#e74c3c",
    "Spleen": "#af7ac5",
    "Solar Plexus": "#f1948a",
    "Root": "#a569bd",
}

CENTER_MAP = {
    "Head": "head", "Ajna": "ajna", "Throat": "throat",
    "G": "g", "Heart": "heart", "Sacral": "sacral",
    "Spleen": "spleen", "Solar Plexus": "solar_plexus", "Root": "root",
}

ALL_CENTERS = ["head","ajna","throat","g","heart","sacral","spleen","solar_plexus","root"]

FIELD_DESCRIPTIONS = {
    "profile": "Conscious/unconscious role pattern for learning, relating, and projection.",
    "type": "Aura mechanics and the broad way energy engages with life.",
    "definition": "How defined centers connect internally and where relationship bridges matter.",
    "environment": "The setting where the nervous system tends to regulate best.",
    "view_perspective": "The way the mind sees clearly when it is not controlling decisions.",
    "signature": "The felt signal that the mechanics are working.",
    "variables": "Four-arrow orientation for digestion, environment, mind, and motivation.",
    "distraction": "The mental lure that pulls perspective off track.",
    "strategy": "The cleanest way to meet life with less resistance.",
    "not_self": "The early warning light that the person is forcing or moving off-pattern.",
    "sense": "The sensory emphasis the body may use to orient.",
    "trajectory": "The directional arc cognition and environment are tuned to follow.",
    "authority": "The body’s decision-making signal to trust before mental explanation.",
    "cognition": "The specific sense channel that can operate as body intelligence.",
    "motivation": "The deeper motive that keeps the mind clean and useful.",
    "transference": "The compensating motive the mind can slide into.",
    "determination": "How the body best digests food, information, and experience.",
    "incarnation_cross": "The life-theme frame carried by the Sun/Earth gates.",
    "bridging_gates": "Gates that can bridge split definition or become relational connectors.",
    "melancholy": "Individual-circuit gates where mood, timing, and creative pulse may need space.",
    "fears": "Splenic fear themes that can mature into wisdom when named.",
    "penta_qualities": "Family, group, and business qualities visible in team fields.",
    "genetic_trauma": "A trauma lens for wound-pattern integration.",
    "astrohd_star_archetype": "A star/archetype layer for mythic language and coaching content.",
}

PLANET_SIGNIFICANCE = {
    "Sun": "core life-force and visible theme",
    "Earth": "grounding, balance, and integration point",
    "Moon": "emotional pull and recurring need",
    "Mercury": "communication, naming, and mental processing",
    "Venus": "values, aesthetics, and relational standards",
    "Mars": "maturation edge, assertion, and raw drive",
    "Jupiter": "growth, protection, and natural opportunity",
    "Saturn": "discipline, consequence, and life lessons",
    "Uranus": "disruption, originality, and individuation",
    "Neptune": "mystery, sensitivity, and spiritual atmosphere",
    "Pluto": "depth, transformation, and evolutionary pressure",
    "True Node": "directional environment and life path orientation",
    "South Node": "familiar patterning and early-life orientation",
}


def _safe_chart_value(chart: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = chart.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


# ── Request / Response schemas ────────────────────────────────────────


class BodygraphRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    location: Optional[str] = Field(None, max_length=500)
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0)
    lon: Optional[float] = Field(None, ge=-180.0, le=180.0)
    timezone: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def _check_coords(self) -> "BodygraphRequest":
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must both be provided or both omitted")
        return self


class BodygraphResponse(BaseModel):
    success: bool
    endpoint: str = "/v1/bodygraph"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ── Mapping logic ─────────────────────────────────────────────────────


def _build_bodygraph_payload(chart: Dict[str, Any]) -> Dict[str, Any]:
    """Transform natal chart output into a bodygraph-payload."""

    defined_centers = set(chart.get("defined_centers", []))
    all_active_gates = set(chart.get("all_active_gates", []))

    # Extract gate numbers from personality/design gate dict lists
    personality_gate_nums = set(
        g["gate"] if isinstance(g, dict) else g
        for g in chart.get("personality_gates", [])
    )
    design_gate_nums = set(
        g["gate"] if isinstance(g, dict) else g
        for g in chart.get("design_gates", [])
    )

    # Build set of defined channel gate-pair tuples for O(1) lookup
    defined_channel_pairs = set()
    for ch in chart.get("defined_channels", []):
        gates = ch.get("gates", ())
        if len(gates) == 2:
            defined_channel_pairs.add((gates[0], gates[1]))
            defined_channel_pairs.add((gates[1], gates[0]))

    # ── Meta ──
    meta = {
        "name": chart.get("name", ""),
        "type": chart.get("hd_type", chart.get("type", "")),
        "profile": chart.get("profile", ""),
        "authority": chart.get("authority", ""),
        "strategy": chart.get("strategy", ""),
        "signature": chart.get("signature", ""),
        "not_self": chart.get("not_self_theme", ""),
        "definition": chart.get("definition", ""),
        "incarnation_cross": chart.get("incarnation_cross", {}),
        "environment": _safe_chart_value(chart, "environment"),
        "view_perspective": _safe_chart_value(chart, "perspective", "view"),
        "variables": _safe_chart_value(chart, "variables", "variable", "variable_code"),
        "distraction": _safe_chart_value(chart, "distraction"),
        "sense": _safe_chart_value(chart, "sense"),
        "trajectory": _safe_chart_value(chart, "trajectory"),
        "cognition": _safe_chart_value(chart, "cognition"),
        "motivation": _safe_chart_value(chart, "motivation"),
        "transference": _safe_chart_value(chart, "transference"),
        "determination": _safe_chart_value(chart, "determination", "digestion"),
        "bridging_gates": _safe_chart_value(chart, "bridging_gates"),
        "melancholy": _safe_chart_value(chart, "melancholy_gates"),
        "fears": _safe_chart_value(chart, "fear_gates", "fears"),
        "penta_qualities": _safe_chart_value(chart, "penta_qualities"),
        "genetic_trauma": _safe_chart_value(chart, "genetic_trauma"),
        "astrohd_star_archetype": _safe_chart_value(chart, "star_archetype", "astrohd_star_archetype"),
        "field_descriptions": FIELD_DESCRIPTIONS,
    }

    # ── Centers ──
    centers: Dict[str, Dict[str, Any]] = {}
    for center_key in ALL_CENTERS:
        full_name = next((k for k, v in CENTER_MAP.items() if v == center_key), center_key)
        is_defined = full_name in defined_centers
        centers[center_key] = {
            "defined": is_defined,
            "color": CENTER_COLORS.get(full_name) if is_defined else None,
            "name": full_name,
        }

    # ── Gates (1-64) ──
    gates: Dict[str, Dict[str, Any]] = {}
    for gate_num in range(1, 65):
        gk = str(gate_num)
        active = gate_num in all_active_gates
        activation = None
        planet = None

        if active:
            if gate_num in personality_gate_nums and gate_num in design_gate_nums:
                activation = "both"
            elif gate_num in personality_gate_nums:
                activation = "personality"
            else:
                activation = "design"

            # Find which planet activates this gate
            for planet_name, pdata in chart.get("personality_planets", {}).items():
                if isinstance(pdata, dict) and pdata.get("gate") == gate_num:
                    planet = planet_name
                    break
            if not planet:
                for planet_name, pdata in chart.get("design_planets", {}).items():
                    if isinstance(pdata, dict) and pdata.get("gate") == gate_num:
                        planet = planet_name
                        break

        gates[gk] = {
            "active": active,
            "activation": activation,
            "planet": planet,
            "name": GATE_NAMES.get(gate_num, f"Gate {gate_num}"),
            "center": CENTER_MAP.get(GATE_CENTER.get(gate_num, ""), "unknown"),
        }

    # ── Channels ──
    channels: Dict[str, Dict[str, Any]] = {}
    for channel_id, ch_data in CHANNELS.items():
        if isinstance(ch_data, dict):
            gate_a, gate_b = ch_data.get("gates", channel_id)
            channel_name = ch_data.get("name", "")
        else:
            gate_a, gate_b = channel_id
            channel_name = str(ch_data)
        both_active = gate_a in all_active_gates and gate_b in all_active_gates
        one_active = (gate_a in all_active_gates) != (gate_b in all_active_gates)
        is_defined = (gate_a, gate_b) in defined_channel_pairs

        if is_defined:
            state = "defined"
        elif one_active:
            state = "hanging"
        elif both_active:
            state = "undefined_both"
        else:
            state = "undefined"

        ch_entry: Dict[str, Any] = {
            "state": state,
            "gates": [gate_a, gate_b],
            "name": channel_name,
        }
        if state == "hanging":
            ch_entry["hanging_gate"] = gate_a if gate_a in all_active_gates else gate_b
        channel_key = f"{gate_a}-{gate_b}"
        channels[channel_key] = ch_entry

    # ── Variables ──
    variables = {}
    for prefix, source in [("personality", chart.get("personality_planets", {})),
                            ("design", chart.get("design_planets", {}))]:
        for planet, pdata in source.items():
            if isinstance(pdata, dict):
                key = f"{prefix}_{planet.lower().replace(' ','_')}"
                variables[key] = {
                    "gate": pdata.get("gate"),
                    "line": pdata.get("line"),
                    "color": pdata.get("color"),
                    "tone": pdata.get("tone"),
                    "base": pdata.get("base"),
                }

    activations: List[Dict[str, Any]] = []
    for side, source in (("personality", chart.get("personality_planets", {})),
                         ("design", chart.get("design_planets", {}))):
        if not isinstance(source, dict):
            continue
        for planet, pdata in source.items():
            if not isinstance(pdata, dict) or not pdata.get("gate"):
                continue
            gate_num = pdata.get("gate")
            activations.append({
                "side": side,
                "planet": planet,
                "gate": gate_num,
                "line": pdata.get("line"),
                "color": pdata.get("color"),
                "tone": pdata.get("tone"),
                "base": pdata.get("base"),
                "gate_name": GATE_NAMES.get(int(gate_num), f"Gate {gate_num}") if isinstance(gate_num, int) else f"Gate {gate_num}",
                "center": CENTER_MAP.get(GATE_CENTER.get(int(gate_num), ""), "unknown") if isinstance(gate_num, int) else "unknown",
                "significance": PLANET_SIGNIFICANCE.get(planet, "chart-specific planetary emphasis"),
            })

    return {
        "meta": meta,
        "centers": centers,
        "gates": gates,
        "channels": channels,
        "variables": variables,
        "activations": activations,
    }


# ── Route ──────────────────────────────────────────────────────────────


@router.post("", response_model=BodygraphResponse, status_code=status.HTTP_200_OK)
async def bodygraph(
    body: BodygraphRequest,
    _api_key: str = Depends(require_api_key),
) -> BodygraphResponse:
    try:
        result = await compute_natal_chart(
            name=body.name, year=body.year, month=body.month, day=body.day,
            hour=body.hour, minute=body.minute,
            lat=body.lat or 0.0, lon=body.lon or 0.0,
            location=body.location, timezone=body.timezone,
        )
    except Exception as exc:
        logger.exception("Bodygraph computation failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                           detail=f"Engine unavailable: {exc}") from exc

    if result.get("error"):
        return BodygraphResponse(success=False, error=result.get("detail", "Unknown error"))

    payload = _build_bodygraph_payload(result)
    return BodygraphResponse(success=True, data=payload)


# ── No-auth test endpoint ─────────────────────────────────────────────


@router.post("/noauth", response_model=BodygraphResponse, status_code=status.HTTP_200_OK)
async def bodygraph_noauth(body: BodygraphRequest) -> BodygraphResponse:
    try:
        result = await compute_natal_chart(
            name=body.name, year=body.year, month=body.month, day=body.day,
            hour=body.hour, minute=body.minute,
            lat=body.lat or 0.0, lon=body.lon or 0.0,
            location=body.location, timezone=body.timezone,
        )
    except Exception as exc:
        logger.exception("Bodygraph (noauth) failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                           detail=f"Engine unavailable: {exc}") from exc

    if result.get("error"):
        return BodygraphResponse(success=False, error=result.get("detail", "Unknown error"))

    payload = _build_bodygraph_payload(result)
    return BodygraphResponse(success=True, data=payload)
