"""Baseline queries for evaluation."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from .constants import AnalysisType
from .services.bigquery_runner import BigQueryRunner


BASELINE_QUERIES: Mapping[AnalysisType, str] = {
    AnalysisType.PRODUCT_TRENDS: """
        SELECT
            DATE_TRUNC(o.created_at, MONTH) AS month,
            SUM(oi.sale_price * oi.quantity) AS revenue
        FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
        INNER JOIN `bigquery-public-data.thelook_ecommerce.orders` AS o
            ON oi.order_id = o.order_id
        WHERE o.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY month
        ORDER BY month ASC
    """.strip(),
    AnalysisType.CUSTOMER_SEGMENTATION: """
        SELECT
            u.country,
            COUNT(DISTINCT u.id) AS customer_count
        FROM `bigquery-public-data.thelook_ecommerce.users` AS u
        GROUP BY u.country
        ORDER BY customer_count DESC
    """.strip(),
    AnalysisType.GEO_ANALYSIS: """
        SELECT
            u.country,
            COUNT(o.order_id) AS order_count
        FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
        INNER JOIN `bigquery-public-data.thelook_ecommerce.users` AS u
            ON o.user_id = u.id
        GROUP BY u.country
        ORDER BY order_count DESC
    """.strip(),
}


# deprecafted, not used in MVP.
def run_baseline(analysis_type: AnalysisType) -> pd.DataFrame:
    """Execute the baseline query for comparison."""

    runner = BigQueryRunner()
    return runner.execute_query(BASELINE_QUERIES[analysis_type])


