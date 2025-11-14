"""Type definitions for SQL generation components."""

from typing import TypedDict, Optional, List, Dict, Any

class SQLGenerationStep(TypedDict, total=False):
    """Track a single SQL generation attempt."""

    attempt_number: int
    """Which generation attempt is this (1, 2, ...)"""

    sql: str
    """Generated SQL query"""

    reasoning: str
    """LLM's explanation of why it generated this SQL"""

    timestamp: float
    """Unix timestamp of generation"""

    duration_ms: int
    """Time taken to generate (LLM latency)"""

    model: str
    """Which LLM model was used"""


class TableSchema(TypedDict, total=False):
    """Schema information for a single table."""

    name: str
    """Table name (e.g., 'orders')"""

    columns: Dict[str, str]
    """Mapping of column_name → column_type (e.g., {'order_id': 'INT64'})"""

    row_count: Optional[int]
    """Approximate row count from metadata"""

    description: Optional[str]
    """Table description from BigQuery metadata"""


class SchemaInfo(TypedDict, total=False):
    """Complete schema information for the database."""

    tables: Dict[str, TableSchema]
    """Mapping of table_name → TableSchema"""

    retrieved_at: float
    """Unix timestamp when schema was retrieved (for caching)"""

