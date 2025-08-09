"""Unit tests for text cleaning utilities."""

from __future__ import annotations

import pytest

from cognitive_reader.utils.text_cleaning import (
    clean_markdown_internal_links,
    clean_section_title,
)


class TestCleanMarkdownInternalLinks:
    """Test markdown internal link cleaning functionality."""

    def test_clean_basic_internal_link(self) -> None:
        """Test cleaning basic internal link pattern."""
        text = "## Introduction {#introduction}"
        expected = "## Introduction"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_spanish_example(self) -> None:
        """Test cleaning the specific Spanish example from the issue."""
        text = "## De nómadas a sedentarios {#de-nómadas-a-sedentarios}"
        expected = "## De nómadas a sedentarios"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_link_with_dashes(self) -> None:
        """Test cleaning links with dashes."""
        text = "Title with {#link-with-dashes} here"
        expected = "Title with here"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_link_with_underscores(self) -> None:
        """Test cleaning links with underscores."""
        text = "Title with {#link_with_underscores} here"
        expected = "Title with here"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_multiple_links(self) -> None:
        """Test cleaning multiple internal links."""
        text = "Multiple {#link1} patterns {#link2} in text"
        expected = "Multiple patterns in text"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_link_at_end(self) -> None:
        """Test cleaning link at the end of text."""
        text = "Section title {#section}"
        expected = "Section title"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_link_at_beginning(self) -> None:
        """Test cleaning link at the beginning of text."""
        text = "{#intro} Introduction text"
        expected = "Introduction text"
        assert clean_markdown_internal_links(text) == expected

    def test_preserve_normal_braces(self) -> None:
        """Test that normal braces without # are preserved."""
        text = "Code example: {variable} and {#link}"
        expected = "Code example: {variable} and"
        assert clean_markdown_internal_links(text) == expected

    def test_preserve_text_without_links(self) -> None:
        """Test that text without internal links is unchanged."""
        text = "Normal title without any links"
        expected = "Normal title without any links"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_empty_string(self) -> None:
        """Test cleaning empty string."""
        text = ""
        expected = ""
        assert clean_markdown_internal_links(text) == expected

    def test_clean_whitespace_around_links(self) -> None:
        """Test cleaning with various whitespace patterns."""
        text = "Title   {#link}   with spaces"
        expected = "Title with spaces"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_multiple_spaces_collapsed(self) -> None:
        """Test that multiple spaces are collapsed to single space."""
        text = "Title    {#link1}     {#link2}    end"
        expected = "Title end"
        assert clean_markdown_internal_links(text) == expected

    def test_clean_complex_anchor_names(self) -> None:
        """Test cleaning complex anchor names with numbers and symbols."""
        text = "Section {#section-1.2_example-test} title"
        expected = "Section title"
        assert clean_markdown_internal_links(text) == expected


class TestCleanSectionTitle:
    """Test section title cleaning main function."""

    def test_clean_section_title_basic(self) -> None:
        """Test basic section title cleaning."""
        title = "Introduction {#intro}"
        expected = "Introduction"
        assert clean_section_title(title) == expected

    def test_clean_section_title_multiple_operations(self) -> None:
        """Test that function can be extended for multiple operations."""
        title = "Complex   {#link1}   title   {#link2}   here"
        expected = "Complex title here"
        assert clean_section_title(title) == expected

    def test_clean_section_title_empty(self) -> None:
        """Test cleaning empty section title."""
        title = ""
        expected = ""
        assert clean_section_title(title) == expected

    def test_clean_section_title_no_links(self) -> None:
        """Test section title without links remains unchanged."""
        title = "Normal section title"
        expected = "Normal section title"
        assert clean_section_title(title) == expected

    def test_clean_section_title_markdown_headers(self) -> None:
        """Test cleaning section titles that include markdown header symbols."""
        title = "## Advanced Topics {#advanced-topics}"
        expected = "## Advanced Topics"
        assert clean_section_title(title) == expected

    def test_clean_section_title_with_other_markdown(self) -> None:
        """Test that other markdown elements are preserved."""
        title = "**Bold Title** {#bold} with *emphasis*"
        expected = "**Bold Title** with *emphasis*"
        assert clean_section_title(title) == expected


class TestStructureDetectorIntegration:
    """Test integration of text cleaning with StructureDetector."""

    def test_heading_content_cleaning(self) -> None:
        """Test that both title and content are cleaned for headings."""
        from cognitive_reader.parsers.structure_detector import StructureDetector
        
        detector = StructureDetector()
        
        # Mock document elements with internal links
        elements = [
            {
                "type": "heading_1",
                "text": "## Introduction {#introduction}",
                "level": 1
            }
        ]
        
        sections = detector.detect_structure(elements)
        
        assert len(sections) == 1
        section = sections[0]
        
        # Both title and content should be cleaned
        assert section.title == "## Introduction"
        assert section.content == "## Introduction"
        assert "{#introduction}" not in section.title
        assert "{#introduction}" not in section.content

    def test_paragraph_content_cleaning(self) -> None:
        """Test that both title and content are cleaned for paragraph sections."""
        from cognitive_reader.parsers.structure_detector import StructureDetector
        
        detector = StructureDetector()
        
        # Mock paragraph content with internal links (needs to be >= 50 chars)
        content_with_links = "Short title {#short}. This is some content that also has {#another-link} in the middle. And more text here {#final-link} to meet minimum length requirement."
        
        elements = [
            {
                "type": "paragraph",
                "text": content_with_links,
                "level": 1
            }
        ]
        
        sections = detector.detect_structure(elements)
        
        assert len(sections) == 1
        section = sections[0]
        
        # Title should be cleaned version of first line
        assert section.title.startswith("Short title .")
        assert "{#short}" not in section.title
        assert "{#another-link}" not in section.title
        assert "{#final-link}" not in section.title
        
        # Content should be completely cleaned
        assert "{#another-link}" not in section.content
        assert "{#final-link}" not in section.content
        assert "{#short}" not in section.content
        
        # Verify that the content still makes sense
        assert "Short title" in section.content
        assert "This is some content" in section.content

    def test_complex_link_patterns_in_content(self) -> None:
        """Test cleaning of complex link patterns in content."""
        from cognitive_reader.parsers.structure_detector import StructureDetector
        
        detector = StructureDetector()
        
        # Use heading_2 type to trigger section creation
        complex_content = "## Advanced Topics {#advanced-topics-section} with content about {#link-with-dashes}, {#link_with_underscores}, and {#link123numbers} patterns."
        
        elements = [
            {
                "type": "heading_2", 
                "text": complex_content,
                "level": 2
            }
        ]
        
        sections = detector.detect_structure(elements)
        
        assert len(sections) == 1
        section = sections[0]
        
        # All link patterns should be removed from both title and content
        # Note: clean_section_title collapses whitespace, so multiple spaces become single spaces
        expected_clean = "## Advanced Topics with content about , , and patterns."
        
        assert section.title == expected_clean
        assert section.content == expected_clean
        
        # Verify no link patterns remain
        assert "{#" not in section.title
        assert "{#" not in section.content
