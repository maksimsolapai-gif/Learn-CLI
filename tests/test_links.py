from pathlib import Path

import pytest

from learn_cli.links import (
    add_link,
    backlinks_index,
    collect_links,
    extract_wikilink_ids,
    link_pair,
)
from learn_cli.notes import Note, now_iso
from learn_cli.vault import ensure_layout


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    ensure_layout(tmp_path)
    return tmp_path


def make_note(vault: Path, nid: str, body: str = "", links: list[str] | None = None) -> Note:
    path = vault / "zettel" / f"{nid}.md"
    note = Note(
        path=path, id=nid, title=f"n{nid}", type="zettel",
        status="fleeting", created=now_iso(), body=body, links=links or [],
    )
    note.save()
    return Note.load(path)


def test_extract_wikilink_ids():
    text = "see [[202605061200]] and [[202605061300|alias]] and [[not-id]]"
    out = extract_wikilink_ids(text)
    assert out == ["202605061200", "202605061300"]


def test_extract_wikilink_dedup():
    text = "[[202605061200]] [[202605061200]] [[202605061201]]"
    assert extract_wikilink_ids(text) == ["202605061200", "202605061201"]


def test_collect_links_merges_frontmatter_and_body():
    note = Note(
        path=Path("x.md"), id="100000000000", title="t", type="zettel",
        status="fleeting", created="", links=["202605061200"],
        body="and [[202605061300]]",
    )
    assert collect_links(note) == ["202605061200", "202605061300"]


def test_add_link_idempotent():
    note = Note(
        path=Path("x.md"), id="100000000000", title="t", type="zettel",
        status="fleeting", created="",
    )
    assert add_link(note, "202605061200") is True
    assert add_link(note, "202605061200") is False
    assert add_link(note, "100000000000") is False
    assert note.links == ["202605061200"]


def test_link_pair_bidirectional(vault: Path):
    a = make_note(vault, "202605061200", body="hello")
    b = make_note(vault, "202605061300", body="world")

    a2, b2 = link_pair(vault, a.id, b.id)
    assert b.id in a2.links
    assert a.id in b2.links

    a3, b3 = link_pair(vault, a.id, b.id)
    assert a3.links.count(b.id) == 1
    assert b3.links.count(a.id) == 1


def test_backlinks_index(vault: Path):
    a = make_note(vault, "202605061200", body="-> [[202605061300]]")
    b = make_note(vault, "202605061300", body="orphan")

    idx = backlinks_index(vault)
    assert b.id in idx
    assert a.id in idx[b.id]
