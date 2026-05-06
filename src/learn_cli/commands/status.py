"""`learn status` — vault statistics + git status."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from learn_cli import git_ops
from learn_cli.config import Config
from learn_cli.notes import Note, iter_notes
from learn_cli.vault import require_vault

console = Console()


def status_command() -> None:
    """Show counts of notes by type and a brief git status."""
    vault = require_vault(Config.load())

    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total = 0
    for path in iter_notes(vault):
        n = Note.load(path)
        by_type[n.type] = by_type.get(n.type, 0) + 1
        by_status[n.status] = by_status.get(n.status, 0) + 1
        total += 1

    types_table = Table(title=f"Notes ({total})")
    types_table.add_column("Type")
    types_table.add_column("Count", justify="right")
    for k in sorted(by_type):
        types_table.add_row(k, str(by_type[k]))
    console.print(types_table)

    status_table = Table(title="By status")
    status_table.add_column("Status")
    status_table.add_column("Count", justify="right")
    for k in sorted(by_status):
        status_table.add_row(k, str(by_status[k]))
    console.print(status_table)

    console.print(f"[bold]Vault:[/bold] {vault}")
    if git_ops.have_git() and git_ops.is_repo(vault):
        porcelain = git_ops.status_porcelain(vault)
        if porcelain:
            console.print("[yellow]Uncommitted changes:[/yellow]")
            console.print(porcelain)
        else:
            console.print("[green]Working tree clean.[/green]")
    else:
        console.print("[dim]git not available or vault not a repo.[/dim]")
