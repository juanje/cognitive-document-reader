"""Processing metrics tracking for cognitive document reading."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table


def _format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds:.0f}s"


@dataclass
class LLMCallMetrics:
    """Metrics for different types of LLM calls."""

    summary_calls: int = 0
    summary_tokens: int = 0
    concept_calls: int = 0
    concept_tokens: int = 0

    def add_summary_call(self, tokens: int) -> None:
        """Add a summary generation call."""
        self.summary_calls += 1
        self.summary_tokens += tokens

    def add_concept_call(self, tokens: int) -> None:
        """Add a concept extraction call."""
        self.concept_calls += 1
        self.concept_tokens += tokens

    @property
    def total_calls(self) -> int:
        """Total number of LLM calls."""
        return self.summary_calls + self.concept_calls

    @property
    def total_tokens(self) -> int:
        """Total tokens sent across all calls."""
        return self.summary_tokens + self.concept_tokens

    @property
    def avg_summary_tokens(self) -> float:
        """Average tokens per summary call."""
        return self.summary_tokens / self.summary_calls if self.summary_calls > 0 else 0

    @property
    def avg_concept_tokens(self) -> float:
        """Average tokens per concept call."""
        return self.concept_tokens / self.concept_calls if self.concept_calls > 0 else 0

    @property
    def avg_tokens_per_call(self) -> float:
        """Average tokens across all calls."""
        return self.total_tokens / self.total_calls if self.total_calls > 0 else 0


@dataclass
class ProcessingMetrics:
    """Comprehensive processing metrics for cognitive reading."""

    # LLM metrics
    llm_metrics: LLMCallMetrics = field(default_factory=LLMCallMetrics)

    # Timing metrics
    start_time: float = field(default_factory=time.time)
    pass_durations: dict[int, float] = field(default_factory=dict)

    # Content metrics
    sections_processed: int = 0
    concepts_generated: int = 0

    def start_pass(self, pass_number: int) -> float:
        """Start timing a processing pass."""
        pass_start = time.time()
        return pass_start

    def end_pass(self, pass_number: int, pass_start_time: float) -> float:
        """End timing a processing pass and record duration."""
        duration = time.time() - pass_start_time
        self.pass_durations[pass_number] = duration
        return duration

    def add_section(self) -> None:
        """Increment sections processed count."""
        self.sections_processed += 1

    def add_concepts(self, count: int) -> None:
        """Add to concepts generated count."""
        self.concepts_generated += count

    @property
    def total_duration(self) -> float:
        """Total processing duration."""
        return time.time() - self.start_time

    @property
    def avg_tokens_per_section(self) -> float:
        """Average tokens sent per section processed."""
        return (
            self.llm_metrics.total_tokens / self.sections_processed
            if self.sections_processed > 0
            else 0
        )

    def format_stats_table(self) -> str:
        """Format metrics as a beautiful Rich table."""
        table = Table(
            title="Processing Statistics", show_header=False, box=None, padding=(0, 1)
        )

        # Add columns: metric name and value
        table.add_column("Metric", style="bold cyan", justify="left")
        table.add_column("Value", style="green", justify="right")

        # LLM Call metrics
        table.add_row("LLM Calls", f"{self.llm_metrics.total_calls:,} calls")
        table.add_row("  Summary Calls", f"{self.llm_metrics.summary_calls:,} calls")
        table.add_row("  Concept Calls", f"{self.llm_metrics.concept_calls:,} calls")

        # Token metrics (grouped together)
        table.add_row("", "")  # Separator
        table.add_row("Total Tokens Sent", f"{self.llm_metrics.total_tokens:,} tokens")
        if self.llm_metrics.summary_calls > 0:
            table.add_row(
                "  Avg Summary", f"{self.llm_metrics.avg_summary_tokens:.0f} tokens"
            )
        if self.llm_metrics.concept_calls > 0:
            table.add_row(
                "  Avg Concepts", f"{self.llm_metrics.avg_concept_tokens:.0f} tokens"
            )
        if self.sections_processed > 0:
            table.add_row(
                "  Avg per Section", f"{self.avg_tokens_per_section:.0f} tokens"
            )

        # Timing metrics (grouped together)
        table.add_row("", "")  # Separator
        for pass_num, duration in sorted(self.pass_durations.items()):
            table.add_row(f"Pass {pass_num} Duration", _format_duration(duration))

        table.add_row("Total Duration", _format_duration(self.total_duration))

        # Content metrics
        table.add_row("", "")  # Separator
        table.add_row("Sections Processed", f"{self.sections_processed:,} sections")
        table.add_row("Concepts Generated", f"{self.concepts_generated:,} concepts")

        # Render table to string
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
