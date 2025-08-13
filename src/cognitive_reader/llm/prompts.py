"""Prompt management for LLM interactions."""

from __future__ import annotations

from ..models.knowledge import LanguageCode


class PromptManager:
    """Manages prompts for different LLM operations and languages.

    Centralizes all prompt templates with versioning and language support.
    Ensures consistent and optimized prompts for cognitive reading tasks.
    """

    # Prompt version for tracking changes
    PROMPT_VERSION = "v1.4.0"  # Fixed concept contamination and improved definition accuracy

    # Language code to full name mapping
    LANGUAGE_NAMES = {
        LanguageCode.EN: "English",
        LanguageCode.ES: "Spanish",
        LanguageCode.AUTO: "English",  # Default to English for auto-detection
    }

    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self._prompts = self._initialize_prompts()

    def get_prompt(
        self, prompt_type: str, language: LanguageCode = LanguageCode.EN
    ) -> str:
        """Get a prompt template by type and language.

        Args:
            prompt_type: The type of prompt needed (e.g., 'section_summary', 'document_summary').
            language: The target language for the prompt.

        Returns:
            The prompt template string formatted with the target language.

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

    def format_section_summary_prompt(
        self,
        section_title: str,
        section_content: str,
        accumulated_context: str = "",
        language: LanguageCode = LanguageCode.EN,
    ) -> str:
        """Format a prompt for section summarization.

        Args:
            section_title: Title of the section to summarize.
            section_content: Content of the section.
            accumulated_context: Previously accumulated context from other sections.
            language: Target language for the prompt.

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
        )

    def format_document_summary_prompt(
        self,
        document_title: str,
        section_summaries: list[str],
        language: LanguageCode = LanguageCode.EN,
    ) -> str:
        """Format a prompt for document-level summarization.

        Args:
            document_title: Title of the document.
            section_summaries: List of section summaries to synthesize.
            language: Target language for the prompt.

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
            document_title=document_title, section_summaries=summaries_text
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

        return template.format(
            concept_name=concept_name, context=context
        )

    def _initialize_prompts(self) -> dict[str, str]:
        """Initialize all prompt templates.

        Returns:
            Dictionary of unified prompt templates by type.
        """
        return {
            "section_summary": self._get_section_summary_prompt(),
            "document_summary": self._get_document_summary_prompt(),
            "concept_extraction": self._get_concept_extraction_prompt(),
            "concept_definition": self._get_concept_definition_prompt(),
        }

    def _get_section_summary_prompt(self) -> str:
        """Unified prompt for section summarization."""
        return """You are an expert document analyst performing cognitive reading. Your task is to create a concise, high-quality summary of a document section while considering the broader context.

SECTION TO SUMMARIZE:
Title: {section_title}
Content: {section_content}

ACCUMULATED CONTEXT FROM PREVIOUS SECTIONS:
{accumulated_context}

INSTRUCTIONS:
1. Create a clear, concise summary (2-4 sentences) that captures the main ideas
2. Write in DIRECT SYNTHESIS style - present the content as facts, not meta-descriptions
3. AVOID meta-references like "The section explains...", "The document states...", "The author says..."
4. Consider how this section relates to the previous context
5. Identify 2-3 key concepts that are central to this section
6. Maintain consistency with the accumulated understanding
7. Focus on information that would be valuable for human understanding

STYLE EXAMPLES:
❌ BAD: "In this section, the document explains that [topic] is more than just [simple definition]..."
✅ GOOD: "[Topic] is more than just [simple definition] but represents [deeper understanding]..."

❌ BAD: "The author describes how [subject] functioned in [context]..."
✅ GOOD: "Throughout [time period], [subject] functioned as [specific role], establishing [key patterns]..."

RESPONSE FORMAT:
Summary: [Your 2-4 sentence direct synthesis here]
Key Concepts: [concept1, concept2, concept3]

**IMPORTANT: Respond in {{language}}.**

Provide only the summary and key concepts, no additional commentary."""

    def _get_document_summary_prompt(self) -> str:
        """Unified prompt for document-level summarization."""
        return """You are an expert document analyst creating a comprehensive document summary. Synthesize the section summaries into a coherent overview that captures the document's main narrative and key insights.

DOCUMENT TITLE: {document_title}

SECTION SUMMARIES:
{section_summaries}

INSTRUCTIONS:
1. Create a comprehensive summary (4-6 sentences) that synthesizes all sections
2. Write in DIRECT SYNTHESIS style - present the content as unified knowledge, not meta-descriptions
3. AVOID meta-references like "The document discusses...", "This text covers...", "The sections explain..."
4. Maintain the logical flow and narrative structure of the document
5. Highlight the most important insights and conclusions
6. Ensure the summary is valuable for human reading and understanding
7. Connect related concepts across sections

STYLE EXAMPLES:
❌ BAD: "This document explores the concept of [topic] and explains how..."
✅ GOOD: "[Main concept] represents more than [surface description] - it reflects [deeper implications] that [broader context]..."

❌ BAD: "The text describes various movement patterns and discusses..."
✅ GOOD: "Human ancestors engaged in diverse movement patterns including walking, climbing, and carrying objects..."

RESPONSE FORMAT:
Document Summary: [Your comprehensive 4-6 sentence direct synthesis here]

**IMPORTANT: Respond in {{language}}.**

Provide only the document summary, no additional commentary."""

    def _get_concept_extraction_prompt(self) -> str:
        """Unified prompt for concept extraction."""
        return """You are an expert at identifying key concepts for glossary creation. Extract concepts that represent specialized knowledge, methodologies, or domain-specific terms that would benefit from definition.

SECTION TO ANALYZE:
Title: {section_title}
Content: {section_content}

INSTRUCTIONS:
1. Identify 3-5 key concepts that are central to this section's meaning
2. PRIORITIZE concepts that are:
   - Technical terms or specialized vocabulary
   - Processes, methodologies, or systematic approaches
   - Domain-specific concepts that require context to understand
   - Ideas that are defined, explained, or developed in detail
   - Multi-word concepts that represent unified ideas
3. AVOID concepts that are:
   - Common words (unless they have specialized meaning here)
   - Generic actions or states without specific context
   - Overly broad categories that lack precision
   - Single words that are self-explanatory
4. Consider SEMANTIC IMPORTANCE over word frequency
5. Present concepts as precise, meaningful terms (can be 1-3 words)

CONCEPT SELECTION EXAMPLES:
✅ GOOD TYPES: [technical terms], [specialized methodologies], [domain-specific processes], [compound concepts]
❌ BAD TYPES: [common nouns], [generic verbs], [overly broad terms], [everyday words], [basic concepts]

EXAMPLE PATTERNS (adapt to your document's domain):
✅ For health/fitness: [specific conditions], [exercise techniques], [medical terms], [therapeutic approaches]
✅ For technology: [technical algorithms], [system architectures], [specialized tools], [domain frameworks]
❌ AVOID: generic words like "time", "people", "important", "system", "process" unless domain-specific

RESPONSE FORMAT:
Key Concepts: [concept1, concept2, concept3, concept4, concept5]

**IMPORTANT: Respond in {{language}}.**

Provide only the key concepts list, no additional commentary."""

    def _get_concept_definition_prompt(self) -> str:
        """Unified prompt for concept definition generation."""
        return """You are an expert at creating clear, concise definitions for key concepts. Generate a precise definition for the given concept based on how it's used in the document context.

CONCEPT TO DEFINE: {concept_name}

CONTEXT FROM DOCUMENT:
{context}

INSTRUCTIONS:
1. CAREFULLY READ the concept name and context to understand what you're defining
2. Create a clear, precise definition (1-2 sentences maximum) that accurately reflects the concept
3. Write in DIRECT DEFINITION style - state what the concept IS, not what "the document says it is"
4. Focus on how this concept is used specifically in this document context
5. Ensure the definition matches the CONCEPT NAME - do not confuse it with other concepts
6. Avoid generic dictionary definitions - be context-specific and accurate
7. AVOID meta-references like "According to the text...", "The document defines this as..."
8. Do not include reasoning process or thinking steps
9. Provide only the definition, no prefixes or additional commentary

**IMPORTANT: Respond in {{language}}.**

RESPONSE FORMAT:
Provide ONLY the definition text. Do not include "Definition:", "Summary:", or any other prefixes.

STYLE EXAMPLES:
❌ BAD: "According to the document, [concept] is defined as..."
✅ GOOD: "A [category] characterized by [key attributes] and [distinguishing features]."

Example: "A systematic approach to processing information that mimics human cognitive patterns for enhanced understanding."

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
