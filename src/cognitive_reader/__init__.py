"""Cognitive Document Reader - Human-like document understanding.

This library simulates human-like document reading through progressive understanding
and hierarchical synthesis, providing high-quality summaries for human reading
and enriched metadata for AI projects.
"""

from __future__ import annotations

from .core.progressive_reader import CognitiveReader
from .models.config import CognitiveConfig
from .models.document import CognitiveKnowledge, DocumentSection, SectionSummary
from .models.knowledge import LanguageCode

try:
    from ._version import __version__
except ImportError:
    __version__ = "dev"

__all__ = [
    "CognitiveReader",
    "CognitiveConfig",
    "CognitiveKnowledge",
    "DocumentSection",
    "SectionSummary",
    "LanguageCode",
    "__version__",
]
