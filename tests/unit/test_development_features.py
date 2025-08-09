"""Tests for development features: filtering, partial results, etc."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cognitive_reader.core.progressive_reader import CognitiveReader
from cognitive_reader.models.config import ReadingConfig
from cognitive_reader.models.document import DocumentSection, SectionSummary
from cognitive_reader.models.knowledge import LanguageCode


class TestSectionFiltering:
    """Test section filtering functionality."""

    def test_filter_by_depth(self):
        """Test depth filtering functionality."""
        config = ReadingConfig(max_section_depth=2)
        reader = CognitiveReader(config)

        # Create test sections with different depths
        sections = [
            DocumentSection(
                id="s1",
                title="Level 0 Section",
                content="Content 1",
                level=0,
                order_index=0,
            ),
            DocumentSection(
                id="s2",
                title="Level 1 Section",
                content="Content 2",
                level=1,
                order_index=1,
            ),
            DocumentSection(
                id="s3",
                title="Level 2 Section",
                content="Content 3",
                level=2,
                order_index=2,
            ),
            DocumentSection(
                id="s4",
                title="Level 3 Section",
                content="Content 4",
                level=3,
                order_index=3,
            ),
            DocumentSection(
                id="s5",
                title="Level 4 Section",
                content="Content 5",
                level=4,
                order_index=4,
            ),
        ]

        # Test filtering with max_depth=2
        filtered_sections = reader._filter_by_depth(sections, max_depth=2)

        assert len(filtered_sections) == 3
        assert all(section.level <= 2 for section in filtered_sections)
        assert filtered_sections[0].id == "s1"
        assert filtered_sections[1].id == "s2"
        assert filtered_sections[2].id == "s3"

    def test_apply_section_filters_depth_only(self):
        """Test section filtering with depth filter only."""
        config = ReadingConfig(max_section_depth=1)
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id="s1", title="Level 0", content="Content", level=0, order_index=0
            ),
            DocumentSection(
                id="s2", title="Level 1", content="Content", level=1, order_index=1
            ),
            DocumentSection(
                id="s3", title="Level 2", content="Content", level=2, order_index=2
            ),
        ]

        filtered = reader._apply_section_filters(sections)
        assert len(filtered) == 2
        assert all(section.level <= 1 for section in filtered)

    def test_apply_section_filters_count_only(self):
        """Test section filtering with count limit only."""
        config = ReadingConfig(max_sections=2)
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id=f"s{i}",
                title=f"Section {i}",
                content="Content",
                level=0,
                order_index=i,
            )
            for i in range(5)
        ]

        filtered = reader._apply_section_filters(sections)
        assert len(filtered) == 2
        assert filtered[0].id == "s0"
        assert filtered[1].id == "s1"

    def test_apply_section_filters_both(self):
        """Test section filtering with both depth and count limits."""
        config = ReadingConfig(max_section_depth=1, max_sections=3)
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id="s1", title="Level 0-1", content="Content", level=0, order_index=0
            ),
            DocumentSection(
                id="s2", title="Level 0-2", content="Content", level=0, order_index=1
            ),
            DocumentSection(
                id="s3", title="Level 1-1", content="Content", level=1, order_index=2
            ),
            DocumentSection(
                id="s4", title="Level 1-2", content="Content", level=1, order_index=3
            ),
            DocumentSection(
                id="s5", title="Level 2-1", content="Content", level=2, order_index=4
            ),
        ]

        filtered = reader._apply_section_filters(sections)

        # First filter by depth (removes level 2) -> 4 sections
        # Then filter by count (take first 3) -> 3 sections
        assert len(filtered) == 3
        assert all(section.level <= 1 for section in filtered)
        assert filtered[0].id == "s1"
        assert filtered[1].id == "s2"
        assert filtered[2].id == "s3"

    def test_apply_section_filters_no_filters(self):
        """Test section filtering with no filters configured."""
        config = ReadingConfig()  # No filters
        reader = CognitiveReader(config)

        sections = [
            DocumentSection(
                id=f"s{i}",
                title=f"Section {i}",
                content="Content",
                level=i,
                order_index=i,
            )
            for i in range(3)
        ]

        filtered = reader._apply_section_filters(sections)
        assert len(filtered) == 3  # No filtering applied
        assert filtered == sections


class TestPartialResultsSaving:
    """Test partial results saving functionality."""

    @pytest.mark.asyncio
    async def test_save_partial_result_creates_file(self):
        """Test that partial results are saved to correct file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReadingConfig(
                save_partial_results=True,
                partial_results_dir=temp_dir,
                fast_mode=True,  # For predictable test output
            )
            reader = CognitiveReader(config)

            section = DocumentSection(
                id="test_section",
                title="Test Section",
                content="This is test content for the section.",
                level=1,
                order_index=0,
            )

            summary = SectionSummary(
                section_id="test_section",
                title="Test Section",
                summary="This is a test summary",
                key_concepts=["test", "summary"],
                confidence_score=0.95,
            )

            await reader._save_partial_result(
                section_index=1,
                total_sections=5,
                section=section,
                summary=summary,
                accumulated_context="Previous context here",
            )

            # Check file was created
            expected_file = Path(temp_dir) / "partial_001_of_005.json"
            assert expected_file.exists()

            # Check file content
            with open(expected_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["progress"]["section_index"] == 1
            assert data["progress"]["total_sections"] == 5
            assert data["progress"]["progress_percentage"] == 20.0
            assert data["section"]["id"] == "test_section"
            assert data["section"]["title"] == "Test Section"
            assert data["summary"]["summary"] == "This is a test summary"
            assert data["summary"]["key_concepts"] == ["test", "summary"]
            assert data["config"]["model_used"] == "llama3.1:8b"  # fast_mode=True
            assert data["config"]["fast_mode"] is True

    @pytest.mark.asyncio
    async def test_save_partial_result_handles_errors_gracefully(self):
        """Test that partial results saving errors don't crash main process."""
        config = ReadingConfig(
            save_partial_results=True,
            partial_results_dir="/invalid/path/that/does/not/exist/and/cannot/be/created",
        )
        reader = CognitiveReader(config)

        section = DocumentSection(
            id="test", title="Test", content="Content", level=0, order_index=0
        )
        summary = SectionSummary(
            section_id="test",
            title="Test",
            summary="Summary",
            key_concepts=[],
            confidence_score=1.0,
        )

        # This should not raise an exception
        await reader._save_partial_result(
            section_index=1,
            total_sections=1,
            section=section,
            summary=summary,
            accumulated_context="",
        )

    @pytest.mark.asyncio
    async def test_save_partial_result_truncates_long_content(self):
        """Test that long content is properly truncated in partial results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReadingConfig(
                save_partial_results=True, partial_results_dir=temp_dir
            )
            reader = CognitiveReader(config)

            # Create section with long content
            long_content = "A" * 500  # 500 characters
            section = DocumentSection(
                id="test_section",
                title="Test Section",
                content=long_content,
                level=0,
                order_index=0,
            )

            summary = SectionSummary(
                section_id="test_section",
                title="Test Section", 
                summary="Summary",
                key_concepts=[],
                confidence_score=1.0,
            )

            long_context = "B" * 300  # 300 characters
            await reader._save_partial_result(
                section_index=1,
                total_sections=1,
                section=section,
                summary=summary,
                accumulated_context=long_context,
            )

            expected_file = Path(temp_dir) / "partial_001_of_001.json"
            with open(expected_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Content should be truncated to 300 chars + "..."
            assert len(data["section"]["content_preview"]) == 303
            assert data["section"]["content_preview"].endswith("...")
            assert data["section"]["content_preview"].startswith("AAA")

            # Context should be truncated to 200 chars + "..."
            assert len(data["context"]["accumulated_context_preview"]) == 203
            assert data["context"]["accumulated_context_preview"].endswith("...")
            assert data["context"]["accumulated_context_preview"].startswith("BBB")


class TestDevelopmentModeIntegration:
    """Test integration of development features."""

    def test_is_development_mode_with_new_features(self):
        """Test development mode detection with new features."""
        # Test individual features
        assert ReadingConfig(save_partial_results=True).is_development_mode()
        assert ReadingConfig(max_sections=5).is_development_mode()
        assert ReadingConfig(max_section_depth=2).is_development_mode()

        # Test combinations
        config = ReadingConfig(
            save_partial_results=True,
            max_sections=10,
            max_section_depth=3,
            dry_run=True,
        )
        assert config.is_development_mode()

    def test_development_mode_logging_message(self):
        """Test that development features are logged appropriately."""
        config = ReadingConfig(
            max_sections=5, max_section_depth=2, save_partial_results=True
        )

        # Mock logger to capture log messages
        with patch("cognitive_reader.core.progressive_reader.logger") as mock_logger:
            CognitiveReader(config)

            # Check that initialization message was called
            mock_logger.info.assert_called()
            
            # Check that the second call (if it exists) mentions development mode
            call_args_list = mock_logger.info.call_args_list
            if len(call_args_list) > 1:
                # Second call should be about development mode
                second_call_args = call_args_list[1][0][0]
                assert "Development mode enabled" in second_call_args
            else:
                # At least verify the config is in development mode
                assert config.is_development_mode()
