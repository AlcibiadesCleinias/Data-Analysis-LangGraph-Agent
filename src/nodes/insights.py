"""Insights node: summarize results into business takeaways."""

from __future__ import annotations

import logging
from typing import List

from langchain_core.messages import HumanMessage

from ..models.state import AgentState
from ..services.llm_client import get_chat_model
from ..constants import LLMProvider
from .prompts import INSIGHTS_PROMPT

try:
    from google.api_core.exceptions import GoogleAPIError
except ImportError:  # pragma: no cover
    GoogleAPIError = Exception


LOGGER = logging.getLogger(__name__)


def insights_node(state: AgentState) -> AgentState:
    """Generate concise business insights using the LLM."""

    results = state.get("bq_results", {})
    data_sample: List[dict] = results.get("data", [])[:5]
    if not data_sample:
        state["insights"] = "No data available for insights."
        return state

    chart_type = state.get("chart_type", "")
    analysis_type = state.get("analysis_type", "")

    prompt = INSIGHTS_PROMPT.format(
        analysis_type=analysis_type,
        chart_type=chart_type,
        data_sample=data_sample,
    )

    try:
        chat_model = get_chat_model(temperature=0.1)
        response = chat_model.invoke([HumanMessage(content=prompt)])
    except GoogleAPIError as exc:  # pragma: no cover - external dependency
        LOGGER.warning("Primary LLM provider failed", exc_info=exc)
        try:
            chat_model = get_chat_model(temperature=0.1, provider=LLMProvider.OPENAI)
            response = chat_model.invoke([HumanMessage(content=prompt)])
        except ValueError:
            state["insights"] = "LLM unavailable; unable to generate insights."
            return state
        except Exception as openai_error:  # pragma: no cover
            LOGGER.warning("Fallback LLM provider failed", exc_info=openai_error)
            state["insights"] = "LLM unavailable; unable to generate insights."
            return state
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Insight generation failed")
        state["insights"] = f"Insight generation failed: {exc}"
        return state

    state["insights"] = response.content if hasattr(response, "content") else str(response)

    return state


