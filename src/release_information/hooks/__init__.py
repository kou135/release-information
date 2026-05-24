"""Git hook installation logic for release-information.

The :mod:`release_information.hooks.install` module exposes :func:`install`
and :func:`uninstall` which place / restore the bundled ``pre-commit.sh``
template at ``<repo_root>/.git/hooks/pre-commit``.
"""
