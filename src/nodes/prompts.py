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

# Keep all prompt constants here; consider adding Langfuse/other tracking for versions.


