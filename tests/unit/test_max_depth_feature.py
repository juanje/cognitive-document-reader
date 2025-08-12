"""Tests for --max-depth development feature.

Tests the depth filtering functionality that allows limiting
the maximum hierarchy depth processed during cognitive reading.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from cognitive_reader.cli.main import cli
from cognitive_reader.core.progressive_reader import CognitiveReader
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.document import DocumentSection


class TestMaxDepthFiltering:
    """Test max-depth filtering functionality."""

    def test_filter_by_depth_basic(self):
        """Test basic depth filtering functionality."""
        config = CognitiveConfig(max_hierarchy_depth=2)
        reader = CognitiveReader(config)

        # Create test sections with different depths
        sections = [
            DocumentSection(
                id="s1",
                title="Level 1 Section",
                content="Content 1",
                level=1,
                order_index=0,
            ),
            DocumentSection(
                id="s2",
                title="Level 2 Section",
                content="Content 2",
                level=2,
                order_index=1,
            ),
            DocumentSection(
                id="s3",
                title="Level 3 Section",
                content="Content 3",
                level=3,
                order_index=2,
            ),
            DocumentSection(
                id="s4",
                title="Level 4 Section",
                content="Content 4",
                level=4,
                order_index=3,
            ),
        ]

        # Test filtering with max_depth=2
        filtered_sections = reader._filter_by_depth(sections, max_depth=2)

        assert len(filtered_sections) == 2
        assert filtered_sections[0].level == 1
        assert filtered_sections[1].level == 2

    def test_filter_by_depth_no_filtering_high_limit(self):
        """Test that high max_depth values don't filter anything."""
        config = CognitiveConfig(max_hierarchy_depth=10)  # High value = no filtering
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id="s1",
                title="Level 1 Section",
                content="Content 1",
                level=1,
                order_index=0,
            ),
            DocumentSection(
                id="s2",
                title="Level 3 Section",
                content="Content 2",
                level=3,
                order_index=1,
            ),
        ]

        filtered_sections = reader._apply_section_filters(sections)
        assert len(filtered_sections) == 2  # No filtering applied

    def test_filter_by_depth_preserves_order(self):
        """Test that filtering preserves section order."""
        config = CognitiveConfig(max_hierarchy_depth=2)
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
                title="Level 3 (filtered)",
                content="Content",
                level=3,
                order_index=1,
            ),
            DocumentSection(
                id="s3",
                title="Level 2 B",
                content="Content",
                level=2,
                order_index=2,
            ),
            DocumentSection(
                id="s4",
                title="Level 1 C",
                content="Content",
                level=1,
                order_index=3,
            ),
        ]

        filtered_sections = reader._filter_by_depth(sections, max_depth=2)

        assert len(filtered_sections) == 3
        assert filtered_sections[0].order_index == 0  # Level 1 A
        assert filtered_sections[1].order_index == 2  # Level 2 B
        assert filtered_sections[2].order_index == 3  # Level 1 C

    def test_config_defaults(self):
        """Test that config defaults work correctly."""
        config = CognitiveConfig()

        # Default should be 10 (no filtering)
        assert config.max_hierarchy_depth == 10

    def test_config_from_env(self):
        """Test loading max_hierarchy_depth from environment."""

        # Test default
        config = CognitiveConfig.from_env()
        assert config.max_hierarchy_depth == 10

        # Test custom value (would need to mock os.getenv)
        with pytest.MonkeyPatch().context() as m:
            m.setenv("COGNITIVE_READER_MAX_HIERARCHY_DEPTH", "3")
            config = CognitiveConfig.from_env()
            assert config.max_hierarchy_depth == 3


class TestMaxDepthCLI:
    """Test max-depth CLI functionality."""

    def test_cli_max_depth_option(self):
        """Test that --max-depth CLI option works."""
        runner = CliRunner()

        # Test with structure-only mode (existing functionality)
        result = runner.invoke(cli, [
            'examples/sample_document.md',
            '--max-depth=2',
            '--structure-only'
        ])

        assert result.exit_code == 0
        assert "Cognitive Document Reader Example" in result.output

    def test_cli_max_depth_with_dry_run(self):
        """Test that --max-depth works with processing mode."""
        runner = CliRunner()

        result = runner.invoke(cli, [
            'examples/sample_document.md',
            '--max-depth=2',
            '--dry-run',
            '--quiet'
        ])

        assert result.exit_code == 0
        # Should show some sections processed (basic functionality test)
        assert "**Total Sections**:" in result.output

    def test_cli_max_depth_verbose_logging(self):
        """Test that --max-depth shows development mode info."""
        runner = CliRunner()

        result = runner.invoke(cli, [
            'examples/sample_document.md',
            '--max-depth=2',
            '--dry-run',
            '--verbose'
        ])

        assert result.exit_code == 0
        assert "max-depth=2" in result.output
        # Basic functionality test - logs are captured differently in pytest
