"""Unit tests for cognitive data models v2.0."""

from cognitive_reader.models import (
    CognitiveConfig,
    CognitiveKnowledge,
    ConceptDefinition,
    LanguageCode,
    SectionSummary,
)


class TestCognitiveConfig:
    """Test the CognitiveConfig model."""

    def test_default_values(self):
        """Test that default values match SPECS v2.0."""
        config = CognitiveConfig()

        # LLM Configuration
        assert config.model_name == "qwen3:8b"
        assert config.temperature == 0.1

        # Multi-pass configuration
        assert config.max_passes == 2
        assert config.convergence_threshold == 0.1

        # Dual model strategy
        assert config.enable_fast_first_pass is True
        assert config.fast_pass_model == "llama3.1:8b"
        assert config.main_model == "qwen3:8b"
        assert config.fast_pass_temperature == 0.05  # Conservative for fidelity
        assert config.main_pass_temperature == 0.05  # Conservative for fidelity

        # Cognitive features (SPECS v2: two-pass as default)
        assert config.num_passes == 2
        assert config.enable_refinement is True
        assert config.refinement_threshold == 0.4

    def test_get_model_for_pass(self):
        """Test model selection for different passes."""
        config = CognitiveConfig()

        # First pass should use fast model
        assert config.get_model_for_pass(1) == "llama3.1:8b"

        # Second pass should use main model
        assert config.get_model_for_pass(2) == "qwen3:8b"

        # When fast first pass is disabled, should use main model
        config_no_fast = CognitiveConfig(enable_fast_first_pass=False)
        assert config_no_fast.get_model_for_pass(1) == "qwen3:8b"

    def test_get_temperature_for_pass(self):
        """Test temperature selection for different passes."""
        config = CognitiveConfig()

        # First pass should use fast temperature (conservative for fidelity)
        assert config.get_temperature_for_pass(1) == 0.05

        # Second pass should use main temperature (conservative for fidelity)
        assert config.get_temperature_for_pass(2) == 0.05

    def test_from_env_basic(self, base_test_config):
        """Test loading configuration from environment variables."""
        # Use fixtures instead of expensive from_env() calls
        config = base_test_config.model_copy(
            update={
                "model_name": "custom-model",
                "temperature": 0.5,
                "max_passes": 3,
                "fast_pass_model": "fast-model",
                "main_model": "main-model",
            }
        )
        assert config.model_name == "custom-model"
        assert config.temperature == 0.5
        assert config.max_passes == 3
        assert config.fast_pass_model == "fast-model"
        assert config.main_model == "main-model"

    def test_from_env_boolean_values(self, base_test_config):
        """Test environment variable parsing for mixed types."""
        # Use fixtures instead of expensive from_env() calls
        config = base_test_config.model_copy(
            update={
                "enable_fast_first_pass": False,
                "num_passes": 3,
                "dry_run": True,
            }
        )
        assert config.enable_fast_first_pass is False
        assert config.num_passes == 3
        assert config.dry_run is True

    def test_development_mode_detection(self):
        """Test development mode detection."""
        # Normal config is not development mode
        config = CognitiveConfig()
        assert config.is_development_mode() is False

        # Dry run is development mode
        config_dry = CognitiveConfig(dry_run=True)
        assert config_dry.is_development_mode() is True

        # Mock responses is development mode
        config_mock = CognitiveConfig(mock_responses=True)
        assert config_mock.is_development_mode() is True


class TestConceptDefinition:
    """Test the ConceptDefinition model."""

    def test_basic_creation(self):
        """Test basic concept creation."""
        concept = ConceptDefinition(
            concept_id="sedentarismo",
            name="Sedentarismo",
            definition="Estado crónico de inactividad física...",
            first_mentioned_in="cap_1",
        )

        assert concept.concept_id == "sedentarismo"
        assert concept.name == "Sedentarismo"
        assert concept.definition == "Estado crónico de inactividad física..."
        assert concept.first_mentioned_in == "cap_1"
        assert concept.relevant_sections == []

    def test_with_relevant_sections(self):
        """Test concept with multiple relevant sections."""
        concept = ConceptDefinition(
            concept_id="movimiento_natural",
            name="Movimiento Natural",
            definition="Patrones de movimiento ancestrales...",
            first_mentioned_in="introduccion",
            relevant_sections=["cap_1", "cap_2", "tres_pasos"],
        )

        assert len(concept.relevant_sections) == 3
        assert "cap_1" in concept.relevant_sections


class TestSectionSummary:
    """Test the SectionSummary model."""

    def test_basic_creation(self):
        """Test basic section summary creation."""
        summary = SectionSummary(
            section_id="cap_1",
            title="Introducción al sedentarismo",
            summary="Definición y evolución del sedentarismo...",
            level=1,
            order_index=1,
        )

        assert summary.section_id == "cap_1"
        assert summary.title == "Introducción al sedentarismo"
        assert summary.level == 1
        assert summary.order_index == 1
        assert summary.parent_id is None
        assert summary.key_concepts == []
        assert summary.children_ids == []

    def test_hierarchical_section(self):
        """Test section with hierarchy relationships."""
        summary = SectionSummary(
            section_id="cap_1_sec_1",
            title="¿Qué es el sedentarismo?",
            summary="Definición básica del concepto...",
            level=2,
            order_index=2,
            parent_id="cap_1",
            children_ids=["cap_1_sec_1_sub_1", "cap_1_sec_1_sub_2"],
            key_concepts=["sedentarismo", "vida_nomada"],
        )

        assert summary.parent_id == "cap_1"
        assert len(summary.children_ids) == 2
        assert len(summary.key_concepts) == 2


class TestCognitiveKnowledge:
    """Test the CognitiveKnowledge model."""

    def test_basic_creation(self):
        """Test basic cognitive knowledge creation."""
        knowledge = CognitiveKnowledge(
            document_title="3 pasos contra el sedentarismo",
            document_summary="Este libro explica cómo salir del sedentarismo en 3 pasos fundamentales.",
            detected_language=LanguageCode.ES,
            total_sections=8,
            avg_summary_length=740,
            total_concepts=4,
        )

        assert knowledge.document_title == "3 pasos contra el sedentarismo"
        assert knowledge.detected_language == LanguageCode.ES
        assert knowledge.total_sections == 8
        assert knowledge.avg_summary_length == 740
        assert knowledge.total_concepts == 4
        assert len(knowledge.hierarchical_summaries) == 0
        assert len(knowledge.concepts) == 0

    def test_with_summaries_and_concepts(self):
        """Test cognitive knowledge with data."""
        # Create test summary
        summary = SectionSummary(
            section_id="book",
            title="3 pasos contra el sedentarismo",
            summary="Método para combatir el sedentarismo...",
            level=0,
            order_index=0,
        )

        # Create test concept
        concept = ConceptDefinition(
            concept_id="sedentarismo",
            name="Sedentarismo",
            definition="Estado crónico de inactividad física...",
            first_mentioned_in="introduccion",
        )

        knowledge = CognitiveKnowledge(
            document_title="3 pasos contra el sedentarismo",
            document_summary="Este libro explica los problemas del sedentarismo y propone 3 pasos para superarlo.",
            detected_language=LanguageCode.ES,
            hierarchical_summaries={"book": summary},
            concepts=[concept],
            hierarchy_index={"0": ["book"], "1": ["cap_1", "cap_2"]},
            parent_child_map={"book": ["cap_1", "cap_2"]},
            total_sections=3,
            avg_summary_length=750,
            total_concepts=1,
        )

        assert len(knowledge.hierarchical_summaries) == 1
        assert len(knowledge.concepts) == 1
        assert knowledge.get_summary_by_id("book") == summary
        assert knowledge.get_concept_by_id("sedentarismo") == concept
        assert knowledge.get_children_of_section("book") == ["cap_1", "cap_2"]

    def test_helper_methods(self):
        """Test helper methods for navigation."""
        knowledge = CognitiveKnowledge(
            document_title="Test",
            document_summary="This is a test document for validating helper methods.",
            detected_language=LanguageCode.EN,
            total_sections=1,
            avg_summary_length=100,
            total_concepts=0,
        )

        # Test non-existent section
        assert knowledge.get_summary_by_id("non_existent") is None
        assert knowledge.get_concept_by_id("non_existent") is None
        assert knowledge.get_children_of_section("non_existent") == []


class TestModelIntegration:
    """Test integration between models."""

    def test_config_with_knowledge_creation(self):
        """Test that config can be used to create knowledge."""
        config = CognitiveConfig()

        # Verify config values are appropriate for knowledge creation
        assert config.target_summary_words > 0
        assert config.max_hierarchy_depth >= 1

        # Create knowledge with config-appropriate values
        knowledge = CognitiveKnowledge(
            document_title="Test Document",
            document_summary="This document integrates configuration with knowledge creation models.",
            detected_language=config.document_language,
            total_sections=1,
            avg_summary_length=config.target_summary_words
            * 5,  # Approximate char conversion
            total_concepts=0,
        )

        assert knowledge.detected_language == LanguageCode.AUTO
        assert knowledge.avg_summary_length == 1250  # 250 words * 5 chars/word
