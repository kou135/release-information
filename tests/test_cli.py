"""Smoke tests for the ``release-information`` CLI.

The tests invoke the installed entry-point via :mod:`subprocess` so we exercise
the entire boot path (argparse, lazy imports, entry_points). All file system
side effects are confined to ``tmp_path``.

The CLI script is assumed to be on ``PATH`` because ``pip install -e .[dev]``
was executed during the dev environment setup (see plan.md §6.2 and the T1
handoff).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import release_information

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_BASIC = REPO_ROOT / "tests" / "fixtures" / "sample-basic.md"

CLI = "release-information"


def _have_cli() -> bool:
    """Return True iff the ``release-information`` entry point is on PATH."""
    return shutil.which(CLI) is not None


# All CLI tests share the same skip guard: if pip install -e . was not run in
# the active environment, the entry point will be missing and we cannot
# exercise the subprocess path.
pytestmark = pytest.mark.skipif(
    not _have_cli(),
    reason=(
        "release-information CLI not on PATH; run `pip install -e \".[dev]\"` first"
    ),
)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run the CLI with the given args in ``cwd`` and return the completed proc."""
    return subprocess.run(
        [CLI, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_help_lists_all_subcommands(tmp_path: Path) -> None:
    """``--help`` must mention every sub-command we expose."""
    result = _run("--help", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    for sub in ("render", "render-all", "install", "uninstall", "version"):
        assert sub in result.stdout, (
            f"sub-command {sub!r} missing from --help output:\n{result.stdout}"
        )


def test_cli_version_matches_package_version(tmp_path: Path) -> None:
    """``release-information version`` must print the package's __version__."""
    result = _run("version", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == release_information.__version__


def test_cli_render_emits_html_next_to_input(tmp_path: Path) -> None:
    """``render <md>`` must create the same-stem ``.html`` and exit 0."""
    src = tmp_path / "input.md"
    src.write_text(FIXTURE_BASIC.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run("render", str(src), cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    out_html = src.with_suffix(".html")
    assert out_html.is_file(), f"expected {out_html} to be created"
    # stdout must report the absolute path of the produced HTML.
    assert str(out_html) in result.stdout
    # The output must look like the renderer's HTML5 envelope.
    content = out_html.read_text(encoding="utf-8")
    assert content.startswith("<!DOCTYPE html>")
    assert "<title>Sample Title</title>" in content


def test_cli_render_returns_2_for_missing_file(tmp_path: Path) -> None:
    """``render`` against a non-existent path exits with code 2 (per CLI contract)."""
    result = _run("render", str(tmp_path / "does-not-exist.md"), cwd=tmp_path)

    assert result.returncode == 2
    assert "not a file" in result.stderr


def test_cli_render_all_processes_every_markdown(tmp_path: Path) -> None:
    """``render-all`` must convert every md under ``docs/release-information/``."""
    docs = tmp_path / "docs" / "release-information"
    docs.mkdir(parents=True)
    md_a = docs / "a.md"
    md_b = docs / "b.md"
    md_a.write_text("# Doc A\n\nfirst doc body.\n", encoding="utf-8")
    md_b.write_text("# Doc B\n\nsecond doc body.\n", encoding="utf-8")

    result = _run("render-all", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert (docs / "a.html").is_file()
    assert (docs / "b.html").is_file()
    # stdout reports both produced paths.
    assert str(docs / "a.html") in result.stdout
    assert str(docs / "b.html") in result.stdout


def test_cli_render_all_is_noop_for_empty_directory(tmp_path: Path) -> None:
    """An empty ``docs/release-information/`` must exit 0 with no file produced."""
    docs = tmp_path / "docs" / "release-information"
    docs.mkdir(parents=True)

    result = _run("render-all", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert not any(docs.iterdir()), "no files should have been produced"


def test_cli_render_all_errors_when_root_missing(tmp_path: Path) -> None:
    """``render-all --root <missing>`` exits with code 2."""
    bogus = tmp_path / "no-such-dir"
    result = _run("render-all", "--root", str(bogus), cwd=tmp_path)
    assert result.returncode == 2


def test_cli_install_creates_docs_release_information_dir(tmp_path: Path) -> None:
    """``release-information install --repo-root <path>`` also mkdirs docs/release-information/.

    Exercised through the actual CLI entry point (not the Python API) so we
    catch any regression in ``_cmd_install`` argument plumbing.
    """
    # git init the tmp_path so install() does not bail on the .git check.
    subprocess.run(
        ["git", "init", "--quiet"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    docs_dir = tmp_path / "docs" / "release-information"
    assert not docs_dir.exists()

    result = _run("install", "--repo-root", str(tmp_path), cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert docs_dir.is_dir(), (
        f"expected {docs_dir} to be created by `release-information install`"
    )
    # stdout should mention both the hook and the docs dir so users see the
    # side effect explicitly.
    assert "installed:" in result.stdout
    assert "ensured:" in result.stdout
    assert str(docs_dir) in result.stdout


def test_python_dash_m_invocation_works(tmp_path: Path) -> None:
    """``python -m release_information --help`` works as the equivalent entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "release_information", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "render" in result.stdout
