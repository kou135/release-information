"""Tests for ``release_information.files.delete`` (Python API direct).

These tests exercise the underlying ``delete`` function without going through
the CLI subprocess layer. CLI-level smoke is covered separately in
``tests/test_cli.py``.

All filesystem activity is confined to ``tmp_path``; we never touch the real
repository under test.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from release_information.files.delete import delete

_DOCS_SUBDIR = ("docs", "release-information")


def _make_docs_dir(repo_root: Path) -> Path:
    docs = repo_root.joinpath(*_DOCS_SUBDIR)
    docs.mkdir(parents=True, exist_ok=True)
    return docs


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_delete_removes_both_md_and_html(tmp_path: Path) -> None:
    """Both files present: both are unlinked, returned in [md, html] order."""
    docs = _make_docs_dir(tmp_path)
    md = docs / "v1.0.0.md"
    html = docs / "v1.0.0.html"
    md.write_text("# Doc\n", encoding="utf-8")
    html.write_text("<html></html>", encoding="utf-8")

    removed = delete(tmp_path, "v1.0.0")

    assert removed == [md, html]
    assert not md.exists()
    assert not html.exists()


def test_delete_removes_only_md_when_html_missing(tmp_path: Path) -> None:
    """Only the .md exists: just the .md is removed."""
    docs = _make_docs_dir(tmp_path)
    md = docs / "v1.0.0.md"
    md.write_text("# Doc\n", encoding="utf-8")

    removed = delete(tmp_path, "v1.0.0")

    assert removed == [md]
    assert not md.exists()


def test_delete_removes_only_html_when_md_missing(tmp_path: Path) -> None:
    """Only the .html exists: just the .html is removed."""
    docs = _make_docs_dir(tmp_path)
    html = docs / "v1.0.0.html"
    html.write_text("<html></html>", encoding="utf-8")

    removed = delete(tmp_path, "v1.0.0")

    assert removed == [html]
    assert not html.exists()


def test_delete_accepts_name_with_md_extension(tmp_path: Path) -> None:
    """``v1.0.0.md`` and ``v1.0.0`` must behave identically."""
    docs = _make_docs_dir(tmp_path)
    md = docs / "v1.0.0.md"
    html = docs / "v1.0.0.html"
    md.write_text("# Doc\n", encoding="utf-8")
    html.write_text("<html></html>", encoding="utf-8")

    removed = delete(tmp_path, "v1.0.0.md")

    assert removed == [md, html]
    assert not md.exists()
    assert not html.exists()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_delete_raises_when_neither_exists(tmp_path: Path) -> None:
    """Neither file present: FileNotFoundError, nothing else touched."""
    _make_docs_dir(tmp_path)

    with pytest.raises(FileNotFoundError):
        delete(tmp_path, "v1.0.0")


def test_delete_raises_when_docs_dir_does_not_exist(tmp_path: Path) -> None:
    """The docs directory itself is absent: still FileNotFoundError (idempotent)."""
    # No _make_docs_dir(); docs/release-information/ is missing entirely.
    with pytest.raises(FileNotFoundError):
        delete(tmp_path, "v1.0.0")


# ---------------------------------------------------------------------------
# Safety: path traversal, separators, absolute paths
# ---------------------------------------------------------------------------


def test_delete_rejects_path_traversal_dotdot(tmp_path: Path) -> None:
    """``../etc/passwd`` style names must be rejected before any unlink."""
    _make_docs_dir(tmp_path)

    with pytest.raises(ValueError, match="path separator|'..'|absolute"):
        delete(tmp_path, "../etc/passwd")


def test_delete_rejects_subdirectory_in_name(tmp_path: Path) -> None:
    """A name containing a path separator must be rejected."""
    _make_docs_dir(tmp_path)

    with pytest.raises(ValueError, match="path separator"):
        delete(tmp_path, "subdir/file")


def test_delete_rejects_backslash_in_name(tmp_path: Path) -> None:
    """Backslash is also a path separator (Windows-style)."""
    _make_docs_dir(tmp_path)

    with pytest.raises(ValueError, match="path separator"):
        delete(tmp_path, "subdir\\file")


def test_delete_rejects_absolute_path(tmp_path: Path) -> None:
    """An absolute path as ``name`` must be rejected."""
    _make_docs_dir(tmp_path)

    # ``Path("/etc/passwd")`` is .is_absolute() on POSIX; on Windows the
    # equivalent rejection happens via the separator check. Both branches are
    # covered.
    with pytest.raises(ValueError):
        delete(tmp_path, "/etc/passwd")


def test_delete_rejects_empty_name(tmp_path: Path) -> None:
    """An empty string name must be rejected."""
    _make_docs_dir(tmp_path)

    with pytest.raises(ValueError, match="non-empty"):
        delete(tmp_path, "")


def test_delete_rejects_name_that_is_only_md_suffix(tmp_path: Path) -> None:
    """``.md`` alone has an empty stem after stripping; must be rejected."""
    _make_docs_dir(tmp_path)

    with pytest.raises(ValueError, match="non-empty stem"):
        delete(tmp_path, ".md")


# ---------------------------------------------------------------------------
# Safety: symlinks
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    os.name == "nt",
    reason="symlink creation on Windows requires elevated privileges",
)
def test_delete_rejects_symlink_md(tmp_path: Path) -> None:
    """A symlinked .md target must be refused (link is never followed)."""
    docs = _make_docs_dir(tmp_path)
    # Point the symlink at a file *outside* docs/ so a buggy implementation
    # that follows the link would clearly cross the safety boundary.
    outside = tmp_path / "outside.md"
    outside.write_text("# outside\n", encoding="utf-8")
    md_link = docs / "v1.0.0.md"
    md_link.symlink_to(outside)

    with pytest.raises(ValueError, match="symlink"):
        delete(tmp_path, "v1.0.0")

    # Neither the link nor its target must have been touched.
    assert md_link.is_symlink()
    assert outside.exists()


@pytest.mark.skipif(
    os.name == "nt",
    reason="symlink creation on Windows requires elevated privileges",
)
def test_delete_rejects_symlink_html(tmp_path: Path) -> None:
    """A symlinked .html target must also be refused."""
    docs = _make_docs_dir(tmp_path)
    outside = tmp_path / "outside.html"
    outside.write_text("<html></html>", encoding="utf-8")
    html_link = docs / "v1.0.0.html"
    html_link.symlink_to(outside)
    # Add a real .md to ensure the symlink check fires before the .md is
    # nuked (otherwise a buggy impl could remove the .md first and only
    # later notice the symlink).
    md = docs / "v1.0.0.md"
    md.write_text("# Doc\n", encoding="utf-8")

    with pytest.raises(ValueError, match="symlink"):
        delete(tmp_path, "v1.0.0")

    assert html_link.is_symlink()
    assert outside.exists()
    # NOTE: the contract does not promise atomicity. The .md may or may not
    # have been removed before the symlink was discovered. We assert only the
    # safety-critical fact: the symlink and its outside-target are untouched.
