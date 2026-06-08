"""CLI tests for the --theme flag and themes sub-command."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from release_information.core.theme import DEFAULT_THEME_NAME, THEMES

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_BASIC = REPO_ROOT / "tests" / "fixtures" / "sample-basic.md"
CLI = "release-information"


def _have_cli() -> bool:
    return shutil.which(CLI) is not None


pytestmark = pytest.mark.skipif(
    not _have_cli(),
    reason=(
        "release-information CLI not on PATH; run `pip install -e \".[dev]\"` first"
    ),
)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [CLI, *args], cwd=cwd, capture_output=True, text=True, check=False,
    )


def test_cli_themes_subcommand_lists_all_registered_themes(tmp_path: Path) -> None:
    result = _run("themes", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    for name in THEMES:
        assert name in result.stdout, (
            f"theme name {name!r} missing from `themes` output:\n{result.stdout}"
        )


def test_cli_render_accepts_theme_flag(tmp_path: Path) -> None:
    # use the first non-default theme if available, else fall back to default
    non_default = sorted(n for n in THEMES if n != DEFAULT_THEME_NAME)
    theme_name = non_default[0] if non_default else DEFAULT_THEME_NAME

    src = tmp_path / "input.md"
    src.write_text(FIXTURE_BASIC.read_text(encoding="utf-8"), encoding="utf-8")
    result = _run("render", str(src), "--theme", theme_name, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    out_html = src.with_suffix(".html")
    assert out_html.is_file()
    content = out_html.read_text(encoding="utf-8")
    # at least one hex color from the theme's CSS must appear in the rendered HTML
    theme = THEMES[theme_name]
    assert any(
        hex_color in content
        for hex_color in _extract_hex_colors(theme.base_css)
    ), f"no hex color from theme {theme_name} found in rendered HTML"


def test_cli_render_unknown_theme_exits_2(tmp_path: Path) -> None:
    src = tmp_path / "input.md"
    src.write_text(FIXTURE_BASIC.read_text(encoding="utf-8"), encoding="utf-8")
    result = _run("render", str(src), "--theme", "definitely-not-a-theme-xxx", cwd=tmp_path)
    assert result.returncode == 2
    assert "available themes" in result.stderr.lower() or "available" in result.stderr.lower()


def test_cli_render_all_accepts_theme_flag(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "release-information"
    docs.mkdir(parents=True)
    (docs / "a.md").write_text("# Doc A\n\nfirst.\n", encoding="utf-8")
    (docs / "b.md").write_text("# Doc B\n\nsecond.\n", encoding="utf-8")

    non_default = sorted(n for n in THEMES if n != DEFAULT_THEME_NAME)
    theme_name = non_default[0] if non_default else DEFAULT_THEME_NAME

    result = _run("render-all", "--theme", theme_name, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (docs / "a.html").is_file()
    assert (docs / "b.html").is_file()


# --- helpers ---

_HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def _extract_hex_colors(css: str) -> list[str]:
    return _HEX_RE.findall(css)
