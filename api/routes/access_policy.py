"""Public/protected routing policy for HD Engine operational endpoints.

Revenue and report-delivery paths intentionally remain public at the edge. Diagnostic
inventory endpoints require an explicit operator token or Cloudflare Access service-token
headers so Access policy changes do not accidentally expose runtime internals.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(tags=["access-policy"])

# Public by product requirement: checkout/report delivery must work without Cloudflare
# Access identity prompts. API-key protected computation endpoints remain protected by
# their own X-API-Key dependency and are not listed here.
PUBLIC_OPERATIONAL_ROUTES = {
    "GET /ping",
    "GET /api/health",
    "POST /api/checkout/create-session",
    "GET /api/checkout/session",
    "POST /api/public/compute-chart",
    "GET /api/public/bodygraph",
    "POST /api/public/bodygraph",
    "GET /api/public/catalog",
    "POST /api/public/capture-lead",
    "GET /api/reports/download/{filename}",
}

PROTECTED_DIAGNOSTIC_ROUTES = {
    "GET /api/diagnostics/routes",
    "GET /api/reports",
}


def _access_configured() -> bool:
    return bool(
        os.environ.get("HDE_DIAGNOSTIC_TOKEN")
        or (
            os.environ.get("CF_ACCESS_CLIENT_ID")
            and os.environ.get("CF_ACCESS_CLIENT_SECRET")
        )
    )


def require_diagnostic_access(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    cf_access_client_id: Optional[str] = Header(None, alias="CF-Access-Client-Id"),
    cf_access_client_secret: Optional[str] = Header(None, alias="CF-Access-Client-Secret"),
) -> None:
    """Require either an operator bearer token or Cloudflare Access service token.

    The failure mode is closed: if no diagnostic credential is configured, diagnostic
    routes return 503 instead of silently becoming public.
    """
    expected_token = os.environ.get("HDE_DIAGNOSTIC_TOKEN")
    if expected_token and authorization == f"Bearer {expected_token}":
        return

    expected_cf_id = os.environ.get("CF_ACCESS_CLIENT_ID")
    expected_cf_secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if (
        expected_cf_id
        and expected_cf_secret
        and cf_access_client_id == expected_cf_id
        and cf_access_client_secret == expected_cf_secret
    ):
        return

    if not _access_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Diagnostic access is not configured.",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Diagnostic access requires Cloudflare Access or operator bearer token.",
    )


@router.get("/api/health", tags=["health"])
async def public_health() -> dict[str, str]:
    """Public liveness probe safe for uptime monitors and Cloudflare health checks."""
    return {"status": "ok", "service": "hd-platform-api"}


@router.get("/api/diagnostics/routes")
async def diagnostic_routes(_access: None = Depends(require_diagnostic_access)) -> dict[str, Any]:
    """Access-protected route policy inventory for operators."""
    return {
        "public": sorted(PUBLIC_OPERATIONAL_ROUTES),
        "protected": sorted(PROTECTED_DIAGNOSTIC_ROUTES),
    }
