"""`learn sync` — git add + commit (+ push if remote)."""

from __future__ import annotations

from datetime import datetime

import typer
from rich.console import Console

from learn_cli import git_ops
from learn_cli.config import Config
from learn_cli.vault import require_vault

console = Console()


def sync_command(
    message: str = typer.Option(
        "", "--message", "-m", help="Commit message (default: timestamped notes update)."
    ),
    no_push: bool = typer.Option(False, "--no-push", help="Do not push even if a remote is set."),
) -> None:
    """Stage, commit, and (optionally) push all changes in the vault."""
    cfg = Config.load()
    vault = require_vault(cfg)

    if not git_ops.have_git():
        console.print(
            "[red]git not found in PATH.[/red] Install git from https://git-scm.com/."
        )
        raise typer.Exit(code=1)

    if not git_ops.is_repo(vault):
        console.print("[yellow]Vault is not a git repo. Initializing...[/yellow]")
        git_ops.init_repo(vault)

    if not git_ops.has_changes(vault):
        console.print("[green]Nothing to commit — working tree clean.[/green]")
    else:
        git_ops.add_all(vault)
        msg = message or f"notes: update {datetime.now():%Y-%m-%d %H:%M}"
        res = git_ops.commit(vault, msg)
        if res.returncode != 0:
            console.print(f"[red]git commit failed[/red]\n{res.stderr or res.stdout}")
            raise typer.Exit(code=res.returncode)
        console.print(f"[green]Committed:[/green] {msg}")

    if no_push:
        return
    if git_ops.has_remote(vault, cfg.git_remote):
        res = git_ops.push(vault, cfg.git_remote)
        if res.returncode != 0:
            console.print(f"[yellow]Push failed:[/yellow] {res.stderr or res.stdout}")
        else:
            console.print(f"[green]Pushed to {cfg.git_remote}.[/green]")
    else:
        console.print(
            f"[dim]No remote {cfg.git_remote!r} configured. "
            f"Run `git -C {vault} remote add {cfg.git_remote} <url>` to enable push.[/dim]"
        )
