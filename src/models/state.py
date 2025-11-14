"""State models for the LangGraph agent."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from .sql_generation_types import SQLGenerationStep, SchemaInfo

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
    schema_retrieval_time_ms: int
    """Time taken to retrieve schema"""
    sql_generation_time_ms: int
    """Time taken to generate SQL"""


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

    # Schema Context
    schema_info: Optional[SchemaInfo]
    """Database schema with available tables and columns"""

    available_tables: List[str]
    """List of table names accessible for this query"""

    # SQL Generation Tracking
    sql_generation_history: List[SQLGenerationStep]
    """History of all SQL generation attempts"""

    sql_generation_attempt: int
    """Current attempt number (1, 2, ...)"""

    last_execution_error: Optional[str]
    """Error from previous execution (if retry)"""


