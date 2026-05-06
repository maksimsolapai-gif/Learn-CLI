"""Zettel ID generation and slug helpers."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime

ID_RE = re.compile(r"^\d{12}$")
ID_FROM_FILENAME_RE = re.compile(r"^(\d{12})(?:[-_].*)?$")


def new_id(now: datetime | None = None) -> str:
    """Return a 12-digit timestamp ID: YYYYMMDDHHMM."""
    now = now or datetime.now()
    return now.strftime("%Y%m%d%H%M")


def is_id(value: str) -> bool:
    return bool(ID_RE.match(value))


def id_from_filename(name: str) -> str | None:
    """Extract zettel id from a file path or stem (e.g. '202605061430-foo.md')."""
    stem = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if stem.endswith(".md"):
        stem = stem[:-3]
    m = ID_FROM_FILENAME_RE.match(stem)
    return m.group(1) if m else None


def slugify(title: str, max_len: int = 60) -> str:
    """Conservative slug suitable for filenames on all OSes."""
    if not title:
        return ""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    has_letters = bool(re.search(r"[A-Za-z0-9]", ascii_only))
    base = ascii_only if has_letters else title
    base = base.lower().strip()
    base = re.sub(r"[^\w\s-]", "", base, flags=re.UNICODE)
    base = re.sub(r"[\s_]+", "-", base, flags=re.UNICODE)
    base = re.sub(r"-+", "-", base).strip("-")
    if len(base) > max_len:
        base = base[:max_len].rstrip("-")
    return base
