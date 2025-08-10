"""Utility functions."""

from __future__ import annotations

from .language import LanguageDetector
from .structure_formatter import (
    filter_sections_by_depth,
    format_structure_as_json,
    format_structure_as_text,
    format_structure_compact,
    get_structure_summary,
    validate_structure_integrity,
)
from .text_cleaning import clean_markdown_internal_links, clean_section_title

__all__ = [
    "LanguageDetector",
    "clean_markdown_internal_links",
    "clean_section_title",
    "format_structure_as_text",
    "format_structure_as_json",
    "format_structure_compact",
    "get_structure_summary",
    "filter_sections_by_depth",
    "validate_structure_integrity",
]
