"""Document structure formatting utilities."""

from __future__ import annotations

import json
from typing import Any

from ..models.document import DocumentSection


def format_structure_as_text(sections: list[DocumentSection], headings_only: bool = False) -> str:
    """Format document structure as clean tree-like hierarchy.

    Args:
        sections: List of document sections in hierarchical order.
        headings_only: If True, only show sections that are real headings (H1, H2, etc.),
                      not paragraph content.

    Returns:
        Clean tree representation of the document structure.

    Examples:
        >>> sections = [
        ...     DocumentSection(id="1", title="Introduction", level=1, order_index=1, is_heading=True),
        ...     DocumentSection(id="2", title="Overview", level=2, order_index=2, is_heading=True),
        ... ]
        >>> print(format_structure_as_text(sections))
        Introduction
          Overview
    """
    if not sections:
        return "(No sections detected)"

    # Filter to only headings if requested
    display_sections = sections
    if headings_only:
        display_sections = [s for s in sections if s.is_heading]
        if not display_sections:
            return "(No headings detected)"

    lines = []

    for section in display_sections:
        # Create indentation based on level (level 1 = no indent, level 2 = 2 spaces, etc.)
        indent = "  " * (section.level - 1) if section.level > 1 else ""

        # Simple format: just the title with appropriate indentation
        line = f"{indent}{section.title}"
        lines.append(line)

    return "\n".join(lines)


def format_structure_as_json(sections: list[DocumentSection]) -> str:
    """Format document structure as JSON for integration.

    Args:
        sections: List of document sections in hierarchical order.

    Returns:
        JSON representation of the document structure.
    """
    structure_data = {
        "document_structure": {
            "total_sections": len(sections),
            "max_depth": max((s.level for s in sections), default=0),
            "sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "level": section.level,
                    "order_index": section.order_index,
                    "parent_id": section.parent_id,
                    "children_count": len(section.children_ids),
                    "has_children": len(section.children_ids) > 0,
                }
                for section in sections
            ]
        }
    }

    return json.dumps(structure_data, indent=2, ensure_ascii=False)


def format_structure_compact(sections: list[DocumentSection]) -> str:
    """Format document structure as compact text for verbose logs.

    Args:
        sections: List of document sections in hierarchical order.

    Returns:
        Compact text representation suitable for logging.

    Examples:
        >>> sections = [DocumentSection(id="1", title="Introduction", level=1, order_index=1)]
        >>> format_structure_compact(sections)
        "Structure: 1 sections, max depth 1 | Introduction"
    """
    if not sections:
        return "Structure: No sections detected"

    total_sections = len(sections)
    max_depth = max((s.level for s in sections), default=0)

    # Create abbreviated section list (first 5 sections, truncate if more)
    section_previews = []
    max_preview = 5
    for i, section in enumerate(sections[:max_preview]):
        # Add simple indentation indicator for levels > 1
        indent_indicator = "→ " * (section.level - 1) if section.level > 1 else ""
        preview = f"{indent_indicator}{section.title}"
        section_previews.append(preview)

    if len(sections) > max_preview:
        section_previews.append(f"... (+{len(sections) - max_preview} more)")

    sections_text = " | ".join(section_previews)

    return f"Structure: {total_sections} sections, max depth {max_depth} | {sections_text}"


def get_structure_summary(sections: list[DocumentSection]) -> dict[str, Any]:
    """Get summary statistics about document structure.

    Args:
        sections: List of document sections.

    Returns:
        Dictionary with structure statistics.
    """
    if not sections:
        return {
            "total_sections": 0,
            "max_depth": 0,
            "sections_by_level": {},
            "has_hierarchy": False
        }

    # Count sections by level
    sections_by_level: dict[int, int] = {}
    for section in sections:
        level = section.level
        sections_by_level[level] = sections_by_level.get(level, 0) + 1

    max_depth = max((s.level for s in sections), default=0)
    has_hierarchy = max_depth > 1

    return {
        "total_sections": len(sections),
        "max_depth": max_depth,
        "sections_by_level": sections_by_level,
        "has_hierarchy": has_hierarchy
    }


def filter_sections_by_depth(
    sections: list[DocumentSection], max_depth: int
) -> list[DocumentSection]:
    """Filter sections by maximum depth level.

    Args:
        sections: List of document sections.
        max_depth: Maximum depth level to include (1-based, so level 1 = top level).

    Returns:
        Filtered list of sections within the depth limit.

    Examples:
        >>> sections = [
        ...     DocumentSection(id="1", title="Chapter", level=1, order_index=1),
        ...     DocumentSection(id="2", title="Section", level=2, order_index=2),
        ...     DocumentSection(id="3", title="Subsection", level=3, order_index=3),
        ... ]
        >>> filtered = filter_sections_by_depth(sections, 2)
        >>> len(filtered)  # Should include only Chapter and Section
        2
    """
    return [section for section in sections if section.level <= max_depth]


def validate_structure_integrity(sections: list[DocumentSection]) -> list[str]:
    """Validate document structure integrity and return any issues found.

    Args:
        sections: List of document sections to validate.

    Returns:
        List of validation issues found (empty if structure is valid).
    """
    issues = []

    if not sections:
        return ["No sections found in document"]

    # Check for gaps in order indices
    order_indices = [s.order_index for s in sections]
    expected_indices = list(range(1, len(sections) + 1))
    if sorted(order_indices) != expected_indices:
        issues.append("Gaps or duplicates found in section order indices")

    # Check for reasonable level progression
    for i, section in enumerate(sections[1:], 1):
        prev_section = sections[i - 1]
        level_jump = section.level - prev_section.level

        # Level increases by more than 1 might indicate missing intermediate levels
        if level_jump > 1:
            issues.append(f"Large level jump from {prev_section.level} to {section.level} "
                         f"at section '{section.title}'")

    # Check for orphaned high-level sections
    if sections and sections[0].level > 1:
        issues.append("Document starts with section level > 1 (no top-level section)")

    return issues
