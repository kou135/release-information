"""Japanese (ja) string bundle.

Mirrors the key set defined in :mod:`release_information.core.locales.en`
(the source of truth). Loaded on demand via
:func:`release_information.core.i18n.get_strings` when the resolved locale
is ``"ja"``.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    "toc_title": "目次",
    "brand_subtitle": "仕様",
    "html_lang": "ja",
}
