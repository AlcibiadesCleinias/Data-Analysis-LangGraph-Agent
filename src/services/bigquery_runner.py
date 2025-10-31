"""Utility wrapper around the BigQuery client."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from google.cloud import bigquery

from ..config import get_settings


LOGGER = logging.getLogger(__name__)


class BigQueryRunner:
    """A lean BigQuery client for executing SQL queries."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset_id: str = "bigquery-public-data.thelook_ecommerce",
        client: Optional[bigquery.Client] = None,
    ) -> None:
        settings = get_settings()
        resolved_project = project_id or settings.google_project_id
        self.client = client or bigquery.Client(project=resolved_project)
        self.dataset_id = dataset_id
        self._maximum_bytes_billed = settings.bigquery_maximum_bytes_billed
        self._location = settings.bigquery_location
        LOGGER.debug(
            "Initialized BigQueryRunner", extra={"project": resolved_project, "dataset": dataset_id}
        )

    def execute_query(
        self,
        sql_query: str,
        maximum_bytes_billed: Optional[int] = None,
    ) -> pd.DataFrame:
        """Execute SQL query and return a DataFrame."""

        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=maximum_bytes_billed or self._maximum_bytes_billed
        )

        LOGGER.info("Executing BigQuery query", extra={"maximum_bytes_billed": job_config.maximum_bytes_billed})
        query_job = self.client.query(
            sql_query,
            job_config=job_config,
            location=self._location,
        )

        result_df = query_job.result().to_dataframe(create_bqstorage_client=False)
        LOGGER.info("Query completed", extra={"rows": len(result_df), "columns": list(result_df.columns)})
        return result_df

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Return schema metadata for a table."""

        table_ref = f"{self.dataset_id}.{table_name}"
        table = self.client.get_table(table_ref)
        return [
            {
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
                "description": field.description or "",
            }
            for field in table.schema
        ]


