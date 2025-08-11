"""Hierarchical synthesis engine for document knowledge."""

from __future__ import annotations

import logging

from ..llm.client import LLMClient
from ..models.config import CognitiveConfig
from ..models.document import CognitiveKnowledge, DocumentSection, SectionSummary
from ..models.knowledge import LanguageCode
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

        # TODO: Phase 2 - Generate document-level summary
        # document_summary = await self._generate_document_summary(
        #     document_title, sections, all_summaries, detected_language
        # )

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

        # Collect all unique concepts from sections (MVP: basic concept counting)
        all_concepts = set()
        for summary in all_summaries.values():
            all_concepts.update(summary.key_concepts)

        return CognitiveKnowledge(
            document_title=clean_section_title(document_title),
            detected_language=detected_language,
            hierarchical_summaries=hierarchical_summaries,
            concepts=[],  # TODO: Phase 2 - convert concepts to ConceptDefinition objects
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

        # Combine child summaries for synthesis
        combined_content = "\n\n".join(child_summaries)

        try:
            # Generate container summary from children
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
