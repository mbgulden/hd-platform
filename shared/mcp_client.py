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
from transit_engine import compute_transit_overlay, datetime_to_jd

# Initialise once at module load (idempotent)
init_ephemeris()

logger = logging.getLogger(__name__)


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
        birth_dt = datetime(year, month, day, hour, minute)
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
        birth_dt = datetime(year, month, day, hour, minute)
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
        birth_dt_a = datetime(
            birth_a["year"],
            birth_a["month"],
            birth_a["day"],
            birth_a.get("hour", 12),
            birth_a.get("minute", 0),
        )
        birth_dt_b = datetime(
            birth_b["year"],
            birth_b["month"],
            birth_b["day"],
            birth_b.get("hour", 12),
            birth_b.get("minute", 0),
        )

        chart_a = calculate_natal_chart(
            name=name_a,
            birth_dt=birth_dt_a,
            lat=birth_a.get("lat", 0),
            lon=birth_a.get("lon", 0),
            timezone=birth_a.get("timezone", "UTC"),
        )
        chart_b = calculate_natal_chart(
            name=name_b,
            birth_dt=birth_dt_b,
            lat=birth_b.get("lat", 0),
            lon=birth_b.get("lon", 0),
            timezone=birth_b.get("timezone", "UTC"),
        )

        # Optional composite (synastry_engine may not exist in all versions)
        try:
            from synastry_engine import calculate_composite
            composite = calculate_composite(chart_a, chart_b)
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
