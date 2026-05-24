"""Theme dataclass, :data:`THEMES` registry, and HTML assembly.

This module replaces the v0.1.1 monolithic ``_BASE_CSS`` constant with a
:class:`Theme` dataclass + a ``THEMES: dict[str, Theme]`` registry. Each
concrete theme lives in :mod:`release_information.core.themes` as a small
module that only exports CSS / metadata constants; this module wires them
into ``Theme`` instances.

Why this split:

* Avoids a circular import — ``themes/*.py`` never needs to know about the
  ``Theme`` dataclass; they only export raw strings / booleans.
* Lets us register 9 more themes in subsequent commits without touching
  ``theme.py`` itself beyond adding one line to ``THEMES``.

Backward compatibility:

* ``render_markdown(md)`` without ``theme_name`` returns the Midnight Museum
  theme (``DEFAULT_THEME_NAME``), producing structurally identical output to
  v0.1.1.
* ``BRAND_TITLE`` / ``BRAND_SUBTITLE`` remain importable at module level for
  existing call sites.
* ``build_html(...)`` keeps its positional signature; the new ``theme=``
  parameter is keyword-only and defaults to the registry default.
"""

from __future__ import annotations

from dataclasses import dataclass

from .themes import midnight_museum as _midnight_museum
from .themes import nord as _nord
from .themes import tokyo_night as _tokyo_night


@dataclass(frozen=True)
class Theme:
    """A complete visual theme: inline CSS + Pygments style name + brand strings.

    Attributes
    ----------
    name:
        Registry key (e.g. ``"midnight-museum"``).
    display_name:
        Human label (e.g. ``"Midnight Museum"``) shown by the ``themes``
        sub-command and the README gallery.
    description:
        One-line short description.
    base_css:
        The full inline ``<style>`` CSS body.
    pygments_style:
        Style name passed to ``HtmlFormatter(style=...)`` by the renderer.
    brand_title:
        Title shown in the sidebar aside (default ``"Release Information"``).
    brand_subtitle:
        Subtitle shown under the brand title (default ``"Spec"``).
    is_dark:
        Hint used by docs / preview gallery (does not affect rendering).
    source_url:
        Optional web search citation for the palette / typography origin.
    """

    name: str
    display_name: str
    description: str
    base_css: str
    pygments_style: str
    brand_title: str = "Release Information"
    brand_subtitle: str = "Spec"
    is_dark: bool = True
    source_url: str | None = None


THEMES: dict[str, Theme] = {
    "midnight-museum": Theme(
        name="midnight-museum",
        display_name=_midnight_museum.DISPLAY_NAME,
        description=_midnight_museum.DESCRIPTION,
        base_css=_midnight_museum.BASE_CSS,
        pygments_style=_midnight_museum.PYGMENTS_STYLE,
        is_dark=_midnight_museum.IS_DARK,
        source_url=_midnight_museum.SOURCE_URL,
    ),
    "nord": Theme(
        name="nord",
        display_name=_nord.DISPLAY_NAME,
        description=_nord.DESCRIPTION,
        base_css=_nord.BASE_CSS,
        pygments_style=_nord.PYGMENTS_STYLE,
        is_dark=_nord.IS_DARK,
        source_url=_nord.SOURCE_URL,
    ),
    "tokyo-night": Theme(
        name="tokyo-night",
        display_name=_tokyo_night.DISPLAY_NAME,
        description=_tokyo_night.DESCRIPTION,
        base_css=_tokyo_night.BASE_CSS,
        pygments_style=_tokyo_night.PYGMENTS_STYLE,
        is_dark=_tokyo_night.IS_DARK,
        source_url=_tokyo_night.SOURCE_URL,
    ),
}

DEFAULT_THEME_NAME: str = "midnight-museum"

# Backward-compatible module-level brand constants. Existing code that does
# ``from release_information.core.theme import BRAND_TITLE`` keeps working.
BRAND_TITLE: str = THEMES[DEFAULT_THEME_NAME].brand_title
BRAND_SUBTITLE: str = THEMES[DEFAULT_THEME_NAME].brand_subtitle


def get_theme(name: str | None) -> Theme:
    """Return the named theme, falling back to :data:`DEFAULT_THEME_NAME`.

    Parameters
    ----------
    name:
        Registry key, or ``None`` to receive the default theme.

    Raises
    ------
    ValueError
        If ``name`` is not ``None`` and is not present in :data:`THEMES`. The
        message lists every available theme name sorted alphabetically so the
        CLI can surface it verbatim in error output.
    """
    if name is None:
        return THEMES[DEFAULT_THEME_NAME]
    if name not in THEMES:
        available = ", ".join(sorted(THEMES.keys()))
        raise ValueError(
            f"unknown theme: {name!r}. available themes: {available}"
        )
    return THEMES[name]


def build_html(
    title: str,
    body: str,
    toc: str,
    pygments_css: str,
    *,
    theme: Theme | None = None,
) -> str:
    """Assemble the final single-file HTML document for the given theme.

    Parameters
    ----------
    title:
        Value to place inside ``<title>``. Already escaped/cleaned by caller.
    body:
        Rendered Markdown HTML (the inner content of ``<main>``).
    toc:
        The ``markdown.Markdown`` ``toc`` attribute, already HTML.
    pygments_css:
        Stylesheet emitted by ``pygments.formatters.HtmlFormatter``.
    theme:
        Theme to render with. ``None`` falls back to :data:`DEFAULT_THEME_NAME`
        so existing call sites that omit the keyword stay working.

    Returns
    -------
    str
        A complete UTF-8 HTML5 document with inline CSS and no external assets.
    """
    if theme is None:
        theme = THEMES[DEFAULT_THEME_NAME]
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ja">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n'
        '<style>'
        f'{theme.base_css}\n'
        f'{pygments_css}\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="layout">\n'
        '  <aside class="toc">\n'
        f'    <div class="toc-brand">{theme.brand_title}</div>\n'
        f'    <div class="toc-sub">{theme.brand_subtitle}</div>\n'
        f'    {toc}\n'
        '  </aside>\n'
        '  <main class="content">\n'
        f'{body}\n'
        '  </main>\n'
        '</div>\n'
        '</body>\n'
        '</html>\n'
    )
