"""`learn init` — bootstrap a new vault."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from learn_cli import git_ops
from learn_cli.config import (
    Config,
    USER_CONFIG_PATH,
    write_user_config,
    write_vault_config,
)
from learn_cli.templates import template_text
from learn_cli.vault import ensure_layout

console = Console()


def init_command(
    path: Path = typer.Argument(..., help="Vault path. Will be created if missing."),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git repository setup."),
    set_default: bool = typer.Option(
        True, "--set-default/--no-set-default",
        help="Save this vault as the default in the user config."
    ),
) -> None:
    """Initialize a knowledge vault at PATH."""
    vault = path.expanduser().resolve()
    vault.mkdir(parents=True, exist_ok=True)
    ensure_layout(vault)

    _write_template(vault, "zettel")
    _write_template(vault, "daily")
    _write_template(vault, "inbox")

    cfg = Config.load(vault)
    cfg.vault_path = vault
    write_vault_config(vault, cfg)

    if set_default:
        write_user_config(cfg)
        console.print(f"[dim]User config:[/dim] {USER_CONFIG_PATH}")

    readme = vault / "README.md"
    if not readme.exists():
        readme.write_text(_vault_readme(vault.name), encoding="utf-8")

    if not no_git:
        if git_ops.have_git():
            if not git_ops.is_repo(vault):
                git_ops.init_repo(vault)
                git_ops.add_all(vault)
                if git_ops.has_changes(vault):
                    git_ops.commit(vault, "chore: initialize learn-cli vault")
                console.print("[green]Initialized git repository.[/green]")
            else:
                console.print("[yellow]Existing git repository detected — skipping init.[/yellow]")
        else:
            console.print(
                "[yellow]git not found in PATH — skipping repo init. "
                "Install git and run `git init` inside the vault later.[/yellow]"
            )

    console.print(f"[bold green]Vault ready at[/bold green] {vault}")
    console.print(
        "Next steps: [cyan]learn capture \"first idea\"[/cyan], "
        "[cyan]learn new \"topic\"[/cyan], or [cyan]learn daily[/cyan]."
    )


def _write_template(vault: Path, name: str) -> None:
    target = vault / "templates" / f"{name}.md"
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template_text(name), encoding="utf-8")


def _vault_readme(name: str) -> str:
    return (
        f"# {name}\n\n"
        "Personal knowledge vault managed by `learn-cli`.\n\n"
        "Methods: Zettelkasten + CODE + PARA.\n\n"
        "## Layout\n"
        "- `inbox/` — quick captures (CODE: Capture)\n"
        "- `zettel/` — atomic permanent notes (Zettelkasten)\n"
        "- `daily/` — daily learning notes\n"
        "- `projects/`, `areas/`, `resources/`, `archive/` — PARA\n"
        "- `templates/` — note templates\n\n"
        "Run `learn --help` for available commands.\n"
    )
