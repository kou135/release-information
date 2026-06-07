# release-information

🌐 **English** | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [हिन्दी](./README.hi.md)

[![CI](https://github.com/kou135/release-information/actions/workflows/ci.yml/badge.svg)](https://github.com/kou135/release-information/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

A git pre-commit driven Markdown to single-file HTML renderer for release notes and design
specs. Drop a Markdown file under `docs/release-information/`, commit, and a self-contained
HTML document (Anthropic-flavoured **Midnight Museum** dark theme, inline CSS, auto table of
contents, zero external dependencies) is regenerated and staged alongside it.

## Why this OSS (and not `python-markdown` directly / MkDocs / Quarto / Pandoc)?

Plain `python-markdown` gets you HTML, but not the *kind* of HTML you actually want to hand
to a teammate or to Claude. MkDocs, Quarto, and Pandoc are great, but they ship a site / a
themed multi-page artefact / a Lua-extensible toolchain. `release-information` is deliberately
narrower:

- **A specs-grade dark theme in a package, not a snippet you copy between repos.** The
  Anthropic-style *Midnight Museum* CSS (dark `#0F172A` ground, serif body, sans heading,
  Pygments monokai code, auto `[TOC]`) is shipped *with* the converter, so visual identity
  is uniform across every repository that installs it. No more diverging `style.css` clones.
- **A `docs/release-information/` convention enforced by a pre-commit hook.** The
  `release-information install` command writes a single shell hook that re-renders
  *exactly* the staged Markdown under that one glob — nothing else — and `git add`s the
  resulting HTML in the same commit. No site directory, no `mkdocs build`, no CI step:
  the artefact lives next to its source in the same commit.
- **Single HTML output, inline CSS, zero CDN — pasteable into a Claude context window.**
  Each `.html` is one file. There is no `_site/`, no asset directory, no `<link rel>` to
  external fonts. The whole document is dense, self-contained, and copy-paste-able to an
  AI agent or to Slack without losing styling. This is the gap the existing tools leave
  open: they optimise for *publishing*, this OSS optimises for *handing dense context to a
  reader (human or model)*.

If you only need "Markdown to HTML", reach for `python-markdown` directly. If you want a
documentation site, reach for MkDocs or Quarto. Reach for `release-information` when you
want the **same** dark, dense, single-file release-note HTML in **every** project, generated
on every commit, without thinking about it again.

## Install

Currently installed straight from GitHub. `pipx` is recommended so the CLI is available
globally without polluting any project's venv.

```bash
pipx install git+https://github.com/kou135/release-information.git
# or: pip install git+https://github.com/kou135/release-information.git
```

`release-information` requires Python 3.10+. macOS and Linux are supported; Windows is on
the roadmap (the bundled pre-commit hook is a POSIX shell script).

> **PyPI**: a publish workflow is wired up (`.github/workflows/publish.yml`) but has not
> been triggered yet. See [`docs/PUBLISHING.md`](./docs/PUBLISHING.md) if you want to fork
> and publish your own copy.

## Quick start

Five-minute path from zero to a rendered HTML release note:

```bash
# 1. install the CLI globally
pipx install git+https://github.com/kou135/release-information.git

# 2. move into the repository where you want HTML release notes
cd ~/workspace/your-project

# 3. install the pre-commit hook into <repo>/.git/hooks/pre-commit
#    (also creates docs/release-information/ if missing — see "install" below)
release-information install
#   - existing pre-commit hook? back it up first with: release-information install --force
#   - .git missing? you get an explicit error, nothing else is written.

# 4. add a release note (the directory was created by `install` above)
cat > docs/release-information/v1.0.0.md <<'EOF'
# v1.0.0

## Highlights
- First public release.

## Breaking changes
- None.
EOF

# 5. commit. The hook renders docs/release-information/v1.0.0.html and stages it
#    automatically as part of the same commit.
git add docs/release-information/v1.0.0.md
git commit -m "docs: add v1.0.0 release notes"

# 6. verify
ls docs/release-information/
# v1.0.0.md  v1.0.0.html   <- generated and committed together
```

## Theme gallery

`release-information` ships **11 themes** out of the box. Pick one with the
`--theme` flag on `render` / `render-all`, or list them all with the
`themes` sub-command:

```bash
release-information themes
release-information render docs/release-information/v1.0.0.md --theme nord
```

Browse the full gallery at [`docs/themes/preview.html`](./docs/themes/preview.html)
(open it locally — single-file HTML, no server needed). The same Markdown
source ([`docs/themes/preview-source.md`](./docs/themes/preview-source.md))
is rendered once per theme so you can compare them side by side.

| name              | mode  | one-liner                                                         |
|-------------------|-------|-------------------------------------------------------------------|
| midnight-museum   | dark  | Anthropic-flavoured dark theme with serif headings, warm gold.    |
| nord              | dark  | Arctic, north-bluish palette designed for clarity.                |
| tokyo-night       | dark  | Clean dark theme with vivid neon accents.                         |
| dracula           | dark  | Purple, pink, and cyan accents on a deep slate background.        |
| one-dark          | dark  | Atom-flavoured warm reds, greens, and blues on muted slate.       |
| gruvbox-dark      | dark  | Retro-groove warm earth tones (Pavel Pertsev's gruvbox).          |
| catppuccin-mocha  | dark  | Soothing pastel dark theme (Mocha flavour) from Catppuccin.       |
| monokai-classic   | dark  | Vivid magenta, lime, and cyan on warm coal.                       |
| github-light      | light | Clean light theme inspired by github.com / Primer.                |
| github-dark       | dark  | GitHub's default dark mode palette (Primer dark, calm blue accents). |
| solarized-light   | light | Ethan Schoonover's warm light palette with selective contrast.    |

## Usage

```text
release-information [--version]
release-information --help
release-information render <FILE.md>
release-information render-all [--root .]
release-information install [--repo-root PATH] [--force]
release-information uninstall [--repo-root PATH]
release-information delete --file <NAME> [--repo-root PATH]
release-information version
```

### `render` — single file

```bash
release-information render docs/release-information/v1.0.0.md
# writes docs/release-information/v1.0.0.html (same stem, same directory)
# prints the absolute path of the output to stdout

release-information render docs/release-information/v1.0.0.md --theme nord
# same, but rendered with the `nord` theme instead of the default
# (`midnight-museum`). See `release-information themes` for the full list.
```

### `render-all` — bulk re-render

```bash
release-information render-all                # uses CWD as --root
release-information render-all --root ./repo  # explicit root
release-information render-all --theme nord   # apply the same theme to every file

# Globs docs/release-information/**/*.md (recursive) and re-renders each.
# An empty match is *not* an error: exit code 0.
```

### `themes` — list registered themes

```bash
release-information themes
# Prints one line per registered theme: name, display name, mode (dark/light),
# and a short description. Use any name with --theme on render / render-all.
```

### `install` / `uninstall` — manage the pre-commit hook

```bash
release-information install                   # writes <repo>/.git/hooks/pre-commit
release-information install --force           # overwrite existing hook (backed up)
release-information uninstall                 # restore backup, or remove our hook
```

Side effect: `install` also ensures `<repo>/docs/release-information/` exists
(`mkdir -p`, idempotent). The previously documented manual
`mkdir -p docs/release-information` Quick-start step is no longer required.

The hook only acts on staged files matching `docs/release-information/**/*.md`. Edits to
any other Markdown file (a `README.md`, a `docs/blog/*.md`, etc.) are ignored entirely;
the hook short-circuits with exit 0.

### `delete` — remove a spec and its HTML

```bash
release-information delete --file v1.0.0
# removes docs/release-information/v1.0.0.md and docs/release-information/v1.0.0.html
# the `--file` argument accepts either `v1.0.0` or `v1.0.0.md` (extension stripped)
```

Both `.md` and `.html` are removed in one call. If only one of the pair
exists, only that file is removed. Path traversal (`..`, `/`, absolute
paths) and symlinks under `docs/release-information/` are rejected with
exit code 2. If neither file exists, the command exits with code 2 and
prints a `no such file` message to stderr.

## Design philosophy

### Why HTML for specs?

The Anthropic team and several writers in 2026 (Lenny's Newsletter, Simon Willison, Thariq
Shihipar on ChatPRD) converged on the same finding independently: HTML is a higher
information-density format than Markdown for handing context to AI agents. You can stack
typography, color, table of contents, syntax-highlighted code, and inline data in one file
that a model parses with no preprocessing. `release-information` builds on that observation.

### Why "Midnight Museum"?

The default theme inherits its palette and typography from the author's `minima` workspace
spec renderer: dark `#0F172A` ground, serif body (Hiragino Mincho on macOS, Noto Serif JP
fallback), sans-serif headings, Pygments *monokai* for code. The aesthetic is closer to a
gallery wall card than a docs site — dense, calm, low-contrast where it doesn't matter,
high-contrast where it does. The theme is shipped as a single inline `<style>` block in
`core/theme.py`; no external font CDN is hit at render or view time.

### Why a single HTML output, not a site?

A release note is read once, archived forever, and occasionally pasted into an AI context
window. None of those workflows want a `_site/` directory. One file per `.md` keeps the
output trivially `cat`-able, e-mailable, attachable, and reviewable in a single GitHub diff.

### References

- Lenny Rachitsky — *HTML is the new Markdown* (Lenny's Newsletter, 2026)
- Simon Willison — *The Unreasonable Effectiveness of HTML* (2026-05-08)
- Thariq Shihipar — interview on ChatPRD (*How I AI*, "Claude Code at Anthropic")

## Contributing

```bash
git clone https://github.com/kou135/release-information.git
cd release-information
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

Issues and PRs are welcome. The project optimises for **stability of the rendered HTML
output** (the inline CSS is a public contract; changing it forces every downstream repo to
re-render); behaviour changes require a `CHANGELOG.md` entry under *Changed* or *Breaking*.

## Releasing

Maintainers: see [`docs/PUBLISHING.md`](./docs/PUBLISHING.md) for the PyPI release workflow
(tag-driven, trusted publishing via OIDC — no API tokens).

## Roadmap (out of scope for v0.1.0)

- `pre-commit` framework (`.pre-commit-hooks.yaml`) integration alongside the bundled hook
- Front-matter driven theme selection per file (`theme:` key in YAML front-matter)
- Front-matter driven release note structure (`version`, `date`, `breaking` keys)
- npm distribution / Husky bridge
- Windows pre-commit hook (PowerShell)

## License

[MIT](./LICENSE)
