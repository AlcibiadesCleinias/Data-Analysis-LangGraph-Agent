from src.nodes.visualization import visualization_node


def test_visualization_node_returns_chart_json():
    state = {
        "validation_passed": True,
        "analysis_type": "product_trends",
        "chart_type": "line",
        "bq_results": {
            "data": [
                {"month": "2024-01-01", "revenue": 1000.0, "total_quantity": 10},
                {"month": "2024-02-01", "revenue": 1100.0, "total_quantity": 12},
            ]
        },
    }

    result = visualization_node(state)

    assert result["chart_json"] is not None

