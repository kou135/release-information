"""Golden tests for ``release_information.core.renderer.render_markdown``.

The rendered HTML embeds large inline CSS, so we cannot rely on byte-for-byte
equality (a single CSS tweak would shatter every assertion). Instead we verify
the contract: structural markers, brand strings, codehilite class for fenced
code, [TOC] non-duplication, and that the output size lands in a plausible
range.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from release_information.core.renderer import _inject_toc_marker, render_markdown

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def basic_md() -> str:
    return (FIXTURES_DIR / "sample-basic.md").read_text(encoding="utf-8")


@pytest.fixture
def with_toc_md() -> str:
    return (FIXTURES_DIR / "sample-with-toc.md").read_text(encoding="utf-8")


def test_render_returns_complete_html5_document(basic_md: str) -> None:
    """Output is a complete HTML5 document with the inline-CSS skeleton."""
    html = render_markdown(basic_md)

    assert html.startswith("<!DOCTYPE html>"), "output must start with HTML5 doctype"
    assert html.rstrip().endswith("</html>"), "output must end with </html>"
    assert "<style>" in html, "inline CSS block must be present"
    assert "</style>" in html


def test_render_contains_brand_strings(basic_md: str) -> None:
    """The Midnight Museum aside must carry the Release Information brand."""
    html = render_markdown(basic_md)

    # Brand title from core/theme.py (BRAND_TITLE = "Release Information").
    assert "Release Information" in html


def test_render_extracts_h1_into_title_tag(basic_md: str) -> None:
    """The first <h1> text becomes the document <title>."""
    html = render_markdown(basic_md)

    # sample-basic.md begins with "# Sample Title".
    assert "<title>Sample Title</title>" in html


def test_render_uses_fallback_title_when_no_h1() -> None:
    """When the markdown has no h1, ``title_fallback`` is used."""
    html = render_markdown(
        "no top-level heading here, only a paragraph.",
        title_fallback="v9.9.9",
    )

    assert "<title>v9.9.9</title>" in html


def test_render_applies_codehilite_class_to_fenced_code(basic_md: str) -> None:
    """Fenced code blocks must end up wrapped in the codehilite class."""
    html = render_markdown(basic_md)

    assert "codehilite" in html, (
        "Pygments via the codehilite extension must wrap fenced code blocks"
    )


def test_inject_toc_marker_is_idempotent_when_marker_present(with_toc_md: str) -> None:
    """``_inject_toc_marker`` must not duplicate an existing ``[TOC]`` marker."""
    # plan.md / task: "[TOC] が既にあれば自動挿入が二重にならない"
    # We assert on the *source-level* transform because that is precisely the
    # invariant the injection step is supposed to enforce; once Markdown
    # processes the source, ``[TOC]`` becomes an opaque ``<div class="toc">``
    # block whose count is also influenced by the aside template.
    assert with_toc_md.count("[TOC]") == 1
    transformed = _inject_toc_marker(with_toc_md)
    assert transformed.count("[TOC]") == 1, (
        "second [TOC] must not be injected when one already exists"
    )


def test_inject_toc_marker_adds_marker_when_missing(basic_md: str) -> None:
    """When the source has no ``[TOC]``, exactly one is injected after the first h1."""
    assert basic_md.count("[TOC]") == 0
    transformed = _inject_toc_marker(basic_md)
    assert transformed.count("[TOC]") == 1


def test_render_emits_one_body_toc_block(with_toc_md: str) -> None:
    """The body must contain exactly one TOC block regardless of marker presence.

    The aside template always renders its own TOC block from ``md.toc``, so the
    full document has two ``<div class="toc">`` occurrences (aside + body) when
    the source contains ``[TOC]``. We verify the *body-side* count to ensure
    we did not accidentally double-render the in-body TOC because of double
    injection.
    """
    html = render_markdown(with_toc_md)
    body_start = html.index('<main class="content">')
    body_end = html.index("</main>")
    body_html = html[body_start:body_end]
    assert body_html.count('<div class="toc">') == 1


def test_render_output_size_is_within_reasonable_range(basic_md: str) -> None:
    """Inline CSS gives us a ~8KB floor; anything past 100KB is suspicious."""
    html = render_markdown(basic_md)

    size = len(html.encode("utf-8"))
    assert 8 * 1024 <= size <= 100 * 1024, (
        f"rendered HTML size {size}B outside expected 8KB..100KB range"
    )


def test_render_includes_table_markup(basic_md: str) -> None:
    """Markdown tables must compile to <table>/<th>/<td> via the ``extra`` extension."""
    html = render_markdown(basic_md)

    assert "<table>" in html
    assert "<th>" in html
    assert "<td>" in html


def test_render_includes_blockquote(basic_md: str) -> None:
    """Blockquote source must produce a <blockquote> tag."""
    html = render_markdown(basic_md)

    assert "<blockquote>" in html
