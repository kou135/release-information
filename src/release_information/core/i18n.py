"""Locale resolution and string-bundle access for the renderer.

This module is the i18n entry point for the rest of the package. It defines
the supported locales, the default locale (English), and the resolution order
that the renderer (and the CLI ``--lang`` flag) use to decide which language
bundle to pull strings from.

Resolution order (highest priority first):

1. The explicit ``explicit`` argument passed to :func:`resolve_locale`.
2. The ``RELEASE_INFORMATION_LANG`` environment variable.
3. The ``LANG`` environment variable (POSIX locale, e.g. ``ja_JP.UTF-8``).
4. :data:`DEFAULT_LOCALE` (``"en"``).

Unknown locales (anything not in :data:`SUPPORTED_LOCALES`) silently fall back
to English so that the renderer never raises on a stray env var.
"""

from __future__ import annotations

import importlib
import os
from typing import Final

SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en", "ja", "ko", "hi")
DEFAULT_LOCALE: Final[str] = "en"

_ENV_OVERRIDE: Final[str] = "RELEASE_INFORMATION_LANG"
_ENV_POSIX: Final[str] = "LANG"


def _normalize(candidate: str | None) -> str | None:
    """Return a SUPPORTED locale code if ``candidate`` matches one, else ``None``.

    Accepts POSIX-style values like ``ja_JP.UTF-8`` and reduces them to their
    ISO 639-1 prefix (``ja``). Empty / ``None`` inputs return ``None``.
    """
    if not candidate:
        return None
    # POSIX LANG values look like "ja_JP.UTF-8" or "C" / "C.UTF-8"; take the
    # 2-letter prefix only. "C" and "POSIX" do not map to any supported locale.
    prefix = candidate.split("_", 1)[0].split(".", 1)[0].lower()
    if prefix in SUPPORTED_LOCALES:
        return prefix
    return None


def resolve_locale(explicit: str | None = None) -> str:
    """Resolve the effective locale code following the documented priority order.

    Parameters
    ----------
    explicit:
        Optional explicit locale code. When non-``None`` and supported, it wins
        unconditionally. Unsupported explicit values fall through to env vars.

    Returns
    -------
    str
        One of :data:`SUPPORTED_LOCALES`. Always defined; never raises.
    """
    for candidate in (
        explicit,
        os.environ.get(_ENV_OVERRIDE),
        os.environ.get(_ENV_POSIX),
    ):
        resolved = _normalize(candidate)
        if resolved is not None:
            return resolved
    return DEFAULT_LOCALE


def get_strings(locale: str) -> dict[str, str]:
    """Return the string bundle for ``locale``, falling back to English.

    The bundle is a plain ``dict[str, str]`` exported as ``STRINGS`` from
    ``release_information.core.locales.<locale>``. Unknown / not-yet-shipped
    locales transparently fall back to ``en`` so the renderer keeps working
    even before the per-language packs land in subsequent commits.
    """
    effective = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    try:
        module = importlib.import_module(
            f"release_information.core.locales.{effective}"
        )
    except ModuleNotFoundError:
        module = importlib.import_module(
            f"release_information.core.locales.{DEFAULT_LOCALE}"
        )
    strings: dict[str, str] = module.STRINGS
    # Defensive copy: callers must not be able to mutate the cached module dict.
    return dict(strings)
