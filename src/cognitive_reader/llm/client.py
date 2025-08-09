"""LLM client abstraction with focus on Ollama integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from ..models.config import ReadingConfig
from ..models.knowledge import LanguageCode
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class LLMClient:
    """Simple LLM abstraction with Ollama focus and development-friendly features.

    Provides a clean interface for LLM operations with built-in retry logic,
    error handling, and support for development modes (dry-run, mocking).
    """

    def __init__(self, config: ReadingConfig) -> None:
        """Initialize the LLM client.

        Args:
            config: Reading configuration with LLM settings.
        """
        self.config = config
        self.prompt_manager = PromptManager()
        self._base_url = "http://localhost:11434"  # Default Ollama URL
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> LLMClient:
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    async def generate_summary(
        self,
        content: str,
        context: str = "",
        prompt_type: str = "section_summary",
        language: LanguageCode = LanguageCode.EN,
        section_title: str = "Untitled Section",
    ) -> str:
        """Generate a summary for given content.

        Args:
            content: The content to summarize.
            context: Additional context for the summary.
            prompt_type: Type of prompt to use for summarization.
            language: Target language for the summary.
            section_title: Title of the section being summarized.

        Returns:
            Generated summary text.

        Raises:
            ValueError: If generation fails after retries.
        """
        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            return self._get_mock_summary(content, prompt_type, language)

        # Format the appropriate prompt
        if prompt_type == "section_summary":
            prompt = self.prompt_manager.format_section_summary_prompt(
                section_title=section_title,
                section_content=content,
                accumulated_context=context,
                language=language,
            )
        elif prompt_type == "document_summary":
            # For document summary, content should be section summaries
            prompt = self.prompt_manager.format_document_summary_prompt(
                document_title=section_title,
                section_summaries=[content],  # Expecting formatted summaries
                language=language,
            )
        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

        # Generate with retry logic
        return await self._generate_with_retries(prompt)

    async def extract_concepts(
        self,
        section_title: str,
        section_content: str,
        language: LanguageCode = LanguageCode.EN,
    ) -> list[str]:
        """Extract key concepts from section content.

        Args:
            section_title: Title of the section.
            section_content: Content to analyze.
            language: Target language for extraction.

        Returns:
            List of extracted key concepts.
        """
        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            return self._get_mock_concepts(section_content)

        prompt = self.prompt_manager.format_concept_extraction_prompt(
            section_title=section_title,
            section_content=section_content,
            language=language,
        )

        response = await self._generate_with_retries(prompt)

        # Parse concepts from response
        return self._parse_concepts_response(response)

    async def _generate_with_retries(self, prompt: str) -> str:
        """Generate response with retry logic.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            Generated response text.

        Raises:
            ValueError: If all retry attempts fail.
        """
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._call_ollama(prompt)
            except Exception as e:
                last_error = e
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")

                if attempt < self.config.max_retries:
                    # Exponential backoff
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                    logger.info(f"Retrying in {wait_time}s...")

        raise ValueError(
            f"LLM generation failed after {self.config.max_retries + 1} attempts: {last_error}"
        )

    async def _call_ollama(self, prompt: str) -> str:
        """Make actual call to Ollama API.

        Args:
            prompt: The prompt to send.

        Returns:
            Response text from Ollama.
        """
        if not self._session:
            raise RuntimeError(
                "LLM client not properly initialized. Use async context manager."
            )

        payload = {
            "model": self.config.active_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_ctx": self.config.context_window,
            },
        }

        url = f"{self._base_url}/api/generate"

        async with self._session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise ValueError(f"Ollama API error {response.status}: {error_text}")

            data = await response.json()
            response_text = data.get("response", "")
            return str(response_text).strip()

    def _get_mock_summary(
        self, content: str, prompt_type: str, language: LanguageCode
    ) -> str:
        """Generate mock summary for development/testing.

        Args:
            content: Content being summarized.
            prompt_type: Type of summary.
            language: Target language.

        Returns:
            Mock summary text.
        """
        content_preview = content[:100] + "..." if len(content) > 100 else content

        if language == LanguageCode.ES:
            if prompt_type == "document_summary":
                return f"Resumen del Documento: Este documento contiene información importante sobre varios temas. El contenido analizado incluye: {content_preview}. Los puntos clave se han identificado y sintetizado para proporcionar una visión general coherente."
            else:
                return f"Resumen: Esta sección contiene información relevante sobre el tema presentado. El contenido incluye: {content_preview}. Se han identificado conceptos clave importantes.\nConceptos Clave: [concepto1, concepto2, concepto3]"
        else:
            if prompt_type == "document_summary":
                return f"Document Summary: This document contains important information about various topics. The analyzed content includes: {content_preview}. Key points have been identified and synthesized to provide a coherent overview."
            else:
                return f"Summary: This section contains relevant information about the presented topic. The content includes: {content_preview}. Important key concepts have been identified.\nKey Concepts: [concept1, concept2, concept3]"

    def _get_mock_concepts(self, content: str) -> list[str]:
        """Generate mock concepts for development/testing.

        Args:
            content: Content to analyze.

        Returns:
            List of mock concepts.
        """
        # Generate simple mock concepts based on content length and first words
        words = content.split()[:10]  # First 10 words

        concepts = []
        for i, word in enumerate(words[:3]):  # Up to 3 concepts
            if len(word) > 3:  # Skip short words
                concepts.append(f"concept_{i + 1}_{word.lower()}")

        # Ensure we always have at least 2 concepts
        while len(concepts) < 2:
            concepts.append(f"mock_concept_{len(concepts) + 1}")

        return concepts[:5]  # Maximum 5 concepts

    def _parse_concepts_response(self, response: str) -> list[str]:
        """Parse key concepts from LLM response.

        Args:
            response: Raw response from LLM.

        Returns:
            List of extracted concepts.
        """
        concepts = []

        # Look for "Key Concepts:" or "Conceptos Clave:" lines
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith(("Key Concepts:", "Conceptos Clave:")):
                # Extract concepts after the colon
                concepts_text = line.split(":", 1)[1].strip()

                # Parse comma-separated concepts, removing brackets
                concepts_text = concepts_text.strip("[]")
                if concepts_text:
                    concepts = [
                        concept.strip().strip("'\"")
                        for concept in concepts_text.split(",")
                        if concept.strip()
                    ]
                break

        # Fallback: if no structured format found, try to extract from text
        if not concepts:
            # Simple fallback - extract capitalized words as potential concepts
            words = response.split()
            concepts = [
                word.strip(".,!?")
                for word in words
                if word[0].isupper() and len(word) > 3
            ][:5]

        return concepts[:5]  # Limit to 5 concepts

    async def validate_configuration(self) -> bool:
        """Validate LLM configuration and connectivity.

        Returns:
            True if configuration is valid and LLM is accessible.
        """
        if self.config.dry_run or self.config.mock_responses:
            logger.info("Validation successful (development mode)")
            return True

        try:
            if not self._session:
                async with aiohttp.ClientSession() as session:
                    self._session = session
                    return await self._test_ollama_connection()
            else:
                return await self._test_ollama_connection()
        except Exception as e:
            logger.error(f"LLM configuration validation failed: {e}")
            return False

    async def _test_ollama_connection(self) -> bool:
        """Test connection to Ollama API.

        Returns:
            True if connection successful.
        """
        if not self._session:
            return False

        try:
            url = f"{self._base_url}/api/tags"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]

                    # Check if configured model is available
                    model_available = any(
                        self.config.active_model in model for model in models
                    )

                    if not model_available:
                        logger.warning(
                            f"Model {self.config.active_model} not found in Ollama. Available models: {models}"
                        )

                    return model_available
                else:
                    logger.error(f"Ollama API returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to test Ollama connection: {e}")
            return False
