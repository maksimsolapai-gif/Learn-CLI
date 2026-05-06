"""Bundled note templates."""

from importlib import resources


def _read(name: str) -> str:
    return (resources.files(__package__) / f"{name}.md").read_text(encoding="utf-8")


def render(name: str, **vars: str) -> str:
    """Load a template by stem (e.g. 'zettel') and substitute {{vars}}."""
    text = _read(name)
    for key, value in vars.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def template_text(name: str) -> str:
    """Return the raw template text (with placeholders intact)."""
    return _read(name)


def template_path(name: str):
    """Backwards-compatible accessor — returns a Traversable for the template file."""
    return resources.files(__package__) / f"{name}.md"
