"""LLM prompt templates used by the LangGraph agent."""
# TODO: add Langfuse/other tracking for prompt versions.

from __future__ import annotations

REASONING_PROMPT = (
    """
    You are a senior analytics strategist.

    Classify the user query into ONE category:
    1. "product_trends" – product performance, revenue over time
    2. "customer_segmentation" – customer groups, demographics
    3. "geo_analysis" – geographic patterns, regional sales

    Provide JSON: {"analysis_type": "...", "reasoning": "..."}
    """
    .strip()
)

# Insight prompt is kept concise; add instrumentation if prompts are versioned later.
INSIGHTS_PROMPT = (
    """
    You are a senior analytics consultant. Review the dataset sample and produce 2-3 concise
    business insights. Each insight should be on a separate line with no bullet symbols.

    Provided fields:
    - analysis_type: {analysis_type}
    - preferred chart type: {chart_type}
    - data sample (first rows): {data_sample}

    Focus on actionable observations (trends, segments, regions).
    """
    .strip()
)

# SQL Generation Prompt Template
SQL_GENERATION_PROMPT = """You are a BigQuery SQL expert. Your task is to generate valid BigQuery Standard SQL.

## Available Tables and Columns

{schema_context}

## Examples

Example 1 (Product Trends - Monthly Revenue):
User Query: "Show product revenue trends"
Generated SQL:
```sql
SELECT
    DATE_TRUNC(DATE(o.created_at), MONTH) AS month,
    COUNT(DISTINCT oi.product_id) AS unique_products,
    SUM(oi.sale_price) AS revenue
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
INNER JOIN `bigquery-public-data.thelook_ecommerce.orders` AS o
    ON oi.order_id = o.order_id
WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
GROUP BY month
ORDER BY month ASC
```

Example 2 (Customer Segmentation by Country):
User Query: "Segment customers by country"
Generated SQL:
```sql
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
```

## Your Task

User Query: "{user_query}"

Generate a SINGLE valid BigQuery SQL query that answers the user's question.

Requirements:
- Use only columns from available tables above
- Include proper JOINs where needed
- Add WHERE clause with date filter (last 12 months)
- Use GROUP BY and aggregations appropriately
- Return ONLY the SQL wrapped in ```sql``` block
- No explanations, just SQL

Generated SQL:
```sql
"""

# SQL Generation Retry Prompt (used when first attempt fails)
SQL_GENERATION_RETRY_PROMPT = """You are a BigQuery SQL expert. Fix the SQL based on the error.

## Available Tables and Columns

{schema_context}

## Previous Attempt (Attempt {attempt_number})

This SQL failed with an error:

```sql
{failed_sql}
```

Error Message:
{error_message}

## Your Task

Generate a corrected SQL query that fixes the error.

Requirements:
- Address the specific error mentioned above
- Use ONLY columns that exist in the available tables
- Keep the same logic but fix syntax/schema issues
- Return ONLY the corrected SQL wrapped in ```sql``` block

Corrected SQL:
```sql
"""

# Keep all prompt constants here; consider adding Langfuse/other tracking for versions.


