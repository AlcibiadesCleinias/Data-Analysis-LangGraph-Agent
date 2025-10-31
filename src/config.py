"""Configuration management for the LangGraph Data Analysis Agent."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_GOOGLE_MODEL,
    DEFAULT_MAX_BYTES_BILLED,
    DEFAULT_OPENAI_MODEL,
    LLMProvider,
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    google_project_id: Optional[str] = Field(default=None, alias="GOOGLE_CLOUD_PROJECT_ID")
    default_llm_provider: LLMProvider = Field(
        default=LLMProvider.GOOGLE,
        alias="DEFAULT_LLM_PROVIDER",
    )
    google_model_name: str = Field(
        default=DEFAULT_GOOGLE_MODEL,
        alias="GOOGLE_MODEL_NAME",
    )
    openai_model_name: str = Field(
        default=DEFAULT_OPENAI_MODEL,
        alias="OPENAI_MODEL_NAME",
    )
    bigquery_maximum_bytes_billed: int = Field(
        default=DEFAULT_MAX_BYTES_BILLED,
        alias="BIGQUERY_MAX_BYTES",
    )
    bigquery_location: Optional[str] = Field(default=None, alias="BIGQUERY_LOCATION")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


