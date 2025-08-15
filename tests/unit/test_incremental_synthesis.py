"""Unit tests for incremental synthesis functionality in CognitiveReader."""

from __future__ import annotations

import pytest

from cognitive_reader.core.progressive_reader import CognitiveReader
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.document import DocumentSection, SectionSummary
from cognitive_reader.models.knowledge import LanguageCode


class TestIncrementalSynthesis:
    """Test incremental synthesis methods in CognitiveReader."""

    @pytest.fixture
    def test_config(self) -> CognitiveConfig:
        """Create test configuration."""
        return CognitiveConfig(
            dry_run=True,
            mock_responses=True,
            model_name="test_model",
            max_glossary_concepts=10,
        )

    @pytest.fixture
    def reader(self, test_config: CognitiveConfig) -> CognitiveReader:
        """Create CognitiveReader instance."""
        return CognitiveReader(test_config)

    @pytest.fixture
    def sample_summaries(self) -> dict[str, SectionSummary]:
        """Create sample section summaries for testing."""
        return {
            "section_1": SectionSummary(
                section_id="section_1",
                title="Introduction",
                summary="Introduction to cognitive reading",
                key_concepts=["cognitive", "reading", "Document Processing"],
                parent_id=None,
                children_ids=["section_2"],
                level=0,
                order_index=0,
            ),
            "section_2": SectionSummary(
                section_id="section_2",
                title="Methods",
                summary="Methods for document processing",
                key_concepts=["cognitive", "methods", "processing"],
                parent_id="section_1",
                children_ids=[],
                level=1,
                order_index=1,
            ),
        }

    def test_deduplicate_concepts_basic(self, reader: CognitiveReader) -> None:
        """Test basic concept deduplication."""
        concepts = {
            "Cognitive": "Definition of cognitive",  # 21 chars - longest
            "cognitive": "Another definition",       # 18 chars
            "COGNITIVE": "Third definition",         # 16 chars
            "Reading": "Reading definition",
        }

        result = reader._deduplicate_concepts(concepts)

        # Should have only 2 unique concepts (case-insensitive)
        assert len(result) == 2
        assert "Reading" in result

        # Should keep the concept with longest definition for duplicates
        cognitive_kept = None
        for name, definition in result.items():
            if name.lower() == "cognitive":
                cognitive_kept = (name, definition)
                break

        assert cognitive_kept is not None
        # Should keep the longest definition ("Definition of cognitive" = 21 chars)
        assert "Definition of cognitive" in cognitive_kept[1]
        assert cognitive_kept[0] == "Cognitive"  # Should keep the original case

    def test_deduplicate_concepts_with_separators(self, reader: CognitiveReader) -> None:
        """Test deduplication with spaces, underscores, and hyphens."""
        concepts = {
            "cognitive reading": "Spaces version definition",          # 25 chars - longest
            "cognitive_reading": "Underscores version",                # 19 chars
            "cognitive-reading": "Hyphens version",                   # 15 chars
            "COGNITIVE_READING": "Uppercase underscores",             # 21 chars
            "document processing": "Different concept",               # 17 chars
            "document_processing": "Same concept with underscores",   # 31 chars - longest
        }

        result = reader._deduplicate_concepts(concepts)

        # Should have only 2 unique concepts after normalization
        assert len(result) == 2

        # Find the cognitive reading concept (should keep longest definition)
        cognitive_reading_kept = None
        document_processing_kept = None

        for name, definition in result.items():
            normalized = name.lower().replace('_', ' ').replace('-', ' ')
            normalized = ' '.join(normalized.split())

            if normalized == "cognitive reading":
                cognitive_reading_kept = (name, definition)
            elif normalized == "document processing":
                document_processing_kept = (name, definition)

        assert cognitive_reading_kept is not None
        assert document_processing_kept is not None

        # Should keep the longest definitions
        assert "Spaces version definition" in cognitive_reading_kept[1]
        assert "Same concept with underscores" in document_processing_kept[1]

    def test_normalize_concept_name(self, reader: CognitiveReader) -> None:
        """Test concept name normalization helper function."""
        assert reader._normalize_concept_name("Cognitive Reading") == "cognitive reading"
        assert reader._normalize_concept_name("cognitive_reading") == "cognitive reading"
        assert reader._normalize_concept_name("cognitive-reading") == "cognitive reading"
        assert reader._normalize_concept_name("COGNITIVE_READING") == "cognitive reading"
        assert reader._normalize_concept_name("  Document__Processing  ") == "document processing"
        assert reader._normalize_concept_name("technical-terms_preservation") == "technical terms preservation"

    def test_concept_to_sections_mapping_with_separators(
        self, reader: CognitiveReader
    ) -> None:
        """Test that section mapping handles separator normalization."""
        summaries = {
            "section_1": SectionSummary(
                section_id="section_1",
                title="Section 1",
                summary="Test summary",
                key_concepts=["cognitive reading", "document_processing"],
                parent_id=None,
                children_ids=[],
                level=0,
                order_index=0,
            ),
            "section_2": SectionSummary(
                section_id="section_2",
                title="Section 2",
                summary="Test summary 2",
                key_concepts=["cognitive_reading", "document-processing"],
                parent_id=None,
                children_ids=[],
                level=0,
                order_index=1,
            ),
        }

        result = reader._build_concept_to_sections_mapping(summaries)

        # Should normalize and group correctly
        assert "cognitive reading" in result
        assert "document processing" in result

        # Both sections should be mapped to normalized concepts
        assert len(result["cognitive reading"]) == 2
        assert len(result["document processing"]) == 2
        assert "section_1" in result["cognitive reading"]
        assert "section_2" in result["cognitive reading"]
        assert "section_1" in result["document processing"]
        assert "section_2" in result["document processing"]

    def test_concept_specific_context_with_separators(
        self, reader: CognitiveReader
    ) -> None:
        """Test that context building works with normalized concept names."""
        summaries = {
            "section_1": SectionSummary(
                section_id="section_1",
                title="Introduction",
                summary="About cognitive reading",
                key_concepts=["cognitive_reading"],
                parent_id=None,
                children_ids=[],
                level=0,
                order_index=0,
            ),
            "section_2": SectionSummary(
                section_id="section_2",
                title="Methods",
                summary="Processing methods",
                key_concepts=["document-processing"],
                parent_id=None,
                children_ids=[],
                level=0,
                order_index=1,
            ),
        }

        concept_to_sections = reader._build_concept_to_sections_mapping(summaries)

        # Test with different separator formats - should all work
        context1 = reader._build_concept_specific_context(
            "cognitive reading", summaries, concept_to_sections
        )
        context2 = reader._build_concept_specific_context(
            "cognitive_reading", summaries, concept_to_sections
        )

        # Both should find the same context
        assert "Introduction: About cognitive reading" in context1
        assert context1 == context2

    def test_deduplicate_concepts_empty(self, reader: CognitiveReader) -> None:
        """Test deduplication with empty input."""
        result = reader._deduplicate_concepts({})
        assert result == {}

    def test_deduplicate_concepts_no_duplicates(self, reader: CognitiveReader) -> None:
        """Test deduplication when no duplicates exist."""
        concepts = {
            "Concept1": "Definition 1",
            "Concept2": "Definition 2",
            "Concept3": "Definition 3",
        }

        result = reader._deduplicate_concepts(concepts)

        assert len(result) == 3
        assert result == concepts

    def test_build_concept_to_sections_mapping(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test concept to sections mapping creation."""
        result = reader._build_concept_to_sections_mapping(sample_summaries)

        # Check that concepts are mapped correctly (normalized to lowercase)
        assert "cognitive" in result
        assert "reading" in result
        assert "document processing" in result
        assert "methods" in result
        assert "processing" in result

        # Check section mapping
        assert "section_1" in result["cognitive"]
        assert "section_2" in result["cognitive"]
        assert "section_1" in result["reading"]
        assert "section_1" in result["document processing"]
        assert "section_2" in result["methods"]

    def test_build_concept_to_sections_mapping_empty(self, reader: CognitiveReader) -> None:
        """Test mapping with empty summaries."""
        result = reader._build_concept_to_sections_mapping({})
        assert result == {}

    def test_build_concept_specific_context(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test concept-specific context building."""
        concept_to_sections = reader._build_concept_to_sections_mapping(sample_summaries)

        # Test context for concept that appears in both sections
        context = reader._build_concept_specific_context(
            "cognitive", sample_summaries, concept_to_sections
        )

        assert "Introduction: Introduction to cognitive reading" in context
        assert "Methods: Methods for document processing" in context

    def test_build_concept_specific_context_single_section(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test context building for concept in single section."""
        concept_to_sections = reader._build_concept_to_sections_mapping(sample_summaries)

        context = reader._build_concept_specific_context(
            "reading", sample_summaries, concept_to_sections
        )

        # Should only include section where concept appears
        assert "Introduction: Introduction to cognitive reading" in context
        assert "Methods: Methods for document processing" not in context

    def test_build_concept_specific_context_unknown_concept(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test context building for unknown concept (fallback)."""
        concept_to_sections = reader._build_concept_to_sections_mapping(sample_summaries)

        context = reader._build_concept_specific_context(
            "unknown_concept", sample_summaries, concept_to_sections
        )

        # Should fallback to all summaries
        assert "Introduction: Introduction to cognitive reading" in context
        assert "Methods: Methods for document processing" in context

    def test_build_concept_specific_context_limits_sections(
        self, reader: CognitiveReader
    ) -> None:
        """Test that context building limits number of sections."""
        # Create many summaries
        many_summaries = {}
        concept_to_sections: dict[str, list[str]] = {"test_concept": []}

        for i in range(10):
            section_id = f"section_{i}"
            many_summaries[section_id] = SectionSummary(
                section_id=section_id,
                title=f"Title {i}",
                summary=f"Summary {i}",
                key_concepts=["test_concept"],
                parent_id=None,
                children_ids=[],
                level=0,
                order_index=i,
            )
            concept_to_sections["test_concept"].append(section_id)

        context = reader._build_concept_specific_context(
            "test_concept", many_summaries, concept_to_sections
        )

        # Should limit to 5 sections max
        context_lines = context.split("\n")
        assert len(context_lines) <= 5

    @pytest.mark.asyncio
    async def test_build_cognitive_knowledge_from_current_state(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test building CognitiveKnowledge from current state."""
        # Mock the current glossary
        reader.current_pass_glossary = {
            "Cognitive Reading": "Process of understanding documents",
            "Document Processing": "Technical handling of documents",
        }

        # Create sample sections
        sections = [
            DocumentSection(
                id="section_1",
                title="Introduction",
                content="Content 1",
                level=0,
                parent_id=None,
                children_ids=["section_2"],
                order_index=0,
            ),
            DocumentSection(
                id="section_2",
                title="Methods",
                content="Content 2",
                level=1,
                parent_id="section_1",
                children_ids=[],
                order_index=1,
            ),
        ]

        knowledge = reader._build_cognitive_knowledge_from_current_state(
            sections=sections,
            section_summaries=sample_summaries,
            document_title="**Test Document** with *markdown*",
            detected_language=LanguageCode.EN,
        )

        # Check basic structure
        assert knowledge.document_title == "Test Document with markdown"  # Cleaned
        assert knowledge.detected_language == LanguageCode.EN
        assert len(knowledge.hierarchical_summaries) == 2
        assert len(knowledge.concepts) == 2
        assert knowledge.total_sections == 2  # Should match processed sections (section_summaries)
        assert knowledge.total_concepts == 2

        # Check hierarchy index
        assert "0" in knowledge.hierarchy_index
        assert "1" in knowledge.hierarchy_index
        assert "section_1" in knowledge.hierarchy_index["0"]
        assert "section_2" in knowledge.hierarchy_index["1"]

        # Check parent-child mapping
        assert "section_1" in knowledge.parent_child_map
        assert "section_2" in knowledge.parent_child_map["section_1"]

        # Check concepts
        concept_names = [c.name for c in knowledge.concepts]
        assert "Cognitive Reading" in concept_names
        assert "Document Processing" in concept_names

    @pytest.mark.asyncio
    async def test_update_existing_concept_definitions(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test updating existing concept definitions."""
        # Set up initial glossary with duplicates
        reader.current_pass_glossary = {
            "Cognitive": "Initial definition",
            "cognitive": "Another definition",
            "COGNITIVE": "Third definition (longest)",
            "Reading": "Reading definition",
        }

        # Test the update method - this will create its own LLMClient internally in dry_run mode
        await reader._update_existing_concept_definitions(sample_summaries, LanguageCode.EN)

        # Should have deduplicated concepts
        assert len(reader.current_pass_glossary) == 2

        # Should keep concepts with case variations handled
        concept_names_lower = [name.lower() for name in reader.current_pass_glossary.keys()]
        assert "cognitive" in concept_names_lower
        assert "reading" in concept_names_lower

    @pytest.mark.asyncio
    async def test_update_existing_concept_definitions_no_glossary(
        self, reader: CognitiveReader, sample_summaries: dict[str, SectionSummary]
    ) -> None:
        """Test update when no existing glossary exists."""
        # Ensure no glossary exists
        if hasattr(reader, 'current_pass_glossary'):
            delattr(reader, 'current_pass_glossary')

        # Should not raise error and should exit gracefully
        await reader._update_existing_concept_definitions(sample_summaries, LanguageCode.EN)

        # Should still not have glossary
        assert not hasattr(reader, 'current_pass_glossary') or not reader.current_pass_glossary
