"""Factory helpers for obtaining LLM chat models."""

from __future__ import annotations

from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from ..config import get_settings
from ..constants import LLMProvider


class LLMClientFactory:
    """Factory for creating chat models with smart provider fallback."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def _resolve_provider(self, explicit: Optional[LLMProvider]) -> LLMProvider:
        if explicit:
            return explicit
        preferred = self._settings.default_llm_provider

        if preferred == LLMProvider.GOOGLE and self._settings.google_api_key:
            return LLMProvider.GOOGLE
        if preferred == LLMProvider.OPENAI and self._settings.openai_api_key:
            return LLMProvider.OPENAI

        if self._settings.google_api_key:
            return LLMProvider.GOOGLE
        if self._settings.openai_api_key:
            return LLMProvider.OPENAI

        return preferred

    def create_chat_model(
        self,
        *,
        temperature: float = 0.0,
        provider: Optional[LLMProvider] = None,
    ) -> BaseChatModel:
        """Instantiate the configured chat model."""

        resolved_provider = self._resolve_provider(provider)

        if resolved_provider == LLMProvider.GOOGLE:
            if not self._settings.google_api_key:
                if self._settings.openai_api_key:
                    return self._create_openai_model(temperature)
                raise ValueError("GOOGLE_API_KEY is required for the Google LLM provider")
            return self._create_google_model(temperature)

        if resolved_provider == LLMProvider.OPENAI:
            if not self._settings.openai_api_key:
                if self._settings.google_api_key:
                    return self._create_google_model(temperature)
                raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")
            return self._create_openai_model(temperature)

        raise ValueError(f"Unsupported LLM provider: {resolved_provider}")

    def _create_google_model(self, temperature: float) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore import

        return ChatGoogleGenerativeAI(
            model=self._settings.google_model_name,
            google_api_key=self._settings.google_api_key,
            temperature=temperature,
        )

    def _create_openai_model(self, temperature: float) -> BaseChatModel:
        return ChatOpenAI(
            model=self._settings.openai_model_name,
            api_key=self._settings.openai_api_key,
            temperature=temperature,
        )


def get_chat_model(*, temperature: float = 0.0, provider: Optional[LLMProvider] = None) -> BaseChatModel:
    """Helper that fetches a chat model using the shared factory."""

    factory = LLMClientFactory()
    return factory.create_chat_model(temperature=temperature, provider=provider)


