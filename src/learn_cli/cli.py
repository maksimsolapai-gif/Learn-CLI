"""Typer CLI entry point."""

from __future__ import annotations

import typer
from rich.console import Console

from learn_cli import __version__
from learn_cli.commands.capture import capture_command
from learn_cli.commands.config_cmd import app as config_app
from learn_cli.commands.daily import daily_command
from learn_cli.commands.distill import distill_command
from learn_cli.commands.express import express_command
from learn_cli.commands.init import init_command
from learn_cli.commands.link import link_command
from learn_cli.commands.new import new_command
from learn_cli.commands.open import open_command
from learn_cli.commands.para import app as para_app, archive_command
from learn_cli.commands.process import process_command
from learn_cli.commands.search import search_command
from learn_cli.commands.status import status_command
from learn_cli.commands.sync import sync_command
from learn_cli.commands.tags import tags_command
from learn_cli.vault import VaultNotFound

console = Console()

app = typer.Typer(
    help=(
        "learn — git-based PKM CLI. Combines Zettelkasten, CODE "
        "(Capture/Organize/Distill/Express) and PARA in plain Markdown."
    ),
    add_completion=False,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"learn-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-V", help="Show version and exit.",
        callback=_version_callback, is_eager=True,
    ),
) -> None:
    """Top-level options."""


app.command("init", help="Initialize a knowledge vault at PATH.")(init_command)
app.command("new", help="Create a new permanent zettel.")(new_command)
app.command("capture", help="Quick fleeting note into the inbox.")(capture_command)
app.command("process", help="Interactively triage notes from the inbox.")(process_command)
app.command("distill", help="Promote a note's status (CODE: Distill).")(distill_command)
app.command("express", help="List notes ready to be used (CODE: Express).")(express_command)
app.command("link", help="Bidirectional link between two zettels.")(link_command)
app.command("open", help="Open a note by id or title query.")(open_command)
app.command("daily", help="Open or create today's daily note.")(daily_command)
app.command("search", help="Full-text search across the vault.")(search_command)
app.command("tags", help="List tags with counts.")(tags_command)
app.command("status", help="Vault stats + git status.")(status_command)
app.command("sync", help="git add + commit + push (if remote).")(sync_command)
app.command("archive", help="Archive a note (PARA shortcut).")(archive_command)

app.add_typer(para_app, name="para")
app.add_typer(config_app, name="config")


def main() -> None:
    try:
        app()
    except VaultNotFound as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
