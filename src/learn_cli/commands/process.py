"""`learn process` — walk the inbox and route each note (CODE: Organize)."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.notes import Note, iter_notes, now_iso
from learn_cli.vault import require_vault

console = Console()

CHOICES = {
    "z": ("zettel", "zettel"),
    "p": ("project", "projects"),
    "a": ("area", "areas"),
    "r": ("resource", "resources"),
    "x": ("archive", "archive"),
    "k": ("inbox", "inbox"),
}


def process_command(
    edit: bool = typer.Option(False, "--edit", "-e", help="Open each note in the editor first."),
    limit: int = typer.Option(0, "--limit", "-n", help="Process at most N notes (0 = all)."),
) -> None:
    """Interactively triage every note in `inbox/`."""
    cfg = Config.load()
    vault = require_vault(cfg)

    inbox_paths = sorted(iter_notes(vault, ["inbox"]))
    if not inbox_paths:
        console.print("[yellow]Inbox is empty — nothing to process.[/yellow]")
        return

    if limit and limit > 0:
        inbox_paths = inbox_paths[:limit]

    for idx, path in enumerate(inbox_paths, 1):
        note = Note.load(path)
        _show(note, idx, len(inbox_paths))
        if edit:
            open_in_editor(cfg.editor_command, path)
            note = Note.load(path)

        action = typer.prompt(
            "Move to [z]ettel / [p]roject / [a]rea / [r]esource / archi[x]e / [k]eep / [d]elete / [s]kip",
            default="k",
        ).strip().lower()

        if action == "d":
            path.unlink(missing_ok=True)
            console.print(f"[red]Deleted[/red] {path.name}")
            continue
        if action == "s":
            console.print("[dim]Skipped[/dim]")
            continue
        if action not in CHOICES:
            console.print(f"[yellow]Unknown action {action!r} — kept[/yellow]")
            continue

        new_type, new_dir = CHOICES[action]
        target = vault / new_dir / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target != path:
            console.print(f"[red]Target already exists:[/red] {target}")
            continue

        if target != path:
            shutil.move(str(path), str(target))

        moved = Note.load(target)
        moved.type = new_type
        if new_type == "zettel" and moved.status == "fleeting":
            moved.status = "literature"
        if not moved.created:
            moved.created = now_iso()
        moved.save()

        rel = target.relative_to(vault)
        console.print(f"[green]->[/green] {rel}  [dim](type={new_type})[/dim]")


def _show(note: Note, idx: int, total: int) -> None:
    head = f"[{idx}/{total}] {note.id}  {note.title}"
    body = (note.body or "").strip()
    preview = body if len(body) <= 600 else body[:600] + "\n..."
    console.print(Panel(Markdown(preview or "_(empty)_"), title=head, border_style="cyan"))


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
