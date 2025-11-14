"""Schema retrieval node: fetch database metadata from INFORMATION_SCHEMA."""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, Optional

from ..models.state import AgentState
from ..models.sql_generation_types import SchemaInfo, TableSchema
from ..services.bigquery_runner import BigQueryRunner

LOGGER = logging.getLogger(__name__)


def schema_retrieval_node(state: AgentState) -> AgentState:
    """
    Retrieve schema information from BigQuery INFORMATION_SCHEMA.

    Input state fields:
        - analysis_type: Classification of user intent (used for filtering)
        - user_query: Original user query (for logging)

    Output state fields:
        - schema_info: SchemaInfo dict with tables and columns
        - available_tables: List of table names
        - metrics["schema_retrieval_time_ms"]: Time taken

    Errors are logged but don't halt execution (fallback to empty schema).
    """

    analysis_type = state.get("analysis_type", "product_trends")
    user_query = state.get("user_query", "").strip()

    start_time = time.perf_counter()

    # Define which tables are relevant per analysis type
    # (These map to columns in thelook_ecommerce dataset)
    RELEVANT_TABLES = {
        "product_trends": ["orders", "order_items", "products"],
        "customer_segmentation": ["users", "orders", "order_items"],
        "geo_analysis": ["users", "orders", "order_items"],
    }

    relevant_tables = RELEVANT_TABLES.get(analysis_type, ["orders", "users", "order_items"])

    try:
        runner = BigQueryRunner()
        client = runner.client

        schema_info: SchemaInfo = {
            "tables": {},
            "retrieved_at": time.time(),
        }

        # Query INFORMATION_SCHEMA for each relevant table
        for table_name in relevant_tables:
            try:
                # Get table metadata
                table = client.get_table(
                    f"bigquery-public-data.thelook_ecommerce.{table_name}"
                )

                # Build columns dict
                columns: Dict[str, str] = {}
                for field in table.schema:
                    columns[field.name] = str(field.field_type)

                # Create TableSchema
                table_schema: TableSchema = {
                    "name": table_name,
                    "columns": columns,
                    "row_count": table.num_rows,
                    "description": table.description or f"Table: {table_name}",
                }

                schema_info["tables"][table_name] = table_schema

                LOGGER.info(
                    "Schema retrieved for table",
                    extra={
                        "table": table_name,
                        "columns": len(columns),
                        "row_count": table.num_rows,
                    },
                )

            except Exception as table_error:  # pragma: no cover
                LOGGER.warning(
                    "Failed to retrieve schema for table",
                    extra={"table": table_name, "error": str(table_error)},
                )
                continue

        state["schema_info"] = schema_info
        state["available_tables"] = list(schema_info["tables"].keys())

    except Exception as exc:  # pragma: no cover
        LOGGER.warning(
            "Schema retrieval failed",
            extra={"error": str(exc), "analysis_type": analysis_type},
        )
        # Fallback: empty schema
        state["schema_info"] = {"tables": {}, "retrieved_at": time.time()}
        state["available_tables"] = []

    # Track metric
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    metrics = dict(state.get("metrics", {}))  # type: ignore[assignment]
    metrics["schema_retrieval_time_ms"] = latency_ms
    state["metrics"] = metrics

    LOGGER.info(
        "Schema retrieval complete",
        extra={
            "tables": len(state.get("available_tables", [])),
            "latency_ms": latency_ms,
        },
    )

    return state

