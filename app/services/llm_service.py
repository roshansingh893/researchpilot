"""
Configurable LLM provider factory.

ResearchPilot uses a small generate(prompt) -> str interface so the RAG service
does not depend on a specific vendor SDK.

Supported providers:
- groq:    ChatGroq via langchain-groq (production default)
- openai:  ChatOpenAI via langchain-openai
- test:    Deterministic stub for pytest (no API calls)

Future providers (add a branch in get_llm_service):
- ollama:  ChatOllama from langchain-ollama (local models)
"""

import logging
import os
from abc import ABC, abstractmethod
from functools import lru_cache

from app.core.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_LLM_MODEL,
)

logger = logging.getLogger(__name__)


class LLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text completion from a fully constructed prompt."""


class OpenAILLMService(LLMService):
    def __init__(self, model: str, api_key: str | None) -> None:
        from langchain_openai import ChatOpenAI

        self._llm = ChatOpenAI(model=model, api_key=api_key, temperature=0)

    def generate(self, prompt: str) -> str:
        response = self._llm.invoke(prompt)
        return str(response.content).strip()


class GroqLLMService(LLMService):
    def __init__(self, model: str, api_key: str | None) -> None:
        from langchain_groq import ChatGroq

        self._llm = ChatGroq(model=model, api_key=api_key, temperature=0)

    def generate(self, prompt: str) -> str:
        response = self._llm.invoke(prompt)
        return str(response.content).strip()


class TestLLMService(LLMService):
    """
    Deterministic LLM stub for automated tests.

    Returns grounded-style answers when known context phrases appear in the
    prompt; otherwise returns a generic context-based acknowledgement.
    """

    def generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if (
            "positional encoding injects order" in prompt_lower
            or "positional encoding is essential" in prompt_lower
            or "positional encoding is added before" in prompt_lower
        ):
            return (
                "Positional encoding injects order information into "
                "transformer inputs."
            )
        if "sqlite stores structured relational metadata" in prompt_lower:
            return (
                "SQLite stores structured relational metadata for documents."
            )
        if "self-attention computes weighted relationships" in prompt_lower:
            return (
                "Self-attention computes weighted relationships between tokens."
            )
        return "Answer synthesized from the provided document context."


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()

    if provider == "groq":
        logger.info("Loading LLM provider: Groq / %s", GROQ_MODEL)
        return GroqLLMService(model=GROQ_MODEL, api_key=GROQ_API_KEY)

    if provider == "openai":
        logger.info("Loading LLM provider: OpenAI / %s", OPENAI_LLM_MODEL)
        return OpenAILLMService(model=OPENAI_LLM_MODEL, api_key=OPENAI_API_KEY)

    if provider == "test":
        logger.info("Loading LLM provider: TestLLMService (stub).")
        return TestLLMService()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. "
        "Supported values: groq, openai, test."
    )


def generate_answer(prompt: str) -> str:
    """Generate an answer using the configured LLM provider."""
    return get_llm_service().generate(prompt)
