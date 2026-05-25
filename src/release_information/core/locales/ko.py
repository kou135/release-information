"""Korean (ko) string bundle.

Mirrors the key set defined in :mod:`release_information.core.locales.en`
(the source of truth). Loaded on demand via
:func:`release_information.core.i18n.get_strings` when the resolved locale
is ``"ko"``.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    "toc_title": "목차",
    "brand_subtitle": "사양",
    "html_lang": "ko",
}
