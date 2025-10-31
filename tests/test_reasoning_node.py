from typing import Any, List

from langchain_core.messages import BaseMessage

from src.nodes import reasoning_node


class DummyChatModel:
    def __init__(self, content: str) -> None:
        self._content = content

    def invoke(self, messages: List[BaseMessage]) -> Any:  # pragma: no cover - signature compliance
        return type("Response", (), {"content": self._content})()


def test_reasoning_node_classifies(monkeypatch):
    dummy_response = '{"analysis_type": "geo_analysis", "reasoning": "Focus on regions"}'

    def fake_get_chat_model(*args, **kwargs):
        return DummyChatModel(dummy_response)

    monkeypatch.setattr("src.nodes.reasoning.get_chat_model", fake_get_chat_model)

    state = {"user_query": "Show sales by geography"}
    result = reasoning_node(state)

    assert result["analysis_type"] == "geo_analysis"
    assert "regions" in result["analysis_plan"]

