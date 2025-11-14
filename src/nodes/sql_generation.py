"""SQL generation node: LLM generates SQL using schema context."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict

from langchain_core.messages import HumanMessage

from ..constants import (
    CHART_TYPE_BY_ANALYSIS,
    DEFAULT_ANALYSIS_TYPE,
    LLMProvider,
    AnalysisType,
)
from ..models.state import AgentState
from ..models.sql_generation_types import SQLGenerationStep
from ..services.llm_client import get_chat_model
from ..config import get_settings
from .prompts import SQL_GENERATION_PROMPT, SQL_GENERATION_RETRY_PROMPT

LOGGER = logging.getLogger(__name__)


def _schema_to_context(schema_info: Dict[str, Any]) -> str:
    """
    Convert schema_info dict to readable text format for LLM prompt.

    Example output:
    ## orders
    - order_id: INT64
    - user_id: INT64
    - created_at: TIMESTAMP
    ...
    """

    if not schema_info or "tables" not in schema_info:
        return "(No schema available)"

    lines = []
    for table_name, table_info in schema_info.get("tables", {}).items():
        lines.append(f"## {table_name}")
        for col_name, col_type in table_info.get("columns", {}).items():
            lines.append(f"- {col_name}: {col_type}")
        lines.append("")

    return "\n".join(lines)


def _extract_sql_from_response(response_text: str) -> str:
    """Extract SQL from code block or use entire response."""

    # Try to extract from ```sql``` block
    pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: try just ``` block
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: use entire response
    return response_text.strip()


def _get_sql_generation_model():
    """
    Get chat model for SQL generation.
    Uses gemini-1.5-pro for better SQL generation quality.
    Falls back to default model if gemini-1.5-pro is not available.
    """
    settings = get_settings()
    
    # Try to use gemini-1.5-pro for SQL generation
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore import
        
        if settings.google_api_key:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=settings.google_api_key,
                temperature=0.0,
            )
    except Exception as e:
        LOGGER.debug("Failed to create gemini-1.5-pro model, falling back to default", extra={"error": str(e)})
    
    # Fallback to default model
    return get_chat_model(temperature=0.0)


def sql_generation_node(state: AgentState) -> AgentState:
    """
    Generate SQL query using LLM with schema context.

    Input state fields:
        - user_query: Original user query
        - analysis_type: Intent classification
        - schema_info: Database schema with tables/columns
        - sql_generation_attempt: Current attempt number (1, 2, ...)
        - last_execution_error: Error from previous execution (if retry)

    Output state fields:
        - sql_query: Generated SQL
        - sql_generation_history: Appended with new attempt
        - metrics["sql_generation_time_ms"]: Time taken

    On error, logs warning but doesn't crash (may use fallback template later).
    """

    user_query = state.get("user_query", "").strip()
    analysis_type = state.get("analysis_type", DEFAULT_ANALYSIS_TYPE.value)
    schema_info = state.get("schema_info", {})
    attempt_number = state.get("sql_generation_attempt", 1)
    last_error = state.get("last_execution_error")

    start_time = time.perf_counter()

    if not user_query:
        LOGGER.warning("No user query provided to SQL generation node")
        state["sql_query"] = ""
        return state

    try:
        # Format schema for prompt
        schema_context = _schema_to_context(schema_info)

        # Choose prompt template based on attempt
        if attempt_number == 1:
            # First attempt: standard prompt
            prompt_template = SQL_GENERATION_PROMPT
            prompt = prompt_template.format(
                schema_context=schema_context,
                user_query=user_query,
            )
        else:
            # Retry attempt: include error context
            failed_sql = state.get("sql_query", "")
            prompt_template = SQL_GENERATION_RETRY_PROMPT
            prompt = prompt_template.format(
                schema_context=schema_context,
                attempt_number=attempt_number,
                failed_sql=failed_sql,
                error_message=last_error or "Unknown error",
            )

        # Call LLM
        chat_model = _get_sql_generation_model()
        response = chat_model.invoke([HumanMessage(content=prompt)])
        response_text = response.content if hasattr(response, "content") else str(response)

        # Extract SQL from response
        generated_sql = _extract_sql_from_response(response_text)

        if not generated_sql:
            LOGGER.warning("No SQL extracted from LLM response")
            state["sql_query"] = ""
            return state

        # Validate SQL is not empty
        if len(generated_sql.strip()) < 10:
            LOGGER.warning("Generated SQL too short", extra={"length": len(generated_sql)})
            state["sql_query"] = ""
            return state

        state["sql_query"] = generated_sql

        # Set chart_type based on analysis_type (for visualization node)
        try:
            analysis_type_enum = AnalysisType(analysis_type)
            chart_type = CHART_TYPE_BY_ANALYSIS.get(analysis_type_enum)
            if chart_type:
                state["chart_type"] = chart_type.value
        except (ValueError, KeyError):
            # Fallback to default if analysis_type is not recognized
            LOGGER.debug("Could not determine chart_type from analysis_type", extra={"analysis_type": analysis_type})

        # Track generation attempt
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        generation_step: SQLGenerationStep = {
            "attempt_number": attempt_number,
            "sql": generated_sql,
            "reasoning": f"Attempt {attempt_number}: {last_error or 'First attempt'}",
            "timestamp": time.time(),
            "duration_ms": latency_ms,
            "model": "gemini-1.5-pro",
        }

        history = list(state.get("sql_generation_history", []))
        history.append(generation_step)
        state["sql_generation_history"] = history

        # Track metrics
        metrics = dict(state.get("metrics", {}))  # type: ignore[assignment]
        metrics["sql_generation_time_ms"] = latency_ms
        state["metrics"] = metrics

        LOGGER.info(
            "SQL generated",
            extra={
                "attempt": attempt_number,
                "sql_length": len(generated_sql),
                "latency_ms": latency_ms,
            },
        )

    except Exception as exc:  # pragma: no cover
        LOGGER.warning(
            "SQL generation failed",
            extra={"error": str(exc), "attempt": attempt_number},
        )
        state["sql_query"] = ""

    return state

