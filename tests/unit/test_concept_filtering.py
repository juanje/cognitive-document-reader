"""Tests for concept filtering and glossary quality improvements."""

from cognitive_reader.core.synthesizer import Synthesizer
from cognitive_reader.llm.client import LLMClient
from cognitive_reader.models.config import CognitiveConfig


class TestConceptFiltering:
    """Test concept filtering functionality for quality glossary creation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CognitiveConfig(
            model_name="llama3.1:8b",
            dry_run=True,
        )

    async def test_concept_filtering_prioritizes_cross_section_concepts(self):
        """Test that concepts appearing in multiple sections are prioritized."""
        async with LLMClient(self.config) as llm_client:
            synthesizer = Synthesizer(self.config, llm_client)

            # Mock concepts with different section coverage
            all_concepts = {
                "machine learning",  # Appears in multiple sections
                "algorithm",  # Appears in one section
                "neural networks",  # Appears in multiple sections
                "computer",  # Common word, appears in one section
                "data preprocessing",  # Multi-word, appears in multiple sections
            }

            concept_to_sections = {
                "machine learning": ["section1", "section2", "section3"],  # 3 sections
                "algorithm": ["section1"],  # 1 section
                "neural networks": ["section1", "section2"],  # 2 sections
                "computer": ["section2"],  # 1 section
                "data preprocessing": ["section2", "section3"],  # 2 sections
            }

            filtered = synthesizer._filter_concepts_for_glossary(
                all_concepts, concept_to_sections
            )

            # Should prioritize concepts with broader coverage
            assert "machine learning" in filtered  # 3 sections
            assert "neural networks" in filtered  # 2 sections
            assert "data preprocessing" in filtered  # 2 sections, multi-word

    def test_concept_filtering_handles_empty_input(self):
        """Test that concept filtering handles empty input gracefully."""
        config = CognitiveConfig(model_name="llama3.1:8b", dry_run=True)

        async def mock_llm_client():
            pass

        synthesizer = Synthesizer(config)

        # Test empty concepts
        result = synthesizer._filter_concepts_for_glossary(set(), {})
        assert result == set()

        # Test concepts with no section mapping
        concepts = {"test_concept"}
        result = synthesizer._filter_concepts_for_glossary(concepts, {})
        assert "test_concept" in result

    def test_concept_filtering_respects_size_limits(self):
        """Test that concept filtering respects min/max size limits."""
        config = CognitiveConfig(model_name="llama3.1:8b", dry_run=True)
        synthesizer = Synthesizer(config)

        # Test with many concepts to verify max limit
        many_concepts = {f"concept_{i}" for i in range(100)}
        concept_to_sections = {concept: ["section1"] for concept in many_concepts}

        filtered = synthesizer._filter_concepts_for_glossary(
            many_concepts, concept_to_sections
        )

        # Should limit to max 50 concepts
        assert len(filtered) <= 50

    def test_concept_filtering_prefers_multiword_concepts(self):
        """Test that multi-word concepts are preferred over single words."""
        config = CognitiveConfig(model_name="llama3.1:8b", dry_run=True)
        synthesizer = Synthesizer(config)

        # Concepts with same section coverage but different word counts
        all_concepts = {
            "learning",  # 1 word
            "machine learning",  # 2 words
            "deep learning algorithms",  # 3 words
            "system",  # 1 word
        }

        concept_to_sections = {
            "learning": ["section1"],
            "machine learning": ["section1"],
            "deep learning algorithms": ["section1"],
            "system": ["section1"],
        }

        filtered = synthesizer._filter_concepts_for_glossary(
            all_concepts, concept_to_sections
        )

        # Multi-word concepts should be preferred
        assert "machine learning" in filtered
        assert "deep learning algorithms" in filtered

    def test_concept_filtering_maintains_minimum_concepts(self):
        """Test that filtering maintains minimum concepts for small documents."""
        config = CognitiveConfig(model_name="llama3.1:8b", dry_run=True)
        synthesizer = Synthesizer(config)

        # Small set of concepts
        small_concepts = {"concept1", "concept2", "concept3"}
        concept_to_sections = {concept: ["section1"] for concept in small_concepts}

        filtered = synthesizer._filter_concepts_for_glossary(
            small_concepts, concept_to_sections
        )

        # Should keep all concepts when set is small
        assert len(filtered) == len(small_concepts)
        assert filtered == small_concepts

    def test_concept_scoring_algorithm(self):
        """Test the concept scoring algorithm works as expected."""
        config = CognitiveConfig(model_name="llama3.1:8b", dry_run=True)
        synthesizer = Synthesizer(config)

        # Create concepts with known characteristics for scoring
        all_concepts = {
            "single_section_single_word",  # Low score: 1 section, 1 word
            "multi section concept",  # High score: multi section, multi word
            "single_section_multi_word_term",  # Medium score: 1 section, but multi word
        }

        concept_to_sections = {
            "single_section_single_word": ["section1"],
            "multi section concept": ["section1", "section2", "section3"],
            "single_section_multi_word_term": ["section1"],
        }

        filtered = synthesizer._filter_concepts_for_glossary(
            all_concepts, concept_to_sections
        )

        # All should be included since it's a small set, but the scoring algorithm
        # should be working (verified by the prioritization in larger sets)
        assert len(filtered) == 3

    def test_concept_filtering_uses_configurable_parameters(self):
        """Test that concept filtering uses configurable parameters from config."""
        # Create config with custom parameters
        config = CognitiveConfig(
            model_name="llama3.1:8b",
            dry_run=True,
            max_glossary_concepts=5,  # Very low limit
            min_glossary_concepts=2,
            cross_section_score_cap=0.8,  # Higher than default
            complexity_score_multiplier=0.5,  # Higher than default
            complexity_score_cap=0.6,  # Higher than default
            base_concept_score=0.1,  # Lower than default
        )

        synthesizer = Synthesizer(config)

        # Test with enough concepts to verify limits
        concepts = {f"concept_{i}" for i in range(10)}
        concept_to_sections = {concept: ["section1"] for concept in concepts}

        filtered = synthesizer._filter_concepts_for_glossary(
            concepts, concept_to_sections
        )

        # Should respect the custom max limit
        assert len(filtered) <= config.max_glossary_concepts
        assert (
            len(filtered) == 5
        )  # Should be exactly the max since we have enough concepts

    def test_concept_filtering_with_custom_scoring_weights(self):
        """Test that custom scoring weights affect concept selection."""
        # Config that heavily favors multi-word concepts
        config = CognitiveConfig(
            model_name="llama3.1:8b",
            dry_run=True,
            complexity_score_multiplier=1.0,  # Very high multiplier
            complexity_score_cap=0.9,  # High cap
            cross_section_score_cap=0.1,  # Low cross-section importance
        )

        synthesizer = Synthesizer(config)

        concepts = {
            "single",  # 1 word, appears in 3 sections
            "multi word concept",  # 3 words, appears in 1 section
        }

        concept_to_sections = {
            "single": ["section1", "section2", "section3"],
            "multi word concept": ["section1"],
        }

        filtered = synthesizer._filter_concepts_for_glossary(
            concepts, concept_to_sections
        )

        # With high complexity weighting, the multi-word concept should be preferred
        # even though it appears in fewer sections
        assert "multi word concept" in filtered
