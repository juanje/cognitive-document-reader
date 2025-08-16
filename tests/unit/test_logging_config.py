"""Test logging configuration functionality."""

from __future__ import annotations

import logging
from unittest.mock import patch

from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.utils.logging_config import (
    configure_from_config,
    configure_logging,
)


class TestLoggingConfiguration:
    """Test logging configuration functions."""

    def setup_method(self):
        """Reset logging state before each test."""
        # Clear all handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Reset level
        root_logger.setLevel(logging.WARNING)

    def test_configure_logging_default(self):
        """Test default logging configuration (stderr, INFO level)."""
        configure_logging()

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert root_logger.level == logging.INFO

        # Handler should be StreamHandler (stderr)
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)

    def test_configure_logging_verbose(self):
        """Test verbose logging configuration (DEBUG for cognitive_reader)."""
        configure_logging(verbose=True)

        root_logger = logging.getLogger()
        cognitive_logger = logging.getLogger("cognitive_reader")

        assert root_logger.level == logging.DEBUG
        assert cognitive_logger.level == logging.DEBUG

    def test_configure_logging_quiet(self):
        """Test quiet logging configuration (ERROR level only)."""
        configure_logging(quiet=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR

    def test_configure_logging_file_output(self, tmp_path):
        """Test logging to file instead of stderr."""
        log_file = tmp_path / "test.log"
        configure_logging(log_file=log_file)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1

        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.FileHandler)

        # Test that logs are written to file
        logger = logging.getLogger("test_logger")
        logger.info("Test log message")

        # Force handler to flush
        handler.flush()

        assert log_file.exists()
        log_content = log_file.read_text()
        assert "Test log message" in log_content

    def test_configure_logging_file_creates_directories(self, tmp_path):
        """Test that logging creates parent directories if needed."""
        log_file = tmp_path / "nested" / "dir" / "test.log"

        # Directory doesn't exist yet
        assert not log_file.parent.exists()

        configure_logging(log_file=log_file)

        # Directory should be created
        assert log_file.parent.exists()

    def test_configure_logging_multiple_calls_clears_handlers(self, tmp_path):
        """Test that multiple calls clear previous handlers."""
        # First configuration
        configure_logging(verbose=True)
        assert len(logging.getLogger().handlers) == 1

        # Second configuration should clear previous handlers
        log_file = tmp_path / "test.log"
        configure_logging(log_file=log_file)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.FileHandler)

    def test_configure_logging_http_logger_levels(self):
        """Test that HTTP library loggers are configured correctly."""
        configure_logging(verbose=True)

        # In verbose mode, some HTTP loggers should allow INFO
        assert logging.getLogger("httpx").level == logging.INFO
        assert logging.getLogger("httpcore").level == logging.WARNING

        # Test non-verbose mode
        configure_logging(verbose=False)

        # In normal mode, HTTP loggers should be WARNING
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("httpcore").level == logging.WARNING


class TestConfigurFromConfig:
    """Test configure_from_config function."""

    def setup_method(self):
        """Reset logging state before each test."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_configure_from_config_no_log_file(self, base_test_config):
        """Test configuration with config that has no log_file set."""
        config = base_test_config.model_copy(update={"log_file": None})
        configure_from_config(config)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    def test_configure_from_config_with_log_file(self, base_test_config, tmp_path):
        """Test configuration with config that has log_file set."""
        log_file = tmp_path / "config_test.log"
        config = base_test_config.model_copy(update={"log_file": log_file})

        configure_from_config(config)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.FileHandler)

    def test_configure_from_config_environment_variable(self, tmp_path):
        """Test that COGNITIVE_READER_LOG_FILE environment variable works."""
        log_file = tmp_path / "env_test.log"

        with patch.dict("os.environ", {"COGNITIVE_READER_LOG_FILE": str(log_file)}):
            config = CognitiveConfig.from_env()
            configure_from_config(config)

            # Test that logging is configured to use the file
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) == 1
            assert isinstance(root_logger.handlers[0], logging.FileHandler)

            # Test that logs actually go to the file
            logger = logging.getLogger("test_env_logger")
            logger.info("Environment test message")

            root_logger.handlers[0].flush()
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Environment test message" in log_content


class TestIntegrationWithCognitiveConfig:
    """Test integration between logging config and CognitiveConfig."""

    def test_log_file_field_exists(self):
        """Test that log_file field exists in CognitiveConfig."""
        config = CognitiveConfig()
        assert hasattr(config, 'log_file')
        assert config.log_file is None

    def test_log_file_field_accepts_path(self, tmp_path):
        """Test that log_file field accepts Path objects."""
        log_file = tmp_path / "test.log"
        config = CognitiveConfig(log_file=log_file)
        assert config.log_file == log_file

    def test_from_env_reads_log_file_variable(self, tmp_path):
        """Test that from_env() reads COGNITIVE_READER_LOG_FILE."""
        log_file = tmp_path / "env_config.log"

        with patch.dict("os.environ", {"COGNITIVE_READER_LOG_FILE": str(log_file)}):
            config = CognitiveConfig.from_env()
            assert config.log_file == log_file

    def test_from_env_no_log_file_variable(self):
        """Test that from_env() defaults to None when no env var set."""
        with patch.dict("os.environ", {}, clear=True):
            config = CognitiveConfig.from_env()
            assert config.log_file is None
