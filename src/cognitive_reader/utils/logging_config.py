"""Logging configuration utilities for Cognitive Document Reader."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.config import CognitiveConfig


def configure_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Path | None = None,
) -> None:
    """Configure logging handlers and levels.

    This function can be used both from CLI and from library code to set up
    consistent logging behavior.

    Args:
        verbose: Enable verbose logging (DEBUG level for cognitive_reader)
        quiet: Suppress all logs except errors
        log_file: Optional file path to write logs to instead of stderr

    Examples:
        # From library code
        from cognitive_reader.utils.logging_config import configure_logging
        configure_logging(verbose=True, log_file=Path("app.log"))

        # CLI will call this automatically based on --log, --verbose, --quiet flags
    """
    # Clear any existing handlers to start fresh
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set base logging level
    if quiet:
        root_logger.setLevel(logging.ERROR)
    elif verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create handler (file or stderr)
    handler: logging.Handler
    if log_file:
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    else:
        handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure specific logger levels
    if verbose:
        # Enable DEBUG for cognitive_reader logs only
        logging.getLogger("cognitive_reader").setLevel(logging.DEBUG)

        # In verbose mode, allow some HTTP logs but not the noisy DEBUG ones
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("langsmith").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.INFO)
    else:
        # Default: suppress noisy HTTP logs
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("langsmith").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)


def configure_from_config(config: CognitiveConfig) -> None:
    """Configure logging from a CognitiveConfig instance.

    This is a convenience function for library users who have a CognitiveConfig
    and want to set up logging based on its log_file setting.

    Args:
        config: CognitiveConfig instance with log_file setting

    Examples:
        from cognitive_reader.models.config import CognitiveConfig
        from cognitive_reader.utils.logging_config import configure_from_config

        config = CognitiveConfig.from_env()  # COGNITIVE_READER_LOG_FILE env var
        configure_from_config(config)

        # Now all cognitive_reader logging will go to the configured file
    """
    configure_logging(log_file=config.log_file)
