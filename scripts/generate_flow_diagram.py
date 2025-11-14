"""Generate a static diagram of the LangGraph flow using Graphviz."""

from __future__ import annotations

from pathlib import Path

from graphviz import Digraph


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "docs" / "agent_flow"


def build_graph() -> Digraph:
    dot = Digraph("LangGraphFlow", format="png")
    dot.attr(rankdir="LR", splines="spline", fontname="Inter", fontsize="12")
    dot.attr("node", shape="rect", style="filled", fillcolor="#2563eb", fontcolor="white", height="1", width="2")

    dot.node("start", "Start", shape="circle", fillcolor="#111827")
    dot.node("reasoning", "Reasoning")
    dot.node("schema_retrieval", "Schema Retrieval")
    dot.node("sql_generation", "SQL Generation")
    dot.node("execution", "Execution")
    dot.node("visualization", "Visualization")
    dot.node("insights", "Insights")
    dot.node("end", "End", shape="circle", fillcolor="#111827")
    dot.node("error_end", "Error End", shape="doublecircle", fillcolor="#ef4444")

    dot.edge("start", "reasoning")
    dot.edge("reasoning", "schema_retrieval")
    dot.edge("schema_retrieval", "sql_generation")
    dot.edge("sql_generation", "execution")
    dot.edge("execution", "visualization", label="validation_passed")
    dot.edge("visualization", "insights")
    dot.edge("insights", "end")
    dot.edge("execution", "error_end", label="validation_failed", style="dashed")

    return dot


def main() -> None:
    graph = build_graph()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    graph.render(filename=OUTPUT_PATH.name, directory=str(OUTPUT_PATH.parent), cleanup=True)
    print(f"Diagram written to {OUTPUT_PATH.with_suffix('.png')}")


if __name__ == "__main__":
    main()

