"""Hierarchical synthesis engine for document knowledge."""

from __future__ import annotations

import logging

from ..llm.client import LLMClient
from ..models.config import CognitiveConfig
from ..models.document import CognitiveKnowledge, DocumentSection, SectionSummary
from ..models.knowledge import ConceptDefinition, LanguageCode
from ..utils.text_cleaning import clean_section_title

logger = logging.getLogger(__name__)


class Synthesizer:
    """Hierarchical synthesis engine for document knowledge.

    Performs bottom-up synthesis from individual sections to complete document
    understanding, creating summaries at each level of the hierarchy.
    """

    def __init__(self, config: CognitiveConfig) -> None:
        """Initialize the synthesizer.

        Args:
            config: Reading configuration with synthesis settings.
        """
        self.config = config

    async def synthesize_document(
        self,
        sections: list[DocumentSection],
        section_summaries: dict[str, SectionSummary],
        document_title: str,
        detected_language: LanguageCode,
    ) -> CognitiveKnowledge:
        """Synthesize complete document knowledge from sections and summaries.

        Args:
            sections: All document sections in hierarchical order.
            section_summaries: Individual section summaries.
            document_title: Title of the document.
            detected_language: Detected language of the document.

        Returns:
            Complete DocumentKnowledge with document-level synthesis.
        """
        logger.info(f"Starting document synthesis for: {document_title}")

        # Start with existing section summaries
        all_summaries = dict(section_summaries)

        # Synthesize container sections (sections with children)
        container_summaries = await self._synthesize_container_sections(
            sections, all_summaries, detected_language
        )
        all_summaries.update(container_summaries)

        # Generate document-level summary (core map-reduce functionality)
        document_summary = await self._generate_document_summary(
            document_title, sections, all_summaries, detected_language
        )

        # TODO: Phase 2 - Create processing metadata
        # processing_metadata = {
        #     "total_sections": len(sections),
        #     "total_summaries": len(all_summaries),
        #     "synthesis_method": "hierarchical_bottom_up",
        #     "language": detected_language.value,
        #     "model_used": self.config.main_model or self.config.model_name,
        #     "dry_run": self.config.dry_run,
        # }

        logger.info(
            f"Document synthesis completed. Generated {len(all_summaries)} summaries."
        )

        # TODO: Phase 2 - Convert to CognitiveKnowledge format
        # For now, create a basic CognitiveKnowledge structure
        hierarchical_summaries = {s.section_id: s for s in all_summaries.values()}

        # Collect all unique concepts from sections and convert to ConceptDefinition objects
        all_concepts = set()
        concept_to_sections: dict[str, list[str]] = {}  # Track which sections mention each concept
        concept_first_mention = {}  # Track first mention of each concept

        for summary in all_summaries.values():
            for concept in summary.key_concepts:
                all_concepts.add(concept)
                # Track sections where this concept appears
                if concept not in concept_to_sections:
                    concept_to_sections[concept] = []
                    concept_first_mention[concept] = summary.section_id  # First mention
                concept_to_sections[concept].append(summary.section_id)

        # Convert unique concepts to ConceptDefinition objects with real definitions
        concept_definitions = []

        # Generate real definitions for concepts using LLM
        concept_definitions = await self._generate_concept_definitions(
            list(sorted(all_concepts)),
            all_summaries,
            concept_first_mention,
            concept_to_sections,
            detected_language
        )

        return CognitiveKnowledge(
            document_title=clean_section_title(document_title),
            document_summary=document_summary,
            detected_language=detected_language,
            hierarchical_summaries=hierarchical_summaries,
            concepts=concept_definitions,  # Now includes actual ConceptDefinition objects
            hierarchy_index={},  # TODO: Phase 2 - implement hierarchy index
            parent_child_map={},  # TODO: Phase 2 - implement parent-child mapping
            total_sections=len(sections),
            avg_summary_length=sum(len(s.summary) for s in all_summaries.values()) / max(len(all_summaries), 1),
            total_concepts=len(all_concepts),  # Count unique concepts from all sections
        )

    async def _synthesize_container_sections(
        self,
        sections: list[DocumentSection],
        existing_summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> dict[str, SectionSummary]:
        """Synthesize summaries for container sections based on their children.

        Args:
            sections: All document sections.
            existing_summaries: Already generated section summaries.
            language: Document language.

        Returns:
            Dictionary of new summaries for container sections.
        """
        container_summaries = {}

        # Find container sections (sections with children)
        container_sections = [s for s in sections if s.children_ids]

        # Sort by level (deepest first) to ensure children are processed before parents
        container_sections.sort(key=lambda s: s.level, reverse=True)

        async with LLMClient(self.config) as llm_client:
            for section in container_sections:
                if section.id not in existing_summaries:
                    summary = await self._synthesize_container_section(
                        section, sections, existing_summaries, language, llm_client
                    )
                    if summary:
                        container_summaries[section.id] = summary
                        # Add to existing summaries so parent sections can use it
                        existing_summaries[section.id] = summary

        return container_summaries

    async def _generate_concept_definitions(
        self,
        concepts: list[str],
        all_summaries: dict[str, SectionSummary],
        concept_first_mention: dict[str, str],
        concept_to_sections: dict[str, list[str]],
        language: LanguageCode
    ) -> list[ConceptDefinition]:
        """Generate real definitions for concepts using LLM.

        Args:
            concepts: List of unique concepts to define.
            all_summaries: All section summaries for context.
            concept_first_mention: First mention section for each concept.
            concept_to_sections: Sections where each concept appears.
            language: Document language.

        Returns:
            List of ConceptDefinition objects with real definitions.
        """
        from ..llm.client import LLMClient

        concept_definitions = []

        # Use LLM to generate real definitions
        async with LLMClient(self.config) as llm_client:
            for concept in concepts:
                try:
                    # Get context from sections where this concept appears
                    context_sections = []
                    for section_id in concept_to_sections[concept][:3]:  # Use first 3 sections for context
                        if section_id in all_summaries:
                            summary = all_summaries[section_id]
                            context_sections.append(f"{summary.title}: {summary.summary}")

                    context = "\n\n".join(context_sections)

                    # Generate definition using LLM
                    if self.config.dry_run or self.config.mock_responses:
                        # Use varied mock definitions for development
                        mock_definitions = {
                            # Core concepts
                            "processing": "The systematic handling, analysis, or transformation of data or information through defined procedures.",
                            "language": "A structured system of communication using words, symbols, or patterns to convey meaning.",
                            "detection": "The automated process of identifying, discovering, or recognizing specific elements or patterns.",
                            "architecture": "The fundamental structural design and organizational framework of a system or application.",
                            "components": "Modular parts or elements that work together to form a complete functional system.",
                            "flow": "The sequential movement, progression, or routing of data, processes, or information through a system.",
                            "output": "The final result, product, or information generated by a system or computational process.",
                            "structured": "Information or data organized in a systematic, standardized, or methodical format.",
                            "document": "A digital or written record containing structured information, content, or instructions.",
                            "example": "A representative sample or demonstration that illustrates a concept, process, or functionality.",
                            "automatic": "Processes or operations that execute independently without manual intervention.",
                            "generates": "The action of creating, producing, or outputting content, results, or data.",
                            "reader": "A software component or system designed to process, interpret, and extract information from documents.",
                            "cognitive": "Relating to mental processes of understanding, analysis, and knowledge extraction similar to human thinking.",
                            "introduction": "An opening section that provides context, overview, and foundational information about a topic.",
                            "conclusion": "A final section that summarizes findings, insights, and key takeaways from the analysis.",
                            "technical": "Relating to specialized knowledge, methods, or implementation details of a system or process.",
                            "core": "Essential, fundamental, or central elements that form the foundation of a system.",
                            "purpose": "The intended goal, objective, or reason for existence of a system, feature, or process.",
                            "features": "Distinct capabilities, functionalities, or characteristics provided by a system or application.",
                            "json": "JavaScript Object Notation - a lightweight, text-based data interchange format for structured information.",
                            "markdown": "A lightweight markup language used for formatting plain text documents with simple syntax.",
                            "integration": "The process of combining different systems, components, or data sources to work together seamlessly.",
                            "humans": "Human users who interact with, benefit from, or are the intended audience for system outputs."
                        }

                        # Smart matching for concept definitions
                        definition = None
                        concept_lower = concept.lower()

                        # Direct match
                        if concept_lower in mock_definitions:
                            definition = mock_definitions[concept_lower]
                        else:
                            # Try to find matching keywords within the concept
                            for key, def_text in mock_definitions.items():
                                if key in concept_lower:
                                    definition = def_text
                                    break

                        # Fallback to contextual definition
                        if not definition:
                            definition = f"A key concept in the document referring to {concept.replace('_', ' ').replace('concept ', '').strip()}."
                    else:
                        # Real LLM call for definition generation
                        definition_prompt = f"""Based on the following context from the document, provide a clear and concise definition for the concept "{concept}":

Context:
{context}

Provide only the definition (1-2 sentences maximum), focusing on how this concept is used in the document context."""

                        definition_response = await llm_client.generate_summary(
                            content=definition_prompt,
                            context="",
                            prompt_type="section_summary",
                            language=language,
                            section_title=f"Definition for {concept}"
                        )

                        # Extract definition from response and clean formatting
                        if definition_response:
                            # Remove "Summary: " prefix and other common prefixes
                            definition = definition_response.strip()
                            for prefix in ["Summary: ", "Definition: ", "Concept: ", "This section provides detailed information about "]:
                                if definition.startswith(prefix):
                                    definition = definition[len(prefix):].strip()
                            # Ensure first letter is capitalized
                            if definition:
                                definition = definition[0].upper() + definition[1:] if len(definition) > 1 else definition.upper()
                        else:
                            definition = f"Key concept: {concept}"

                    concept_definitions.append(ConceptDefinition(
                        concept_id=concept.lower().replace(" ", "_").replace(":", "").replace("-", "_"),
                        name=concept,
                        definition=definition,
                        first_mentioned_in=concept_first_mention[concept],
                        relevant_sections=concept_to_sections[concept][:5]  # Limit to first 5 sections
                    ))

                except Exception as e:
                    logger.warning(f"Failed to generate definition for concept '{concept}': {e}")
                    # Fallback to basic definition
                    concept_definitions.append(ConceptDefinition(
                        concept_id=concept.lower().replace(" ", "_").replace(":", "").replace("-", "_"),
                        name=concept,
                        definition=f"Key concept: {concept}",
                        first_mentioned_in=concept_first_mention[concept],
                        relevant_sections=concept_to_sections[concept][:5]
                    ))

        return concept_definitions

    async def _synthesize_container_section(
        self,
        section: DocumentSection,
        all_sections: list[DocumentSection],
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
        llm_client: LLMClient,
    ) -> SectionSummary | None:
        """Synthesize a summary for a container section from its children.

        Args:
            section: The container section to synthesize.
            all_sections: All document sections for reference.
            summaries: Existing section summaries.
            language: Document language.
            llm_client: LLM client for generation.

        Returns:
            SectionSummary for the container section, or None if synthesis fails.
        """
        # Get child summaries
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        if not child_summaries:
            logger.warning(
                f"No child summaries found for container section: {section.title}"
            )
            return None

        # Combine section's own content with child summaries (true hierarchical synthesis)
        content_parts = []

        # Add section's own content if it has any
        if section.content and section.content.strip():
            content_parts.append(f"Section content:\n{section.content}")

        # Add child summaries
        if child_summaries:
            content_parts.append("Subsection summaries:\n" + "\n\n".join(child_summaries))

        combined_content = "\n\n".join(content_parts)

        try:
            # Generate container summary from own content + children (hierarchical reduce)
            summary_text = await llm_client.generate_summary(
                content=combined_content,
                context="",  # Container sections don't need progressive context
                prompt_type="section_summary",
                language=language,
                section_title=section.title,
            )

            # Extract key concepts from children
            all_child_concepts = []
            for child_id in section.children_ids:
                if child_id in summaries:
                    all_child_concepts.extend(summaries[child_id].key_concepts)

            # Remove duplicates while preserving order
            unique_concepts = []
            seen = set()
            for concept in all_child_concepts:
                if concept not in seen:
                    unique_concepts.append(concept)
                    seen.add(concept)

            # Parse summary and concepts from response
            parsed_summary, parsed_concepts = self._parse_summary_response(summary_text)

            # Combine concepts from children with newly extracted ones
            final_concepts = unique_concepts[:3] + parsed_concepts[:2]  # Max 5 total
            final_concepts = final_concepts[:5]  # Ensure we don't exceed 5

            return SectionSummary(
                section_id=section.id,
                title=section.title,
                summary=parsed_summary,
                key_concepts=final_concepts,
                level=section.level,
                order_index=section.order_index,
                parent_id=section.parent_id,
                children_ids=section.children_ids,
            )

        except Exception as e:
            logger.error(f"Failed to synthesize container section {section.title}: {e}")
            return None

    async def _generate_document_summary(
        self,
        document_title: str,
        sections: list[DocumentSection],
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> str:
        """Generate document-level summary from section summaries.

        Args:
            document_title: Title of the document.
            sections: All document sections.
            summaries: All section summaries.
            language: Document language.

        Returns:
            Document-level summary text.
        """
        # Get top-level section summaries for document synthesis
        top_level_sections = [s for s in sections if s.level == 1]
        top_level_summaries = []

        for section in top_level_sections:
            if section.id in summaries:
                summary = summaries[section.id]
                top_level_summaries.append(f"{summary.title}: {summary.summary}")

        if not top_level_summaries:
            logger.warning("No top-level summaries found for document synthesis")
            return f"Summary of {document_title}: Document analysis completed with {len(sections)} sections processed."

        # Combine summaries for document-level synthesis
        combined_summaries = "\n\n".join(top_level_summaries)

        try:
            async with LLMClient(self.config) as llm_client:
                summary_response = await llm_client.generate_summary(
                    content=combined_summaries,
                    context="",
                    prompt_type="document_summary",
                    language=language,
                    section_title=document_title,
                )

                # Extract just the summary part
                document_summary, _ = self._parse_summary_response(summary_response)
                return document_summary

        except Exception as e:
            logger.error(f"Failed to generate document summary: {e}")
            # Fallback summary
            return f"Summary of {document_title}: This document contains {len(sections)} sections covering various topics. The content has been analyzed and structured for cognitive understanding."

    def _parse_summary_response(self, response: str) -> tuple[str, list[str]]:
        """Parse summary and concepts from LLM response.

        Args:
            response: Raw response from LLM.

        Returns:
            Tuple of (summary_text, key_concepts_list).
        """
        lines = response.strip().split("\n")
        summary = ""
        concepts = []

        for line in lines:
            line = line.strip()
            if line.startswith(
                ("Summary:", "Resumen:", "Document Summary:", "Resumen del Documento:")
            ):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith(("Key Concepts:", "Conceptos Clave:")):
                concepts_text = line.split(":", 1)[1].strip()
                # Parse comma-separated concepts, removing brackets
                concepts_text = concepts_text.strip("[]")
                if concepts_text:
                    concepts = [
                        concept.strip().strip("'\"")
                        for concept in concepts_text.split(",")
                        if concept.strip()
                    ]

        # If no structured format found, use the whole response as summary
        if not summary:
            summary = response.strip()

        return summary, concepts[:5]  # Limit to 5 concepts
