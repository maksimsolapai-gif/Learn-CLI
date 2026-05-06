"""`learn new` — create a new permanent zettel."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.ids import new_id
from learn_cli.notes import Note, filename_for, now_iso
from learn_cli.templates import render
from learn_cli.vault import require_vault

console = Console()


def new_command(
    title: str = typer.Argument(..., help="Title of the new zettel."),
    tag: list[str] = typer.Option(
        [], "--tag", "-t", help="Add tag(s). Repeat or comma-separate."
    ),
    no_open: bool = typer.Option(False, "--no-open", help="Do not launch the editor."),
) -> None:
    """Create a new atomic zettel and open it in the editor."""
    cfg = Config.load()
    vault = require_vault(cfg)

    nid = new_id()
    tags = _flatten_tags(tag)
    fname = filename_for(nid, title)
    path = vault / "zettel" / fname

    if path.exists():
        console.print(f"[red]A note with this id/slug already exists:[/red] {path}")
        raise typer.Exit(code=1)

    body = render("zettel", id=nid, title=title, created=now_iso())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")

    note = Note.load(path)
    note.title = title
    note.tags = tags
    note.created = note.created or now_iso()
    note.save()

    console.print(f"[green]Created[/green] {path}")
    if not no_open:
        open_in_editor(cfg.editor_command, path)


def _flatten_tags(values: list[str]) -> list[str]:
    out: list[str] = []
    for v in values:
        for piece in str(v).split(","):
            piece = piece.strip()
            if piece and piece not in out:
                out.append(piece)
    return out
