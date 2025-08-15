"""Prompt management for LLM interactions."""

from __future__ import annotations

from ..models.knowledge import LanguageCode


class PromptManager:
    """Manages prompts for different LLM operations and languages.

    Centralizes all prompt templates with versioning and language support.
    Ensures consistent and optimized prompts for cognitive reading tasks.
    """

    # Prompt version for tracking changes
    PROMPT_VERSION = (
        "v1.4.0"  # Fixed concept contamination and improved definition accuracy
    )

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
        return """You are an expert document analyst performing cognitive reading. Your task is to create a faithful, accurate summary that represents the source text with maximum fidelity.

SECTION TO SUMMARIZE:
Title: {section_title}
Content: {section_content}

ACCUMULATED CONTEXT FROM PREVIOUS SECTIONS:
{accumulated_context}

CRITICAL FIDELITY REQUIREMENTS:
1. The SOURCE TEXT (section content) is your PRIMARY and ULTIMATE authority
2. Quote, paraphrase, or directly reference the original text whenever possible
3. Preserve technical terms, proper nouns, specific numbers, and details exactly as stated
4. NEVER add information, interpretations, or inferences not explicitly present in the source
5. If accumulated context conflicts with the source text, the SOURCE TEXT is always correct
6. Stay strictly within the boundaries of what the source explicitly states
7. When summarizing, use the author's own words and phrasing when possible

SUMMARY INSTRUCTIONS:
1. Create a comprehensive summary targeting approximately {target_words} words
2. Minimum {min_words} words for sufficient detail - Maximum {max_words} words to maintain focus
3. Count words as you write to stay within the {min_words}-{max_words} word range
4. Provide enough detail for RAG context and AI fine-tuning applications
5. Write in DIRECT SYNTHESIS style - present the content as facts, not meta-descriptions
6. AVOID meta-references like "The section explains...", "The document states...", "The author says..."
7. Consider how this section relates to the previous context only for coherent flow
8. Identify 3-5 key concepts that are explicitly mentioned in the SOURCE TEXT
9. Maintain consistency with accumulated understanding, but SOURCE TEXT overrides any conflicts
10. Focus on accurate representation of what the source actually says

STYLE EXAMPLES:
❌ BAD: "In this section, the document explains that [topic] is more than just [simple definition]..."
✅ GOOD: "[Topic] is more than just [simple definition] but represents [deeper understanding]..."

❌ BAD: "The author describes how [subject] functioned in [context]..."
✅ GOOD: "Throughout [time period], [subject] functioned as [specific role], establishing [key patterns]..."

RESPONSE FORMAT:
Summary: [Your comprehensive ~{target_words} word summary here]
Key Concepts: [concept1, concept2, concept3, concept4, concept5]

**IMPORTANT: Respond in {{language}}. Target approximately {target_words} words for optimal RAG context.**

Provide only the summary and key concepts, no additional commentary."""

    def _get_document_summary_prompt(self) -> str:
        """Unified prompt for document-level summarization."""
        return """You are an expert document analyst creating a comprehensive document summary. Your task is to faithfully synthesize the section summaries without adding information not present in them.

DOCUMENT TITLE: {document_title}

SECTION SUMMARIES:
{section_summaries}

CRITICAL FIDELITY REQUIREMENTS:
1. The SECTION SUMMARIES are your PRIMARY and ULTIMATE source of truth
2. ONLY use information explicitly stated in the provided section summaries
3. NEVER add interpretations, conclusions, or information not present in the summaries
4. Preserve technical terms, proper nouns, and specific details exactly as they appear
5. If you need to connect concepts, do so only based on what's explicitly stated
6. Stay strictly within the boundaries of what the section summaries contain
7. Maintain the logical relationships as presented in the original summaries

SYNTHESIS INSTRUCTIONS:
1. Create a comprehensive document summary targeting approximately {target_words} words
2. Minimum {min_words} words for sufficient coverage - Maximum {max_words} words to maintain focus
3. Count words as you write to stay within the {min_words}-{max_words} word range
4. Provide enough detail for RAG context and comprehensive understanding
5. Write in DIRECT SYNTHESIS style - present the content as unified knowledge, not meta-descriptions
6. AVOID meta-references like "The document discusses...", "This text covers...", "The sections explain..."
7. Maintain the logical flow and narrative structure of the document
8. Highlight the most important insights and conclusions that are explicitly present in the sections
9. Ensure the summary is valuable for human reading and AI applications
10. Connect related concepts and themes only when these connections are evident from the sections

STYLE EXAMPLES:
❌ BAD: "This document explores the concept of [topic] and explains how..."
✅ GOOD: "[Main concept] represents more than [surface description] - it reflects [deeper implications] that [broader context]..."

❌ BAD: "The text describes various movement patterns and discusses..."
✅ GOOD: "Human ancestors engaged in diverse movement patterns including walking, climbing, and carrying objects..."

RESPONSE FORMAT:
Document Summary: [Your comprehensive ~{target_words} word document synthesis here]

**IMPORTANT: Respond in {{language}}. Target approximately {target_words} words for comprehensive coverage.**

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
        return """You are an expert at creating clear, concise definitions for key concepts. Generate a precise definition that is faithful to how the concept appears and is used in the document context.

CONCEPT TO DEFINE: {concept_name}

CONTEXT FROM DOCUMENT:
{context}

FIDELITY GUIDELINES:
1. PRIMARY SOURCE: Use explicit definitions or descriptions from the document context first
2. CONTEXTUAL USAGE: If no explicit definition exists, define based on how the concept is used in context
3. PRESERVE MEANING: Stay true to the specific meaning the document assigns to this concept
4. AVOID EXTERNAL KNOWLEDGE: Don't impose standard definitions that contradict the document's usage
5. FLEXIBLE INFERENCE: When concepts aren't explicitly defined, make reasonable inferences from context
6. DOMAIN SENSITIVITY: Consider the document's domain and how terms might have specialized meanings

DEFINITION INSTRUCTIONS:
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
