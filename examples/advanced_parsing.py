"""Advanced document parsing examples with docling integration."""

from __future__ import annotations

import asyncio
from pathlib import Path

from cognitive_reader import CognitiveReader
from cognitive_reader.models import ReadingConfig
from cognitive_reader.parsers.docling_parser import DoclingParser


async def test_parser_capabilities():
    """Test and demonstrate parser capabilities."""
    print("=== Parser Capabilities Test ===")

    # Initialize parser
    parser = DoclingParser()

    # Get parser information
    info = parser.get_parser_info()
    print("Parser Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    print(f"\nSupported formats: {parser.get_supported_formats()}")
    print(f"Docling available: {parser.is_docling_available()}")

    if parser.is_docling_available():
        print("✅ Enhanced parsing available (PDF, DOCX, HTML, Markdown)")
    else:
        print("⚠️  Fallback mode (Markdown only)")
        print("   To enable full parsing capabilities, install docling:")
        print("   pip install 'docling>=2.40'")


async def test_markdown_parsing():
    """Test basic Markdown parsing (always available)."""
    print("\n=== Markdown Parsing Test ===")

    # Create test markdown content
    test_markdown = """# Advanced Document Processing

## Overview

This document demonstrates the cognitive document reader's capabilities.

### Key Features

- **Progressive Reading**: Processes documents in order
- **Hierarchical Synthesis**: Builds understanding from parts to whole
- **Multi-format Support**: PDF, DOCX, HTML, Markdown (when docling available)

### Technical Architecture

The system uses:

1. **Universal Parser**: Docling for multiple formats
2. **Structure Detection**: Hierarchical section analysis
3. **Cognitive Processing**: Human-like understanding

## Implementation Details

### Parser Strategy

The parser uses an intelligent fallback strategy:

- Primary: Docling for PDF, DOCX, HTML
- Fallback: Built-in Markdown parser
- Output: Consistent Markdown structure

### Benefits

This approach provides:
- **Reliability**: Always works with Markdown
- **Flexibility**: Enhanced capabilities when available
- **Consistency**: Unified processing pipeline

## Conclusion

The cognitive document reader provides robust document processing
with intelligent format detection and fallback mechanisms.
"""

    # Test with cognitive reader
    config = ReadingConfig(dry_run=True, mock_responses=True)
    reader = CognitiveReader(config)

    print("Processing test document...")
    knowledge = await reader.read_document_text(
        test_markdown, "Advanced Document Processing"
    )

    print("✅ Document processed successfully")
    print(f"   Title: {knowledge.document_title}")
    print(f"   Language: {knowledge.detected_language.value}")
    print(f"   Sections: {len(knowledge.sections)}")
    print(f"   Summaries: {len(knowledge.section_summaries)}")

    # Show hierarchy
    print("\n📋 Document Structure:")
    top_sections = knowledge.get_top_level_sections()
    for section in top_sections:
        print(f"   - {section.title} (Level {section.level})")
        children = knowledge.get_children_of_section(section.id)
        for child in children:
            print(f"     - {child.title} (Level {child.level})")


async def test_enhanced_parsing():
    """Test enhanced parsing capabilities (requires docling)."""
    print("\n=== Enhanced Parsing Test ===")

    parser = DoclingParser()

    if not parser.is_docling_available():
        print("⚠️  Docling not available - this test requires docling installation")
        print("   To enable enhanced parsing:")
        print("   1. Install docling: pip install 'docling>=2.40'")
        print("   2. Restart the application")
        print("   3. The parser will automatically detect and use docling")
        return

    print("✅ Docling available - enhanced parsing enabled")
    print(f"   Supported formats: {parser.get_supported_formats()}")

    # Test with various file types (if docling is available)
    test_files = [
        ("sample.pdf", "PDF document parsing"),
        ("sample.docx", "DOCX document parsing"),
        ("sample.html", "HTML document parsing"),
    ]

    for filename, description in test_files:
        print(f"\n📄 {description}:")
        file_path = Path(filename)

        if file_path.exists():
            try:
                title, sections = await parser.parse_document(file_path)
                print(f"   ✅ Successfully parsed {filename}")
                print(f"   📝 Title: {title}")
                print(f"   📊 Sections found: {len(sections)}")
            except Exception as e:
                print(f"   ❌ Failed to parse {filename}: {e}")
        else:
            print(f"   ⚠️  File not found: {filename} (demo only)")


async def demonstrate_installation_detection():
    """Demonstrate how the system detects and adapts to available libraries."""
    print("\n=== Installation Detection Demo ===")

    print("The parser automatically adapts to available libraries:")
    print()

    # Test different scenarios
    scenarios = [
        {
            "condition": "Docling not installed",
            "behavior": "Falls back to Markdown-only parsing",
            "formats": [".md", ".markdown"],
            "advantages": "Always works, no dependencies",
        },
        {
            "condition": "Docling installed and working",
            "behavior": "Full multi-format parsing enabled",
            "formats": [".md", ".markdown", ".pdf", ".docx", ".html"],
            "advantages": "Universal document support, robust parsing",
        },
        {
            "condition": "Docling installed but misconfigured",
            "behavior": "Graceful fallback to Markdown parsing",
            "formats": [".md", ".markdown"],
            "advantages": "Fault tolerance, no application crashes",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. **{scenario['condition']}**")
        print(f"   Behavior: {scenario['behavior']}")
        print(f"   Formats: {', '.join(scenario['formats'])}")
        print(f"   Advantages: {scenario['advantages']}")
        print()

    # Show current status
    parser = DoclingParser()
    current_info = parser.get_parser_info()

    print("🔍 Current System Status:")
    if current_info["enhanced_parsing"]:
        print("   ✅ Enhanced parsing active (Scenario 2)")
    elif current_info["fallback_mode"]:
        print("   ⚠️  Fallback mode active (Scenario 1)")

    print(f"   📊 Available formats: {', '.join(current_info['supported_formats'])}")


async def main():
    """Run all parsing examples and demonstrations."""
    print("🔥 Advanced Document Parsing Examples")
    print("=" * 50)

    await test_parser_capabilities()
    await test_markdown_parsing()
    await test_enhanced_parsing()
    await demonstrate_installation_detection()

    print("\n" + "=" * 50)
    print("✅ All examples completed!")
    print("\n💡 Key Takeaways:")
    print("   • Parser works in all environments (fallback strategy)")
    print("   • Install docling for enhanced multi-format support")
    print("   • Consistent processing pipeline regardless of backend")
    print("   • Automatic detection and graceful degradation")


if __name__ == "__main__":
    asyncio.run(main())
