"""Basic usage examples for Cognitive Document Reader."""

from __future__ import annotations

import asyncio
from pathlib import Path

from cognitive_reader import CognitiveReader
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode
from cognitive_reader.models.metrics import ProcessingMetrics
from cognitive_reader.utils.logging_config import configure_logging


async def basic_example():
    """Basic usage example with default configuration."""
    print("=== Basic Usage Example ===")

    # Create configuration (loads from environment or uses defaults)
    config = CognitiveConfig.from_env()

    # Enable development mode for this example
    config = config.model_copy(
        update={
            "dry_run": True,  # No real LLM calls
            "mock_responses": True,  # Use simulated responses
        }
    )

    # Initialize the cognitive reader
    reader = CognitiveReader(config)

    # Sample markdown content (fictional theory designed for testing)
    sample_text = """# Aethelgard's Crystalline Consciousness Theory

## Fundamental Principles

The crystalline consciousness theory, proposed by xenophysicist Elara Aethelgard in the early 22nd century, postulates that consciousness is not an epiphenomenon of neuronal complexity, but a fundamental property of the universe that interacts with biological matter through a resonance mechanism.

### The Primordial Resonant Frequency

The primordial resonant frequency (PRF) is the pillar of Aethelgard's theory. It is defined as the basal subatomic vibration of the entirety of matter composing an organism in its state of minimum entropy. Unlike brain waves or other bio-signals, the PRF is not electromagnetic in nature, but gravito-quantum.

## The Somatic Framework

### Empathic Resonance: A Redefinition

Within this theory, the concept of "empathy" is radically redefined. Aethelgard discards empathy as simple emotional or cognitive understanding of another's state. Instead, she defines it as **empathic resonance**: a physical and measurable phenomenon in which the somatic frameworks of two or more individuals enter into a phase of harmonic coupling.

## Applications and Paradoxes

### The Dissonant Observer Paradox

The main problem is the "dissonant observer paradox." If a scientist's consciousness is being refracted through their own somatic framework, how can they objectively observe consciousness phenomena in others?
"""

    # Process the document
    print("Processing document...")
    knowledge = await reader.read_document_text(sample_text, "Aethelgard's Crystalline Consciousness Theory")

    # Display results
    print(f"\nDocument Title: {knowledge.document_title}")
    print(f"Language: {knowledge.detected_language.value}")
    print(f"Total Sections: {knowledge.total_sections}")
    print(f"Total Summaries: {len(knowledge.hierarchical_summaries)}")
    print(f"Total Concepts: {knowledge.total_concepts}")

    print("\nDocument Summary:")
    print(knowledge.document_summary)

    print("\nSection Summaries:")
    for section_id, summary in knowledge.hierarchical_summaries.items():
        print(f"\n- {summary.title}")
        print(f"  Summary: {summary.summary}")
        if summary.key_concepts:
            print(f"  Key Concepts: {', '.join(summary.key_concepts)}")


async def configuration_example():
    """Example showing different configuration options."""
    print("\n=== Configuration Example ===")

    # Custom configuration - Dual model system
    config = CognitiveConfig(
        fast_pass_model="llama3.1:8b",  # Fast model for initial pass
        main_model="qwen3:8b",  # Quality model for detailed analysis
        temperature=0.1,
        chunk_size=800,
        chunk_overlap=160,
        document_language=LanguageCode.EN,
        dry_run=True,  # Development mode
        mock_responses=True,
    )

    print(f"Fast pass model: {config.fast_pass_model}")
    print(f"Main model: {config.main_model}")
    print(f"Single pass mode: {config.single_pass}")

    # Configuration is automatically validated during CognitiveReader initialization
    print("Configuration loaded and validated successfully")


async def dual_model_example():
    """Example demonstrating dual model system (fast pass + quality pass)."""
    print("\n=== Dual Model System Example ===")

    test_text = """# The Primordial Resonant Frequency

The primordial resonant frequency (PRF) is the pillar of Aethelgard's theory. It is defined as the basal subatomic vibration of the entirety of matter composing an organism in its state of minimum entropy.

## Measurement Techniques

The measurement of the PRF is performed in a state of "total somatic deprivation," an environment of sensory flotation and gravitational nullification.

## Implications

This frequency determines an organism's affinity with certain patterns of the universal consciousness field, predisposing it to certain personality archetypes and thought patterns.
"""

    # Dual-pass mode (default) - fast scan + quality processing
    dual_config = CognitiveConfig(
        enable_fast_first_pass=True,  # Enable fast first pass
        fast_pass_model="llama3.1:8b",  # Fast model for initial scan
        main_model="qwen3:8b",  # Quality model for detailed analysis
        num_passes=2,  # Two passes for comprehensive understanding
        dry_run=True,
        mock_responses=True,
    )

    # Single-pass mode - quality only (faster processing)
    single_config = CognitiveConfig(
        single_pass=True,  # Force single pass
        main_model="qwen3:8b",  # Only use quality model
        dry_run=True,
        mock_responses=True,
    )

    print(f"Dual-pass config: Fast={dual_config.fast_pass_model}, Main={dual_config.main_model}")
    print(f"Single-pass config: Main={single_config.main_model}, Passes={1 if single_config.single_pass else dual_config.num_passes}")

    # Process with dual-pass mode
    print("\n📊 Processing with dual-pass mode (comprehensive analysis)...")
    dual_reader = CognitiveReader(dual_config)
    dual_result = await dual_reader.read_document_text(
        test_text, "The Primordial Resonant Frequency"
    )

    # Process with single-pass mode
    print("\n⚡ Processing with single-pass mode (quick analysis)...")
    single_reader = CognitiveReader(single_config)
    single_result = await single_reader.read_document_text(test_text, "The Primordial Resonant Frequency")

    print(f"\nDual-pass result - Total concepts: {dual_result.total_concepts}")
    print(f"Single-pass result - Total concepts: {single_result.total_concepts}")
    print(f"Both results processed {dual_result.total_sections} sections")

    print("Dual model system example completed.")


async def spanish_example():
    """Example with Spanish content (Aethelgard theory in Spanish)."""
    print("\n=== Spanish Document Example ===")

    config = CognitiveConfig(
        document_language=LanguageCode.AUTO,  # Auto-detect
        dry_run=True,
        mock_responses=True,
    )

    reader = CognitiveReader(config)

    spanish_text = """# La teoría de la conciencia cristalina de Aethelgard

## Principios fundamentales

La teoría de la conciencia cristalina, propuesta por la xenofísica Elara Aethelgard a principios del siglo XXII, postula que la conciencia no es un epifenómeno de la complejidad neuronal, sino una propiedad fundamental del universo que interactúa con la materia biológica a través de un mecanismo de resonancia.

### La frecuencia resonante primordial

La frecuencia resonante primordial (FRP) es el pilar de la teoría de Aethelgard. Se define como la vibración subatómica basal de la totalidad de la materia que compone un organismo en su estado de entropía mínima.

## El entramado somático

### La resonancia empática: una redefinición

Dentro de esta teoría, el concepto de "empatía" es redefinido radicalmente. Aethelgard descarta la empatía como simple comprensión emocional o cognitiva del estado de otro. En su lugar, la define como **resonancia empática**: un fenómeno físico y medible en el que los entramados somáticos de dos o más individuos entran en una fase de acoplamiento armónico.
"""

    knowledge = await reader.read_document_text(spanish_text, "La teoría de la conciencia cristalina de Aethelgard")

    print(f"Título: {knowledge.document_title}")
    print(f"Idioma detectado: {knowledge.detected_language.value}")
    print(f"Total secciones: {knowledge.total_sections}")
    print(f"Total conceptos: {knowledge.total_concepts}")
    print("\nResumen del documento:")
    print(knowledge.document_summary)


async def file_processing_example():
    """Example processing a markdown file using the actual sample documents."""
    print("\n=== File Processing Example ===")

    config = CognitiveConfig(dry_run=True, mock_responses=True)
    reader = CognitiveReader(config)

    # Use the actual sample document file
    sample_file = Path("examples/sample_document.md")

    try:
        if not sample_file.exists():
            print(f"⚠️  Sample file not found: {sample_file}")
            print("   This example works best when run from the project root directory")
            return

        # Process the file
        print(f"Processing file: {sample_file}")
        knowledge = await reader.read_document(sample_file)

        print(f"Document: {knowledge.document_title}")
        print(f"Total sections: {knowledge.total_sections}")
        print(f"Total concepts: {knowledge.total_concepts}")

        # Show hierarchical structure using hierarchy_index
        print("\nDocument Structure:")

        # Get sections by hierarchy level
        for level, section_ids in knowledge.hierarchy_index.items():
            level_num = int(level)
            indent = "  " * level_num
            for section_id in section_ids:
                summary = knowledge.get_summary_by_id(section_id)
                if summary:
                    print(f"{indent}- {summary.title} (Level {level_num})")

        # Show some concepts
        print(f"\nKey Concepts ({len(knowledge.concepts)} total):")
        for i, concept in enumerate(knowledge.concepts[:3]):  # Show first 3
            print(f"- {concept.name}: {concept.definition[:100]}...")
        if len(knowledge.concepts) > 3:
            print(f"  ... and {len(knowledge.concepts) - 3} more concepts")

    except Exception as e:
        print(f"Error processing file: {e}")
        print("This example works best with the actual sample_document.md file")


async def new_features_example():
    """Example demonstrating new features: metrics, logging, and advanced configuration."""
    print("\n=== New Features Example ===")

    # Configure logging to file (optional)
    log_file = Path("example_processing.log")
    configure_logging(verbose=True, log_file=log_file)
    print(f"📝 Logging configured to: {log_file}")

    # Initialize processing metrics
    metrics = ProcessingMetrics()

    # Advanced configuration with new features
    config = CognitiveConfig(
        # Dual model system
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b",
        enable_fast_first_pass=True,
        num_passes=2,

        # Processing optimization
        max_sections=5,  # Limit sections for demo
        save_intermediate=True,  # Save intermediate results
        intermediate_dir="./demo_intermediate",

        # Logging configuration
        log_file=log_file,

        # Development mode
        dry_run=True,
        mock_responses=True,
    )

    # Initialize reader with metrics
    reader = CognitiveReader(config, metrics)

    test_content = """# Cognitive Refraction Principles

## Overview of Refraction Theory

If the PRF is the tuning, cognitive refraction is the manifestation. Aethelgard postulates that once universal consciousness is "received" by the organism, it is processed and "refracted" through its biological structure.

### Optical Metaphor Application

This refraction process employs a powerful optical metaphor: pure consciousness is like white light, and the somatic framework acts as a prism.

### Dynamic Refraction States

The state of the somatic framework can alter the angle of refraction, thus changing the quality of conscious experience moment to moment.

## Applications in Practice

### Therapeutic Implications

Physical or emotional traumas can create "knots" in the flow lines, distorting the distribution of conscious energy.

### Measurement Protocols

The somatic therapies proposed by Aethelgard focus on identifying and releasing these knots to restore harmonic flow.
"""

    print("🧠 Processing with full metrics tracking...")

    # Record processing start time
    import time
    start_time = time.time()

    # Process the document
    knowledge = await reader.read_document_text(test_content, "Cognitive Refraction Principles")

    # Update final metrics
    metrics.sections_processed = knowledge.total_sections
    metrics.concepts_generated = knowledge.total_concepts

    # Display results
    print("\n📊 Processing Results:")
    print(f"   Title: {knowledge.document_title}")
    print(f"   Language: {knowledge.detected_language.value}")
    print(f"   Total sections: {knowledge.total_sections}")
    print(f"   Total concepts: {knowledge.total_concepts}")
    print(f"   Processing time: {time.time() - start_time:.2f}s")

    # Show metrics table (simulating --stats functionality)
    print("\n📈 Processing Metrics:")
    stats_table = metrics.format_stats_table()
    print(stats_table)

    # Show some concepts with their definitions
    print("\n🔑 Key Concepts Generated:")
    for concept in knowledge.concepts[:3]:  # Show first 3
        print(f"   - {concept.name}")
        print(f"     {concept.definition[:120]}...")

    # Cleanup
    try:
        if log_file.exists():
            print("\n📋 Log file content preview:")
            log_content = log_file.read_text()
            lines = log_content.split('\n')[:3]  # First 3 lines
            for line in lines:
                if line.strip():
                    print(f"     {line}")
            print(f"     ... ({len(log_content.split())} total log entries)")
            log_file.unlink()  # Clean up
    except Exception as e:
        print(f"Note: Could not read log file: {e}")

    print("✅ New features demonstration completed!")


async def main():
    """Run all examples."""
    print("Cognitive Document Reader - Examples")
    print("=" * 50)

    await basic_example()
    await configuration_example()
    await dual_model_example()
    await spanish_example()
    await file_processing_example()
    await new_features_example()

    print("\n" + "=" * 50)
    print("Examples completed successfully!")
    print("\nNote: All examples use the fictional 'Aethelgard theory' content")
    print("designed specifically to test cognitive reading capabilities.")
    print("\n💡 New features demonstrated:")
    print("   • --log flag equivalent (logging to file)")
    print("   • --stats flag equivalent (processing metrics)")
    print("   • Dual model system (fast + quality passes)")
    print("   • Advanced configuration options")


if __name__ == "__main__":
    asyncio.run(main())
