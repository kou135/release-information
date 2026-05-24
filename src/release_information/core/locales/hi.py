"""Hindi (hi) string bundle.

Mirrors the key set defined in :mod:`release_information.core.locales.en`
(the source of truth). Loaded on demand via
:func:`release_information.core.i18n.get_strings` when the resolved locale
is ``"hi"``.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    "toc_title": "विषय-सूची",
    "brand_subtitle": "विनिर्देश",
    "html_lang": "hi",
}
