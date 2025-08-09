"""Progressive reading engine - main cognitive document reader."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..llm.client import LLMClient
from ..models.config import ReadingConfig
from ..models.document import DocumentKnowledge, DocumentSection, SectionSummary
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

    def __init__(self, config: ReadingConfig | None = None) -> None:
        """Initialize the cognitive reader.

        Args:
            config: Reading configuration. If None, will load from environment.
        """
        self.config = config or ReadingConfig.from_env()
        self.parser = DoclingParser()
        self.synthesizer = Synthesizer(self.config)
        self.language_detector = LanguageDetector()

        logger.info(f"CognitiveReader initialized with model: {self.config.active_model} (fast_mode: {self.config.fast_mode})")
        if self.config.is_development_mode():
            logger.info("Development mode enabled - no real LLM calls will be made")

    async def read_document(self, file_path: str | Path) -> DocumentKnowledge:
        """Read and analyze a document file with cognitive understanding.

        Args:
            file_path: Path to the document file to read.

        Returns:
            Complete DocumentKnowledge with analysis and summaries.

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
                return DocumentKnowledge(
                    document_title="Configuration Validation",
                    document_summary="Configuration is valid and ready for processing.",
                    detected_language=LanguageCode.EN,
                    sections=[],
                    section_summaries={},
                    processing_metadata={"validation_only": True},
                )
            else:
                raise ValueError("Configuration validation failed")

        # Parse document structure
        document_title, sections = await self.parser.parse_document(file_path)

        if not sections:
            logger.warning(f"No sections found in document: {file_path}")
            return DocumentKnowledge(
                document_title=document_title,
                document_summary="Empty document - no content to analyze.",
                detected_language=LanguageCode.EN,
                sections=[],
                section_summaries={},
                processing_metadata={"empty_document": True},
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
    ) -> DocumentKnowledge:
        """Read and analyze text content directly with cognitive understanding.

        Args:
            text: Raw text content to analyze.
            title: Title for the document.

        Returns:
            Complete DocumentKnowledge with analysis and summaries.
        """
        logger.info(f"Starting cognitive reading of text: {title}")

        # Validate configuration if requested
        if self.config.validate_config_only:
            is_valid = await self.validate_configuration()
            if is_valid:
                logger.info("Configuration validation successful")
                return DocumentKnowledge(
                    document_title="Configuration Validation",
                    document_summary="Configuration is valid and ready for processing.",
                    detected_language=LanguageCode.EN,
                    sections=[],
                    section_summaries={},
                    processing_metadata={"validation_only": True},
                )
            else:
                raise ValueError("Configuration validation failed")

        # Parse text content
        document_title, sections = await self.parser.parse_text(text, title)

        if not sections:
            logger.warning("No sections found in text content")
            return DocumentKnowledge(
                document_title=document_title,
                document_summary="Empty content - no sections to analyze.",
                detected_language=LanguageCode.EN,
                sections=[],
                section_summaries={},
                processing_metadata={"empty_content": True},
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
        """Perform progressive reading of document sections.

        Processes sections in document order, accumulating context progressively
        and generating summaries for content sections (leaves in the hierarchy).

        Args:
            sections: Document sections to process.
            language: Detected document language.

        Returns:
            Dictionary of section summaries for content sections.
        """
        logger.info(f"Starting progressive reading of {len(sections)} sections")

        section_summaries = {}
        accumulated_context = ""

        # Sort sections by order_index to maintain document flow
        ordered_sections = sorted(sections, key=lambda s: s.order_index)

        # Apply development filters if configured
        filtered_sections = self._apply_section_filters(ordered_sections)

        # Filter to content sections only (sections without children)
        content_sections = [s for s in filtered_sections if not s.children_ids]

        logger.info(f"Processing {len(content_sections)} content sections")
        if self.config.max_sections or self.config.max_section_depth:
            logger.info(f"Filters applied - Original: {len(ordered_sections)}, Filtered: {len(filtered_sections)}")

        async with LLMClient(self.config) as llm_client:
            for i, section in enumerate(content_sections):
                logger.debug(
                    f"Processing section {i + 1}/{len(content_sections)}: {section.title}"
                )

                # Generate section summary with accumulated context
                summary = await self._process_section(
                    section, accumulated_context, language, llm_client
                )

                if summary:
                    section_summaries[section.id] = summary

                    # Save partial result if configured
                    if self.config.save_partial_results:
                        await self._save_partial_result(
                            section_index=i + 1,
                            total_sections=len(content_sections),
                            section=section,
                            summary=summary,
                            accumulated_context=accumulated_context,
                        )

                    # Update accumulated context for next sections
                    accumulated_context = self._update_accumulated_context(
                        accumulated_context, summary
                    )

                    logger.debug(f"Section processed: {section.title}")
                else:
                    logger.warning(f"Failed to process section: {section.title}")

        logger.info(
            f"Progressive reading completed: {len(section_summaries)} summaries generated"
        )
        return section_summaries

    async def _process_section(
        self,
        section: DocumentSection,
        accumulated_context: str,
        language: LanguageCode,
        llm_client: LLMClient,
    ) -> SectionSummary | None:
        """Process a single section to generate its summary.

        Args:
            section: The section to process.
            accumulated_context: Context from previously processed sections.
            language: Document language.
            llm_client: LLM client for generation.

        Returns:
            SectionSummary for the section, or None if processing fails.
        """
        try:
            # Generate summary using LLM
            summary_response = await llm_client.generate_summary(
                content=section.content,
                context=accumulated_context,
                prompt_type="section_summary",
                language=language,
                section_title=section.title,
            )

            # Extract key concepts
            key_concepts = await llm_client.extract_concepts(
                section_title=section.title,
                section_content=section.content,
                language=language,
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
                confidence_score=1.0,
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
        if self.config.max_section_depth is not None:
            filtered_sections = self._filter_by_depth(
                filtered_sections, self.config.max_section_depth
            )
            logger.info(
                f"Depth filter applied (max depth: {self.config.max_section_depth}): "
                f"{len(sections)} -> {len(filtered_sections)} sections"
            )

        # Apply section count limit if configured
        if self.config.max_sections is not None:
            original_count = len(filtered_sections)
            filtered_sections = filtered_sections[: self.config.max_sections]
            logger.info(
                f"Section count limit applied (max: {self.config.max_sections}): "
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

    async def _save_partial_result(
        self,
        section_index: int,
        total_sections: int,
        section: DocumentSection,
        summary: SectionSummary,
        accumulated_context: str,
    ) -> None:
        """Save partial processing result for debugging and evaluation.

        Args:
            section_index: Current section number (1-based).
            total_sections: Total number of sections being processed.
            section: The processed section.
            summary: Generated summary for the section.
            accumulated_context: Current accumulated context.
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
                    "model_used": self.config.active_model,
                    "fast_mode": self.config.fast_mode,
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
