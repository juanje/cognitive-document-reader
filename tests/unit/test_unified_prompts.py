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
        prompt_types = ["section_summary", "document_summary", "concept_extraction", "concept_definition"]
        languages = [LanguageCode.EN, LanguageCode.ES]

        for prompt_type in prompt_types:
            for language in languages:
                prompt = self.prompt_manager.get_prompt(prompt_type, language)

                # Should contain the correct language instruction
                expected_lang_name = "English" if language == LanguageCode.EN else "Spanish"
                assert f"**IMPORTANT: Respond in {expected_lang_name}.**" in prompt

                # Should not contain the placeholder anymore
                assert "{{language}}" not in prompt

    def test_format_section_summary_prompt_with_spanish(self):
        """Test that format methods work with Spanish prompts."""
        formatted = self.prompt_manager.format_section_summary_prompt(
            section_title="Introducción",
            section_content="Este es el contenido de la sección.",
            accumulated_context="Contexto previo del documento.",
            language=LanguageCode.ES
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
            language=LanguageCode.EN
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
                language=language
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
                language=language
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
        assert not hasattr(prompt_manager, '_get_section_summary_prompt_en')
        assert not hasattr(prompt_manager, '_get_section_summary_prompt_es')
        assert not hasattr(prompt_manager, '_get_document_summary_prompt_en')
        assert not hasattr(prompt_manager, '_get_document_summary_prompt_es')
        assert not hasattr(prompt_manager, '_get_concept_extraction_prompt_en')
        assert not hasattr(prompt_manager, '_get_concept_extraction_prompt_es')
        assert not hasattr(prompt_manager, '_get_concept_definition_prompt_en')
        assert not hasattr(prompt_manager, '_get_concept_definition_prompt_es')

    def test_unified_prompts_are_complete(self):
        """Test that all unified prompts contain essential elements."""
        prompt_types = ["section_summary", "document_summary", "concept_extraction", "concept_definition"]

        for prompt_type in prompt_types:
            template = self.prompt_manager._prompts[prompt_type]

            # Should contain the language placeholder before formatting
            assert "{{language}}" in template

            # Should contain instructions and response format
            assert "INSTRUCTIONS:" in template
            assert "RESPONSE FORMAT:" in template or "Generate the definition now:" in template

    def test_version_updated(self):
        """Test that prompt version was updated to reflect unified system."""
        assert self.prompt_manager.PROMPT_VERSION == "v1.1.0"

    def test_language_names_mapping(self):
        """Test that language names mapping is correct."""
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.EN] == "English"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.ES] == "Spanish"
        assert self.prompt_manager.LANGUAGE_NAMES[LanguageCode.AUTO] == "English"
