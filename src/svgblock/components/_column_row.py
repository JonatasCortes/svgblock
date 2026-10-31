from collections.abc import Sequence
from .themes import ThemeData
from ._templates import RenderedComponent, Component, WeightedComponent

COLUMN_GAP = 24


class ColumnRow(Component):
    def __init__(self, columns: Sequence[WeightedComponent]) -> None:
        self._columns = tuple(columns)

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        available_width = width - COLUMN_GAP * (len(self._columns) - 1)
        total_weight = sum(column.weight for column in self._columns)

        parts: list[str] = []
        column_left = left
        row_height = 0.0

        for column in self._columns:
            column_width = available_width * column.weight / total_weight

            rendered = column.render(theme, column_left, top, column_width)

            parts.append(rendered.svg)
            row_height = max(row_height, rendered.height)
            column_left += column_width + COLUMN_GAP

        return RenderedComponent(svg="".join(parts), height=row_height)
