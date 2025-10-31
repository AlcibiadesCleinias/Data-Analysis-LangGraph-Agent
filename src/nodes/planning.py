"""Planning node: select SQL template and visualization config."""

from __future__ import annotations

import logging

from ..constants import (
    CHART_TYPE_BY_ANALYSIS,
    DEFAULT_ANALYSIS_TYPE,
    SQL_TEMPLATES,
    AnalysisType,
)
from ..models.state import AgentState


LOGGER = logging.getLogger(__name__)


def planning_node(state: AgentState) -> AgentState:
    """Populate SQL query and chart type based on the analysis selection."""

    raw_type = state.get("analysis_type", DEFAULT_ANALYSIS_TYPE.value)
    try:
        analysis_type = AnalysisType(str(raw_type))
    except ValueError:
        LOGGER.warning("Unknown analysis type during planning; falling back to default", extra={"raw_type": raw_type})
        analysis_type = DEFAULT_ANALYSIS_TYPE

    state["sql_query"] = SQL_TEMPLATES[analysis_type]
    state["chart_type"] = CHART_TYPE_BY_ANALYSIS[analysis_type].value

    return state


