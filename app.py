"""
app.py
------
FastAPI application for the Technical Skill Extractor.

Endpoints
---------
POST /extract-skills   – Extract skills from a transcript.
GET  /health           – Health-check / liveness probe.
GET  /skills           – List all known skills and their categories.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    LOG_LEVEL,
)
from extractor import extract_skills
from models import ErrorResponse, SkillExtractionResponse, TranscriptRequest
from skill_database import ALL_SKILLS, SKILL_CATEGORIES

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Startup and shutdown hooks."""
    logger.info("Technical Skill Extractor starting up …")
    logger.info("Loaded %d canonical skills.", len(ALL_SKILLS))
    yield
    logger.info("Technical Skill Extractor shutting down.")


# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)

# Allow all origins in development; restrict in production via env-based config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request timing middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    """Attach X-Process-Time header to every response."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred.", "code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/extract-skills",
    response_model=SkillExtractionResponse,
    summary="Extract technical skills from an interview transcript",
    tags=["Extraction"],
)
async def extract_skills_endpoint(payload: TranscriptRequest) -> SkillExtractionResponse:
    """
    Analyse the provided *transcript* and return all detected technical skills
    with their categories.

    **Pipeline:**
    1. Text cleaning
    2. Alias normalisation
    3. Exact skill matching
    4. Tokenisation
    5. Per-token alias lookup
    6. Fuzzy matching (RapidFuzz, threshold = 85)
    7. Duplicate removal
    8. Categorisation

    **Example:**
    ```json
    { "transcript": "I worked with Python, Django, MySQL, AWS and Docker." }
    ```
    """
    logger.info(
        "POST /extract-skills – transcript length=%d chars", len(payload.transcript)
    )

    try:
        result: Dict = extract_skills(payload.transcript)
    except Exception as exc:  # pragma: no cover
        logger.exception("Extraction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skill extraction failed. Please try again.",
        ) from exc

    return SkillExtractionResponse(**result)


@app.get(
    "/health",
    summary="Health check",
    tags=["System"],
)
async def health_check() -> Dict[str, str]:
    """Liveness probe – returns 200 OK when the service is running."""
    return {"status": "ok", "version": API_VERSION}


@app.get(
    "/skills",
    summary="List all known skills",
    tags=["System"],
)
async def list_skills() -> Dict[str, Any]:
    """
    Return all canonical skills grouped by category.
    Useful for building frontend autocomplete lists or documentation.
    """
    grouped: Dict[str, list] = {}
    for skill, category in SKILL_CATEGORIES.items():
        grouped.setdefault(category, []).append(skill)

    return {
        "total": len(ALL_SKILLS),
        "categories": grouped,
    }
