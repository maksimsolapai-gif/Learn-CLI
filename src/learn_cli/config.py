"""Configuration: user-level (~/.config/learn-cli/config.toml) merged with vault-level."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found]


USER_CONFIG_DIR = Path(
    os.environ.get("LEARN_CLI_CONFIG_HOME")
    or (Path(os.environ["APPDATA"]) / "learn-cli" if os.name == "nt" and os.environ.get("APPDATA")
        else Path.home() / ".config" / "learn-cli")
)
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.toml"

VAULT_CONFIG_DIRNAME = ".learn"
VAULT_CONFIG_FILENAME = "config.toml"


@dataclass
class Config:
    vault_path: Path | None = None
    editor_command: str = field(default_factory=lambda: _default_editor())
    git_auto_commit: bool = False
    git_remote: str = "origin"
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, vault: Path | None = None) -> "Config":
        cfg = cls()
        cfg._merge(_load_toml(USER_CONFIG_PATH))
        if vault is not None:
            cfg._merge(_load_toml(vault / VAULT_CONFIG_DIRNAME / VAULT_CONFIG_FILENAME))
            cfg.vault_path = vault
        env_vault = os.environ.get("LEARN_CLI_VAULT")
        if env_vault:
            cfg.vault_path = Path(env_vault).expanduser().resolve()
        env_editor = os.environ.get("LEARN_CLI_EDITOR") or os.environ.get("EDITOR")
        if env_editor:
            cfg.editor_command = env_editor
        return cfg

    def _merge(self, data: dict[str, Any]) -> None:
        if not data:
            return
        vault = data.get("vault", {})
        if isinstance(vault, dict):
            p = vault.get("path")
            if p:
                self.vault_path = Path(str(p)).expanduser().resolve()
        editor = data.get("editor", {})
        if isinstance(editor, dict):
            cmd = editor.get("command")
            if cmd:
                self.editor_command = str(cmd)
        git = data.get("git", {})
        if isinstance(git, dict):
            if "auto_commit" in git:
                self.git_auto_commit = bool(git["auto_commit"])
            if "remote" in git:
                self.git_remote = str(git["remote"])
        for k, v in data.items():
            if k not in {"vault", "editor", "git"}:
                self.extras[k] = v

    def to_dict(self) -> dict[str, Any]:
        return {
            "vault": {"path": str(self.vault_path) if self.vault_path else ""},
            "editor": {"command": self.editor_command},
            "git": {"auto_commit": self.git_auto_commit, "remote": self.git_remote},
        }


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _default_editor() -> str:
    if os.name == "nt":
        return "notepad"
    return os.environ.get("EDITOR") or "vi"


def write_user_config(cfg: Config) -> Path:
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    USER_CONFIG_PATH.write_text(_render_toml(cfg.to_dict()), encoding="utf-8")
    return USER_CONFIG_PATH


def write_vault_config(vault: Path, cfg: Config) -> Path:
    target_dir = vault / VAULT_CONFIG_DIRNAME
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / VAULT_CONFIG_FILENAME
    path.write_text(_render_toml(cfg.to_dict()), encoding="utf-8")
    return path


def _render_toml(data: dict[str, Any]) -> str:
    """Minimal TOML renderer (we only need shallow tables of strings/bools)."""
    lines: list[str] = []
    for section, body in data.items():
        if not isinstance(body, dict):
            continue
        lines.append(f"[{section}]")
        for k, v in body.items():
            lines.append(f"{k} = {_format_value(v)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _format_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def get_value(cfg: Config, key: str) -> str:
    """Read a dotted key like 'editor.command'."""
    data = cfg.to_dict()
    parts = key.split(".")
    cur: Any = data
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return ""
        cur = cur[p]
    return "" if cur is None else str(cur)


def set_value(cfg: Config, key: str, value: str) -> None:
    """Set a dotted key like 'editor.command' on the Config object."""
    if key == "vault.path":
        cfg.vault_path = Path(value).expanduser().resolve() if value else None
    elif key == "editor.command":
        cfg.editor_command = value
    elif key == "git.auto_commit":
        cfg.git_auto_commit = value.lower() in {"1", "true", "yes", "on"}
    elif key == "git.remote":
        cfg.git_remote = value
    else:
        raise KeyError(f"Unknown config key: {key}")
