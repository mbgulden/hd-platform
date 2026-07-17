"""HD Academy course catalog endpoints.

Public, read-only LMS catalog surface for the HD Education project. The
catalog is intentionally file-backed for the first MVP so the static site,
API, and future checkout integration share one source of truth without
requiring a database migration.
"""

from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field


router = APIRouter(prefix="/academy", tags=["academy"])

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "data" / "academy" / "catalog.json"


class LessonModule(BaseModel):
    title: str
    lessons: List[str]


class AcademyCourse(BaseModel):
    slug: str
    title: str
    level: str
    price: str
    duration: str
    format: List[str]
    outcome: str
    modules: List[LessonModule]
    status: str
    checkout_url: Optional[str] = None


class AcademyTrack(BaseModel):
    slug: str
    name: str
    price: str
    includes: List[str]


class AcademyProgram(BaseModel):
    slug: str
    name: str
    tagline: str
    positioning: str
    audience: List[str]
    pricing: Dict[str, str]
    launch_mvp: Dict[str, str]


class AcademyCatalogResponse(BaseModel):
    success: bool = True
    program: AcademyProgram
    courses: List[AcademyCourse]
    tracks: List[AcademyTrack]


class AcademyCourseResponse(BaseModel):
    success: bool = True
    course: AcademyCourse
    related_tracks: List[AcademyTrack] = Field(default_factory=list)


@lru_cache(maxsize=1)
def load_academy_catalog() -> Dict[str, Any]:
    """Load and cache the file-backed Academy catalog."""
    try:
        with CATALOG_PATH.open("r", encoding="utf-8") as catalog_file:
            catalog = json.load(catalog_file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Academy catalog not found at {CATALOG_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Academy catalog is invalid JSON: {exc}") from exc

    required_keys = {"program", "courses", "tracks"}
    missing = required_keys.difference(catalog)
    if missing:
        raise RuntimeError(f"Academy catalog missing keys: {', '.join(sorted(missing))}")
    return catalog


@router.get("", response_model=AcademyCatalogResponse, status_code=status.HTTP_200_OK)
async def academy_catalog() -> AcademyCatalogResponse:
    """Return the HD Academy program, courses, and pricing tracks."""
    catalog = load_academy_catalog()
    return AcademyCatalogResponse(**catalog)


@router.get("/courses/{slug}", response_model=AcademyCourseResponse, status_code=status.HTTP_200_OK)
async def academy_course(slug: str) -> AcademyCourseResponse:
    """Return one HD Academy course by slug."""
    catalog = load_academy_catalog()
    for course in catalog["courses"]:
        if course["slug"] == slug:
            return AcademyCourseResponse(course=course, related_tracks=catalog["tracks"])

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Academy course not found: {slug}",
    )
