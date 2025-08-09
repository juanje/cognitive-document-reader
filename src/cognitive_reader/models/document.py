"""Document data models for hierarchical structure and knowledge representation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .knowledge import LanguageCode


class DocumentSection(BaseModel):
    """Individual document section with hierarchy information.

    Represents a single section in a document with its content, position
    in the hierarchy, and relationships to other sections.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(description="Unique identifier for the section")
    title: str = Field(description="Section title or heading")
    content: str = Field(description="Raw text content of the section")
    level: int = Field(
        ge=0, description="Hierarchical level (0 = root, 1 = top-level, etc.)"
    )
    parent_id: str | None = Field(
        default=None, description="ID of parent section if any"
    )
    children_ids: list[str] = Field(
        default_factory=list, description="List of child section IDs"
    )
    order_index: int = Field(ge=0, description="Order of appearance in document")


class SectionSummary(BaseModel):
    """Summary of a document section with extracted key concepts.

    Contains the processed understanding of a section including
    its summary and key concepts for cognitive reading.
    """

    section_id: str = Field(description="ID of the section this summary describes")
    title: str = Field(description="Section title")
    summary: str = Field(description="Generated summary of the section")
    key_concepts: list[str] = Field(
        default_factory=list, description="Key concepts identified in this section"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the summary quality",
    )


class DocumentKnowledge(BaseModel):
    """Complete knowledge extracted from a document.

    This is the main output of the cognitive reading process,
    containing all extracted knowledge, summaries, and metadata.
    """

    document_title: str = Field(description="Title of the processed document")
    document_summary: str = Field(
        description="High-level summary of the entire document"
    )
    detected_language: LanguageCode = Field(
        description="Auto-detected or specified language"
    )

    sections: list[DocumentSection] = Field(
        default_factory=list, description="All document sections in hierarchical order"
    )
    section_summaries: dict[str, SectionSummary] = Field(
        default_factory=dict,
        description="Summaries for each section keyed by section ID",
    )

    processing_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the processing (timing, model used, etc.)",
    )

    def get_section_by_id(self, section_id: str) -> DocumentSection | None:
        """Get a section by its ID.

        Args:
            section_id: The ID of the section to retrieve.

        Returns:
            The section if found, None otherwise.
        """
        for section in self.sections:
            if section.id == section_id:
                return section
        return None

    def get_top_level_sections(self) -> list[DocumentSection]:
        """Get all top-level sections (level 1).

        Returns:
            List of top-level sections ordered by appearance.
        """
        return [section for section in self.sections if section.level == 1]

    def get_children_of_section(self, section_id: str) -> list[DocumentSection]:
        """Get all direct children of a section.

        Args:
            section_id: The ID of the parent section.

        Returns:
            List of child sections ordered by appearance.
        """
        parent_section = self.get_section_by_id(section_id)
        if not parent_section:
            return []

        children = []
        for child_id in parent_section.children_ids:
            child = self.get_section_by_id(child_id)
            if child:
                children.append(child)

        # Sort by order_index to maintain document order
        return sorted(children, key=lambda s: s.order_index)
