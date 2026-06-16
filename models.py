"""
models.py
---------
Pydantic data models for API request / response validation and serialisation.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TranscriptRequest(BaseModel):
    """Payload received at POST /extract-skills."""

    transcript: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Raw interview transcript text to analyse.",
        examples=["I have experience with Python, Django, and AWS."],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"transcript": "I have experience with Python and AWS."}
            ]
        }
    }


class SkillExtractionResponse(BaseModel):
    """
    Structured extraction result returned to the caller.

    Fields
    ------
    skills      : Deduplicated, canonicalised list of detected skills.
    categories  : Skills grouped by category (languages, frameworks, etc.).
    total_found : Convenience count of unique skills found.
    """

    skills: List[str] = Field(
        default_factory=list,
        description="Flat, deduplicated list of canonical skill names.",
    )
    categories: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Skills grouped by category.",
    )
    total_found: int = Field(
        0,
        description="Total number of unique skills detected.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "skills": ["Python", "Django", "AWS"],
                    "categories": {
                        "languages": ["Python"],
                        "frameworks": ["Django"],
                        "cloud": ["AWS"],
                    },
                    "total_found": 3,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Returned when the API encounters a handled error."""

    detail: str = Field(..., description="Human-readable error description.")
    code: Optional[str] = Field(None, description="Machine-readable error code.")
