"""`learn daily` — open today's daily learning note."""

from __future__ import annotations

from datetime import datetime

import typer
from rich.console import Console

from learn_cli.config import Config
from learn_cli.editor import open_in_editor
from learn_cli.ids import new_id
from learn_cli.notes import now_iso
from learn_cli.templates import render
from learn_cli.vault import require_vault

console = Console()


def daily_command(
    no_open: bool = typer.Option(False, "--no-open", help="Just create the note, don't open it."),
) -> None:
    """Create or open today's daily note in `daily/YYYY-MM-DD.md`."""
    cfg = Config.load()
    vault = require_vault(cfg)

    today = datetime.now().strftime("%Y-%m-%d")
    path = vault / "daily" / f"{today}.md"
    if not path.exists():
        body = render("daily", id=new_id(), date=today, created=now_iso())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        console.print(f"[green]Created[/green] {path.relative_to(vault)}")
    else:
        console.print(f"[dim]Opening[/dim] {path.relative_to(vault)}")

    if not no_open:
        open_in_editor(cfg.editor_command, path)
