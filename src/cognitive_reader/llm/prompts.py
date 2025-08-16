"""Prompt management for LLM interactions."""

from __future__ import annotations

from ..models.knowledge import LanguageCode


class PromptManager:
    """Manages prompts for different LLM operations and languages.

    Centralizes all prompt templates with versioning and language support.
    Ensures consistent and optimized prompts for cognitive reading tasks.
    Now supports separate system prompts for better LLM behavior control.
    """

    # Prompt version for tracking changes
    PROMPT_VERSION = "v1.5.0"  # Added system prompts support for better LLM behavior

    # Language code to full name mapping
    LANGUAGE_NAMES = {
        LanguageCode.EN: "English",
        LanguageCode.ES: "Spanish",
        LanguageCode.AUTO: "English",  # Default to English for auto-detection
    }

    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self._prompts = self._initialize_prompts()
        self._system_prompts = self._initialize_system_prompts()

    def get_prompt(
        self, prompt_type: str, language: LanguageCode = LanguageCode.EN
    ) -> str:
        """Get a user prompt template by type and language.

        Args:
            prompt_type: The type of prompt needed (e.g., 'section_summary', 'document_summary').
            language: The target language for the prompt.

        Returns:
            The user prompt template string formatted with the target language.

        Raises:
            ValueError: If the prompt type or language is not supported.
        """
        if prompt_type not in self._prompts:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

        # Get the unified template and format with target language
        template = self._prompts[prompt_type]
        language_name = self.LANGUAGE_NAMES.get(language, "English")

        # Replace the language placeholder
        return template.replace("{{language}}", language_name)

    def get_system_prompt(
        self, prompt_type: str, language: LanguageCode = LanguageCode.EN
    ) -> str:
        """Get a system prompt template by type and language.

        Args:
            prompt_type: The type of system prompt needed.
            language: The target language for the prompt.

        Returns:
            The system prompt template string formatted with the target language.

        Raises:
            ValueError: If the prompt type or language is not supported.
        """
        if prompt_type not in self._system_prompts:
            raise ValueError(f"Unsupported system prompt type: {prompt_type}")

        # Get the system prompt template and format with target language
        template = self._system_prompts[prompt_type]
        language_name = self.LANGUAGE_NAMES.get(language, "English")

        # Replace the language placeholder
        return template.replace("{{language}}", language_name)

    def format_section_summary_prompt(
        self,
        section_title: str,
        section_content: str,
        accumulated_context: str = "",
        language: LanguageCode = LanguageCode.EN,
        target_words: int = 250,
        min_words: int = 150,
        max_words: int = 400,
    ) -> str:
        """Format a prompt for section summarization.

        Args:
            section_title: Title of the section to summarize.
            section_content: Content of the section.
            accumulated_context: Previously accumulated context from other sections.
            language: Target language for the prompt.
            target_words: Target number of words for the summary.
            min_words: Minimum number of words for the summary.
            max_words: Maximum number of words for the summary.

        Returns:
            Formatted prompt ready for LLM.
        """
        template = self.get_prompt("section_summary", language)

        return template.format(
            section_title=section_title,
            section_content=section_content,
            accumulated_context=accumulated_context
            if accumulated_context
            else "None available yet.",
            target_words=target_words,
            min_words=min_words,
            max_words=max_words,
        )

    def format_document_summary_prompt(
        self,
        document_title: str,
        section_summaries: list[str],
        language: LanguageCode = LanguageCode.EN,
        target_words: int = 400,
        min_words: int = 250,
        max_words: int = 600,
    ) -> str:
        """Format a prompt for document-level summarization.

        Args:
            document_title: Title of the document.
            section_summaries: List of section summaries to synthesize.
            language: Target language for the prompt.
            target_words: Target number of words for the document summary.
            min_words: Minimum number of words for the document summary.
            max_words: Maximum number of words for the document summary.

        Returns:
            Formatted prompt ready for LLM.
        """
        template = self.get_prompt("document_summary", language)

        # Join section summaries with clear separators
        summaries_text = "\n\n".join(
            [
                f"Section {i + 1}: {summary}"
                for i, summary in enumerate(section_summaries)
            ]
        )

        return template.format(
            document_title=document_title,
            section_summaries=summaries_text,
            target_words=target_words,
            min_words=min_words,
            max_words=max_words,
        )

    def format_concept_extraction_prompt(
        self,
        section_title: str,
        section_content: str,
        language: LanguageCode = LanguageCode.EN,
    ) -> str:
        """Format a prompt for key concept extraction.

        Args:
            section_title: Title of the section.
            section_content: Content of the section.
            language: Target language for the prompt.

        Returns:
            Formatted prompt ready for LLM.
        """
        template = self.get_prompt("concept_extraction", language)

        return template.format(
            section_title=section_title, section_content=section_content
        )

    def format_concept_definition_prompt(
        self,
        concept_name: str,
        context: str,
        language: LanguageCode = LanguageCode.EN,
    ) -> str:
        """Format a prompt for concept definition generation.

        Args:
            concept_name: Name of the concept to define.
            context: Contextual information about the concept.
            language: Target language for the prompt.

        Returns:
            Formatted prompt ready for LLM.
        """
        template = self.get_prompt("concept_definition", language)

        return template.format(concept_name=concept_name, context=context)

    def _initialize_prompts(self) -> dict[str, str]:
        """Initialize all user prompt templates.

        Returns:
            Dictionary of user prompt templates by type.
        """
        return {
            "section_summary": self._get_section_summary_user_prompt(),
            "document_summary": self._get_document_summary_user_prompt(),
            "concept_extraction": self._get_concept_extraction_user_prompt(),
            "concept_definition": self._get_concept_definition_user_prompt(),
        }

    def _initialize_system_prompts(self) -> dict[str, str]:
        """Initialize all system prompt templates.

        Returns:
            Dictionary of system prompt templates by type.
        """
        return {
            "section_summary": self._get_section_summary_system_prompt(),
            "document_summary": self._get_document_summary_system_prompt(),
            "concept_extraction": self._get_concept_extraction_system_prompt(),
            "concept_definition": self._get_concept_definition_system_prompt(),
        }

    def _get_section_summary_system_prompt(self) -> str:
        """System prompt for section summarization - defines role and behavior."""
        return """You are an expert document analyst specialized in cognitive reading and faithful summarization.

CORE PRINCIPLES:
- Source text fidelity is paramount - the source content is your PRIMARY and ULTIMATE truth
- Use direct synthesis style: present information as factual knowledge, never as meta-descriptions
- Preserve technical terms, proper nouns, and specific details exactly as stated
- NEVER add information, interpretations, or inferences not explicitly present in the source
- Provide structured, comprehensive summaries optimized for RAG applications and AI fine-tuning

RESPONSE STYLE:
- Write in direct synthesis style: state facts directly from the source
- AVOID meta-references like "The document states...", "The section explains...", "The author says..."
- Use the source text's own words and phrasing when possible
- Count words carefully to meet specified target ranges
- Always respond in {{language}} when specified

QUALITY STANDARDS:
- Comprehensive coverage of source content within word limits
- Clear identification of 3-5 key concepts explicitly mentioned in source
- Accurate representation without external interpretation
- Consistent format with Summary and Key Concepts sections"""

    def _get_section_summary_user_prompt(self) -> str:
        """User prompt for section summarization - provides context and task."""
        return """SECTION TO SUMMARIZE:
Title: {section_title}
Content: {section_content}

ACCUMULATED CONTEXT FROM PREVIOUS SECTIONS:
{accumulated_context}

TASK:
Create a comprehensive summary of approximately {target_words} words ({min_words}-{max_words} range).
If accumulated context conflicts with the source text, the source text is always correct.
Identify 3-5 key concepts explicitly mentioned in the source text.

RESPONSE FORMAT:
Summary: [Your comprehensive ~{target_words} word summary here]
Key Concepts: [concept1, concept2, concept3, concept4, concept5]

Provide only the summary and key concepts, no additional commentary."""

    def _get_document_summary_system_prompt(self) -> str:
        """System prompt for document summarization - defines role and behavior."""
        return """You are an expert document analyst specialized in synthesizing comprehensive document summaries from section summaries.

CORE PRINCIPLES:
- Section summaries are your PRIMARY and ULTIMATE source of truth
- Use direct synthesis style: present content as unified knowledge, never as meta-descriptions
- Preserve technical terms, proper nouns, and specific details exactly as they appear
- ONLY use information explicitly stated in the provided section summaries
- Create coherent document-level narratives that maintain logical flow

RESPONSE STYLE:
- Write in direct synthesis style: present information as factual knowledge
- AVOID meta-references like "The document discusses...", "This text covers...", "The sections explain..."
- Connect related concepts only when connections are evident from the summaries
- Count words carefully to meet specified target ranges
- Always respond in {{language}} when specified

QUALITY STANDARDS:
- Comprehensive coverage within word limits
- Logical flow and narrative structure
- Valuable for both human reading and AI applications
- Faithful synthesis without external interpretation"""

    def _get_document_summary_user_prompt(self) -> str:
        """User prompt for document summarization - provides context and task."""
        return """DOCUMENT TITLE: {document_title}

SECTION SUMMARIES:
{section_summaries}

TASK:
Create a comprehensive document summary of approximately {target_words} words ({min_words}-{max_words} range).
Synthesize the section summaries into a coherent document-level narrative.
Highlight the most important insights and conclusions explicitly present in the sections.

RESPONSE FORMAT:
Document Summary: [Your comprehensive ~{target_words} word document synthesis here]

Provide only the document summary, no additional commentary."""

    def _get_concept_extraction_system_prompt(self) -> str:
        """System prompt for concept extraction - defines role and behavior."""
        return """You are an expert at identifying key concepts for glossary creation and knowledge management.

CORE PRINCIPLES:
- Focus on specialized knowledge, methodologies, and domain-specific terms
- Prioritize concepts that would benefit from definition or explanation
- Consider semantic importance over word frequency
- Extract precise, meaningful terms that represent unified ideas

SELECTION CRITERIA:
PRIORITIZE:
- Technical terms and specialized vocabulary
- Processes, methodologies, or systematic approaches
- Domain-specific concepts requiring context to understand
- Ideas that are defined, explained, or developed in detail
- Multi-word concepts representing unified ideas

AVOID:
- Common words without specialized meaning
- Generic actions or states without specific context
- Overly broad categories lacking precision
- Single words that are self-explanatory

RESPONSE STYLE:
- Present concepts as precise terms (1-3 words typically)
- Always respond in {{language}} when specified
- Focus on concepts that would be valuable in a glossary"""

    def _get_concept_extraction_user_prompt(self) -> str:
        """User prompt for concept extraction - provides context and task."""
        return """SECTION TO ANALYZE:
Title: {section_title}
Content: {section_content}

TASK:
Identify 3-5 key concepts that are central to this section's meaning.
Focus on concepts that represent specialized knowledge or would benefit from definition.

RESPONSE FORMAT:
Key Concepts: [concept1, concept2, concept3, concept4, concept5]

Provide only the key concepts list, no additional commentary."""

    def _get_concept_definition_system_prompt(self) -> str:
        """System prompt for concept definition - defines role and behavior."""
        return """You are an expert at creating clear, precise definitions for key concepts based on document context.

CORE PRINCIPLES:
- Document context is your PRIMARY source of truth
- Use explicit definitions from the document when available
- If no explicit definition exists, define based on contextual usage
- Stay faithful to the specific meaning the document assigns
- Avoid imposing external definitions that contradict document usage

DEFINITION QUALITY:
- Create comprehensive definitions (2-4 sentences typically)
- Focus on how the concept is used in this specific document context
- Include key characteristics, relationships, or applications when relevant
- Be context-specific and accurate rather than generic

RESPONSE STYLE:
- Write in direct definition style: state what the concept IS
- AVOID meta-references like "According to the text...", "The document defines this as..."
- Always respond in {{language}} when specified
- Provide only the definition text without prefixes or additional commentary"""

    def _get_concept_definition_user_prompt(self) -> str:
        """User prompt for concept definition - provides context and task."""
        return """CONCEPT TO DEFINE: {concept_name}

CONTEXT FROM DOCUMENT:
{context}

TASK:
Generate a precise definition that captures how this concept is used in the document context.
If the document provides an explicit definition, use that as your primary source.
Otherwise, define based on contextual usage and reasonable inference.

RESPONSE FORMAT:
Provide ONLY the definition text. Do not include "Definition:", "Summary:", or any other prefixes.

Example format: "A [category] characterized by [key attributes] and [distinguishing features]."

Generate the definition now:"""

    def get_available_prompt_types(self) -> list[str]:
        """Get list of available prompt types.

        Returns:
            List of available prompt type names.
        """
        return list(self._prompts.keys())

    def get_supported_languages(self) -> list[LanguageCode]:
        """Get list of supported languages.

        Returns:
            List of supported language codes.
        """
        return [LanguageCode.EN, LanguageCode.ES]
