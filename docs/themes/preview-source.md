# Theme Gallery Preview

This document is the shared source rendered with every registered theme so that
the rendered output of each theme can be compared side by side. It intentionally
exercises every Markdown construct supported by `release-information`'s
renderer: headings (h1–h4), paragraphs, ordered and unordered lists, fenced
code blocks (Python, Bash, JSON), tables, blockquotes, inline emphasis, links,
and an auto-generated table of contents.

Open `preview.html` in the same directory to browse the gallery index, then
click through to any theme's rendered HTML.

## At a glance

`release-information` is a Markdown to single-file HTML renderer for release
notes and design specs. It ships with **10 themes** out of the box — five
dark, two light, and a handful of designer-classic ports. Pick one with the
`--theme` flag on `render` or `render-all`, or list them all with the
`themes` sub-command.

> Every theme is a self-contained inline `<style>` block. The rendered HTML
> never pulls a font, a stylesheet, or a script from a CDN. One file is one
> file.

### Why ship multiple themes?

* Different audiences read at different times of day — the *light* themes
  (`github-light`, `solarized-light`) make printed specs easier to skim.
* Pair-programming and screen-sharing environments often benefit from
  warmer palettes (`gruvbox-dark`, `monokai-classic`) that are easier on
  the eye for long sessions.
* Brand-aligned themes (`midnight-museum`, `tokyo-night`) make a spec feel
  like part of a product rather than a generic doc.

### What's NOT in scope

The `--theme` flag swaps *visual* identity only. It never changes the
underlying HTML structure, the table of contents, the heading anchors, or
any other contract that downstream tooling might depend on.

## A tour of every theme

Every theme defines exactly five things:

1. A registry **name** (e.g. `midnight-museum`, `nord`).
2. A human **display name** (e.g. *Midnight Museum*, *Nord*).
3. A one-line **description** shown by the `themes` sub-command.
4. A complete inline **CSS** body (no external assets).
5. A Pygments **style name** used to colour fenced code blocks.

The `Theme` dataclass also carries a `is_dark` hint (used by the gallery to
group themes into modes) and an optional `source_url` for palette attribution.

## Code samples

### Python

```python
from release_information.core.renderer import render_markdown


def render_for_theme(md_text: str, theme_name: str) -> str:
    """Render *md_text* with the named theme and return the full HTML5 document."""
    return render_markdown(md_text, theme_name=theme_name)


if __name__ == "__main__":
    sample = "# Hello\n\nThis is a *spec*.\n"
    for name in ("midnight-museum", "nord", "tokyo-night"):
        html = render_for_theme(sample, name)
        print(f"{name}: {len(html)} bytes")
```

### Shell

```bash
# render a single file with a non-default theme
release-information render docs/release-information/v1.0.0.md --theme nord

# bulk-render every spec under docs/release-information/ with one theme
release-information render-all --theme tokyo-night

# list every registered theme
release-information themes
```

### JSON

```json
{
  "themes": [
    {"name": "midnight-museum", "mode": "dark"},
    {"name": "nord",            "mode": "dark"},
    {"name": "tokyo-night",     "mode": "dark"},
    {"name": "dracula",         "mode": "dark"},
    {"name": "one-dark",        "mode": "dark"},
    {"name": "github-light",    "mode": "light"},
    {"name": "solarized-light", "mode": "light"},
    {"name": "gruvbox-dark",    "mode": "dark"},
    {"name": "catppuccin-mocha","mode": "dark"},
    {"name": "monokai-classic", "mode": "dark"}
  ]
}
```

## Tables

### Theme registry at a glance

| name              | mode  | family                | one-liner                                                       |
|-------------------|-------|-----------------------|-----------------------------------------------------------------|
| midnight-museum   | dark  | Anthropic-flavoured   | Serif body with warm gold accents on a deep navy ground.        |
| nord              | dark  | Arctic palette        | North-bluish palette designed for clarity and low eye strain.   |
| tokyo-night       | dark  | Neon city palette     | Vivid neon accents inspired by Tokyo's night lights.            |
| dracula           | dark  | Designer classic      | Purple, pink and cyan accents on a deep slate background.       |
| one-dark          | dark  | Editor-classic        | Atom-flavoured warm reds, greens, and blues on muted slate.     |
| github-light      | light | Primer-inspired       | Calm blues and greens with high-contrast typography.            |
| solarized-light   | light | Ethan Schoonover      | Precision-designed warm light palette with selective contrast.  |
| gruvbox-dark      | dark  | Retro-groove          | Warm earth tones (Pavel Pertsev's gruvbox).                     |
| catppuccin-mocha  | dark  | Community pastel      | Soothing pastel dark theme (Mocha flavour).                     |
| monokai-classic   | dark  | Designer classic      | Vivid magenta, lime, and cyan on warm coal.                     |

### Markdown coverage matrix

| construct           | rendered | notes                                              |
|---------------------|----------|----------------------------------------------------|
| h1 / h2 / h3 / h4   | yes      | h1 is also wrapped as the document `<title>`       |
| ordered list        | yes      | Numbered, nested supported                         |
| unordered list      | yes      | Bullets, nested supported                          |
| fenced code         | yes      | Pygments highlighting via theme `pygments_style`   |
| table               | yes      | Pipe table syntax (markdown.extensions.tables)     |
| blockquote          | yes      | Often styled serif/italic for emphasis             |
| inline emphasis     | yes      | `*italic*`, `**bold**`, `` `code` ``               |
| link                | yes      | Default link colour comes from the theme           |
| auto TOC            | yes      | `[TOC]` injected by the renderer, not by source    |

## Blockquotes

> "Specs are read once and archived forever — except when they are not. Make
>  them dense, make them calm, make them survive being pasted into an AI
>  context window."
>
> — paraphrased from the project's design notes

> A second blockquote, deliberately short, to verify spacing between adjacent
> quoted blocks.

## Inline formatting

A paragraph mixing *italic*, **bold**, and `inline code` together with a
[link to the project README](../../README.md) and a [link to the
Anthropic blog](https://www.anthropic.com/) for external-link styling.

## Closing notes

The same Markdown source above is rendered ten times — once per theme — to
produce the per-theme HTML files in this directory. Differences between
those files are *only* the inline `<style>` block (the base CSS and the
Pygments stylesheet); the body HTML is byte-identical. That property is
verified indirectly by the renderer tests in `tests/test_renderer_themes.py`.
