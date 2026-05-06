from pathlib import Path

import pytest

from learn_cli.notes import Note, find_note_by_id, iter_notes, now_iso
from learn_cli.vault import ensure_layout


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    ensure_layout(tmp_path)
    return tmp_path


def test_save_and_load_roundtrip(vault: Path):
    path = vault / "zettel" / "202605061430-test.md"
    note = Note(
        path=path,
        id="202605061430",
        title="Test note",
        type="zettel",
        status="fleeting",
        created=now_iso(),
        tags=["a", "b"],
        links=["202605061200"],
        body="Body text\n\nMore body.\n",
    )
    note.save()
    assert path.exists()

    reloaded = Note.load(path)
    assert reloaded.id == "202605061430"
    assert reloaded.title == "Test note"
    assert reloaded.type == "zettel"
    assert reloaded.tags == ["a", "b"]
    assert reloaded.links == ["202605061200"]
    assert "Body text" in reloaded.body


def test_iter_and_find(vault: Path):
    path = vault / "zettel" / "202605061500-x.md"
    Note(
        path=path, id="202605061500", title="x", type="zettel",
        status="fleeting", created=now_iso(), body="hi",
    ).save()

    paths = list(iter_notes(vault))
    assert any(p.name == "202605061500-x.md" for p in paths)

    found = find_note_by_id(vault, "202605061500")
    assert found is not None
    assert found.title == "x"

    assert find_note_by_id(vault, "999999999999") is None


def test_extras_preserved(vault: Path):
    path = vault / "zettel" / "202605061600-extras.md"
    note = Note(
        path=path, id="202605061600", title="e", type="zettel",
        status="fleeting", created=now_iso(),
        extras={"custom": "value", "rating": 5},
    )
    note.save()

    reloaded = Note.load(path)
    assert reloaded.extras.get("custom") == "value"
    assert reloaded.extras.get("rating") == 5
