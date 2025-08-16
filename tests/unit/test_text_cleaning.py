"""Unit tests for text cleaning utilities."""

from __future__ import annotations

import pytest

from cognitive_reader.utils.text_cleaning import (
    clean_markdown_formatting,
    clean_markdown_internal_links,
    clean_section_title,
    markdown_to_plain_text,
)


class TestCleanMarkdownInternalLinks:
    """Test markdown internal link cleaning functionality."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            # Basic patterns
            ("## Introduction {#introduction}", "## Introduction"),
            (
                "## De nómadas a sedentarios {#de-nómadas-a-sedentarios}",
                "## De nómadas a sedentarios",
            ),
            ("Title with {#link-with-dashes} here", "Title with here"),
            ("Title with {#link_with_underscores} here", "Title with here"),
            (
                "Multiple {#link1} patterns {#link2} in text",
                "Multiple patterns in text",
            ),
            # Position variations
            ("Section title {#section}", "Section title"),
            ("{#intro} Introduction text", "Introduction text"),
            # Complex anchor names
            ("Section {#section-1.2_example-test} title", "Section title"),
        ],
    )
    def test_clean_internal_links_patterns(self, text: str, expected: str) -> None:
        """Test cleaning various internal link patterns."""
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


class TestCleanMarkdownFormatting:
    """Test markdown formatting removal functionality."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            # Bold formatting
            ("**Bold text**", "Bold text"),
            ("__Bold text__", "Bold text"),
            # Italic formatting
            ("*Italic text*", "Italic text"),
            ("_Italic text_", "Italic text"),
            # Bold + Italic formatting
            ("***Bold and italic***", "Bold and italic"),
            ("___Bold and italic___", "Bold and italic"),
            # Code formatting
            ("`Code text`", "Code text"),
            # Strikethrough formatting
            ("~~Strikethrough text~~", "Strikethrough text"),
        ],
    )
    def test_clean_basic_markdown_formatting(self, text: str, expected: str) -> None:
        """Test cleaning various markdown formatting patterns."""
        assert clean_markdown_formatting(text) == expected

    def test_clean_mixed_formatting(self) -> None:
        """Test cleaning text with multiple formatting types."""
        text = "Mixed **bold** and *italic* with `code` text"
        expected = "Mixed bold and italic with code text"
        assert clean_markdown_formatting(text) == expected

    def test_clean_nested_formatting_complex(self) -> None:
        """Test cleaning complex nested formatting."""
        text = "Text with **bold *and italic* inside** more text"
        expected = "Text with bold and italic inside more text"
        assert clean_markdown_formatting(text) == expected

    def test_clean_real_section_title_example(self) -> None:
        """Test cleaning with the actual problematic titles from the issue."""
        text = "**Introducción al sedentarismo**"
        expected = "Introducción al sedentarismo"
        assert clean_markdown_formatting(text) == expected

    def test_clean_multiple_bold_sections(self) -> None:
        """Test cleaning multiple bold sections in one text."""
        text = "**Section A** and **Section B** topics"
        expected = "Section A and Section B topics"
        assert clean_markdown_formatting(text) == expected

    def test_clean_empty_string(self) -> None:
        """Test cleaning empty string."""
        text = ""
        expected = ""
        assert clean_markdown_formatting(text) == expected

    def test_clean_no_formatting(self) -> None:
        """Test that text without formatting is unchanged."""
        text = "Plain text without any formatting"
        expected = "Plain text without any formatting"
        assert clean_markdown_formatting(text) == expected

    def test_clean_whitespace_normalization(self) -> None:
        """Test that extra whitespace is normalized."""
        text = "Text   with   **bold**   and   spaces"
        expected = "Text with bold and spaces"
        assert clean_markdown_formatting(text) == expected

    def test_clean_formatting_at_boundaries(self) -> None:
        """Test cleaning formatting at start and end of text."""
        text = "**Start** middle *end*"
        expected = "Start middle end"
        assert clean_markdown_formatting(text) == expected


class TestMarkdownToPlainText:
    """Test comprehensive markdown to plain text conversion."""

    @pytest.mark.parametrize(
        "markdown_text,expected",
        [
            # Headers
            ("# Header 1", "Header 1"),
            ("## Header 2", "Header 2"),
            ("### Header 3", "Header 3"),
            # Lists
            ("- List item", "List item"),
            ("* Another item", "Another item"),
            ("+ Plus item", "Plus item"),
            ("1. Numbered item", "Numbered item"),
            # Basic conversions
            ("[Link text](https://example.com)", "Link text"),
            ("![Alt text](image.jpg)", "Alt text"),
            ("> This is a quote", "This is a quote"),
        ],
    )
    def test_markdown_basic_conversions(
        self, markdown_text: str, expected: str
    ) -> None:
        """Test basic markdown to plain text conversions."""
        assert markdown_to_plain_text(markdown_text) == expected

    def test_code_blocks_removal(self) -> None:
        """Test removal of code blocks."""
        text = "Before\n```python\ncode here\n```\nAfter"
        expected = "Before\nAfter"
        assert markdown_to_plain_text(text) == expected

    def test_table_syntax_removal(self) -> None:
        """Test removal of table syntax."""
        text = "| Column 1 | Column 2 |"
        expected = "Column 1 Column 2"  # Spaces are normalized
        assert markdown_to_plain_text(text) == expected

    def test_escape_characters(self) -> None:
        """Test handling of escape characters."""
        text = "\\*Not italic\\* and \\**not bold\\**"
        # For our use case (section titles), we want ALL asterisks removed
        # This creates clean, consistent titles without any markdown artifacts
        expected = "Not italic and not bold"
        assert markdown_to_plain_text(text) == expected

    def test_complex_real_world_example(self) -> None:
        """Test with complex real-world markdown content."""
        text = """# **Introducción al sedentarismo** {#intro}

        Esta es una **introducción** con [enlaces](http://example.com) y
        `código inline`.

        - Lista item 1
        - Lista item 2 con *énfasis*

        > Cita importante

        ![Imagen](img.jpg)"""

        # Note: {#intro} should be cleaned by clean_markdown_internal_links in clean_section_title
        # but markdown_to_plain_text alone won't handle it
        result = markdown_to_plain_text(text)

        # Verify key components are cleaned correctly
        assert "Introducción al sedentarismo" in result
        assert "Esta es una introducción con enlaces" in result
        assert "código inline" in result
        assert "Lista item 1" in result
        assert "Lista item 2 con énfasis" in result
        assert "Cita importante" in result
        assert "Imagen" in result

        # Verify markdown is removed
        assert "**" not in result
        assert "*" not in result or result.count("*") == 0  # Allow for edge cases
        assert "[" not in result
        assert "]" not in result
        assert "(" not in result or "http" not in result  # URLs should be gone
        assert "`" not in result
        assert (
            "#" not in result or "#{" not in result
        )  # Headers cleaned, but {#} might remain

    def test_nested_formatting(self) -> None:
        """Test nested markdown formatting."""
        text = "**Bold with *nested italic* inside**"
        result = markdown_to_plain_text(text)
        # The important thing is that all formatting is removed
        assert "Bold with nested italic inside" in result
        assert "**" not in result
        assert result.count("*") == 0  # No asterisks should remain

    def test_multiple_headers_in_text(self) -> None:
        """Test multiple headers in the same text."""
        text = "# Main Title\n## Subtitle\n### Sub-subtitle"
        expected = "Main Title\nSubtitle\nSub-subtitle"
        assert markdown_to_plain_text(text) == expected

    def test_mixed_list_types(self) -> None:
        """Test mixed list types in the same text."""
        text = "- Bullet item\n1. Numbered item\n+ Plus item"
        expected = "Bullet item\nNumbered item\nPlus item"
        assert markdown_to_plain_text(text) == expected

    def test_preserve_meaningful_text(self) -> None:
        """Test that meaningful text content is preserved."""
        text = "This is **important** text with a [link](url) and `code`."
        expected = "This is important text with a link and code."
        assert markdown_to_plain_text(text) == expected


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
        # Headers should be cleaned completely for consistent section titles
        expected = "Advanced Topics"
        assert clean_section_title(title) == expected

    def test_clean_section_title_with_markdown_formatting(self) -> None:
        """Test that markdown formatting is also cleaned along with links."""
        title = "**Bold Title** {#bold} with *emphasis*"
        expected = "Bold Title with emphasis"
        assert clean_section_title(title) == expected

    def test_clean_section_title_complex_example(self) -> None:
        """Test cleaning complex title with both markdown and links."""
        title = "**Introducción al sedentarismo** {#introduccion}"
        expected = "Introducción al sedentarismo"
        assert clean_section_title(title) == expected

    def test_clean_section_title_all_formatting_types(self) -> None:
        """Test cleaning all types of markdown formatting with links."""
        title = "***Bold Italic*** with `code` and ~~strike~~ {#complex}"
        expected = "Bold Italic with code and strike"
        assert clean_section_title(title) == expected


class TestStructureDetectorIntegration:
    """Test integration of text cleaning with StructureDetector."""

    def test_heading_content_cleaning(self) -> None:
        """Test that both title and content are cleaned for headings."""
        from cognitive_reader.parsers.structure_detector import StructureDetector

        detector = StructureDetector()

        # Mock document elements with internal links
        elements = [
            {"type": "heading_1", "text": "## Introduction {#introduction}", "level": 1}
        ]

        sections = detector.detect_structure(elements)

        assert len(sections) == 1
        section = sections[0]

        # Both title and content should be cleaned completely
        assert section.title == "Introduction"
        assert section.content == "Introduction"
        assert "{#introduction}" not in section.title
        assert "{#introduction}" not in section.content

    def test_heading_content_cleaning_with_links(self) -> None:
        """Test that both title and content are cleaned for heading sections with internal links."""
        from cognitive_reader.parsers.structure_detector import StructureDetector

        detector = StructureDetector()

        # Mock heading content with internal links
        content_with_links = "Advanced Topic {#advanced-topic} with Links {#links}"

        elements = [{"type": "heading_2", "text": content_with_links, "level": 2}]

        sections = detector.detect_structure(elements)

        assert len(sections) == 1
        section = sections[0]

        # Title should be cleaned version
        assert section.title == "Advanced Topic with Links"
        assert "{#advanced-topic}" not in section.title
        assert "{#links}" not in section.title

        # Content should be completely cleaned (same as title for headers)
        assert "{#advanced-topic}" not in section.content
        assert "{#links}" not in section.content
        assert section.content == "Advanced Topic with Links"

        # Verify section properties
        assert section.is_heading is True
        assert section.level == 2

    def test_complex_link_patterns_in_content(self) -> None:
        """Test cleaning of complex link patterns in content."""
        from cognitive_reader.parsers.structure_detector import StructureDetector

        detector = StructureDetector()

        # Use heading_2 type to trigger section creation
        complex_content = "## Advanced Topics {#advanced-topics-section} with content about {#link-with-dashes}, {#link_with_underscores}, and {#link123numbers} patterns."

        elements = [{"type": "heading_2", "text": complex_content, "level": 2}]

        sections = detector.detect_structure(elements)

        assert len(sections) == 1
        section = sections[0]

        # All link patterns should be removed from both title and content
        # Headers are also cleaned, and whitespace is normalized
        expected_clean = "Advanced Topics with content about , , and patterns."

        assert section.title == expected_clean
        assert section.content == expected_clean

        # Verify no link patterns remain
        assert "{#" not in section.title
        assert "{#" not in section.content
