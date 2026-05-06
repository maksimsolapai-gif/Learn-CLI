"""`learn search` — full-text search across the vault."""

from __future__ import annotations

import shutil
import subprocess

import typer
from rich.console import Console
from rich.table import Table

from learn_cli.config import Config
from learn_cli.notes import Note, iter_notes
from learn_cli.vault import require_vault

console = Console()


def search_command(
    query: str = typer.Argument(..., help="Search query (case-insensitive substring or regex)."),
    use_rg: bool = typer.Option(
        True, "--rg/--no-rg",
        help="Use ripgrep when available for fast searching (default).",
    ),
) -> None:
    """Search note titles and bodies."""
    vault = require_vault(Config.load())

    if use_rg and shutil.which("rg"):
        proc = subprocess.run(
            ["rg", "-n", "-i", "--no-heading", "-S", query, "--glob", "*.md", "--", str(vault)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        out = proc.stdout.strip()
        if out:
            console.print(out)
        else:
            console.print("[yellow]No matches.[/yellow]")
        return

    needle = query.lower()
    rows: list[tuple[Note, list[str]]] = []
    for path in iter_notes(vault):
        n = Note.load(path)
        hits: list[str] = []
        if needle in n.title.lower():
            hits.append(f"title: {n.title}")
        for line in (n.body or "").splitlines():
            if needle in line.lower():
                hits.append(line.strip()[:160])
                if len(hits) >= 3:
                    break
        if hits:
            rows.append((n, hits))

    if not rows:
        console.print("[yellow]No matches.[/yellow]")
        return

    table = Table(title=f"Search: {query!r}  ({len(rows)} notes)")
    table.add_column("ID")
    table.add_column("Type", style="dim")
    table.add_column("Title")
    table.add_column("Hits")
    for n, hits in rows:
        table.add_row(n.id, n.type, n.title, "\n".join(hits))
    console.print(table)
