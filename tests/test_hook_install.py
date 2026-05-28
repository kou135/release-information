"""Tests for ``release_information.hooks.install`` (install / uninstall flow).

All filesystem activity is confined to ``tmp_path``; the user's real
``~/.git/hooks`` and ``~/.gitconfig`` are never touched. We exercise the
underlying Python API directly (`hooks.install.install` / `uninstall`) which
is both faster and matches the CLI behavior as documented in the T3 handoff.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from release_information.hooks.install import install, uninstall

# How install() should chmod the produced hook (rwxr-xr-x).
_EXPECTED_MODE = 0o755


def _git_available() -> bool:
    return shutil.which("git") is not None


pytestmark = pytest.mark.skipif(
    not _git_available(), reason="git not on PATH; cannot init a fixture repo"
)


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Path:
    """Create a ``git init`` repository under ``tmp_path`` and return its path."""
    subprocess.run(
        ["git", "init", "--quiet"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (tmp_path / ".git").is_dir(), "git init must produce a .git directory"
    return tmp_path


def test_install_creates_executable_pre_commit_hook(tmp_git_repo: Path) -> None:
    """install() writes an executable ``pre-commit`` script under .git/hooks/."""
    hook_path = install(tmp_git_repo, force=False)

    assert hook_path == tmp_git_repo / ".git" / "hooks" / "pre-commit"
    assert hook_path.is_file()
    # T3 handoff explicitly calls out the 0o755 regression guard.
    assert hook_path.stat().st_mode & 0o777 == _EXPECTED_MODE
    # The hook body should be a shell script (starts with shebang).
    head = hook_path.read_text(encoding="utf-8").splitlines()[0]
    assert head.startswith("#!"), f"unexpected first line: {head!r}"


def test_install_refuses_to_overwrite_existing_hook(tmp_git_repo: Path) -> None:
    """A second install without force raises FileExistsError (no overwrite)."""
    install(tmp_git_repo, force=False)
    with pytest.raises(FileExistsError):
        install(tmp_git_repo, force=False)


def test_install_force_backs_up_existing_hook(tmp_git_repo: Path) -> None:
    """force=True moves the existing hook to ``pre-commit.backup`` and writes ours."""
    hooks_dir = tmp_git_repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    existing = hooks_dir / "pre-commit"
    sentinel = "#!/bin/sh\necho user-supplied-hook\n"
    existing.write_text(sentinel, encoding="utf-8")
    existing.chmod(_EXPECTED_MODE)

    install(tmp_git_repo, force=True)

    backup = hooks_dir / "pre-commit.backup"
    assert backup.is_file(), "existing hook must have been backed up"
    assert backup.read_text(encoding="utf-8") == sentinel
    # The new hook is our template, *not* the sentinel.
    new_hook = (hooks_dir / "pre-commit").read_text(encoding="utf-8")
    assert new_hook != sentinel
    assert (hooks_dir / "pre-commit").stat().st_mode & 0o777 == _EXPECTED_MODE


def test_uninstall_restores_backup_when_present(tmp_git_repo: Path) -> None:
    """uninstall() must restore the backed-up hook contents byte-for-byte."""
    hooks_dir = tmp_git_repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    existing = hooks_dir / "pre-commit"
    sentinel = "#!/bin/sh\necho user-supplied-hook\n"
    existing.write_text(sentinel, encoding="utf-8")
    existing.chmod(_EXPECTED_MODE)

    install(tmp_git_repo, force=True)
    restored = uninstall(tmp_git_repo)

    assert restored == hooks_dir / "pre-commit"
    assert restored.is_file()
    assert restored.read_text(encoding="utf-8") == sentinel
    # The backup file must now be gone (consumed by the restore).
    assert not (hooks_dir / "pre-commit.backup").exists()


def test_uninstall_removes_hook_when_no_backup(tmp_git_repo: Path) -> None:
    """Without a backup, uninstall() removes our installed pre-commit hook."""
    install(tmp_git_repo, force=False)
    hook_path = tmp_git_repo / ".git" / "hooks" / "pre-commit"
    assert hook_path.is_file()

    result = uninstall(tmp_git_repo)

    assert result == hook_path
    assert not hook_path.exists()


def test_uninstall_is_noop_when_hook_absent(tmp_git_repo: Path) -> None:
    """uninstall() returns None when neither pre-commit nor backup exists."""
    # No install() was called; .git/hooks/ exists from git init but is empty
    # of pre-commit / pre-commit.backup.
    result = uninstall(tmp_git_repo)
    assert result is None


def test_install_raises_filenotfounderror_when_not_a_git_tree(tmp_path: Path) -> None:
    """install() refuses to write into a directory without a .git/ sub-dir.

    This is the safety net documented in the T3 handoff: if ``repo_root``
    points outside any real working tree, no file is ever created.
    """
    assert not (tmp_path / ".git").exists()
    with pytest.raises(FileNotFoundError):
        install(tmp_path, force=False)

    # And the hooks dir was not created on the side.
    assert not (tmp_path / ".git").exists()


def test_uninstall_raises_filenotfounderror_when_not_a_git_tree(tmp_path: Path) -> None:
    """Same safety net for uninstall()."""
    assert not (tmp_path / ".git").exists()
    with pytest.raises(FileNotFoundError):
        uninstall(tmp_path)


def test_install_creates_docs_release_information_dir(tmp_git_repo: Path) -> None:
    """install() must also create ``<repo_root>/docs/release-information/``.

    The directory is the convention path the pre-commit hook scans on every
    commit. Creating it here folds the previously documented
    ``mkdir -p docs/release-information`` Quick-start step into ``install``.
    """
    docs_dir = tmp_git_repo / "docs" / "release-information"
    assert not docs_dir.exists(), "fixture must start without the docs dir"

    install(tmp_git_repo, force=False)

    assert docs_dir.is_dir(), (
        f"expected {docs_dir} to be created as a side effect of install()"
    )


def test_install_is_idempotent_when_docs_dir_already_exists(
    tmp_git_repo: Path,
) -> None:
    """install() must not raise when docs/release-information/ already exists.

    Pre-existing files inside the directory must be preserved (no recursive
    delete, no overwrite).
    """
    docs_dir = tmp_git_repo / "docs" / "release-information"
    docs_dir.mkdir(parents=True)
    sentinel = docs_dir / "user-note.md"
    sentinel_body = "# pre-existing release note\n\nuser content.\n"
    sentinel.write_text(sentinel_body, encoding="utf-8")

    # Must not raise (idempotent ``mkdir(..., exist_ok=True)``).
    install(tmp_git_repo, force=False)

    # Directory still there, sentinel file untouched.
    assert docs_dir.is_dir()
    assert sentinel.is_file(), "pre-existing file must survive install()"
    assert sentinel.read_text(encoding="utf-8") == sentinel_body
