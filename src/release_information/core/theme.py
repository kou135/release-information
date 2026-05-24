"""Midnight Museum theme: inline CSS + HTML skeleton for the single-file output.

Ported verbatim from minima/scripts/render-spec.py to preserve visual parity.
Only the aside brand strings are swapped from "Minima" / "Midnight Museum / Spec" to
"Release Information" / "Spec" per plan.md section 3.2.
"""

from __future__ import annotations

# CSS is kept as a raw constant (not an f-string) so that literal `{` / `}` from
# CSS rules do not need escaping. The pygments stylesheet is concatenated at
# render time inside `build_html` instead of being interpolated here.
_BASE_CSS = """
:root {
  --bg: #0F172A;
  --bg-elevated: #131E36;
  --bg-code: #0A1224;
  --fg: #E5E7EB;
  --fg-muted: #94A3B8;
  --fg-dim: #64748B;
  --accent: #C9A961;
  --accent-soft: #A88B4B;
  --border: #1E293B;
  --border-soft: #182338;
  --link: #93C5FD;
  --serif: 'Hiragino Mincho ProN', 'Yu Mincho', 'YuMincho', 'Noto Serif JP', 'Noto Sans Devanagari', 'Times New Roman', serif;
  --sans: -apple-system, BlinkMacSystemFont, 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif;
  --mono: 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace;
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

main.content strong { color: var(--accent); font-weight: 600; }
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
  color: #FBBF24;
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
  background: #1A2540;
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
main.content tr:hover td { background: rgba(201, 169, 97, 0.04); }

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

# Aside brand text: per plan.md section 3.2, the OSS MVP fixes branding to
# "Release Information" / "Spec" instead of minima's "Minima" / "Midnight Museum / Spec".
BRAND_TITLE = "Release Information"
BRAND_SUBTITLE = "Spec"


def build_html(
    title: str,
    body: str,
    toc: str,
    pygments_css: str,
    *,
    html_lang: str = "en",
    brand_subtitle: str = BRAND_SUBTITLE,
) -> str:
    """Assemble the final single-file HTML document.

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
    html_lang:
        Value for ``<html lang="...">``. Defaults to ``"en"`` so callers that
        do not opt into the i18n layer get the English baseline.
    brand_subtitle:
        Aside brand subtitle. Defaults to :data:`BRAND_SUBTITLE` (``"Spec"``)
        so legacy callers continue to render identically.

    Returns
    -------
    str
        A complete UTF-8 HTML5 document with inline CSS and no external assets.
    """
    return (
        '<!DOCTYPE html>\n'
        f'<html lang="{html_lang}">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n'
        '<style>'
        f'{_BASE_CSS}\n'
        f'{pygments_css}\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="layout">\n'
        '  <aside class="toc">\n'
        f'    <div class="toc-brand">{BRAND_TITLE}</div>\n'
        f'    <div class="toc-sub">{brand_subtitle}</div>\n'
        f'    {toc}\n'
        '  </aside>\n'
        '  <main class="content">\n'
        f'{body}\n'
        '  </main>\n'
        '</div>\n'
        '</body>\n'
        '</html>\n'
    )
