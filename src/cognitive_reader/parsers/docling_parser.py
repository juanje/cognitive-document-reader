"""Universal document parser using docling library."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..models.document import DocumentSection
from .structure_detector import StructureDetector

logger = logging.getLogger(__name__)

# Docling imports for universal document parsing
try:
    from docling.datamodel.base_models import ConversionStatus, InputFormat
    from docling.document_converter import (
        DocumentConverter,
        PdfFormatOption,
        WordFormatOption,
    )
    from docling.pipeline.simple_pipeline import SimplePipeline

    DOCLING_AVAILABLE = True
    logger.info("Docling library available for universal document parsing")
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning(
        "Docling library not available, falling back to basic Markdown parsing"
    )
    # Type-safe fallbacks for when docling is not available
    InputFormat = type(None)  # type: ignore[misc,assignment]
    DocumentConverter = type(None)  # type: ignore[misc,assignment]
    PdfFormatOption = type(None)  # type: ignore[misc,assignment]
    WordFormatOption = type(None)  # type: ignore[misc,assignment]
    SimplePipeline = type(None)  # type: ignore[misc,assignment]
    ConversionStatus = type(None)  # type: ignore[misc,assignment]


class DoclingParser:
    """Universal document parser using docling for multiple formats.

    Provides intelligent document parsing with the following strategy:
    - Uses docling library for PDF, DOCX, HTML when available
    - Falls back to basic Markdown parsing for .md files and when docling unavailable
    - Converts all formats to Markdown internally for consistent processing
    - Extracts hierarchical structure for cognitive reading

    Supported formats (when docling available): PDF, DOCX, HTML, Markdown
    Fallback mode (MVP): Markdown only
    """

    def __init__(self) -> None:
        """Initialize the docling parser."""
        self.structure_detector = StructureDetector()
        self._docling_converter: Any = None  # Type depends on runtime availability

        # Configure supported formats based on docling availability
        if DOCLING_AVAILABLE:
            self._supported_extensions = {".md", ".markdown", ".pdf", ".docx", ".html"}
            self._setup_docling_converter()
        else:
            # Fallback to basic Markdown only for MVP
            self._supported_extensions = {".md", ".markdown"}
            self._docling_converter = None

    def _setup_docling_converter(self) -> None:
        """Setup docling document converter with appropriate configurations."""
        if not DOCLING_AVAILABLE:
            return

        try:
            # Configure docling converter for supported formats
            self._docling_converter = DocumentConverter(
                allowed_formats=[
                    InputFormat.MD,
                    InputFormat.PDF,
                    InputFormat.DOCX,
                    InputFormat.HTML,
                ],
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_cls=SimplePipeline),
                    InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline),
                },
            )
            logger.info("Docling converter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize docling converter: {e}")
            self._docling_converter = None

    async def parse_document(
        self, file_path: str | Path
    ) -> tuple[str, list[DocumentSection]]:
        """Parse a document and extract title, content, and structure.

        Args:
            file_path: Path to the document file to parse.

        Returns:
            Tuple of (document_title, list_of_sections).

        Raises:
            FileNotFoundError: If the document file doesn't exist.
            ValueError: If the document format is not supported.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if file_path.suffix.lower() not in self._supported_extensions:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. "
                f"Supported formats: {', '.join(self._supported_extensions)}"
            )

        logger.info(f"Parsing document: {file_path}")

        try:
            # Use docling for non-markdown files if available
            if (
                DOCLING_AVAILABLE
                and self._docling_converter
                and file_path.suffix.lower() not in {".md", ".markdown"}
            ):
                return await self._parse_with_docling(file_path)
            else:
                # Use basic Markdown parser for .md files or as fallback
                return await self._parse_markdown(file_path)
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            raise ValueError(f"Failed to parse document: {e}") from e

    async def parse_text(
        self, text: str, title: str = "Untitled Document"
    ) -> tuple[str, list[DocumentSection]]:
        """Parse text content directly without file I/O.

        Args:
            text: Raw text content to parse.
            title: Title for the document.

        Returns:
            Tuple of (document_title, list_of_sections).
        """
        logger.info(f"Parsing text content, title: {title}")

        try:
            # Parse markdown-like structure from text
            elements = self._extract_markdown_elements(text)

            # Detect hierarchical structure
            sections = self.structure_detector.detect_structure(elements)

            # Build complete section tree
            sections = self.structure_detector.build_section_tree(sections)

            return title, sections
        except Exception as e:
            logger.error(f"Error parsing text content: {e}")
            raise ValueError(f"Failed to parse text: {e}") from e

    async def _parse_markdown(
        self, file_path: Path
    ) -> tuple[str, list[DocumentSection]]:
        """Parse a Markdown document.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            Tuple of (document_title, list_of_sections).
        """
        # Read the file content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Extract title from first header or filename
        title = self._extract_title_from_markdown(content) or file_path.stem

        # Parse the content
        return await self.parse_text(content, title)

    async def _parse_with_docling(
        self, file_path: Path
    ) -> tuple[str, list[DocumentSection]]:
        """Parse a document using docling library.

        Args:
            file_path: Path to the document file.

        Returns:
            Tuple of (document_title, list_of_sections).
        """
        if not DOCLING_AVAILABLE or not self._docling_converter:
            raise ValueError("Docling not available for parsing")

        logger.info(f"Using docling to parse: {file_path}")

        try:
            # Convert document using docling
            conv_results = list(self._docling_converter.convert_all([file_path]))

            if not conv_results:
                raise ValueError("No conversion results from docling")

            # Get the first (and should be only) result
            result = conv_results[0]

            if result.status == ConversionStatus.SUCCESS:
                # Export to markdown for consistent processing
                markdown_content = result.document.export_to_markdown()

                # Try to extract title from markdown content (H1 header) or use filename as fallback
                document_title = self._extract_title_from_markdown(markdown_content)
                if not document_title:
                    # Fallback to document name or filename
                    document_title = result.document.name or file_path.stem

                # Parse the markdown content using our existing parser
                return await self.parse_text(markdown_content, document_title)
            else:
                raise ValueError(
                    f"Docling conversion failed with status: {result.status}"
                )

        except Exception as e:
            logger.error(f"Docling parsing failed for {file_path}: {e}")
            # Fallback to basic parsing if it's a markdown file
            if file_path.suffix.lower() in {".md", ".markdown"}:
                logger.info("Falling back to basic Markdown parsing")
                return await self._parse_markdown(file_path)
            else:
                raise ValueError(f"Failed to parse with docling: {e}") from e

    def _extract_title_from_markdown(self, content: str) -> str | None:
        """Extract document title from Markdown content.

        Args:
            content: Raw Markdown content.

        Returns:
            Document title if found, None otherwise.
        """
        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()

        return None

    def _extract_markdown_elements(self, content: str) -> list[dict[str, Any]]:
        """Extract structural elements from Markdown content.

        This is a simplified implementation for MVP. In future phases,
        this will be replaced with full docling integration.

        Args:
            content: Raw Markdown content.

        Returns:
            List of element dictionaries with type, text, and level.
        """
        elements = []
        lines = content.split("\n")
        current_paragraph: list[str] = []

        for line in lines:
            stripped_line = line.strip()

            # Process current paragraph if we hit a header or empty line
            if (
                stripped_line.startswith("#") or not stripped_line
            ) and current_paragraph:
                paragraph_text = "\n".join(current_paragraph).strip()
                if paragraph_text:
                    elements.append(
                        {"type": "paragraph", "text": paragraph_text, "level": 0}
                    )
                current_paragraph = []

            if not stripped_line:
                continue

            # Headers
            if stripped_line.startswith("#"):
                level = len(stripped_line) - len(stripped_line.lstrip("#"))
                title = stripped_line.lstrip("#").strip()
                elements.append(
                    {"type": f"heading_{level}", "text": title, "level": level}
                )

            # Lists (simplified)
            elif stripped_line.startswith(
                ("- ", "* ", "+ ")
            ) or stripped_line.startswith(tuple(f"{i}. " for i in range(10))):
                elements.append(
                    {"type": "list_item", "text": stripped_line, "level": 0}
                )

            # Code blocks (simplified)
            elif stripped_line.startswith("```"):
                elements.append(
                    {"type": "code_block", "text": stripped_line, "level": 0}
                )

            # Regular content - accumulate into paragraphs
            else:
                current_paragraph.append(line)

        # Handle final paragraph
        if current_paragraph:
            paragraph_text = "\n".join(current_paragraph).strip()
            if paragraph_text:
                elements.append(
                    {"type": "paragraph", "text": paragraph_text, "level": 0}
                )

        return elements

    def get_supported_formats(self) -> set[str]:
        """Get the set of supported file extensions.

        Returns:
            Set of supported file extensions (including the dot).
            When docling available: {'.md', '.markdown', '.pdf', '.docx', '.html'}
            Fallback mode: {'.md', '.markdown'}
        """
        return self._supported_extensions.copy()

    def is_docling_available(self) -> bool:
        """Check if docling library is available for enhanced parsing.

        Returns:
            True if docling is available and configured.
        """
        return DOCLING_AVAILABLE and self._docling_converter is not None

    def get_parser_info(self) -> dict[str, Any]:
        """Get information about the current parser configuration.

        Returns:
            Dictionary with parser status and capabilities.
        """
        return {
            "docling_available": DOCLING_AVAILABLE,
            "docling_configured": self._docling_converter is not None,
            "supported_formats": list(self._supported_extensions),
            "enhanced_parsing": self.is_docling_available(),
            "fallback_mode": not self.is_docling_available(),
        }
