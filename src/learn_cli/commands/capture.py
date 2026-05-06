"""`learn capture` — quick fleeting note into the inbox."""

from __future__ import annotations

import sys

import typer
from rich.console import Console

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.ids import new_id, slugify
from learn_cli.notes import filename_for, now_iso
from learn_cli.templates import render
from learn_cli.vault import require_vault

console = Console()


def capture_command(
    text: list[str] = typer.Argument(
        None, help="The note text. If omitted, reads stdin or opens the editor."
    ),
    title: str = typer.Option("", "--title", "-T", help="Optional title for the inbox note."),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open in editor after capture."),
) -> None:
    """Capture a quick fleeting thought into `inbox/`."""
    cfg = Config.load()
    vault = require_vault(cfg)

    body = " ".join(text) if text else ""
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read().strip()

    if not body and not title:
        edit = True

    nid = new_id()
    derived_title = title or _first_sentence(body) or "untitled"
    fname = filename_for(nid, derived_title)
    path = vault / "inbox" / fname

    rendered = render(
        "inbox", id=nid, title=derived_title, created=now_iso(), body=body or "",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")

    console.print(f"[green]Captured[/green] {path.relative_to(vault)}")
    if edit:
        open_in_editor(cfg.editor_command, path)


def _first_sentence(text: str, limit: int = 60) -> str:
    if not text:
        return ""
    head = text.strip().splitlines()[0]
    head = head.split(". ")[0].strip()
    head = head[:limit].rstrip()
    return slugify(head) and head
