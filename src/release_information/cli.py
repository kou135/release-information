"""``release-information`` command-line entry point.

The CLI is intentionally built on top of the standard library ``argparse`` only,
so the package keeps a minimal runtime dependency surface (just
``markdown`` + ``pygments`` from :mod:`release_information.core.renderer`).

Sub-commands
------------

``render <FILE.md>``
    Render a single Markdown file. The resulting HTML is written next to the
    input file with the ``.html`` suffix (same stem). Accepts both
    ``--theme NAME`` and ``--lang CODE`` (orthogonal: theme drives visual
    palette, lang drives UI strings like the TOC title).

``render-all``
    Recursively render every ``docs/release-information/**/*.md`` under
    ``--root`` (defaults to the current working directory). Empty matches are
    not an error; exit code 0 is returned. Accepts ``--theme`` and ``--lang``.

``themes``
    Print a human-readable table of every registered theme (name, display
    name, light/dark mode, description). Use the ``--theme NAME`` flag of
    ``render`` / ``render-all`` to render with a specific theme; omit it to
    omit it to use the default ``tokyo-night``.

``install`` / ``uninstall``
    Manage the ``.git/hooks/pre-commit`` hook of a target repository. See
    :mod:`release_information.hooks.install` for the underlying logic.

``delete --file <NAME>``
    Remove ``<repo_root>/docs/release-information/<NAME>.md`` and the matching
    ``<NAME>.html`` in one call. ``<NAME>`` accepts either the bare stem or
    the same name with the ``.md`` extension (the suffix is stripped).
    See :mod:`release_information.files.delete` for the underlying logic
    and safety rails (path traversal / symlink rejection).

``version``
    Print :data:`release_information.__version__`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .core.i18n import SUPPORTED_LOCALES
from .core.renderer import render_markdown
from .core.theme import DEFAULT_THEME_NAME

# Glob used by ``render-all`` (relative to ``--root``).
_RENDER_ALL_GLOB = "docs/release-information/**/*.md"


def _resolve_repo_root(arg: str | None) -> Path:
    """Resolve the repository root.

    If ``arg`` is given, it is used verbatim (resolved to an absolute path).
    Otherwise ``git rev-parse --show-toplevel`` is invoked in the current
    working directory.
    """
    if arg:
        return Path(arg).expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit(
            "release-information: failed to detect git repo root. "
            "Pass --repo-root explicitly or run inside a git working tree.\n"
            f"  detail: {exc}"
        ) from exc
    return Path(result.stdout.strip()).resolve()


def _render_file(
    md_path: Path,
    *,
    theme_name: str | None = None,
    locale: str | None = None,
) -> Path:
    """Render ``md_path`` to ``md_path.with_suffix('.html')`` and return the path.

    Both ``theme_name`` and ``locale`` are forwarded to :func:`render_markdown`.
    ``theme_name=None`` uses the default theme (tokyo-night);
    ``locale=None`` defers to the i18n resolver (env-var driven, default
    ``"en"``).
    """
    md_text = md_path.read_text(encoding="utf-8")
    html = render_markdown(
        md_text,
        title_fallback=md_path.stem,
        theme_name=theme_name,
        locale=locale,
    )
    out_path = md_path.with_suffix(".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _cmd_render(args: argparse.Namespace) -> int:
    md_path = Path(args.file).expanduser().resolve()
    if not md_path.is_file():
        print(f"release-information: not a file: {md_path}", file=sys.stderr)
        return 2
    try:
        out_path = _render_file(md_path, theme_name=args.theme, locale=args.lang)
    except ValueError as exc:
        # core.theme.get_theme() raises with an "available themes: ..." list.
        print(f"release-information: {exc}", file=sys.stderr)
        return 2
    print(str(out_path))
    return 0


def _cmd_render_all(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"release-information: --root is not a directory: {root}", file=sys.stderr)
        return 2
    md_files = sorted(p for p in root.glob(_RENDER_ALL_GLOB) if p.is_file())
    if not md_files:
        # plan.md: "該当ディレクトリが空でもエラーにならず exit 0"
        return 0
    for md_path in md_files:
        try:
            out_path = _render_file(md_path, theme_name=args.theme, locale=args.lang)
        except ValueError as exc:
            # An unknown --theme value applies to every file in this batch, so
            # we can fail fast on the first iteration without partial output.
            print(f"release-information: {exc}", file=sys.stderr)
            return 2
        print(str(out_path))
    return 0


def _cmd_themes(_args: argparse.Namespace) -> int:
    """Print a human-readable table of all registered themes to stdout."""
    # Local import to keep ``render`` / ``render-all`` import surface minimal
    # and to avoid loading every theme module when only --help is requested.
    from .core.theme import THEMES

    rows = [
        (name, t.display_name, "dark" if t.is_dark else "light", t.description)
        for name, t in sorted(THEMES.items())
    ]

    name_w = max(len("NAME"), *(len(r[0]) for r in rows))
    label_w = max(len("DISPLAY NAME"), *(len(r[1]) for r in rows))
    mode_w = max(len("MODE"), *(len(r[2]) for r in rows))

    header = (
        f"{'NAME'.ljust(name_w)}  "
        f"{'DISPLAY NAME'.ljust(label_w)}  "
        f"{'MODE'.ljust(mode_w)}  DESCRIPTION"
    )
    print(header)
    print("-" * len(header))
    for name, label, mode, desc in rows:
        print(
            f"{name.ljust(name_w)}  "
            f"{label.ljust(label_w)}  "
            f"{mode.ljust(mode_w)}  {desc}"
        )
    return 0


def _cmd_install(args: argparse.Namespace) -> int:
    # Lazy import so ``render`` / ``render-all`` keep working even before C6
    # ships, and to avoid importing hooks logic when not needed.
    from .hooks.install import install as hooks_install

    repo_root = _resolve_repo_root(args.repo_root)
    try:
        hook_path = hooks_install(repo_root, force=args.force)
    except FileExistsError as exc:
        print(f"release-information: {exc}", file=sys.stderr)
        print(
            "release-information: pass --force to overwrite (the existing file "
            "is backed up to pre-commit.backup)",
            file=sys.stderr,
        )
        return 1
    except FileNotFoundError as exc:
        print(f"release-information: {exc}", file=sys.stderr)
        return 2
    print(f"installed: {hook_path}")
    # ``hooks_install`` has already created the directory (idempotent,
    # ``exist_ok=True``); we only surface the path so users see that the
    # previously documented ``mkdir -p docs/release-information`` step is no
    # longer required.
    docs_dir = repo_root / "docs" / "release-information"
    print(f"ensured: {docs_dir}/")
    return 0


def _cmd_uninstall(args: argparse.Namespace) -> int:
    from .hooks.install import uninstall as hooks_uninstall

    repo_root = _resolve_repo_root(args.repo_root)
    try:
        result = hooks_uninstall(repo_root)
    except FileNotFoundError as exc:
        print(f"release-information: {exc}", file=sys.stderr)
        return 2
    if result is None:
        print("uninstalled: no hook was present")
    else:
        print(f"uninstalled: {result}")
    return 0


def _cmd_delete(args: argparse.Namespace) -> int:
    # Lazy import for symmetry with _cmd_install (keep render/themes hot paths
    # free of files.delete import cost).
    from .files.delete import delete as files_delete

    repo_root = _resolve_repo_root(args.repo_root)
    try:
        removed = files_delete(repo_root, args.file)
    except ValueError as exc:
        print(f"release-information: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"release-information: {exc}", file=sys.stderr)
        return 2
    for path in removed:
        print(str(path))
    return 0


def _cmd_version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release-information",
        description=(
            "Render Markdown release notes / specs into single-file HTML, and "
            "install a git pre-commit hook that does it automatically."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    p_render = sub.add_parser("render", help="render a single Markdown file")
    p_render.add_argument("file", help="path to a Markdown file (.md)")
    p_render.add_argument(
        "--theme",
        default=None,
        help=f"theme name (default: {DEFAULT_THEME_NAME}). use `themes` sub-command to list.",
    )
    p_render.add_argument(
        "--lang",
        choices=list(SUPPORTED_LOCALES),
        default=None,
        help=(
            "output locale (default: resolved from RELEASE_INFORMATION_LANG / "
            "LANG / 'en')"
        ),
    )
    p_render.set_defaults(func=_cmd_render)

    p_render_all = sub.add_parser(
        "render-all",
        help=f"render every {_RENDER_ALL_GLOB} under --root",
    )
    p_render_all.add_argument(
        "--root",
        default=".",
        help="root directory to scan (default: current working directory)",
    )
    p_render_all.add_argument(
        "--theme",
        default=None,
        help=f"theme name (default: {DEFAULT_THEME_NAME}). use `themes` sub-command to list.",
    )
    p_render_all.add_argument(
        "--lang",
        choices=list(SUPPORTED_LOCALES),
        default=None,
        help=(
            "output locale (default: resolved from RELEASE_INFORMATION_LANG / "
            "LANG / 'en')"
        ),
    )
    p_render_all.set_defaults(func=_cmd_render_all)

    p_themes = sub.add_parser(
        "themes",
        help="list all registered themes (name, display name, mode, description)",
    )
    p_themes.set_defaults(func=_cmd_themes)

    p_install = sub.add_parser(
        "install",
        help="install the pre-commit hook into the target repository",
    )
    p_install.add_argument(
        "--repo-root",
        default=None,
        help="path to the git repository (default: `git rev-parse --show-toplevel`)",
    )
    p_install.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing pre-commit hook (it is backed up first)",
    )
    p_install.set_defaults(func=_cmd_install)

    p_uninstall = sub.add_parser(
        "uninstall",
        help="restore the backed-up pre-commit hook (or remove ours)",
    )
    p_uninstall.add_argument(
        "--repo-root",
        default=None,
        help="path to the git repository (default: `git rev-parse --show-toplevel`)",
    )
    p_uninstall.set_defaults(func=_cmd_uninstall)

    p_delete = sub.add_parser(
        "delete",
        help="delete a Markdown spec and its generated HTML under docs/release-information/",
    )
    p_delete.add_argument(
        "--file",
        required=True,
        help="name of the spec file (extension optional; `.md` is stripped if present)",
    )
    p_delete.add_argument(
        "--repo-root",
        default=None,
        help="path to the git repository (default: `git rev-parse --show-toplevel`)",
    )
    p_delete.set_defaults(func=_cmd_delete)

    p_version = sub.add_parser("version", help="print release-information version")
    p_version.set_defaults(func=_cmd_version)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by both ``python -m release_information`` and the script."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover - exercised via __main__.py
    raise SystemExit(main())
