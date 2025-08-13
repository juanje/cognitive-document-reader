"""Progressive reading engine - main cognitive document reader."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..llm.client import LLMClient
from ..models.config import CognitiveConfig
from ..models.document import CognitiveKnowledge, DocumentSection, SectionSummary
from ..models.knowledge import LanguageCode
from ..parsers.docling_parser import DoclingParser
from ..utils.language import LanguageDetector
from .synthesizer import Synthesizer

logger = logging.getLogger(__name__)


class CognitiveReader:
    """Main cognitive document reader with progressive understanding.

    Simulates human-like document reading through progressive understanding
    and hierarchical synthesis. The core component that orchestrates the
    entire cognitive reading process.
    """

    def __init__(self, config: CognitiveConfig | None = None) -> None:
        """Initialize the cognitive reader.

        Args:
            config: Reading configuration. If None, will load from environment.
        """
        self.config = config or CognitiveConfig.from_env()
        self.parser = DoclingParser()
        self.synthesizer = Synthesizer(
            self.config, save_partial_result_fn=self._save_partial_result
        )
        self.language_detector = LanguageDetector()

        # Log the actual processing strategy being used
        if self.config.enable_second_pass:
            logger.info(
                f"CognitiveReader initialized with dual-pass: fast={self.config.fast_pass_model}, main={self.config.main_model}"
            )
        else:
            # Single-pass: only fast first pass enabled
            active_model = self.config.fast_pass_model or self.config.model_name
            logger.info(
                f"CognitiveReader initialized with single-pass (fast model): {active_model}"
            )

        if self.config.is_development_mode():
            logger.info("Development mode enabled - no real LLM calls will be made")

    async def read_document(self, file_path: str | Path) -> CognitiveKnowledge:
        """Read and analyze a document file with cognitive understanding.

        Args:
            file_path: Path to the document file to read.

        Returns:
            Complete CognitiveKnowledge with analysis and summaries.

        Raises:
            FileNotFoundError: If the document file doesn't exist.
            ValueError: If the document format is not supported or parsing fails.
        """
        file_path = Path(file_path)
        logger.info(f"Starting cognitive reading of: {file_path}")

        # Validate configuration if requested
        if self.config.validate_config_only:
            is_valid = await self.validate_configuration()
            if is_valid:
                logger.info("Configuration validation successful")
                # Return empty knowledge for validation-only mode
                return CognitiveKnowledge(
                    document_title="Configuration Validation",
                    document_summary="Configuration validation completed successfully.",
                    detected_language=LanguageCode.EN,
                    hierarchical_summaries={},
                    concepts=[],
                    hierarchy_index={},
                    parent_child_map={},
                    total_sections=0,
                    avg_summary_length=0,
                    total_concepts=0,
                )
            else:
                raise ValueError("Configuration validation failed")

        # Parse document structure
        document_title, sections = await self.parser.parse_document(file_path)

        if not sections:
            logger.warning(f"No sections found in document: {file_path}")
            return CognitiveKnowledge(
                document_title=document_title,
                document_summary=f"Empty document: {document_title}. No content sections were found for processing.",
                detected_language=LanguageCode.EN,
                hierarchical_summaries={},
                concepts=[],
                hierarchy_index={},
                parent_child_map={},
                total_sections=0,
                avg_summary_length=0,
                total_concepts=0,
            )

        # Detect document language
        detected_language = self._detect_document_language(sections)

        # Perform progressive reading
        section_summaries = await self._progressive_reading(sections, detected_language)

        # Synthesize complete knowledge
        knowledge = await self.synthesizer.synthesize_document(
            sections=sections,
            section_summaries=section_summaries,
            document_title=document_title,
            detected_language=detected_language,
        )

        logger.info(
            f"Cognitive reading completed: {len(sections)} sections, {len(section_summaries)} summaries"
        )
        return knowledge

    async def read_document_text(
        self, text: str, title: str = "Untitled Document"
    ) -> CognitiveKnowledge:
        """Read and analyze text content directly with cognitive understanding.

        Args:
            text: Raw text content to analyze.
            title: Title for the document.

        Returns:
            Complete CognitiveKnowledge with analysis and summaries.
        """
        logger.info(f"Starting cognitive reading of text: {title}")

        # Validate configuration if requested
        if self.config.validate_config_only:
            is_valid = await self.validate_configuration()
            if is_valid:
                logger.info("Configuration validation successful")
                return CognitiveKnowledge(
                    document_title="Configuration Validation",
                    document_summary="Text configuration validation completed successfully.",
                    detected_language=LanguageCode.EN,
                    hierarchical_summaries={},
                    concepts=[],
                    hierarchy_index={},
                    parent_child_map={},
                    total_sections=0,
                    avg_summary_length=0,
                    total_concepts=0,
                )
            else:
                raise ValueError("Configuration validation failed")

        # Parse text content
        document_title, sections = await self.parser.parse_text(text, title)

        if not sections:
            logger.warning("No sections found in text content")
            return CognitiveKnowledge(
                document_title=document_title,
                document_summary=f"Empty text content: {document_title}. No sections were identified for processing.",
                detected_language=LanguageCode.EN,
                hierarchical_summaries={},
                concepts=[],
                hierarchy_index={},
                parent_child_map={},
                total_sections=0,
                avg_summary_length=0,
                total_concepts=0,
            )

        # Detect document language
        detected_language = self._detect_document_language(sections)

        # Perform progressive reading
        section_summaries = await self._progressive_reading(sections, detected_language)

        # Synthesize complete knowledge
        knowledge = await self.synthesizer.synthesize_document(
            sections=sections,
            section_summaries=section_summaries,
            document_title=document_title,
            detected_language=detected_language,
        )

        logger.info(
            f"Text cognitive reading completed: {len(sections)} sections, {len(section_summaries)} summaries"
        )
        return knowledge

    async def _progressive_reading(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Perform hierarchical bottom-up processing of document sections.

        Implements the algorithm defined in SPECS v2.0:
        1. Organize sections by hierarchy level
        2. Process from deepest level to root (bottom-up)
        3. For leaf sections: use section.content
        4. For container sections: combine section.content + child_summaries

        Args:
            sections: Document sections to process.
            language: Detected document language.

        Returns:
            Dictionary of section summaries for all sections.
        """
        logger.info(f"Starting hierarchical processing of {len(sections)} sections")

        # Sort sections by order_index to maintain document flow
        ordered_sections = sorted(sections, key=lambda s: s.order_index)

        # Apply development filters if configured
        filtered_sections = self._apply_section_filters(ordered_sections)

        logger.info(
            f"Processing {len(filtered_sections)} sections using hierarchical algorithm"
        )

        # Use hierarchical bottom-up processing instead of sequential
        return await self._hierarchical_processing(filtered_sections, language)

    # TODO: Phase 2 - Implement proper dual-pass with hierarchical order and specialized prompts

    async def _single_pass_reading(
        self,
        content_sections: list[DocumentSection],
        language: LanguageCode,
        pass_name: str = "single_pass",
        model: str | None = None,
        temperature: float | None = None,
        previous_summaries: dict[str, SectionSummary] | None = None,
    ) -> dict[str, SectionSummary]:
        """Perform single-pass reading with specified model.

        Args:
            content_sections: Content sections to process.
            language: Detected document language.
            pass_name: Name of this pass for logging.
            model: Optional model to use.
            temperature: Optional temperature to use.
            previous_summaries: Previous summaries for context (refinement pass).

        Returns:
            Dictionary of section summaries.
        """
        section_summaries = {}
        accumulated_context = ""

        # Log which model we're using
        effective_model: str
        if model:
            effective_model = model
        elif self.config.enable_fast_first_pass:
            # Dual-pass: determine model based on pass name
            if "fast" in pass_name.lower():
                effective_model = self.config.fast_pass_model or "llama3.1:8b"
            else:
                effective_model = self.config.main_model or "qwen3:8b"
        else:
            # Single-pass: use fast model for efficiency
            effective_model = self.config.fast_pass_model or self.config.model_name

        logger.info(f"{pass_name.title()}: Using model '{effective_model}'")

        async with LLMClient(self.config) as llm_client:
            for i, section in enumerate(content_sections):
                logger.debug(
                    f"[{pass_name}] Processing section {i + 1}/{len(content_sections)}: {section.title}"
                )

                # For refinement pass, include previous summary as context
                section_context = accumulated_context
                if previous_summaries and section.id in previous_summaries:
                    prev_summary = previous_summaries[section.id]
                    section_context += f"\n\nPREVIOUS SUMMARY: {prev_summary.summary}"

                # Generate section summary with accumulated context
                summary = await self._process_section(
                    section,
                    section_context,
                    language,
                    llm_client,
                    model=effective_model,
                    temperature=temperature,
                )

                if summary:
                    section_summaries[section.id] = summary

                    # Update accumulated context for next sections
                    accumulated_context = self._update_accumulated_context(
                        accumulated_context, summary
                    )

                    logger.debug(f"[{pass_name}] Section processed: {section.title}")
                else:
                    logger.warning(
                        f"[{pass_name}] Failed to process section: {section.title}"
                    )

        logger.info(
            f"{pass_name.title()} completed: {len(section_summaries)} summaries generated"
        )
        return section_summaries

    async def _process_section(
        self,
        section: DocumentSection,
        accumulated_context: str,
        language: LanguageCode,
        llm_client: LLMClient,
        model: str | None = None,
        temperature: float | None = None,
        content: str | None = None,
    ) -> SectionSummary | None:
        """Process a single section to generate its summary.

        Args:
            section: The section to process.
            accumulated_context: Context from previously processed sections.
            language: Document language.
            llm_client: LLM client for generation.
            model: Optional model to use (overrides config).
            temperature: Optional temperature to use (overrides config).
            content: Optional content to use (overrides section.content for hierarchical processing).

        Returns:
            SectionSummary for the section, or None if processing fails.
        """
        try:
            # Use provided content or fall back to section.content
            effective_content = content or section.content

            # Generate structured summary using LLM - combines summary and key concepts in one call
            structured_response = await llm_client.generate_structured_summary(
                content=effective_content,
                context=accumulated_context,
                section_title=section.title,
                language=language,
                model=model,
                temperature=temperature,
            )

            # Extract structured data - no parsing needed!
            summary_text = structured_response.summary
            unique_concepts = structured_response.key_concepts[:5]  # Already limited in model

            return SectionSummary(
                section_id=section.id,
                title=section.title,
                summary=summary_text,
                key_concepts=unique_concepts[:5],  # Limit to 5 concepts
                level=section.level,
                order_index=section.order_index,
                parent_id=section.parent_id,
                children_ids=section.children_ids,
            )

        except Exception as e:
            logger.error(f"Failed to process section {section.title}: {e}")
            return None

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
            if line.startswith(("Summary:", "Resumen:")):
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

    def _update_accumulated_context(
        self, current_context: str, new_summary: SectionSummary
    ) -> str:
        """Update accumulated context with new section summary.

        Args:
            current_context: Current accumulated context.
            new_summary: New section summary to add.

        Returns:
            Updated accumulated context.
        """
        # Add new summary to context
        new_context_entry = f"{new_summary.title}: {new_summary.summary}"

        if not current_context:
            return new_context_entry

        # Combine with existing context, managing length
        combined_context = f"{current_context}\n\n{new_context_entry}"

        # If context gets too long, truncate from the beginning
        max_context_length = self.config.context_window // 2  # Use half for context
        if len(combined_context) > max_context_length:
            # Keep the most recent context that fits
            lines = combined_context.split("\n\n")
            truncated_context = ""
            for line in reversed(lines):
                test_context = (
                    f"{line}\n\n{truncated_context}" if truncated_context else line
                )
                if len(test_context) <= max_context_length:
                    truncated_context = test_context
                else:
                    break
            combined_context = truncated_context

        return combined_context

    async def _hierarchical_processing(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Process sections using hybrid top-down + bottom-up algorithm.

        Implements the correct parent-first context flow:
        1. Parent WITHOUT content + children: Standard bottom-up processing
        2. Parent WITH content + children: Hybrid processing:
           - TOP-DOWN: Process parent text first → parent_summary
           - CONTEXTUAL: Children receive parent_summary as context
           - BOTTOM-UP: Final parent summary = synthesis(parent_summary + children_summaries)

        Args:
            sections: Document sections to process.
            language: Detected document language.

        Returns:
            Dictionary of section summaries for all sections.
        """
        # Step 1: Build section hierarchy
        levels = self._organize_by_level(sections)
        max_level = max(levels.keys()) if levels else 0

        logger.info(
            f"Hierarchical structure: {len(levels)} levels (max depth: {max_level})"
        )
        for level, level_sections in levels.items():
            section_titles = [s.title for s in level_sections]
            logger.info(
                f"  Level {level}: {len(level_sections)} sections - {section_titles}"
            )

        processing_model = self.config.fast_pass_model or self.config.model_name
        logger.info(
            f"🧠 Processing document with hybrid algorithm, model: {processing_model}"
        )

        # Step 2: Identify parents with content for hybrid processing
        parents_with_content = []
        for level_sections in levels.values():
            for section in level_sections:
                if section.children_ids and section.content and section.content.strip():
                    parents_with_content.append(section)

        logger.info(
            f"🔄 Found {len(parents_with_content)} parents with content for hybrid processing"
        )

        # Step 3: Process using two-pass hybrid approach
        summaries: dict[str, SectionSummary] = {}
        parent_contexts: dict[str, str] = {}  # Store parent summaries for context

        # PASS 1: Process parent texts to generate contexts (top-down)
        for parent in parents_with_content:
            logger.info(f"🔄 PASS 1: Processing parent text for '{parent.title}'")
            parent_summary = await self._process_section_single_pass(
                section=parent, content=parent.content, language=language
            )
            if parent_summary:
                parent_contexts[parent.id] = parent_summary.summary
                # Store temporary summary - will be replaced by final synthesis
                summaries[parent.id] = parent_summary
                logger.debug(f"Generated parent context for '{parent.title}' children")

        # PASS 2: Process all sections with available contexts (hybrid bottom-up)
        for level in range(max_level, 0, -1):
            if level not in levels:
                continue

            level_sections = levels[level]
            logger.info(
                f"🔄 PASS 2: Processing level {level}: {len(level_sections)} sections"
            )

            for section in level_sections:
                if section.children_ids:  # Container section
                    has_own_content = section.content and section.content.strip()

                    if has_own_content:
                        # Case 2: Final synthesis for parent with content
                        summary = await self._synthesize_hybrid_parent_final(
                            section, summaries, parent_contexts, language
                        )
                    else:
                        # Case 1: Standard bottom-up for parent without content
                        summary = await self._process_container_children_only(
                            section, summaries, language
                        )
                else:  # Leaf section
                    summary = await self._process_leaf_section(
                        section, parent_contexts, language
                    )

                if summary:
                    summaries[section.id] = summary
                    logger.info(f"✅ Processed '{section.title}' (level {level})")
                    await self._save_partial_result_if_enabled(
                        section, summary, len(summaries)
                    )
                else:
                    logger.warning(
                        f"❌ Failed to process '{section.title}' (level {level})"
                    )

        logger.info(f"Hybrid processing completed: {len(summaries)} sections processed")
        return summaries

    def _organize_by_level(
        self, sections: list[DocumentSection]
    ) -> dict[int, list[DocumentSection]]:
        """Organize sections by hierarchy level.

        Args:
            sections: Document sections to organize.

        Returns:
            Dictionary mapping level to list of sections at that level.
        """
        levels: dict[int, list[DocumentSection]] = {}

        for section in sections:
            level = section.level
            if level not in levels:
                levels[level] = []
            levels[level].append(section)

        # Sort sections within each level by order_index
        for level_sections in levels.values():
            level_sections.sort(key=lambda s: s.order_index)

        return levels

    async def _synthesize_hybrid_parent_final(
        self,
        section: DocumentSection,
        summaries: dict[str, SectionSummary],
        parent_contexts: dict[str, str],
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Final synthesis for parent with content (PASS 2 of hybrid algorithm).

        Combines the parent summary from PASS 1 with children summaries processed
        with parent context in PASS 2.

        Args:
            section: Parent section with content and children.
            summaries: Section summaries (includes parent from PASS 1 and children from PASS 2).
            parent_contexts: Parent contexts generated in PASS 1.
            language: Document language.

        Returns:
            Final synthesized summary combining parent + children.
        """
        # Get parent summary from PASS 1
        if section.id not in summaries:
            logger.error(
                f"Parent summary not found for '{section.title}' - PASS 1 may have failed"
            )
            return None

        parent_summary = summaries[section.id]

        # Collect children summaries (processed in PASS 2 with parent context)
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        # Final synthesis: parent_summary + children_summaries
        if child_summaries:
            synthesis_content = f"""Parent section summary:
{parent_summary.summary}

Subsection summaries:
{chr(10).join(child_summaries)}"""
            logger.info(
                f"🔀 FINAL SYNTHESIS: '{section.title}' parent + {len(child_summaries)} children"
            )
        else:
            # Fallback: only parent content if no children processed
            logger.warning(
                f"No children found for parent '{section.title}' - using parent summary only"
            )
            return parent_summary

        # Generate final synthesized summary
        final_summary = await self._process_section_single_pass(
            section=section, content=synthesis_content, language=language
        )

        return final_summary

    async def _process_container_children_only(
        self,
        section: DocumentSection,
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Process container with children only (no own content).

        Case 1: Parent WITHOUT content + children (standard bottom-up)

        Args:
            section: Container section without own content.
            summaries: Existing section summaries (children already processed).
            language: Document language.

        Returns:
            Section summary from children summaries only.
        """
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        if not child_summaries:
            logger.warning(f"No child summaries found for container: {section.title}")
            return None

        content = "Subsection summaries:\n" + "\n\n".join(child_summaries)
        logger.debug(
            f"Container '{section.title}': synthesizing {len(child_summaries)} children only"
        )

        return await self._process_section_single_pass(section, content, language)

    async def _process_leaf_section(
        self,
        section: DocumentSection,
        parent_contexts: dict[str, str],
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Process leaf section with optional parent context.

        Args:
            section: Leaf section to process.
            parent_contexts: Available parent contexts for enhanced processing.
            language: Document language.

        Returns:
            Section summary (potentially enhanced with parent context).
        """
        content = section.content

        # Check if this section has a parent with context available
        if section.parent_id and section.parent_id in parent_contexts:
            parent_context = parent_contexts[section.parent_id]
            enhanced_content = f"""Parent context:
{parent_context}

Section content:
{content}"""
            logger.debug(f"Leaf '{section.title}': processing with parent context")
            content = enhanced_content
        else:
            logger.debug(f"Leaf '{section.title}': processing without parent context")

        return await self._process_section_single_pass(section, content, language)

    async def _save_partial_result_if_enabled(
        self, section: DocumentSection, summary: SectionSummary, total_sections: int
    ) -> None:
        """Save partial result if enabled."""
        if hasattr(self, "_save_partial_result"):
            await self._save_partial_result(
                section_index=section.order_index,
                total_sections=total_sections,
                section=section,
                summary=summary,
                accumulated_context="Hybrid hierarchical processing",
            )

    def _combine_children_summaries_only(
        self, section: DocumentSection, summaries: dict[str, SectionSummary]
    ) -> str:
        """Combine only child summaries (for parents without own content).

        Args:
            section: Container section to process.
            summaries: Existing section summaries.

        Returns:
            Combined child summaries for LLM processing.
        """
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        if child_summaries:
            return "Subsection summaries:\n" + "\n\n".join(child_summaries)
        else:
            return ""

    async def _process_container_with_parent_text(
        self,
        section: DocumentSection,
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Process container section with parent text as introductory context.

        Case 2: Parent WITH content + children
        1. Process parent content first (as "section 0")
        2. Children are already processed (bottom-up)
        3. Synthesize parent summary + children summaries into final summary

        Args:
            section: Container section with both content and children.
            summaries: Existing section summaries (children are already processed).
            language: Document language.

        Returns:
            Final section summary combining parent + children.
        """
        # Step 1: Process parent's own content first (as introductory context)
        logger.debug(
            f"Processing parent text for '{section.title}' as introductory context"
        )
        parent_summary = await self._process_section_single_pass(
            section=section, content=section.content, language=language
        )

        if not parent_summary:
            logger.warning(f"Failed to process parent content for '{section.title}'")
            return None

        # Step 2: Collect child summaries (already processed in bottom-up)
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        # Step 3: Synthesize parent summary + child summaries
        if child_summaries:
            synthesis_content = f"""Parent section summary:
{parent_summary.summary}

Subsection summaries:
{chr(10).join(child_summaries)}"""
        else:
            # Fallback: only parent content
            synthesis_content = parent_summary.summary

        # Generate final synthesis summary
        logger.debug(
            f"Synthesizing parent summary + {len(section.children_ids)} children summaries for '{section.title}'"
        )
        final_summary = await self._process_section_single_pass(
            section=section, content=synthesis_content, language=language
        )

        return final_summary

    # TODO: Phase 2 - Implement proper dual-pass with specialized prompts and context

    async def _process_section_single_pass(
        self, section: DocumentSection, content: str, language: LanguageCode
    ) -> SectionSummary | None:
        """Process a section using single-pass approach.

        Args:
            section: Section to process.
            content: Content to summarize.
            language: Document language.

        Returns:
            Section summary from single-pass processing.
        """
        # For single-pass, use fast model (optimized for speed/cost)
        model = self.config.fast_pass_model or self.config.model_name
        temperature = self.config.fast_pass_temperature or self.config.temperature

        async with LLMClient(self.config) as llm_client:
            return await self._process_section(
                section,
                "",  # No accumulated context for hierarchical processing
                language,
                llm_client,
                model=model,
                temperature=temperature,
                content=content,
            )

    def _apply_section_filters(
        self, sections: list[DocumentSection]
    ) -> list[DocumentSection]:
        """Apply development filters to sections for testing and debugging.

        Args:
            sections: Ordered list of document sections.

        Returns:
            Filtered list of sections based on configuration.
        """
        filtered_sections = sections

        # Apply depth filter if configured
        if (
            self.config.max_hierarchy_depth is not None
            and self.config.max_hierarchy_depth < 10
        ):  # Avoid filtering default high values
            original_count = len(filtered_sections)
            filtered_sections = self._filter_by_depth(
                filtered_sections, self.config.max_hierarchy_depth
            )
            if len(filtered_sections) < original_count:
                logger.info(
                    f"🔧 Depth filter applied (max depth: {self.config.max_hierarchy_depth}): "
                    f"{original_count} -> {len(filtered_sections)} sections"
                )

        # Apply section count limit if configured
        if self.config.max_sections is not None:
            original_count = len(filtered_sections)
            filtered_sections = filtered_sections[: self.config.max_sections]
            if len(filtered_sections) < original_count:
                logger.info(
                    f"🔧 Section count limit applied (max: {self.config.max_sections}): "
                    f"{original_count} -> {len(filtered_sections)} sections"
                )

        return filtered_sections

    def _filter_by_depth(
        self, sections: list[DocumentSection], max_depth: int
    ) -> list[DocumentSection]:
        """Filter sections by maximum depth level.

        Args:
            sections: List of document sections.
            max_depth: Maximum depth level to include (0-based).

        Returns:
            Filtered list of sections within the depth limit.
        """
        return [section for section in sections if section.level <= max_depth]

    # TODO: Phase 2 - Re-implement save partial results functionality
    async def _save_partial_result(
        self,
        section_index: int,
        total_sections: int,
        section: DocumentSection | None = None,
        summary: SectionSummary | None = None,
        accumulated_context: str = "",
        section_type: str = "section",
        content: str = "",
        processing_stage: str = "section_processing",
        concepts: list[Any] | None = None,
    ) -> None:
        """Save partial processing result for debugging and evaluation."""
        if not self.config.save_partial_results:
            return
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(self.config.partial_results_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create partial result data based on type
            partial_result = {
                "progress": {
                    "section_index": section_index,
                    "total_sections": total_sections,
                    "progress_percentage": round(
                        (section_index / total_sections) * 100, 1
                    ),
                },
                "type": section_type,
                "processing_stage": processing_stage,
                "config": {
                    "model_used": self.config.fast_pass_model or self.config.model_name,
                    "enable_fast_first_pass": self.config.enable_fast_first_pass,
                    "temperature": self.config.temperature,
                },
            }

            # Add type-specific data
            if section_type == "section" and section and summary:
                # Traditional section processing
                partial_result["section"] = {
                    "id": section.id,
                    "title": section.title,
                    "level": section.level,
                    "order_index": section.order_index,
                    "content_preview": section.content[:300] + "..."
                    if len(section.content) > 300
                    else section.content,
                }
                partial_result["summary"] = {
                    "title": summary.title,
                    "summary": summary.summary,
                    "key_concepts": summary.key_concepts,
                    "level": summary.level,
                    "order_index": summary.order_index,
                }
                partial_result["context"] = {
                    "accumulated_context_length": len(accumulated_context),
                    "accumulated_context_preview": accumulated_context[:200] + "..."
                    if len(accumulated_context) > 200
                    else accumulated_context,
                }
            elif section_type == "document_summary":
                # Document summary generation
                partial_result["document_summary"] = {
                    "content": content,
                    "length": len(content),
                }
            elif section_type == "concept_definitions":
                # Concept definitions generation - include full definitions for debugging
                concept_details = []
                if concepts:
                    for concept in concepts:
                        concept_details.append(
                            {
                                "concept_id": concept.concept_id,
                                "name": concept.name,
                                "definition": concept.definition,
                                "first_mentioned_in": concept.first_mentioned_in,
                                "relevant_sections": concept.relevant_sections,
                            }
                        )

                partial_result["concept_definitions"] = {
                    "count": len(concepts) if concepts else 0,
                    "description": content,
                    "concepts_preview": [
                        c.concept_id for c in (concepts[:5] if concepts else [])
                    ],
                    "full_definitions": concept_details,  # Complete definitions for debugging
                }

            # Save to JSON file with zero-padded numbering
            filename = f"partial_{section_index:03d}_of_{total_sections:03d}.json"
            output_file = output_dir / filename

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(partial_result, f, indent=2, ensure_ascii=False)

            logger.debug(f"Partial result saved: {output_file}")

        except Exception as e:
            # Don't fail the main process if partial saving fails
            logger.warning(
                f"Failed to save partial result for {section_type} {section_index}: {e}"
            )

    def _detect_document_language(
        self, sections: list[DocumentSection]
    ) -> LanguageCode:
        """Detect the primary language of the document.

        Args:
            sections: Document sections to analyze.

        Returns:
            Detected language code.
        """
        if self.config.document_language != LanguageCode.AUTO:
            return self.config.document_language

        # Combine content from first few sections for detection
        sample_text = ""
        for section in sections[:3]:  # Use first 3 sections
            sample_text += f" {section.content}"
            if len(sample_text) > 1000:  # Enough text for reliable detection
                break

        detected = self.language_detector.detect_language(sample_text)
        logger.info(f"Detected document language: {detected}")
        return detected

    async def validate_configuration(self) -> bool:
        """Validate the complete configuration and dependencies.

        Returns:
            True if configuration is valid and ready for processing.
        """
        logger.info("Validating cognitive reader configuration...")

        try:
            # Validate LLM configuration
            async with LLMClient(self.config) as llm_client:
                llm_valid = await llm_client.validate_configuration()

            if not llm_valid:
                logger.error("LLM configuration validation failed")
                return False

            # Validate parser configuration
            supported_formats = self.parser.get_supported_formats()
            if not supported_formats:
                logger.error("No supported document formats available")
                return False

            logger.info(f"Configuration valid. Supported formats: {supported_formats}")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available.

        Returns:
            True if all dependencies are properly installed and accessible.
        """
        try:
            # Check if required modules can be imported
            import aiohttp  # noqa: F401
            import langdetect  # noqa: F401
            import pydantic  # noqa: F401

            logger.info("All dependencies are available")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
