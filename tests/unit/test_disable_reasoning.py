"""Tests for disable reasoning functionality."""

from unittest.mock import patch

from cognitive_reader.llm.client import LLMClient
from cognitive_reader.models.config import CognitiveConfig


class TestDisableReasoningFeature:
    """Test disable reasoning feature in LLM client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CognitiveConfig(
            model_name="llama3.1:8b",
            dry_run=True,  # Don't make real LLM calls
            disable_reasoning=False,  # Default state
        )

    def test_disable_reasoning_config_field(self):
        """Test that disable_reasoning field exists and works in config."""
        # Test default value
        assert self.config.disable_reasoning is False

        # Test setting to True
        config_with_reasoning_disabled = CognitiveConfig(
            model_name="qwen3:8b",
            disable_reasoning=True,
        )
        assert config_with_reasoning_disabled.disable_reasoning is True

    def test_llm_creation_with_reasoning_disabled(self):
        """Test that LLMs are created with reasoning=False when disable_reasoning=True."""
        config = CognitiveConfig(
            model_name="qwen3:8b",
            disable_reasoning=True,
        )

        client = LLMClient(config)

        # Check that main LLM was created with reasoning=False
        assert hasattr(client._llm, "reasoning")
        # The reasoning parameter should be False (disabled)
        assert client._llm.reasoning is False

    def test_llm_creation_with_reasoning_enabled(self):
        """Test that LLMs are created with reasoning=None when disable_reasoning=False."""
        config = CognitiveConfig(
            model_name="qwen3:8b",
            disable_reasoning=False,  # Keep reasoning enabled
        )

        client = LLMClient(config)

        # Check that main LLM was created with reasoning=None (default behavior)
        assert hasattr(client._llm, "reasoning")
        # The reasoning parameter should be None (default)
        assert client._llm.reasoning is None

    def test_fast_llm_creation_with_reasoning_control(self):
        """Test that fast LLM is also created with proper reasoning control."""
        config = CognitiveConfig(
            model_name="qwen3:8b",
            fast_pass_model="llama3.1:8b",
            disable_reasoning=True,
        )

        client = LLMClient(config)

        # Check that fast LLM was created with reasoning=False
        assert client._fast_llm is not None
        assert hasattr(client._fast_llm, "reasoning")
        assert client._fast_llm.reasoning is False

    def test_env_variable_loading(self):
        """Test that disable_reasoning can be loaded from environment variable."""
        import os

        # Test with environment variable set to true
        with patch.dict(os.environ, {"COGNITIVE_READER_DISABLE_REASONING": "true"}):
            config = CognitiveConfig.from_env()
            assert config.disable_reasoning is True

        # Test with environment variable set to false
        with patch.dict(os.environ, {"COGNITIVE_READER_DISABLE_REASONING": "false"}):
            config = CognitiveConfig.from_env()
            assert config.disable_reasoning is False

        # Test with no environment variable (should default to False)
        env_without_reasoning = {
            k: v
            for k, v in os.environ.items()
            if k != "COGNITIVE_READER_DISABLE_REASONING"
        }
        with patch.dict(os.environ, env_without_reasoning, clear=True):
            config = CognitiveConfig.from_env()
            assert config.disable_reasoning is False


class TestCLIIntegration:
    """Test CLI integration for disable reasoning feature."""

    def test_cli_disable_reasoning_flag(self):
        """Test that --disable-reasoning flag is properly handled."""
        from click.testing import CliRunner

        from cognitive_reader.cli.main import cli

        runner = CliRunner()

        # Test with --disable-reasoning flag (only test that it doesn't crash)
        result = runner.invoke(
            cli,
            [
                "--disable-reasoning",
                "--dry-run",
                "--help",  # Just show help instead of trying to process
            ],
        )

        # Should not crash with a serious error (exit code 0 or 1 for help is fine)
        assert result.exit_code in [0, 1]  # 0 = success, 1 = help shown

    def test_cli_help_includes_disable_reasoning(self):
        """Test that --disable-reasoning appears in CLI help."""
        from click.testing import CliRunner

        from cognitive_reader.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--disable-reasoning" in result.output
        assert "Disable reasoning mode for reasoning models" in result.output
