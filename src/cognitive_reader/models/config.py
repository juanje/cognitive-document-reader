"""Configuration models for the Cognitive Document Reader."""

from __future__ import annotations

import os
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from .knowledge import LanguageCode


class ReadingConfig(BaseModel):
    """Simplified reading configuration for MVP - focus on essentials.

    This configuration model provides all necessary settings for the cognitive
    document reader with sensible defaults optimized for production use.
    """

    # LLM Configuration (proven models)
    model_name: str = Field(
        default="llama3.1:8b",
        description="LLM model name - llama3.1:8b proven best for instruction following",
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM - low value for consistent summaries",
    )

    # Document Processing (essential settings)
    chunk_size: int = Field(
        default=1000, gt=100, description="Optimal chunk size for cognitive reading"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        description="Chunk overlap - ~20% overlap maintains continuity",
    )
    context_window: int = Field(
        default=4096,
        gt=0,
        description="Context window size - standard limit that works",
    )

    # Performance Settings (simplified)
    timeout_seconds: int = Field(
        default=120, gt=0, description="Timeout for LLM operations in seconds"
    )
    max_retries: int = Field(
        default=3, ge=0, description="Maximum retry attempts for failed operations"
    )

    # Language and Output
    document_language: LanguageCode = Field(
        default=LanguageCode.AUTO,
        description="Document language - auto-detect or specify",
    )

    # Development modes (AI agent friendly)
    dry_run: bool = Field(
        default=False, description="Enable dry-run mode - no actual LLM calls"
    )
    mock_responses: bool = Field(
        default=False, description="Use simulated responses for testing"
    )
    validate_config_only: bool = Field(
        default=False, description="Only validate configuration, no processing"
    )

    # Environment variable mappings
    _env_mapping: ClassVar[dict[str, str]] = {
        "model_name": "COGNITIVE_READER_MODEL",
        "temperature": "COGNITIVE_READER_TEMPERATURE",
        "chunk_size": "COGNITIVE_READER_CHUNK_SIZE",
        "chunk_overlap": "COGNITIVE_READER_CHUNK_OVERLAP",
        "context_window": "COGNITIVE_READER_CONTEXT_WINDOW",
        "timeout_seconds": "COGNITIVE_READER_TIMEOUT_SECONDS",
        "max_retries": "COGNITIVE_READER_MAX_RETRIES",
        "document_language": "COGNITIVE_READER_LANGUAGE",
        "dry_run": "COGNITIVE_READER_DRY_RUN",
        "mock_responses": "COGNITIVE_READER_MOCK_RESPONSES",
        "validate_config_only": "COGNITIVE_READER_VALIDATE_CONFIG_ONLY",
    }

    @classmethod
    def from_env(cls) -> ReadingConfig:
        """Create config from environment variables with fallback to defaults.

        Returns:
            ReadingConfig: Configuration instance with values from environment
                          variables or defaults.
        """
        kwargs: dict[str, Any] = {}

        for field_name, env_var in cls._env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Handle type conversion based on field
                if field_name in {"temperature"}:
                    kwargs[field_name] = float(env_value)
                elif field_name in {
                    "chunk_size",
                    "chunk_overlap",
                    "context_window",
                    "timeout_seconds",
                    "max_retries",
                }:
                    kwargs[field_name] = int(env_value)
                elif field_name in {
                    "dry_run",
                    "mock_responses",
                    "validate_config_only",
                }:
                    kwargs[field_name] = env_value.lower() in ("true", "1", "yes", "on")
                elif field_name == "document_language":
                    kwargs[field_name] = LanguageCode(env_value)
                else:
                    kwargs[field_name] = env_value

        return cls(**kwargs)

    def is_development_mode(self) -> bool:
        """Check if any development mode is enabled.

        Returns:
            bool: True if dry_run, mock_responses, or validate_config_only is enabled.
        """
        return self.dry_run or self.mock_responses or self.validate_config_only
