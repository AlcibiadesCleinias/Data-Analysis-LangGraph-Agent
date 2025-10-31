import pandas as pd

from src.nodes.execution import execution_node


class DummyRunner:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def execute_query(self, sql_query: str, maximum_bytes_billed=None) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "month": ["2024-01-01", "2024-02-01"],
                "revenue": [1000.0, 1200.0],
            }
        )


def test_execution_node_collects_metrics(monkeypatch):
    monkeypatch.setattr("src.nodes.execution.BigQueryRunner", DummyRunner)

    state = {"sql_query": "SELECT 1", "metrics": {}}
    result = execution_node(state)

    assert result["validation_passed"] is True
    assert result["metrics"]["rows_returned"] == 2
    assert result["metrics"]["data_completeness"] == 1.0
    assert result["bq_results"]["columns"] == ["month", "revenue"]

