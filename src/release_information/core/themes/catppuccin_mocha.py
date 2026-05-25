"""Catppuccin Mocha theme — soothing pastel dark theme.

Palette inspired by the Catppuccin project (the "Mocha" / darkest flavour).
Web search source: https://github.com/catppuccin/catppuccin
Color palette is factual (hex values) and not subject to copyright; the theme
name "Catppuccin" is used in a nominative sense per the upstream MIT licence
and the project's published "Style Guide" / palette spec, which explicitly
welcomes ports as long as the palette mapping is preserved.
"""

from __future__ import annotations

DISPLAY_NAME = "Catppuccin Mocha"
DESCRIPTION = "Soothing pastel dark theme (Mocha flavour) from the Catppuccin community."
PYGMENTS_STYLE = "one-dark"  # No native catppuccin Pygments style; one-dark is the closest fit.
IS_DARK = True
SOURCE_URL: str | None = "https://github.com/catppuccin/catppuccin"

# Palette reference (Catppuccin "Mocha" flavour, from the official style guide):
#   Base       : #1E1E2E
#   Mantle     : #181825
#   Crust      : #11111B
#   Surface 0  : #313244
#   Surface 1  : #45475A
#   Overlay 0  : #6C7086
#   Text       : #CDD6F4
#   Subtext 0  : #A6ADC8
#   Rosewater  : #F5E0DC
#   Mauve      : #CBA6F7
#   Blue       : #89B4FA
#   Sapphire   : #74C7EC
#   Sky        : #89DCEB
#   Green      : #A6E3A1
#   Yellow     : #F9E2AF
#   Peach      : #FAB387
#   Red        : #F38BA8
BASE_CSS = """
:root {
  --bg: #1E1E2E;
  --bg-elevated: #313244;
  --bg-code: #181825;
  --fg: #CDD6F4;
  --fg-muted: #A6ADC8;
  --fg-dim: #6C7086;
  --accent: #CBA6F7;
  --accent-soft: #F5C2E7;
  --border: #45475A;
  --border-soft: #313244;
  --link: #89B4FA;
  --serif: 'Hiragino Mincho ProN', 'Yu Mincho', 'YuMincho', 'Noto Serif JP', 'Times New Roman', serif;
  --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif;
  --mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

.layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  max-width: 1280px;
  margin: 0 auto;
  min-height: 100vh;
}

aside.toc {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow-y: auto;
  padding: 32px 20px 32px 28px;
  border-right: 1px solid var(--border);
  background: var(--bg);
}

aside.toc .toc-brand {
  font-family: var(--serif);
  font-size: 18px;
  letter-spacing: 0.04em;
  color: var(--accent);
  margin: 0 0 4px 0;
}

aside.toc .toc-sub {
  font-size: 11px;
  color: var(--fg-dim);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin: 0 0 24px 0;
}

aside.toc .toctitle { display: none; }
aside.toc .toc { font-size: 13px; }
aside.toc .toc ul { list-style: none; padding: 0; margin: 0; }
aside.toc .toc > ul { border-left: 1px solid var(--border-soft); }
aside.toc .toc li { margin: 0; }

aside.toc .toc a {
  display: block;
  padding: 4px 0 4px 14px;
  color: var(--fg-muted);
  text-decoration: none;
  border-left: 2px solid transparent;
  margin-left: -1px;
  transition: color 120ms, border-color 120ms;
}

aside.toc .toc a:hover {
  color: var(--fg);
  border-left-color: var(--accent-soft);
}

aside.toc .toc ul ul a {
  padding-left: 26px;
  font-size: 12px;
  color: var(--fg-dim);
}

aside.toc .toc ul ul ul a {
  padding-left: 38px;
  font-size: 11px;
}

main.content {
  padding: 64px 56px 96px 56px;
  max-width: 880px;
  width: 100%;
}

main.content h1 {
  font-family: var(--serif);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: 0.02em;
  line-height: 1.3;
  color: var(--fg);
  border-bottom: 1px solid var(--border);
  padding-bottom: 24px;
  margin: 0 0 8px 0;
}

main.content > h1:first-child + p,
main.content > h1:first-child + blockquote {
  color: var(--fg-muted);
  font-style: italic;
}

main.content h2 {
  font-family: var(--serif);
  font-size: 26px;
  font-weight: 400;
  letter-spacing: 0.01em;
  color: var(--accent);
  margin: 64px 0 16px 0;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

main.content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--fg);
  margin: 40px 0 12px 0;
  letter-spacing: 0.01em;
}

main.content h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--fg);
  margin: 28px 0 10px 0;
}

main.content h5, main.content h6 {
  font-size: 13px;
  font-weight: 600;
  color: var(--fg-muted);
  margin: 20px 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

main.content p { margin: 12px 0; color: var(--fg); }

main.content a {
  color: var(--link);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 120ms;
}
main.content a:hover { border-bottom-color: var(--link); }

main.content .headerlink {
  color: var(--fg-dim);
  margin-left: 8px;
  opacity: 0;
  transition: opacity 120ms;
  text-decoration: none;
  font-size: 0.7em;
}
main.content h2:hover .headerlink,
main.content h3:hover .headerlink,
main.content h4:hover .headerlink { opacity: 1; }

main.content strong { color: #F38BA8; font-weight: 600; }
main.content em { color: var(--fg); font-style: italic; }

main.content ul, main.content ol { padding-left: 24px; margin: 12px 0; }
main.content li { margin: 6px 0; color: var(--fg); }
main.content li::marker { color: var(--accent-soft); }

main.content blockquote {
  margin: 20px 0;
  padding: 12px 20px;
  border-left: 3px solid var(--accent-soft);
  background: var(--bg-elevated);
  color: var(--fg-muted);
  border-radius: 0 4px 4px 0;
}
main.content blockquote p { margin: 4px 0; }

main.content hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 56px 0;
}

main.content code {
  font-family: var(--mono);
  font-size: 13px;
  background: var(--bg-code);
  color: #F9E2AF;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid var(--border-soft);
}

main.content pre {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 18px 20px;
  overflow-x: auto;
  margin: 16px 0;
  font-size: 13px;
  line-height: 1.6;
}
main.content pre code {
  background: transparent;
  color: var(--fg);
  border: none;
  padding: 0;
  font-size: 13px;
}

main.content .codehilite {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 16px 0;
  overflow: hidden;
}
main.content .codehilite pre {
  border: none;
  margin: 0;
  border-radius: 0;
}

main.content table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 13px;
  background: var(--bg-elevated);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border);
}
main.content th {
  background: #45475A;
  color: var(--accent);
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  font-family: var(--sans);
}
main.content td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-soft);
  vertical-align: top;
  color: var(--fg);
}
main.content tr:last-child td { border-bottom: none; }
main.content tr:hover td { background: rgba(203, 166, 247, 0.06); }

main.content li input[type="checkbox"] { margin-right: 6px; }

@media print {
  body { background: #fff; color: #111; }
  .layout { display: block; max-width: none; }
  aside.toc { display: none; }
  main.content { padding: 0; max-width: none; }
  main.content h1, main.content h2, main.content h3 {
    color: #111;
    border-color: #ccc;
  }
  main.content strong { color: #111; }
  main.content pre, main.content code, main.content blockquote, main.content table {
    background: #f7f7f7;
    color: #111;
    border-color: #ddd;
  }
  main.content a { color: #1a4ea8; }
}

@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  aside.toc {
    position: static;
    max-height: none;
    border-right: none;
    border-bottom: 1px solid var(--border);
    padding: 20px 24px;
  }
  aside.toc .toc { max-height: 240px; overflow-y: auto; }
  main.content { padding: 32px 24px 64px 24px; }
  main.content h1 { font-size: 28px; }
  main.content h2 { font-size: 22px; }
}
"""
