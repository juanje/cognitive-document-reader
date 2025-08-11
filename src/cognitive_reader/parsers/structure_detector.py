"""Hierarchical structure detection for documents."""

from __future__ import annotations

import uuid
from typing import Any

from ..models.document import DocumentSection
from ..utils.text_cleaning import clean_section_title


class StructureDetector:
    """Detects and builds hierarchical document structure.

    This class is responsible for analyzing document elements and
    constructing a hierarchical tree of sections with proper
    parent-child relationships.
    """

    def __init__(self) -> None:
        """Initialize the structure detector."""
        self._section_counter = 0

    def detect_structure(
        self, document_elements: list[dict[str, Any]]
    ) -> list[DocumentSection]:
        """Extract hierarchical sections from document elements.

        Args:
            document_elements: List of document elements from docling parser.

        Returns:
            List of DocumentSection objects representing the document hierarchy.
        """
        if not document_elements:
            return []

        sections = []
        section_stack: list[DocumentSection] = []  # Stack to track hierarchy
        i = 0

        while i < len(document_elements):
            element = document_elements[i]
            element_type = element.get("type", "")
            text = element.get("text", "").strip()
            level = element.get("level", 0)

            if not text:
                i += 1
                continue

            # Create section for headers and significant content blocks
            if element_type.startswith("heading") or self._is_significant_content(
                element
            ):
                # For headers, collect following paragraphs as content
                if element_type.startswith("heading"):
                    header_title = text
                    content_parts = [text]  # Start with header text

                    # Look ahead for paragraphs that belong to this header
                    j = i + 1
                    while j < len(document_elements):
                        next_element = document_elements[j]
                        next_type = next_element.get("type", "")
                        next_text = next_element.get("text", "").strip()

                        # Stop if we hit another header or significant content
                        if (next_type.startswith("heading") or
                            self._is_significant_content(next_element)):
                            break

                        # Add paragraphs and other content to this section
                        if next_text and next_type == "paragraph":
                            content_parts.append(next_text)
                            j += 1
                        else:
                            j += 1

                    # Create section with separated title and content
                    combined_content = "\n\n".join(content_parts)
                    section = self._create_section_with_content(
                        title=header_title,
                        content=combined_content,
                        level=level,
                        element_type=element_type,
                    )

                    # Skip the processed paragraphs
                    i = j
                else:
                    # Non-header significant content
                    section = self._create_section(
                        text=text,
                        level=level + 1,
                        element_type=element_type,
                    )
                    i += 1

                # Update hierarchy relationships
                self._update_hierarchy(section, section_stack)
                sections.append(section)
            else:
                # Skip non-significant content that wasn't grouped with a header
                i += 1

        return sections

    def _create_section(
        self, text: str, level: int, element_type: str
    ) -> DocumentSection:
        """Create a DocumentSection from element data.

        Args:
            text: The text content of the section.
            level: The hierarchical level.
            element_type: The type of document element.

        Returns:
            A new DocumentSection instance.
        """
        self._section_counter += 1
        section_id = f"section_{self._section_counter}_{uuid.uuid4().hex[:8]}"

        # Extract title - for headers it's the text, for content use first line
        if element_type.startswith("heading"):
            title = clean_section_title(text)
            content = clean_section_title(text)  # Clean content too for LLM processing
        else:
            lines = text.split("\n")
            raw_title = lines[0][:100] + "..." if len(lines[0]) > 100 else lines[0]
            title = clean_section_title(raw_title)
            content = clean_section_title(text)  # Clean content too for LLM processing

        return DocumentSection(
            id=section_id,
            title=title,
            content=content,
            level=level,
            order_index=self._section_counter,
            is_heading=element_type.startswith("heading"),
        )

    def _create_section_with_content(
        self, title: str, content: str, level: int, element_type: str
    ) -> DocumentSection:
        """Create a DocumentSection with explicit title and content.

        Args:
            title: The section title (header text only).
            content: The complete section content (header + paragraphs).
            level: The hierarchical level.
            element_type: The type of document element.

        Returns:
            A new DocumentSection instance with separated title and content.
        """
        self._section_counter += 1
        section_id = f"section_{self._section_counter}_{uuid.uuid4().hex[:8]}"

        # Clean title and content separately
        clean_title = clean_section_title(title)
        clean_content = clean_section_title(content)

        return DocumentSection(
            id=section_id,
            title=clean_title,
            content=clean_content,
            level=level,
            order_index=self._section_counter,
            is_heading=element_type.startswith("heading"),
        )

    def _update_hierarchy(
        self, section: DocumentSection, section_stack: list[DocumentSection]
    ) -> None:
        """Update parent-child relationships in the hierarchy.

        Args:
            section: The new section to add to hierarchy.
            section_stack: Stack of current parent sections.
        """
        # Remove sections from stack that are at same or deeper level
        while section_stack and section_stack[-1].level >= section.level:
            section_stack.pop()

        # Set parent if there's a section in the stack
        if section_stack:
            parent = section_stack[-1]
            # Update the parent's children list (we need to modify the section)
            # Since DocumentSection is frozen, we'll handle this in the calling code
            section = section.model_copy(update={"parent_id": parent.id})

        # Add to stack for potential children
        section_stack.append(section)

    def _is_significant_content(self, element: dict[str, Any]) -> bool:
        """Determine if an element represents significant content worth sectioning.

        Args:
            element: Document element to evaluate.

        Returns:
            True if the element should create a new section.
        """
        element_type = element.get("type", "")
        text = element.get("text", "").strip()

        # Only consider true structural elements as standalone sections
        # Paragraphs should NEVER be standalone sections - they belong to their parent section

        # Code blocks and tables can be standalone sections when substantial
        significant_types = {"code_block", "table"}
        min_content_length = 100

        return element_type in significant_types and len(text) >= min_content_length

    def build_section_tree(
        self, sections: list[DocumentSection]
    ) -> list[DocumentSection]:
        """Build complete section tree with proper parent-child relationships.

        Args:
            sections: Flat list of sections to organize into tree.

        Returns:
            List of sections with updated parent-child relationships.
        """
        if not sections:
            return []

        # Create a mapping for quick lookups
        {section.id: section for section in sections}
        updated_sections = []

        for section in sections:
            children_ids = []

            # Find all direct children
            for other_section in sections:
                if other_section.parent_id == section.id:
                    children_ids.append(other_section.id)

            # Update section with children IDs
            updated_section = section.model_copy(update={"children_ids": children_ids})
            updated_sections.append(updated_section)

        return updated_sections
