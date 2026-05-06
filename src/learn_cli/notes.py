"""Note CRUD: read/write Markdown files with YAML frontmatter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import frontmatter

from learn_cli.ids import id_from_filename, slugify

NOTE_TYPES = ("zettel", "inbox", "daily", "project", "area", "resource", "archive")
NOTE_STATUSES = ("fleeting", "literature", "permanent")

TYPE_TO_DIR = {
    "zettel": "zettel",
    "inbox": "inbox",
    "daily": "daily",
    "project": "projects",
    "area": "areas",
    "resource": "resources",
    "archive": "archive",
}


@dataclass
class Note:
    path: Path
    id: str
    title: str
    type: str
    status: str
    created: str
    tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    source: str = ""
    body: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Note":
        post = frontmatter.load(path)
        meta = dict(post.metadata or {})
        nid = str(meta.get("id") or id_from_filename(path.name) or "")
        title = str(meta.get("title") or path.stem)
        ntype = str(meta.get("type") or _infer_type_from_path(path))
        status = str(meta.get("status") or "fleeting")
        created = str(meta.get("created") or "")
        tags = _as_str_list(meta.get("tags"))
        links = _as_str_list(meta.get("links"))
        source = str(meta.get("source") or "")
        known = {"id", "title", "type", "status", "created", "tags", "links", "source"}
        extras = {k: v for k, v in meta.items() if k not in known}
        return cls(
            path=path, id=nid, title=title, type=ntype, status=status, created=created,
            tags=tags, links=links, source=source, body=post.content, extras=extras,
        )

    def to_post(self) -> frontmatter.Post:
        meta: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "created": self.created,
            "tags": list(self.tags),
            "links": list(self.links),
        }
        if self.source:
            meta["source"] = self.source
        meta.update(self.extras)
        post = frontmatter.Post(self.body or "", **meta)
        return post

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = frontmatter.dumps(self.to_post(), sort_keys=False)
        if not text.endswith("\n"):
            text += "\n"
        self.path.write_text(text, encoding="utf-8")


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, Iterable):
        items = list(value)
    else:
        items = [value]
    return [str(x) for x in items if str(x).strip()]


def _infer_type_from_path(path: Path) -> str:
    parent = path.parent.name
    mapping = {
        "zettel": "zettel",
        "inbox": "inbox",
        "daily": "daily",
        "projects": "project",
        "areas": "area",
        "resources": "resource",
        "archive": "archive",
    }
    return mapping.get(parent, "zettel")


def filename_for(note_id: str, title: str, ext: str = ".md") -> str:
    slug = slugify(title)
    return f"{note_id}-{slug}{ext}" if slug else f"{note_id}{ext}"


def iter_notes(vault: Path, subdirs: Iterable[str] | None = None) -> Iterable[Path]:
    """Yield .md files inside known content dirs (skip templates and dotfiles)."""
    from learn_cli.vault import ALL_DIRS

    targets = list(subdirs) if subdirs else [d for d in ALL_DIRS if d != "templates"]
    for d in targets:
        base = vault / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if any(part.startswith(".") for part in p.relative_to(vault).parts):
                continue
            yield p


def find_note_by_id(vault: Path, note_id: str) -> Note | None:
    for p in iter_notes(vault):
        if id_from_filename(p.name) == note_id:
            return Note.load(p)
    return None


def find_notes_by_query(vault: Path, query: str, limit: int = 50) -> list[Note]:
    """Quick title/id substring match for `learn open <query>`."""
    q = query.lower()
    results: list[Note] = []
    for p in iter_notes(vault):
        if q in p.name.lower():
            results.append(Note.load(p))
            if len(results) >= limit:
                break
    return results


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
