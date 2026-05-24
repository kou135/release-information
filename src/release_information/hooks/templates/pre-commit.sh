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

if ! python3 -c "import markdown, pygments" 2>/dev/null; then
  echo "[pre-commit] missing python deps for release-information." >&2
  echo "[pre-commit]   pipx install release-information" >&2
  echo "[pre-commit] (or: pip install release-information)" >&2
  exit 1
fi

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
