"""Prompt management for LLM interactions."""

from __future__ import annotations

from ..models.knowledge import LanguageCode


class PromptManager:
    """Manages prompts for different LLM operations and languages.

    Centralizes all prompt templates with versioning and language support.
    Ensures consistent and optimized prompts for cognitive reading tasks.
    """

    # Prompt version for tracking changes
    PROMPT_VERSION = "v1.0.0"

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
            The prompt template string.

        Raises:
            ValueError: If prompt type or language is not supported.
        """
        if prompt_type not in self._prompts:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

        lang_prompts = self._prompts[prompt_type]

        # Try exact language match first, then fall back to English
        if language in lang_prompts:
            return lang_prompts[language]
        elif LanguageCode.EN in lang_prompts:
            return lang_prompts[LanguageCode.EN]
        else:
            raise ValueError(
                f"No prompt available for type '{prompt_type}' in language '{language}'"
            )

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

    def _initialize_prompts(self) -> dict[str, dict[LanguageCode, str]]:
        """Initialize all prompt templates.

        Returns:
            Dictionary of prompt templates organized by type and language.
        """
        return {
            "section_summary": {
                LanguageCode.EN: self._get_section_summary_prompt_en(),
                LanguageCode.ES: self._get_section_summary_prompt_es(),
            },
            "document_summary": {
                LanguageCode.EN: self._get_document_summary_prompt_en(),
                LanguageCode.ES: self._get_document_summary_prompt_es(),
            },
            "concept_extraction": {
                LanguageCode.EN: self._get_concept_extraction_prompt_en(),
                LanguageCode.ES: self._get_concept_extraction_prompt_es(),
            },
            "concept_definition": {
                LanguageCode.EN: self._get_concept_definition_prompt_en(),
                LanguageCode.ES: self._get_concept_definition_prompt_es(),
            },
        }

    def _get_section_summary_prompt_en(self) -> str:
        """English prompt for section summarization."""
        return """You are an expert document analyst performing cognitive reading. Your task is to create a concise, high-quality summary of a document section while considering the broader context.

SECTION TO SUMMARIZE:
Title: {section_title}
Content: {section_content}

ACCUMULATED CONTEXT FROM PREVIOUS SECTIONS:
{accumulated_context}

INSTRUCTIONS:
1. Create a clear, concise summary (2-4 sentences) that captures the main ideas
2. Consider how this section relates to the previous context
3. Identify 2-3 key concepts that are central to this section
4. Maintain consistency with the accumulated understanding
5. Focus on information that would be valuable for human understanding

RESPONSE FORMAT:
Summary: [Your 2-4 sentence summary here]
Key Concepts: [concept1, concept2, concept3]

Provide only the summary and key concepts, no additional commentary."""

    def _get_section_summary_prompt_es(self) -> str:
        """Spanish prompt for section summarization."""
        return """Eres un analista experto de documentos realizando lectura cognitiva. Tu tarea es crear un resumen conciso y de alta calidad de una sección del documento considerando el contexto más amplio.

SECCIÓN A RESUMIR:
Título: {section_title}
Contenido: {section_content}

CONTEXTO ACUMULADO DE SECCIONES ANTERIORES:
{accumulated_context}

INSTRUCCIONES:
1. Crea un resumen claro y conciso (2-4 oraciones) que capture las ideas principales
2. Considera cómo esta sección se relaciona con el contexto previo
3. Identifica 2-3 conceptos clave que son centrales en esta sección
4. Mantén consistencia con la comprensión acumulada
5. Enfócate en información valiosa para la comprensión humana

FORMATO DE RESPUESTA:
Resumen: [Tu resumen de 2-4 oraciones aquí]
Conceptos Clave: [concepto1, concepto2, concepto3]

Proporciona solo el resumen y los conceptos clave, sin comentarios adicionales."""

    def _get_document_summary_prompt_en(self) -> str:
        """English prompt for document-level summarization."""
        return """You are an expert document analyst creating a comprehensive document summary. Synthesize the section summaries into a coherent overview that captures the document's main narrative and key insights.

DOCUMENT TITLE: {document_title}

SECTION SUMMARIES:
{section_summaries}

INSTRUCTIONS:
1. Create a comprehensive summary (4-6 sentences) that synthesizes all sections
2. Maintain the logical flow and narrative structure of the document
3. Highlight the most important insights and conclusions
4. Ensure the summary is valuable for human reading and understanding
5. Connect related concepts across sections

RESPONSE FORMAT:
Document Summary: [Your comprehensive 4-6 sentence summary here]

Provide only the document summary, no additional commentary."""

    def _get_document_summary_prompt_es(self) -> str:
        """Spanish prompt for document-level summarization."""
        return """Eres un analista experto de documentos creando un resumen integral del documento. Sintetiza los resúmenes de secciones en una visión general coherente que capture la narrativa principal y las ideas clave del documento.

TÍTULO DEL DOCUMENTO: {document_title}

RESÚMENES DE SECCIONES:
{section_summaries}

INSTRUCCIONES:
1. Crea un resumen integral (4-6 oraciones) que sintetice todas las secciones
2. Mantén el flujo lógico y la estructura narrativa del documento
3. Destaca las ideas y conclusiones más importantes
4. Asegúrate de que el resumen sea valioso para la lectura y comprensión humana
5. Conecta conceptos relacionados entre secciones

FORMATO DE RESPUESTA:
Resumen del Documento: [Tu resumen integral de 4-6 oraciones aquí]

Proporciona solo el resumen del documento, sin comentarios adicionales."""

    def _get_concept_extraction_prompt_en(self) -> str:
        """English prompt for concept extraction."""
        return """You are an expert at identifying key concepts in text. Extract the most important concepts from this section that would be valuable for creating a glossary or knowledge base.

SECTION TO ANALYZE:
Title: {section_title}
Content: {section_content}

INSTRUCTIONS:
1. Identify 3-5 key concepts that are central to this section
2. Focus on concepts that are defined, explained, or given significant attention
3. Prefer concepts that would be useful in a glossary or for cross-referencing
4. Avoid overly common terms unless they have specific meaning in this context
5. Present concepts as clear, concise terms

RESPONSE FORMAT:
Key Concepts: [concept1, concept2, concept3, concept4, concept5]

Provide only the key concepts list, no additional commentary."""

    def _get_concept_extraction_prompt_es(self) -> str:
        """Spanish prompt for concept extraction."""
        return """Eres un experto en identificar conceptos clave en textos. Extrae los conceptos más importantes de esta sección que serían valiosos para crear un glosario o base de conocimiento.

SECCIÓN A ANALIZAR:
Título: {section_title}
Contenido: {section_content}

INSTRUCCIONES:
1. Identifica 3-5 conceptos clave que son centrales en esta sección
2. Enfócate en conceptos que son definidos, explicados o reciben atención significativa
3. Prefiere conceptos que serían útiles en un glosario o para referencias cruzadas
4. Evita términos demasiado comunes a menos que tengan significado específico en este contexto
5. Presenta conceptos como términos claros y concisos

FORMATO DE RESPUESTA:
Conceptos Clave: [concepto1, concepto2, concepto3, concepto4, concepto5]

Proporciona solo la lista de conceptos clave, sin comentarios adicionales."""

    def _get_concept_definition_prompt_en(self) -> str:
        """English prompt for concept definition generation."""
        return """You are an expert at creating clear, concise definitions for key concepts. Generate a precise definition for the given concept based on how it's used in the document context.

CONCEPT TO DEFINE: {concept_name}

CONTEXT FROM DOCUMENT:
{context}

INSTRUCTIONS:
1. Create a clear, precise definition (1-2 sentences maximum)
2. Focus on how this concept is used specifically in this document
3. Avoid generic dictionary definitions - be context-specific
4. Do not include reasoning process or thinking steps
5. Provide only the definition, no prefixes or additional commentary

RESPONSE FORMAT:
Provide ONLY the definition text. Do not include "Definition:", "Summary:", or any other prefixes.

Example: "A systematic approach to processing information that mimics human cognitive patterns for enhanced understanding."

Generate the definition now:"""

    def _get_concept_definition_prompt_es(self) -> str:
        """Spanish prompt for concept definition generation."""
        return """Eres un experto en crear definiciones claras y concisas para conceptos clave. Genera una definición precisa para el concepto dado basándote en cómo se usa en el contexto del documento.

CONCEPTO A DEFINIR: {concept_name}

CONTEXTO DEL DOCUMENTO:
{context}

INSTRUCCIONES:
1. Crea una definición clara y precisa (máximo 1-2 oraciones)
2. Enfócate en cómo se usa este concepto específicamente en este documento
3. Evita definiciones genéricas de diccionario - sé específico al contexto
4. No incluyas proceso de razonamiento o pasos de pensamiento
5. Proporciona solo la definición, sin prefijos o comentarios adicionales

FORMATO DE RESPUESTA:
Proporciona SOLO el texto de la definición. No incluyas "Definición:", "Resumen:", u otros prefijos.

Ejemplo: "Un enfoque sistemático para procesar información que imita patrones cognitivos humanos para mejorar la comprensión."

Genera la definición ahora:"""

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
