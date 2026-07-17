"""
Engine client for HD Platform — direct import, no HTTP/MCP transport.

Imports the OpenHumanDesignMCP engine directly (same pattern as
reports/server.py) so the FastAPI wrapper can compute charts
without relying on an external MCP server.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# ── Engine path ────────────────────────────────────────────────────────
ENGINE_PATH = os.environ.get(
    "ENGINE_PATH",
    "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src",
)
sys.path.insert(0, ENGINE_PATH)

from cosmic_calculator import calculate_natal_chart
from ephemeris_engine import init_ephemeris
from geo_resolver import local_to_utc
from transit_engine import compute_transit_overlay, datetime_to_jd

# Initialise once at module load (idempotent)
init_ephemeris()

logger = logging.getLogger(__name__)


TYPE_COMPATIBILITY = {
    ("Generator", "Generator"): "Shared sustainable life-force; watch for mutual frustration when neither person is responding cleanly.",
    ("Generator", "Manifesting Generator"): "High-energy response field; move fast after both bodies have a yes, not before.",
    ("Manifesting Generator", "Manifesting Generator"): "Fast catalytic field; build in permission to pivot without making either person wrong.",
    ("Projector", "Generator"): "Guidance plus energy; works best when the Projector is recognized and the Generator has a real sacral yes.",
    ("Projector", "Manifesting Generator"): "Guidance plus acceleration; the Projector needs recognition and the MG needs room to iterate.",
    ("Projector", "Projector"): "Mutual seeing; protect rest and avoid trying to force generator-style output from the bond.",
    ("Manifestor", "Generator"): "Initiation plus response; the Manifestor informs, the Generator checks for a body yes.",
    ("Manifestor", "Projector"): "Initiation plus guidance; clarity improves when the Manifestor informs and the Projector waits for recognition.",
    ("Manifestor", "Manifestor"): "Independent initiation field; peace comes from informing before impact.",
    ("Reflector", "Generator"): "Sampling plus consistency; give the Reflector time and let the Generator be the stable energetic reference point.",
    ("Reflector", "Projector"): "Sensitive guidance field; protect spacious timing and environmental fit.",
    ("Reflector", "Manifestor"): "Sensitive mirror plus initiation; inform gently and allow the Reflector time to metabolize impact.",
    ("Reflector", "Reflector"): "Highly environmental mirror; choose places and timing carefully before making the relationship mean anything fixed.",
}


def _gate_set(chart: Dict[str, Any]) -> set[int]:
    return {int(g) for g in chart.get("all_active_gates") or chart.get("defined_gates") or []}


def _type_compatibility(type_a: Optional[str], type_b: Optional[str]) -> Optional[str]:
    if not type_a or not type_b:
        return None
    return TYPE_COMPATIBILITY.get((type_a, type_b)) or TYPE_COMPATIBILITY.get((type_b, type_a))


def _enrich_composite(composite: Optional[Dict[str, Any]], chart_a: Dict[str, Any], chart_b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not composite:
        return composite
    gates_a = _gate_set(chart_a)
    gates_b = _gate_set(chart_b)
    enriched = dict(composite)
    enriched.setdefault("shared_gates", sorted(gates_a & gates_b))
    type_a = chart_a.get("hd_type") or chart_a.get("type")
    type_b = chart_b.get("hd_type") or chart_b.get("type")
    enriched.setdefault("type_a", type_a)
    enriched.setdefault("type_b", type_b)
    enriched.setdefault("type_compatibility", _type_compatibility(type_a, type_b))
    enriched.setdefault("type_dynamic", enriched.get("type_compatibility"))
    for channel in enriched.get("electromagnetic_channels", []):
        if isinstance(channel, dict):
            gates = channel.get("gates") or []
            channel["gates_label"] = "–".join(str(g) for g in gates)
            channel.setdefault("description", "Notice the spark, then name the agreement this channel asks from you.")
    return enriched


# ---------------------------------------------------------------------------
# Public API — async wrappers matching the original signatures
# ---------------------------------------------------------------------------


async def compute_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    lat: float,
    lon: float,
    minute: int = 0,
    location: Optional[str] = None,
    timezone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a natal (birth) chart via direct engine import.

    Returns the full chart dict on success, or ``{"error": True,
    "detail": "..."}`` on failure.
    """
    try:
        # Convert local birth time to UTC — critical for correct chart
        decimal_hour = hour + minute / 60.0
        if location or timezone:
            utc_year, utc_month, utc_day, utc_decimal_hour = local_to_utc(
                year, month, day, decimal_hour,
                location=location or timezone, lat=lat, lon=lon
            )
        else:
            # No location/timezone info — assume the caller already sent UTC
            utc_year, utc_month, utc_day, utc_decimal_hour = year, month, day, decimal_hour

        utc_hour = int(utc_decimal_hour)
        utc_minute = int((utc_decimal_hour % 1) * 60)
        birth_dt = datetime(utc_year, utc_month, utc_day, utc_hour, utc_minute)
        chart = calculate_natal_chart(
            name=name,
            birth_dt=birth_dt,
            lat=lat,
            lon=lon,
            timezone=timezone or "UTC",
        )
        logger.info("Natal chart computed for %s", name)
        return chart
    except Exception as exc:
        logger.exception("Engine error computing natal chart for %s", name)
        return {"error": True, "detail": str(exc)}


async def compute_transits(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    lat: float,
    lon: float,
    minute: int = 0,
    location: Optional[str] = None,
    timezone: Optional[str] = None,
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a transit overlay for a natal chart via direct engine import.

    Parameters
    ----------
    target_date : str, optional
        ISO date string (YYYY-MM-DD) for the transit snapshot.
        Defaults to today when omitted.
    """
    try:
        # Convert local birth time to UTC — critical for correct chart
        decimal_hour = hour + minute / 60.0
        if location or timezone:
            utc_year, utc_month, utc_day, utc_decimal_hour = local_to_utc(
                year, month, day, decimal_hour,
                location=location or timezone, lat=lat, lon=lon
            )
        else:
            utc_year, utc_month, utc_day, utc_decimal_hour = year, month, day, decimal_hour

        utc_hour = int(utc_decimal_hour)
        utc_minute = int((utc_decimal_hour % 1) * 60)
        birth_dt = datetime(utc_year, utc_month, utc_day, utc_hour, utc_minute)
        natal = calculate_natal_chart(
            name=name,
            birth_dt=birth_dt,
            lat=lat,
            lon=lon,
            timezone=timezone or "UTC",
        )

        if target_date:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            target_jd = datetime_to_jd(target_dt)
        else:
            target_jd = None  # defaults to now inside the engine

        overlay = compute_transit_overlay(natal, target_jd)

        logger.info("Transit overlay computed for %s", name)
        return {
            "natal": natal,
            "overlay": overlay,
        }
    except Exception as exc:
        logger.exception("Engine error computing transits for %s", name)
        return {"error": True, "detail": str(exc)}


async def compute_synastry(
    name_a: str,
    birth_a: Dict[str, Any],
    name_b: str,
    birth_b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute synastry (relationship composite) between two birth charts.

    Parameters
    ----------
    birth_a, birth_b : dict
        Dicts containing keys: year, month, day, hour, lat, lon,
        and optionally minute, location, timezone.
    """
    try:
        # Convert local birth times to UTC — critical for correct charts
        def _birth_dt_from_dict(birth: Dict[str, Any]) -> datetime:
            hour = birth.get("hour", 12)
            minute = birth.get("minute", 0)
            decimal_hour = hour + minute / 60.0
            loc = birth.get("location") or birth.get("timezone")
            if loc:
                lat = birth.get("lat") or 0.0
                lon = birth.get("lon") or 0.0
                utc_year, utc_month, utc_day, utc_decimal_hour = local_to_utc(
                    birth["year"], birth["month"], birth["day"], decimal_hour,
                    location=loc, lat=lat, lon=lon
                )
            else:
                utc_year, utc_month, utc_day, utc_decimal_hour = (
                    birth["year"], birth["month"], birth["day"], decimal_hour
                )
            utc_hour = int(utc_decimal_hour)
            utc_minute = int((utc_decimal_hour % 1) * 60)
            return datetime(utc_year, utc_month, utc_day, utc_hour, utc_minute)

        birth_dt_a = _birth_dt_from_dict(birth_a)
        birth_dt_b = _birth_dt_from_dict(birth_b)

        chart_a = calculate_natal_chart(
            name=name_a,
            birth_dt=birth_dt_a,
            lat=birth_a.get("lat") or 0.0,
            lon=birth_a.get("lon") or 0.0,
            timezone=birth_a.get("timezone", "UTC"),
        )
        chart_b = calculate_natal_chart(
            name=name_b,
            birth_dt=birth_dt_b,
            lat=birth_b.get("lat") or 0.0,
            lon=birth_b.get("lon") or 0.0,
            timezone=birth_b.get("timezone", "UTC"),
        )

        # Optional composite (synastry_engine may not exist in all versions)
        try:
            from synastry_engine import calculate_composite
            composite = calculate_composite(_gate_set(chart_a), _gate_set(chart_b), name_a, name_b)
            composite = _enrich_composite(composite, chart_a, chart_b)
        except ImportError:
            logger.warning("synastry_engine not available — composite skipped")
            composite = None

        logger.info("Synastry computed for %s & %s", name_a, name_b)
        return {
            "chart_a": chart_a,
            "chart_b": chart_b,
            "composite": composite,
        }
    except Exception as exc:
        logger.exception("Engine error computing synastry for %s & %s", name_a, name_b)
        return {"error": True, "detail": str(exc)}
