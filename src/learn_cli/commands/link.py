"""`learn link` — create bidirectional link between two zettels."""

from __future__ import annotations

import typer
from rich.console import Console

from learn_cli.config import Config
from learn_cli.links import link_pair
from learn_cli.vault import require_vault

console = Console()


def link_command(
    id_a: str = typer.Argument(..., help="First note ID."),
    id_b: str = typer.Argument(..., help="Second note ID."),
) -> None:
    """Add a bidirectional link between two notes (updates `links:` in both)."""
    vault = require_vault(Config.load())
    try:
        a, b = link_pair(vault, id_a, id_b)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]Linked[/green] {a.id} <-> {b.id}")
