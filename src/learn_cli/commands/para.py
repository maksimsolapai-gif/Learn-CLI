"""`learn para` — list and move notes across PARA categories."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from learn_cli.config import Config
from learn_cli.ids import is_id
from learn_cli.notes import Note, find_note_by_id, iter_notes
from learn_cli.vault import require_vault

app = typer.Typer(help="PARA — projects / areas / resources / archive.")
console = Console()

CATEGORY_TO_DIR = {
    "projects": ("project", "projects"),
    "project":  ("project", "projects"),
    "p":        ("project", "projects"),
    "areas":    ("area", "areas"),
    "area":     ("area", "areas"),
    "a":        ("area", "areas"),
    "resources": ("resource", "resources"),
    "resource":  ("resource", "resources"),
    "r":         ("resource", "resources"),
    "archive":  ("archive", "archive"),
    "x":        ("archive", "archive"),
}


@app.command("list")
def list_command(
    category: str = typer.Argument(
        "all",
        help="One of: projects | areas | resources | archive | all (default).",
    ),
) -> None:
    """List notes in a PARA category."""
    vault = require_vault(Config.load())

    if category == "all":
        for c in ("projects", "areas", "resources", "archive"):
            _print_category(vault, c)
        return

    _print_category(vault, _normalize(category))


@app.command("move")
def move_command(
    note_id: str = typer.Argument(..., help="ID of the note to move."),
    category: str = typer.Argument(
        ..., help="Target category: projects | areas | resources | archive | zettel."
    ),
) -> None:
    """Move a note into a PARA category and update its `type` field."""
    if not is_id(note_id):
        console.print(f"[red]Not a valid note id:[/red] {note_id}")
        raise typer.Exit(code=1)

    vault = require_vault(Config.load())
    note = find_note_by_id(vault, note_id)
    if not note:
        console.print(f"[red]Note not found:[/red] {note_id}")
        raise typer.Exit(code=1)

    cat = category.lower()
    if cat in {"zettel", "z"}:
        new_type, new_dir = "zettel", "zettel"
    else:
        try:
            new_type, new_dir = CATEGORY_TO_DIR[_normalize(cat)]
        except KeyError:
            console.print(
                f"[red]Unknown category {category!r}. Use projects/areas/resources/archive/zettel.[/red]"
            )
            raise typer.Exit(code=1)

    target = vault / new_dir / note.path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target != note.path:
        console.print(f"[red]Target already exists:[/red] {target}")
        raise typer.Exit(code=1)

    if target != note.path:
        shutil.move(str(note.path), str(target))
    moved = Note.load(target)
    moved.type = new_type
    moved.save()
    console.print(
        f"[green]Moved[/green] {note.id} -> {target.relative_to(vault)} "
        f"[dim](type={new_type})[/dim]"
    )


def archive_command(note_id: str = typer.Argument(..., help="ID of the note to archive.")) -> None:
    """Move a note to `archive/` and mark its type accordingly."""
    move_command(note_id=note_id, category="archive")


def _normalize(c: str) -> str:
    c = c.lower()
    return c if c in CATEGORY_TO_DIR else c


def _print_category(vault: Path, category: str) -> None:
    if category not in CATEGORY_TO_DIR:
        console.print(f"[red]Unknown category {category!r}[/red]")
        raise typer.Exit(code=1)
    _, dirname = CATEGORY_TO_DIR[category]
    rows = []
    for p in iter_notes(vault, [dirname]):
        n = Note.load(p)
        rows.append(n)
    rows.sort(key=lambda n: n.id, reverse=True)

    table = Table(title=f"{dirname} ({len(rows)})")
    table.add_column("ID")
    table.add_column("Status", style="dim")
    table.add_column("Tags", style="dim")
    table.add_column("Title")
    for n in rows:
        table.add_row(n.id, n.status, ", ".join(n.tags), n.title)
    console.print(table)
