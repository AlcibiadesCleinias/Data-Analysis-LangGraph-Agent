"""Project-wide constants and enumerations."""

from __future__ import annotations

from enum import Enum
from typing import Final


class AnalysisType(str, Enum):
    """Supported analysis types."""

    PRODUCT_TRENDS = "product_trends"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    GEO_ANALYSIS = "geo_analysis"


class ChartType(str, Enum):
    """Supported visualization chart types."""

    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"


class LLMProvider(str, Enum):
    """LLM providers available for the agent."""

    GOOGLE = "google"
    OPENAI = "openai"


SUPPORTED_ANALYSIS_TYPES: Final[tuple[AnalysisType, ...]] = (
    AnalysisType.PRODUCT_TRENDS,
    AnalysisType.CUSTOMER_SEGMENTATION,
    AnalysisType.GEO_ANALYSIS,
)

DEFAULT_ANALYSIS_TYPE: Final[AnalysisType] = AnalysisType.PRODUCT_TRENDS

CHART_TYPE_BY_ANALYSIS: Final[dict[AnalysisType, ChartType]] = {
    AnalysisType.PRODUCT_TRENDS: ChartType.LINE,
    AnalysisType.CUSTOMER_SEGMENTATION: ChartType.BAR,
    AnalysisType.GEO_ANALYSIS: ChartType.BAR,
}


SQL_TEMPLATES: Final[dict[AnalysisType, str]] = {
    AnalysisType.PRODUCT_TRENDS: """
        SELECT
            DATE_TRUNC(DATE(o.created_at), MONTH) AS month,
            COUNT(DISTINCT oi.product_id) AS unique_products,
            COUNT(oi.id) AS total_items,
            SUM(oi.sale_price) AS revenue
        FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
        INNER JOIN `bigquery-public-data.thelook_ecommerce.orders` AS o
            ON oi.order_id = o.order_id
        WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY month
        ORDER BY month ASC
    """.strip(),
    AnalysisType.CUSTOMER_SEGMENTATION: """
        SELECT
            u.country,
            COUNT(DISTINCT u.id) AS customer_count,
            SUM(oi.sale_price) AS total_revenue
        FROM `bigquery-public-data.thelook_ecommerce.users` AS u
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` AS o
            ON u.id = o.user_id
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
            ON oi.order_id = o.order_id
        WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY u.country
        ORDER BY customer_count DESC
        LIMIT 20
    """.strip(),
    AnalysisType.GEO_ANALYSIS: """
        SELECT
            u.country,
            u.state,
            COUNT(o.order_id) AS order_count,
            SUM(oi.sale_price) AS revenue
        FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
        INNER JOIN `bigquery-public-data.thelook_ecommerce.users` AS u
            ON o.user_id = u.id
        INNER JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi
            ON oi.order_id = o.order_id
        WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY u.country, u.state
        ORDER BY revenue DESC
        LIMIT 50
    """.strip(),
}


DEFAULT_GOOGLE_MODEL: Final[str] = "gemini-1.5-flash"
DEFAULT_OPENAI_MODEL: Final[str] = "gpt-4o-mini"
DEFAULT_MAX_BYTES_BILLED: Final[int] = 1_000_000_000


