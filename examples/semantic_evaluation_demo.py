"""Demonstration of semantic evaluation for cognitive reading quality assessment."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from cognitive_reader import CognitiveReader
from cognitive_reader.evaluation.semantic_evaluator import SemanticEvaluator
from cognitive_reader.models.config import CognitiveConfig
from cognitive_reader.models.knowledge import LanguageCode


async def process_and_evaluate_document(
    document_path: Path,
    output_dir: Path,
    language: LanguageCode = LanguageCode.AUTO,
    verbose: bool = True
) -> Any:
    """Process a document and evaluate its semantic quality.

    Args:
        document_path: Path to the document to process
        output_dir: Directory to save outputs
        language: Document language (AUTO for detection)
        verbose: Whether to show detailed progress
    """
    output_dir.mkdir(exist_ok=True)

    if verbose:
        print(f"🧠 Processing document: {document_path}")

    # Configure cognitive reader
    config = CognitiveConfig(
        document_language=language,
        enable_fast_first_pass=True,  # Use dual-pass system
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b",
        dry_run=True,  # Use mock responses for demo
        mock_responses=True,
    )

    reader = CognitiveReader(config)

    # Process the document
    knowledge = await reader.read_document(document_path)

    if verbose:
        print("✅ Document processed:")
        print(f"   Title: {knowledge.document_title}")
        print(f"   Language: {knowledge.detected_language.value}")
        print(f"   Sections: {knowledge.total_sections}")
        print(f"   Concepts: {knowledge.total_concepts}")

    # Save knowledge to JSON for evaluation
    json_filename = f"{document_path.stem}_knowledge.json"
    json_path = output_dir / json_filename

    # Convert knowledge to JSON-serializable format
    knowledge_dict = {
        "document_title": knowledge.document_title,
        "document_summary": knowledge.document_summary,
        "detected_language": knowledge.detected_language.value,
        "total_sections": knowledge.total_sections,
        "total_concepts": knowledge.total_concepts,
        "avg_summary_length": knowledge.avg_summary_length,
        "hierarchical_summaries": {
            section_id: {
                "title": summary.title,
                "summary": summary.summary,
                "level": summary.level,
                "key_concepts": summary.key_concepts,
                "order_index": summary.order_index,
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
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_dict, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"💾 Knowledge saved to: {json_path}")

    # Run semantic evaluation
    if verbose:
        print("\n🔍 Running semantic evaluation...")

    evaluator = SemanticEvaluator()
    report = evaluator.evaluate_document(json_path, verbose=verbose)

    # Display evaluation results
    evaluator.print_report(report, detailed=True)

    # Export detailed evaluation report
    eval_filename = f"{document_path.stem}_evaluation.json"
    eval_path = output_dir / eval_filename
    evaluator.export_report(report, eval_path)

    return report


async def demo_english_document() -> Any | None:
    """Demonstrate evaluation with English Aethelgard document."""
    print("=" * 70)
    print("🇬🇧 ENGLISH DOCUMENT EVALUATION")
    print("=" * 70)

    document_path = Path("examples/sample_document.md")

    if not document_path.exists():
        print(f"❌ Document not found: {document_path}")
        print("   Please run this demo from the project root directory")
        return None

    output_dir = Path("evaluation_outputs")

    return await process_and_evaluate_document(
        document_path=document_path,
        output_dir=output_dir,
        language=LanguageCode.EN,
        verbose=True
    )


async def demo_spanish_document() -> Any | None:
    """Demonstrate evaluation with Spanish Aethelgard document."""
    print("\n" + "=" * 70)
    print("🇪🇸 SPANISH DOCUMENT EVALUATION")
    print("=" * 70)

    document_path = Path("examples/sample_document_es.md")

    if not document_path.exists():
        print(f"❌ Document not found: {document_path}")
        print("   Please run this demo from the project root directory")
        return None

    output_dir = Path("evaluation_outputs")

    return await process_and_evaluate_document(
        document_path=document_path,
        output_dir=output_dir,
        language=LanguageCode.ES,
        verbose=True
    )


async def compare_language_results(english_report: Any, spanish_report: Any) -> None:
    """Compare evaluation results between languages."""
    if not english_report or not spanish_report:
        print("\n❌ Cannot compare - missing evaluation reports")
        return

    print("\n" + "=" * 70)
    print("📊 CROSS-LANGUAGE COMPARISON")
    print("=" * 70)

    print(f"🇬🇧 English Overall Score: {english_report.overall_score:.2f} ({english_report.quality_grade})")
    print(f"🇪🇸 Spanish Overall Score: {spanish_report.overall_score:.2f} ({spanish_report.quality_grade})")
    print()

    # Compare individual test categories
    english_tests = {outcome.test_name: outcome.score for outcome in english_report.test_outcomes}
    spanish_tests = {outcome.test_name: outcome.score for outcome in spanish_report.test_outcomes}

    print("📋 Test-by-Test Comparison:")
    for test_name in english_tests:
        en_score = english_tests[test_name]
        es_score = spanish_tests.get(test_name, 0.0)
        difference = es_score - en_score

        trend_icon = "📈" if difference > 0.1 else ("📉" if difference < -0.1 else "➡️")

        print(f"   {test_name:25} | EN: {en_score:.2f} | ES: {es_score:.2f} | Diff: {difference:+.2f} {trend_icon}")

    # Analysis
    print("\n🔍 Analysis:")
    if abs(english_report.overall_score - spanish_report.overall_score) < 0.1:
        print("   ✅ Similar quality across languages - good consistency!")
    elif english_report.overall_score > spanish_report.overall_score:
        print("   📊 English processing shows higher quality")
    else:
        print("   📊 Spanish processing shows higher quality")

    avg_score = (english_report.overall_score + spanish_report.overall_score) / 2
    print(f"   📈 Average cross-language score: {avg_score:.2f}")


async def main() -> int:
    """Run the complete semantic evaluation demonstration."""
    print("🧠 Cognitive Reading Semantic Evaluation Demo")
    print("=" * 70)
    print()
    print("This demo processes the Aethelgard theory documents in both")
    print("English and Spanish, then evaluates how well the cognitive")
    print("reader understood and summarized the complex fictional concepts.")
    print()

    try:
        # Process both documents
        english_report = await demo_english_document()
        spanish_report = await demo_spanish_document()

        # Compare results
        await compare_language_results(english_report, spanish_report)

        print("\n" + "=" * 70)
        print("🎉 SEMANTIC EVALUATION DEMO COMPLETED")
        print("=" * 70)
        print()
        print("📁 Output files saved in: evaluation_outputs/")
        print("   • *_knowledge.json     - Processed cognitive knowledge")
        print("   • *_evaluation.json    - Detailed evaluation reports")
        print()
        print("💡 Next steps:")
        print("   • Review detailed evaluation reports")
        print("   • Analyze specific test failures")
        print("   • Use insights to improve cognitive reading algorithms")
        print("   • Run evaluations on real (non-mock) LLM outputs")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
