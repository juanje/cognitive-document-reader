"""Pytest configuration and fixtures for cognitive reader tests."""

from __future__ import annotations

import pytest

from cognitive_reader.models import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode


@pytest.fixture
def test_config() -> CognitiveConfig:
    """Simple test configuration with mocks enabled.

    Returns:
        CognitiveConfig with development modes enabled for testing.
    """
    return CognitiveConfig(
        model_name="test-model",
        temperature=0.1,
        chunk_size=500,  # Smaller for faster tests
        chunk_overlap=100,
        context_window=2048,
        timeout_seconds=30,  # Faster timeout for tests
        max_retries=1,  # Fewer retries for tests
        document_language=LanguageCode.EN,
        dry_run=True,  # No real LLM calls
        mock_responses=True,  # Use mock responses
        validate_config_only=False,
    )


@pytest.fixture
def sample_markdown() -> str:
    """Simple markdown document for testing.

    Returns:
        Sample markdown content with multiple sections.
    """
    return """# Test Document

This is a test document for the cognitive reader.

## Introduction

This section introduces the main concepts that will be discussed.
It provides background information and sets the context for the reader.

## Main Content

### Subsection 1

This is the first subsection with detailed information.
It contains several important points that need to be understood.

### Subsection 2

This is the second subsection with additional details.
It builds upon the previous subsection and adds new concepts.

## Conclusion

This final section summarizes the key points discussed.
It provides closure and reinforces the main ideas."""


@pytest.fixture
def sample_spanish_markdown() -> str:
    """Spanish markdown document for testing language detection.

    Returns:
        Sample Spanish markdown content.
    """
    return """# Documento de Prueba

Este es un documento de prueba para el lector cognitivo.

## Introducción

Esta sección introduce los conceptos principales que se discutirán.
Proporciona información de contexto para el lector.

## Contenido Principal

### Subsección 1

Esta es la primera subsección con información detallada.
Contiene varios puntos importantes que necesitan ser comprendidos.

## Conclusión

Esta sección final resume los puntos clave discutidos.
Proporciona cierre y refuerza las ideas principales."""


@pytest.fixture
def complex_markdown() -> str:
    """More complex markdown document for testing hierarchical structure.

    Returns:
        Complex markdown with multiple levels and various content types.
    """
    return """# Complex Document

A comprehensive test document with multiple hierarchical levels.

## Chapter 1: Introduction

This chapter provides an overview of the topics covered.

### Section 1.1: Background

Background information is essential for understanding.

#### Subsection 1.1.1: Historical Context

The historical context provides important perspective.

#### Subsection 1.1.2: Current State

The current state shows how things have evolved.

### Section 1.2: Objectives

The main objectives of this document are:

- Demonstrate hierarchical structure
- Test complex parsing
- Validate cognitive reading

## Chapter 2: Methodology

This chapter describes the methods used.

### Section 2.1: Data Collection

Data collection follows established protocols.

### Section 2.2: Analysis Techniques

Various analysis techniques are employed for comprehensive understanding.

## Chapter 3: Results

The results section presents findings.

## Chapter 4: Discussion

Discussion of the implications and significance.

### Section 4.1: Limitations

Acknowledging limitations is important for scientific integrity.

## Conclusion

Final thoughts and future directions."""


@pytest.fixture
def empty_markdown() -> str:
    """Empty markdown document for edge case testing.

    Returns:
        Minimal markdown content.
    """
    return "# Empty Document\n\nThis document has minimal content."


@pytest.fixture
def mock_cognitive_knowledge():
    """Mock CognitiveKnowledge for testing outputs.

    Returns:
        Mock CognitiveKnowledge object with sample data.
    """
    from cognitive_reader.models import (
        CognitiveKnowledge,
        SectionSummary,
    )

    # Example sections for reference (not used in this fixture)
    # sections = [
    #     DocumentSection(
    #         id="section_1",
    #         title="Introduction",
    #         content="This is the introduction section.",
    #         level=1,
    #         order_index=1,
    #     ),
    #     DocumentSection(
    #         id="section_2",
    #         title="Main Content",
    #         content="This is the main content section.",
    #         level=1,
    #         order_index=2,
    #     ),
    # ]

    summaries = {
        "section_1": SectionSummary(
            section_id="section_1",
            title="Introduction",
            summary="This section provides an introduction to the topic.",
            key_concepts=["introduction", "overview", "context"],
            level=1,
            order_index=1,
        ),
        "section_2": SectionSummary(
            section_id="section_2",
            title="Main Content",
            summary="This section contains the main discussion.",
            key_concepts=["main topic", "discussion", "analysis"],
            level=1,
            order_index=2,
        ),
    }

    return CognitiveKnowledge(
        document_title="Test Document",
        document_summary="This is a comprehensive test document with multiple sections for validation purposes.",
        detected_language=LanguageCode.EN,
        hierarchical_summaries=summaries,
        concepts=[],  # Empty for basic test
        hierarchy_index={"1": ["section_1", "section_2"]},
        parent_child_map={},
        total_sections=2,
        avg_summary_length=50,
        total_concepts=0,
    )
