"""Execution node: run BigQuery SQL and collect metrics."""

from __future__ import annotations

import logging
import time

import pandas as pd

from ..models.state import AgentState, Metrics, QueryResult
from ..services.bigquery_runner import BigQueryRunner

try:
    from google.auth.exceptions import DefaultCredentialsError
except ImportError:  # pragma: no cover
    DefaultCredentialsError = Exception


LOGGER = logging.getLogger(__name__)


def execution_node(state: AgentState) -> AgentState:
    """Execute the prepared SQL query against BigQuery."""

    sql_query = state.get("sql_query")
    if not sql_query:
        state["validation_passed"] = False
        state["error_message"] = "SQL query not set"
        state["last_execution_error"] = "SQL query not set"
        return state

    try:
        runner = BigQueryRunner()
    except DefaultCredentialsError as cred_error:  # pragma: no cover - external dependency
        LOGGER.exception("BigQuery credentials not found", exc_info=cred_error)
        metrics: Metrics = dict(state.get("metrics", {}))  # type: ignore[assignment]
        metrics["latency_sec"] = 0.0
        state["metrics"] = metrics
        state["validation_passed"] = False
        error_msg = (
            "BigQuery credentials missing. Run 'python -m src.cli auth' or set "
            "GOOGLE_APPLICATION_CREDENTIALS."
        )
        state["error_message"] = error_msg
        state["last_execution_error"] = error_msg
        return state

    metrics: Metrics = dict(state.get("metrics", {}))  # type: ignore[assignment]

    start_time = time.perf_counter()
    try:
        df = runner.execute_query(sql_query)
    except Exception as exc:  # pragma: no cover - network/external dependency
        LOGGER.exception("BigQuery execution failed")
        metrics["latency_sec"] = time.perf_counter() - start_time
        state["metrics"] = metrics
        state["validation_passed"] = False
        error_msg = str(exc)
        state["error_message"] = error_msg
        state["last_execution_error"] = error_msg
        return state

    latency = time.perf_counter() - start_time
    metrics["latency_sec"] = latency
    row_count, column_count = df.shape
    metrics["rows_returned"] = row_count

    completeness = _calculate_completeness(df)
    metrics["data_completeness"] = completeness

    result: QueryResult = {
        "data": df.to_dict(orient="records"),
        "shape": df.shape,
        "columns": list(df.columns),
    }

    state["bq_results"] = result
    state["metrics"] = metrics

    is_valid = row_count > 0 and completeness >= 0.8
    state["validation_passed"] = bool(is_valid)
    if is_valid:
        state["error_message"] = None
        state["last_execution_error"] = None
    else:
        error_msg = state.get(
            "error_message",
            "Query returned insufficient data for visualization",
        )
        state["error_message"] = error_msg
        state["last_execution_error"] = error_msg

    return state


def _calculate_completeness(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0
    null_count = df.isnull().sum().sum()
    completeness = 1.0 - (float(null_count) / float(total_cells))
    return round(float(completeness), 4)


