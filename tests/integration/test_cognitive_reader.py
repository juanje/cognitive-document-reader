"""Integration tests for the main CognitiveReader component."""

from __future__ import annotations

import pytest

from cognitive_reader import CognitiveReader
from cognitive_reader.models.knowledge import LanguageCode


@pytest.mark.asyncio
async def test_basic_reading(test_config, sample_markdown):
    """Test basic document reading with mock responses."""
    reader = CognitiveReader(test_config)

    # Test text reading
    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    assert knowledge.document_title == "Test Document"
    assert knowledge.detected_language in [LanguageCode.EN, LanguageCode.AUTO]
    assert len(knowledge.sections) > 0
    assert knowledge.document_summary is not None
    assert len(knowledge.document_summary) > 0

    # Should have processing metadata
    assert (
        "test_mode" in knowledge.processing_metadata
        or "dry_run" in knowledge.processing_metadata
    )


@pytest.mark.asyncio
async def test_spanish_document_reading(test_config, sample_spanish_markdown):
    """Test reading Spanish document with language detection."""
    # Override language to AUTO for detection testing
    spanish_config = test_config.model_copy(
        update={"document_language": LanguageCode.AUTO}
    )
    reader = CognitiveReader(spanish_config)

    knowledge = await reader.read_document_text(
        sample_spanish_markdown, "Documento de Prueba"
    )

    assert knowledge.document_title == "Documento de Prueba"
    assert knowledge.detected_language == LanguageCode.ES
    assert len(knowledge.sections) > 0
    assert knowledge.document_summary is not None


@pytest.mark.asyncio
async def test_complex_hierarchical_document(test_config, complex_markdown):
    """Test reading complex document with multiple hierarchy levels."""
    reader = CognitiveReader(test_config)

    knowledge = await reader.read_document_text(complex_markdown, "Complex Document")

    assert knowledge.document_title == "Complex Document"
    assert len(knowledge.sections) > 5  # Should have many sections

    # Check hierarchy
    sections_by_level = {}
    for section in knowledge.sections:
        level = section.level
        if level not in sections_by_level:
            sections_by_level[level] = []
        sections_by_level[level].append(section)

    # Should have multiple levels
    assert len(sections_by_level) >= 2
    assert 1 in sections_by_level  # Should have top-level sections

    # Check parent-child relationships
    for section in knowledge.sections:
        if section.parent_id:
            # Parent should exist
            parent = knowledge.get_section_by_id(section.parent_id)
            assert parent is not None
            assert section.id in parent.children_ids


@pytest.mark.asyncio
async def test_empty_document_handling(test_config, empty_markdown):
    """Test handling of minimal/empty documents."""
    reader = CognitiveReader(test_config)

    knowledge = await reader.read_document_text(empty_markdown, "Empty Document")

    assert knowledge.document_title == "Empty Document"
    # Should handle gracefully, even if no substantial content
    assert knowledge.document_summary is not None


@pytest.mark.asyncio
async def test_configuration_validation_mode(test_config):
    """Test validation-only mode."""
    # Enable validation-only mode
    validation_config = test_config.model_copy(update={"validate_config_only": True})
    reader = CognitiveReader(validation_config)

    # Should work without a document
    knowledge = await reader.read_document_text("# Test", "Test")

    assert knowledge.document_title == "Configuration Validation"
    assert "validation_only" in knowledge.processing_metadata
    assert knowledge.processing_metadata["validation_only"] is True


@pytest.mark.asyncio
async def test_configuration_validation():
    """Test configuration validation functionality."""
    from cognitive_reader.models import ReadingConfig

    # Valid configuration
    config = ReadingConfig(dry_run=True, mock_responses=True)
    reader = CognitiveReader(config)

    is_valid = await reader.validate_configuration()
    assert is_valid is True


@pytest.mark.asyncio
async def test_dependency_checking():
    """Test dependency checking functionality."""
    from cognitive_reader.models import ReadingConfig

    config = ReadingConfig(dry_run=True)
    reader = CognitiveReader(config)

    # Should pass since we have all required dependencies in test environment
    dependencies_ok = reader.check_dependencies()
    assert dependencies_ok is True


@pytest.mark.asyncio
async def test_progressive_context_accumulation(test_config, sample_markdown):
    """Test that context accumulates progressively between sections."""
    reader = CognitiveReader(test_config)

    knowledge = await reader.read_document_text(sample_markdown, "Test Document")

    # Should have multiple sections with summaries
    assert len(knowledge.section_summaries) > 1

    # All sections should have summaries in development mode
    content_sections = [s for s in knowledge.sections if not s.children_ids]
    for section in content_sections:
        if section.id in knowledge.section_summaries:
            summary = knowledge.section_summaries[section.id]
            assert summary.summary is not None
            assert len(summary.summary) > 0
            assert isinstance(summary.key_concepts, list)


@pytest.mark.asyncio
async def test_section_hierarchy_methods(test_config, complex_markdown):
    """Test DocumentKnowledge helper methods for hierarchy navigation."""
    reader = CognitiveReader(test_config)

    knowledge = await reader.read_document_text(complex_markdown, "Complex Document")

    # Test get_top_level_sections
    top_sections = knowledge.get_top_level_sections()
    assert len(top_sections) > 0
    for section in top_sections:
        assert section.level == 1

    # Test get_section_by_id
    if knowledge.sections:
        first_section = knowledge.sections[0]
        found_section = knowledge.get_section_by_id(first_section.id)
        assert found_section is not None
        assert found_section.id == first_section.id

    # Test get_children_of_section
    for section in knowledge.sections:
        if section.children_ids:
            children = knowledge.get_children_of_section(section.id)
            assert len(children) == len(section.children_ids)
            for child in children:
                assert child.parent_id == section.id


@pytest.mark.asyncio
async def test_development_mode_features(test_config):
    """Test that development mode features work correctly."""
    assert test_config.is_development_mode() is True
    assert test_config.dry_run is True
    assert test_config.mock_responses is True

    reader = CognitiveReader(test_config)

    # Should work in development mode
    knowledge = await reader.read_document_text("# Test\n\nSome content.", "Test")

    assert knowledge is not None
    assert knowledge.document_title == "Test"

    # Should indicate development mode in metadata
    metadata = knowledge.processing_metadata
    assert metadata.get("dry_run") is True or metadata.get("test_mode") is True
