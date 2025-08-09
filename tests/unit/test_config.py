"""Tests for configuration models and environment loading."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from cognitive_reader.models import ReadingConfig
from cognitive_reader.models.knowledge import LanguageCode


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    config = ReadingConfig()

    assert config.fast_model == "llama3.1:8b"
    assert config.quality_model == "qwen3:8b"
    assert config.fast_mode is False
    assert config.active_model == "qwen3:8b"  # Should use quality_model when fast_mode=False
    assert config.temperature == 0.1
    assert config.chunk_size == 1000
    assert config.chunk_overlap == 200
    assert config.context_window == 4096
    assert config.timeout_seconds == 120
    assert config.max_retries == 3
    assert config.document_language == LanguageCode.AUTO
    assert config.dry_run is False
    assert config.mock_responses is False
    assert config.validate_config_only is False


def test_config_validation():
    """Test configuration validation."""
    # Valid configuration
    config = ReadingConfig(
        temperature=0.5,
        chunk_size=500,
        chunk_overlap=100,
        context_window=2048,
        timeout_seconds=60,
        max_retries=2,
    )
    assert config.temperature == 0.5
    assert config.chunk_size == 500

    # Invalid temperature
    with pytest.raises(ValueError):
        ReadingConfig(temperature=-0.1)

    with pytest.raises(ValueError):
        ReadingConfig(temperature=2.1)

    # Invalid chunk size
    with pytest.raises(ValueError):
        ReadingConfig(chunk_size=50)

    # Invalid negative values
    with pytest.raises(ValueError):
        ReadingConfig(chunk_overlap=-1)

    with pytest.raises(ValueError):
        ReadingConfig(timeout_seconds=0)

    with pytest.raises(ValueError):
        ReadingConfig(max_retries=-1)


def test_config_from_env_empty():
    """Test config creation from empty environment."""
    # Clear any existing environment variables

    with mock.patch.dict(os.environ, {}, clear=True):
        config = ReadingConfig.from_env()

        # Should have defaults
        assert config.fast_model == "llama3.1:8b"
        assert config.quality_model == "qwen3:8b"
        assert config.fast_mode is False
        assert config.active_model == "qwen3:8b"
        assert config.temperature == 0.1
        assert config.document_language == LanguageCode.AUTO
        assert config.dry_run is False


def test_config_from_env_with_values():
    """Test config creation with environment variables."""
    env_vars = {
        "COGNITIVE_READER_MODEL": "custom-model",  # Legacy support
        "COGNITIVE_READER_TEMPERATURE": "0.5",
        "COGNITIVE_READER_CHUNK_SIZE": "750",
        "COGNITIVE_READER_CHUNK_OVERLAP": "150",
        "COGNITIVE_READER_TIMEOUT_SECONDS": "90",
        "COGNITIVE_READER_MAX_RETRIES": "2",
        "COGNITIVE_READER_LANGUAGE": "es",
        "COGNITIVE_READER_DRY_RUN": "true",
        "COGNITIVE_READER_MOCK_RESPONSES": "false",
    }

    with mock.patch.dict(os.environ, env_vars):
        config = ReadingConfig.from_env()

        # Legacy COGNITIVE_READER_MODEL should set both models
        assert config.fast_model == "custom-model"
        assert config.quality_model == "custom-model"
        assert config.active_model == "custom-model"
        assert config.temperature == 0.5
        assert config.chunk_size == 750
        assert config.chunk_overlap == 150
        assert config.timeout_seconds == 90
        assert config.max_retries == 2
        assert config.document_language == LanguageCode.ES
        assert config.dry_run is True
        assert config.mock_responses is False


def test_config_development_mode():
    """Test development mode detection."""
    # Normal mode
    config = ReadingConfig()
    assert config.is_development_mode() is False

    # Dry run mode
    config = ReadingConfig(dry_run=True)
    assert config.is_development_mode() is True

    # Mock responses mode
    config = ReadingConfig(mock_responses=True)
    assert config.is_development_mode() is True

    # Validate only mode
    config = ReadingConfig(validate_config_only=True)
    assert config.is_development_mode() is True

    # Multiple modes
    config = ReadingConfig(dry_run=True, mock_responses=True)
    assert config.is_development_mode() is True


def test_config_boolean_env_parsing():
    """Test boolean environment variable parsing."""
    # Test various boolean representations
    true_values = ["true", "True", "TRUE", "1", "yes", "Yes"]
    false_values = ["false", "False", "FALSE", "0", "no", "No", ""]

    for true_val in true_values:
        with mock.patch.dict(os.environ, {"COGNITIVE_READER_DRY_RUN": true_val}):
            config = ReadingConfig.from_env()
            assert config.dry_run is True, f"Failed for value: {true_val}"

    for false_val in false_values:
        with mock.patch.dict(os.environ, {"COGNITIVE_READER_DRY_RUN": false_val}):
            config = ReadingConfig.from_env()
            # Note: only "true" (lowercase) is considered True in our implementation
            expected = false_val.lower() == "true"
            assert config.dry_run is expected, f"Failed for value: {false_val}"


def test_config_language_enum():
    """Test language enum handling."""
    # Valid language codes
    config = ReadingConfig(document_language=LanguageCode.EN)
    assert config.document_language == LanguageCode.EN

    config = ReadingConfig(document_language=LanguageCode.ES)
    assert config.document_language == LanguageCode.ES

    config = ReadingConfig(document_language=LanguageCode.AUTO)
    assert config.document_language == LanguageCode.AUTO

    # Test from environment
    with mock.patch.dict(os.environ, {"COGNITIVE_READER_LANGUAGE": "en"}):
        config = ReadingConfig.from_env()
        assert config.document_language == LanguageCode.EN


def test_config_fast_mode():
    """Test fast mode functionality."""
    # Default: quality mode
    config = ReadingConfig()
    assert config.fast_mode is False
    assert config.active_model == "qwen3:8b"

    # Enable fast mode
    config = ReadingConfig(fast_mode=True)
    assert config.fast_mode is True
    assert config.active_model == "llama3.1:8b"

    # Test mode switching methods
    fast_config = config.enable_fast_mode()
    assert fast_config.fast_mode is True
    assert fast_config.active_model == "llama3.1:8b"

    quality_config = fast_config.enable_quality_mode()
    assert quality_config.fast_mode is False
    assert quality_config.active_model == "qwen3:8b"


def test_config_new_env_vars():
    """Test new environment variables for dual model system."""
    env_vars = {
        "COGNITIVE_READER_FAST_MODEL": "llama3.1:8b",
        "COGNITIVE_READER_QUALITY_MODEL": "qwen3:8b",
        "COGNITIVE_READER_FAST_MODE": "true",
    }

    with mock.patch.dict(os.environ, env_vars):
        config = ReadingConfig.from_env()

        assert config.fast_model == "llama3.1:8b"
        assert config.quality_model == "qwen3:8b"
        assert config.fast_mode is True
        assert config.active_model == "llama3.1:8b"
