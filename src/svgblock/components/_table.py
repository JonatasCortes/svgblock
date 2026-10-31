from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal
from xml.sax.saxutils import escape
from ._stylized_markup import segments_markup, svg_text_markup
from .text import (
    parse_markup,
    wrap_into_lines,
    wrap_bold_text,
    calculate_line_height,
    calculate_baseline
)
from ._templates import RenderedComponent
from .themes import ThemeData

TABLE_FONT_SIZE = 14
TABLE_CELL_PADDING = 8
TABLE_BORDER_RADIUS = 8
TABLE_LINE_WIDTH = 1

CellValue = str | int | float | bool | None

TRUE_SYMBOL = "✓"
FALSE_SYMBOL = "✗"

CellLines = list[str]
Row = list[CellLines]

# --- Style ------------------------------------------------------------------


@dataclass(frozen=True)
class TableStyle:
    font_size: float
    cell_padding: float
    border_radius: float
    striped: bool
    row_dividers: bool
    column_dividers: bool


# --- Alignment --------------------------------------------------------------

Alignment = Literal["left", "center", "right"]


@dataclass(frozen=True)
class AlignmentRule:
    anchor: str
    text_x: Callable[[float, float, float], float]


ALIGNMENT_RULES: dict[Alignment, AlignmentRule] = {
    "left": AlignmentRule("start", lambda left, width, pad: left + pad),
    "center": AlignmentRule("middle", lambda left, width, pad: left + width / 2),
    "right": AlignmentRule("end", lambda left, width, pad: left + width - pad),
}


# --- Layout -----------------------------------------------------------------

@dataclass(frozen=True)
class TableLayout:
    left: float
    top: float
    width: float
    height: float
    column_lefts: list[float]
    column_widths: list[float]
    row_tops: list[float]
    row_heights: list[float]


def column_widths(width: float, weights: tuple[float, ...]) -> list[float]:
    total_weight = sum(weights)
    return [width * weight / total_weight for weight in weights]


def text_width(column_width: float, style: TableStyle) -> float:
    return column_width - 2 * style.cell_padding


def measure(
    left: float, top: float, width: float,
    widths: list[float], rows: list[Row], style: TableStyle,
) -> TableLayout:
    row_heights = [_row_height(row, style) for row in rows]
    return TableLayout(
        left=left,
        top=top,
        width=width,
        height=sum(row_heights),
        column_lefts=_running_positions(left, widths),
        column_widths=widths,
        row_tops=_running_positions(top, row_heights),
        row_heights=row_heights,
    )


def _row_height(row: Row, style: TableStyle) -> float:
    line_count = max([1, *(len(cell) for cell in row)])
    return line_count * calculate_line_height(style.font_size) + 2 * style.cell_padding


def _running_positions(start: float, sizes: list[float]) -> list[float]:
    positions: list[float] = []
    current = start
    for size in sizes:
        positions.append(current)
        current += size
    return positions


# --- Cell content -----------------------------------------------------------

def format_cell_value(value: CellValue) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return TRUE_SYMBOL if value else FALSE_SYMBOL
    return str(value)


def header_cells(columns: tuple[str, ...], widths: list[float], style: TableStyle) -> Row:
    return [
        [
            escape(line)
            for line in wrap_bold_text(name, style.font_size, text_width(width, style))
        ]
        for name, width in zip(columns, widths)
    ]


def body_cells(
    rows: tuple[tuple[str, ...], ...], widths: list[float],
    style: TableStyle, theme: ThemeData,
) -> list[Row]:
    return [
        [_body_cell(text, width, style, theme)
         for text, width in zip(row, widths)]
        for row in rows
    ]


def _body_cell(text: str, width: float, style: TableStyle, theme: ThemeData) -> CellLines:
    segments = parse_markup(text)
    lines = wrap_into_lines(segments, style.font_size,
                            text_width(width, style))
    return [segments_markup(line, theme) for line in lines]


# --- SVG primitives ---------------------------------------------------------

def _filled_rect(x: float, y: float, width: float, height: float, fill: str) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{height:.1f}" fill="{fill}"/>'
    )


def _line(x1: float, y1: float, x2: float, y2: float, color: str) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{TABLE_LINE_WIDTH}"/>'
    )


def _cell_lines_markup(
    contents: CellLines, x: float, top: float, font_size: float,
    fill: str, anchor: str, bold: bool,
) -> str:
    line_height = calculate_line_height(font_size)
    return "".join(
        svg_text_markup(
            x=x,
            baseline=calculate_baseline(top + index * line_height, font_size),
            font_size=font_size,
            fill=fill,
            content=content,
            bold=bold,
            anchor=anchor,
        )
        for index, content in enumerate(contents)
    )


# --- SVG layers -------------------------------------------------------------

@dataclass(frozen=True)
class TableContext:
    theme: ThemeData
    style: TableStyle
    layout: TableLayout
    rows: list[Row]
    alignments: tuple[Alignment, ...]


def _background(ctx: TableContext) -> str:
    g, theme = ctx.layout, ctx.theme
    clip_id = f"table-clip-{g.left:.0f}-{g.top:.0f}"
    clip = (
        f'<clipPath id="{clip_id}"><rect x="{g.left:.1f}" y="{g.top:.1f}" '
        f'width="{g.width:.1f}" height="{g.height:.1f}" rx="{ctx.style.border_radius:g}"/></clipPath>'
    )
    return (
        clip
        + f'<g clip-path="url(#{clip_id})">'
        + _filled_rect(g.left, g.top, g.width, g.height,
                       theme["table_background"])
        + _filled_rect(g.left, g.top, g.width,
                       g.row_heights[0], theme["table_header_background"])
        + _stripes(ctx)
        + "</g>"
    )


def _stripes(ctx: TableContext, first_striped_row: int = 2, striped_interval: int = 2) -> str:
    if not ctx.style.striped:
        return ""
    g = ctx.layout
    return "".join(
        _filled_rect(g.left, g.row_tops[i], g.width, g.row_heights[i],
                     ctx.theme["table_stripe_background"])
        for i in range(first_striped_row, len(g.row_tops), striped_interval)
    )


def _dividers(ctx: TableContext) -> str:
    g, color = ctx.layout, ctx.theme["table_divider"]
    lines: list[str] = []
    for row_index in range(len(g.row_tops) - 1):
        if row_index == 0 or ctx.style.row_dividers:
            y = g.row_tops[row_index] + g.row_heights[row_index]
            lines.append(_line(g.left, y, g.left + g.width, y, color))
    if ctx.style.column_dividers:
        for column_left in g.column_lefts[1:]:
            lines.append(_line(column_left, g.top,
                         column_left, g.top + g.height, color))
    return "".join(lines)


def _text(ctx: TableContext) -> str:
    g, theme, style = ctx.layout, ctx.theme, ctx.style
    parts: list[str] = []
    for row_index, row in enumerate(ctx.rows):
        is_header = row_index == 0
        fill = theme["table_header_text"] if is_header else theme["table_text"]
        for column_index, line_markups in enumerate(row):
            rule = ALIGNMENT_RULES[ctx.alignments[column_index]]
            parts.append(
                _cell_lines_markup(
                    line_markups,
                    x=rule.text_x(g.column_lefts[column_index],
                                  g.column_widths[column_index], style.cell_padding),
                    top=g.row_tops[row_index] + style.cell_padding,
                    font_size=style.font_size,
                    fill=fill,
                    anchor=rule.anchor,
                    bold=is_header,
                )
            )
    return "".join(parts)


def _border(ctx: TableContext) -> str:
    g, inset = ctx.layout, TABLE_LINE_WIDTH / 2
    return (
        f'<rect x="{g.left + inset:.1f}" y="{g.top + inset:.1f}" '
        f'width="{g.width - TABLE_LINE_WIDTH:.1f}" '
        f'height="{g.height - TABLE_LINE_WIDTH:.1f}" '
        f'rx="{ctx.style.border_radius:g}" fill="none" stroke="{ctx.theme["table_border"]}" '
        f'stroke-width="{TABLE_LINE_WIDTH}"/>'
    )


TableLayer = Callable[[TableContext], str]
TABLE_LAYERS: tuple[TableLayer, ...] = (_background, _dividers, _text, _border)


# --- Component --------------------------------------------------------------

@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    alignments: tuple[Alignment, ...]
    weights: tuple[float, ...]
    style: TableStyle

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        widths = column_widths(width, self.weights)
        cells = [
            header_cells(self.columns, widths, self.style),
            *body_cells(self.rows, widths, self.style, theme),
        ]
        layout = measure(left, top, width, widths, cells, self.style)
        context = TableContext(theme, self.style, layout,
                               cells, self.alignments)

        svg = "".join(layer(context) for layer in TABLE_LAYERS)
        return RenderedComponent(svg=svg, height=layout.height)
