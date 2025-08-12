"""Configuration models for the Cognitive Document Reader."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field

from .knowledge import LanguageCode


class CognitiveConfig(BaseModel):
    """Configuration for cognitive document processing v2.0.

    This configuration implements the dual model strategy and multi-pass processing
    according to SPECS v2.0 for authentic cognitive reading simulation.
    """

    # LLM Configuration
    model_name: str = Field(default="qwen3:8b", description="Default LLM model name (used when dual models not configured)")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="LLM temperature")

    # Multi-pass configuration (extensible design)
    max_passes: int = Field(default=2, ge=1, le=10, description="Maximum number of cognitive passes")
    convergence_threshold: float = Field(default=0.1, ge=0.01, le=1.0, description="Threshold to detect when additional passes add minimal value")

    # Dual model strategy: fast first scan + quality processing (Phase 2)
    enable_fast_first_pass: bool = Field(default=True, description="Use fast model for initial scan (always enabled)")
    fast_pass_model: str | None = Field(default="llama3.1:8b", description="Fast model for initial document scan")
    main_model: str | None = Field(default="qwen3:8b", description="Quality model for detailed cognitive processing")

    # Temperature settings
    fast_pass_temperature: float | None = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for fast scan")
    main_pass_temperature: float | None = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for quality processing")

    # Cognitive Features
    enable_second_pass: bool = Field(default=False, description="Enable second pass processing (disabled for Phase 1)")
    enable_refinement: bool = Field(default=True, description="Enable refinement during reading")
    refinement_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Threshold for triggering refinement (0.0=never, 1.0=always)"
    )

    # Document Processing
    chunk_size: int = Field(default=1000, gt=100, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks")
    context_window: int = Field(default=4096, gt=0, description="LLM context window limit")

    # Performance Settings
    timeout_seconds: int = Field(default=120, gt=0, description="Request timeout")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    document_language: LanguageCode = Field(default=LanguageCode.AUTO, description="Document language")

    # Summary Optimization for RAG/Fine-tuning
    target_summary_length: int = Field(default=800, gt=100, description="Target summary length in characters")
    min_summary_length: int = Field(default=400, gt=50, description="Minimum summary length in characters")
    max_summary_length: int = Field(default=1200, gt=100, description="Maximum summary length in characters")
    max_hierarchy_depth: int = Field(default=3, ge=1, description="Maximum hierarchy depth (0=book, 1=chapter, 2=section)")

    # Development Features
    dry_run: bool = Field(default=False, description="Enable dry-run mode (no actual LLM calls)")
    mock_responses: bool = Field(default=False, description="Use mock responses for testing")
    validate_config_only: bool = Field(default=False, description="Only validate configuration")

    # NOTE: max_hierarchy_depth is used for --structure-only --max-depth functionality

    @classmethod
    def from_env(cls) -> CognitiveConfig:
        """Create configuration from environment variables with fallback to defaults.

        Returns:
            CognitiveConfig: Configuration instance with values from environment
                          variables or defaults according to SPECS v2.0.
        """
        return cls(
            # LLM settings
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),

            # Multi-pass configuration (extensible design)
            max_passes=int(os.getenv("COGNITIVE_READER_MAX_PASSES", "2")),
            convergence_threshold=float(os.getenv("COGNITIVE_READER_CONVERGENCE_THRESHOLD", "0.1")),

            # Dual model settings (fast scan + quality processing) - Always enable fast pass, control second pass
            enable_fast_first_pass=os.getenv("COGNITIVE_READER_ENABLE_FAST_FIRST_PASS", "true").lower() == "true",
            fast_pass_model=os.getenv("COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"),
            main_model=os.getenv("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            fast_pass_temperature=float(os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE", "0.1")) if os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE") else None,
            main_pass_temperature=float(os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE", "0.3")) if os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE") else None,

            # Cognitive features
            enable_second_pass=os.getenv("COGNITIVE_READER_ENABLE_SECOND_PASS", "false").lower() == "true",
            enable_refinement=os.getenv("COGNITIVE_READER_ENABLE_REFINEMENT", "true").lower() == "true",
            refinement_threshold=float(os.getenv("COGNITIVE_READER_REFINEMENT_THRESHOLD", "0.4")),

            # Processing settings
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),

            # Performance settings
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(os.getenv("COGNITIVE_READER_LANGUAGE", "auto")),

            # Summary optimization for RAG/Fine-tuning
            target_summary_length=int(os.getenv("COGNITIVE_READER_TARGET_SUMMARY_LENGTH", "800")),
            min_summary_length=int(os.getenv("COGNITIVE_READER_MIN_SUMMARY_LENGTH", "400")),
            max_summary_length=int(os.getenv("COGNITIVE_READER_MAX_SUMMARY_LENGTH", "1200")),
            max_hierarchy_depth=int(os.getenv("COGNITIVE_READER_MAX_HIERARCHY_DEPTH", "3")),

            # Development features
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
            validate_config_only=os.getenv("COGNITIVE_READER_VALIDATE_CONFIG_ONLY", "false").lower() == "true",
        )

    def get_model_for_pass(self, pass_number: int) -> str:
        """Get the appropriate model for a specific pass.

        Args:
            pass_number: The pass number (1-based)

        Returns:
            str: Model name to use for this pass
        """
        if pass_number == 1 and self.enable_fast_first_pass and self.fast_pass_model:
            return self.fast_pass_model
        return self.main_model or self.model_name

    def get_temperature_for_pass(self, pass_number: int) -> float:
        """Get the appropriate temperature for a specific pass.

        Args:
            pass_number: The pass number (1-based)

        Returns:
            float: Temperature to use for this pass
        """
        if pass_number == 1 and self.enable_fast_first_pass and self.fast_pass_temperature is not None:
            return self.fast_pass_temperature
        if pass_number > 1 and self.main_pass_temperature is not None:
            return self.main_pass_temperature
        return self.temperature

    def is_development_mode(self) -> bool:
        """Check if any development mode is enabled.

        Returns:
            bool: True if any development or testing mode is enabled.
        """
        return (
            self.dry_run
            or self.mock_responses
            or self.validate_config_only
        )
