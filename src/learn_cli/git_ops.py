"""Thin wrapper over the git CLI via subprocess."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitNotInstalled(RuntimeError):
    pass


@dataclass
class GitResult:
    returncode: int
    stdout: str
    stderr: str


def have_git() -> bool:
    return shutil.which("git") is not None


def run(cwd: Path, *args: str, check: bool = False) -> GitResult:
    if not have_git():
        raise GitNotInstalled(
            "git executable was not found in PATH. Install git from https://git-scm.com/."
        )
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, proc.args, proc.stdout, proc.stderr)
    return GitResult(proc.returncode, proc.stdout.strip(), proc.stderr.strip())


def is_repo(cwd: Path) -> bool:
    if not have_git():
        return False
    res = run(cwd, "rev-parse", "--is-inside-work-tree")
    return res.returncode == 0 and res.stdout.lower().startswith("true")


def init_repo(cwd: Path, branch: str = "main") -> GitResult:
    return run(cwd, "init", "-b", branch)


def add_all(cwd: Path) -> GitResult:
    return run(cwd, "add", "-A")


def commit(cwd: Path, message: str) -> GitResult:
    return run(cwd, "commit", "-m", message)


def status_porcelain(cwd: Path) -> str:
    return run(cwd, "status", "--porcelain").stdout


def has_changes(cwd: Path) -> bool:
    return bool(status_porcelain(cwd).strip())


def has_remote(cwd: Path, name: str = "origin") -> bool:
    res = run(cwd, "remote")
    return name in res.stdout.split()


def push(cwd: Path, remote: str = "origin") -> GitResult:
    return run(cwd, "push", remote, "HEAD")


def pull(cwd: Path, remote: str = "origin") -> GitResult:
    return run(cwd, "pull", remote, "--ff-only")
