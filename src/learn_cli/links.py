"""Wikilink parsing and bidirectional link maintenance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from learn_cli.ids import ID_RE
from learn_cli.notes import Note, find_note_by_id, iter_notes

WIKILINK_RE = re.compile(r"\[\[([^\[\]\|]+?)(?:\|[^\[\]]+)?\]\]")


def extract_wikilink_ids(text: str) -> list[str]:
    """Return unique zettel IDs referenced by [[id]] or [[id|alias]] in text."""
    seen: list[str] = []
    for m in WIKILINK_RE.finditer(text or ""):
        target = m.group(1).strip()
        if ID_RE.match(target) and target not in seen:
            seen.append(target)
    return seen


def collect_links(note: Note) -> list[str]:
    """Union of frontmatter `links` and inline [[id]] references."""
    out: list[str] = []
    for src in (note.links, extract_wikilink_ids(note.body)):
        for x in src:
            if x and x not in out:
                out.append(x)
    return out


def add_link(note: Note, target_id: str) -> bool:
    """Add target_id to note.links if missing. Returns True if changed."""
    if not target_id or target_id == note.id:
        return False
    if target_id in note.links:
        return False
    note.links.append(target_id)
    return True


def link_pair(vault: Path, id_a: str, id_b: str) -> tuple[Note, Note]:
    """Add bidirectional link between two notes. Saves both and returns them."""
    if id_a == id_b:
        raise ValueError("Cannot link a note to itself.")
    a = find_note_by_id(vault, id_a)
    b = find_note_by_id(vault, id_b)
    if not a:
        raise FileNotFoundError(f"Note not found: {id_a}")
    if not b:
        raise FileNotFoundError(f"Note not found: {id_b}")
    changed_a = add_link(a, b.id)
    changed_b = add_link(b, a.id)
    if changed_a:
        a.save()
    if changed_b:
        b.save()
    return a, b


def backlinks_index(vault: Path, note_ids: Iterable[str] | None = None) -> dict[str, list[str]]:
    """Map of target_id -> [source_id, ...] across the vault."""
    targets = set(note_ids) if note_ids else None
    index: dict[str, list[str]] = {}
    for p in iter_notes(vault):
        note = Note.load(p)
        for ref in collect_links(note):
            if targets is not None and ref not in targets:
                continue
            index.setdefault(ref, []).append(note.id)
    return index
