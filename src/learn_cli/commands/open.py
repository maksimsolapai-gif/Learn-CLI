"""`learn open` — open a note by id or query in the editor."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.ids import is_id
from learn_cli.notes import find_note_by_id, find_notes_by_query
from learn_cli.vault import require_vault

console = Console()


def open_command(
    query: str = typer.Argument(..., help="Note id or filename substring."),
) -> None:
    """Open a note in the configured editor."""
    cfg = Config.load()
    vault = require_vault(cfg)

    if is_id(query):
        note = find_note_by_id(vault, query)
        if not note:
            console.print(f"[red]No note with id {query}[/red]")
            raise typer.Exit(code=1)
        open_in_editor(cfg.editor_command, note.path)
        return

    matches = find_notes_by_query(vault, query)
    if not matches:
        console.print(f"[red]No matches for {query!r}[/red]")
        raise typer.Exit(code=1)
    if len(matches) == 1:
        open_in_editor(cfg.editor_command, matches[0].path)
        return

    table = Table(title=f"Matches for {query!r}")
    table.add_column("#", justify="right")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Title")
    for i, n in enumerate(matches, 1):
        table.add_row(str(i), n.id, n.type, n.title)
    console.print(table)

    choice = typer.prompt("Open #", default="1")
    try:
        idx = int(choice) - 1
        target = matches[idx]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
        raise typer.Exit(code=1)
    open_in_editor(cfg.editor_command, target.path)
