"""Document data models for hierarchical structure and knowledge representation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .knowledge import ConceptDefinition, LanguageCode


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
    is_heading: bool = Field(
        default=False, description="True if this section represents a real heading (H1, H2, etc.)"
    )


class SectionSummary(BaseModel):
    """Summary of a document section according to SPECS v2.0."""

    section_id: str = Field(description="Unique identifier for the section")
    title: str = Field(description="Section title (cleaned)")
    summary: str = Field(description="Cognitive-refined summary of the section")
    key_concepts: list[str] = Field(default_factory=list, description="List of key concepts (concept_ids)")
    parent_id: str | None = Field(default=None, description="Parent section ID (None for root)")
    children_ids: list[str] = Field(default_factory=list, description="Child section IDs")
    level: int = Field(description="Hierarchy level (0=document, 1=chapter, 2=section, etc.)")
    order_index: int = Field(description="Order of appearance in document")


class CognitiveKnowledge(BaseModel):
    """Complete cognitive knowledge extracted from a document according to SPECS v2.0.

    This is the main output of the cognitive reading process for RAG and fine-tuning.
    """

    # Document Metadata
    document_title: str = Field(description="Title of the processed document")
    detected_language: LanguageCode = Field(description="Auto-detected or specified language")

    # Hierarchical Summaries (optimized for RAG chunks)
    hierarchical_summaries: dict[str, SectionSummary] = Field(
        default_factory=dict, description="Hierarchical summaries by section_id"
    )

    # Concepts (top-level list for consistent terminology)
    concepts: list[ConceptDefinition] = Field(
        default_factory=list, description="Key concepts with cognitive-refined definitions"
    )

    # Hierarchy Navigation (essential for RAG context)
    hierarchy_index: dict[str, list[str]] = Field(
        default_factory=dict, description="Sections by hierarchy level: {'0': ['book'], '1': ['cap_1', 'cap_2']}"
    )
    parent_child_map: dict[str, list[str]] = Field(
        default_factory=dict, description="Parent to children mapping for navigation"
    )

    # Document Statistics (useful for apps consuming the data)
    total_sections: int = Field(description="Total number of sections processed")
    avg_summary_length: int = Field(description="Average summary length in characters")
    total_concepts: int = Field(description="Total number of concepts identified")

    def get_summary_by_id(self, section_id: str) -> SectionSummary | None:
        """Get a section summary by its ID.

        Args:
            section_id: The ID of the section to retrieve.

        Returns:
            The section summary if found, None otherwise.
        """
        return self.hierarchical_summaries.get(section_id)

    def get_concept_by_id(self, concept_id: str) -> ConceptDefinition | None:
        """Get a concept by its ID.

        Args:
            concept_id: The ID of the concept to retrieve.

        Returns:
            The concept if found, None otherwise.
        """
        for concept in self.concepts:
            if concept.concept_id == concept_id:
                return concept
        return None

    def get_children_of_section(self, section_id: str) -> list[str]:
        """Get all direct children IDs of a section.

        Args:
            section_id: The ID of the parent section.

        Returns:
            List of child section IDs.
        """
        return self.parent_child_map.get(section_id, [])
