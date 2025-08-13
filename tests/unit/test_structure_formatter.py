"""Unit tests for structure formatting utilities."""

from __future__ import annotations

import json

from cognitive_reader.models.document import DocumentSection
from cognitive_reader.utils.structure_formatter import (
    filter_sections_by_depth,
    format_structure_as_json,
    format_structure_as_text,
    format_structure_compact,
    get_structure_summary,
    validate_structure_integrity,
)


class TestFormatStructureAsText:
    """Test text formatting of document structure."""

    def test_format_empty_structure(self) -> None:
        """Test formatting empty structure."""
        sections: list[DocumentSection] = []
        result = format_structure_as_text(sections)

        expected = "(No sections detected)"
        assert result == expected

    def test_format_single_section(self) -> None:
        """Test formatting single section."""
        sections = [
            DocumentSection(
                id="section_1",
                title="Introduction",
                content="Intro content",
                level=1,
                order_index=1,
                is_heading=True,
            )
        ]

        result = format_structure_as_text(sections)

        expected = "Introduction"
        assert result == expected

    def test_format_hierarchical_structure(self) -> None:
        """Test formatting hierarchical structure."""
        sections = [
            DocumentSection(
                id="section_1",
                title="Chapter 1",
                content="Chapter content",
                level=1,
                order_index=1,
            ),
            DocumentSection(
                id="section_2",
                title="Section 1.1",
                content="Section content",
                level=2,
                order_index=2,
                parent_id="section_1",
            ),
            DocumentSection(
                id="section_3",
                title="Section 1.2",
                content="Section content",
                level=2,
                order_index=3,
                parent_id="section_1",
            ),
            DocumentSection(
                id="section_4",
                title="Chapter 2",
                content="Chapter content",
                level=1,
                order_index=4,
            ),
        ]

        result = format_structure_as_text(sections)

        expected_lines = [
            "Chapter 1",
            "  Section 1.1",
            "  Section 1.2",
            "Chapter 2",
        ]
        expected = "\n".join(expected_lines)

        assert result == expected

    def test_format_deep_hierarchy(self) -> None:
        """Test formatting deep hierarchical structure."""
        sections = [
            DocumentSection(
                id="1", title="Level 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Level 2", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Level 3", content="", level=3, order_index=3
            ),
        ]

        result = format_structure_as_text(sections)

        expected_lines = [
            "Level 1",
            "  Level 2",
            "    Level 3",
        ]
        expected = "\n".join(expected_lines)

        assert result == expected

    def test_format_with_cleaned_titles(self) -> None:
        """Test that cleaned titles are displayed correctly."""
        sections = [
            DocumentSection(
                id="section_1",
                title="Introduction",  # Already cleaned by structure detector
                content="Introduction {#intro}",  # Content may still have original
                level=1,
                order_index=1,
            )
        ]

        result = format_structure_as_text(sections)

        # Should show cleaned title, not content
        assert result == "Introduction"
        assert "{#intro}" not in result

    def test_format_headings_only_filter(self) -> None:
        """Test filtering to show only headings, not content sections."""
        sections = [
            DocumentSection(
                id="1",
                title="Chapter 1",
                content="",
                level=1,
                order_index=1,
                is_heading=True,
            ),
            DocumentSection(
                id="2",
                title="Some paragraph content here...",
                content="",
                level=1,
                order_index=2,
                is_heading=False,
            ),
            DocumentSection(
                id="3",
                title="Section 1.1",
                content="",
                level=2,
                order_index=3,
                is_heading=True,
            ),
            DocumentSection(
                id="4",
                title="Another paragraph...",
                content="",
                level=2,
                order_index=4,
                is_heading=False,
            ),
        ]

        # Without filter - shows all sections
        result_all = format_structure_as_text(sections, headings_only=False)
        assert "Chapter 1" in result_all
        assert "Some paragraph content here..." in result_all
        assert "Section 1.1" in result_all
        assert "Another paragraph..." in result_all

        # With filter - shows only headings
        result_headings = format_structure_as_text(sections, headings_only=True)
        assert "Chapter 1" in result_headings
        assert "Section 1.1" in result_headings
        assert "Some paragraph content here..." not in result_headings
        assert "Another paragraph..." not in result_headings

        # Structure should be clean
        expected_lines = ["Chapter 1", "  Section 1.1"]
        assert result_headings == "\n".join(expected_lines)

    def test_format_headings_only_empty(self) -> None:
        """Test headings_only filter when no headings exist."""
        sections = [
            DocumentSection(
                id="1",
                title="Some content",
                content="",
                level=1,
                order_index=1,
                is_heading=False,
            ),
            DocumentSection(
                id="2",
                title="More content",
                content="",
                level=1,
                order_index=2,
                is_heading=False,
            ),
        ]

        result = format_structure_as_text(sections, headings_only=True)
        assert result == "(No headings detected)"


class TestFormatStructureAsJson:
    """Test JSON formatting of document structure."""

    def test_format_empty_structure_json(self) -> None:
        """Test JSON formatting of empty structure."""
        sections: list[DocumentSection] = []
        result = format_structure_as_json(sections)

        parsed = json.loads(result)

        assert parsed["document_structure"]["total_sections"] == 0
        assert parsed["document_structure"]["max_depth"] == 0
        assert parsed["document_structure"]["sections"] == []

    def test_format_single_section_json(self) -> None:
        """Test JSON formatting of single section."""
        sections = [
            DocumentSection(
                id="section_1",
                title="Introduction",
                content="Intro content",
                level=1,
                order_index=1,
                children_ids=["child_1", "child_2"],
            )
        ]

        result = format_structure_as_json(sections)
        parsed = json.loads(result)

        structure = parsed["document_structure"]
        assert structure["total_sections"] == 1
        assert structure["max_depth"] == 1

        section_data = structure["sections"][0]
        assert section_data["id"] == "section_1"
        assert section_data["title"] == "Introduction"
        assert section_data["level"] == 1
        assert section_data["order_index"] == 1
        assert section_data["children_count"] == 2
        assert section_data["has_children"] is True

    def test_format_hierarchical_structure_json(self) -> None:
        """Test JSON formatting of hierarchical structure."""
        sections = [
            DocumentSection(
                id="section_1", title="Chapter 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="section_2",
                title="Section 1.1",
                content="",
                level=2,
                order_index=2,
                parent_id="section_1",
            ),
        ]

        result = format_structure_as_json(sections)
        parsed = json.loads(result)

        structure = parsed["document_structure"]
        assert structure["total_sections"] == 2
        assert structure["max_depth"] == 2

        # Check parent section
        parent = structure["sections"][0]
        assert parent["level"] == 1
        assert parent["has_children"] is False  # children_ids is empty in this test

        # Check child section
        child = structure["sections"][1]
        assert child["level"] == 2
        assert child["parent_id"] == "section_1"


class TestFormatStructureCompact:
    """Test compact formatting for verbose logs."""

    def test_format_empty_structure_compact(self) -> None:
        """Test compact formatting of empty structure."""
        sections: list[DocumentSection] = []
        result = format_structure_compact(sections)

        assert result == "Structure: No sections detected"

    def test_format_single_section_compact(self) -> None:
        """Test compact formatting of single section."""
        sections = [
            DocumentSection(
                id="1", title="Introduction", content="", level=1, order_index=1
            )
        ]

        result = format_structure_compact(sections)

        expected = "Structure: 1 sections, max depth 1 | Introduction"
        assert result == expected

    def test_format_multiple_sections_compact(self) -> None:
        """Test compact formatting with multiple sections."""
        sections = [
            DocumentSection(
                id="1", title="Chapter 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 1.1", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Section 1.2", content="", level=2, order_index=3
            ),
            DocumentSection(
                id="4", title="Chapter 2", content="", level=1, order_index=4
            ),
        ]

        result = format_structure_compact(sections)

        expected = "Structure: 4 sections, max depth 2 | Chapter 1 | → Section 1.1 | → Section 1.2 | Chapter 2"
        assert result == expected

    def test_format_many_sections_truncated(self) -> None:
        """Test compact formatting truncates when too many sections."""
        sections = [
            DocumentSection(
                id=f"{i}", title=f"Section {i}", content="", level=1, order_index=i
            )
            for i in range(1, 8)  # 7 sections
        ]

        result = format_structure_compact(sections)

        assert "Structure: 7 sections, max depth 1" in result
        assert "Section 1" in result
        assert "Section 2" in result
        assert "Section 3" in result
        assert "Section 4" in result
        assert "Section 5" in result
        assert "... (+2 more)" in result
        assert "Section 6" not in result  # Should be truncated
        assert "Section 7" not in result  # Should be truncated


class TestGetStructureSummary:
    """Test structure summary statistics."""

    def test_empty_structure_summary(self) -> None:
        """Test summary of empty structure."""
        sections: list[DocumentSection] = []
        summary = get_structure_summary(sections)

        expected = {
            "total_sections": 0,
            "max_depth": 0,
            "sections_by_level": {},
            "has_hierarchy": False,
        }
        assert summary == expected

    def test_flat_structure_summary(self) -> None:
        """Test summary of flat structure."""
        sections = [
            DocumentSection(
                id="1", title="Section 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 2", content="", level=1, order_index=2
            ),
        ]

        summary = get_structure_summary(sections)

        expected = {
            "total_sections": 2,
            "max_depth": 1,
            "sections_by_level": {1: 2},
            "has_hierarchy": False,
        }
        assert summary == expected

    def test_hierarchical_structure_summary(self) -> None:
        """Test summary of hierarchical structure."""
        sections = [
            DocumentSection(
                id="1", title="Chapter", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 1", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Section 2", content="", level=2, order_index=3
            ),
            DocumentSection(
                id="4", title="Subsection", content="", level=3, order_index=4
            ),
        ]

        summary = get_structure_summary(sections)

        expected = {
            "total_sections": 4,
            "max_depth": 3,
            "sections_by_level": {1: 1, 2: 2, 3: 1},
            "has_hierarchy": True,
        }
        assert summary == expected


class TestValidateStructureIntegrity:
    """Test structure validation functionality."""

    def test_validate_empty_structure(self) -> None:
        """Test validation of empty structure."""
        sections: list[DocumentSection] = []
        issues = validate_structure_integrity(sections)

        assert len(issues) == 1
        assert "No sections found" in issues[0]

    def test_validate_valid_structure(self) -> None:
        """Test validation of valid structure."""
        sections = [
            DocumentSection(
                id="1", title="Chapter 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 1.1", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Chapter 2", content="", level=1, order_index=3
            ),
        ]

        issues = validate_structure_integrity(sections)

        assert len(issues) == 0

    def test_validate_gap_in_order_indices(self) -> None:
        """Test validation detects gaps in order indices."""
        sections = [
            DocumentSection(
                id="1", title="Section 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 3", content="", level=1, order_index=3
            ),  # Gap: missing 2
        ]

        issues = validate_structure_integrity(sections)

        assert len(issues) >= 1
        assert any("order indices" in issue for issue in issues)

    def test_validate_large_level_jump(self) -> None:
        """Test validation detects large level jumps."""
        sections = [
            DocumentSection(
                id="1", title="Chapter", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Deep section", content="", level=4, order_index=2
            ),  # Jump from 1 to 4
        ]

        issues = validate_structure_integrity(sections)

        assert len(issues) >= 1
        assert any("Large level jump" in issue for issue in issues)

    def test_validate_starts_with_high_level(self) -> None:
        """Test validation detects document starting with high level."""
        sections = [
            DocumentSection(
                id="1", title="Subsection", content="", level=3, order_index=1
            ),  # Starts with level 3
        ]

        issues = validate_structure_integrity(sections)

        assert len(issues) >= 1
        assert any("starts with section level > 1" in issue for issue in issues)


class TestFilterSectionsByDepth:
    """Test filtering sections by depth level."""

    def test_filter_empty_sections(self) -> None:
        """Test filtering empty list of sections."""
        sections: list[DocumentSection] = []
        result = filter_sections_by_depth(sections, 2)

        assert result == []

    def test_filter_single_level(self) -> None:
        """Test filtering with single level sections."""
        sections = [
            DocumentSection(
                id="1", title="Section 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 2", content="", level=1, order_index=2
            ),
        ]

        result = filter_sections_by_depth(sections, 1)

        assert len(result) == 2
        assert all(section.level <= 1 for section in result)

    def test_filter_hierarchical_structure(self) -> None:
        """Test filtering hierarchical structure."""
        sections = [
            DocumentSection(
                id="1", title="Chapter 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Section 1.1", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Subsection 1.1.1", content="", level=3, order_index=3
            ),
            DocumentSection(
                id="4", title="Subsection 1.1.2", content="", level=3, order_index=4
            ),
            DocumentSection(
                id="5", title="Section 1.2", content="", level=2, order_index=5
            ),
            DocumentSection(
                id="6", title="Chapter 2", content="", level=1, order_index=6
            ),
        ]

        # Filter to depth 2 (should include levels 1 and 2 only)
        result = filter_sections_by_depth(sections, 2)

        assert len(result) == 4  # Chapter 1, Section 1.1, Section 1.2, Chapter 2
        assert all(section.level <= 2 for section in result)
        assert "Chapter 1" in [s.title for s in result]
        assert "Section 1.1" in [s.title for s in result]
        assert "Section 1.2" in [s.title for s in result]
        assert "Chapter 2" in [s.title for s in result]
        assert "Subsection 1.1.1" not in [s.title for s in result]
        assert "Subsection 1.1.2" not in [s.title for s in result]

    def test_filter_deep_hierarchy(self) -> None:
        """Test filtering very deep hierarchy."""
        sections = [
            DocumentSection(
                id="1", title="Level 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Level 2", content="", level=2, order_index=2
            ),
            DocumentSection(
                id="3", title="Level 3", content="", level=3, order_index=3
            ),
            DocumentSection(
                id="4", title="Level 4", content="", level=4, order_index=4
            ),
            DocumentSection(
                id="5", title="Level 5", content="", level=5, order_index=5
            ),
        ]

        # Filter to depth 3
        result = filter_sections_by_depth(sections, 3)

        assert len(result) == 3
        assert [s.title for s in result] == ["Level 1", "Level 2", "Level 3"]

    def test_filter_preserves_order(self) -> None:
        """Test that filtering preserves the original order."""
        sections = [
            DocumentSection(id="1", title="A", content="", level=1, order_index=1),
            DocumentSection(id="2", title="B", content="", level=3, order_index=2),
            DocumentSection(id="3", title="C", content="", level=2, order_index=3),
            DocumentSection(id="4", title="D", content="", level=1, order_index=4),
            DocumentSection(id="5", title="E", content="", level=3, order_index=5),
        ]

        result = filter_sections_by_depth(sections, 2)

        # Should preserve original order: A, C, D
        assert len(result) == 3
        assert [s.title for s in result] == ["A", "C", "D"]
        assert [s.order_index for s in result] == [1, 3, 4]

    def test_filter_max_depth_higher_than_any_level(self) -> None:
        """Test filtering with max_depth higher than any section level."""
        sections = [
            DocumentSection(
                id="1", title="Level 1", content="", level=1, order_index=1
            ),
            DocumentSection(
                id="2", title="Level 2", content="", level=2, order_index=2
            ),
        ]

        result = filter_sections_by_depth(sections, 10)

        # Should return all sections when max_depth is higher than any level
        assert len(result) == 2
        assert result == sections
