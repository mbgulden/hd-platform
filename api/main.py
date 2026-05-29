"""
HD Platform — FastAPI application entry-point.

Start with:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router as v1_router
from shared.database import close_db, init_db
from shared.redis_client import get_redis

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("hd-platform")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle startup and shutdown events for DB and Redis."""
    logger.info("HD Platform starting up …")

    # Initialise database tables (idempotent)
    await init_db()
    logger.info("Database tables ensured.")

    # Warm up Redis connection
    redis = await get_redis()
    await redis.ping()
    logger.info("Redis connection verified.")

    yield  # application runs here

    # Shutdown
    logger.info("HD Platform shutting down …")
    await close_db()
    redis_client = await get_redis()
    await redis_client.aclose()
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="HD Platform API",
    description="Human Design chart computation and transit analysis API",
    version="0.1.0",
    license_info={"name": "AGPLv3", "url": "https://www.gnu.org/licenses/agpl-3.0.html"},
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(v1_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/ping", tags=["health"])
async def ping() -> dict:
    """Simple liveness / readiness probe."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "license": "AGPLv3",
    }
