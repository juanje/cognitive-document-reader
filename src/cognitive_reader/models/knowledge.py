"""Knowledge structures and language definitions."""

from __future__ import annotations

from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes for document processing."""

    AUTO = "auto"
    EN = "en"
    ES = "es"
