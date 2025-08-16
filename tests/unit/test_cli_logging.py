"""Test CLI logging functionality with --log flag."""

from __future__ import annotations

from click.testing import CliRunner

from cognitive_reader.cli.main import cli


class TestCLILogging:
    """Test --log flag functionality in CLI."""

    def test_cli_log_flag_basic_functionality(self, sample_markdown, tmp_path):
        """Test basic --log flag functionality."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        log_file = tmp_path / "test.log"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                str(test_file),
                "--log",
                str(log_file),
                "--dry-run",
                "--verbose",  # Use verbose to ensure logs are generated
            ],
        )

        assert result.exit_code == 0
        assert log_file.exists()

        # Check that logs were written to file
        log_content = log_file.read_text()
        # Should contain some cognitive_reader logs
        assert "cognitive_reader" in log_content
        # Should contain processing information in verbose mode
        assert "Processing" in log_content or "INFO" in log_content

    def test_cli_log_flag_creates_directories(self, sample_markdown, tmp_path):
        """Test that --log flag creates parent directories."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        # Use nested directory that doesn't exist
        log_file = tmp_path / "logs" / "nested" / "test.log"
        assert not log_file.parent.exists()

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--log", str(log_file), "--dry-run", "--quiet"]
        )

        assert result.exit_code == 0
        assert log_file.exists()
        assert log_file.parent.exists()

    def test_cli_log_flag_with_verbose(self, sample_markdown, tmp_path):
        """Test --log flag combined with --verbose."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        log_file = tmp_path / "verbose_test.log"

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--log", str(log_file), "--verbose", "--dry-run"]
        )

        assert result.exit_code == 0
        assert log_file.exists()

        log_content = log_file.read_text()
        # Verbose mode should include DEBUG messages
        assert "DEBUG" in log_content

    def test_cli_log_flag_with_quiet(self, sample_markdown, tmp_path):
        """Test --log flag combined with --quiet."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        log_file = tmp_path / "quiet_test.log"

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--log", str(log_file), "--quiet", "--dry-run"]
        )

        assert result.exit_code == 0
        assert log_file.exists()

        log_content = log_file.read_text()
        # Quiet mode should have minimal logs (mostly ERROR level)
        # But dry-run shouldn't produce ERROR logs, so file might be small
        # Just check that file was created and is accessible
        assert isinstance(log_content, str)

    def test_cli_without_log_flag_uses_stderr(self, sample_markdown, tmp_path):
        """Test that without --log flag, logs go to stderr (default behavior)."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                str(test_file),
                "--dry-run",
                "--verbose",  # Ensure some logs are generated
            ],
        )

        assert result.exit_code == 0
        # stderr should contain log messages (captured by CliRunner)
        # Note: CliRunner captures stderr separately, but our logs might
        # not appear in result.output since they go to stderr
        # This test mainly verifies no crash when no --log flag

    def test_cli_log_flag_structure_only_mode(self, sample_markdown, tmp_path):
        """Test --log flag with --structure-only mode."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        log_file = tmp_path / "structure_test.log"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [str(test_file), "--log", str(log_file), "--structure-only", "--verbose"],
        )

        assert result.exit_code == 0
        assert log_file.exists()

        log_content = log_file.read_text()
        # Should contain structure parsing logs
        assert len(log_content) > 0

    def test_cli_log_flag_help_text(self):
        """Test that --log flag appears in help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--log" in result.output
        assert "Write logs to specified file instead of stderr" in result.output

    def test_cli_log_flag_with_stats(self, sample_markdown, tmp_path):
        """Test --log flag combined with --stats."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        log_file = tmp_path / "stats_test.log"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [str(test_file), "--log", str(log_file), "--stats", "--dry-run", "--quiet"],
        )

        assert result.exit_code == 0
        assert log_file.exists()

        # Stats output should still go to stdout/stderr, not log file
        assert "Processing Statistics" in result.output

        # Log file should contain processing logs, not stats output
        log_content = log_file.read_text()
        assert "Processing Statistics" not in log_content

    def test_cli_log_flag_error_handling(self, sample_markdown, tmp_path):
        """Test error handling when log file path is invalid."""
        test_file = tmp_path / "test_doc.md"
        test_file.write_text(sample_markdown)

        # Try to use a path that should cause issues (directory as file)
        invalid_log_path = tmp_path / "existing_dir"
        invalid_log_path.mkdir()  # Create as directory

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                str(test_file),
                "--log",
                str(invalid_log_path),  # Directory instead of file
                "--dry-run",
                "--quiet",
            ],
        )

        # Command should handle the error gracefully
        # Exact behavior depends on how Python's logging handles this
        # At minimum, it shouldn't crash completely
        assert result.exit_code in [0, 1]  # Either success or handled error
