from datetime import datetime

from learn_cli.ids import id_from_filename, is_id, new_id, slugify


def test_new_id_format():
    nid = new_id(datetime(2026, 5, 6, 14, 30))
    assert nid == "202605061430"
    assert is_id(nid)


def test_id_from_filename_variants():
    assert id_from_filename("202605061430-foo-bar.md") == "202605061430"
    assert id_from_filename("202605061430.md") == "202605061430"
    assert id_from_filename("path/to/202605061430-foo.md") == "202605061430"
    assert id_from_filename("not-an-id.md") is None


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  multiple   spaces  ") == "multiple-spaces"
    assert slugify("") == ""


def test_slugify_cyrillic_keeps_letters():
    out = slugify("Атомарность заметок")
    assert out
    assert " " not in out
    assert "-" in out
