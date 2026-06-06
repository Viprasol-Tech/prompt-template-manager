"""Command-line interface for Prompt Template Manager.

``prompt-template-manager demo`` registers a couple of versioned templates,
renders the latest, and shows version resolution — all offline, no API keys.

Part of Prompt Template Manager by Viprasol Tech Private Limited
(https://viprasol.com).
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from prompt_template_manager import __version__
from prompt_template_manager.registry import PromptRegistry
from prompt_template_manager.template import MissingVariableError, PromptTemplate

app = typer.Typer(add_completion=False, help="Prompt Template Manager — by Viprasol Tech.")
console = Console()


def _demo_registry() -> PromptRegistry:
    """Build a registry pre-loaded with two versions of a 'summarize' template."""
    registry = PromptRegistry()
    registry.register(
        PromptTemplate(
            name="summarize",
            version=1,
            body="Summarize the following text:\n\n{text}",
        )
    )
    registry.register(
        PromptTemplate(
            name="summarize",
            version=2,
            body="Summarize the following {style} text in {sentences} sentences:\n\n{text}",
        )
    )
    return registry


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"prompt-template-manager [bold cyan]{__version__}[/] - by Viprasol Tech")


@app.command()
def demo() -> None:
    """Register versioned templates, then render the latest one offline."""
    registry = _demo_registry()

    table = Table(title="Registered templates")
    table.add_column("name", style="cyan")
    table.add_column("versions")
    table.add_column("latest required vars")
    for name in registry.names():
        versions = registry.list_versions(name)
        latest = registry.latest(name)
        table.add_row(
            name,
            ", ".join(str(v) for v in versions),
            ", ".join(latest.required_variables),
        )
    console.print(table)

    latest = registry.latest("summarize")
    console.print(f"\nUsing [bold]summarize[/] v[bold]{latest.version}[/] (latest):")
    rendered = latest.render(
        style="technical",
        sentences=3,
        text="Prompt templates keep your LLM calls consistent and versioned.",
    )
    console.print("[dim]--- rendered prompt ---[/]")
    console.print(rendered)
    console.print("[dim]-----------------------[/]")

    # Demonstrate validation: rendering v2 without 'text' raises.
    try:
        latest.render(style="plain", sentences=1)
    except MissingVariableError as exc:
        console.print(f"\n[yellow]Validation works:[/] {exc}")

    # Demonstrate fetching a specific older version.
    v1 = registry.get("summarize", version=1)
    console.print(f"\nFetched specific version v{v1.version}; requires: {v1.required_variables}")


if __name__ == "__main__":
    app()
