"""Tests for language detection utilities."""

from __future__ import annotations

import pytest

from cognitive_reader.models.knowledge import LanguageCode
from cognitive_reader.utils.language import LanguageDetector


@pytest.fixture
def detector():
    """Create language detector instance."""
    return LanguageDetector()


def test_language_detector_init(detector):
    """Test language detector initialization."""
    assert detector is not None
    assert isinstance(detector.get_supported_languages(), list)
    assert LanguageCode.EN in detector.get_supported_languages()
    assert LanguageCode.ES in detector.get_supported_languages()


def test_detect_empty_text(detector):
    """Test detection with empty or whitespace text."""
    assert detector.detect_language("") == LanguageCode.EN
    assert detector.detect_language("   ") == LanguageCode.EN
    assert detector.detect_language("\n\t  ") == LanguageCode.EN


def test_detect_english_text(detector):
    """Test detection of English text."""
    english_texts = [
        "This is a test document in English. It contains several sentences.",
        "The quick brown fox jumps over the lazy dog. This is a common phrase.",
        "Hello world! This is an example of English text for testing purposes.",
        "In this document, we will discuss various topics related to software development.",
    ]

    for text in english_texts:
        result = detector.detect_language(text)
        assert result == LanguageCode.EN, f"Failed to detect English in: {text[:50]}..."


def test_detect_spanish_text(detector):
    """Test detection of Spanish text."""
    spanish_texts = [
        "Este es un documento de prueba en español. Contiene varias oraciones.",
        "Hola mundo! Este es un ejemplo de texto en español para propósitos de prueba.",
        "En este documento, discutiremos varios temas relacionados con el desarrollo de software.",
        "La programación es una disciplina que requiere práctica y dedicación constante.",
    ]

    for text in spanish_texts:
        result = detector.detect_language(text)
        assert result == LanguageCode.ES, f"Failed to detect Spanish in: {text[:50]}..."


def test_detect_mixed_text(detector):
    """Test detection with mixed language content."""
    # Text with both languages - should detect the dominant one
    mixed_text = """
    Este es un documento mixto. This document contains both Spanish and English.
    However, the majority of the content is in Spanish. Por lo tanto, debería
    detectarse como español. La detección de idioma es importante para el
    procesamiento de documentos.
    """

    result = detector.detect_language(mixed_text)
    # Should detect Spanish as dominant (more Spanish words)
    assert result == LanguageCode.ES


def test_detect_short_text(detector):
    """Test detection with short text snippets."""
    # Short texts should still work but may default to English if uncertain
    short_english = "Hello world"
    short_spanish = "Hola mundo"

    # These might not be long enough for reliable detection
    # but should not crash
    result_en = detector.detect_language(short_english)
    result_es = detector.detect_language(short_spanish)

    assert result_en in [LanguageCode.EN, LanguageCode.ES]
    assert result_es in [LanguageCode.EN, LanguageCode.ES]


def test_heuristic_detection_fallback(detector):
    """Test heuristic detection when langdetect is not available."""
    # Force heuristic detection by simulating missing langdetect
    detector._langdetect_available = False

    # Test English indicators
    english_text = "The dog and cat are in the house with their owner."
    result = detector.detect_language(english_text)
    assert result == LanguageCode.EN

    # Test Spanish indicators
    spanish_text = "El perro y el gato están en la casa con su dueño."
    result = detector.detect_language(spanish_text)
    assert result == LanguageCode.ES

    # Reset for other tests
    detector._langdetect_available = True


def test_supported_languages(detector):
    """Test supported languages functionality."""
    supported = detector.get_supported_languages()

    assert isinstance(supported, list)
    assert len(supported) >= 2
    assert LanguageCode.EN in supported
    assert LanguageCode.ES in supported

    # Test language support checking
    assert detector.is_supported_language(LanguageCode.EN) is True
    assert detector.is_supported_language(LanguageCode.ES) is True
    assert detector.is_supported_language(LanguageCode.AUTO) is False


def test_heuristic_detection_details(detector):
    """Test specific heuristic detection logic."""
    detector._langdetect_available = False

    # Test with text that has clear Spanish indicators
    spanish_heavy = (
        "En este documento se presenta la metodología para el análisis de datos."
    )
    result = detector.detect_language(spanish_heavy)
    assert result == LanguageCode.ES

    # Test with text that has clear English indicators
    english_heavy = (
        "This document presents the methodology for data analysis and processing."
    )
    result = detector.detect_language(english_heavy)
    assert result == LanguageCode.EN

    # Test with ambiguous text (should default to English)
    ambiguous = "Data analysis methodology presentation framework."
    result = detector.detect_language(ambiguous)
    assert result == LanguageCode.EN  # Default fallback

    detector._langdetect_available = True


def test_confidence_threshold_scaling(detector):
    """Test that confidence threshold scales with text length."""
    detector._langdetect_available = False

    # Short text with few indicators
    short_text = "El gato"
    result = detector.detect_language(short_text)
    # May not be reliable enough to detect Spanish
    assert result in [LanguageCode.EN, LanguageCode.ES]

    # Longer text with many indicators
    long_text = (
        "El gato está en la casa con el perro y los otros animales que viven allí."
    )
    result = detector.detect_language(long_text)
    assert result == LanguageCode.ES

    detector._langdetect_available = True
