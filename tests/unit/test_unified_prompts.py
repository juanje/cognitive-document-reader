"""Tests for unified prompt system."""

from cognitive_reader.llm.prompts import PromptManager
from cognitive_reader.models.knowledge import LanguageCode


class TestUnifiedPromptSystem:
    """Test the unified prompt system functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.prompt_manager = PromptManager()

    def test_get_prompt_with_english(self):
        """Test that user prompts contain task context without language instructions."""
        user_prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.EN)
        system_prompt = self.prompt_manager.get_system_prompt("section_summary", LanguageCode.EN)

        # User prompt should NOT contain language instruction (moved to system prompt)
        assert "**IMPORTANT: Respond in English." not in user_prompt

        # System prompt SHOULD contain the English instruction
        assert "English" in system_prompt

        # User prompt should contain the task and template variables
        assert "{section_title}" in user_prompt
        assert "{section_content}" in user_prompt
        assert "{accumulated_context}" in user_prompt
        assert "SECTION TO SUMMARIZE:" in user_prompt

    def test_get_prompt_with_spanish(self):
        """Test that user prompts contain task context without language instructions."""
        user_prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.ES)
        system_prompt = self.prompt_manager.get_system_prompt("section_summary", LanguageCode.ES)

        # User prompt should NOT contain language instruction (moved to system prompt)
        assert "**IMPORTANT: Respond in Spanish." not in user_prompt

        # System prompt SHOULD contain the Spanish instruction
        assert "Spanish" in system_prompt

        # User prompt should contain the task and template variables
        assert "{section_title}" in user_prompt
        assert "{section_content}" in user_prompt
        assert "{accumulated_context}" in user_prompt

    def test_get_prompt_with_auto_defaults_to_english(self):
        """Test that AUTO language code defaults to English."""
        user_prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.AUTO)
        system_prompt = self.prompt_manager.get_system_prompt("section_summary", LanguageCode.AUTO)

        # User prompt should NOT contain language instruction
        assert "**IMPORTANT: Respond in English." not in user_prompt

        # System prompt should default to English
        assert "English" in system_prompt

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
                user_prompt = self.prompt_manager.get_prompt(prompt_type, language)
                system_prompt = self.prompt_manager.get_system_prompt(prompt_type, language)

                # User prompt should NOT contain language instructions
                expected_lang_name = (
                    "English" if language == LanguageCode.EN else "Spanish"
                )
                assert f"**IMPORTANT: Respond in {expected_lang_name}." not in user_prompt

                # System prompt should contain the correct language reference
                assert expected_lang_name in system_prompt

                # Should not contain the placeholder anymore (in user prompt)
                assert "{{language}}" not in user_prompt

    def test_format_section_summary_prompt_with_spanish(self):
        """Test that format methods work and don't include language instructions in user prompt."""
        formatted = self.prompt_manager.format_section_summary_prompt(
            section_title="Introducción",
            section_content="Este es el contenido de la sección.",
            accumulated_context="Contexto previo del documento.",
            language=LanguageCode.ES,
        )

        # Should NOT contain the Spanish instruction (moved to system prompt)
        assert "**IMPORTANT: Respond in Spanish." not in formatted

        # Should have variables replaced
        assert "Introducción" in formatted
        assert "Este es el contenido de la sección." in formatted
        assert "Contexto previo del documento." in formatted

        # Should not contain template variables
        assert "{section_title}" not in formatted
        assert "{section_content}" not in formatted
        assert "{accumulated_context}" not in formatted

    def test_format_section_summary_prompt_with_english(self):
        """Test that format methods work and don't include language instructions in user prompt."""
        formatted = self.prompt_manager.format_section_summary_prompt(
            section_title="Introduction",
            section_content="This is the section content.",
            accumulated_context="Previous document context.",
            language=LanguageCode.EN,
        )

        # Should NOT contain the English instruction (moved to system prompt)
        assert "**IMPORTANT: Respond in English." not in formatted

        # Should have variables replaced
        assert "Introduction" in formatted
        assert "This is the section content." in formatted
        assert "Previous document context." in formatted

    def test_format_document_summary_prompt_multilingual(self):
        """Test document summary formatting works without language instructions in user prompt."""
        for language in [LanguageCode.EN, LanguageCode.ES]:
            formatted = self.prompt_manager.format_document_summary_prompt(
                document_title="Test Document",
                section_summaries=["Summary 1", "Summary 2"],
                language=language,
            )

            # Should NOT contain language instruction in user prompt (moved to system prompt)
            expected_lang_name = "English" if language == LanguageCode.EN else "Spanish"
            assert f"**IMPORTANT: Respond in {expected_lang_name}." not in formatted

            # Should have variables replaced
            assert "Test Document" in formatted
            assert "Summary 1" in formatted
            assert "Summary 2" in formatted

    def test_format_concept_definition_prompt_multilingual(self):
        """Test concept definition formatting works without language instructions in user prompt."""
        for language in [LanguageCode.EN, LanguageCode.ES]:
            formatted = self.prompt_manager.format_concept_definition_prompt(
                concept_name="machine learning",
                context="Context about machine learning in the document.",
                language=language,
            )

            # Should NOT contain language instruction in user prompt (moved to system prompt)
            expected_lang_name = "English" if language == LanguageCode.EN else "Spanish"
            assert f"**IMPORTANT: Respond in {expected_lang_name}.**" not in formatted

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
        """Test that system and user prompts contain essential elements."""
        prompt_types = [
            "section_summary",
            "document_summary",
            "concept_extraction",
            "concept_definition",
        ]

        for prompt_type in prompt_types:
            user_template = self.prompt_manager._prompts[prompt_type]
            system_template = self.prompt_manager._system_prompts[prompt_type]

            # User template should NOT contain language placeholder (moved to system)
            assert "{{language}}" not in user_template

            # System template should contain language placeholder
            assert "{{language}}" in system_template

            # User prompt should contain task structure
            assert ("TASK:" in user_template or "RESPONSE FORMAT:" in user_template)

            # System prompt should contain behavioral guidance
            assert ("CORE PRINCIPLES" in system_template or "expert" in system_template.lower())

    def test_version_updated(self):
        """Test that prompt version was updated to reflect system prompts architecture."""
        assert self.prompt_manager.PROMPT_VERSION == "v1.5.0"

    def test_language_names_mapping(self):
        """Test that language names mapping is correct."""
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.EN] == "English"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.ES] == "Spanish"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.AUTO] == "English"

    def test_direct_synthesis_instructions_in_prompts(self):
        """Test that system prompts include direct synthesis style instructions."""
        prompt_types = ["section_summary", "document_summary", "concept_definition"]

        for prompt_type in prompt_types:
            system_template = self.prompt_manager._system_prompts[prompt_type]

            # System prompts should contain behavioral instructions
            assert (
                "CORE PRINCIPLES" in system_template or
                "direct synthesis" in system_template.lower() or
                "RESPONSE STYLE" in system_template
            )

            # System prompt should contain style guidance
            assert (
                "AVOID meta-references" in system_template or
                "direct synthesis" in system_template.lower()
            )

    def test_section_summary_prompt_quality_instructions(self):
        """Test that section summary system prompt has quality instructions."""
        system_prompt = self.prompt_manager.get_system_prompt("section_summary", LanguageCode.EN)
        user_prompt = self.prompt_manager.get_prompt("section_summary", LanguageCode.EN)

        # System prompt should contain behavioral guidance
        assert "expert document analyst" in system_prompt.lower()

        # User prompt should contain task structure
        assert "SECTION TO SUMMARIZE:" in user_prompt

        # System prompt should contain behavioral guidance (examples moved there)
        assert "AVOID meta-references" in system_prompt or "direct synthesis" in system_prompt.lower()

    def test_document_summary_prompt_quality_instructions(self):
        """Test that document summary system prompt has quality instructions."""
        system_prompt = self.prompt_manager.get_system_prompt("document_summary", LanguageCode.EN)
        user_prompt = self.prompt_manager.get_prompt("document_summary", LanguageCode.EN)

        # System prompt should contain behavioral guidance
        assert "expert document analyst" in system_prompt.lower()

        # User prompt should contain task structure
        assert "DOCUMENT TITLE:" in user_prompt

        # System prompt should contain behavioral guidance
        assert "AVOID meta-references" in system_prompt or "direct synthesis" in system_prompt.lower()

    def test_concept_definition_prompt_quality_instructions(self):
        """Test that concept definition system prompt has quality instructions."""
        system_prompt = self.prompt_manager.get_system_prompt("concept_definition", LanguageCode.EN)
        user_prompt = self.prompt_manager.get_prompt("concept_definition", LanguageCode.EN)

        # System prompt should contain behavioral guidance
        assert "expert" in system_prompt.lower()

        # User prompt should contain task structure
        assert "CONCEPT TO DEFINE:" in user_prompt

        # System prompt should contain behavioral guidance
        assert "AVOID meta-references" in system_prompt or "direct definition" in system_prompt.lower()

        # System prompt should emphasize direct definition style
        assert "DIRECT" in system_prompt or "direct definition" in system_prompt.lower()

    def test_concept_extraction_prompt_quality_instructions(self):
        """Test that concept extraction system prompt has enhanced quality instructions."""
        system_prompt = self.prompt_manager.get_system_prompt("concept_extraction", LanguageCode.EN)
        user_prompt = self.prompt_manager.get_prompt("concept_extraction", LanguageCode.EN)

        # System prompt should contain conceptual guidance
        assert ("specialized knowledge" in system_prompt or "expert" in system_prompt.lower())

        # User prompt should contain task structure
        assert "SECTION TO ANALYZE:" in user_prompt

        # System prompt should contain guidance for specialized terms
        assert ("specialized" in system_prompt.lower() or "technical" in system_prompt.lower())

        # System prompt should contain guidance about what to avoid
        assert ("Common words" in system_prompt or "avoid" in system_prompt.lower())

        # System prompt should contain concept selection guidance
        assert ("technical" in system_prompt.lower() and "specialized" in system_prompt.lower())

        # System prompt should show what to avoid
        assert ("AVOID" in system_prompt or "avoid" in system_prompt.lower())

    def test_concept_extraction_multilingual_examples(self):
        """Test that concept extraction works properly in multiple languages."""
        system_prompt_en = self.prompt_manager.get_system_prompt("concept_extraction", LanguageCode.EN)
        system_prompt_es = self.prompt_manager.get_system_prompt("concept_extraction", LanguageCode.ES)

        user_prompt_en = self.prompt_manager.get_prompt("concept_extraction", LanguageCode.EN)
        user_prompt_es = self.prompt_manager.get_prompt("concept_extraction", LanguageCode.ES)

        # System prompts should contain language references
        assert "English" in system_prompt_en
        assert "Spanish" in system_prompt_es

        # User prompts should NOT contain language instructions
        assert "**IMPORTANT: Respond in English." not in user_prompt_en
        assert "**IMPORTANT: Respond in Spanish." not in user_prompt_es
