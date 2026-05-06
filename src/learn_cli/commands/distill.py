"""`learn distill` — promote a note's status (CODE: Distill)."""

from __future__ import annotations

import typer
from rich.console import Console

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.ids import is_id
from learn_cli.notes import NOTE_STATUSES, find_note_by_id
from learn_cli.vault import require_vault

console = Console()

NEXT_STATUS = {
    "fleeting": "literature",
    "literature": "permanent",
    "permanent": "permanent",
}


def distill_command(
    note_id: str = typer.Argument(..., help="ID of the note to distill."),
    status: str = typer.Option(
        "", "--status", "-s",
        help=f"Target status: one of {', '.join(NOTE_STATUSES)}. Default: bump to next stage.",
    ),
    edit: bool = typer.Option(True, "--edit/--no-edit", help="Open in editor for highlighting."),
) -> None:
    """Open a note for progressive summarization and bump its status."""
    if not is_id(note_id):
        console.print(f"[red]Not a valid note id:[/red] {note_id}")
        raise typer.Exit(code=1)

    cfg = Config.load()
    vault = require_vault(cfg)

    note = find_note_by_id(vault, note_id)
    if not note:
        console.print(f"[red]Note not found:[/red] {note_id}")
        raise typer.Exit(code=1)

    target = status or NEXT_STATUS.get(note.status, "literature")
    if target not in NOTE_STATUSES:
        console.print(f"[red]Invalid status {target!r}. Use: {', '.join(NOTE_STATUSES)}[/red]")
        raise typer.Exit(code=1)

    note.status = target
    note.save()
    console.print(
        f"[green]Distilled[/green] {note.id}  status -> [bold]{note.status}[/bold]"
    )
    console.print("[dim]Bold the most important sentences, then review.[/dim]")

    if edit:
        open_in_editor(cfg.editor_command, note.path)
