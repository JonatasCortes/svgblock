"""Generates every SVG block used by the svgblock README.

Importing a section module registers its blocks, so the list below is also
the list of README sections, in the order they appear on the page.
"""

from . import (
    header_and_footer,
    how_it_is_built,
    how_to_use,
    building_a_block,
    animations,
    customization,
    themes,
    troubleshooting,
    easings,
    repeating_and_sequences
)

__all__ = [
    "header_and_footer",
    "how_it_is_built",
    "how_to_use",
    "building_a_block",
    "animations",
    "customization",
    "themes",
    "troubleshooting",
    "easings",
    "repeating_and_sequences"
]
