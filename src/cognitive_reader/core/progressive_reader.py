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
                f"CognitiveReader initialized with multi-pass models: fast={self.config.fast_pass_model}, main={self.config.main_model}"
            )
        else:
            # Single model: use fast model for all passes
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
            f"Processing {len(filtered_sections)} sections using sequential algorithm"
        )

        # Use sequential processing with cumulative context (SPECS v2.0)
        return await self._sequential_processing(filtered_sections, language)

    # TODO: Phase 2 - Implement second pass with enriched context (summaries + glossary)

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
            unique_concepts = structured_response.key_concepts[
                :5
            ]  # Already limited in model

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

    async def _sequential_processing(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Process sections using sequential algorithm with cumulative context.

        Implements the authentic sequential reading process from SPECS v2.0:
        1. Process sections in document order (natural reading flow)
        2. Build cumulative context (parents + previous siblings) for each section
        3. Apply text source authority principle (text > context)
        4. Update parent levels incrementally as children are processed
        5. Handle deferred synthesis for parents without own content

        Args:
            sections: Document sections to process.
            language: Detected document language.

        Returns:
            Dictionary of section summaries for all sections.
        """
        # Step 1: Store sections for context building and order in document sequence
        self.sections_cache = sections  # Store for context building methods
        ordered_sections = self._order_by_document_sequence(sections)

        logger.info(
            f"📖 Sequential processing: {len(ordered_sections)} sections in document order"
        )
        for i, section in enumerate(ordered_sections[:5]):  # Show first 5 for brevity
            logger.info(f"  {i + 1}. '{section.title}' (level {section.level})")
        if len(ordered_sections) > 5:
            logger.info(f"  ... and {len(ordered_sections) - 5} more sections")

        processing_model = self.config.fast_pass_model or self.config.model_name
        logger.info(
            f"🧠 Processing document with sequential algorithm, model: {processing_model}"
        )

        # Step 2: Process sections sequentially with cumulative context
        summaries: dict[str, SectionSummary] = {}
        pending_parents: dict[
            str, DocumentSection
        ] = {}  # Parents without content waiting for children

        for section in ordered_sections:
            logger.debug(
                f"📖 Processing section '{section.title}' (level {section.level})"
            )

            # Build cumulative context (parents + previous siblings)
            cumulative_context = self._build_cumulative_context(section, summaries)

            if section.children_ids and (
                not section.content or not section.content.strip()
            ):
                # Parent WITHOUT content: defer synthesis until all children processed
                logger.debug(
                    f"⏳ Deferring synthesis for parent without content: '{section.title}'"
                )
                pending_parents[section.id] = section
                continue

            # Process section with cumulative context and text authority principle
            summary = await self._process_section_with_authority(
                section=section,
                cumulative_context=cumulative_context,
                language=language,
            )

            if summary:
                summaries[section.id] = summary
                logger.info(f"✅ Processed '{section.title}' (level {section.level})")

                # Step 3: Update parent levels incrementally
                await self._update_parent_levels_incrementally(
                    section, summary, summaries, language
                )

                # Step 4: Check if any pending parents can now be synthesized
                await self._process_pending_parents(
                    section, pending_parents, summaries, language
                )

                # Save partial result
                await self._save_partial_result_if_enabled(
                    section, summary, len(summaries)
                )
            else:
                logger.warning(
                    f"❌ Failed to process '{section.title}' (level {section.level})"
                )

        # Step 5: Process any remaining pending parents
        await self._finalize_pending_parents(pending_parents, summaries, language)

        logger.info(
            f"Sequential processing completed: {len(summaries)} sections processed"
        )
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

    def _order_by_document_sequence(
        self, sections: list[DocumentSection]
    ) -> list[DocumentSection]:
        """Order sections in document sequence (natural reading flow).

        This implements the core sequential processing requirement from SPECS v2.0:
        sections are processed in the order they appear in the document, not by hierarchy level.

        Args:
            sections: Document sections to order.

        Returns:
            List of sections ordered by document sequence (order_index).
        """
        # Sort by order_index which represents the natural document order
        ordered_sections = sorted(sections, key=lambda s: s.order_index)

        logger.debug(
            f"📖 Ordered {len(ordered_sections)} sections by document sequence"
        )
        return ordered_sections

    def _build_cumulative_context(
        self, section: DocumentSection, summaries: dict[str, SectionSummary]
    ) -> str:
        """Build cumulative context for a section (parents + previous siblings).

        Implements the cumulative context requirement from SPECS v2.0:
        each section receives context from all parents + previous siblings.

        Args:
            section: Section to build context for.
            summaries: Existing section summaries.

        Returns:
            Cumulative context string for the section.
        """
        context_parts = []

        # 1. Parent contexts (all levels up the hierarchy)
        parent_contexts = self._get_parent_contexts(section, summaries)
        if parent_contexts:
            context_parts.append("PARENT CONTEXT:\n" + "\n\n".join(parent_contexts))

        # 2. Previous sibling contexts (same level, processed before this section)
        sibling_contexts = self._get_previous_sibling_contexts(section, summaries)
        if sibling_contexts:
            context_parts.append("PREVIOUS SIBLINGS:\n" + "\n\n".join(sibling_contexts))

        # Combine all context parts
        cumulative_context = "\n\n".join(context_parts) if context_parts else ""

        if cumulative_context:
            logger.debug(
                f"📖 Built cumulative context for '{section.title}': {len(context_parts)} context parts"
            )

        return cumulative_context

    def _get_parent_contexts(
        self, section: DocumentSection, summaries: dict[str, SectionSummary]
    ) -> list[str]:
        """Get contexts from all parent levels."""
        parent_contexts = []

        # Traverse up the parent hierarchy
        current_parent_id = section.parent_id
        while current_parent_id and current_parent_id in summaries:
            parent_summary = summaries[current_parent_id]
            parent_contexts.append(f"{parent_summary.title}: {parent_summary.summary}")

            # Find the next parent up the hierarchy
            # We need to look for the parent of this parent
            parent_section = None
            for (
                s
            ) in self.sections_cache:  # We'll need to store sections for this lookup
                if s.id == current_parent_id:
                    parent_section = s
                    break

            current_parent_id = parent_section.parent_id if parent_section else None

        # Return in hierarchical order (highest level first)
        return list(reversed(parent_contexts))

    def _get_previous_sibling_contexts(
        self, section: DocumentSection, summaries: dict[str, SectionSummary]
    ) -> list[str]:
        """Get contexts from previous siblings (same parent, processed before this section)."""
        if not section.parent_id:
            return []  # Root section has no siblings

        sibling_contexts = []

        # Find all siblings with the same parent
        for (
            other_section
        ) in self.sections_cache:  # We'll need to store sections for this lookup
            if (
                other_section.parent_id == section.parent_id
                and other_section.id != section.id
                and other_section.order_index
                < section.order_index  # Previous siblings only
                and other_section.id in summaries
            ):
                sibling_summary = summaries[other_section.id]
                sibling_contexts.append(
                    f"{sibling_summary.title}: {sibling_summary.summary}"
                )

        return sibling_contexts

    async def _process_section_with_authority(
        self,
        section: DocumentSection,
        cumulative_context: str,
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Process section with text source authority principle.

        Implements the text authority principle from SPECS v2.0:
        The original text is the supreme authority - context is supporting information only.

        Args:
            section: Section to process.
            cumulative_context: Cumulative context (parents + previous siblings).
            language: Document language.

        Returns:
            Section summary with text authority applied.
        """
        # Prepare content with authority hierarchy: TEXT > CONTEXT
        if cumulative_context:
            # Structure prompt to enforce text authority principle
            content_with_authority = f"""CONTEXT (background information only):
{cumulative_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section.content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use CONTEXT only as background information to inform understanding
3. If SOURCE TEXT contradicts any CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
   - The SOURCE TEXT is always correct
4. Generate summary that accurately reflects the SOURCE TEXT
5. Identify concepts mentioned in SOURCE TEXT (not just from context)

Remember: SOURCE TEXT has supreme authority over all context information."""

            logger.debug(
                f"🏆 Processing '{section.title}' with text authority principle + context"
            )
        else:
            # No context available - process text directly
            content_with_authority = section.content
            logger.debug(
                f"🏆 Processing '{section.title}' with text authority principle (no context)"
            )

        # Process using the authority-aware content
        summary = await self._process_section_single_pass(
            section=section, content=content_with_authority, language=language
        )

        return summary

    async def _update_parent_levels_incrementally(
        self,
        processed_section: DocumentSection,
        section_summary: SectionSummary,
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> None:
        """Update parent levels incrementally as children are processed.

        Implements incremental updates from SPECS v2.0:
        Parent summaries evolve as their children are processed.

        Args:
            processed_section: Section that was just processed.
            section_summary: Summary of the processed section.
            summaries: All current summaries.
            language: Document language.
        """
        if not processed_section.parent_id:
            return  # Root section has no parents to update

        # Find the parent section
        parent_section = None
        for section in self.sections_cache:
            if section.id == processed_section.parent_id:
                parent_section = section
                break

        if not parent_section:
            logger.warning(f"Parent section not found for '{processed_section.title}'")
            return

        # Check if parent has own content - if so, it should be processed/updated
        if parent_section.content and parent_section.content.strip():
            if parent_section.id in summaries:
                # Parent exists - update it with new child information
                await self._update_existing_parent_summary(
                    parent_section, section_summary, summaries, language
                )
                logger.debug(
                    f"📈 Updated parent '{parent_section.title}' with child '{processed_section.title}'"
                )
            else:
                logger.debug(
                    f"⏳ Parent '{parent_section.title}' not yet processed, will be handled later"
                )
        else:
            # Parent without content - will be handled in deferred synthesis
            logger.debug(
                f"⏳ Parent '{parent_section.title}' without content, deferred synthesis"
            )

    async def _update_existing_parent_summary(
        self,
        parent_section: DocumentSection,
        new_child_summary: SectionSummary,
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> None:
        """Update existing parent summary with new child information."""
        if parent_section.id not in summaries:
            return

        current_parent_summary = summaries[parent_section.id]

        # Gather all existing child summaries
        child_summaries = []
        for child_id in parent_section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        if child_summaries:
            # Create updated synthesis content
            synthesis_content = f"""Parent section summary:
{current_parent_summary.summary}

Updated subsection summaries:
{chr(10).join(child_summaries)}"""

            # Re-process parent with updated children context
            updated_summary = await self._process_section_single_pass(
                section=parent_section,
                content=synthesis_content,
                language=language,
            )

            if updated_summary:
                summaries[parent_section.id] = updated_summary
                logger.debug(
                    f"📈 Parent '{parent_section.title}' summary updated with {len(child_summaries)} children"
                )

    async def _process_pending_parents(
        self,
        processed_section: DocumentSection,
        pending_parents: dict[str, DocumentSection],
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> None:
        """Check if any pending parents can now be synthesized.

        Implements deferred synthesis from SPECS v2.0:
        Parents without content wait until all children are processed.

        Args:
            processed_section: Section that was just processed.
            pending_parents: Dictionary of pending parent sections.
            summaries: Current summaries.
            language: Document language.
        """
        # Check if the processed section makes any pending parent ready
        to_process = []

        for parent_id, parent_section in pending_parents.items():
            if self._are_all_children_processed(parent_section, summaries):
                to_process.append((parent_id, parent_section))

        # Process ready parents
        for parent_id, parent_section in to_process:
            summary = await self._synthesize_parent_from_children(
                parent_section, summaries, language
            )

            if summary:
                summaries[parent_section.id] = summary
                logger.info(
                    f"✅ Synthesized parent '{parent_section.title}' from {len(parent_section.children_ids)} children"
                )

                # Remove from pending
                del pending_parents[parent_id]

                # Save partial result
                await self._save_partial_result_if_enabled(
                    parent_section, summary, len(summaries)
                )
            else:
                logger.warning(
                    f"❌ Failed to synthesize parent '{parent_section.title}'"
                )

    def _are_all_children_processed(
        self,
        parent_section: DocumentSection,
        summaries: dict[str, SectionSummary],
    ) -> bool:
        """Check if all children of a parent section have been processed."""
        for child_id in parent_section.children_ids:
            if child_id not in summaries:
                return False
        return True

    async def _synthesize_parent_from_children(
        self,
        parent_section: DocumentSection,
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Synthesize parent summary from children summaries only."""
        # Gather all child summaries
        child_summaries = []
        for child_id in parent_section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(
                    f"{child_summary.title}: {child_summary.summary}"
                )

        if not child_summaries:
            logger.warning(
                f"No child summaries found for parent: {parent_section.title}"
            )
            return None

        # Build cumulative context (from parents above this one)
        cumulative_context = self._build_cumulative_context(parent_section, summaries)

        # Create synthesis content
        if cumulative_context:
            synthesis_content = f"""CONTEXT (background information only):
{cumulative_context}

SUBSECTION SUMMARIES (to synthesize):
{chr(10).join(child_summaries)}

INSTRUCTIONS:
Synthesize the above subsection summaries into a coherent parent section summary.
The subsection summaries are authoritative for their content.
Use context as background information only."""
        else:
            synthesis_content = f"""SUBSECTION SUMMARIES (to synthesize):
{chr(10).join(child_summaries)}

INSTRUCTIONS:
Synthesize the above subsection summaries into a coherent parent section summary."""

        # Process synthesis
        summary = await self._process_section_single_pass(
            section=parent_section, content=synthesis_content, language=language
        )

        return summary

    async def _finalize_pending_parents(
        self,
        pending_parents: dict[str, DocumentSection],
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> None:
        """Process any remaining pending parents at the end.

        This handles edge cases where some parents might still be pending
        at the end of sequential processing.
        """
        if not pending_parents:
            return

        logger.info(f"🔄 Finalizing {len(pending_parents)} remaining pending parents")

        # Process remaining parents in order
        pending_list = list(pending_parents.items())

        for parent_id, parent_section in pending_list:
            summary = await self._synthesize_parent_from_children(
                parent_section, summaries, language
            )

            if summary:
                summaries[parent_section.id] = summary
                logger.info(
                    f"✅ Finalized parent '{parent_section.title}' from {len(parent_section.children_ids)} children"
                )
            else:
                logger.warning(f"❌ Failed to finalize parent '{parent_section.title}'")

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

    # TODO: Phase 2 - Implement multi-pass processing with specialized prompts and enriched context

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
