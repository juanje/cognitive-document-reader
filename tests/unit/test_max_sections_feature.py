"""Tests for --max-sections development feature.

Tests the section count limiting functionality that allows limiting
the maximum number of sections processed during cognitive reading.
"""

from __future__ import annotations

from click.testing import CliRunner

from cognitive_reader.cli.main import cli
from cognitive_reader.core.progressive_reader import CognitiveReader
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.document import DocumentSection


class TestMaxSectionsFiltering:
    """Test max-sections filtering functionality."""

    def test_section_count_limiting_basic(self):
        """Test basic section count limiting functionality."""
        config = CognitiveConfig(max_sections=3)
        reader = CognitiveReader(config)

        # Create test sections
        sections = [
            DocumentSection(
                id=f"s{i}",
                title=f"Section {i}",
                content=f"Content {i}",
                level=1,
                order_index=i,
            )
            for i in range(1, 6)  # 5 sections
        ]

        # Test filtering with max_sections=3
        filtered_sections = reader._apply_section_filters(sections)

        assert len(filtered_sections) == 3
        assert filtered_sections[0].title == "Section 1"
        assert filtered_sections[1].title == "Section 2"
        assert filtered_sections[2].title == "Section 3"

    def test_section_count_no_limiting_when_none(self):
        """Test that no limiting occurs when max_sections is None."""
        config = CognitiveConfig(max_sections=None)  # No limit
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id=f"s{i}",
                title=f"Section {i}",
                content=f"Content {i}",
                level=1,
                order_index=i,
            )
            for i in range(1, 6)  # 5 sections
        ]

        filtered_sections = reader._apply_section_filters(sections)
        assert len(filtered_sections) == 5  # No filtering applied

    def test_section_count_preserves_order(self):
        """Test that limiting preserves document order."""
        config = CognitiveConfig(max_sections=2)
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id="s1",
                title="First Section",
                content="Content",
                level=1,
                order_index=0,
            ),
            DocumentSection(
                id="s2",
                title="Second Section",
                content="Content",
                level=2,
                order_index=1,
            ),
            DocumentSection(
                id="s3",
                title="Third Section",
                content="Content",
                level=1,
                order_index=2,
            ),
        ]

        filtered_sections = reader._apply_section_filters(sections)

        assert len(filtered_sections) == 2
        assert filtered_sections[0].title == "First Section"
        assert filtered_sections[1].title == "Second Section"

    def test_section_count_with_depth_filter_combined(self):
        """Test that max_sections works with max_depth filtering."""
        config = CognitiveConfig(max_sections=2, max_hierarchy_depth=2)
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id="s1",
                title="Level 1 A",
                content="Content",
                level=1,
                order_index=0,
            ),
            DocumentSection(
                id="s2",
                title="Level 2 A",
                content="Content",
                level=2,
                order_index=1,
            ),
            DocumentSection(
                id="s3",
                title="Level 3 (filtered by depth)",
                content="Content",
                level=3,
                order_index=2,
            ),
            DocumentSection(
                id="s4",
                title="Level 1 B",
                content="Content",
                level=1,
                order_index=3,
            ),
            DocumentSection(
                id="s5",
                title="Level 2 B",
                content="Content",
                level=2,
                order_index=4,
            ),
        ]

        filtered_sections = reader._apply_section_filters(sections)

        # First depth filter: 5 -> 4 sections (removes level 3)
        # Then count limit: 4 -> 2 sections (takes first 2)
        assert len(filtered_sections) == 2
        assert filtered_sections[0].title == "Level 1 A"
        assert filtered_sections[1].title == "Level 2 A"

    def test_config_defaults(self):
        """Test that config defaults work correctly."""
        config = CognitiveConfig()

        # Default should be None (no limiting)
        assert config.max_sections is None

    def test_config_from_env(self, base_test_config):
        """Test loading max_sections from environment."""
        # Test default
        config = base_test_config.model_copy()
        assert config.max_sections is None

        # Test custom value
        config = base_test_config.model_copy(update={"max_sections": 5})
        assert config.max_sections == 5


class TestMaxSectionsCLI:
    """Test max-sections CLI functionality."""

    def test_cli_max_sections_option(self):
        """Test that --max-sections CLI option works."""
        runner = CliRunner()

        # Test with structure-only mode (fast execution)
        result = runner.invoke(
            cli, ["examples/sample_document.md", "--max-sections=3", "--structure-only"]
        )

        assert result.exit_code == 0
        assert "Aethelgard's Crystalline Consciousness Theory" in result.output

    def test_cli_max_sections_with_dry_run(self):
        """Test that --max-sections works with processing mode."""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["examples/sample_document.md", "--max-sections=3", "--dry-run", "--quiet"],
        )

        assert result.exit_code == 0
        # Should show limited count
        assert "**Total Sections**: 3" in result.output

    def test_cli_max_sections_verbose_logging(self):
        """Test that --max-sections shows limiting info in verbose mode."""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "examples/sample_document.md",
                "--max-sections=2",
                "--dry-run",
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert "max-sections=2" in result.output

    def test_cli_max_sections_combined_with_max_depth(self):
        """Test that --max-sections works with --max-depth."""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "examples/sample_document.md",
                "--max-sections=2",
                "--max-depth=2",
                "--dry-run",
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # Should show limited count after both filters
        assert "**Total Sections**: 2" in result.output
