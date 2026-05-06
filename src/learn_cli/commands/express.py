"""`learn express` — list notes ready to be used (CODE: Express)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from learn_cli.config import Config
from learn_cli.notes import Note, iter_notes
from learn_cli.vault import require_vault

console = Console()


def express_command(
    status: str = typer.Option(
        "permanent", "--status", "-s",
        help="Filter by note status (default: permanent).",
    ),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Filter by tag(s)."),
) -> None:
    """List notes that are ready to be turned into something (article, talk, project)."""
    vault = require_vault(Config.load())

    wanted_tags = {t.strip().lower() for t in tag if t.strip()}
    rows: list[Note] = []
    for path in iter_notes(vault):
        n = Note.load(path)
        if status and n.status != status:
            continue
        if wanted_tags and not wanted_tags.issubset({t.lower() for t in n.tags}):
            continue
        rows.append(n)

    if not rows:
        console.print("[yellow]Nothing to express yet — keep distilling![/yellow]")
        return

    rows.sort(key=lambda n: n.id, reverse=True)

    table = Table(title=f"Ready to express ({len(rows)})")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Tags", style="dim")
    table.add_column("Title")
    for n in rows:
        table.add_row(n.id, n.type, ", ".join(n.tags), n.title)
    console.print(table)
