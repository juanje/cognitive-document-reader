"""Command-line interface for Cognitive Document Reader."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

import click

from ..core.progressive_reader import CognitiveReader
from ..models.config import ReadingConfig
from ..models.document import DocumentKnowledge
from ..models.knowledge import LanguageCode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.command()
@click.argument(
    "document", type=click.Path(exists=True, path_type=Path), required=False
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default="markdown",
    help="Output format for results (default: markdown)",
)
@click.option(
    "--language",
    "-l",
    type=click.Choice(["auto", "en", "es"], case_sensitive=False),
    default="auto",
    help="Document language (default: auto-detect)",
)
@click.option(
    "--model", "-m", type=str, help="LLM model to use (overrides environment config)"
)
@click.option(
    "--fast-mode", is_flag=True, help="Use fast model for quicker processing"
)
@click.option(
    "--temperature", "-t", type=float, help="Temperature for LLM generation (0.0-2.0)"
)
@click.option(
    "--dry-run", is_flag=True, help="Run in dry-run mode (no actual LLM calls)"
)
@click.option("--mock-responses", is_flag=True, help="Use mock responses for testing")
@click.option(
    "--validate-config",
    is_flag=True,
    help="Only validate configuration, don't process document",
)
@click.option(
    "--output-file",
    "-f",
    type=click.Path(path_type=Path),
    help="Save output to file instead of stdout",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except results")
@click.version_option()
def cli(
    document: Path | None,
    output: str,
    language: str,
    model: str | None,
    fast_mode: bool,
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
    output_file: Path | None,
    verbose: bool,
    quiet: bool,
) -> None:
    """Cognitive Document Reader - Human-like document understanding.

    Process documents with progressive understanding and hierarchical synthesis.
    Supports Markdown files and provides structured summaries for human reading
    and enriched metadata for AI projects.

    Examples:

        # Basic usage
        cognitive-reader document.md

        # JSON output to file
        cognitive-reader document.md --output json -f analysis.json

        # Spanish document with specific model
        cognitive-reader documento.md --language es --model qwen3:8b

        # Development modes
        cognitive-reader document.md --dry-run
        cognitive-reader --validate-config
    """
    # Configure logging based on verbosity
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Run the async main function
        asyncio.run(
            _async_main(
                document=document,
                output=output,
                language=language,
                model=model,
                fast_mode=fast_mode,
                temperature=temperature,
                dry_run=dry_run,
                mock_responses=mock_responses,
                validate_config=validate_config,
                output_file=output_file,
                verbose=verbose,
                quiet=quiet,
            )
        )
    except KeyboardInterrupt:
        if not quiet:
            click.echo("\nOperation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        if not quiet:
            click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


async def _async_main(
    document: Path | None,
    output: str,
    language: str,
    model: str | None,
    fast_mode: bool,
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
    output_file: Path | None,
    verbose: bool,
    quiet: bool,
) -> None:
    """Async main function for CLI operations."""

    # Build configuration
    config = _build_config(
        language=language,
        model=model,
        fast_mode=fast_mode,
        temperature=temperature,
        dry_run=dry_run,
        mock_responses=mock_responses,
        validate_config=validate_config,
    )

    # Initialize reader
    reader = CognitiveReader(config)

    # Handle validation-only mode
    if validate_config:
        if not quiet:
            click.echo("Validating configuration...")

        is_valid = await reader.validate_configuration()

        if is_valid:
            if not quiet:
                click.echo("✅ Configuration is valid and ready for processing")
            # Return success for validation mode
            return
        else:
            raise click.ClickException("❌ Configuration validation failed")

    # Require document for processing modes
    if not document:
        raise click.UsageError(
            "Document argument is required unless using --validate-config"
        )

    if not quiet:
        click.echo(f"Processing document: {document}")
        if config.is_development_mode():
            dev_modes = []
            if config.dry_run:
                dev_modes.append("dry-run")
            if config.mock_responses:
                dev_modes.append("mock-responses")
            click.echo(f"Development mode: {', '.join(dev_modes)}")

    # Process the document
    knowledge = await reader.read_document(document)

    # Generate output
    if output.lower() == "json":
        output_text = _format_json_output(knowledge)
    else:
        output_text = _format_markdown_output(knowledge)

    # Save or display output
    if output_file:
        _save_output(output_text, output_file, quiet)
    else:
        click.echo(output_text)

    if not quiet:
        total_sections = len(knowledge.sections)
        total_summaries = len(knowledge.section_summaries)
        click.echo(
            f"\n✅ Processing completed: {total_sections} sections, {total_summaries} summaries",
            err=True,
        )


def _build_config(
    language: str,
    model: str | None,
    fast_mode: bool,
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
) -> ReadingConfig:
    """Build configuration from CLI options and environment."""

    # Start with environment configuration
    config_dict: dict[str, Any] = {}

    # Override with CLI options
    if model:
        # Legacy support: if --model is specified, use it for both fast and quality
        config_dict["fast_model"] = model
        config_dict["quality_model"] = model
    if fast_mode:
        config_dict["fast_mode"] = fast_mode
    if temperature is not None:
        config_dict["temperature"] = temperature
    if language != "auto":
        config_dict["document_language"] = LanguageCode(language)

    # Development modes
    config_dict["dry_run"] = dry_run
    config_dict["mock_responses"] = mock_responses
    config_dict["validate_config_only"] = validate_config

    # Create configuration
    base_config = ReadingConfig.from_env()

    # Apply overrides
    if config_dict:
        config = base_config.model_copy(update=config_dict)
    else:
        config = base_config

    return config


def _format_json_output(knowledge: DocumentKnowledge) -> str:
    """Format knowledge as JSON output."""
    # Convert to dict for JSON serialization
    output_dict = {
        "document_title": knowledge.document_title,
        "document_summary": knowledge.document_summary,
        "detected_language": knowledge.detected_language.value,
        "sections": [
            {
                "id": section.id,
                "title": section.title,
                "level": section.level,
                "parent_id": section.parent_id,
                "children_ids": section.children_ids,
                "order_index": section.order_index,
                "content_preview": section.content[:200] + "..."
                if len(section.content) > 200
                else section.content,
            }
            for section in knowledge.sections
        ],
        "section_summaries": {
            section_id: {
                "title": summary.title,
                "summary": summary.summary,
                "key_concepts": summary.key_concepts,
                "confidence_score": summary.confidence_score,
            }
            for section_id, summary in knowledge.section_summaries.items()
        },
        "processing_metadata": knowledge.processing_metadata,
    }

    return json.dumps(output_dict, indent=2, ensure_ascii=False)


def _format_markdown_output(knowledge: DocumentKnowledge) -> str:
    """Format knowledge as enhanced Markdown output."""
    lines = []

    # Title and summary
    lines.append(f"# {knowledge.document_title}")
    lines.append("")
    lines.append("## Document Summary")
    lines.append("")
    lines.append(knowledge.document_summary)
    lines.append("")

    # Metadata
    lines.append("## Processing Information")
    lines.append("")
    lines.append(f"- **Language**: {knowledge.detected_language.value}")
    lines.append(f"- **Total Sections**: {len(knowledge.sections)}")
    lines.append(f"- **Total Summaries**: {len(knowledge.section_summaries)}")

    if knowledge.processing_metadata:
        for key, value in knowledge.processing_metadata.items():
            if key not in ["total_sections", "total_summaries"]:
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines.append("")

    # Section summaries
    if knowledge.section_summaries:
        lines.append("## Section Analysis")
        lines.append("")

        # Get sections ordered by appearance
        ordered_sections = sorted(knowledge.sections, key=lambda s: s.order_index)

        for section in ordered_sections:
            if section.id in knowledge.section_summaries:
                summary = knowledge.section_summaries[section.id]

                # Section header with level indication
                level_prefix = "#" * (min(section.level + 2, 6))  # Max heading level 6
                lines.append(f"{level_prefix} {summary.title}")
                lines.append("")

                # Summary
                lines.append(f"**Summary**: {summary.summary}")
                lines.append("")

                # Key concepts
                if summary.key_concepts:
                    concepts_text = ", ".join(summary.key_concepts)
                    lines.append(f"**Key Concepts**: {concepts_text}")
                    lines.append("")

                # Confidence score
                if summary.confidence_score < 1.0:
                    lines.append(f"**Confidence**: {summary.confidence_score:.2f}")
                    lines.append("")

    # Document structure
    lines.append("## Document Structure")
    lines.append("")

    # Build hierarchical view
    def add_section_tree(section: Any, indent: int = 0) -> None:
        prefix = "  " * indent + "- "
        lines.append(f"{prefix}{section.title} (Level {section.level})")

        # Add children
        children = [s for s in knowledge.sections if s.parent_id == section.id]
        children.sort(key=lambda s: s.order_index)
        for child in children:
            add_section_tree(child, indent + 1)

    # Find root sections (no parent)
    root_sections = [s for s in knowledge.sections if s.parent_id is None]
    root_sections.sort(key=lambda s: s.order_index)

    for root in root_sections:
        add_section_tree(root)

    return "\n".join(lines)


def _save_output(content: str, output_file: Path, quiet: bool) -> None:
    """Save output content to file."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        if not quiet:
            click.echo(f"Output saved to: {output_file}", err=True)
    except Exception as e:
        raise click.ClickException(f"Failed to save output to {output_file}: {e}")


if __name__ == "__main__":
    cli()
