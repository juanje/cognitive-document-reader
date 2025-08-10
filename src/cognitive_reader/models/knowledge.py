"""Knowledge structures and language definitions."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LanguageCode(str, Enum):
    """Supported language codes for document processing."""

    AUTO = "auto"
    EN = "en"
    ES = "es"


class ConceptDefinition(BaseModel):
    """Key concept with cognitive-refined definition according to SPECS v2.0."""

    concept_id: str = Field(description="Unique identifier (e.g., 'sedentarismo', 'movimiento_natural')")
    name: str = Field(description="Human-readable name of the concept")
    definition: str = Field(description="Cognitive-refined definition")
    first_mentioned_in: str = Field(description="Section ID where this concept was first identified")
    relevant_sections: list[str] = Field(default_factory=list, description="Section IDs where concept is relevant")
