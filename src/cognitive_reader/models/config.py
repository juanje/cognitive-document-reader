"""Configuration models for the Cognitive Document Reader."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

from .knowledge import LanguageCode


class CognitiveConfig(BaseModel):
    """Configuration for cognitive document processing v2.0.

    This configuration implements the dual model strategy and multi-pass processing
    according to SPECS v2.0 for authentic cognitive reading simulation.
    """

    # LLM Configuration
    model_name: str = Field(
        default="qwen3:8b",
        description="Default LLM model name (used when dual models not configured)",
    )
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="LLM temperature"
    )

    # Multi-pass configuration (extensible design)
    max_passes: int = Field(
        default=2, ge=1, le=10, description="Maximum number of cognitive passes"
    )
    convergence_threshold: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        description="Threshold to detect when additional passes add minimal value",
    )

    # Dual model strategy: fast first scan + quality processing (Phase 2)
    enable_fast_first_pass: bool = Field(
        default=True, description="Use fast model for initial scan (always enabled)"
    )
    fast_pass_model: str | None = Field(
        default="llama3.1:8b", description="Fast model for initial document scan"
    )
    main_model: str | None = Field(
        default="qwen3:8b",
        description="Quality model for detailed cognitive processing",
    )

    # Temperature settings - optimized for maximum fidelity to source text
    fast_pass_temperature: float | None = Field(
        default=0.05,
        ge=0.0,
        le=2.0,
        description="Temperature for fast scan (very conservative for fidelity)",
    )
    main_pass_temperature: float | None = Field(
        default=0.05,
        ge=0.0,
        le=2.0,
        description="Temperature for quality processing (very conservative for fidelity)",
    )

    # Cognitive Features
    num_passes: int = Field(
        default=2,
        ge=1,
        description="Number of cognitive passes to perform (1=single-pass, 2=dual-pass, N=multi-pass)",
    )
    enable_refinement: bool = Field(
        default=True, description="Enable refinement during reading"
    )
    refinement_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Threshold for triggering refinement (0.0=never, 1.0=always)",
    )

    # Document Processing
    chunk_size: int = Field(
        default=1000, gt=100, description="Text chunk size for processing"
    )
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks")
    context_window: int = Field(
        default=16384,
        gt=0,
        description="LLM context window limit (safe for enriched context)",
    )

    # Performance Settings
    timeout_seconds: int = Field(default=120, gt=0, description="Request timeout")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    document_language: LanguageCode = Field(
        default=LanguageCode.AUTO, description="Document language"
    )

    # LLM Provider Configuration
    llm_provider: str = Field(
        default="ollama", description="LLM provider (ollama, openai, anthropic, etc.)"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama server base URL"
    )
    # Future: openai_api_key, anthropic_api_key, etc.

    # Summary Optimization for RAG/Fine-tuning (word-based for natural control)
    target_summary_words: int = Field(
        default=250, gt=20, description="Target summary length in words (~320 tokens)"
    )
    min_summary_words: int = Field(
        default=150, gt=10, description="Minimum summary length in words (~190 tokens)"
    )
    max_summary_words: int = Field(
        default=400, gt=30, description="Maximum summary length in words (~500 tokens)"
    )

    # Document-level summaries (longer for comprehensive understanding)
    target_document_summary_words: int = Field(
        default=400,
        gt=50,
        description="Target document summary length in words (~500 tokens)",
    )
    min_document_summary_words: int = Field(
        default=250,
        gt=20,
        description="Minimum document summary length in words (~320 tokens)",
    )
    max_document_summary_words: int = Field(
        default=600,
        gt=80,
        description="Maximum document summary length in words (~750 tokens)",
    )
    max_hierarchy_depth: int = Field(
        default=10,
        ge=1,
        description="Maximum hierarchy depth for processing (high default = no filtering)",
    )

    # Development Features
    dry_run: bool = Field(
        default=False, description="Enable dry-run mode (no actual LLM calls)"
    )
    mock_responses: bool = Field(
        default=False, description="Use mock responses for testing"
    )
    show_context_usage: bool = Field(
        default=False, description="Show context window usage for each LLM call"
    )
    validate_config_only: bool = Field(
        default=False, description="Only validate configuration"
    )
    save_partial_results: bool = Field(
        default=False, description="Save intermediate results during processing"
    )
    partial_results_dir: str = Field(
        default="./partial_results", description="Directory to save partial results"
    )
    single_pass: bool = Field(
        default=False,
        description="Force single-pass processing (disable additional passes for fast testing)",
    )
    save_intermediate: bool = Field(
        default=False,
        description="Save intermediate state between passes (useful for debugging and comparison)",
    )
    intermediate_dir: str = Field(
        default="./intermediate_passes",
        description="Directory to save intermediate pass results",
    )
    max_sections: int | None = Field(
        default=None,
        description="Maximum number of sections to process (None = no limit)",
    )
    disable_reasoning: bool = Field(
        default=False,
        description="Disable reasoning mode for reasoning models (faster, direct answers)",
    )
    skip_glossary: bool = Field(
        default=False,
        description="Skip concept definitions generation (faster processing, summaries only)",
    )
    log_file: Path | None = Field(
        default=None,
        description="File path to write logs to instead of stderr (None = use stderr)",
    )

    # Concept filtering parameters for glossary quality
    max_glossary_concepts: int = Field(
        default=50, description="Maximum number of concepts in glossary"
    )
    min_glossary_concepts: int = Field(
        default=10, description="Minimum number of concepts in glossary"
    )
    cross_section_score_cap: float = Field(
        default=0.5, description="Maximum score for cross-section relevance (0.0-1.0)"
    )
    complexity_score_multiplier: float = Field(
        default=0.2, description="Multiplier for word count in complexity scoring"
    )
    complexity_score_cap: float = Field(
        default=0.3, description="Maximum score for concept complexity (0.0-1.0)"
    )
    base_concept_score: float = Field(
        default=0.2, description="Base score for LLM-selected concepts (0.0-1.0)"
    )

    # NOTE: max_hierarchy_depth is used for --structure-only --max-depth functionality

    @staticmethod
    def _load_dotenv() -> None:
        """Load environment variables from .env file if it exists."""
        try:
            from dotenv import load_dotenv

            env_file = Path.cwd() / ".env"
            if env_file.exists():
                load_dotenv(
                    env_file, override=False
                )  # Don't override existing env vars
        except ImportError:
            # python-dotenv not installed, skip loading
            pass

    @classmethod
    def from_env(cls) -> CognitiveConfig:
        """Create configuration from environment variables with fallback to defaults.

        Automatically loads .env file if present before reading environment variables.

        Returns:
            CognitiveConfig: Configuration instance with values from environment
                          variables or defaults according to SPECS v2.0.
        """
        # Load .env file before reading environment variables
        cls._load_dotenv()
        return cls(
            # LLM settings
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),
            # Multi-pass configuration (extensible design)
            max_passes=int(os.getenv("COGNITIVE_READER_MAX_PASSES", "2")),
            convergence_threshold=float(
                os.getenv("COGNITIVE_READER_CONVERGENCE_THRESHOLD", "0.1")
            ),
            # Dual model settings (fast scan + quality processing) - Always enable fast pass, control second pass
            enable_fast_first_pass=os.getenv(
                "COGNITIVE_READER_ENABLE_FAST_FIRST_PASS", "true"
            ).lower()
            == "true",
            fast_pass_model=os.getenv(
                "COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"
            ),
            main_model=os.getenv("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            fast_pass_temperature=float(
                os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE", "0.05")
            )
            if os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE")
            else None,
            main_pass_temperature=float(
                os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE", "0.05")
            )
            if os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE")
            else None,
            # Cognitive features
            num_passes=int(os.getenv("COGNITIVE_READER_NUM_PASSES", "2")),
            enable_refinement=os.getenv(
                "COGNITIVE_READER_ENABLE_REFINEMENT", "true"
            ).lower()
            == "true",
            refinement_threshold=float(
                os.getenv("COGNITIVE_READER_REFINEMENT_THRESHOLD", "0.4")
            ),
            # Processing settings
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),
            # Performance settings
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(
                os.getenv("COGNITIVE_READER_LANGUAGE", "auto")
            ),
            # LLM Provider configuration
            llm_provider=os.getenv("COGNITIVE_READER_LLM_PROVIDER", "ollama"),
            ollama_base_url=os.getenv(
                "COGNITIVE_READER_OLLAMA_BASE_URL", "http://localhost:11434"
            ),
            # Summary optimization for RAG/Fine-tuning
            target_summary_words=int(
                os.getenv("COGNITIVE_READER_TARGET_SUMMARY_WORDS", "250")
            ),
            min_summary_words=int(
                os.getenv("COGNITIVE_READER_MIN_SUMMARY_WORDS", "150")
            ),
            max_summary_words=int(
                os.getenv("COGNITIVE_READER_MAX_SUMMARY_WORDS", "400")
            ),
            target_document_summary_words=int(
                os.getenv("COGNITIVE_READER_TARGET_DOCUMENT_SUMMARY_WORDS", "400")
            ),
            min_document_summary_words=int(
                os.getenv("COGNITIVE_READER_MIN_DOCUMENT_SUMMARY_WORDS", "250")
            ),
            max_document_summary_words=int(
                os.getenv("COGNITIVE_READER_MAX_DOCUMENT_SUMMARY_WORDS", "600")
            ),
            max_hierarchy_depth=int(
                os.getenv("COGNITIVE_READER_MAX_HIERARCHY_DEPTH", "10")
            ),
            # Development features
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower()
            == "true",
            show_context_usage=os.getenv(
                "COGNITIVE_READER_SHOW_CONTEXT_USAGE", "false"
            ).lower()
            == "true",
            validate_config_only=os.getenv(
                "COGNITIVE_READER_VALIDATE_CONFIG_ONLY", "false"
            ).lower()
            == "true",
            save_partial_results=os.getenv(
                "COGNITIVE_READER_SAVE_PARTIAL_RESULTS", "false"
            ).lower()
            == "true",
            partial_results_dir=os.getenv(
                "COGNITIVE_READER_PARTIAL_RESULTS_DIR", "./partial_results"
            ),
            single_pass=os.getenv("COGNITIVE_READER_SINGLE_PASS", "false").lower()
            == "true",
            save_intermediate=os.getenv(
                "COGNITIVE_READER_SAVE_INTERMEDIATE", "false"
            ).lower()
            == "true",
            intermediate_dir=os.getenv(
                "COGNITIVE_READER_INTERMEDIATE_DIR", "./intermediate_passes"
            ),
            max_sections=int(env_val)
            if (env_val := os.getenv("COGNITIVE_READER_MAX_SECTIONS"))
            else None,
            disable_reasoning=os.getenv(
                "COGNITIVE_READER_DISABLE_REASONING", "false"
            ).lower()
            == "true",
            skip_glossary=os.getenv("COGNITIVE_READER_SKIP_GLOSSARY", "false").lower()
            == "true",
            log_file=Path(log_path)
            if (log_path := os.getenv("COGNITIVE_READER_LOG_FILE"))
            else None,
            # Concept filtering parameters
            max_glossary_concepts=int(
                os.getenv("COGNITIVE_READER_MAX_GLOSSARY_CONCEPTS", "50")
            ),
            min_glossary_concepts=int(
                os.getenv("COGNITIVE_READER_MIN_GLOSSARY_CONCEPTS", "10")
            ),
            cross_section_score_cap=float(
                os.getenv("COGNITIVE_READER_CROSS_SECTION_SCORE_CAP", "0.5")
            ),
            complexity_score_multiplier=float(
                os.getenv("COGNITIVE_READER_COMPLEXITY_SCORE_MULTIPLIER", "0.2")
            ),
            complexity_score_cap=float(
                os.getenv("COGNITIVE_READER_COMPLEXITY_SCORE_CAP", "0.3")
            ),
            base_concept_score=float(
                os.getenv("COGNITIVE_READER_BASE_CONCEPT_SCORE", "0.2")
            ),
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
        if (
            pass_number == 1
            and self.enable_fast_first_pass
            and self.fast_pass_temperature is not None
        ):
            return self.fast_pass_temperature
        if pass_number > 1 and self.main_pass_temperature is not None:
            return self.main_pass_temperature
        return self.temperature

    def is_development_mode(self) -> bool:
        """Check if any development mode is enabled.

        Returns:
            bool: True if any development or testing mode is enabled.
        """
        return self.dry_run or self.mock_responses or self.validate_config_only
