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
        gate_a, gate_b = ch_data["gates"]
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
            "name": ch_data.get("name", ""),
        }
        if state == "hanging":
            ch_entry["hanging_gate"] = gate_a if gate_a in all_active_gates else gate_b
        channels[channel_id] = ch_entry

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

    return {
        "meta": meta,
        "centers": centers,
        "gates": gates,
        "channels": channels,
        "variables": variables,
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
