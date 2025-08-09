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


def clean_section_title(title: str) -> str:
    """Clean section title by applying various cleaning operations.
    
    This is the main function to clean section titles during document processing.
    Currently handles internal link cleaning, but can be extended for other
    cleaning operations in the future.
    
    Args:
        title: The original section title.
        
    Returns:
        The cleaned title.
        
    Examples:
        >>> clean_section_title("Introduction {#intro}")
        "Introduction"
        >>> clean_section_title("De nómadas a sedentarios {#de-nómadas-a-sedentarios}")
        "De nómadas a sedentarios"
    """
    # Always clean internal links - they don't add value to summaries
    cleaned_title = clean_markdown_internal_links(title)
    
    return cleaned_title
