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
from ..models.metrics import ProcessingMetrics
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

    def __init__(
        self,
        config: CognitiveConfig | None = None,
        metrics: ProcessingMetrics | None = None,
    ) -> None:
        """Initialize the cognitive reader.

        Args:
            config: Reading configuration. If None, will load from environment.
            metrics: Optional metrics collector for tracking processing statistics.
        """
        self.config = config or CognitiveConfig.from_env()
        self.metrics = metrics
        self.parser = DoclingParser()
        self.synthesizer = Synthesizer(
            self.config,
            save_partial_result_fn=self._save_partial_result,
            metrics=self.metrics,
        )
        self.language_detector = LanguageDetector()

        # Storage for passing glossary between passes
        self.current_pass_glossary: dict[str, str] = {}

        # Log the actual processing strategy being used
        if self.config.num_passes > 1:
            logger.info(
                f"CognitiveReader initialized with {self.config.num_passes}-pass models: fast={self.config.fast_pass_model}, main={self.config.main_model}"
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

        # Build complete knowledge from incrementally updated state
        # (avoiding expensive re-synthesis - summaries and glossary already updated)
        knowledge = self._build_cognitive_knowledge_from_current_state(
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

        # Build complete knowledge from incrementally updated state
        # (avoiding expensive re-synthesis - summaries and glossary already updated)
        knowledge = self._build_cognitive_knowledge_from_current_state(
            sections=sections,
            section_summaries=section_summaries,
            document_title=title,
            detected_language=detected_language,
        )

        logger.info(
            f"Text cognitive reading completed: {len(sections)} sections, {len(section_summaries)} summaries"
        )
        return knowledge

    async def _progressive_reading(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Perform multi-pass cognitive processing of document sections.

        Implements the algorithm defined in SPECS v2.0:
        - Pass 1: Sequential processing with cumulative context
        - Pass 2+: Sequential processing with enriched context (summaries + glossary)
        - N-pass extensible architecture for future iterations

        Args:
            sections: Document sections to process.
            language: Detected document language.

        Returns:
            Dictionary of section summaries for all sections.
        """
        logger.info(f"Starting cognitive processing of {len(sections)} sections")

        # Sort sections by order_index to maintain document flow
        ordered_sections = sorted(sections, key=lambda s: s.order_index)

        # Apply development filters if configured
        filtered_sections = self._apply_section_filters(ordered_sections)

        # Determine number of passes to perform
        if self.config.single_pass:
            logger.info(
                "🚀 Single-pass mode: Processing with one pass only (fast testing)"
            )
            return await self._single_pass_processing(filtered_sections, language)
        elif self.config.num_passes > 1:
            logger.info(
                f"🔄 Multi-pass mode: Processing with {self.config.num_passes} passes"
            )
            return await self._multi_pass_processing(filtered_sections, language)
        else:
            logger.info("📖 Standard mode: Processing with sequential algorithm")
            return await self._single_pass_processing(filtered_sections, language)

    async def _single_pass_processing(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Process sections with a single pass using sequential algorithm."""
        logger.info(f"Processing {len(sections)} sections using sequential algorithm")
        return await self._sequential_processing(sections, language)

    async def _multi_pass_processing(
        self, sections: list[DocumentSection], language: LanguageCode
    ) -> dict[str, SectionSummary]:
        """Process sections with multiple passes using enriched context.

        Architecture designed for N-pass extensibility:
        - Pass 1: Sequential processing with cumulative context
        - Pass 2+: Sequential processing with enriched context (previous summaries + glossary)
        - Intermediate files saved between passes (if enabled)

        Args:
            sections: Document sections to process.
            language: Document language.

        Returns:
            Final section summaries after all passes.
        """
        # Pass 1: Initial sequential processing
        logger.info("🔄 PASS 1: Sequential processing with cumulative context")
        pass1_start = self.metrics.start_pass(1) if self.metrics else 0
        pass1_summaries = await self._sequential_processing(sections, language)
        if self.metrics:
            self.metrics.end_pass(1, pass1_start)

        # Save intermediate results after Pass 1
        if self.config.save_intermediate:
            await self._save_intermediate_pass(
                pass_number=1,
                sections=sections,
                summaries=pass1_summaries,
                language=language,
                description="Sequential processing with cumulative context",
            )

        # For now, implement just 2 passes (Pass 1 + Pass 2)
        # Architecture is ready for N passes in the future

        # Pass 2: Sequential processing with enriched context
        logger.info("🔄 PASS 2: Sequential processing with enriched context")
        pass2_start = self.metrics.start_pass(2) if self.metrics else 0
        pass2_summaries = await self._sequential_processing_with_enriched_context(
            sections=sections, previous_summaries=pass1_summaries, language=language
        )
        if self.metrics:
            self.metrics.end_pass(2, pass2_start)

        # Save intermediate results after Pass 2
        if self.config.save_intermediate:
            await self._save_intermediate_pass(
                pass_number=2,
                sections=sections,
                summaries=pass2_summaries,
                language=language,
                description="Sequential processing with enriched context (summaries + glossary)",
            )

        # TODO: Future N-pass implementation would loop here
        # for pass_num in range(3, self.config.max_passes + 1):
        #     pass_summaries = await self._sequential_processing_with_enriched_context(...)

        logger.info("✅ Multi-pass processing completed")
        return pass2_summaries

    async def _sequential_processing_with_enriched_context(
        self,
        sections: list[DocumentSection],
        previous_summaries: dict[str, SectionSummary],
        language: LanguageCode,
    ) -> dict[str, SectionSummary]:
        """Sequential processing with enriched context from previous passes.

        Uses the same sequential algorithm but with enriched context:
        - Current parent summaries (from previous pass)
        - Previous summary of same node (from previous pass)
        - Concept glossary (extracted from previous pass)
        - Still maintains text authority principle: text > enriched context

        Args:
            sections: Document sections to process.
            previous_summaries: Summaries from previous pass.
            language: Document language.

        Returns:
            Enhanced section summaries with enriched context.
        """
        # Step 1: Use concept glossary from previous pass (already generated)
        logger.info("📚 Using concept glossary from previous pass")
        concept_glossary = self.current_pass_glossary

        # Step 2: Order sections in document sequence (same as Pass 1)
        self.sections_cache = sections  # Store for context building methods
        ordered_sections = self._order_by_document_sequence(sections)

        logger.info(
            f"📖 Sequential processing (Pass 2+): {len(ordered_sections)} sections with enriched context"
        )

        # Show which model is being used for pass 2+
        processing_model = self.config.main_model or self.config.model_name
        logger.info(
            f"🧠 Processing document with enriched sequential algorithm, model: {processing_model}"
        )

        # Step 3: Process sections sequentially with enriched context
        summaries: dict[str, SectionSummary] = {}
        pending_parents: dict[str, DocumentSection] = {}

        for section in ordered_sections:
            logger.debug(
                f"📖 Processing section '{section.title}' with enriched context"
            )

            # Build enriched cumulative context
            enriched_context = self._build_enriched_cumulative_context(
                section=section,
                current_summaries=summaries,
                previous_summaries=previous_summaries,
                concept_glossary=concept_glossary,
            )

            if section.children_ids and (
                not section.content or not section.content.strip()
            ):
                # Parent WITHOUT content: defer synthesis
                logger.debug(
                    f"⏳ Deferring synthesis for parent without content: '{section.title}'"
                )
                pending_parents[section.id] = section
                continue

            # Process section with enriched context and text authority
            summary = await self._process_section_with_enriched_authority(
                section=section, enriched_context=enriched_context, language=language
            )

            if summary:
                summaries[section.id] = summary
                logger.info(f"✅ Enhanced '{section.title}' with enriched context")

                # Update parent levels incrementally
                await self._update_parent_levels_incrementally(
                    section, summary, summaries, language
                )

                # Check pending parents
                await self._process_pending_parents(
                    section, pending_parents, summaries, language
                )

                # Save partial result
                await self._save_partial_result_if_enabled(
                    section, summary, len(summaries)
                )
            else:
                logger.warning(
                    f"❌ Failed to enhance '{section.title}' with enriched context"
                )

        # Finalize pending parents
        await self._finalize_pending_parents(pending_parents, summaries, language)

        # Update existing concept definitions with enriched context
        logger.info("📚 Updating concept definitions with enriched context")
        await self._update_existing_concept_definitions(summaries, language)

        logger.info(
            f"Enhanced sequential processing completed: {len(summaries)} sections processed"
        )
        return summaries

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

        async with LLMClient(self.config, self.metrics) as llm_client:
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

                    # Update metrics if available
                    if self.metrics:
                        self.metrics.add_section()

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

        # Generate concept glossary as part of this pass (using synthesizer)
        logger.info("📚 Generating concept glossary for this pass")
        await self._generate_pass_glossary(summaries, language)

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

    async def _generate_pass_glossary(
        self, summaries: dict[str, SectionSummary], language: LanguageCode
    ) -> None:
        """Generate concept glossary for this pass using synthesizer (automatically respects max_glossary_concepts).

        This creates a complete glossary as part of the pass using full document synthesis.
        The glossary is stored in self.current_pass_glossary for the next pass.
        """
        try:
            # Get sections from cache for synthesizer
            if not hasattr(self, "sections_cache") or not self.sections_cache:
                logger.warning(
                    "📚 No sections cache available, using fallback glossary"
                )
                await self._create_fallback_glossary(summaries)
                return

            # Create document title from summaries
            root_summaries = [s for s in summaries.values() if not s.parent_id]
            document_title = (
                root_summaries[0].title if root_summaries else "Document Analysis"
            )

            # Use synthesizer to perform complete document synthesis (includes glossary)
            # This automatically respects max_glossary_concepts configuration
            cognitive_knowledge = await self.synthesizer.synthesize_document(
                sections=self.sections_cache,
                section_summaries=summaries,
                document_title=document_title,
                detected_language=language,
            )

            # Extract glossary from synthesis result and convert to simple dict for context
            self.current_pass_glossary = {
                concept.name: concept.definition
                for concept in cognitive_knowledge.concepts
            }

            logger.info(
                f"📚 Generated pass glossary with {len(self.current_pass_glossary)} concept definitions "
                f"(synthesizer automatically respected max_glossary_concepts={self.config.max_glossary_concepts})"
            )

        except Exception as e:
            logger.warning(
                f"📚 Failed to generate pass glossary using synthesizer: {e}"
            )
            await self._create_fallback_glossary(summaries)

    async def _create_fallback_glossary(
        self, summaries: dict[str, SectionSummary]
    ) -> None:
        """Create simple fallback glossary from summaries when synthesizer fails."""
        # Fallback: extract key concepts from summaries
        all_concepts = set()
        for summary in summaries.values():
            if summary.key_concepts:
                all_concepts.update(summary.key_concepts)

        # Respect user's max_glossary_concepts configuration
        max_concepts = min(self.config.max_glossary_concepts, len(all_concepts))
        concept_list = list(all_concepts)[:max_concepts]
        self.current_pass_glossary = {
            concept: "Key concept identified in document analysis"
            for concept in concept_list
        }

        logger.info(
            f"📚 Generated fallback glossary with {len(self.current_pass_glossary)} concepts"
        )

    async def _update_existing_concept_definitions(
        self, summaries: dict[str, SectionSummary], language: LanguageCode
    ) -> None:
        """Update existing concept definitions with enriched context from updated summaries.

        This method incrementally improves concept definitions rather than regenerating
        the entire glossary, making it much more efficient for multi-pass processing.

        Args:
            summaries: Updated section summaries from current pass
            language: Document language
        """
        if not hasattr(self, "current_pass_glossary") or not self.current_pass_glossary:
            logger.info(
                "📚 No existing glossary found, skipping concept definition updates"
            )
            return

        # Deduplicate concepts (case-insensitive) first
        deduplicated_concepts = self._deduplicate_concepts(self.current_pass_glossary)
        original_count = len(self.current_pass_glossary)
        dedupe_count = len(deduplicated_concepts)

        if original_count != dedupe_count:
            logger.info(f"📚 Deduplicated concepts: {original_count} → {dedupe_count}")

        # Build concept-to-sections mapping for targeted context
        concept_to_sections = self._build_concept_to_sections_mapping(summaries)

        updated_concepts = {}
        concept_count = len(deduplicated_concepts)

        logger.info(
            f"📚 Updating {concept_count} existing concept definitions with enriched context"
        )

        # Create LLM client for concept definition updates
        from ..llm.client import LLMClient

        async with LLMClient(self.config, self.metrics) as llm_client:
            for i, (concept_name, current_definition) in enumerate(
                deduplicated_concepts.items(), 1
            ):
                try:
                    # Build specific context for this concept
                    concept_context = self._build_concept_specific_context(
                        concept_name, summaries, concept_to_sections
                    )

                    # Generate enhanced definition using concept-specific context
                    enhanced_response = await llm_client.generate_concept_definition(
                        concept=concept_name, context=concept_context, language=language
                    )

                    updated_concepts[concept_name] = enhanced_response.definition

                    logger.debug(
                        f"📚 Updated definition for '{concept_name}' ({i}/{concept_count})"
                    )

                except Exception as e:
                    logger.warning(
                        f"📚 Failed to update definition for '{concept_name}': {e}"
                    )
                    # Keep original definition if update fails
                    updated_concepts[concept_name] = current_definition

        # Update the glossary with enhanced definitions
        self.current_pass_glossary = updated_concepts

        logger.info(
            f"📚 Successfully updated {len(updated_concepts)} concept definitions "
            f"using enriched context from {len(summaries)} section summaries"
        )

    def _normalize_concept_name(self, concept_name: str) -> str:
        """Normalize concept name for consistent deduplication and mapping.

        Converts to lowercase, removes extra whitespace, and normalizes separators.

        Args:
            concept_name: Raw concept name

        Returns:
            Normalized concept name

        Examples:
            >>> _normalize_concept_name("Cognitive_Reading")
            "cognitive reading"
            >>> _normalize_concept_name("document-processing  ")
            "document processing"
        """
        # Comprehensive normalization: lowercase, strip, and normalize separators
        normalized = concept_name.lower().strip().replace("_", " ").replace("-", " ")
        # Clean up multiple spaces
        return " ".join(normalized.split())

    def _deduplicate_concepts(self, concepts: dict[str, str]) -> dict[str, str]:
        """Remove duplicate concepts using comprehensive normalization.

        Handles case-insensitive deduplication and normalizes spaces/underscores.
        Preserves the concept with the longest definition when duplicates are found.

        Args:
            concepts: Original concept dictionary {name: definition}

        Returns:
            Deduplicated concept dictionary
        """
        if not concepts:
            return {}

        # Group concepts by normalized name (lowercase + spaces/underscores normalized)
        concept_groups: dict[str, list[tuple[str, str]]] = {}

        for name, definition in concepts.items():
            normalized_name = self._normalize_concept_name(name)

            if normalized_name not in concept_groups:
                concept_groups[normalized_name] = []
            concept_groups[normalized_name].append((name, definition))

        # For each group, select the best representative
        deduplicated = {}
        for normalized_name, group in concept_groups.items():
            if len(group) == 1:
                # No duplicates, keep as-is
                name, definition = group[0]
                deduplicated[name] = definition
            else:
                # Multiple concepts, choose the one with longest definition
                best_name, best_definition = max(group, key=lambda x: len(x[1]))
                deduplicated[best_name] = best_definition

                # Log deduplication for debugging
                duplicate_names = [name for name, _ in group if name != best_name]
                logger.debug(
                    f"📚 Deduplicated '{normalized_name}': kept '{best_name}', removed {duplicate_names}"
                )

        return deduplicated

    def _build_concept_to_sections_mapping(
        self, summaries: dict[str, SectionSummary]
    ) -> dict[str, list[str]]:
        """Build mapping of concepts to sections where they appear.

        Uses the same normalization as _deduplicate_concepts for consistency.

        Args:
            summaries: Section summaries with key_concepts

        Returns:
            Dictionary mapping concept names to section IDs
        """
        concept_to_sections: dict[str, list[str]] = {}

        for section_id, summary in summaries.items():
            for concept in summary.key_concepts:
                normalized_concept = self._normalize_concept_name(concept)

                if normalized_concept not in concept_to_sections:
                    concept_to_sections[normalized_concept] = []
                concept_to_sections[normalized_concept].append(section_id)

        return concept_to_sections

    def _build_concept_specific_context(
        self,
        concept_name: str,
        summaries: dict[str, SectionSummary],
        concept_to_sections: dict[str, list[str]],
    ) -> str:
        """Build context specific to a concept by including relevant sections.

        Args:
            concept_name: Name of the concept
            summaries: All section summaries
            concept_to_sections: Mapping of concepts to sections

        Returns:
            Targeted context string for this specific concept
        """
        # Use same normalization as other functions for consistency
        normalized_concept = self._normalize_concept_name(concept_name)
        relevant_section_ids = concept_to_sections.get(normalized_concept, [])

        if not relevant_section_ids:
            # Fallback: use all summaries (but this should rarely happen)
            context_parts = [f"{s.title}: {s.summary}" for s in summaries.values()]
        else:
            # Use only sections where this concept appears
            context_parts = []
            for section_id in relevant_section_ids:
                if section_id in summaries:
                    summary = summaries[section_id]
                    context_parts.append(f"{summary.title}: {summary.summary}")

        # Limit context size to avoid token overflow
        max_context_parts = 5  # Reasonable limit for concept-specific context
        if len(context_parts) > max_context_parts:
            context_parts = context_parts[:max_context_parts]
            logger.debug(
                f"📚 Limited context for '{concept_name}' to {max_context_parts} most relevant sections"
            )

        return "\n".join(context_parts)

    def _build_cognitive_knowledge_from_current_state(
        self,
        sections: list[DocumentSection],
        section_summaries: dict[str, SectionSummary],
        document_title: str,
        detected_language: LanguageCode,
    ) -> CognitiveKnowledge:
        """Build CognitiveKnowledge from current state without full synthesis.

        This method constructs the final cognitive knowledge object using the
        incrementally updated summaries and glossary, avoiding expensive re-synthesis.

        Args:
            sections: Original document sections
            section_summaries: Final section summaries from all passes
            document_title: Document title
            detected_language: Detected document language

        Returns:
            Complete CognitiveKnowledge object
        """
        # Generate document summary from section summaries
        document_summary_text = self._generate_document_summary_from_sections(
            section_summaries, document_title
        )

        # Convert current glossary to ConceptDefinition objects
        from ..models.knowledge import ConceptDefinition

        # Ensure concepts are deduplicated before final construction
        final_concepts = self._deduplicate_concepts(self.current_pass_glossary or {})

        # Build concept-to-sections mapping for accurate section tracking
        concept_to_sections = self._build_concept_to_sections_mapping(section_summaries)

        concepts = []
        for concept_name, definition in final_concepts.items():
            # Find sections where this concept actually appears
            normalized_concept = concept_name.lower().strip()
            relevant_section_ids = concept_to_sections.get(normalized_concept, [])

            # Use first occurrence as "first mentioned"
            first_mentioned = (
                relevant_section_ids[0]
                if relevant_section_ids
                else (
                    list(section_summaries.keys())[0]
                    if section_summaries
                    else "unknown"
                )
            )

            concept_def = ConceptDefinition(
                concept_id=concept_name.lower().replace(" ", "_").replace("-", "_"),
                name=concept_name,
                definition=definition,
                first_mentioned_in=first_mentioned,
                relevant_sections=relevant_section_ids
                or list(section_summaries.keys()),
            )
            concepts.append(concept_def)

        # Calculate statistics
        avg_summary_length = (
            sum(len(summary.summary) for summary in section_summaries.values())
            / len(section_summaries)
            if section_summaries
            else 0.0
        )

        # Build hierarchy index and parent-child map
        hierarchy_index: dict[str, list[str]] = {}
        parent_child_map: dict[str, list[str]] = {}

        for summary in section_summaries.values():
            level_str = str(summary.level)
            if level_str not in hierarchy_index:
                hierarchy_index[level_str] = []
            hierarchy_index[level_str].append(summary.section_id)

            if summary.children_ids:
                parent_child_map[summary.section_id] = summary.children_ids

        # Build cognitive knowledge (clean title from markdown)
        from ..utils.text_cleaning import clean_section_title

        knowledge = CognitiveKnowledge(
            document_title=clean_section_title(document_title),
            document_summary=document_summary_text,
            detected_language=detected_language,
            hierarchical_summaries=section_summaries,
            concepts=concepts,
            hierarchy_index=hierarchy_index,
            parent_child_map=parent_child_map,
            total_sections=len(section_summaries),  # Use processed sections count
            avg_summary_length=avg_summary_length,
            total_concepts=len(concepts),
        )

        logger.info(
            f"🧠 Built cognitive knowledge from current state: {len(section_summaries)} summaries, "
            f"{len(concepts)} concepts, avoiding expensive re-synthesis"
        )

        return knowledge

    def _generate_document_summary_from_sections(
        self, section_summaries: dict[str, SectionSummary], document_title: str
    ) -> str:
        """Generate document summary from section summaries without LLM call.

        For now, this creates a simple concatenation-based summary.
        Could be enhanced to use LLM for better synthesis if needed.
        """
        if not section_summaries:
            return f"Analysis of {document_title} (no sections processed)"

        # Get root-level sections (those without parent_id)
        root_sections = [s for s in section_summaries.values() if not s.parent_id]

        if root_sections:
            summary_parts = [f"{s.title}: {s.summary}" for s in root_sections]
            return f"{document_title} - " + "; ".join(summary_parts)
        else:
            # Fallback: use first few section summaries
            first_sections = list(section_summaries.values())[:3]
            summary_parts = [f"{s.title}: {s.summary}" for s in first_sections]
            return f"{document_title} - " + "; ".join(summary_parts)

    def _build_enriched_cumulative_context(
        self,
        section: DocumentSection,
        current_summaries: dict[str, SectionSummary],
        previous_summaries: dict[str, SectionSummary],
        concept_glossary: dict[str, str],
    ) -> str:
        """Build enriched cumulative context with previous summaries + glossary."""
        # Build regular cumulative context first
        base_context = self._build_cumulative_context(section, current_summaries)

        # Add previous summary of same node if available
        previous_context_parts = []
        if base_context:
            previous_context_parts.append(f"CURRENT CONTEXT:\n{base_context}")

        if section.id in previous_summaries:
            prev_summary = previous_summaries[section.id]
            previous_context_parts.append(
                f"PREVIOUS SUMMARY OF THIS SECTION:\n{prev_summary.title}: {prev_summary.summary}"
            )

        # Add concept glossary if available
        if concept_glossary:
            glossary_entries = [
                f"{concept}: {definition}"
                for concept, definition in list(concept_glossary.items())[:10]
            ]  # Limit to 10 concepts
            if glossary_entries:
                previous_context_parts.append(
                    "CONCEPT GLOSSARY:\n" + "\n".join(glossary_entries)
                )

        enriched_context = "\n\n".join(previous_context_parts)

        if enriched_context:
            logger.debug(
                f"📚 Built enriched context for '{section.title}': {len(previous_context_parts)} context parts"
            )

        return enriched_context

    async def _process_section_with_enriched_authority(
        self,
        section: DocumentSection,
        enriched_context: str,
        language: LanguageCode,
    ) -> SectionSummary | None:
        """Process section with enriched context but maintain text authority."""
        # Similar to _process_section_with_authority but with enriched context
        if enriched_context:
            content_with_authority = f"""ENRICHED CONTEXT (background information only):
{enriched_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section.content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use ENRICHED CONTEXT only as background information to inform understanding
3. The enriched context includes previous summaries and concept definitions
4. If SOURCE TEXT contradicts any ENRICHED CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
   - The SOURCE TEXT is always correct
5. Generate summary that accurately reflects the SOURCE TEXT
6. Use concept definitions to enhance understanding but never override text meaning

Remember: SOURCE TEXT has supreme authority over all enriched context information."""

            logger.debug(
                f"🏆 Processing '{section.title}' with enriched text authority principle + context"
            )
        else:
            content_with_authority = section.content
            logger.debug(
                f"🏆 Processing '{section.title}' with enriched text authority principle (no context)"
            )

        # Process using the authority-aware content with MAIN MODEL (pass 2+)
        model = self.config.main_model or self.config.model_name
        temperature = self.config.main_pass_temperature or self.config.temperature

        async with LLMClient(self.config, self.metrics) as llm_client:
            # Create a temporary section with the authority-aware content
            temp_section = DocumentSection(
                id=section.id,
                title=section.title,
                content=content_with_authority,
                level=section.level,
                order_index=section.order_index,
                parent_id=section.parent_id,
            )
            summary = await self._process_section(
                temp_section,
                "",  # Context already integrated in temp_section.content as authority-aware content
                language,
                llm_client,
                model=model,
                temperature=temperature,
            )

        return summary

    async def _save_intermediate_pass(
        self,
        pass_number: int,
        sections: list[DocumentSection],
        summaries: dict[str, SectionSummary],
        language: LanguageCode,
        description: str,
    ) -> None:
        """Save intermediate pass results to files."""
        if not self.config.save_intermediate:
            return

        import json
        from pathlib import Path

        # Create intermediate directory
        intermediate_dir = Path(self.config.intermediate_dir)
        intermediate_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pass_{pass_number}_{timestamp}.json"
        filepath = intermediate_dir / filename

        # Prepare data for saving
        pass_data = {
            "pass_number": pass_number,
            "description": description,
            "language": language.value,
            "timestamp": timestamp,
            "total_sections": len(sections),
            "total_summaries": len(summaries),
            "sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "level": section.level,
                    "parent_id": section.parent_id,
                    "children_ids": section.children_ids,
                    "order_index": section.order_index,
                }
                for section in sections
            ],
            "summaries": {
                section_id: {
                    "section_id": summary.section_id,
                    "title": summary.title,
                    "summary": summary.summary,
                    "key_concepts": summary.key_concepts,
                    "summary_length": len(summary.summary),
                }
                for section_id, summary in summaries.items()
            },
        }

        # Save to JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(pass_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved Pass {pass_number} intermediate results to: {filepath}")

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

        async with LLMClient(self.config, self.metrics) as llm_client:
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
            async with LLMClient(self.config, self.metrics) as llm_client:
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
