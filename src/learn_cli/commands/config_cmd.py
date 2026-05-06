"""`learn config` — read/write user-level configuration."""

from __future__ import annotations

import typer
from rich.console import Console

from learn_cli.config import (
    Config,
    USER_CONFIG_PATH,
    get_value,
    set_value,
    write_user_config,
)

app = typer.Typer(help="Read and write learn-cli configuration.")
console = Console()


@app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Dotted key (e.g. editor.command, vault.path)."),
) -> None:
    """Print the current value for KEY."""
    cfg = Config.load()
    val = get_value(cfg, key)
    console.print(val)


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Dotted key (e.g. editor.command, vault.path)."),
    value: str = typer.Argument(..., help="Value to write."),
) -> None:
    """Write KEY = VALUE into the user config (~/.config/learn-cli/config.toml)."""
    cfg = Config.load()
    try:
        set_value(cfg, key, value)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)
    path = write_user_config(cfg)
    console.print(f"[green]Set[/green] {key} = {value}  [dim]({path})[/dim]")


@app.command("path")
def config_path() -> None:
    """Print the path to the user-level config file."""
    console.print(str(USER_CONFIG_PATH))


@app.command("show")
def config_show() -> None:
    """Print the resolved config (user + vault + env)."""
    cfg = Config.load()
    data = cfg.to_dict()
    for section, body in data.items():
        console.print(f"[bold]{section}[/bold]")
        for k, v in body.items():
            console.print(f"  {k} = {v}")
