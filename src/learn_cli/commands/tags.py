"""`learn tags` — list all tags with counts."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from learn_cli.config import Config
from learn_cli.notes import Note, iter_notes
from learn_cli.vault import require_vault

console = Console()


def tags_command(
    sort_by: str = typer.Option(
        "count", "--sort", help="Sort by 'count' (default) or 'name'."
    ),
) -> None:
    """List all tags used in the vault with their counts."""
    vault = require_vault(Config.load())

    counts: dict[str, int] = {}
    for path in iter_notes(vault):
        n = Note.load(path)
        for t in n.tags:
            t = t.strip()
            if t:
                counts[t] = counts.get(t, 0) + 1

    if not counts:
        console.print("[yellow]No tags yet.[/yellow]")
        return

    items = list(counts.items())
    if sort_by == "name":
        items.sort(key=lambda kv: kv[0].lower())
    else:
        items.sort(key=lambda kv: (-kv[1], kv[0].lower()))

    table = Table(title=f"Tags ({len(items)})")
    table.add_column("Tag")
    table.add_column("Count", justify="right")
    for name, count in items:
        table.add_row(name, str(count))
    console.print(table)
