"""Token estimation utilities."""

from __future__ import annotations


def estimate_tokens_from_words(word_count: int) -> int:
    """Estimate token count from word count.

    Based on empirical analysis of different encodings (cl100k_base, p50k_base, etc.)
    with English and Spanish text samples. Factor 1.3 provides good balance and
    includes safety margin for different languages and tokenizers.

    Args:
        word_count: Number of words in the text

    Returns:
        Estimated number of tokens

    Examples:
        >>> estimate_tokens_from_words(100)
        130
        >>> estimate_tokens_from_words(250)  # Target summary length
        325
    """
    return int(word_count * 1.3)


def estimate_words_from_tokens(token_count: int) -> int:
    """Estimate word count from token count.

    Inverse of estimate_tokens_from_words using factor ~0.77 (1/1.3).

    Args:
        token_count: Number of tokens

    Returns:
        Estimated number of words

    Examples:
        >>> estimate_words_from_tokens(130)
        100
        >>> estimate_words_from_tokens(325)
        250
    """
    return int(token_count / 1.3)


def get_context_usage_info(prompt: str, context_window: int) -> tuple[int, float]:
    """Get context usage information for a prompt.

    Args:
        prompt: The text prompt to analyze
        context_window: Maximum context window size in tokens

    Returns:
        Tuple of (estimated_tokens, usage_percentage)

    Examples:
        >>> tokens, usage = get_context_usage_info("Hello world test", 4096)
        >>> tokens
        4
        >>> usage  # percentage
        0.1
    """
    word_count = len(prompt.split())
    estimated_tokens = estimate_tokens_from_words(word_count)
    usage_percentage = (
        (estimated_tokens / context_window) * 100 if context_window > 0 else 0
    )

    return estimated_tokens, usage_percentage
