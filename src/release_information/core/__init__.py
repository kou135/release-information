"""Core rendering primitives: markdown -> HTML conversion and theme assembly."""

from .renderer import render_markdown
from .theme import build_html

__all__ = ["render_markdown", "build_html"]
