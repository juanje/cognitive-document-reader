"""Base classes for semantic evaluation tests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class TestResult(Enum):
    """Test result status."""

    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    UNABLE_TO_EVALUATE = "UNABLE_TO_EVALUATE"


@dataclass
class TestOutcome:
    """Result of a semantic test."""

    test_name: str
    result: TestResult
    score: float  # 0.0 to 1.0
    details: str
    expected_answer: str
    found_evidence: str
    failure_reason: str | None = None


class SemanticTest(ABC):
    """Base class for semantic evaluation tests."""

    def __init__(self, name: str, description: str):
        """Initialize semantic test.

        Args:
            name: Test name/identifier
            description: Human-readable test description
        """
        self.name = name
        self.description = description

    @abstractmethod
    def evaluate(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Evaluate the test against processed document knowledge.

        Args:
            knowledge_data: Processed cognitive knowledge (JSON format)

        Returns:
            TestOutcome with evaluation results
        """
        pass

    def _search_in_text(self, text: str, keywords: list[str], case_sensitive: bool = False) -> bool:
        """Helper to search for keywords in text.

        Args:
            text: Text to search in
            keywords: List of keywords to find
            case_sensitive: Whether search should be case sensitive

        Returns:
            True if all keywords found, False otherwise
        """
        search_text = text if case_sensitive else text.lower()
        search_keywords = keywords if case_sensitive else [k.lower() for k in keywords]

        return all(keyword in search_text for keyword in search_keywords)

    def _extract_concept_definitions(self, knowledge_data: dict[str, Any]) -> dict[str, str]:
        """Extract concept definitions from knowledge data.

        Args:
            knowledge_data: Processed cognitive knowledge

        Returns:
            Dictionary mapping concept names to their definitions
        """
        concepts = {}

        # Extract from concepts array
        if "concepts" in knowledge_data:
            for concept in knowledge_data["concepts"]:
                if isinstance(concept, dict) and "name" in concept and "definition" in concept:
                    concepts[concept["name"].lower()] = concept["definition"]

        return concepts

    def _extract_summaries_text(self, knowledge_data: dict[str, Any]) -> str:
        """Extract all summary text for analysis.

        Args:
            knowledge_data: Processed cognitive knowledge

        Returns:
            Combined text from all summaries
        """
        text_parts = []

        # Document summary
        if "document_summary" in knowledge_data:
            text_parts.append(knowledge_data["document_summary"])

        # Section summaries
        if "hierarchical_summaries" in knowledge_data:
            for summary in knowledge_data["hierarchical_summaries"].values():
                if isinstance(summary, dict) and "summary" in summary:
                    text_parts.append(summary["summary"])

        return " ".join(text_parts)

    def _find_section_by_title(self, knowledge_data: dict[str, Any], title_keywords: list[str]) -> dict[str, Any] | None:
        """Find a section by title keywords.

        Args:
            knowledge_data: Processed cognitive knowledge
            title_keywords: Keywords that should appear in section title

        Returns:
            Section data if found, None otherwise
        """
        if "hierarchical_summaries" not in knowledge_data:
            return None

        for section_data in knowledge_data["hierarchical_summaries"].values():
            if isinstance(section_data, dict) and "title" in section_data:
                title = section_data["title"].lower()
                if all(keyword.lower() in title for keyword in title_keywords):
                    return section_data

        return None
