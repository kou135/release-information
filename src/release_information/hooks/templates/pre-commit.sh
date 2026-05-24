#!/usr/bin/env bash
# release-information pre-commit hook.
#
# Re-renders every staged ``docs/release-information/**/*.md`` file to a
# single-file HTML (same stem) using the ``release-information`` CLI and
# automatically ``git add``s the resulting ``.html``. Edits to other ``.md``
# files are ignored.
#
# Installed by ``release-information install`` into
# ``<repo>/.git/hooks/pre-commit``.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# NOTE: ``**`` is *not* glob-expanded by git's default pathspec, so writing
# ``docs/release-information/**/*.md`` matches a literal ``**`` segment that
# never exists. The ``:(glob)`` pathspec magic prefix opts into shell-style
# globbing (see ``man gitglossary`` → "pathspec / glob magic"), which lets us
# capture every staged markdown under ``docs/release-information/``,
# including nested sub-directories.
staged_md=$(git diff --cached --name-only --diff-filter=ACMR -- ':(glob)docs/release-information/**/*.md' || true)

if [ -z "$staged_md" ]; then
  exit 0
fi

# NOTE: We intentionally do *not* probe the host ``python3`` for the
# renderer's Python deps here. Those deps live inside the
# ``release-information`` CLI's own environment (e.g. a pipx-managed venv
# under ``~/.local/pipx/venvs/release-information/``), not in the system
# interpreter, so a host-level dep check would false-positive on every
# isolated-venv install. The ``command -v`` probe below is the right
# boundary: if the CLI is on PATH, we trust its packaging to have brought
# its own deps. See the static guard in ``tests/test_pre_commit_hook.py``
# (T6 regression).
if ! command -v release-information >/dev/null 2>&1; then
  echo "[pre-commit] release-information CLI not found on PATH." >&2
  echo "[pre-commit]   pipx install release-information" >&2
  exit 1
fi

while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  [ -f "$spec" ] || continue
  echo "[pre-commit] rendering $spec"
  release-information render "$spec"
  git add "${spec%.md}.html"
done <<< "$staged_md"

echo "[pre-commit] re-rendered HTML staged"
