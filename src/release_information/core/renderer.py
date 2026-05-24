"""Markdown -> HTML rendering pipeline.

Ported from minima/scripts/render-spec.py. The rendering pipeline is:

1. Parse Markdown with Python-Markdown (``extra``, ``toc``, ``codehilite``,
   ``sane_lists``, ``admonition``).
2. If ``[TOC]`` is not present, inject it immediately after the first ``# `` heading
   so every document gets a sidebar TOC by default.
3. Extract the first ``<h1>`` text as the document ``<title>`` (with a caller
   provided fallback).
4. Build the syntax-highlighting stylesheet via Pygments (monokai).
5. Compose the final HTML by handing everything to
   :func:`release_information.core.theme.build_html`.
"""

from __future__ import annotations

import copy
import re

import markdown
from pygments.formatters import HtmlFormatter

from .i18n import get_strings, resolve_locale
from .theme import build_html

_MARKDOWN_EXTENSIONS: list[str] = [
    "extra",
    "toc",
    "codehilite",
    "sane_lists",
    "admonition",
]

# Note: the ``toc.title`` entry is overwritten per render based on the resolved
# locale (see ``render_markdown``); the literal here is a harmless placeholder
# that gets replaced before being handed to ``markdown.Markdown``.
_MARKDOWN_EXTENSION_CONFIGS: dict[str, dict[str, object]] = {
    "toc": {
        "title": "Contents",
        "anchorlink": True,
        "permalink": False,
        "toc_depth": "2-3",
    },
    "codehilite": {
        "guess_lang": False,
        "noclasses": False,
        "css_class": "codehilite",
    },
}

_H1_TITLE_RE = re.compile(r"<h1[^>]*>(.+?)</h1>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _inject_toc_marker(md_text: str) -> str:
    """Insert ``[TOC]`` right after the first ``# `` heading if absent.

    Mirrors the minima behavior so every rendered document automatically gets
    the sidebar TOC without the author having to remember the marker.
    """
    if "[TOC]" in md_text:
        return md_text
    lines = md_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "")
            lines.insert(i + 2, "[TOC]")
            lines.insert(i + 3, "")
            break
    return "\n".join(lines)


def _extract_title(body_html: str, fallback: str) -> str:
    """Extract a plain-text title from the first ``<h1>`` in the rendered HTML.

    Falls back to ``fallback`` if no ``<h1>`` is found or its text is empty.
    """
    match = _H1_TITLE_RE.search(body_html)
    if not match:
        return fallback
    inner = _TAG_RE.sub("", match.group(1)).strip()
    return inner or fallback


def render_markdown(
    md_text: str,
    *,
    title_fallback: str = "",
    locale: str | None = None,
) -> str:
    """Render a Markdown string to a single-file HTML document.

    Parameters
    ----------
    md_text:
        UTF-8 Markdown source.
    title_fallback:
        Used as the ``<title>`` value when no ``<h1>`` is present in ``md_text``.
    locale:
        Optional locale code (``"en"``, ``"ja"``, ``"ko"``, ``"hi"``). When
        ``None`` the effective locale is resolved via
        :func:`release_information.core.i18n.resolve_locale` (env-var driven).

    Returns
    -------
    str
        A complete HTML5 document (``<!DOCTYPE html>`` through ``</html>``) with
        inline CSS, Pygments-highlighted code blocks, and an auto-injected TOC.
    """
    effective_locale = resolve_locale(locale)
    strings = get_strings(effective_locale)

    # Deep-copy so the per-render TOC title override never mutates the
    # module-level config (otherwise concurrent renders with different
    # locales would race on the shared dict).
    extension_configs = copy.deepcopy(_MARKDOWN_EXTENSION_CONFIGS)
    extension_configs["toc"]["title"] = strings["toc_title"]

    prepared = _inject_toc_marker(md_text)
    md = markdown.Markdown(
        extensions=_MARKDOWN_EXTENSIONS,
        extension_configs=extension_configs,
        output_format="html5",
    )
    body = md.convert(prepared)
    pygments_css = HtmlFormatter(style="monokai").get_style_defs(".codehilite")
    title = _extract_title(body, title_fallback)
    return build_html(
        title=title,
        body=body,
        toc=md.toc,
        pygments_css=pygments_css,
        html_lang=strings["html_lang"],
        brand_subtitle=strings["brand_subtitle"],
    )
