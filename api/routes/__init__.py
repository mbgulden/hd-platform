"""
HD Platform API route aggregation.

Groups v1 endpoints under a single FastAPI APIRouter.
"""

from fastapi import APIRouter

from .natal import router as natal_router
from .transits import router as transits_router
from .bodygraph import router as bodygraph_router
from .synastry import router as synastry_router
from .academy import router as academy_router

router = APIRouter(prefix="/v1")
router.include_router(natal_router)
router.include_router(transits_router)
router.include_router(bodygraph_router)
router.include_router(synastry_router)
router.include_router(academy_router)
