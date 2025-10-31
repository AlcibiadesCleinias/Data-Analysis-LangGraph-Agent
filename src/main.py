"""Entry module for building and invoking the LangGraph agent."""

from __future__ import annotations

from .graph import compile_agent
from .models.state import AgentState


agent = compile_agent()


def run_agent(user_query: str) -> AgentState:
    """Convenience function for single-turn execution."""

    initial_state: AgentState = {
        "user_query": user_query,
        "metrics": {},
        "validation_passed": False,
    }
    return agent.invoke(initial_state)


