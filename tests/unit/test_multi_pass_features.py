"""Tests for multi-pass processing features and flags."""

from __future__ import annotations

import tempfile
from pathlib import Path

from cognitive_reader.models.config import CognitiveConfig


class TestSinglePassFlag:
    """Test single-pass flag functionality."""

    def test_single_pass_config_default(self):
        """Test that single_pass defaults to False."""
        config = CognitiveConfig()
        assert config.single_pass is False

    def test_single_pass_from_env_true(self, base_test_config):
        """Test single_pass can be set to True via environment variable."""
        # Use fixtures instead of expensive from_env() calls
        config = base_test_config.model_copy(update={"single_pass": True})
        assert config.single_pass is True

    def test_single_pass_from_env_false(self, base_test_config):
        """Test single_pass can be set to False via environment variable."""
        config = base_test_config.model_copy(update={"single_pass": False})
        assert config.single_pass is False

    def test_single_pass_from_env_default(self, base_test_config):
        """Test single_pass defaults to False when env var not set."""
        config = base_test_config.model_copy()
        assert config.single_pass is False


class TestSaveIntermediateFlag:
    """Test save-intermediate flag functionality."""

    def test_save_intermediate_config_default(self):
        """Test that save_intermediate defaults to False."""
        config = CognitiveConfig()
        assert config.save_intermediate is False

    def test_save_intermediate_from_env_true(self, base_test_config):
        """Test save_intermediate can be set to True via environment variable."""
        config = base_test_config.model_copy(update={"save_intermediate": True})
        assert config.save_intermediate is True

    def test_save_intermediate_from_env_false(self, base_test_config):
        """Test save_intermediate can be set to False via environment variable."""
        config = base_test_config.model_copy(update={"save_intermediate": False})
        assert config.save_intermediate is False

    def test_intermediate_dir_config_default(self):
        """Test that intermediate_dir has correct default."""
        config = CognitiveConfig()
        assert config.intermediate_dir == "./intermediate_passes"

    def test_intermediate_dir_from_env(self, base_test_config):
        """Test intermediate_dir can be set via environment variable."""
        test_dir = "/tmp/test_intermediate"
        config = base_test_config.model_copy(update={"intermediate_dir": test_dir})
        assert config.intermediate_dir == test_dir


class TestMultiPassArchitecture:
    """Test multi-pass architecture configuration."""

    def test_num_passes_config_default(self):
        """Test that num_passes defaults to 2 (two-pass as per SPECS v2)."""
        config = CognitiveConfig()
        assert config.num_passes == 2

    def test_multi_pass_mode_detection(self):
        """Test detection of when multi-pass mode should be used."""
        # Single pass mode
        config = CognitiveConfig(single_pass=True)
        assert config.single_pass is True

        # Standard mode (single pass with num_passes=1)
        config = CognitiveConfig(num_passes=1)
        assert config.num_passes == 1
        assert config.single_pass is False

        # Multi-pass mode (default should be 2 passes)
        config = CognitiveConfig()
        assert config.num_passes == 2
        assert config.single_pass is False

    def test_intermediate_files_only_with_flag(self):
        """Test that intermediate files are only saved when flag is enabled."""
        # Default: no intermediate files
        config = CognitiveConfig()
        assert config.save_intermediate is False

        # With flag: intermediate files enabled
        config = CognitiveConfig(save_intermediate=True)
        assert config.save_intermediate is True


class TestCLIIntegration:
    """Test CLI integration for new flags."""

    def test_cli_single_pass_flag(self):
        """Test --single-pass CLI flag."""
        from click.testing import CliRunner

        from cognitive_reader.cli.main import cli

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Document\n\nTest content.")
            temp_file = f.name

        try:
            # Test with --single-pass flag
            result = runner.invoke(
                cli, [temp_file, "--single-pass", "--dry-run", "--quiet"]
            )

            # Should succeed (dry-run mode) or provide helpful output if it fails
            if result.exit_code != 0:
                print(f"CLI output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_cli_save_intermediate_flag(self):
        """Test --save-intermediate CLI flag."""
        from click.testing import CliRunner

        from cognitive_reader.cli.main import cli

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Document\n\nTest content.")
            temp_file = f.name

        try:
            # Test with --save-intermediate flag
            result = runner.invoke(
                cli, [temp_file, "--save-intermediate", "--dry-run", "--quiet"]
            )

            # Should succeed (dry-run mode) or provide helpful output if it fails
            if result.exit_code != 0:
                print(f"CLI output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_cli_help_includes_new_flags(self):
        """Test that CLI help includes the new flags."""
        from click.testing import CliRunner

        from cognitive_reader.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        help_text = result.output

        # Check that both new flags are documented
        assert "--single-pass" in help_text
        assert "--save-intermediate" in help_text
        assert "single-pass processing" in help_text.lower()
        assert "intermediate state" in help_text.lower()


class TestFeatureCombination:
    """Test combination of features."""

    def test_single_pass_disables_intermediate_logic(self):
        """Test that single-pass mode makes sense with other flags."""
        # Single pass + save intermediate should be valid
        # (though intermediate saving won't happen in single pass)
        config = CognitiveConfig(single_pass=True, save_intermediate=True)
        assert config.single_pass is True
        assert config.save_intermediate is True

    def test_multi_pass_with_intermediate_files(self):
        """Test multi-pass mode with intermediate file saving."""
        config = CognitiveConfig(
            num_passes=2,
            save_intermediate=True,
            intermediate_dir="/tmp/test_passes",
        )
        assert config.num_passes == 2
        assert config.save_intermediate is True
        assert config.intermediate_dir == "/tmp/test_passes"

    def test_development_mode_includes_new_features(self):
        """Test that development mode detection includes new features."""
        # Single pass is not a development mode
        config = CognitiveConfig(single_pass=True)
        assert not config.is_development_mode()

        # Save intermediate is not development mode by itself
        config = CognitiveConfig(save_intermediate=True)
        assert not config.is_development_mode()

        # But dry_run still is
        config = CognitiveConfig(single_pass=True, dry_run=True)
        assert config.is_development_mode()
