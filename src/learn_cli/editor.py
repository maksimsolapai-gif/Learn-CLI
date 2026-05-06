"""Open files in the user's configured editor."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path


def open_in_editor(command: str, path: Path) -> int:
    """Run `<command> <path>` and return the exit code (0 on success)."""
    if not command:
        command = "notepad" if os.name == "nt" else "vi"
    if os.name == "nt":
        parts = _split_windows(command)
    else:
        parts = shlex.split(command)
    parts.append(str(path))
    try:
        proc = subprocess.run(parts, check=False)
        return proc.returncode
    except FileNotFoundError:
        fallback = "notepad" if os.name == "nt" else "vi"
        proc = subprocess.run([fallback, str(path)], check=False)
        return proc.returncode


def _split_windows(command: str) -> list[str]:
    """Naive split that keeps quoted paths intact on Windows."""
    out: list[str] = []
    buf: list[str] = []
    in_quote = False
    for ch in command:
        if ch == '"':
            in_quote = not in_quote
            continue
        if ch == " " and not in_quote:
            if buf:
                out.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out
