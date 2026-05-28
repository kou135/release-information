"""End-to-end regression test for the bundled ``pre-commit`` hook.

T5 background
-------------

T3 shipped a pre-commit hook that re-renders every staged
``docs/release-information/**/*.md`` to a single-file HTML and ``git add``s
the result, so a single ``git commit -m "..."`` produces the matching HTML
in the same commit (dogfooding).

In T4 we discovered the hook was a silent no-op: git's default pathspec does
not glob-expand ``**``, so the hook's ``git diff --cached --name-only --
'docs/release-information/**/*.md'`` always returned an empty list and the
script exited 0 without rendering anything.

The existing ``test_hook_install.py`` only covered the install/uninstall
metadata flow (where the file lands, chmod bits, backup/restore). It never
actually ran the hook from inside ``git commit``, which is why the glob bug
slipped through. This module fills that gap: it spins up a real tmp git repo,
installs the hook, commits a markdown file, and asserts the resulting commit
contains the rendered HTML next to it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

import release_information.hooks.install as _hooks_install_mod
from release_information.hooks.install import install

# Absolute path to the bundled hook template that ``install()`` copies into
# ``<repo>/.git/hooks/pre-commit``. Resolving it from the install module keeps
# this test honest if the template ever moves.
HOOK_TEMPLATE_PATH = (
    Path(_hooks_install_mod.__file__).parent / "templates" / "pre-commit.sh"
)


def _git_available() -> bool:
    return shutil.which("git") is not None


def _cli_available() -> bool:
    return shutil.which("release-information") is not None


pytestmark = pytest.mark.skipif(
    not (_git_available() and _cli_available()),
    reason=(
        "needs both ``git`` and the ``release-information`` CLI on PATH"
        " (run `pip install -e \".[dev]\"` first)"
    ),
)


def _run_git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command in ``cwd`` with deterministic identity envs."""
    env = os.environ.copy()
    # Make commits work in an isolated tmp repo without depending on the
    # user's global git config (also keeps the test deterministic).
    env.setdefault("GIT_AUTHOR_NAME", "release-information tests")
    env.setdefault("GIT_AUTHOR_EMAIL", "tests@release-information.local")
    env.setdefault("GIT_COMMITTER_NAME", "release-information tests")
    env.setdefault("GIT_COMMITTER_EMAIL", "tests@release-information.local")
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.fixture
def hooked_repo(tmp_path: Path) -> Path:
    """tmp_path with an initialised git repo *and* our pre-commit hook installed."""
    init = _run_git("init", "--quiet", cwd=tmp_path)
    assert init.returncode == 0, init.stderr
    # Initial branch name does not matter for this test; git's default is fine.

    hook_path = install(tmp_path, force=False)
    assert hook_path.is_file()
    return tmp_path


def test_pre_commit_hook_renders_staged_markdown_into_same_commit(
    hooked_repo: Path,
) -> None:
    """Committing ``docs/release-information/v0.1.0.md`` produces ``v0.1.0.html``.

    Regression guard for the T4-discovered glob bug: before the fix the hook
    silently exited 0 and ``v0.1.0.html`` was never staged. With the
    ``:(glob)`` pathspec fix the hook re-renders the markdown and ``git add``s
    the resulting HTML, so both files appear in the same commit.
    """
    docs = hooked_repo / "docs" / "release-information"
    # ``install()`` (run by the hooked_repo fixture) now creates this directory
    # itself, so the test must tolerate the directory already existing.
    docs.mkdir(parents=True, exist_ok=True)
    md = docs / "v0.1.0.md"
    md.write_text(
        "# v0.1.0\n\nInitial release of release-information.\n",
        encoding="utf-8",
    )

    add = _run_git("add", str(md.relative_to(hooked_repo)), cwd=hooked_repo)
    assert add.returncode == 0, add.stderr

    commit = _run_git(
        "commit", "-m", "docs: add v0.1.0 release notes", cwd=hooked_repo
    )
    assert commit.returncode == 0, (
        f"commit failed.\nstdout:\n{commit.stdout}\nstderr:\n{commit.stderr}"
    )

    # The hook must have written the rendered HTML next to the markdown.
    rendered = docs / "v0.1.0.html"
    assert rendered.is_file(), (
        "pre-commit hook did not produce the HTML file"
        f" (regression of the T5 glob bug?). Commit output:\n"
        f"stdout:\n{commit.stdout}\nstderr:\n{commit.stderr}"
    )

    # And it must be part of HEAD (the hook ``git add``s it before commit
    # finalisation, which is the whole point of dogfooding via pre-commit).
    show = _run_git("show", "--name-only", "--pretty=format:", "HEAD", cwd=hooked_repo)
    assert show.returncode == 0, show.stderr
    committed_paths = {
        line.strip() for line in show.stdout.splitlines() if line.strip()
    }
    assert "docs/release-information/v0.1.0.md" in committed_paths
    assert "docs/release-information/v0.1.0.html" in committed_paths, (
        "v0.1.0.html was rendered but not included in the same commit;"
        f" git show output:\n{show.stdout}"
    )


def test_pre_commit_hook_ignores_unrelated_markdown(hooked_repo: Path) -> None:
    """Markdown outside ``docs/release-information/`` must not be auto-rendered.

    The hook is intentionally scoped to the release-notes directory. This
    test pins the contract so a future glob change does not silently start
    rendering ``README.md`` or other top-level markdown.
    """
    readme = hooked_repo / "README.md"
    readme.write_text("# Sample repo\n\nNothing to see here.\n", encoding="utf-8")

    add = _run_git("add", "README.md", cwd=hooked_repo)
    assert add.returncode == 0, add.stderr

    commit = _run_git("commit", "-m", "chore: add README", cwd=hooked_repo)
    assert commit.returncode == 0, (
        f"commit failed.\nstdout:\n{commit.stdout}\nstderr:\n{commit.stderr}"
    )

    # No README.html should have been generated.
    assert not (hooked_repo / "README.html").exists()

    show = _run_git("show", "--name-only", "--pretty=format:", "HEAD", cwd=hooked_repo)
    committed_paths = {
        line.strip() for line in show.stdout.splitlines() if line.strip()
    }
    assert committed_paths == {"README.md"}, (
        f"unexpected files in HEAD commit: {committed_paths}"
    )


def test_pre_commit_hook_template_has_no_system_python_dep_check() -> None:
    """Static guard against the T6-discovered isolated-venv regression.

    The bundled hook template runs in the *system* shell, so any
    ``python3 -c "import markdown, pygments"`` style probe would resolve
    against the user's system ``python3`` — but those packages live in the
    CLI's own (often pipx-managed) venv, not in the system interpreter.
    The previous version of the hook did exactly that and consequently
    failed every commit under a pipx install.

    We pin the contract at the template level: the file must not contain
    any ``import markdown`` / ``import pygments`` string. The hook is
    allowed to *invoke* the ``release-information`` CLI (which brings its
    own deps); it must not second-guess them through the host interpreter.

    Bypassing this guard requires a deliberate, reviewed change to both
    the hook and this test, which is the point.
    """
    assert HOOK_TEMPLATE_PATH.is_file(), (
        f"hook template not found at {HOOK_TEMPLATE_PATH}"
    )
    template_src = HOOK_TEMPLATE_PATH.read_text(encoding="utf-8")

    forbidden_fragments = (
        "import markdown",
        "import pygments",
    )
    offending = [frag for frag in forbidden_fragments if frag in template_src]
    assert not offending, (
        "pre-commit.sh must not probe deps through the system python3"
        f" (found forbidden fragments: {offending}). See T6 handoff:"
        " those packages only exist in the CLI's own venv under pipx"
        " installs, so a host-level import check always false-positives."
    )
