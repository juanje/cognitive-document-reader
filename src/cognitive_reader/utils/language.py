"""Language detection utilities."""

from __future__ import annotations

import logging

from ..models.knowledge import LanguageCode

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Simple language detection for document processing.

    Provides reliable language detection for supported languages
    with fallback to English for unsupported or ambiguous cases.
    """

    def __init__(self) -> None:
        """Initialize the language detector."""
        self._langdetect_available = True
        try:
            import langdetect  # noqa: F401
        except ImportError:
            logger.warning("langdetect library not available, using fallback detection")
            self._langdetect_available = False

    def detect_language(self, text: str) -> LanguageCode:
        """Detect the primary language of the given text.

        Args:
            text: Text to analyze for language detection.

        Returns:
            Detected language code from supported languages.
        """
        if not text or not text.strip():
            return LanguageCode.EN

        # Try advanced detection if available
        if self._langdetect_available:
            detected = self._detect_with_langdetect(text)
            if detected:
                return detected

        # Fallback to simple heuristic detection
        return self._detect_with_heuristics(text)

    def _detect_with_langdetect(self, text: str) -> LanguageCode | None:
        """Detect language using langdetect library.

        Args:
            text: Text to analyze.

        Returns:
            Detected language code or None if detection fails.
        """
        try:
            from langdetect import DetectorFactory, detect
            from langdetect.lang_detect_exception import LangDetectException

            # Set seed for consistent results
            DetectorFactory.seed = 0

            detected_lang = detect(text)

            # Map to our supported languages
            if detected_lang == "es":
                return LanguageCode.ES
            elif detected_lang == "en":
                return LanguageCode.EN
            else:
                # For unsupported languages, default to English
                logger.info(
                    f"Detected language '{detected_lang}' not supported, defaulting to English"
                )
                return LanguageCode.EN

        except (LangDetectException, ImportError) as e:
            logger.debug(f"Language detection failed: {e}")
            return None

    def _detect_with_heuristics(self, text: str) -> LanguageCode:
        """Detect language using simple heuristics.

        Uses common words and patterns to identify Spanish vs English.
        This is a fallback method when langdetect is not available.

        Args:
            text: Text to analyze.

        Returns:
            Detected language code (defaults to English if uncertain).
        """
        text_lower = text.lower()

        # Common Spanish indicators
        spanish_indicators = [
            "el ",
            "la ",
            "los ",
            "las ",
            "un ",
            "una ",
            "de ",
            "del ",
            "al ",
            "con ",
            "por ",
            "para ",
            "que ",
            "en ",
            "es ",
            "son ",
            "está ",
            "están ",
            "tiene ",
            "tienen ",
            "hacer ",
            "hace ",
            "hacen ",
            "puede ",
            "pueden ",
            "también ",
            "también",
            "además",
            "mientras",
            "durante",
            "después",
            "antes",
            "sobre",
            "entre",
            "bajo",
            "hasta",
            "desde",
            "hacia",
            "según",
        ]

        # Common English indicators
        english_indicators = [
            "the ",
            "and ",
            "or ",
            "but ",
            "with ",
            "for ",
            "to ",
            "of ",
            "in ",
            "on ",
            "at ",
            "by ",
            "from ",
            "up ",
            "about ",
            "into ",
            "through ",
            "is ",
            "are ",
            "was ",
            "were ",
            "have ",
            "has ",
            "had ",
            "do ",
            "does ",
            "did ",
            "will ",
            "would ",
            "could ",
            "should ",
            "can ",
            "may ",
            "might ",
            "this ",
            "that ",
            "these ",
            "those ",
            "which ",
            "what ",
            "when ",
            "where ",
            "why ",
            "how ",
            "who ",
            "whom ",
            "whose ",
        ]

        # Count indicators
        spanish_count = sum(
            1 for indicator in spanish_indicators if indicator in text_lower
        )
        english_count = sum(
            1 for indicator in english_indicators if indicator in text_lower
        )

        # Calculate text length factor (longer text = more reliable)
        text_length = len(text)
        confidence_threshold = max(
            2, text_length // 200
        )  # Minimum 2, scales with text length

        # Determine language based on counts
        if spanish_count >= confidence_threshold and spanish_count > english_count:
            logger.debug(
                f"Heuristic detection: Spanish (score: {spanish_count} vs {english_count})"
            )
            return LanguageCode.ES
        elif english_count >= confidence_threshold:
            logger.debug(
                f"Heuristic detection: English (score: {english_count} vs {spanish_count})"
            )
            return LanguageCode.EN
        else:
            # Default to English if uncertain
            logger.debug(
                f"Heuristic detection: Uncertain (ES: {spanish_count}, EN: {english_count}), defaulting to English"
            )
            return LanguageCode.EN

    def get_supported_languages(self) -> list[LanguageCode]:
        """Get list of supported language codes.

        Returns:
            List of supported language codes.
        """
        return [LanguageCode.EN, LanguageCode.ES]

    def is_supported_language(self, language: LanguageCode) -> bool:
        """Check if a language is supported.

        Args:
            language: Language code to check.

        Returns:
            True if the language is supported.
        """
        return language in self.get_supported_languages()
