"""
Natal chart endpoint — POST /v1/natal.

Accepts birth data, validates via Pydantic, forwards to the MCP
engine, and returns a standardised API response.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator

from shared.mcp_client import compute_natal_chart

from ..middleware import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/natal", tags=["natal"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class NatalRequest(BaseModel):
    """Validated body for a natal chart calculation."""

    name: str = Field(..., min_length=1, max_length=255, description="Person or entity name")
    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month (1–12)")
    day: int = Field(..., ge=1, le=31, description="Birth day (1–31)")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0–23)")
    minute: int = Field(0, ge=0, le=59, description="Birth minute (0–59)")
    location: Optional[str] = Field(None, max_length=500, description="Place name")
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude")
    lon: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude")
    timezone: Optional[str] = Field(None, max_length=100, description="IANA timezone")

    @model_validator(mode="after")
    def _check_coords(self) -> "NatalRequest":
        """Ensure lat/lon are provided together (or both absent)."""
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must both be provided or both omitted")
        return self


class NatalResponse(BaseModel):
    """Standard API wrapper for natal chart responses."""

    success: bool
    endpoint: str = "/v1/natal"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post("", response_model=NatalResponse, status_code=status.HTTP_200_OK)
async def natal_chart(
    body: NatalRequest,
    _api_key: str = Depends(require_api_key),
) -> NatalResponse:
    """
    Compute a natal (birth) chart.

    Requires a valid **X-API-Key** header.
    """
    try:
        result = await compute_natal_chart(
            name=body.name,
            year=body.year,
            month=body.month,
            day=body.day,
            hour=body.hour,
            lat=body.lat or 0.0,
            lon=body.lon or 0.0,
            location=body.location,
            timezone=body.timezone,
        )
    except Exception as exc:
        logger.exception("Unhandled exception in natal_chart")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MCP engine unavailable",
        ) from exc

    if result.get("error"):
        return NatalResponse(success=False, error=result.get("detail", "Unknown MCP error"))

    return NatalResponse(success=True, data=result)
