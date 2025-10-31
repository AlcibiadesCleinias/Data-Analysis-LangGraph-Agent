"""State models for the LangGraph agent."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

class QueryResult(TypedDict, total=False):
    """Structure for BigQuery execution results stored in state."""

    data: List[Dict[str, Any]]
    shape: tuple[int, int]
    columns: List[str]


class Metrics(TypedDict, total=False):
    """Execution metrics collected during the agent run."""

    latency_sec: float
    data_completeness: float
    rows_returned: int
    baseline_match: bool


class AgentState(TypedDict, total=False):
    """Shared LangGraph state container for the agent."""

    # Input
    user_query: str

    # Analysis decision
    analysis_type: str
    analysis_plan: str

    # Execution
    sql_query: str
    chart_type: str
    bq_results: QueryResult

    # Output
    chart_json: str
    chart_image_path: str
    insights: str

    # Quality
    validation_passed: bool
    metrics: Metrics
    error_message: Optional[str]


