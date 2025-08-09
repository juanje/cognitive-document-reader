"""Basic usage examples for Cognitive Document Reader."""

from __future__ import annotations

import asyncio
from pathlib import Path

from cognitive_reader import CognitiveReader
from cognitive_reader.models import ReadingConfig
from cognitive_reader.models.knowledge import LanguageCode


async def basic_example():
    """Basic usage example with default configuration."""
    print("=== Basic Usage Example ===")

    # Create configuration (loads from environment or uses defaults)
    config = ReadingConfig.from_env()

    # Enable development mode for this example
    config = config.model_copy(
        update={
            "dry_run": True,  # No real LLM calls
            "mock_responses": True,  # Use simulated responses
        }
    )

    # Initialize the cognitive reader
    reader = CognitiveReader(config)

    # Sample markdown content
    sample_text = """# Sample Document

## Introduction

This is a sample document to demonstrate the Cognitive Document Reader.
It shows how the system processes hierarchical content progressively.

## Main Content

### Technical Overview

The cognitive reader simulates human-like understanding by:
- Processing sections in order
- Accumulating context progressively
- Building hierarchical knowledge structures

### Key Features

- Progressive reading with context accumulation
- Hierarchical synthesis from sections to document
- Multi-language support (English and Spanish)
- Development-friendly modes for testing

## Conclusion

This example demonstrates the basic functionality of cognitive document reading.
The system provides structured summaries suitable for both human reading and AI applications.
"""

    # Process the document
    print("Processing document...")
    knowledge = await reader.read_document_text(sample_text, "Sample Document")

    # Display results
    print(f"\nDocument Title: {knowledge.document_title}")
    print(f"Language: {knowledge.detected_language.value}")
    print(f"Total Sections: {len(knowledge.sections)}")
    print(f"Total Summaries: {len(knowledge.section_summaries)}")

    print("\nDocument Summary:")
    print(knowledge.document_summary)

    print("\nSection Summaries:")
    for section_id, summary in knowledge.section_summaries.items():
        print(f"\n- {summary.title}")
        print(f"  Summary: {summary.summary}")
        if summary.key_concepts:
            print(f"  Key Concepts: {', '.join(summary.key_concepts)}")


async def configuration_example():
    """Example showing different configuration options."""
    print("\n=== Configuration Example ===")

    # Custom configuration
    config = ReadingConfig(
        model_name="llama3.1:8b",
        temperature=0.1,
        chunk_size=800,
        chunk_overlap=160,
        document_language=LanguageCode.EN,
        dry_run=True,  # Development mode
        mock_responses=True,
    )

    reader = CognitiveReader(config)

    # Validate configuration
    is_valid = await reader.validate_configuration()
    print(f"Configuration valid: {is_valid}")

    # Check dependencies
    deps_ok = reader.check_dependencies()
    print(f"Dependencies OK: {deps_ok}")


async def spanish_example():
    """Example with Spanish content."""
    print("\n=== Spanish Document Example ===")

    config = ReadingConfig(
        document_language=LanguageCode.AUTO,  # Auto-detect
        dry_run=True,
        mock_responses=True,
    )

    reader = CognitiveReader(config)

    spanish_text = """# Documento de Ejemplo

## Introducción

Este es un documento de ejemplo para demostrar el Lector Cognitivo de Documentos.
Muestra cómo el sistema procesa contenido jerárquico de manera progresiva.

## Contenido Principal

### Visión Técnica

El lector cognitivo simula la comprensión humana mediante:
- Procesamiento de secciones en orden
- Acumulación progresiva de contexto
- Construcción de estructuras jerárquicas de conocimiento

## Conclusión

Este ejemplo demuestra la funcionalidad básica de la lectura cognitiva de documentos.
El sistema proporciona resúmenes estructurados adecuados tanto para lectura humana como para aplicaciones de IA.
"""

    knowledge = await reader.read_document_text(spanish_text, "Documento de Ejemplo")

    print(f"Título: {knowledge.document_title}")
    print(f"Idioma detectado: {knowledge.detected_language.value}")
    print(f"Resumen: {knowledge.document_summary}")


async def file_processing_example():
    """Example processing a markdown file (if it exists)."""
    print("\n=== File Processing Example ===")

    config = ReadingConfig(dry_run=True, mock_responses=True)
    reader = CognitiveReader(config)

    # Create a sample file for demonstration
    sample_file = Path("sample_document.md")

    sample_content = """# Machine Learning Fundamentals

## Overview

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

## Core Concepts

### Supervised Learning

In supervised learning, algorithms learn from labeled training data to make predictions on new, unseen data.

### Unsupervised Learning

Unsupervised learning finds hidden patterns in data without labeled examples.

### Deep Learning

Deep learning uses neural networks with multiple layers to model complex patterns in data.

## Applications

Machine learning has applications in:
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles

## Conclusion

Understanding these fundamentals provides a foundation for exploring more advanced machine learning topics.
"""

    try:
        # Write sample file
        sample_file.write_text(sample_content, encoding="utf-8")

        # Process the file
        print(f"Processing file: {sample_file}")
        knowledge = await reader.read_document(sample_file)

        print(f"Document: {knowledge.document_title}")
        print(f"Sections: {len(knowledge.sections)}")

        # Show hierarchical structure
        print("\nDocument Structure:")
        top_sections = knowledge.get_top_level_sections()
        for section in top_sections:
            print(f"- {section.title} (Level {section.level})")
            children = knowledge.get_children_of_section(section.id)
            for child in children:
                print(f"  - {child.title} (Level {child.level})")

    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()


async def main():
    """Run all examples."""
    print("Cognitive Document Reader - Examples")
    print("=" * 50)

    await basic_example()
    await configuration_example()
    await spanish_example()
    await file_processing_example()

    print("\n" + "=" * 50)
    print("Examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
