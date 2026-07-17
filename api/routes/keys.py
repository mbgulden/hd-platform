"""
API Key management endpoints — POST /v1/keys.

Provides registration, status checking, and revocation for API keys.
In dev mode (no PostgreSQL), uses in-memory storage.
When PostgreSQL is available, uses the `api_keys` and `users` tables.
"""

import hashlib
import logging
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import APIKey, UsageLog, User, async_session_factory
from ..middleware import require_api_key, _hash_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/keys", tags=["api-keys"])

# In-memory store for dev mode: key_hash → {name, tier, rate_limit, email, created_at, usage_count}
_memory_store: dict = {}

# Track whether we've detected DB availability
_db_available: Optional[bool] = None


async def _db_is_available() -> bool:
    """Check if PostgreSQL is actually reachable (not just configured)."""
    global _db_available
    if _db_available is not None:
        return _db_available

    if async_session_factory is None:
        _db_available = False
        return False

    try:
        async with async_session_factory() as session:
            await session.execute(select(func.now()))
        _db_available = True
        return True
    except Exception:
        _db_available = False
        return False


# ── Request / Response schemas ────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, pattern=r".+@.+")
    name: str = Field(default="Default", min_length=1, max_length=255)
    tier: str = Field(default="free", pattern="^(free|pro|enterprise)$")


class RegisterResponse(BaseModel):
    success: bool
    api_key: Optional[str] = None
    key_prefix: Optional[str] = None
    tier: Optional[str] = None
    rate_limit: Optional[int] = None
    message: Optional[str] = None


class StatusResponse(BaseModel):
    success: bool
    tier: Optional[str] = None
    rate_limit: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    usage_count: Optional[int] = None
    message: Optional[str] = None


class RevokeResponse(BaseModel):
    success: bool
    message: Optional[str] = None


# ── Tier configuration ─────────────────────────────────────────────────

TIER_CONFIG = {
    "free": {"rate_limit": 100, "description": "100 requests/minute"},
    "pro": {"rate_limit": 1000, "description": "1,000 requests/minute"},
    "enterprise": {"rate_limit": 10000, "description": "10,000 requests/minute"},
}


def _generate_api_key() -> str:
    """Generate a new API key: hd_ prefix + 32 random URL-safe characters."""
    return f"hd_{secrets.token_urlsafe(32)}"


# ── Routes ─────────────────────────────────────────────────────────────


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_key(body: RegisterRequest) -> RegisterResponse:
    """
    Register a new API key.

    Provide an email address and optional key name / tier.
    Returns the full API key — **save it immediately**, it won't be shown again.
    """
    tier = body.tier.lower()
    if tier not in TIER_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier '{tier}'. Valid: free, pro, enterprise",
        )

    rate_limit = TIER_CONFIG[tier]["rate_limit"]
    raw_key = _generate_api_key()
    key_hash = _hash_key(raw_key)
    key_prefix = raw_key[:10]  # First 10 chars for identification

    if not await _db_is_available():
        # In-memory dev mode
        _memory_store[key_hash] = {
            "name": body.name,
            "tier": tier,
            "rate_limit": rate_limit,
            "email": body.email,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "usage_count": 0,
        }
        logger.info("Dev-mode key registered: %s (tier=%s)", key_prefix, tier)
    else:
        # PostgreSQL mode
        try:
            async with async_session_factory() as session:
                session: AsyncSession

                # Find or create user
                result = await session.execute(
                    select(User).where(User.email == body.email)
                )
                user = result.scalar_one_or_none()

                if user is None:
                    user = User(email=body.email)
                    session.add(user)
                    await session.flush()

                # Create API key
                api_key = APIKey(
                    user_id=user.id,
                    key_hash=key_hash,
                    name=body.name,
                    tier=tier,
                    rate_limit=rate_limit,
                )
                session.add(api_key)
                await session.commit()

                logger.info("Key registered for %s: %s (tier=%s)", body.email, key_prefix, tier)

        except Exception as exc:
            logger.error("Failed to register key: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable — try again later",
            )

    return RegisterResponse(
        success=True,
        api_key=raw_key,
        key_prefix=key_prefix,
        tier=tier,
        rate_limit=rate_limit,
        message=f"Key registered ({tier} tier, {rate_limit} req/min). Save your key — it won't be shown again.",
    )


@router.get("/status", response_model=StatusResponse)
async def key_status(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> StatusResponse:
    """
    Get the status of the API key passed in the X-API-Key header.

    Returns tier, rate limit, creation date, and usage count.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    key_hash = _hash_key(x_api_key)

    if not await _db_is_available():
        entry = _memory_store.get(key_hash)
        if entry is None:
            # Check if key was registered — if not, treat as unknown
            return StatusResponse(
                success=False,
                message="API key not found. Register at POST /v1/keys/register",
            )
        return StatusResponse(
            success=True,
            tier=entry["tier"],
            rate_limit=entry["rate_limit"],
            name=entry["name"],
            created_at=entry["created_at"],
            usage_count=entry["usage_count"],
        )

    # PostgreSQL mode
    try:
        async with async_session_factory() as session:
            session: AsyncSession

            result = await session.execute(
                select(APIKey).where(APIKey.key_hash == key_hash)
            )
            api_key = result.scalar_one_or_none()

            if api_key is None:
                return StatusResponse(
                    success=False,
                    message="API key not found. Register at POST /v1/keys/register",
                )

            # Count usage
            usage_result = await session.execute(
                select(func.count(UsageLog.id)).where(UsageLog.api_key_id == api_key.id)
            )
            usage_count = usage_result.scalar() or 0

            return StatusResponse(
                success=True,
                tier=api_key.tier,
                rate_limit=api_key.rate_limit,
                name=api_key.name,
                created_at=api_key.created_at.isoformat() if api_key.created_at else None,
                usage_count=usage_count,
            )

    except Exception as exc:
        logger.error("Failed to check key status: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable — try again later",
        )


@router.delete("/revoke", response_model=RevokeResponse)
async def revoke_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> RevokeResponse:
    """
    Revoke the API key passed in the X-API-Key header.

    Once revoked, the key can no longer be used. This action is permanent.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    key_hash = _hash_key(x_api_key)
    key_prefix = x_api_key[:10]

    if not await _db_is_available():
        if key_hash not in _memory_store:
            return RevokeResponse(
                success=False,
                message="API key not found.",
            )
        del _memory_store[key_hash]
        logger.info("Dev-mode key revoked: %s", key_prefix)
        return RevokeResponse(
            success=True,
            message="API key revoked successfully.",
        )

    # PostgreSQL mode
    try:
        async with async_session_factory() as session:
            session: AsyncSession

            result = await session.execute(
                select(APIKey).where(APIKey.key_hash == key_hash)
            )
            api_key = result.scalar_one_or_none()

            if api_key is None:
                return RevokeResponse(
                    success=False,
                    message="API key not found.",
                )

            await session.delete(api_key)
            await session.commit()

            logger.info("Key revoked: %s", key_prefix)
            return RevokeResponse(
                success=True,
                message="API key revoked successfully.",
            )

    except Exception as exc:
        logger.error("Failed to revoke key: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable — try again later",
        )
