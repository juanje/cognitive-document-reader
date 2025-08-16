"""Tests for processing metrics functionality."""

from __future__ import annotations

import time

from cognitive_reader.models.metrics import LLMCallMetrics, ProcessingMetrics


class TestLLMCallMetrics:
    """Test LLM call metrics tracking."""

    def test_initial_state(self):
        """Test initial state of LLMCallMetrics."""
        metrics = LLMCallMetrics()

        assert metrics.summary_calls == 0
        assert metrics.summary_tokens == 0
        assert metrics.concept_calls == 0
        assert metrics.concept_tokens == 0
        assert metrics.total_calls == 0
        assert metrics.total_tokens == 0
        assert metrics.avg_summary_tokens == 0
        assert metrics.avg_concept_tokens == 0
        assert metrics.avg_tokens_per_call == 0

    def test_add_summary_call(self):
        """Test adding summary calls."""
        metrics = LLMCallMetrics()

        metrics.add_summary_call(100)
        assert metrics.summary_calls == 1
        assert metrics.summary_tokens == 100
        assert metrics.total_calls == 1
        assert metrics.total_tokens == 100
        assert metrics.avg_summary_tokens == 100
        assert metrics.avg_tokens_per_call == 100

    def test_add_concept_call(self):
        """Test adding concept calls."""
        metrics = LLMCallMetrics()

        metrics.add_concept_call(50)
        assert metrics.concept_calls == 1
        assert metrics.concept_tokens == 50
        assert metrics.total_calls == 1
        assert metrics.total_tokens == 50
        assert metrics.avg_concept_tokens == 50
        assert metrics.avg_tokens_per_call == 50

    def test_mixed_calls(self):
        """Test mixed summary and concept calls."""
        metrics = LLMCallMetrics()

        metrics.add_summary_call(200)
        metrics.add_summary_call(150)
        metrics.add_concept_call(75)
        metrics.add_concept_call(25)

        assert metrics.summary_calls == 2
        assert metrics.summary_tokens == 350
        assert metrics.concept_calls == 2
        assert metrics.concept_tokens == 100
        assert metrics.total_calls == 4
        assert metrics.total_tokens == 450
        assert metrics.avg_summary_tokens == 175
        assert metrics.avg_concept_tokens == 50
        assert metrics.avg_tokens_per_call == 112.5


class TestProcessingMetrics:
    """Test processing metrics functionality."""

    def test_initial_state(self):
        """Test initial state of ProcessingMetrics."""
        metrics = ProcessingMetrics()

        assert isinstance(metrics.llm_metrics, LLMCallMetrics)
        assert isinstance(metrics.start_time, float)
        assert metrics.pass_durations == {}
        assert metrics.sections_processed == 0
        assert metrics.concepts_generated == 0

    def test_pass_timing(self):
        """Test pass timing functionality."""
        metrics = ProcessingMetrics()

        # Start and end pass 1 (using real timing, but short duration)
        start_time = metrics.start_pass(1)
        time.sleep(0.01)  # Small sleep to ensure some duration
        duration = metrics.end_pass(1, start_time)

        assert isinstance(start_time, float)
        assert duration > 0  # Should have some positive duration
        assert metrics.pass_durations[1] == duration

    def test_multiple_passes(self):
        """Test multiple pass timing."""
        metrics = ProcessingMetrics()

        # Pass 1
        start1 = metrics.start_pass(1)
        time.sleep(0.01)
        metrics.end_pass(1, start1)

        # Pass 2
        start2 = metrics.start_pass(2)
        time.sleep(0.01)
        metrics.end_pass(2, start2)

        assert 1 in metrics.pass_durations
        assert 2 in metrics.pass_durations
        assert metrics.pass_durations[1] > 0
        assert metrics.pass_durations[2] > 0

    def test_section_tracking(self):
        """Test section counting."""
        metrics = ProcessingMetrics()

        assert metrics.sections_processed == 0

        metrics.add_section()
        assert metrics.sections_processed == 1

        metrics.add_section()
        assert metrics.sections_processed == 2

    def test_concept_tracking(self):
        """Test concept counting."""
        metrics = ProcessingMetrics()

        assert metrics.concepts_generated == 0

        metrics.add_concepts(3)
        assert metrics.concepts_generated == 3

        metrics.add_concepts(2)
        assert metrics.concepts_generated == 5

    def test_total_duration(self):
        """Test total duration calculation."""
        metrics = ProcessingMetrics()

        # Add a small delay to ensure some duration
        time.sleep(0.01)
        duration = metrics.total_duration

        assert duration > 0  # Should have some positive duration

    def test_avg_tokens_per_section_with_sections(self):
        """Test average tokens per section calculation."""
        metrics = ProcessingMetrics()

        metrics.llm_metrics.add_summary_call(200)
        metrics.llm_metrics.add_concept_call(100)
        metrics.add_section()
        metrics.add_section()

        assert metrics.avg_tokens_per_section == 150.0  # 300 tokens / 2 sections

    def test_avg_tokens_per_section_no_sections(self):
        """Test average tokens per section with zero sections."""
        metrics = ProcessingMetrics()

        metrics.llm_metrics.add_summary_call(200)

        assert metrics.avg_tokens_per_section == 0

    def test_rich_table_formatting(self):
        """Test Rich table formatting produces output."""
        metrics = ProcessingMetrics()

        # Add some test data
        metrics.llm_metrics.add_summary_call(200)
        metrics.llm_metrics.add_concept_call(100)
        start_time = metrics.start_pass(1)
        time.sleep(0.01)  # Small delay for timing
        metrics.end_pass(1, start_time)
        metrics.add_section()
        metrics.add_section()
        metrics.add_concepts(5)

        # Test table formatting
        table_output = metrics.format_stats_table()

        # Verify table contains expected content structure
        assert "Processing Statistics" in table_output
        assert "LLM Calls" in table_output
        assert "2 calls" in table_output  # total calls
        assert "1 calls" in table_output  # summary and concept calls each
        assert "300 tokens" in table_output  # total tokens
        assert "Pass 1 Duration" in table_output
        assert "2 sections" in table_output
        assert "5 concepts" in table_output
        assert "150 tokens" in table_output  # tokens per section
        # Don't check exact timing values since they're real

    def test_rich_table_formatting_empty_data(self):
        """Test Rich table formatting with empty data."""
        metrics = ProcessingMetrics()

        table_output = metrics.format_stats_table()

        # Verify table handles empty data gracefully
        assert "Processing Statistics" in table_output
        assert "0 calls" in table_output
        assert "0 tokens" in table_output
        assert "0 sections" in table_output
        assert "0 concepts" in table_output
        # Should not show tokens per section when no sections
        assert "avg tokens" not in table_output or "0 avg tokens" in table_output
