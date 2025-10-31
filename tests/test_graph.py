from src.graph import build_agent_graph, compile_agent


def test_graph_compiles():
    graph = build_agent_graph()
    compiled = graph.compile()
    assert compiled is not None


def test_compile_agent_returns_callable():
    agent = compile_agent()
    assert hasattr(agent, "invoke")

