"""Typer CLI entrypoint for the LangGraph data analysis agent."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .graph import compile_agent
from .models.state import AgentState
app = typer.Typer(help="LangGraph Data Analysis Agent CLI")
console = Console()


@app.command()
def chat(
    save_chart: Optional[Path] = typer.Option(
        None,
        help="Optional path to write the latest chart JSON output.",
    ),
) -> None:
    """Interactive chat loop for querying the agent."""

    agent = compile_agent()
    console.print(Panel.fit("📊 LangGraph Data Analysis Agent", style="bold cyan"))
    console.print(
        Panel(
            Text.from_markup(
                "Dataset: [bold]bigquery-public-data.thelook_ecommerce[/bold]\n"
                "Docs: https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce",
            ),
            style="cyan",
        )
    )

    console.print(
        Panel(
            Text.from_markup(
                "Example prompts:\n"
                "• `Show product revenue trends for the last year`\n"
                "• `Segment customers by country for the past 12 months`\n"
                "• `Where are we seeing the strongest regional sales growth?`\n\n"
                "Type your own business question or choose one above."
            ),
            style="green",
        )
    )

    console.print("Type your business question (or 'exit' to quit).\n")

    while True:
        query = console.input("[bold green]You:[/bold green] ").strip()
        if query.lower() in {"exit", "quit"}:
            console.print("👋 Exiting. Goodbye!")
            break
        if not query:
            console.print("[yellow]Please enter a non-empty prompt.[/yellow]")
            continue

        state: AgentState = {
            "user_query": query,
            "metrics": {},
            "validation_passed": False,
        }

        result = agent.invoke(state)
        _display_result(result, save_chart)


def _display_result(result: AgentState, save_chart: Optional[Path]) -> None:
    console.print(Panel.fit(f"Analysis type: {result.get('analysis_type', 'unknown')}", style="bold blue"))
    console.print(f"Plan: {result.get('analysis_plan', 'N/A')}")

    metrics = result.get("metrics", {})
    if metrics:
        table = Table(title="Execution Metrics")
        table.add_column("Metric")
        table.add_column("Value")
        for key, value in metrics.items():
            table.add_row(key, str(value))
        console.print(table)

    insights = result.get("insights")
    if insights:
        console.print(Panel(insights, title="Insights", style="bold cyan"))

    if result.get("error_message"):
        console.print(f"[red]Error: {result['error_message']}[/red]")

    chart_json = result.get("chart_json")
    if chart_json:
        console.print("Chart generated successfully (JSON).")
        if save_chart:
            save_chart.write_text(chart_json, encoding="utf-8")
            console.print(f"Chart JSON written to {save_chart}")

    chart_image_path = result.get("chart_image_path")
    if chart_image_path:
        console.print(
            f"Chart image saved to [link=file://{chart_image_path}]open image[/link] "
            f"({chart_image_path})"
        )


if __name__ == "__main__":
    app()


