"""Vault discovery and folder layout."""

from __future__ import annotations

import os
from pathlib import Path

from learn_cli.config import VAULT_CONFIG_DIRNAME, Config

PARA_DIRS = ("projects", "areas", "resources", "archive")
ZK_DIRS = ("inbox", "zettel", "daily")
TEMPLATE_DIR = "templates"

ALL_DIRS = (*ZK_DIRS, *PARA_DIRS, TEMPLATE_DIR)


def find_vault(start: Path | None = None) -> Path | None:
    """Walk upward from `start` (default: cwd) looking for a `.learn/` marker."""
    env = os.environ.get("LEARN_CLI_VAULT")
    if env:
        candidate = Path(env).expanduser().resolve()
        if (candidate / VAULT_CONFIG_DIRNAME).is_dir():
            return candidate
    cur = (start or Path.cwd()).resolve()
    for path in (cur, *cur.parents):
        if (path / VAULT_CONFIG_DIRNAME).is_dir():
            return path
    return None


def require_vault(cfg: Config | None = None) -> Path:
    """Return the active vault path or raise a helpful error."""
    if cfg and cfg.vault_path and (cfg.vault_path / VAULT_CONFIG_DIRNAME).is_dir():
        return cfg.vault_path
    found = find_vault()
    if found:
        return found
    if cfg and cfg.vault_path:
        return cfg.vault_path
    raise VaultNotFound(
        "Could not locate a learn-cli vault. Run `learn init <path>` first, "
        "or set [vault].path in your user config / LEARN_CLI_VAULT env var."
    )


def ensure_layout(vault: Path) -> None:
    """Create the standard directory layout inside an existing vault path."""
    vault.mkdir(parents=True, exist_ok=True)
    (vault / VAULT_CONFIG_DIRNAME).mkdir(exist_ok=True)
    for d in ALL_DIRS:
        (vault / d).mkdir(exist_ok=True)
    for d in ALL_DIRS:
        keep = vault / d / ".gitkeep"
        if not any((vault / d).iterdir()):
            keep.touch()


class VaultNotFound(RuntimeError):
    pass
