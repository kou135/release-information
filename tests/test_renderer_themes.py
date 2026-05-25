"""Render every registered theme on a fixture markdown and assert basics.

Three assertions per theme:
1. The output is a complete HTML5 document (doctype to </html>).
2. The output contains the theme's brand_title (default: "Release Information").
3. The output size is in a reasonable range (8KB..200KB — upper bound is
   relaxed vs. test_renderer.py to accommodate larger themes / more inline CSS).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from release_information.core.renderer import render_markdown
from release_information.core.theme import THEMES, Theme

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample-basic.md"


@pytest.fixture(scope="module")
def sample_md() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.mark.parametrize("name,theme", sorted(THEMES.items()))
def test_render_with_theme_produces_complete_html(name: str, theme: Theme, sample_md: str) -> None:
    html = render_markdown(sample_md, theme_name=name)
    assert html.startswith("<!DOCTYPE html>"), f"{name}: missing HTML5 doctype"
    assert html.rstrip().endswith("</html>"), f"{name}: not ending with </html>"


@pytest.mark.parametrize("name,theme", sorted(THEMES.items()))
def test_render_with_theme_contains_brand_title(name: str, theme: Theme, sample_md: str) -> None:
    html = render_markdown(sample_md, theme_name=name)
    assert theme.brand_title in html, f"{name}: brand_title {theme.brand_title!r} missing"


@pytest.mark.parametrize("name,theme", sorted(THEMES.items()))
def test_render_with_theme_size_in_reasonable_range(name: str, theme: Theme, sample_md: str) -> None:
    html = render_markdown(sample_md, theme_name=name)
    size = len(html.encode("utf-8"))
    assert 8 * 1024 <= size <= 200 * 1024, (
        f"{name}: rendered HTML size {size}B outside 8KB..200KB range"
    )
