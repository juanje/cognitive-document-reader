"""LLM response models for structured parsing."""

from pydantic import BaseModel, Field


class SectionSummary(BaseModel):
    """Section summary with metadata."""

    summary: str = Field(description="Extracted summary of the section")
    key_concepts: list[str] = Field(
        default_factory=list, description="Key concepts identified in the section"
    )
    model_used: str = Field(description="Model that generated this summary")


class DocumentSummary(BaseModel):
    """Document-level summary with metadata."""

    summary: str = Field(description="Overall document summary")
    total_sections: int = Field(description="Total number of sections processed")
    model_used: str = Field(description="Model that generated this summary")


# New structured response models for LLM output
class SectionSummaryResponse(BaseModel):
    """Structured response for section summarization."""

    summary: str = Field(description="Clear, concise summary of the section content")
    key_concepts: list[str] = Field(
        max_length=5,
        description="List of up to 5 key concepts found in the section (important terms, ideas, or entities)",
    )


class ConceptDefinitionResponse(BaseModel):
    """Structured response for concept definition."""

    definition: str = Field(
        description="Clear, direct definition of the concept without meta-references"
    )
