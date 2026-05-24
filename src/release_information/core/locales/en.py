"""English (en) string bundle — source of truth for the i18n key set.

Any new UI string added to the renderer must first land here. Per-language
bundles (``ja``, ``ko``, ``hi``) ship in subsequent commits and are validated
against the keys defined in this file.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    "toc_title": "Contents",
    "brand_subtitle": "Spec",
    "html_lang": "en",
}
