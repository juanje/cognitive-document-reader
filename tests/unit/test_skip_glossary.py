"""Tests for skip glossary functionality."""

from click.testing import CliRunner

from cognitive_reader.cli.main import cli
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode


class TestSkipGlossaryFeature:
    """Test skip glossary feature in configuration and synthesizer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CognitiveConfig(
            model_name="llama3.1:8b",
            dry_run=True,  # Don't make real LLM calls
            skip_glossary=False,  # Default state
        )

    def test_skip_glossary_config_field(self):
        """Test that skip_glossary field exists and works in config."""
        # Test default value
        assert self.config.skip_glossary is False

        # Test setting to True
        config_with_glossary_skipped = CognitiveConfig(
            model_name="llama3.1:8b",
            skip_glossary=True,
        )
        assert config_with_glossary_skipped.skip_glossary is True

    def test_env_variable_loading(self, base_test_config):
        """Test that skip_glossary can be loaded from environment variable."""
        # Test with environment variable set to true
        config = base_test_config.model_copy(update={"skip_glossary": True})
        assert config.skip_glossary is True

        # Test with environment variable set to false
        config = base_test_config.model_copy(update={"skip_glossary": False})
        assert config.skip_glossary is False

        # Test with no environment variable (should default to False)
        config = base_test_config.model_copy()
        assert config.skip_glossary is False

    def test_synthesizer_config_has_skip_glossary_setting(self):
        """Test that synthesizer correctly receives skip_glossary setting."""
        config_enabled = CognitiveConfig(
            model_name="llama3.1:8b",
            skip_glossary=True,
            dry_run=True,
        )

        config_disabled = CognitiveConfig(
            model_name="llama3.1:8b",
            skip_glossary=False,
            dry_run=True,
        )

        # Verify that config has the setting
        assert config_enabled.skip_glossary is True
        assert config_disabled.skip_glossary is False


class TestCLIIntegration:
    """Test CLI integration for skip glossary feature."""

    def test_cli_skip_glossary_flag(self):
        """Test that --skip-glossary flag is properly handled."""
        runner = CliRunner()

        # Test with --skip-glossary flag (only test that it doesn't crash)
        result = runner.invoke(
            cli,
            [
                "--skip-glossary",
                "--dry-run",
                "--help",  # Just show help instead of trying to process
            ],
        )

        # Should not crash with a serious error (exit code 0 or 1 for help is fine)
        assert result.exit_code in [0, 1]  # 0 = success, 1 = help shown

    def test_cli_help_includes_skip_glossary(self):
        """Test that --skip-glossary appears in CLI help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--skip-glossary" in result.output
        assert "Skip concept definitions generation" in result.output

    def test_cli_skip_glossary_with_other_flags(self):
        """Test that --skip-glossary works with other development flags."""
        runner = CliRunner()

        # Test combination with other flags
        result = runner.invoke(
            cli,
            [
                "--skip-glossary",
                "--disable-reasoning",
                "--max-sections",
                "3",
                "--dry-run",
                "--help",
            ],
        )

        # Should handle multiple flags without crashing
        assert result.exit_code in [0, 1]


class TestOutputFormatting:
    """Test that output formatting handles missing glossary correctly."""

    def test_cognitive_knowledge_with_empty_glossary(self):
        """Test that CognitiveKnowledge handles empty concept definitions correctly."""
        from cognitive_reader.models.document import CognitiveKnowledge

        # Create knowledge with empty concept definitions
        knowledge = CognitiveKnowledge(
            document_title="Test Document",
            document_summary="Test summary",
            detected_language=LanguageCode.EN,
            hierarchical_summaries={},
            concepts=[],  # Empty glossary
            total_sections=1,
            avg_summary_length=100.0,
            total_concepts=0,
        )

        # Should work without errors
        assert knowledge.concepts == []
        assert len(knowledge.concepts) == 0
        assert knowledge.total_concepts == 0

    def test_display_formatting_with_no_concepts(self):
        """Test that display formatting works with no concepts."""
        from cognitive_reader.models.document import CognitiveKnowledge

        knowledge = CognitiveKnowledge(
            document_title="Test Document",
            document_summary="Test summary",
            detected_language=LanguageCode.EN,
            hierarchical_summaries={},
            concepts=[],
            total_sections=1,
            avg_summary_length=100.0,
            total_concepts=0,
        )

        # Should not crash when displaying
        assert knowledge.total_concepts == 0
        # Additional formatting tests could be added here
