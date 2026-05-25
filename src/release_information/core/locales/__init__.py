"""Per-locale string bundles for the renderer.

Each module in this package exports a ``STRINGS: dict[str, str]`` mapping
keyed by the same set of identifiers (with ``en`` acting as the source of
truth for that set). Loaded on demand via
:func:`release_information.core.i18n.get_strings`.
"""
