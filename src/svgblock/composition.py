from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from .image_reader import read_image
from .themes import ThemeData
from .components import (
    DIVIDER_COVERAGE, TABLE_BORDER_RADIUS, TABLE_CELL_PADDING, TABLE_FONT_SIZE,
    Alignment, CellValue, Component, Image, Paragraph, RenderedComponent,
    Subsection, Table, Title, Divider, format_cell_value,
)

TITLE_FONT_SIZE = 20
SUBSECTION_FONT_SIZE = 17
TEXT_FONT_SIZE = 16

COMPONENT_GAP = 10
COLUMN_GAP = 24

DEFAULT_COLUMN_WEIGHT = 1

_Self = TypeVar("_Self", bound="Composer")


class Composer:
    def __init__(self) -> None:
        self._components: list[Component] = []

    def title(self: _Self, text: str, font_size: float = TITLE_FONT_SIZE) -> _Self:
        self._components.append(Title(text, font_size))
        return self

    def subsection(
        self: _Self, text: str, font_size: float = SUBSECTION_FONT_SIZE
    ) -> _Self:
        self._components.append(Subsection(text, font_size))
        return self

    def text(self: _Self, text: str, font_size: float = TEXT_FONT_SIZE) -> _Self:
        self._components.append(Paragraph(text, font_size))
        return self

    def image(
        self: _Self, path: str | Path, width: float | None = None
    ) -> _Self:
        if width is not None and width <= 0:
            raise ValueError(
                f"Image width must be greater than zero, got {width!r}.")
        self._components.append(Image(read_image(path), width))
        return self

    def columns(self: _Self, *columns: "Column") -> _Self:
        if not columns:
            raise ValueError("columns() needs at least one Column.")
        self._components.append(_Columns(columns))
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
        if any(weight <= 0 for weight in column_weights):
            raise ValueError(
                f"Column weights must be greater than zero, got {column_weights!r}.")

        self._components.append(
            Table(
                columns=tuple(columns),
                rows=tuple(tuple(format_cell_value(cell)
                           for cell in row) for row in rows),
                font_size=font_size,
                cell_padding=cell_padding,
                border_radius=border_radius,
                alignments=alignments,
                weights=column_weights,
                striped=striped,
                row_dividers=row_dividers,
                column_dividers=column_dividers,
            )
        )
        return self

    def divider(self: _Self, coverage: float = DIVIDER_COVERAGE) -> _Self:
        if not 0 <= coverage <= 1:
            raise ValueError(
                f"Divider coverage must be between 0 and 1, got {coverage!r}.")
        self._components.append(Divider(coverage))
        return self

    def _render_components(
        self, theme: ThemeData, left: float, top: float, width: float
    ) -> RenderedComponent:
        parts: list[str] = []
        current_top = top
        for index, component in enumerate(self._components):
            if index > 0:
                current_top += COMPONENT_GAP
            rendered = component.render(theme, left, current_top, width)
            parts.append(rendered.svg)
            current_top += rendered.height
        return RenderedComponent(svg="".join(parts), height=current_top - top)


class Column(Composer):
    def __init__(self, weight: float = DEFAULT_COLUMN_WEIGHT) -> None:
        super().__init__()
        if weight <= 0:
            raise ValueError(
                f"Column weight must be greater than zero, got {weight!r}.")
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        return self._render_components(theme, left, top, width)


class _Columns(Component):
    def __init__(self, columns: Sequence[Column]) -> None:
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
