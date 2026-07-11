"""
Synastry endpoint — POST /v1/synastry.

Computes relationship composite between two birth charts, including
electromagnetic gates, dominance channels, compromise channels, and
companion channels.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator

from shared.mcp_client import compute_synastry

from ..middleware import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(tags=["relationships"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class BirthData(BaseModel):
    """Birth data for one person in a synastry pair."""

    name: str = Field(..., min_length=1, max_length=255, description="Person name")
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
    def _check_coords(self) -> "BirthData":
        """Ensure lat/lon are provided together (or both absent)."""
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must both be provided or both omitted")
        return self


class SynastryRequest(BaseModel):
    """Validated body for a synastry (relationship composite) calculation."""

    person_a: BirthData = Field(..., description="First person's birth data")
    person_b: BirthData = Field(..., description="Second person's birth data")


class SynastryResponse(BaseModel):
    """Standard API wrapper for synastry responses."""

    success: bool
    endpoint: str = "/v1/synastry"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post("/synastry", response_model=SynastryResponse, status_code=status.HTTP_200_OK)
@router.post("/match", response_model=SynastryResponse, status_code=status.HTTP_200_OK)
async def synastry_chart(
    body: SynastryRequest,
    _api_key: str = Depends(require_api_key),
) -> SynastryResponse:
    """
    Compute a relationship composite between two birth charts.

    Requires a valid **X-API-Key** header. Available as both
    `/v1/synastry` and `/v1/match`. Returns both individual
    charts plus the composite with electromagnetic gates, channel
    dynamics, compatibility scoring, and combined centers.
    """
    try:
        result = await compute_synastry(
            name_a=body.person_a.name,
            birth_a=body.person_a.model_dump(),
            name_b=body.person_b.name,
            birth_b=body.person_b.model_dump(),
        )
    except Exception as exc:
        logger.exception("Unhandled exception in synastry_chart")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MCP engine unavailable",
        ) from exc

    if result.get("error"):
        return SynastryResponse(success=False, error=result.get("detail", "Unknown MCP error"))

    return SynastryResponse(success=True, data=result)


