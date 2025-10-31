"""Reasoning node: classify user query into analysis types."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage

try:
    from google.api_core.exceptions import GoogleAPIError
except ImportError:  # pragma: no cover - optional dependency guard
    GoogleAPIError = Exception

from ..constants import (
    DEFAULT_ANALYSIS_TYPE,
    SUPPORTED_ANALYSIS_TYPES,
    AnalysisType,
    LLMProvider,
)
from ..models.state import AgentState
from ..services.llm_client import get_chat_model
from .prompts import REASONING_PROMPT


LOGGER = logging.getLogger(__name__)


def _parse_response(content: str) -> Dict[str, Any]:
    cleaned = content.strip()

    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        LOGGER.debug("Reasoning response was not valid JSON", extra={"content": cleaned})
        return {
            "analysis_type": DEFAULT_ANALYSIS_TYPE.value,
            "reasoning": cleaned[:200] or "No reasoning provided.",
        }


def reasoning_node(state: AgentState) -> AgentState:
    """Classify the analysis type based on the user query."""

    user_query = state.get("user_query", "").strip()
    if not user_query:
        state["analysis_type"] = DEFAULT_ANALYSIS_TYPE
        state["analysis_plan"] = "User query missing; defaulting to product trends."
        return state

    prompt = REASONING_PROMPT + f"\n\nUser query: \"{user_query}\""

    try:
        chat_model = get_chat_model(temperature=0.0)
        response = chat_model.invoke([HumanMessage(content=prompt)])
    except GoogleAPIError as exc:  # pragma: no cover - external dependency
        LOGGER.warning("Primary LLM provider failed", exc_info=exc)
        try:
            chat_model = get_chat_model(temperature=0.0, provider=LLMProvider.OPENAI)
            response = chat_model.invoke([HumanMessage(content=prompt)])
        except ValueError:
            state["analysis_type"] = DEFAULT_ANALYSIS_TYPE.value
            state["analysis_plan"] = (
                "LLM unavailable; defaulting to product trends analysis."
            )
            return state
        except Exception as openai_error:  # pragma: no cover
            LOGGER.warning("Fallback LLM provider failed", exc_info=openai_error)
            state["analysis_type"] = DEFAULT_ANALYSIS_TYPE.value
            state["analysis_plan"] = (
                "LLM unavailable; defaulting to product trends analysis."
            )
            return state

    parsed = _parse_response(response.content if hasattr(response, "content") else str(response))
    raw_type = str(parsed.get("analysis_type", DEFAULT_ANALYSIS_TYPE.value)).strip().lower()

    try:
        analysis_type = AnalysisType(raw_type)
    except ValueError:
        LOGGER.warning("Unsupported analysis type, falling back to default", extra={"raw_type": raw_type})
        analysis_type = DEFAULT_ANALYSIS_TYPE

    if analysis_type not in SUPPORTED_ANALYSIS_TYPES:
        analysis_type = DEFAULT_ANALYSIS_TYPE

    state["analysis_type"] = analysis_type.value
    state["analysis_plan"] = str(parsed.get("reasoning", "")) or "No reasoning provided."

    return state


