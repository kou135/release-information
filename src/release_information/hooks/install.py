"""Install / uninstall the bundled pre-commit hook into a git repository.

Behavior overview
-----------------

``install(repo_root, *, force=False)``
    1. Verify ``repo_root / ".git"`` exists (raises :class:`FileNotFoundError`
       otherwise — we never write outside a real git working tree).
    2. Ensure ``repo_root / ".git" / "hooks"`` exists (mkdir if missing).
    3. If a ``pre-commit`` hook already exists:
         - with ``force=False``: raise :class:`FileExistsError`.
         - with ``force=True``: copy it to ``pre-commit.backup`` and overwrite.
    4. Copy the bundled :mod:`templates.pre-commit.sh` to ``pre-commit`` and
       set mode ``0o755``.

``uninstall(repo_root)``
    1. Verify ``repo_root / ".git"`` exists.
    2. If ``pre-commit.backup`` exists, move it back to ``pre-commit`` and
       return its path.
    3. Else if ``pre-commit`` exists, delete it via :meth:`pathlib.Path.unlink`
       and return its (now removed) path.
    4. Else return ``None``.

Safety constraints
------------------

- All writes are confined to ``<repo_root>/.git/hooks/``. No other path is ever
  touched.
- We never use :func:`os.remove` recursively — only single-file
  :meth:`Path.unlink` / :func:`shutil.copy2`.
- We never invoke ``git`` here; the caller (CLI) resolves ``repo_root``.
"""

from __future__ import annotations

import shutil
import stat
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "pre-commit.sh"

_HOOK_FILENAME = "pre-commit"
_BACKUP_FILENAME = "pre-commit.backup"


def _hooks_dir(repo_root: Path) -> Path:
    """Return ``<repo_root>/.git/hooks`` after validating the .git directory.

    Raises
    ------
    FileNotFoundError
        If ``<repo_root>/.git`` does not exist (i.e. ``repo_root`` is not a
        git working tree).
    """
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        raise FileNotFoundError(
            f"not a git working tree: {repo_root} (missing .git/)"
        )
    hooks = git_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    return hooks


def install(repo_root: Path, *, force: bool = False) -> Path:
    """Install the bundled pre-commit hook into ``repo_root``.

    Parameters
    ----------
    repo_root:
        Path to a git working tree (the directory that contains ``.git/``).
    force:
        If True and an existing ``pre-commit`` hook is present, it is backed
        up to ``pre-commit.backup`` and then overwritten. If False, a
        :class:`FileExistsError` is raised when an existing hook is found.

    Returns
    -------
    pathlib.Path
        Absolute path to the installed hook (i.e.
        ``<repo_root>/.git/hooks/pre-commit``).

    Raises
    ------
    FileNotFoundError
        ``repo_root`` is not a git working tree.
    FileExistsError
        A ``pre-commit`` hook already exists and ``force`` is False.
    """
    hooks_dir = _hooks_dir(repo_root)
    target = hooks_dir / _HOOK_FILENAME
    backup = hooks_dir / _BACKUP_FILENAME

    if target.exists():
        if not force:
            raise FileExistsError(
                f"pre-commit hook already exists: {target}"
            )
        # force=True: back up existing hook before overwrite.
        shutil.copy2(target, backup)

    shutil.copyfile(_TEMPLATE_PATH, target)
    # chmod 0o755 (rwxr-xr-x)
    target.chmod(
        stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
    )
    return target


def uninstall(repo_root: Path) -> Path | None:
    """Remove our pre-commit hook, restoring the previous backup if any.

    Parameters
    ----------
    repo_root:
        Path to a git working tree.

    Returns
    -------
    pathlib.Path | None
        - When a backup is restored: the path of the restored hook.
        - When the hook is simply removed (no backup): the path of the (now
          deleted) hook.
        - When neither file exists: ``None``.

    Raises
    ------
    FileNotFoundError
        ``repo_root`` is not a git working tree.
    """
    hooks_dir = _hooks_dir(repo_root)
    target = hooks_dir / _HOOK_FILENAME
    backup = hooks_dir / _BACKUP_FILENAME

    if backup.exists():
        # Restore: replace ``pre-commit`` with the backed-up contents and drop
        # the backup file.
        if target.exists():
            target.unlink()
        shutil.move(str(backup), str(target))
        return target

    if target.exists():
        target.unlink()
        return target

    return None
