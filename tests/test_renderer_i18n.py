"""Renderer-side i18n tests (en baseline + ja from C1 + ko from C2; hi lands in C3).

Per plan-i18n.md section 4.2 / 4.3, this module verifies that:

1. ``<html lang="...">`` is emitted with the resolved locale code.
2. The TOC title text in the rendered HTML matches the per-locale string
   bundle (``"Contents"`` for en, ``"目次"`` for ja, etc.).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from release_information.core.renderer import render_markdown

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(autouse=True)
def _clean_locale_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the renderer to resolve to ``en`` regardless of host env vars."""
    monkeypatch.delenv("RELEASE_INFORMATION_LANG", raising=False)
    monkeypatch.delenv("LANG", raising=False)


@pytest.fixture
def basic_md() -> str:
    return (FIXTURES_DIR / "sample-basic.md").read_text(encoding="utf-8")


def test_render_emits_html_lang_attribute_en(basic_md: str) -> None:
    """Default (no LANG / no override / no arg) -> ``<html lang="en">``."""
    html = render_markdown(basic_md, locale="en")
    assert '<html lang="en">' in html


def test_render_uses_locale_specific_toc_title_en(basic_md: str) -> None:
    """The en TOC title 'Contents' must appear in the rendered body."""
    html = render_markdown(basic_md, locale="en")
    # The toc extension wraps its title in a <span class="toctitle"> by default.
    # We only assert presence of the literal string, which is what end users
    # see (the aside also surfaces the TOC tree).
    assert "Contents" in html


def test_render_emits_html_lang_attribute_ja(basic_md: str) -> None:
    """Explicit ``locale="ja"`` -> ``<html lang="ja">`` plus the ja TOC title."""
    html = render_markdown(basic_md, locale="ja")
    assert '<html lang="ja">' in html
    assert "目次" in html


def test_render_emits_html_lang_attribute_ko(basic_md: str) -> None:
    """Explicit ``locale="ko"`` -> ``<html lang="ko">`` plus the ko TOC title."""
    html = render_markdown(basic_md, locale="ko")
    assert '<html lang="ko">' in html
    assert "목차" in html
