"""Delete a release-information spec and its rendered HTML in one call.

Behavior overview
-----------------

``delete(repo_root, name)``
    1. Validate ``name`` rejects path traversal (no ``/``, ``\\``, ``..``,
       no absolute path components). Raises :class:`ValueError` on violation.
    2. Strip a trailing ``.md`` from ``name`` if present, producing the
       canonical stem.
    3. Compute the two candidate paths::

           <repo_root>/docs/release-information/<stem>.md
           <repo_root>/docs/release-information/<stem>.html

    4. For each candidate that exists:
         - refuse to unlink if it is a symlink (raises :class:`ValueError`);
         - verify ``Path.resolve()`` is still inside the docs directory
           (raises :class:`ValueError` otherwise);
         - call :meth:`pathlib.Path.unlink`.
    5. If neither file existed at all, raise :class:`FileNotFoundError`.
    6. Return the list of paths that were actually removed (preserving the
       ``.md`` then ``.html`` order, length 1 or 2).

Safety constraints
------------------

- All writes are confined to ``<repo_root>/docs/release-information/``. The
  ``resolve().is_relative_to(docs_dir)`` check is the second line of defense
  after the ``name`` sanitization.
- We never use recursive removal (:func:`shutil.rmtree`). Only single-file
  :meth:`pathlib.Path.unlink` is invoked.
- Symlinks are rejected with :class:`ValueError`; we never follow them and
  never unlink the link itself implicitly.
"""

from __future__ import annotations

from pathlib import Path

_DOCS_SUBDIR = ("docs", "release-information")
_MD_SUFFIX = ".md"
_HTML_SUFFIX = ".html"


def _validate_name(name: str) -> str:
    """Validate ``name`` and return the canonical stem (``.md`` stripped).

    Raises
    ------
    ValueError
        If ``name`` is empty, contains a path separator (``/`` or ``\\``),
        contains ``..``, or is otherwise unsafe to use as a single-file stem.
    """
    if not name:
        raise ValueError("name must be a non-empty string")
    if "/" in name or "\\" in name:
        raise ValueError(
            f"name must not contain path separators: {name!r}"
        )
    # Reject any ".." segment as a defense-in-depth check (even though the
    # separator check above already catches "../foo"). A bare ".." is also
    # nonsensical as a file stem.
    if name == ".." or name.startswith("../") or name.endswith("/..") or "/.." in name:
        raise ValueError(f"name must not contain '..': {name!r}")
    # Reject anything that looks like an absolute path. ``Path(name).is_absolute()``
    # catches both POSIX (``/foo``) and Windows-drive (``C:\foo``) forms.
    if Path(name).is_absolute():
        raise ValueError(f"name must be a bare filename, not an absolute path: {name!r}")

    # Strip a single trailing ``.md`` (and only ``.md``) so callers can pass
    # either ``v1.0.0`` or ``v1.0.0.md`` interchangeably.
    if name.endswith(_MD_SUFFIX):
        stem = name[: -len(_MD_SUFFIX)]
    else:
        stem = name

    if not stem:
        raise ValueError(f"name must have a non-empty stem: {name!r}")
    # After stripping ``.md`` the result must still be a single path component.
    # (e.g. reject ``"./.md"`` etc.)
    if stem in {".", ".."}:
        raise ValueError(f"name resolves to a special directory entry: {name!r}")

    return stem


def _check_inside_docs(candidate: Path, docs_dir: Path) -> None:
    """Verify ``candidate`` resolves to a path inside ``docs_dir``.

    ``candidate`` is allowed to not exist; we still ``.resolve(strict=False)``
    so that the comparison is meaningful even before the file is created.

    Raises
    ------
    ValueError
        If the resolved candidate escapes ``docs_dir``.
    """
    resolved_candidate = candidate.resolve(strict=False)
    resolved_docs = docs_dir.resolve(strict=False)
    if not resolved_candidate.is_relative_to(resolved_docs):
        raise ValueError(
            "refusing to operate outside docs/release-information/: "
            f"{resolved_candidate} is not under {resolved_docs}"
        )


def delete(repo_root: Path, name: str) -> list[Path]:
    """Remove ``<repo_root>/docs/release-information/<name>.{md,html}``.

    Parameters
    ----------
    repo_root:
        Path to a git working tree (the directory that contains
        ``docs/release-information/``).
    name:
        Bare name of the spec (e.g. ``"v1.0.0"``). Accepts either the bare
        stem or the same stem with the ``.md`` extension — the suffix is
        stripped before computing the target paths. Path separators,
        ``..`` segments, and absolute paths are rejected with
        :class:`ValueError`.

    Returns
    -------
    list[pathlib.Path]
        The list of paths that were actually unlinked, in the order
        ``[.md, .html]`` (length 1 or 2).

    Raises
    ------
    ValueError
        ``name`` failed the safety sanitization (path traversal, separator,
        empty, ...), or one of the target files was a symlink, or one of
        the resolved targets escaped ``docs/release-information/``.
    FileNotFoundError
        Neither the ``.md`` nor the ``.html`` file existed.
    """
    stem = _validate_name(name)
    docs_dir = repo_root.joinpath(*_DOCS_SUBDIR)

    md_path = docs_dir / f"{stem}{_MD_SUFFIX}"
    html_path = docs_dir / f"{stem}{_HTML_SUFFIX}"

    removed: list[Path] = []
    for candidate in (md_path, html_path):
        # ``lstat`` lets us detect symlinks without following them; ``exists``
        # would follow the link and report on the target instead.
        if not candidate.is_symlink() and not candidate.exists():
            continue
        if candidate.is_symlink():
            raise ValueError(
                f"refusing to delete symlink: {candidate}"
            )
        # Defense-in-depth: even after the name check, verify the resolved
        # path is still under docs_dir. Catches anyone who manages to bypass
        # _validate_name() in the future.
        _check_inside_docs(candidate, docs_dir)
        candidate.unlink()
        removed.append(candidate)

    if not removed:
        raise FileNotFoundError(
            f"no such file: neither {md_path} nor {html_path} exists"
        )

    return removed
