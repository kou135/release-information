"""Tests for the THEMES registry contract.

These tests are decoupled from any specific theme by iterating over THEMES.
Adding a new theme requires no test changes as long as the new theme
satisfies the registry contract (Theme dataclass fields are populated).
"""
from __future__ import annotations

import re
import pytest
from pygments.styles import get_all_styles

from release_information.core.theme import (
    DEFAULT_THEME_NAME,
    THEMES,
    Theme,
    get_theme,
)

# C0 で midnight-museum 1 件、C1 で +9 を目標。実装が 8 テーマだった場合に
# テストが落ちないよう、minimum を 8 にしておく（plan §3 の許容範囲）。
THEME_MINIMUM = 8


def test_themes_registry_has_minimum_entries() -> None:
    assert len(THEMES) >= THEME_MINIMUM, (
        f"expected >= {THEME_MINIMUM} themes, got {len(THEMES)}: "
        f"{sorted(THEMES.keys())}"
    )


def test_default_theme_is_registered() -> None:
    assert DEFAULT_THEME_NAME in THEMES
    assert THEMES[DEFAULT_THEME_NAME].name == DEFAULT_THEME_NAME


@pytest.mark.parametrize("name,theme", sorted(THEMES.items()))
def test_theme_name_matches_registry_key(name: str, theme: Theme) -> None:
    assert theme.name == name


@pytest.mark.parametrize("theme", sorted(THEMES.values(), key=lambda t: t.name))
def test_theme_pygments_style_is_valid(theme: Theme) -> None:
    all_styles = set(get_all_styles())
    assert theme.pygments_style in all_styles, (
        f"theme {theme.name!r} uses pygments_style {theme.pygments_style!r} "
        f"which is not a Pygments builtin style"
    )


@pytest.mark.parametrize("theme", sorted(THEMES.values(), key=lambda t: t.name))
def test_theme_base_css_size_is_reasonable(theme: Theme) -> None:
    size = len(theme.base_css.encode("utf-8"))
    assert 1 * 1024 <= size <= 100 * 1024, (
        f"theme {theme.name!r} base_css size {size}B outside 1KB..100KB range"
    )


HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


@pytest.mark.parametrize("theme", sorted(THEMES.values(), key=lambda t: t.name))
def test_theme_base_css_has_minimum_hex_colors(theme: Theme) -> None:
    hexes = set(HEX_RE.findall(theme.base_css))
    assert len(hexes) >= 6, (
        f"theme {theme.name!r} has only {len(hexes)} distinct hex colors; "
        f"expected >= 6 (bg / fg / accent / link / muted / border)"
    )


def test_get_theme_none_returns_default() -> None:
    assert get_theme(None) is THEMES[DEFAULT_THEME_NAME]


def test_get_theme_known_name_returns_that_theme() -> None:
    for name, theme in THEMES.items():
        assert get_theme(name) is theme


def test_get_theme_unknown_raises_valueerror_with_listing() -> None:
    with pytest.raises(ValueError) as exc_info:
        get_theme("definitely-not-a-theme-xxx")
    msg = str(exc_info.value)
    assert "definitely-not-a-theme-xxx" in msg
    # ensure the error message helps the caller discover what is available
    for name in THEMES:
        assert name in msg, f"theme name {name!r} missing from error message: {msg}"
