"""Evaluation utilities for comparing agent output to baselines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from .models.state import Metrics, QueryResult


@dataclass
class MVPMetrics:
    latency_sec: float
    data_completeness: float
    rows_returned: int
    matches_baseline: bool = False


def evaluate_result(
    agent_output: QueryResult,
    metrics: Metrics,
    baseline_output: pd.DataFrame,
) -> MVPMetrics:
    """Compare agentic result vs. baseline query output."""

    agent_df = pd.DataFrame(agent_output.get("data", []))
    baseline_df = baseline_output

    matches = _rough_match(agent_df, baseline_df)

    return MVPMetrics(
        latency_sec=float(metrics.get("latency_sec", 0.0)),
        data_completeness=float(metrics.get("data_completeness", 1.0)),
        rows_returned=int(agent_df.shape[0]) if not agent_df.empty else 0,
        matches_baseline=matches,
    )


def _rough_match(agent_df: pd.DataFrame, baseline_df: pd.DataFrame) -> bool:
    if agent_df.empty or baseline_df.empty:
        return False

    row_delta = abs(agent_df.shape[0] - baseline_df.shape[0])
    if row_delta > 2:
        return False

    shared_columns = set(agent_df.columns) & set(baseline_df.columns)
    if not shared_columns:
        return False

    sampled_cols: Sequence[str] = list(shared_columns)[:2]
    agent_sample = agent_df.iloc[:5][sampled_cols].round(3)
    baseline_sample = baseline_df.iloc[:5][sampled_cols].round(3)

    return agent_sample.equals(baseline_sample)


