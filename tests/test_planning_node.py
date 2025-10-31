from src.constants import AnalysisType, ChartType
from src.nodes.planning import planning_node


def test_planning_node_sets_sql_and_chart_type():
    state = {"analysis_type": AnalysisType.PRODUCT_TRENDS.value}

    updated_state = planning_node(state)

    assert "FROM `bigquery-public-data.thelook_ecommerce.order_items`" in updated_state["sql_query"]
    assert updated_state["chart_type"] == ChartType.LINE.value

