"""LLM client abstraction with LangChain integration and multi-provider support."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, TypeVar

import aiohttp
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from ..models.config import CognitiveConfig
from ..models.knowledge import LanguageCode
from ..models.llm_responses import ConceptDefinitionResponse, SectionSummaryResponse
from ..models.metrics import ProcessingMetrics
from ..utils.tokens import get_context_usage_info
from .prompts import PromptManager

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class LLMClient:
    """LangChain-powered LLM abstraction with multi-provider support and development features.

    Provides a clean interface for LLM operations using LangChain under the hood.
    Supports multiple providers (currently Ollama, extensible for OpenAI, Anthropic, etc.)
    with built-in retry logic, error handling, and development modes (dry-run, mocking).
    """

    def __init__(
        self, config: CognitiveConfig, metrics: ProcessingMetrics | None = None
    ) -> None:
        """Initialize the LLM client.

        Args:
            config: Reading configuration with LLM settings.
            metrics: Optional metrics collector for tracking LLM call statistics.
        """
        self.config = config
        self.metrics = metrics
        self.prompt_manager = PromptManager()
        self._session: aiohttp.ClientSession | None = None

        # Initialize LangChain LLM based on provider
        self._llm = self._create_llm_provider()
        self._fast_llm = (
            self._create_fast_llm_provider() if config.fast_pass_model else None
        )

    def _create_llm_provider(self) -> BaseChatModel:
        """Create LangChain Chat Model provider based on configuration.

        Returns:
            Configured LangChain Chat Model instance.

        Raises:
            ValueError: If unsupported provider is specified.
        """
        if self.config.llm_provider == "ollama":
            main_model = self.config.main_model or self.config.model_name

            # Configure reasoning parameter for reasoning models
            reasoning_param = None if not self.config.disable_reasoning else False

            return ChatOllama(
                model=main_model,
                base_url=self.config.ollama_base_url,
                temperature=self.config.main_pass_temperature
                or self.config.temperature,
                num_ctx=self.config.context_window,
                reasoning=reasoning_param,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")

    def _create_fast_llm_provider(self) -> BaseChatModel | None:
        """Create fast pass LLM provider if configured.

        Returns:
            Configured fast LangChain LLM instance or None.
        """
        if not self.config.fast_pass_model:
            return None

        if self.config.llm_provider == "ollama":
            # Configure reasoning parameter for reasoning models
            reasoning_param = None if not self.config.disable_reasoning else False

            return ChatOllama(
                model=self.config.fast_pass_model,
                base_url=self.config.ollama_base_url,
                temperature=self.config.fast_pass_temperature
                or self.config.temperature,
                num_ctx=self.config.context_window,
                reasoning=reasoning_param,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")

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
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Generate a summary for given content.

        Args:
            content: The content to summarize.
            context: Additional context for the summary.
            prompt_type: Type of prompt to use for summarization.
            language: Target language for the summary.
            section_title: Title of the section being summarized.
            model: Optional model to use (overrides config).
            temperature: Optional temperature to use (overrides config).

        Returns:
            Generated summary text.

        Raises:
            ValueError: If generation fails after retries.
        """
        # Show context usage if requested (for dry-run and real calls)
        if self.config.show_context_usage:
            # Create prompt to estimate context size
            if prompt_type == "section_summary":
                prompt = self.prompt_manager.format_section_summary_prompt(
                    section_title=section_title,
                    section_content=content,
                    accumulated_context=context,
                    language=language,
                )
            else:
                # For other prompt types, estimate based on content + context
                prompt = f"Context: {context}\n\nContent: {content}"

            estimated_tokens, usage_percentage = get_context_usage_info(
                prompt, self.config.context_window
            )
            logger.info(
                f"→ Context size: {estimated_tokens:,} tokens "
                f"({usage_percentage:.1f}% of {self.config.context_window:,} window)"
            )

        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            # Still track metrics in development mode for testing purposes
            if self.metrics:
                estimated_tokens, _ = get_context_usage_info(
                    content, self.config.context_window
                )
                self.metrics.llm_metrics.add_summary_call(estimated_tokens)
            return self._get_mock_summary(content, prompt_type, language)

        # Format the appropriate prompt
        if prompt_type == "section_summary":
            prompt = self.prompt_manager.format_section_summary_prompt(
                section_title=section_title,
                section_content=content,
                accumulated_context=context,
                language=language,
                target_words=self.config.target_summary_words,
                min_words=self.config.min_summary_words,
                max_words=self.config.max_summary_words,
            )
        elif prompt_type == "document_summary":
            # For document summary, content should be section summaries
            prompt = self.prompt_manager.format_document_summary_prompt(
                document_title=section_title,
                section_summaries=[content],  # Expecting formatted summaries
                language=language,
                target_words=self.config.target_document_summary_words,
                min_words=self.config.min_document_summary_words,
                max_words=self.config.max_document_summary_words,
            )
        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

        # Generate with retry logic
        return await self._generate_with_retries(
            prompt, model=model, temperature=temperature
        )

    async def extract_concepts(
        self,
        section_title: str,
        section_content: str,
        language: LanguageCode = LanguageCode.EN,
        model: str | None = None,
        temperature: float | None = None,
    ) -> list[str]:
        """Extract key concepts from section content.

        Args:
            section_title: Title of the section.
            section_content: Content to analyze.
            language: Target language for extraction.
            model: Optional model to use (overrides config).
            temperature: Optional temperature to use (overrides config).

        Returns:
            List of extracted key concepts.
        """
        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            # Still track metrics in development mode for testing purposes
            if self.metrics:
                estimated_tokens, _ = get_context_usage_info(
                    section_content, self.config.context_window
                )
                self.metrics.llm_metrics.add_concept_call(estimated_tokens)
            return self._get_mock_concepts(section_content)

        prompt = self.prompt_manager.format_concept_extraction_prompt(
            section_title=section_title,
            section_content=section_content,
            language=language,
        )

        response = await self._generate_with_retries(
            prompt, model=model, temperature=temperature
        )

        # Parse concepts from response
        return self._parse_concepts_response(response)

    async def generate_structured_summary(
        self,
        content: str,
        context: str = "",
        section_title: str = "Untitled Section",
        language: LanguageCode = LanguageCode.EN,
        model: str | None = None,
        temperature: float | None = None,
    ) -> SectionSummaryResponse:
        """Generate a structured summary for given content using Pydantic models.

        This method uses LangChain's structured output to ensure consistent format.

        Args:
            content: The content to summarize.
            context: Additional context for the summary.
            section_title: Title of the section being summarized.
            language: Target language for the summary.
            model: Optional model to use (overrides config).
            temperature: Optional temperature to use (overrides config).

        Returns:
            Structured summary response with validated format.

        Raises:
            ValueError: If generation fails after retries.
        """
        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            mock_summary = self._get_mock_summary(content, "section_summary", language)
            mock_concepts = self._get_mock_concepts(content)
            return SectionSummaryResponse(
                summary=mock_summary, key_concepts=mock_concepts
            )

        # Format the prompt for section summary
        prompt = self.prompt_manager.format_section_summary_prompt(
            section_title=section_title,
            section_content=content,
            accumulated_context=context,
            language=language,
        )

        # Generate with structured output
        return await self._generate_structured_with_retries(
            prompt,
            response_model=SectionSummaryResponse,
            model=model,
            temperature=temperature,
        )

    async def generate_concept_definition(
        self,
        concept: str,
        context: str,
        language: LanguageCode = LanguageCode.EN,
        model: str | None = None,
        temperature: float | None = None,
    ) -> ConceptDefinitionResponse:
        """Generate a structured definition for a concept.

        This method uses LangChain's structured output to ensure consistent format.

        Args:
            concept: The concept to define.
            context: Context where the concept appears.
            language: Target language for the definition.
            model: Optional model to use (overrides config).
            temperature: Optional temperature to use (overrides config).

        Returns:
            Structured definition response with validated format.

        Raises:
            ValueError: If generation fails after retries.
        """
        # Handle development modes
        if self.config.dry_run or self.config.mock_responses:
            if language == LanguageCode.ES:
                mock_definition = f"Definición del concepto '{concept}' basada en el contexto proporcionado."
            else:
                mock_definition = (
                    f"Definition of concept '{concept}' based on provided context."
                )

            return ConceptDefinitionResponse(definition=mock_definition)

        # Format the prompt for concept definition
        prompt = self.prompt_manager.format_concept_definition_prompt(
            concept_name=concept,
            context=context,
            language=language,
        )

        # Generate with structured output
        return await self._generate_structured_with_retries(
            prompt,
            response_model=ConceptDefinitionResponse,
            model=model,
            temperature=temperature,
        )

    async def _generate_with_retries(
        self, prompt: str, model: str | None = None, temperature: float | None = None
    ) -> str:
        """Generate response with retry logic using LangChain.

        Args:
            prompt: The prompt to send to the LLM.
            model: Optional model hint (selects fast vs main LLM).
            temperature: Optional temperature to use (overrides config).

        Returns:
            Generated response text.

        Raises:
            ValueError: If all retry attempts fail.
        """
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._call_langchain_llm(
                    prompt, model=model, temperature=temperature
                )
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

    async def _generate_structured_with_retries(
        self,
        prompt: str,
        response_model: type[T],  # Pydantic BaseModel class
        model: str | None = None,
        temperature: float | None = None,
    ) -> T:  # Returns instance of response_model
        """Generate structured response with retry logic using LangChain.

        Args:
            prompt: The prompt to send to the LLM.
            response_model: Pydantic model class to structure the response.
            model: Optional model hint (selects fast vs main LLM).
            temperature: Optional temperature to use (overrides config).

        Returns:
            Generated response as an instance of response_model.

        Raises:
            ValueError: If all retry attempts fail.
        """
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._call_structured_langchain_llm(
                    prompt, response_model, model=model, temperature=temperature
                )
            except Exception as e:
                last_error = e
                logger.warning(f"Structured LLM call attempt {attempt + 1} failed: {e}")

                if attempt < self.config.max_retries:
                    # Exponential backoff
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                    logger.info(f"Retrying in {wait_time}s...")

        raise ValueError(
            f"Structured LLM generation failed after {self.config.max_retries + 1} attempts: {last_error}"
        )

    async def _call_langchain_llm(
        self, prompt: str, model: str | None = None, temperature: float | None = None
    ) -> str:
        """Make actual call to LLM using LangChain.

        Args:
            prompt: The prompt to send.
            model: Optional model hint (selects fast vs main LLM).
            temperature: Optional temperature to use (overrides LLM config).

        Returns:
            Response text from LLM.
        """
        # Select appropriate LLM (fast vs main)
        # If specific model requested and matches fast model, use fast LLM
        if (
            model
            and self._fast_llm
            and self.config.fast_pass_model
            and model == self.config.fast_pass_model
        ):
            selected_llm = self._fast_llm
        else:
            selected_llm = self._llm

        # Apply temperature override if specified
        if temperature is not None:
            # Create a copy of the LLM with different temperature
            if self.config.llm_provider == "ollama":
                if selected_llm == self._fast_llm:
                    model_name = self.config.fast_pass_model
                else:
                    model_name = self.config.main_model or self.config.model_name

                # Ensure model_name is not None
                if not model_name:
                    raise ValueError("Model name cannot be None")

                # Configure reasoning parameter for reasoning models
                reasoning_param = None if not self.config.disable_reasoning else False

                selected_llm = ChatOllama(
                    model=model_name,
                    base_url=self.config.ollama_base_url,
                    temperature=temperature,
                    num_ctx=self.config.context_window,
                    reasoning=reasoning_param,
                )

        # Show context usage if requested
        if self.config.show_context_usage:
            estimated_tokens, usage_percentage = get_context_usage_info(
                prompt, self.config.context_window
            )
            logger.info(
                f"→ Context size: {estimated_tokens:,} tokens "
                f"({usage_percentage:.1f}% of {self.config.context_window:,} window)"
            )

        # Track metrics if available
        if self.metrics:
            estimated_tokens, _ = get_context_usage_info(
                prompt, self.config.context_window
            )
            self.metrics.llm_metrics.add_summary_call(estimated_tokens)

        # Make the call using LangChain
        try:
            response = await selected_llm.ainvoke(prompt)
            # ChatOllama returns AIMessage objects, extract content
            if hasattr(response, "content"):
                return str(response.content).strip()
            else:
                return str(response).strip()
        except Exception as e:
            raise ValueError(f"LangChain LLM call failed: {e}") from e

    async def _call_structured_langchain_llm(
        self,
        prompt: str,
        response_model: type[T],  # Pydantic BaseModel class
        model: str | None = None,
        temperature: float | None = None,
    ) -> T:  # Returns instance of response_model
        """Make structured call to LLM using LangChain's with_structured_output.

        Args:
            prompt: The prompt to send.
            response_model: Pydantic model class to structure the response.
            model: Optional model hint (selects fast vs main LLM).
            temperature: Optional temperature to use (overrides LLM config).

        Returns:
            Structured response as an instance of response_model.
        """
        # Select appropriate LLM (fast vs main)
        if (
            model
            and self._fast_llm
            and self.config.fast_pass_model
            and model == self.config.fast_pass_model
        ):
            selected_llm = self._fast_llm
        else:
            selected_llm = self._llm

        # Apply temperature override if specified
        if temperature is not None:
            # Create a copy of the LLM with different temperature
            if self.config.llm_provider == "ollama":
                if selected_llm == self._fast_llm:
                    model_name = self.config.fast_pass_model
                else:
                    model_name = self.config.main_model or self.config.model_name

                # Ensure model_name is not None
                if not model_name:
                    raise ValueError("Model name cannot be None")

                # Configure reasoning parameter for reasoning models
                reasoning_param = None if not self.config.disable_reasoning else False

                selected_llm = ChatOllama(
                    model=model_name,
                    base_url=self.config.ollama_base_url,
                    temperature=temperature,
                    num_ctx=self.config.context_window,
                    reasoning=reasoning_param,
                )

        # Show context usage if requested
        if self.config.show_context_usage:
            estimated_tokens, usage_percentage = get_context_usage_info(
                prompt, self.config.context_window
            )
            logger.info(
                f"→ Context size: {estimated_tokens:,} tokens "
                f"({usage_percentage:.1f}% of {self.config.context_window:,} window)"
            )

        # Track metrics if available
        if self.metrics:
            estimated_tokens, _ = get_context_usage_info(
                prompt, self.config.context_window
            )
            # Determine call type based on response model
            if "Summary" in response_model.__name__:
                self.metrics.llm_metrics.add_summary_call(estimated_tokens)
            else:
                self.metrics.llm_metrics.add_concept_call(estimated_tokens)

        # Create structured LLM with Pydantic output
        try:
            structured_llm = selected_llm.with_structured_output(response_model)
            response = await structured_llm.ainvoke(prompt)
            # The response should be an instance of the response_model
            return response  # type: ignore[return-value]
        except Exception as e:
            raise ValueError(f"Structured LangChain LLM call failed: {e}") from e

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
                return f"Este documento contiene información importante sobre varios temas. El contenido analizado incluye: {content_preview}. Los puntos clave se han identificado y sintetizado para proporcionar una visión general coherente."
            else:
                return f"Esta sección presenta información detallada sobre {content_preview}. Se analiza el contenido de manera integral, proporcionando insights valiosos para la comprensión del tema tratado."
        else:
            if prompt_type == "document_summary":
                return f"This document contains important information about various topics. The analyzed content includes: {content_preview}. Key points have been identified and synthesized to provide a coherent overview."
            else:
                return f"This section provides detailed information about {content_preview}. The content is analyzed comprehensively, offering valuable insights for understanding the topic at hand."

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
            url = f"{self.config.ollama_base_url}/api/tags"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]

                    # Check if configured model is available
                    # Check if the main model is available
                    main_model = self.config.main_model or self.config.model_name
                    main_model_available = any(main_model in model for model in models)

                    if not main_model_available:
                        logger.warning(
                            f"Main model {main_model} not found in Ollama. Available models: {models}"
                        )

                    # Also check fast model if configured
                    fast_model_available = True
                    if (
                        self.config.enable_fast_first_pass
                        and self.config.fast_pass_model
                    ):
                        fast_model_available = any(
                            self.config.fast_pass_model in model for model in models
                        )
                        if not fast_model_available:
                            logger.warning(
                                f"Fast model {self.config.fast_pass_model} not found in Ollama. Available models: {models}"
                            )

                    return main_model_available and fast_model_available
                else:
                    logger.error(f"Ollama API returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to test Ollama connection: {e}")
            return False
