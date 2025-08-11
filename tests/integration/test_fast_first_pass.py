"""Integration tests for Fast First Pass dual-model cognitive reading.

Tests the complete workflow of dual-pass cognitive reading with fast and main models.
"""

from __future__ import annotations

import pytest

from cognitive_reader import CognitiveConfig, CognitiveReader
from cognitive_reader.models.knowledge import LanguageCode


@pytest.fixture
def fast_pass_config() -> CognitiveConfig:
    """Configuration with Fast First Pass enabled."""
    return CognitiveConfig(
        # Enable dual-pass approach
        enable_fast_first_pass=True,
        enable_second_pass=True,

        # Model configuration
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b",
        fast_pass_temperature=0.1,
        main_pass_temperature=0.3,

        # Development modes
        dry_run=True,
        mock_responses=True,

        # Basic settings
        model_name="qwen3:8b",  # Fallback
        temperature=0.3,
        max_retries=2,
        timeout_seconds=30,
    )


@pytest.fixture
def single_pass_config() -> CognitiveConfig:
    """Configuration with single-pass approach."""
    return CognitiveConfig(
        # Disable dual-pass approach
        enable_fast_first_pass=False,
        enable_second_pass=False,

        # Model configuration
        main_model="qwen3:8b",
        main_pass_temperature=0.3,

        # Development modes
        dry_run=True,
        mock_responses=True,

        # Basic settings
        model_name="qwen3:8b",
        temperature=0.3,
        max_retries=2,
        timeout_seconds=30,
    )


@pytest.fixture
def sample_document() -> str:
    """Sample document for testing."""
    return """# Test Document

## Introduction

This is a test document with multiple sections.

### Subsection 1

Content for subsection 1 with some important concepts.

### Subsection 2

Content for subsection 2 with more concepts and ideas.

## Conclusion

Final thoughts and summary of the document.
"""


@pytest.mark.asyncio
async def test_dual_pass_reading_workflow(fast_pass_config: CognitiveConfig, sample_document: str):
    """Test complete dual-pass reading workflow."""
    reader = CognitiveReader(fast_pass_config)

    # Process document
    knowledge = await reader.read_document_text(sample_document, "Test Document")

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
        assert hasattr(summary, 'title')
        assert hasattr(summary, 'summary')
        assert hasattr(summary, 'key_concepts')
        assert hasattr(summary, 'level')
        assert hasattr(summary, 'order_index')
        assert len(summary.summary) > 0
        assert isinstance(summary.key_concepts, list)


@pytest.mark.asyncio
async def test_single_pass_reading_workflow(single_pass_config: CognitiveConfig, sample_document: str):
    """Test single-pass reading workflow for comparison."""
    reader = CognitiveReader(single_pass_config)

    # Process document
    knowledge = await reader.read_document_text(sample_document, "Test Document")

    # Verify basic structure (same as dual-pass)
    assert knowledge.document_title == "Test Document"
    assert knowledge.detected_language in [LanguageCode.EN, LanguageCode.AUTO]
    assert isinstance(knowledge.hierarchical_summaries, dict)
    assert len(knowledge.hierarchical_summaries) > 0
    assert knowledge.total_sections > 0


@pytest.mark.asyncio
async def test_fast_pass_only_workflow(fast_pass_config: CognitiveConfig, sample_document: str):
    """Test fast pass only (second pass disabled)."""
    # Disable second pass
    config = fast_pass_config.model_copy(update={"enable_second_pass": False})
    reader = CognitiveReader(config)

    # Process document
    knowledge = await reader.read_document_text(sample_document, "Test Document")

    # Should still work with just fast pass
    assert knowledge.document_title == "Test Document"
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_spanish_document_dual_pass(fast_pass_config: CognitiveConfig):
    """Test dual-pass with Spanish document."""
    spanish_doc = """# Documento de Prueba

## Introducción

Este es un documento de prueba en español.

### Sección 1

Contenido en español con conceptos importantes.

## Conclusión

Pensamientos finales sobre el documento.
"""

    reader = CognitiveReader(fast_pass_config)
    knowledge = await reader.read_document_text(spanish_doc, "Documento de Prueba")

    # Should detect Spanish
    assert knowledge.detected_language == LanguageCode.ES
    assert knowledge.document_title == "Documento de Prueba"
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_model_configuration_validation(fast_pass_config: CognitiveConfig, sample_document: str):
    """Test that models are configured correctly in dual-pass mode."""
    reader = CognitiveReader(fast_pass_config)

    # Verify configuration
    assert reader.config.enable_fast_first_pass is True
    assert reader.config.enable_second_pass is True
    assert reader.config.fast_pass_model == "llama3.1:8b"
    assert reader.config.main_model == "qwen3:8b"
    assert reader.config.fast_pass_temperature == 0.1
    assert reader.config.main_pass_temperature == 0.3

    # Process document (should work without errors)
    knowledge = await reader.read_document_text(sample_document, "Test Document")
    assert len(knowledge.hierarchical_summaries) > 0


@pytest.mark.asyncio
async def test_markdown_title_cleaning_integration(fast_pass_config: CognitiveConfig):
    """Test that markdown formatting is cleaned from document title."""
    doc_with_markdown_title = """# **Bold Title** with *italic* and `code`

## Section

Content here.
"""

    reader = CognitiveReader(fast_pass_config)
    knowledge = await reader.read_document_text(doc_with_markdown_title, "**Bold Title** with *italic* and `code`")

    # Title should be cleaned of markdown
    assert knowledge.document_title == "Bold Title with italic and code"
    assert "**" not in knowledge.document_title
    assert "*" not in knowledge.document_title
    assert "`" not in knowledge.document_title


@pytest.mark.asyncio
async def test_section_title_cleaning_integration(fast_pass_config: CognitiveConfig):
    """Test that section titles are cleaned of markdown formatting."""
    doc_with_markdown_sections = """# Document

## **Bold Section** Title

Content here.

### *Italic Section* Title

More content.
"""

    reader = CognitiveReader(fast_pass_config)
    knowledge = await reader.read_document_text(doc_with_markdown_sections, "Document")

    # Check that section titles are cleaned
    section_titles = [summary.title for summary in knowledge.hierarchical_summaries.values()]

    # Should contain cleaned titles
    cleaned_titles = [title for title in section_titles if "**" not in title and "*" not in title]
    assert len(cleaned_titles) > 0

    # Verify specific cleaning
    bold_section_found = any("Bold Section Title" in title for title in section_titles)
    italic_section_found = any("Italic Section Title" in title for title in section_titles)

    assert bold_section_found or italic_section_found  # At least one should be found and cleaned


@pytest.mark.asyncio
async def test_json_output_structure_compliance(fast_pass_config: CognitiveConfig, sample_document: str):
    """Test that output structure complies with SPECS v2.0."""
    reader = CognitiveReader(fast_pass_config)
    knowledge = await reader.read_document_text(sample_document, "Test Document")

    # Test SPECS v2.0 structure compliance

    # Required top-level fields
    assert hasattr(knowledge, 'document_title')
    assert hasattr(knowledge, 'detected_language')
    assert hasattr(knowledge, 'hierarchical_summaries')
    assert hasattr(knowledge, 'concepts')
    assert hasattr(knowledge, 'hierarchy_index')
    assert hasattr(knowledge, 'parent_child_map')
    assert hasattr(knowledge, 'total_sections')
    assert hasattr(knowledge, 'avg_summary_length')
    assert hasattr(knowledge, 'total_concepts')

    # Should NOT have deprecated fields
    assert not hasattr(knowledge, 'document_summary')
    assert not hasattr(knowledge, 'sections')
    assert not hasattr(knowledge, 'section_summaries')
    assert not hasattr(knowledge, 'processing_metadata')

    # Verify types
    assert isinstance(knowledge.document_title, str)
    assert isinstance(knowledge.detected_language, LanguageCode)
    assert isinstance(knowledge.hierarchical_summaries, dict)
    assert isinstance(knowledge.concepts, list)
    assert isinstance(knowledge.hierarchy_index, dict)
    assert isinstance(knowledge.parent_child_map, dict)
    assert isinstance(knowledge.total_sections, int)
    assert isinstance(knowledge.avg_summary_length, float)
    assert isinstance(knowledge.total_concepts, int)


@pytest.mark.asyncio
async def test_performance_comparison_dual_vs_single():
    """Test performance characteristics of dual-pass vs single-pass."""
    # This is more of a smoke test to ensure both approaches work
    # In a real scenario, you might measure timing differences

    sample_doc = """# Performance Test

## Section 1
Content for performance testing.

## Section 2
More content for testing.
"""

    # Test dual-pass
    dual_config = CognitiveConfig(
        enable_fast_first_pass=True,
        enable_second_pass=True,
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b",
        dry_run=True,
        mock_responses=True,
    )

    # Test single-pass
    single_config = CognitiveConfig(
        enable_fast_first_pass=False,
        main_model="qwen3:8b",
        dry_run=True,
        mock_responses=True,
    )

    # Both should complete successfully
    dual_reader = CognitiveReader(dual_config)
    single_reader = CognitiveReader(single_config)

    dual_knowledge = await dual_reader.read_document_text(sample_doc, "Performance Test")
    single_knowledge = await single_reader.read_document_text(sample_doc, "Performance Test")

    # Both should produce valid results
    assert len(dual_knowledge.hierarchical_summaries) > 0
    assert len(single_knowledge.hierarchical_summaries) > 0

    # Both should have same basic structure
    assert dual_knowledge.document_title == single_knowledge.document_title
    assert dual_knowledge.detected_language == single_knowledge.detected_language
