"""Tests for unified prompt system."""

from cognitive_reader.llm.prompts import PromptManager
from cognitive_reader.models.knowledge import LanguageCode


class TestUnifiedPromptSystem:
    """Test the unified prompt system functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.prompt_manager = PromptManager()

    def test_get_prompt_with_english(self):
        """Test that prompts are correctly formatted with English."""
        prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.EN)

        # Should contain the English instruction
        assert "**IMPORTANT: Respond in English.**" in prompt

        # Should contain the template variables
        assert "{section_title}" in prompt
        assert "{section_content}" in prompt
        assert "{accumulated_context}" in prompt

    def test_get_prompt_with_spanish(self):
        """Test that prompts are correctly formatted with Spanish."""
        prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.ES)

        # Should contain the Spanish instruction
        assert "**IMPORTANT: Respond in Spanish.**" in prompt

        # Should contain the template variables
        assert "{section_title}" in prompt
        assert "{section_content}" in prompt
        assert "{accumulated_context}" in prompt

    def test_get_prompt_with_auto_defaults_to_english(self):
        """Test that AUTO language code defaults to English."""
        prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.AUTO)

        # Should contain the English instruction
        assert "**IMPORTANT: Respond in English.**" in prompt

    def test_all_prompt_types_work_with_different_languages(self):
        """Test all prompt types work with different languages."""
        prompt_types = [
            "section_summary",
            "document_summary",
            "concept_extraction",
            "concept_definition",
        ]
        languages = [LanguageCode.EN, LanguageCode.ES]

        for prompt_type in prompt_types:
            for language in languages:
                prompt = self.prompt_manager.get_prompt(prompt_type, language)

                # Should contain the correct language instruction
                expected_lang_name = (
                    "English" if language == LanguageCode.EN else "Spanish"
                )
                assert f"**IMPORTANT: Respond in {expected_lang_name}.**" in prompt

                # Should not contain the placeholder anymore
                assert "{{language}}" not in prompt

    def test_format_section_summary_prompt_with_spanish(self):
        """Test that format methods work with Spanish prompts."""
        formatted = self.prompt_manager.format_section_summary_prompt(
            section_title="Introducción",
            section_content="Este es el contenido de la sección.",
            accumulated_context="Contexto previo del documento.",
            language=LanguageCode.ES,
        )

        # Should contain the Spanish instruction
        assert "**IMPORTANT: Respond in Spanish.**" in formatted

        # Should have variables replaced
        assert "Introducción" in formatted
        assert "Este es el contenido de la sección." in formatted
        assert "Contexto previo del documento." in formatted

        # Should not contain template variables
        assert "{section_title}" not in formatted
        assert "{section_content}" not in formatted
        assert "{accumulated_context}" not in formatted

    def test_format_section_summary_prompt_with_english(self):
        """Test that format methods work with English prompts."""
        formatted = self.prompt_manager.format_section_summary_prompt(
            section_title="Introduction",
            section_content="This is the section content.",
            accumulated_context="Previous document context.",
            language=LanguageCode.EN,
        )

        # Should contain the English instruction
        assert "**IMPORTANT: Respond in English.**" in formatted

        # Should have variables replaced
        assert "Introduction" in formatted
        assert "This is the section content." in formatted
        assert "Previous document context." in formatted

    def test_format_document_summary_prompt_multilingual(self):
        """Test document summary formatting with different languages."""
        for language in [LanguageCode.EN, LanguageCode.ES]:
            formatted = self.prompt_manager.format_document_summary_prompt(
                document_title="Test Document",
                section_summaries=["Summary 1", "Summary 2"],
                language=language,
            )

            # Should contain correct language instruction
            expected_lang_name = "English" if language == LanguageCode.EN else "Spanish"
            assert f"**IMPORTANT: Respond in {expected_lang_name}.**" in formatted

            # Should have variables replaced
            assert "Test Document" in formatted
            assert "Summary 1" in formatted
            assert "Summary 2" in formatted

    def test_format_concept_definition_prompt_multilingual(self):
        """Test concept definition formatting with different languages."""
        for language in [LanguageCode.EN, LanguageCode.ES]:
            formatted = self.prompt_manager.format_concept_definition_prompt(
                concept_name="machine learning",
                context="Context about machine learning in the document.",
                language=language,
            )

            # Should contain correct language instruction
            expected_lang_name = "English" if language == LanguageCode.EN else "Spanish"
            assert f"**IMPORTANT: Respond in {expected_lang_name}.**" in formatted

            # Should have variables replaced
            assert "machine learning" in formatted
            assert "Context about machine learning in the document." in formatted

    def test_no_language_code_duplication_in_prompts(self):
        """Test that no old language-specific methods remain."""
        # All prompt methods should be unified now
        prompt_manager = PromptManager()

        # These old methods should not exist
        assert not hasattr(prompt_manager, "_get_section_summary_prompt_en")
        assert not hasattr(prompt_manager, "_get_section_summary_prompt_es")
        assert not hasattr(prompt_manager, "_get_document_summary_prompt_en")
        assert not hasattr(prompt_manager, "_get_document_summary_prompt_es")
        assert not hasattr(prompt_manager, "_get_concept_extraction_prompt_en")
        assert not hasattr(prompt_manager, "_get_concept_extraction_prompt_es")
        assert not hasattr(prompt_manager, "_get_concept_definition_prompt_en")
        assert not hasattr(prompt_manager, "_get_concept_definition_prompt_es")

    def test_unified_prompts_are_complete(self):
        """Test that all unified prompts contain essential elements."""
        prompt_types = [
            "section_summary",
            "document_summary",
            "concept_extraction",
            "concept_definition",
        ]

        for prompt_type in prompt_types:
            template = self.prompt_manager._prompts[prompt_type]

            # Should contain the language placeholder before formatting
            assert "{{language}}" in template

            # Should contain instructions and response format
            assert "INSTRUCTIONS:" in template
            assert (
                "RESPONSE FORMAT:" in template
                or "Generate the definition now:" in template
            )

    def test_version_updated(self):
        """Test that prompt version was updated to reflect concept contamination fixes."""
        assert self.prompt_manager.PROMPT_VERSION == "v1.4.0"

    def test_language_names_mapping(self):
        """Test that language names mapping is correct."""
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.EN] == "English"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.ES] == "Spanish"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.AUTO] == "English"

    def test_direct_synthesis_instructions_in_prompts(self):
        """Test that all prompts include direct synthesis style instructions."""
        prompt_types = ["section_summary", "document_summary", "concept_definition"]

        for prompt_type in prompt_types:
            template = self.prompt_manager._prompts[prompt_type]

            # Should contain direct synthesis instructions
            assert "DIRECT" in template and (
                "SYNTHESIS" in template or "DEFINITION" in template
            )

            # Should contain avoidance of meta-references
            assert "AVOID meta-references" in template

            # Should contain style examples
            assert "STYLE EXAMPLES:" in template
            assert "❌ BAD:" in template
            assert "✅ GOOD:" in template

    def test_section_summary_prompt_quality_instructions(self):
        """Test that section summary prompt has quality instructions."""
        prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.EN)

        # Should contain specific bad examples to avoid
        assert '"The section explains..."' in prompt
        assert '"The document states..."' in prompt
        assert '"The author says..."' in prompt

        # Should contain generic good examples with placeholders (no contamination)
        assert "[Topic] is more than just [simple definition]" in prompt
        assert "Throughout [time period], [subject] functioned" in prompt

        # Should emphasize direct synthesis
        assert "direct synthesis" in prompt.lower()

    def test_document_summary_prompt_quality_instructions(self):
        """Test that document summary prompt has quality instructions."""
        prompt = self.prompt_manager.get_prompt("document_summary", LanguageCode.EN)

        # Should contain specific bad examples to avoid
        assert '"The document discusses..."' in prompt
        assert '"This text covers..."' in prompt

        # Should contain generic good examples with placeholders (no contamination)
        assert "[Main concept] represents more than [surface description]" in prompt
        assert "Human ancestors engaged in diverse movement patterns" in prompt

        # Should emphasize direct synthesis
        assert "direct synthesis" in prompt.lower()

    def test_concept_definition_prompt_quality_instructions(self):
        """Test that concept definition prompt has quality instructions."""
        prompt = self.prompt_manager.get_prompt("concept_definition", LanguageCode.EN)

        # Should contain specific bad examples to avoid
        assert '"According to the text..."' in prompt
        assert '"The document defines this as..."' in prompt

        # Should contain generic good examples with placeholders (no contamination)
        assert "A [category] characterized by [key attributes]" in prompt

        # Should emphasize direct definition style
        assert "DIRECT DEFINITION style" in prompt

    def test_concept_extraction_prompt_quality_instructions(self):
        """Test that concept extraction prompt has enhanced quality instructions."""
        prompt = self.prompt_manager.get_prompt("concept_extraction", LanguageCode.EN)

        # Should contain semantic prioritization instructions
        assert "SEMANTIC IMPORTANCE over word frequency" in prompt

        # Should prioritize specialized terms
        assert "Technical terms or specialized vocabulary" in prompt
        assert "Processes, methodologies, or systematic approaches" in prompt
        assert "Domain-specific concepts" in prompt

        # Should avoid common words
        assert "Common words" in prompt
        assert "Generic actions" in prompt
        assert "self-explanatory" in prompt

        # Should contain concept selection guidance
        assert "CONCEPT SELECTION EXAMPLES:" in prompt or "EXAMPLE PATTERNS" in prompt
        assert "technical terms" in prompt.lower()
        assert "specialized" in prompt.lower()

        # Should show what to avoid in general terms
        assert "generic" in prompt.lower() or "common" in prompt.lower()
        assert "avoid" in prompt.lower()

    def test_concept_extraction_multilingual_examples(self):
        """Test that concept extraction has proper guidance in multiple languages."""
        prompt_en = self.prompt_manager.get_prompt(
            "concept_extraction", LanguageCode.EN
        )
        prompt_es = self.prompt_manager.get_prompt(
            "concept_extraction", LanguageCode.ES
        )

        # Both should contain proper language instruction and guidance
        for prompt, lang in [(prompt_en, "English"), (prompt_es, "Spanish")]:
            assert f"**IMPORTANT: Respond in {lang}.**" in prompt
            assert "GOOD TYPES:" in prompt
            assert "BAD TYPES:" in prompt
            assert "domain-specific" in prompt.lower()
            assert "technical" in prompt.lower()
