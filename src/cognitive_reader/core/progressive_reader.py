"""Progressive reading engine - main cognitive document reader."""

from __future__ import annotations

import logging
from pathlib import Path

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
        self.synthesizer = Synthesizer(self.config)
        self.language_detector = LanguageDetector()

        # Log the actual processing strategy being used
        if self.config.enable_second_pass:
            logger.info(f"CognitiveReader initialized with dual-pass: fast={self.config.fast_pass_model}, main={self.config.main_model}")
        else:
            # Single-pass: only fast first pass enabled
            active_model = self.config.fast_pass_model or self.config.model_name
            logger.info(f"CognitiveReader initialized with single-pass (fast model): {active_model}")

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

        logger.info(f"Processing {len(filtered_sections)} sections using hierarchical algorithm")

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
        previous_summaries: dict[str, SectionSummary] | None = None
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
                    section, section_context, language, llm_client,
                    model=effective_model, temperature=temperature
                )

                if summary:
                    section_summaries[section.id] = summary

                    # Update accumulated context for next sections
                    accumulated_context = self._update_accumulated_context(
                        accumulated_context, summary
                    )

                    logger.debug(f"[{pass_name}] Section processed: {section.title}")
                else:
                    logger.warning(f"[{pass_name}] Failed to process section: {section.title}")

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

            # Generate summary using LLM
            summary_response = await llm_client.generate_summary(
                content=effective_content,
                context=accumulated_context,
                prompt_type="section_summary",
                language=language,
                section_title=section.title,
                model=model,
                temperature=temperature,
            )

            # Extract key concepts
            key_concepts = await llm_client.extract_concepts(
                section_title=section.title,
                section_content=effective_content,
                language=language,
                model=model,
                temperature=temperature,
            )

            # Parse the summary response
            summary_text, additional_concepts = self._parse_summary_response(
                summary_response
            )

            # Combine concepts, removing duplicates
            all_concepts = key_concepts + additional_concepts
            unique_concepts = []
            seen = set()
            for concept in all_concepts:
                if concept not in seen:
                    unique_concepts.append(concept)
                    seen.add(concept)

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
        """Process sections using hierarchical bottom-up algorithm.

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
        # Step 1: Organize sections by hierarchy level
        levels = self._organize_by_level(sections)
        max_level = max(levels.keys()) if levels else 0

        logger.info(f"Hierarchical structure: {len(levels)} levels (max depth: {max_level})")
        for level, level_sections in levels.items():
            section_titles = [s.title for s in level_sections]
            logger.info(f"  Level {level}: {len(level_sections)} sections - {section_titles}")

        # Step 2: Process from deepest level to root (bottom-up)
        summaries: dict[str, SectionSummary] = {}

        # Log which model will be used for this level
        processing_model = self.config.fast_pass_model or self.config.model_name
        logger.info(f"🧠 Processing document with model: {processing_model}")

        for level in range(max_level, 0, -1):  # Bottom-up processing
            if level not in levels:
                continue

            level_sections = levels[level]

            for section in level_sections:
                # Determine content based on section type
                if section.children_ids:  # Container section
                    content = self._combine_section_and_children_content(section, summaries)
                    logger.debug(f"Container section '{section.title}': own content + {len(section.children_ids)} child summaries")
                else:  # Leaf section
                    content = section.content
                    logger.debug(f"Leaf section '{section.title}': using section content")

                # Process with single-pass approach (Phase 1: dual-pass disabled)
                summary = await self._process_section_single_pass(section, content, language)

                if summary:
                    summaries[section.id] = summary
                    logger.info(f"✅ Processed '{section.title}' (level {level})")
                else:
                    logger.warning(f"❌ Failed to process '{section.title}' (level {level})")

        logger.info(f"Hierarchical processing completed: {len(summaries)} sections processed")
        return summaries

    def _organize_by_level(self, sections: list[DocumentSection]) -> dict[int, list[DocumentSection]]:
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

    def _combine_section_and_children_content(
        self, section: DocumentSection, summaries: dict[str, SectionSummary]
    ) -> str:
        """Combine section's own content with child summaries.

        Args:
            section: Container section to process.
            summaries: Existing section summaries.

        Returns:
            Combined content for LLM processing.
        """
        content_parts = []

        # Add section's own content if it has any
        if section.content and section.content.strip():
            content_parts.append(f"Section content:\n{section.content}")

        # Add child summaries
        child_summaries = []
        for child_id in section.children_ids:
            if child_id in summaries:
                child_summary = summaries[child_id]
                child_summaries.append(f"{child_summary.title}: {child_summary.summary}")

        if child_summaries:
            content_parts.append("Subsection summaries:\n" + "\n\n".join(child_summaries))

        return "\n\n".join(content_parts)

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
                content=content
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

        # TODO: Phase 2 - Re-implement filtering logic
        # Apply depth filter if configured
        # if self.config.max_section_depth is not None:
        #     filtered_sections = self._filter_by_depth(
        #         filtered_sections, self.config.max_section_depth
        #     )
        #     logger.info(
        #         f"Depth filter applied (max depth: {self.config.max_section_depth}): "
        #         f"{len(sections)} -> {len(filtered_sections)} sections"
        #     )

        # Apply section count limit if configured
        # if self.config.max_sections is not None:
        #     original_count = len(filtered_sections)
        #     filtered_sections = filtered_sections[: self.config.max_sections]
        #     logger.info(
        #         f"Section count limit applied (max: {self.config.max_sections}): "
        #         f"{original_count} -> {len(filtered_sections)} sections"
        #     )

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
        section: DocumentSection,
        summary: SectionSummary,
        accumulated_context: str,
    ) -> None:
        """Save partial processing result for debugging and evaluation.

        NOTE: Temporarily disabled for Phase 1 MVP.
        """
        # Temporarily disabled - no-op for Phase 1
        pass

        # TODO: Phase 2 - Re-implement this functionality
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(self.config.partial_results_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create partial result data
            partial_result = {
                "progress": {
                    "section_index": section_index,
                    "total_sections": total_sections,
                    "progress_percentage": round((section_index / total_sections) * 100, 1),
                },
                "section": {
                    "id": section.id,
                    "title": section.title,
                    "level": section.level,
                    "order_index": section.order_index,
                    "content_preview": section.content[:300] + "..."
                    if len(section.content) > 300
                    else section.content,
                },
                "summary": {
                    "title": summary.title,
                    "summary": summary.summary,
                    "key_concepts": summary.key_concepts,
                    "confidence_score": summary.confidence_score,
                },
                "context": {
                    "accumulated_context_length": len(accumulated_context),
                    "accumulated_context_preview": accumulated_context[:200] + "..."
                    if len(accumulated_context) > 200
                    else accumulated_context,
                },
                "config": {
                    "model_used": self.config.main_model or self.config.model_name,
                    "enable_fast_first_pass": self.config.enable_fast_first_pass,
                    "temperature": self.config.temperature,
                },
            }

            # Save to JSON file with zero-padded numbering
            filename = f"partial_{section_index:03d}_of_{total_sections:03d}.json"
            output_file = output_dir / filename

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(partial_result, f, indent=2, ensure_ascii=False)

            logger.debug(f"Partial result saved: {output_file}")

        except Exception as e:
            # Don't fail the main process if partial saving fails
            logger.warning(f"Failed to save partial result for section {section_index}: {e}")
        """

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
