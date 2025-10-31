"""Visualization node: convert tabular results into Plotly JSON."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Sequence

import pandas as pd
import plotly.express as px

from ..constants import ChartType
from ..models.state import AgentState


LOGGER = logging.getLogger(__name__)


def visualization_node(state: AgentState) -> AgentState:
    """Generate a Plotly chart JSON when validation succeeds."""

    if not state.get("validation_passed"):
        state["chart_json"] = None
        return state

    results = state.get("bq_results", {})
    data = results.get("data")
    if not data:
        state["chart_json"] = None
        return state

    data_frame = pd.DataFrame(data)
    columns = list(data_frame.columns)
    if not columns:
        state["chart_json"] = None
        return state

    raw_chart_type = state.get("chart_type", ChartType.BAR.value)
    try:
        chart_type = ChartType(str(raw_chart_type))
    except ValueError:
        LOGGER.warning("Unsupported chart type; defaulting to bar", extra={"raw_chart_type": raw_chart_type})
        chart_type = ChartType.BAR

    try:
        figure = _create_figure(chart_type, data_frame, columns, state)
        figure.update_layout(height=600, width=1100)
        state["chart_json"] = figure.to_json()

        try:
            output_dir = _resolve_output_dir()
            output_dir.mkdir(parents=True, exist_ok=True)
            file_name = f"{state.get('analysis_type', 'chart')}_{int(time.time())}.png"
            file_path = output_dir / file_name
            figure.write_image(str(file_path))
            state["chart_image_path"] = str(file_path)
        except Exception as artwork_error:  # pragma: no cover - filesystem/driver issues
            LOGGER.warning("Failed to write chart image", exc_info=artwork_error)
    except Exception as exc:  # pragma: no cover - plotting libs
        LOGGER.exception("Visualization failed")
        state["chart_json"] = None
        state["error_message"] = f"Visualization error: {exc}"

    return state


def _create_figure(chart_type: ChartType, df: pd.DataFrame, columns: Sequence[str], state: AgentState):
    if chart_type == ChartType.LINE:
        x_col = columns[0]
        y_cols = columns[1:] or columns[:1]
        figure = px.line(df, x=x_col, y=y_cols, markers=True)
        figure.update_traces(mode="lines+markers")
        return figure

    if chart_type == ChartType.SCATTER and len(columns) >= 2:
        return px.scatter(df, x=columns[0], y=columns[1], color=columns[2] if len(columns) > 2 else None)

    y_col = columns[1] if len(columns) > 1 else columns[0]
    return px.bar(df, x=columns[0], y=y_col)


def _resolve_output_dir() -> Path:
    env_path = os.getenv("PLOT_OUTPUT_DIR")
    if env_path:
        return Path(env_path)
    return Path.cwd() / "data-plotly"


