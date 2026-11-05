import math
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from ._image_reader import read_image
from .themes import ThemeData
from ._templates import Component, RenderedComponent, WeightedComponent
from ._divider import Divider
from ._image import Image
from ._paragraph import Paragraph
from ._subsection import Subsection
from ._title import Title
from ._table import (
    Alignment,
    TABLE_BORDER_RADIUS,
    TABLE_CELL_PADDING,
    TABLE_FONT_SIZE,
    CellValue,
    Table,
    TableStyle,
    format_cell_value,
)
from ._column_row import ColumnRow

TITLE_FONT_SIZE = 20
SUBSECTION_FONT_SIZE = 17
TEXT_FONT_SIZE = 16

COMPONENT_GAP = 10

DEFAULT_COLUMN_WEIGHT = 1

_Self = TypeVar("_Self", bound="Composer")


class Composer:
    def __init__(self) -> None:
        self._components: list[Component] = []

    def title(self: _Self, text: str, font_size: float = TITLE_FONT_SIZE) -> _Self:
        self._components.append(Title(text, font_size))
        return self

    def subsection(self: _Self, text: str, font_size: float = SUBSECTION_FONT_SIZE) -> _Self:
        self._components.append(Subsection(text, font_size))
        return self

    def text(self: _Self, text: str, font_size: float = TEXT_FONT_SIZE) -> _Self:
        self._components.append(Paragraph(text, font_size))
        return self

    def image(self: _Self, path: str | Path, width: float | None = None) -> _Self:
        if width is not None and (not math.isfinite(width) or width <= 0):
            raise ValueError(
                f"Image width must be greater than zero and finite, got {width!r}.")
        self._components.append(Image(read_image(path), width))
        return self

    def columns(self: _Self, *columns: WeightedComponent) -> _Self:
        if not columns:
            raise ValueError("columns() needs at least one Column.")
        for column in columns:
            if isinstance(column, Composer) and column._contains(self):
                raise ValueError(
                    "columns() cannot contain the composer it is being added to, "
                    "directly or indirectly."
                )
        self._components.append(ColumnRow(columns))
        return self

    def table(
        self: _Self,
        columns: Sequence[str],
        rows: Sequence[Sequence[CellValue]],
        *,
        font_size: float = TABLE_FONT_SIZE,
        cell_padding: float = TABLE_CELL_PADDING,
        border_radius: float = TABLE_BORDER_RADIUS,
        align: Sequence[Alignment] | None = None,
        weights: Sequence[float] | None = None,
        striped: bool = True,
        row_dividers: bool = True,
        column_dividers: bool = False,
    ) -> _Self:
        if not columns:
            raise ValueError("table() needs at least one column.")
        column_count = len(columns)
        for row in rows:
            if len(row) != column_count:
                raise ValueError(
                    f"Every row needs {column_count} cells, got {len(row)}: {list(row)!r}.")

        alignments = tuple(align) if align is not None else (
            "left",) * column_count
        if len(alignments) != column_count:
            raise ValueError(
                f"align needs {column_count} values, got {len(alignments)}.")

        column_weights = tuple(weights) if weights is not None else (
            DEFAULT_COLUMN_WEIGHT,) * column_count
        if len(column_weights) != column_count:
            raise ValueError(
                f"weights needs {column_count} values, got {len(column_weights)}.")
        if any(not math.isfinite(weight) or weight <= 0 for weight in column_weights):
            raise ValueError(
                f"Column weights must be greater than zero and finite, got {column_weights!r}.")

        style = TableStyle(
            font_size=font_size,
            cell_padding=cell_padding,
            border_radius=border_radius,
            striped=striped,
            row_dividers=row_dividers,
            column_dividers=column_dividers,
        )
        self._components.append(
            Table(
                columns=tuple(columns),
                rows=tuple(
                    tuple(format_cell_value(cell) for cell in row) for row in rows
                ),
                alignments=alignments,
                weights=column_weights,
                style=style,
            )
        )
        return self

    def divider(self: _Self, coverage: float = 1) -> _Self:
        if not 0 <= coverage <= 1:
            raise ValueError(
                f"Divider coverage must be between 0 and 1, got {coverage!r}.")
        self._components.append(Divider(coverage))
        return self

    def _contains(self, target: "Composer") -> bool:
        pending: list[Composer] = [self]
        visited: set[int] = set()
        while pending:
            current = pending.pop()
            if current is target:
                return True
            if id(current) in visited:
                continue
            visited.add(id(current))
            for component in current._components:
                if isinstance(component, ColumnRow):
                    pending.extend(
                        child
                        for child in component.columns
                        if isinstance(child, Composer)
                    )
        return False

    def _render_components(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        parts: list[str] = []
        current_top = top
        for index, component in enumerate(self._components):
            if index > 0:
                current_top += COMPONENT_GAP
            rendered = component.render(theme, left, current_top, width)
            parts.append(rendered.svg)
            current_top += rendered.height
        return RenderedComponent(svg="".join(parts), height=current_top - top)
