"""Text cleaning utilities for document processing."""

from __future__ import annotations

import re


def clean_markdown_internal_links(title: str) -> str:
    """Remove markdown internal link references from titles.

    Removes patterns like {#anchor-name} that are commonly used for
    internal linking in markdown documents.

    Args:
        title: The original title that may contain internal link references.

    Returns:
        The cleaned title with internal link references removed.

    Examples:
        >>> clean_markdown_internal_links("## Introduction {#introduction}")
        "## Introduction"
        >>> clean_markdown_internal_links("De nómadas a sedentarios {#de-nómadas-a-sedentarios}")
        "De nómadas a sedentarios"
        >>> clean_markdown_internal_links("Normal title without links")
        "Normal title without links"
        >>> clean_markdown_internal_links("Multiple {#link1} patterns {#link2}")
        "Multiple  patterns"
        >>> clean_markdown_internal_links("Title with {#link-with-dashes} and spaces")
        "Title with  and spaces"
    """
    if not title:
        return title

    # Pattern to match markdown internal links: {#...}
    # Matches: {#word}, {#word-with-dashes}, {#word_with_underscores}, etc.
    pattern = r'\s*\{#[^}]+\}\s*'

    # Remove the pattern and clean up extra whitespace
    cleaned = re.sub(pattern, ' ', title)

    # Clean up multiple spaces and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def markdown_to_plain_text(text: str) -> str:
    """Convert markdown text to clean plain text.

    Removes ALL markdown formatting and syntax while preserving the actual text content.
    This is more comprehensive than regex-based approaches and handles edge cases better.

    Args:
        text: Text that may contain markdown formatting.

    Returns:
        The text with all markdown formatting removed.

    Examples:
        >>> markdown_to_plain_text("**Bold text**")
        "Bold text"
        >>> markdown_to_plain_text("[Link text](https://example.com)")
        "Link text"
        >>> markdown_to_plain_text("![Alt text](image.jpg)")
        "Alt text"
        >>> markdown_to_plain_text("# Header 1")
        "Header 1"
        >>> markdown_to_plain_text("- List item")
        "List item"
        >>> markdown_to_plain_text("`Code text` and **bold**")
        "Code text and bold"
    """
    if not text:
        return text

    # Start with the original text
    result = text

    # 1. Remove code blocks first (``` ... ```)
    result = re.sub(r'```[\s\S]*?```', '', result, flags=re.MULTILINE)

    # 2. Remove inline code (` ... `)
    result = re.sub(r'`([^`]+)`', r'\1', result)

    # 3. Remove images ![alt](url) - extract alt text
    result = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', result)

    # 4. Remove links [text](url) - extract link text
    result = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', result)

    # 5. Remove headers (# ## ### etc) - keep text
    result = re.sub(r'^#{1,6}\s*(.*)$', r'\1', result, flags=re.MULTILINE)

    # 6. Remove horizontal rules (--- or ***)
    result = re.sub(r'^[-*_]{3,}$', '', result, flags=re.MULTILINE)

    # 7. Remove list markers (- * + 1. 2.)
    result = re.sub(r'^[\s]*[-*+]\s+', '', result, flags=re.MULTILINE)
    result = re.sub(r'^\s*\d+\.\s+', '', result, flags=re.MULTILINE)

    # 8. Remove blockquote markers (>)
    result = re.sub(r'^>\s*', '', result, flags=re.MULTILINE)

    # 9. Handle escape characters first (before removing formatting)
    result = re.sub(r'\\(.)', r'\1', result)

    # 10. Remove bold and italic formatting - use iterative approach for nested cases
    # Repeat until no more changes (handles nested formatting)
    prev_result = ""
    while prev_result != result:
        prev_result = result

        # Bold+italic combinations first
        result = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', result)
        result = re.sub(r'___(.+?)___', r'\1', result)

        # Bold
        result = re.sub(r'\*\*(.+?)\*\*', r'\1', result)
        result = re.sub(r'__(.+?)__', r'\1', result)

        # Italic
        result = re.sub(r'\*([^*]+?)\*', r'\1', result)
        result = re.sub(r'_([^_]+?)_', r'\1', result)

    # 11. Remove strikethrough
    result = re.sub(r'~~([^~]+)~~', r'\1', result)

    # 12. Remove table syntax (|) and replace with space
    result = re.sub(r'\|', ' ', result)

    # 13. Clean up whitespace
    # Remove empty lines
    result = re.sub(r'\n\s*\n', '\n', result)
    # Normalize spaces
    result = re.sub(r' +', ' ', result)
    # Clean up line breaks followed by spaces
    result = re.sub(r'\n\s+', '\n', result)

    # 14. Final cleanup
    result = result.strip()

    return result


def clean_markdown_formatting(text: str) -> str:
    """Remove markdown formatting marks from text.

    This function is kept for backward compatibility.
    New code should use markdown_to_plain_text() for more comprehensive cleaning.

    Args:
        text: Text that may contain markdown formatting.

    Returns:
        The text with markdown formatting removed.
    """
    return markdown_to_plain_text(text)


def clean_section_title(title: str) -> str:
    """Clean section title by applying various cleaning operations.

    This is the main function to clean section titles during document processing.
    Removes all markdown formatting and internal links for clean, consistent titles.

    Args:
        title: The original section title.

    Returns:
        The cleaned title with all markdown formatting and internal links removed.

    Examples:
        >>> clean_section_title("**Introduction** {#intro}")
        "Introduction"
        >>> clean_section_title("*De nómadas* a sedentarios {#de-nómadas-a-sedentarios}")
        "De nómadas a sedentarios"
        >>> clean_section_title("# Header with **bold** and [link](url)")
        "Header with bold and link"
    """
    if not title:
        return title

    # First clean internal links - they don't add value to summaries
    cleaned_title = clean_markdown_internal_links(title)

    # Then clean all markdown formatting comprehensively
    cleaned_title = markdown_to_plain_text(cleaned_title)

    return cleaned_title
