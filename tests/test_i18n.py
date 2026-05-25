"""Tests for ``release_information.core.i18n``: resolver + string bundle access.

Five cases pin down the resolution priority order and the en-fallback behavior
documented in plan-i18n.md section 4.2. They are environment-sensitive (they
read ``RELEASE_INFORMATION_LANG`` and ``LANG``), so each test scrubs both
variables via ``monkeypatch`` before asserting.
"""

from __future__ import annotations

import pytest

from release_information.core.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    get_strings,
    resolve_locale,
)


@pytest.fixture(autouse=True)
def _clean_locale_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure no host-machine LANG / override env var leaks into the assertions."""
    monkeypatch.delenv("RELEASE_INFORMATION_LANG", raising=False)
    monkeypatch.delenv("LANG", raising=False)


def test_resolve_locale_default_is_en() -> None:
    """No explicit arg, no env vars -> DEFAULT_LOCALE (`en`)."""
    assert resolve_locale() == "en"
    assert DEFAULT_LOCALE == "en"


def test_resolve_locale_respects_explicit_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit argument has highest priority, even when env vars are set."""
    monkeypatch.setenv("RELEASE_INFORMATION_LANG", "ko")
    monkeypatch.setenv("LANG", "hi_IN.UTF-8")
    assert resolve_locale("ja") == "ja"


def test_resolve_locale_falls_back_to_env_lang(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When explicit + override env are absent, POSIX LANG is used."""
    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    assert resolve_locale() == "ja"


def test_get_strings_returns_en_for_unknown_locale() -> None:
    """Unknown locale codes silently fall back to en (no exception)."""
    en_bundle = get_strings("en")
    assert get_strings("zz") == en_bundle


def test_get_strings_en_contains_all_keys() -> None:
    """`en` is the source of truth: it must define every key the renderer uses."""
    en_bundle = get_strings("en")
    required = {"toc_title", "brand_subtitle", "html_lang"}
    assert required.issubset(en_bundle.keys()), (
        f"en bundle is missing required i18n keys: {required - en_bundle.keys()}"
    )
    # Locale code listed in SUPPORTED_LOCALES sanity check.
    assert "en" in SUPPORTED_LOCALES
