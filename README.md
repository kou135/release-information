# release-information

Pre-commit driven Markdown to single-file HTML renderer for release notes and design specs.

`release-information` watches `docs/release-information/**/*.md` in any git repository and, on each
commit, regenerates the matching `.html` file using a dark "Midnight Museum" theme with inline CSS,
syntax highlighting, and an auto-injected table of contents. The output is a self-contained HTML
document with zero runtime dependencies, optimised for handing dense context to AI agents and human
reviewers alike.

Status: WIP (v0.1.0 in progress). CLI, hook installer, and full documentation will land in
subsequent commits.
