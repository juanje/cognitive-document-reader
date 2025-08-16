"""Pytest configuration and fixtures for cognitive reader tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from cognitive_reader.models import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode


@pytest.fixture(scope="session")
def base_test_config() -> CognitiveConfig:
    """Base test configuration for session-wide reuse.

    Cached at session level for optimal performance.

    Returns:
        CognitiveConfig with optimized test settings.
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
def test_config(base_test_config: CognitiveConfig) -> CognitiveConfig:
    """Test configuration that can be modified per test.

    Returns:
        Fresh copy of base config for test isolation.
    """
    return base_test_config.model_copy()


@pytest.fixture(scope="session")
def fast_pass_base_config() -> CognitiveConfig:
    """Base fast pass configuration for session-wide reuse.

    Returns:
        CognitiveConfig with fast pass settings enabled.
    """
    return CognitiveConfig(
        # Enable dual-pass approach
        enable_fast_first_pass=True,
        num_passes=2,
        # Model configuration
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b",
        fast_pass_temperature=0.1,
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


@pytest.fixture(scope="session")
def single_pass_base_config() -> CognitiveConfig:
    """Base single pass configuration for session-wide reuse.

    Returns:
        CognitiveConfig with single-pass approach.
    """
    return CognitiveConfig(
        # Disable dual-pass approach
        enable_fast_first_pass=False,
        num_passes=1,
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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def empty_markdown() -> str:
    """Empty markdown document for edge case testing.

    Returns:
        Minimal markdown content.
    """
    return "# Empty Document\n\nThis document has minimal content."


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session", autouse=True)
def mock_dotenv_loading():
    """Mock expensive dotenv loading operations for all tests.

    This prevents the slow filesystem operations in _load_dotenv() while
    still allowing environment variable testing through mocked values.
    """
    with patch("cognitive_reader.models.config.CognitiveConfig._load_dotenv"):
        yield


@pytest.fixture(scope="session")
def mock_env_vars():
    """Mock environment variables for testing configuration loading."""
    return {
        "COGNITIVE_READER_MODEL": "test-model",
        "COGNITIVE_READER_TEMPERATURE": "0.1",
        "COGNITIVE_READER_MAX_PASSES": "2",
        "COGNITIVE_READER_FAST_PASS_MODEL": "llama3.1:8b",
        "COGNITIVE_READER_MAIN_MODEL": "qwen3:8b",
        "COGNITIVE_READER_DRY_RUN": "true",
        "COGNITIVE_READER_MOCK_RESPONSES": "true",
    }


@pytest.fixture
def mocked_from_env(mock_env_vars):
    """Fixture that provides a fast mocked version of from_env()."""

    def _mock_from_env():
        return CognitiveConfig(
            model_name=mock_env_vars.get("COGNITIVE_READER_MODEL", "test-model"),
            temperature=float(mock_env_vars.get("COGNITIVE_READER_TEMPERATURE", "0.1")),
            max_passes=int(mock_env_vars.get("COGNITIVE_READER_MAX_PASSES", "2")),
            fast_pass_model=mock_env_vars.get(
                "COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"
            ),
            main_model=mock_env_vars.get("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            dry_run=mock_env_vars.get("COGNITIVE_READER_DRY_RUN", "true").lower()
            == "true",
            mock_responses=mock_env_vars.get(
                "COGNITIVE_READER_MOCK_RESPONSES", "true"
            ).lower()
            == "true",
        )

    return _mock_from_env


@pytest.fixture(scope="session", autouse=True)
def mock_llm_initialization():
    """Mock expensive LLM initialization for all tests.

    Prevents ChatOllama creation and network connections.
    """
    from unittest.mock import MagicMock

    # Mock the entire ChatOllama class to prevent network connections
    with patch("cognitive_reader.llm.client.ChatOllama") as mock_chat_ollama:
        # Configure mock to return a simple mock instance
        mock_instance = MagicMock()
        mock_instance.model_name = "mocked-model"
        mock_instance.reasoning = None  # Default reasoning value
        mock_chat_ollama.return_value = mock_instance

        # Mock aiohttp.ClientSession to prevent HTTP initialization
        mock_session = MagicMock()

        async def mock_close():
            return None

        mock_session.close = mock_close

        with patch(
            "cognitive_reader.llm.client.aiohttp.ClientSession",
            return_value=mock_session,
        ):
            yield


@pytest.fixture(scope="session", autouse=True)
def mock_docling_imports():
    """Mock heavy docling imports for faster test startup.

    Prevents loading of heavy ML/document processing libraries.
    """
    import sys
    from unittest.mock import MagicMock

    # Mock docling modules if they're not already imported
    mock_modules = [
        "docling",
        "docling.datamodel.base_models",
        "docling.document_converter",
        "docling.pipeline.simple_pipeline",
    ]

    original_modules = {}
    for module in mock_modules:
        if module not in sys.modules:
            original_modules[module] = sys.modules.get(module)
            sys.modules[module] = MagicMock()

    yield

    # Cleanup (restore original modules if needed)
    for module, original in original_modules.items():
        if original is None and module in sys.modules:
            del sys.modules[module]


@pytest.fixture(scope="session")
def fast_cognitive_reader(base_test_config: CognitiveConfig):
    """Session-scoped CognitiveReader with all expensive ops mocked.

    Returns a fully functional reader for tests without network/file I/O costs.
    """
    from cognitive_reader.core.progressive_reader import CognitiveReader

    # Create one instance per session and reuse it
    reader = CognitiveReader(base_test_config)
    return reader


@pytest.fixture
def cognitive_reader(fast_cognitive_reader):
    """Per-test cognitive reader fixture.

    Returns a fresh copy of the session-scoped reader for test isolation.
    """
    # For immutable operations, we can reuse the same instance
    # For mutable operations, tests should use model_copy() on configs
    return fast_cognitive_reader
