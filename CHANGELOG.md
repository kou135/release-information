# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New `github-dark` theme (11th theme) — GitHub.com's default dark palette
  (Primer dark). Use via `--theme github-dark`. Palette sourced from
  Primer Primitives (`primer/primitives`) and confirmed against
  projekt0n/github-nvim-theme's `github_dark` port (Primer dark default).
  Includes `docs/themes/github-dark.html` preview rendered from the shared
  gallery source. Pygments style: `github-dark` (confirmed Pygments builtin).
- `release-information delete --file <NAME>` sub-command: removes
  `<repo_root>/docs/release-information/<NAME>.md` and the matching
  `.html` in one call. Path traversal (`..`, `/`, absolute paths) and
  symlinks are rejected (exit code 2). Accepts either bare names or
  names with the `.md` extension.
- i18n support for ja/ko/hi. New `--lang` CLI flag on `render` and
  `render-all` subcommands; `release_information.core.i18n` module exposing
  `resolve_locale` and `get_strings`. Locale resolution order: explicit
  argument > `RELEASE_INFORMATION_LANG` > `LANG` > `en`. Translation packs
  for ja/ko/hi land in subsequent commits.
- `release-information install` now ensures `<repo_root>/docs/release-information/`
  exists (idempotent, `exist_ok=True`). The `mkdir -p docs/release-information`
  step previously documented in the Quick start is no longer required. The
  CLI also prints an `ensured: <path>/` line alongside the existing
  `installed: <hook_path>` output.

## [0.3.0] - 2026-05-25

### Added

- 9 additional themes registered alongside `midnight-museum`:
  `nord`, `tokyo-night`, `dracula`, `one-dark`, `github-light`,
  `solarized-light`, `gruvbox-dark`, `catppuccin-mocha`, `monokai-classic`.
- `--theme NAME` flag for `render` / `render-all` sub-commands.
- `release-information themes` sub-command listing all registered themes
  (name, display name, mode, one-line description).
- `docs/themes/preview.html` gallery comparing all 10 themes side by side,
  plus per-theme HTML previews (`docs/themes/<theme-name>.html`) rendered
  from a shared `docs/themes/preview-source.md` source.

### Changed

- `core.theme` refactored into a `THEMES: dict[str, Theme]` registry. The
  Midnight Museum theme is now registered under the name `midnight-museum`
  and remains the default. No behaviour change for callers using
  `render_markdown(md_text)` without `theme_name`.

## [0.1.1] - 2026-05-24

### Fixed

- pre-commit hook now works correctly under pipx (and any isolated-venv)
  installs by removing the system-python dep pre-check that referenced
  packages only present in the CLI's own venv. The hook still verifies the
  `release-information` CLI is on `PATH` (`command -v` probe), which is the
  correct boundary: if the CLI is installed, its packaging guarantees its own
  `markdown` / `pygments` dependencies are present inside its venv.

## [0.1.0] - 2026-05-24

Initial public release. Carves the `minima` workspace's spec renderer out into a
reusable, installable OSS package.

### Added

- `release_information.core.renderer.render_markdown(md_text, title_fallback=...)`
  pure function that converts a Markdown string into a self-contained HTML5
  document with auto-injected `[TOC]`, syntax highlighting (Pygments monokai),
  and the **Midnight Museum** dark theme.
- `release_information.core.theme` module bundling the Anthropic-flavoured
  Midnight Museum inline CSS (`#0F172A` ground, serif body, sans heading) and
  the brand strings `Release Information` / `Spec`.
- `release-information` CLI (`argparse` based, standard-library only) with
  sub-commands:
  - `render <FILE.md>` — render a single file to `<stem>.html`.
  - `render-all [--root .]` — recursively render
    `docs/release-information/**/*.md`.
  - `install [--repo-root PATH] [--force]` — write the bundled pre-commit hook
    to `<repo>/.git/hooks/pre-commit`, backing up any existing hook to
    `pre-commit.backup`.
  - `uninstall [--repo-root PATH]` — restore the backup, or remove the hook
    if no backup is present.
  - `version` — print `release_information.__version__`.
- Bundled `pre-commit.sh` hook template that re-renders only the staged
  `docs/release-information/**/*.md` files, ignores every other Markdown edit,
  and `git add`s the resulting HTML in the same commit.
- `pytest` suite (27 cases) covering renderer goldens, CLI smoke,
  install/uninstall flows on a temporary `git init`'d repository.
- GitHub Actions CI (`ruff check src tests` + `pytest`) on a Python
  3.10 / 3.11 / 3.12 matrix.
- `docs/release-information/v0.1.0.md` — dogfooded release note that produces
  `v0.1.0.html` via the project's own pre-commit hook on commit.
- MIT license.

### Changed

- _N/A (initial release)._

### Fixed

- _N/A (initial release)._

### Security

- The pre-commit hook never recursively deletes anything: install writes a
  single file (`pre-commit`) with `chmod 0o755`; uninstall removes a single
  file (`pre-commit`) or restores a single file (`pre-commit.backup`). The
  `.git/` directory is never traversed.

[Unreleased]: https://github.com/kou135/release-information/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/kou135/release-information/compare/v0.1.1...v0.3.0
[0.1.1]: https://github.com/kou135/release-information/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/kou135/release-information/releases/tag/v0.1.0
