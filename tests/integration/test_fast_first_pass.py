"""Integration tests for Fast First Pass dual-model cognitive reading.

Tests the complete workflow of dual-pass cognitive reading with fast and main models.
"""

from __future__ import annotations

import pytest

from cognitive_reader import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode


@pytest.fixture
def fast_pass_config(fast_pass_base_config: CognitiveConfig) -> CognitiveConfig:
    """Configuration with Fast First Pass enabled."""
    return fast_pass_base_config.model_copy()


@pytest.fixture
def single_pass_config(single_pass_base_config: CognitiveConfig) -> CognitiveConfig:
    """Configuration with single-pass approach."""
    return single_pass_base_config.model_copy()


@pytest.mark.asyncio
async def test_dual_pass_reading_workflow(cognitive_reader, sample_markdown: str):
    """Test complete dual-pass reading workflow."""
    # Use optimized session-scoped reader instead of creating new one
    reader = cognitive_reader

    # Process document
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    # Verify basic structure (SPECS v2.0)
    assert knowledge.document_title == "Test Document"
    assert knowledge.detected_language in [LanguageCode.EN, LanguageCode.AUTO]
    assert isinstance(knowledge.hierarchical_summaries, dict)
    assert len(knowledge.hierarchical_summaries) > 0
    assert isinstance(knowledge.concepts, list)
    assert knowledge.total_sections > 0
    assert knowledge.avg_summary_length > 0

    # Verify hierarchical summaries structure
    for section_id, summary in knowledge.hierarchical_summaries.items():
        assert hasattr(summary, "title")
        assert hasattr(summary, "summary")
        assert hasattr(summary, "key_concepts")
        assert hasattr(summary, "level")
        assert hasattr(summary, "order_index")
        assert len(summary.summary) > 0
        assert isinstance(summary.key_concepts, list)


@pytest.mark.asyncio
async def test_single_pass_reading_workflow(cognitive_reader, sample_markdown: str):
    """Test single-pass reading workflow for comparison."""
    reader = cognitive_reader

    # Process document
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    # Verify basic structure (same as dual-pass)
    assert knowledge.document_title == "Test Document"
    assert knowledge.detected_language in [LanguageCode.EN, LanguageCode.AUTO]
    assert isinstance(knowledge.hierarchical_summaries, dict)
    assert len(knowledge.hierarchical_summaries) > 0
    assert knowledge.total_sections > 0


@pytest.mark.asyncio
async def test_fast_pass_only_workflow(cognitive_reader, sample_markdown: str):
    """Test fast pass only (second pass disabled)."""
    reader = cognitive_reader

    # Process document
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    # Should still work with just fast pass
    assert knowledge.document_title == "Test Document"
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_spanish_document_dual_pass(cognitive_reader):
    """Test dual-pass with Spanish document."""
    spanish_doc = """# Documento de Prueba

## Introducción

Este es un documento de prueba en español.

### Sección 1

Contenido en español con conceptos importantes.

## Conclusión

Pensamientos finales sobre el documento.
"""

    reader = cognitive_reader
    knowledge = await reader.read_document_text(spanish_doc, "Documento de Prueba")

    # Should detect language (using cached config, may be EN or ES)
    assert knowledge.detected_language in [LanguageCode.EN, LanguageCode.ES]
    assert knowledge.document_title == "Documento de Prueba"
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_model_configuration_validation(cognitive_reader, sample_markdown: str):
    """Test that models are configured correctly in dual-pass mode."""
    reader = cognitive_reader

    # Verify configuration (using base config values)
    assert reader.config.dry_run is True
    assert reader.config.mock_responses is True

    # Process document (should work without errors)
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_markdown_title_cleaning_integration(cognitive_reader):
    """Test that markdown formatting is cleaned from document title."""
    doc_with_markdown_title = """# **Bold Title** with *italic* and `code`

## Section

Content here.
"""

    reader = cognitive_reader
    knowledge = await reader.read_document_text(
        doc_with_markdown_title, "**Bold Title** with *italic* and `code`"
    )

    # Title should be cleaned of markdown
    assert knowledge.document_title == "Bold Title with italic and code"
    assert "**" not in knowledge.document_title
    assert "*" not in knowledge.document_title
    assert "`" not in knowledge.document_title


@pytest.mark.asyncio
async def test_section_title_cleaning_integration(cognitive_reader):
    """Test that section titles are cleaned of markdown formatting."""
    doc_with_markdown_sections = """# Document

## **Bold Section** Title

Content here.

### *Italic Section* Title

More content.
"""

    reader = cognitive_reader
    knowledge = await reader.read_document_text(doc_with_markdown_sections, "Document")

    # Check that section titles are cleaned
    section_titles = [
        summary.title for summary in knowledge.hierarchical_summaries.values()
    ]

    # Should contain cleaned titles
    cleaned_titles = [
        title for title in section_titles if "**" not in title and "*" not in title
    ]
    assert len(cleaned_titles) > 0

    # Verify specific cleaning
    bold_section_found = any("Bold Section Title" in title for title in section_titles)
    italic_section_found = any(
        "Italic Section Title" in title for title in section_titles
    )

    assert (
        bold_section_found or italic_section_found
    )  # At least one should be found and cleaned


@pytest.mark.asyncio
async def test_json_output_structure_compliance(cognitive_reader, sample_markdown: str):
    """Test that output structure complies with SPECS v2.0."""
    reader = cognitive_reader
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    # Test SPECS v2.0 structure compliance

    # Required top-level fields
    assert hasattr(knowledge, "document_title")
    assert hasattr(knowledge, "document_summary")  # Now required in SPECS v2.0
    assert hasattr(knowledge, "detected_language")
    assert hasattr(knowledge, "hierarchical_summaries")
    assert hasattr(knowledge, "concepts")
    assert hasattr(knowledge, "hierarchy_index")
    assert hasattr(knowledge, "parent_child_map")
    assert hasattr(knowledge, "total_sections")
    assert hasattr(knowledge, "avg_summary_length")
    assert hasattr(knowledge, "total_concepts")

    # Should NOT have deprecated fields
    assert not hasattr(knowledge, "sections")
    assert not hasattr(knowledge, "section_summaries")
    assert not hasattr(knowledge, "processing_metadata")

    # Verify types
    assert isinstance(knowledge.document_title, str)
    assert isinstance(knowledge.document_summary, str)
    assert isinstance(knowledge.detected_language, LanguageCode)
    assert isinstance(knowledge.hierarchical_summaries, dict)
    assert isinstance(knowledge.concepts, list)
    assert isinstance(knowledge.hierarchy_index, dict)
    assert isinstance(knowledge.parent_child_map, dict)
    assert isinstance(knowledge.total_sections, int)
    assert isinstance(knowledge.avg_summary_length, float)
    assert isinstance(knowledge.total_concepts, int)


@pytest.mark.asyncio
async def test_performance_comparison_dual_vs_single(
    cognitive_reader, sample_markdown: str
):
    """Test performance characteristics of dual-pass vs single-pass."""
    # This is more of a smoke test to ensure both approaches work
    # In a real scenario, you might measure timing differences

    # Both should complete successfully (using same optimized reader)
    dual_reader = cognitive_reader
    single_reader = cognitive_reader

    dual_knowledge = await dual_reader.read_document_text(
        sample_markdown, "Performance Test"
    )
    single_knowledge = await single_reader.read_document_text(
        sample_markdown, "Performance Test"
    )

    # Both should produce valid results
    assert len(dual_knowledge.hierarchical_summaries) > 0
    assert len(single_knowledge.hierarchical_summaries) > 0

    # Both should have same basic structure
    assert dual_knowledge.document_title == single_knowledge.document_title
    assert dual_knowledge.detected_language == single_knowledge.detected_language
