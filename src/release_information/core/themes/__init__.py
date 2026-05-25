"""Theme definitions registered into :data:`release_information.core.theme.THEMES`.

Each module in this package exports CSS / metadata constants (``BASE_CSS``,
``PYGMENTS_STYLE``, ``DISPLAY_NAME``, ``DESCRIPTION``, ``IS_DARK``,
``SOURCE_URL``). The :mod:`release_information.core.theme` module imports
these modules and constructs :class:`Theme` instances in its ``THEMES`` dict.

This split avoids a circular import (``themes/*.py`` never imports the
``Theme`` dataclass) and lets each theme file own a single concern: its CSS.
"""
