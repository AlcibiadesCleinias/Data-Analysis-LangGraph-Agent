"""Graph assembly for the LangGraph data analysis agent."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from .models.state import AgentState
from .nodes import (
    execution_node,
    insights_node,
    planning_node,
    reasoning_node,
    visualization_node,
)


def build_agent_graph() -> StateGraph:
    """Construct the agent's state graph."""

    graph = StateGraph(AgentState)

    graph.add_node("reasoning", reasoning_node)
    graph.add_node("planning", planning_node)
    graph.add_node("execution", execution_node)
    graph.add_node("visualization", visualization_node)
    graph.add_node("insights", insights_node)

    graph.add_edge("reasoning", "planning")
    graph.add_edge("planning", "execution")

    graph.add_conditional_edges(
        "execution",
        _should_visualize,
        {"visualization": "visualization", "error_end": END},
    )

    graph.add_edge("visualization", "insights")
    graph.add_edge("insights", END)
    graph.set_entry_point("reasoning")

    return graph


def compile_agent():
    """Compile and return the runnable agent."""

    return build_agent_graph().compile()


def _should_visualize(state: AgentState) -> str:
    if state.get("validation_passed"):
        return "visualization"
    return "error_end"


