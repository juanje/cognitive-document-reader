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
from ..models.config import CognitiveConfig
from ..models.document import CognitiveKnowledge
from ..models.knowledge import LanguageCode
from ..utils.structure_formatter import (
    filter_sections_by_depth,
    format_structure_as_text,
    validate_structure_integrity,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress noisy HTTP logs by default (only show in verbose mode)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("langsmith").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)
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
@click.option(
    "--save-partials",
    is_flag=True,
    help="Save partial results as sections are processed",
)
@click.option(
    "--partials-dir",
    type=click.Path(path_type=Path),
    help="Directory to save partial results (default: ./partial_results)",
)
@click.option(
    "--max-sections",
    type=int,
    help="Maximum number of sections to process (for testing with large docs)",
)
@click.option(
    "--max-depth",
    type=int,
    help="Maximum section depth level to analyze (avoid deep hierarchies)",
)
@click.option(
    "--structure-only",
    is_flag=True,
    help="Show only document structure without processing summaries",
)
@click.option(
    "--fast-mode",
    is_flag=True,
    help="Use fast model for processing - optimizes for speed over quality",
)
@click.option(
    "--disable-reasoning",
    is_flag=True,
    help="Disable reasoning mode for reasoning models (faster processing, direct answers)",
)
@click.option(
    "--skip-glossary",
    is_flag=True,
    help="Skip concept definitions generation (faster processing, summaries only)",
)
@click.version_option()
def cli(
    document: Path | None,
    output: str,
    language: str,
    model: str | None,
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
    output_file: Path | None,
    verbose: bool,
    quiet: bool,
    save_partials: bool,
    partials_dir: Path | None,
    max_sections: int | None,
    max_depth: int | None,  # ✅ WORKING: for --structure-only
    structure_only: bool,
    fast_mode: bool,
    disable_reasoning: bool,
    skip_glossary: bool,
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

        # Show only document structure (fast, no LLM processing)

        cognitive-reader document.md --structure-only

        # Show structure limited to depth 2 (first two hierarchy levels)

        cognitive-reader document.md --structure-only --max-depth 2

        # Verbose mode to see document structure before processing

        cognitive-reader document.md --verbose

        # Process with custom temperature

        cognitive-reader document.md --temperature 0.2
    """
    # Configure logging based on verbosity
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        # Enable DEBUG for cognitive_reader logs only, keep HTTP libs minimal
        logging.getLogger().setLevel(logging.INFO)  # Keep root at INFO
        logging.getLogger("cognitive_reader").setLevel(logging.DEBUG)

        # In verbose mode, allow some HTTP logs but not the noisy DEBUG ones
        logging.getLogger("httpcore").setLevel(logging.WARNING)  # Still quiet
        logging.getLogger("httpx").setLevel(logging.INFO)  # Show HTTP requests
        logging.getLogger("langsmith").setLevel(logging.WARNING)  # Still quiet
        logging.getLogger("langchain").setLevel(logging.INFO)

    try:
        # Run the async main function
        asyncio.run(
            _async_main(
                document=document,
                output=output,
                language=language,
                model=model,
                temperature=temperature,
                dry_run=dry_run,
                mock_responses=mock_responses,
                validate_config=validate_config,
                output_file=output_file,
                verbose=verbose,
                quiet=quiet,
                save_partials=save_partials,
                partials_dir=partials_dir,
                max_sections=max_sections,
                max_depth=max_depth,  # ✅ WORKING
                structure_only=structure_only,
                fast_mode=fast_mode,
                disable_reasoning=disable_reasoning,
                skip_glossary=skip_glossary,
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
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
    output_file: Path | None,
    verbose: bool,
    quiet: bool,
    save_partials: bool,
    partials_dir: Path | None,
    max_sections: int | None,
    max_depth: int | None,  # ✅ WORKING
    structure_only: bool,
    fast_mode: bool,
    disable_reasoning: bool,
    skip_glossary: bool,
) -> None:
    """Async main function for CLI operations."""

    # Build configuration
    config = _build_config(
        language=language,
        model=model,
        temperature=temperature,
        dry_run=dry_run,
        mock_responses=mock_responses,
        validate_config=validate_config,
        save_partials=save_partials,
        partials_dir=partials_dir,
        max_sections=max_sections,
        max_depth=max_depth,  # ✅ WORKING
        fast_mode=fast_mode,
        disable_reasoning=disable_reasoning,
        skip_glossary=skip_glossary,
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
            # TODO: Phase 2 - Re-implement these development features:
            # if config.save_partial_results:
            #     dev_modes.append("save-partials")
            if config.max_sections:
                dev_modes.append(f"max-sections={config.max_sections}")

            # Show max-depth when filtering is active (not default high value)
            if (
                config.max_hierarchy_depth and config.max_hierarchy_depth < 10
            ):  # Show when filtering
                dev_modes.append(f"max-depth={config.max_hierarchy_depth}")

            click.echo(f"Development mode: {', '.join(dev_modes)}")
            # TODO: Phase 2 - Re-implement:
            # if config.save_partial_results:
            #     click.echo(f"Partial results will be saved to: {config.partial_results_dir}")

    # Handle structure-only mode
    if structure_only:
        # Parse document to extract structure without any LLM processing
        document_title, sections = await reader.parser.parse_text(
            document.read_text(encoding="utf-8"), document.name
        )

        # Apply depth filtering if specified
        if config.max_hierarchy_depth:
            sections = filter_sections_by_depth(sections, config.max_hierarchy_depth)

        # Simply show the clean structure tree (headings only)
        structure_output = format_structure_as_text(sections, headings_only=True)

        # Output to file or console
        if output_file:
            output_file.write_text(structure_output, encoding="utf-8")
        else:
            click.echo(structure_output)

        return

    # Show structure in verbose mode before processing
    if verbose and not quiet:
        # Parse document to extract structure for preview
        document_title, sections = await reader.parser.parse_text(
            document.read_text(encoding="utf-8"), document.name
        )

        # Apply depth filtering if specified
        display_sections = sections
        if config.max_hierarchy_depth:
            display_sections = filter_sections_by_depth(
                sections, config.max_hierarchy_depth
            )
            if len(display_sections) < len(sections):
                click.echo(
                    f"📋 Document Structure (showing depth ≤ {config.max_hierarchy_depth}):"
                )
            else:
                click.echo("📋 Document Structure:")
        else:
            click.echo("📋 Document Structure:")

        structure_tree = format_structure_as_text(display_sections, headings_only=True)
        # Indent the structure tree for better visual separation
        for line in structure_tree.split("\n"):
            if line.strip():  # Only indent non-empty lines
                click.echo(f"   {line}")

        # Show validation issues if any (on full structure, not filtered)
        issues = validate_structure_integrity(sections)
        if issues:
            click.echo("⚠️  Structure issues detected:")
            for issue in issues:
                click.echo(f"   - {issue}")

        click.echo()  # Add spacing before processing starts

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
        total_sections = knowledge.total_sections
        total_summaries = len(knowledge.hierarchical_summaries)
        click.echo(
            f"\n✅ Processing completed: {total_sections} sections, {total_summaries} summaries",
            err=True,
        )


def _build_config(
    language: str,
    model: str | None,
    temperature: float | None,
    dry_run: bool,
    mock_responses: bool,
    validate_config: bool,
    save_partials: bool,
    partials_dir: Path | None,
    max_sections: int | None,
    max_depth: int | None,  # ✅ WORKING
    fast_mode: bool,
    disable_reasoning: bool,
    skip_glossary: bool,
) -> CognitiveConfig:
    """Build configuration from CLI options and environment."""

    # Create configuration
    base_config = CognitiveConfig.from_env()

    # Start with environment configuration
    config_dict: dict[str, Any] = {}

    # Override with CLI options
    if model:
        config_dict["model_name"] = model
        # If --model is specified, override fast_pass_model
        config_dict["fast_pass_model"] = model
        # If --model is specified, override the main model
        config_dict["main_model"] = model

    # Fast mode: use fast model for processing (optimizes for speed over quality)
    if fast_mode:
        fast_model = base_config.fast_pass_model
        config_dict["main_model"] = fast_model
        # Use fast temperature settings
        config_dict["main_pass_temperature"] = base_config.fast_pass_temperature

    if temperature is not None:
        config_dict["temperature"] = temperature
    if language != "auto":
        config_dict["document_language"] = LanguageCode(language)

    # Development modes
    config_dict["dry_run"] = dry_run
    config_dict["mock_responses"] = mock_responses
    config_dict["validate_config_only"] = validate_config
    config_dict["disable_reasoning"] = disable_reasoning
    config_dict["skip_glossary"] = skip_glossary

    # Development and testing features
    # Apply CLI overrides
    config_dict["save_partial_results"] = save_partials
    if partials_dir is not None:
        config_dict["partial_results_dir"] = str(partials_dir)
    if max_sections is not None:
        config_dict["max_sections"] = max_sections

    # ✅ WORKING: max_depth with --structure-only
    if max_depth is not None:
        config_dict["max_hierarchy_depth"] = max_depth

    # Apply overrides
    if config_dict:
        config = base_config.model_copy(update=config_dict)
    else:
        config = base_config

    return config


def _format_json_output(knowledge: CognitiveKnowledge) -> str:
    """Format knowledge as JSON output according to SPECS v2.0."""
    # Convert to dict for JSON serialization using v2.0 structure
    output_dict = {
        "document_title": knowledge.document_title,
        "document_summary": knowledge.document_summary,
        "detected_language": knowledge.detected_language.value,
        "hierarchical_summaries": {
            section_id: {
                "title": summary.title,
                "summary": summary.summary,
                "key_concepts": summary.key_concepts,
                "level": summary.level,
                "order_index": summary.order_index,
                "parent_id": summary.parent_id,
                "children_ids": summary.children_ids,
            }
            for section_id, summary in knowledge.hierarchical_summaries.items()
        },
        "concepts": [
            {
                "concept_id": concept.concept_id,
                "name": concept.name,
                "definition": concept.definition,
                "first_mentioned_in": concept.first_mentioned_in,
                "relevant_sections": concept.relevant_sections,
            }
            for concept in knowledge.concepts
        ],
        "hierarchy_index": knowledge.hierarchy_index,
        "parent_child_map": knowledge.parent_child_map,
        "statistics": {
            "total_sections": knowledge.total_sections,
            "avg_summary_length": knowledge.avg_summary_length,
            "total_concepts": knowledge.total_concepts,
        },
    }

    return json.dumps(output_dict, indent=2, ensure_ascii=False)


def _format_markdown_output(knowledge: CognitiveKnowledge) -> str:
    """Format knowledge as enhanced Markdown output according to SPECS v2.0."""
    lines = []

    # Title
    lines.append(f"# {knowledge.document_title}")
    lines.append("")

    # Document Summary
    lines.append("## Document Summary")
    lines.append("")
    lines.append(knowledge.document_summary)
    lines.append("")

    # Processing Information
    lines.append("## Processing Information")
    lines.append("")
    lines.append(f"- **Language**: {knowledge.detected_language.value}")
    lines.append(f"- **Total Sections**: {knowledge.total_sections}")
    lines.append(f"- **Total Concepts**: {knowledge.total_concepts}")
    lines.append(
        f"- **Average Summary Length**: {knowledge.avg_summary_length} characters"
    )
    lines.append("")

    # Section Analysis (ordered summaries)
    if knowledge.hierarchical_summaries:
        lines.append("## Section Analysis")
        lines.append("")

        # Get summaries ordered by order_index
        ordered_summaries = sorted(
            knowledge.hierarchical_summaries.values(), key=lambda s: s.order_index
        )

        for summary in ordered_summaries:
            # Section header with level indication
            level_prefix = "#" * (min(summary.level + 2, 6))  # Max heading level 6
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

    # Concepts Glossary
    if knowledge.concepts:
        lines.append("## Concepts Glossary")
        lines.append("")

        for concept in knowledge.concepts:
            lines.append(f"### {concept.name}")
            lines.append("")
            lines.append(f"**Definition**: {concept.definition}")
            lines.append("")
            if concept.relevant_sections:
                sections_text = ", ".join(concept.relevant_sections)
                lines.append(f"**Found in sections**: {sections_text}")
                lines.append("")

    # TODO: Phase 2 - Document Structure using hierarchy_index and parent_child_map
    # Removed empty structure section until Phase 2 implementation

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
