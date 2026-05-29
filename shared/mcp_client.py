"""
Async HTTP client for the OpenHumanDesign MCP engine.

Uses httpx for async communication with configurable retry logic,
timeouts, and structured error handling.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8765")

DEFAULT_TIMEOUT: float = 30.0
MAX_RETRIES: int = 3
BASE_DELAY: float = 1.0  # seconds, multiplied by 2**attempt for back-off


def _client() -> httpx.AsyncClient:
    """Return a new httpx client with shared defaults (not reused across invocations)."""
    return httpx.AsyncClient(timeout=httpx.Timeout(DEFAULT_TIMEOUT))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _error_dict(endpoint: str, detail: Any) -> Dict[str, Any]:
    """Build a standardised error dict for callers."""
    logger.warning("MCP error on %s: %s", endpoint, detail)
    return {
        "error": True,
        "endpoint": endpoint,
        "detail": str(detail),
    }


async def _post(
    path: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    POST *payload* to *path* on the MCP server with retry + back-off.

    Returns the JSON-parsed response body on success, or a structured
    error dict on failure.
    """
    url = f"{MCP_SERVER_URL.rstrip('/')}{path}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with _client() as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException:
            detail = f"Timeout after {DEFAULT_TIMEOUT}s"
            if attempt == MAX_RETRIES:
                return _error_dict(path, detail)
        except httpx.HTTPStatusError as exc:
            detail = f"HTTP {exc.response.status_code}: {exc.response.text[:500]}"
            if attempt == MAX_RETRIES:
                return _error_dict(path, detail)
        except Exception as exc:
            detail = str(exc)
            if attempt == MAX_RETRIES:
                return _error_dict(path, detail)

        # Exponential back-off: 1s, 2s, 4s
        delay = BASE_DELAY * (2 ** (attempt - 1))
        logger.debug("MCP retry %d/%d for %s — sleeping %.1fs", attempt, MAX_RETRIES, path, delay)
        await asyncio.sleep(delay)

    # Should never be reached; kept for type-safety
    return _error_dict(path, "Max retries exceeded")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def compute_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    lat: float,
    lon: float,
    location: Optional[str] = None,
    timezone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a natal / birth chart via the MCP engine.

    Parameters
    ----------
    name : str
        Person or entity name.
    year, month, day, hour : int
        Birth date / time components.
    lat, lon : float
        Geographic coordinates.
    location : str, optional
        Human-readable location name.
    timezone : str, optional
        IANA timezone string (e.g. 'America/New_York').

    Returns
    -------
    dict
        MCP response body or structured error dict.
    """
    payload: Dict[str, Any] = {
        "name": name,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "lat": lat,
        "lon": lon,
    }
    if location:
        payload["location"] = location
    if timezone:
        payload["timezone"] = timezone

    return await _post("/compute/natal", payload)


async def compute_transits(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    lat: float,
    lon: float,
    location: Optional[str] = None,
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute transit overlays for a given birth chart and target date.

    Parameters
    ----------
    name : str
        Person or entity name.
    year, month, day, hour : int
        Birth date / time components.
    lat, lon : float
        Geographic coordinates.
    location : str, optional
        Human-readable location name.
    target_date : str, optional
        ISO date string for transit snapshot (defaults to today).

    Returns
    -------
    dict
        MCP response body or structured error dict.
    """
    payload: Dict[str, Any] = {
        "name": name,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "lat": lat,
        "lon": lon,
    }
    if location:
        payload["location"] = location
    if target_date:
        payload["target_date"] = target_date

    return await _post("/compute/transits", payload)


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
    name_a, name_b : str
        Names for each chart.
    birth_a, birth_b : dict
        Dicts containing keys: year, month, day, hour, lat, lon,
        and optionally location, timezone.

    Returns
    -------
    dict
        MCP response body or structured error dict.
    """
    payload: Dict[str, Any] = {
        "person_a": {"name": name_a, **birth_a},
        "person_b": {"name": name_b, **birth_b},
    }
    return await _post("/compute/synastry", payload)
