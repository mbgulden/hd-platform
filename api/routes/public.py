"""
Public chart endpoint — POST /v1/public/compute-chart.

Accepts birth data, calculates a natal chart using the calculation engine,
and returns a simplified chart structure. No API key required.
Rate-limited to 10 calls per minute per IP.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, model_validator

from shared.mcp_client import compute_natal_chart
from shared.redis_client import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(tags=["public"])


class BirthData(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Person's name")
    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23)")
    minute: int = Field(0, ge=0, le=59, description="Birth minute (0-59)")
    location: Optional[str] = Field(None, max_length=500, description="Location name")
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude")
    lon: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude")
    timezone: Optional[str] = Field(None, max_length=100, description="IANA timezone string")

    @model_validator(mode="after")
    def _check_coords(self) -> "BirthData":
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must both be provided or both omitted")
        return self


class SimplifiedChart(BaseModel):
    name: str
    hd_type: str
    profile: str
    authority: str
    strategy: str
    definition: str
    defined_centers: List[str]
    undefined_centers: List[str]
    signature: str
    not_self_theme: str


class SimplifiedChartResponse(BaseModel):
    success: bool
    data: Optional[SimplifiedChart] = None
    error: Optional[str] = None


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


async def check_ip_rate_limit(ip: str, limit: int = 10, window: int = 60) -> bool:
    try:
        redis = await get_redis()
        key = f"rate_limit:ip:{ip}"
        
        # Simple count check
        current = await redis.get(key)
        if current is not None and int(current) >= limit:
            return False
            
        async with redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window)
            await pipe.execute()
        return True
    except Exception as e:
        logger.warning("IP rate limiting check failed (Redis offline?): %s", e)
        return True # Fallback to allow if Redis is down


@router.post("/public/compute-chart", response_model=SimplifiedChartResponse, status_code=status.HTTP_200_OK)
async def compute_public_chart(
    body: BirthData,
    request: Request,
) -> SimplifiedChartResponse:
    # 1. Enforce rate limiting
    ip = get_client_ip(request)
    if not await check_ip_rate_limit(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 calls per minute."
        )

    # 2. Compute chart
    try:
        result = await compute_natal_chart(
            name=body.name,
            year=body.year,
            month=body.month,
            day=body.day,
            hour=body.hour,
            minute=body.minute,
            lat=body.lat or 0.0,
            lon=body.lon or 0.0,
            location=body.location,
            timezone=body.timezone,
        )
    except Exception as exc:
        logger.exception("Unhandled exception in compute_public_chart")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MCP engine unavailable",
        ) from exc

    if result.get("error"):
        return SimplifiedChartResponse(success=False, error=result.get("detail", "Unknown MCP error"))

    # 3. Format and return
    hd_type = result.get("hd_type") or result.get("type", "")
    
    data = SimplifiedChart(
        name=result.get("name", ""),
        hd_type=hd_type,
        profile=result.get("profile", ""),
        authority=result.get("authority", ""),
        strategy=result.get("strategy", ""),
        definition=result.get("definition", ""),
        defined_centers=result.get("defined_centers", []),
        undefined_centers=result.get("undefined_centers", []),
        signature=result.get("signature", ""),
        not_self_theme=result.get("not_self_theme", "") or result.get("not_self", "")
    )
    
    return SimplifiedChartResponse(success=True, data=data)
