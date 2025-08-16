"""Tests for --stats CLI functionality."""

from __future__ import annotations

from click.testing import CliRunner

from cognitive_reader.cli.main import cli
from cognitive_reader.models.metrics import ProcessingMetrics


class TestStatsCLI:
    """Test CLI --stats functionality."""

    def test_stats_flag_basic_functionality(self, sample_markdown, tmp_path):
        """Test that --stats flag works and shows statistics."""
        # Create a temporary markdown file
        test_file = tmp_path / "test_stats.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file), "--stats", "--dry-run", "--quiet"])

        assert result.exit_code == 0
        assert "Processing Statistics" in result.output
        assert "LLM Calls" in result.output
        assert "Total Duration" in result.output
        assert "Sections Processed" in result.output
        assert "Concepts Generated" in result.output

    def test_stats_flag_dry_run_mode(self, sample_markdown, tmp_path):
        """Test stats in dry-run mode shows zero LLM calls."""
        test_file = tmp_path / "test_stats_dry.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file), "--stats", "--dry-run", "--quiet"])

        assert result.exit_code == 0
        # In dry-run mode, should show LLM call stats (with token estimates)
        assert "calls" in result.output
        assert "tokens" in result.output
        # But should still show timing and section info
        assert "Duration" in result.output
        assert "sections" in result.output

    def test_stats_flag_mock_responses_mode(self, sample_markdown, tmp_path):
        """Test stats in mock-responses mode."""
        test_file = tmp_path / "test_stats_mock.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--stats", "--mock-responses", "--quiet"]
        )

        assert result.exit_code == 0
        assert "Processing Statistics" in result.output
        # Should show some timing data
        assert "Duration" in result.output
        assert "sections" in result.output
        assert "concepts" in result.output

    def test_without_stats_flag_no_statistics(self, sample_markdown, tmp_path):
        """Test that without --stats flag, no statistics are shown."""
        test_file = tmp_path / "test_no_stats.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file), "--dry-run", "--quiet"])

        assert result.exit_code == 0
        # Should not contain stats table
        assert "Processing Statistics" not in result.output
        assert "LLM Calls" not in result.output

    def test_stats_with_different_configurations(
        self, sample_spanish_markdown, tmp_path
    ):
        """Test stats with different document configurations."""
        test_file = tmp_path / "test_stats_spanish.md"
        test_file.write_text(sample_spanish_markdown)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                str(test_file),
                "--stats",
                "--dry-run",
                "--quiet",
                "--language",
                "es",
                "--single-pass",
            ],
        )

        assert result.exit_code == 0
        assert "Processing Statistics" in result.output
        # Should show duration info even for single-pass
        assert "Duration" in result.output

    def test_stats_table_content_structure(self, sample_markdown, tmp_path):
        """Test that stats table contains all expected metrics."""
        test_file = tmp_path / "test_stats_content.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file), "--stats", "--dry-run", "--quiet"])

        assert result.exit_code == 0

        # Check for all expected metric categories
        expected_metrics = [
            "LLM Calls",
            "Summary Calls",
            "Concept Calls",
            "Total Tokens Sent",
            "Avg Summary",
            "Total Duration",
            "Sections Processed",
            "Concepts Generated",
        ]

        for metric in expected_metrics:
            assert metric in result.output

    def test_metrics_integration_with_cognitive_reader(self, base_test_config):
        """Test that metrics are properly integrated with CognitiveReader."""
        # Test metrics object creation
        metrics = ProcessingMetrics()
        assert metrics is not None

        # Test config integration (using existing base_test_config)
        config = base_test_config.model_copy(update={"dry_run": True})
        assert config.dry_run is True

        # Verify metrics can track basic operations
        metrics.add_section()
        metrics.add_concepts(3)
        assert metrics.sections_processed == 1
        assert metrics.concepts_generated == 3

    def test_stats_flag_help_text(self):
        """Test that --stats flag appears in help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--stats" in result.output
        assert "Show processing statistics at the end" in result.output
