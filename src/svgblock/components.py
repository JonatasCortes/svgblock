from dataclasses import dataclass
from typing import Literal, Protocol
from xml.sax.saxutils import escape

from .image_reader import ImageData
from .line_parser import wrap_into_lines
from .markup import Style, TextSegment, parse_markup
from .themes import ThemeData

LINE_HEIGHT_RATIO = 1.5
BASELINE_RATIO = 1.1
BOLD_WEIGHT = 700

TITLE_BAR_WIDTH = 4
TITLE_BAR_HEIGHT_RATIO = 1.2
TITLE_BAR_GAP = 11

SUBSECTION_MARKER_RADIUS_RATIO = 0.18
SUBSECTION_MARKER_GAP = 8

Alignment = Literal["left", "center", "right"]
CellValue = str | int | float | bool | None

TABLE_FONT_SIZE = 14
TABLE_CELL_PADDING = 8
TABLE_BORDER_RADIUS = 8
TABLE_LINE_WIDTH = 1

TRUE_SYMBOL = "✓"
FALSE_SYMBOL = "✗"

_TEXT_ANCHORS: dict[Alignment, str] = {
    "left": "start",
    "center": "middle",
    "right": "end",
}


@dataclass(frozen=True)
class RenderedComponent:
    svg: str
    height: float


class Component(Protocol):
    def render(
        self, theme: ThemeData, left: float, top: float, width: float
    ) -> RenderedComponent: ...


@dataclass(frozen=True)
class Title:
    text: str
    font_size: float

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_height = _line_height(self.font_size)
        text_offset = TITLE_BAR_WIDTH + TITLE_BAR_GAP
        lines = _wrap_bold_text(self.text, self.font_size, width - text_offset)

        single_bar_height = self.font_size * TITLE_BAR_HEIGHT_RATIO
        bar_top = top + (line_height - single_bar_height) / 2
        bar_height = single_bar_height + (len(lines) - 1) * line_height
        bar = (
            f'<rect x="{left:.1f}" y="{bar_top:.1f}" width="{TITLE_BAR_WIDTH}" '
            f'height="{bar_height:.1f}" rx="{TITLE_BAR_WIDTH / 2:g}" fill="{theme["title_bar"]}"/>'
        )
        text = _bold_lines_markup(
            lines,
            x=left + text_offset,
            top=top,
            font_size=self.font_size,
            fill=theme["title_text"],
        )
        return RenderedComponent(svg=bar + text, height=len(lines) * line_height)


@dataclass(frozen=True)
class Subsection:
    text: str
    font_size: float

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_height = _line_height(self.font_size)
        radius = self.font_size * SUBSECTION_MARKER_RADIUS_RATIO
        text_offset = 2 * radius + SUBSECTION_MARKER_GAP
        lines = _wrap_bold_text(self.text, self.font_size, width - text_offset)

        marker = (
            f'<circle cx="{left + radius:.1f}" cy="{top + line_height / 2:.1f}" '
            f'r="{radius:.1f}" fill="{theme["subsection_marker"]}"/>'
        )
        text = _bold_lines_markup(
            lines,
            x=left + text_offset,
            top=top,
            font_size=self.font_size,
            fill=theme["subsection_text"],
        )
        return RenderedComponent(svg=marker + text, height=len(lines) * line_height)


@dataclass(frozen=True)
class Paragraph:
    text: str
    font_size: float

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        segments = parse_markup(self.text)
        lines = wrap_into_lines(segments, self.font_size, width)
        line_height = _line_height(self.font_size)
        svg = "".join(
            _text_element(
                x=left,
                baseline=_baseline(top + index * line_height, self.font_size),
                font_size=self.font_size,
                fill=theme["text"],
                content=_segments_markup(line, theme),
            )
            for index, line in enumerate(lines)
        )
        return RenderedComponent(svg=svg, height=len(lines) * line_height)


@dataclass(frozen=True)
class Image:
    image: ImageData
    requested_width: float | None = None

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        target_width = (
            self.requested_width
            if self.requested_width is not None
            else self.image.width
        )
        final_width = min(target_width, width)
        if final_width <= 0:
            return RenderedComponent(svg="", height=0)

        final_height = final_width * self.image.height / self.image.width
        svg = (
            f'<image x="{left:.1f}" y="{top:.1f}" width="{final_width:.1f}" '
            f'height="{final_height:.1f}" href="{self.image.data_uri}"/>'
        )
        return RenderedComponent(svg=svg, height=final_height)


def _line_height(font_size: float) -> float:
    return font_size * LINE_HEIGHT_RATIO


def _baseline(top: float, font_size: float) -> float:
    return top + font_size * BASELINE_RATIO


def _wrap_bold_text(text: str, font_size: float, max_width: float) -> list[str]:
    segments = [TextSegment(text=text)]
    lines = wrap_into_lines(segments, font_size, max_width, bold=True)
    return ["".join(segment.text for segment in line) for line in lines] or [""]


def _bold_lines_markup(
    lines: list[str], x: float, top: float, font_size: float, fill: str
) -> str:
    line_height = _line_height(font_size)
    return "".join(
        _text_element(
            x=x,
            baseline=_baseline(top + index * line_height, font_size),
            font_size=font_size,
            fill=fill,
            content=escape(line),
            bold=True,
        )
        for index, line in enumerate(lines)
        if line
    )


def _text_element(
    x: float,
    baseline: float,
    font_size: float,
    fill: str,
    content: str,
    bold: bool = False,
    anchor: str = "start",
) -> str:
    weight = f' font-weight="{BOLD_WEIGHT}"' if bold else ""
    anchor_attribute = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.1f}" y="{baseline:.1f}" font-size="{font_size:g}" '
        f'fill="{fill}"{weight}{anchor_attribute}>{content}</text>'
    )


def _segments_markup(segments: list[TextSegment], theme: ThemeData) -> str:
    return "".join(_segment_markup(segment, theme) for segment in segments)


def _segment_markup(segment: TextSegment, theme: ThemeData) -> str:
    content = escape(segment.text)
    if not segment.styles:
        return content

    innermost_style = segment.styles[-1]
    attributes = [f'fill="{_style_color(theme, innermost_style)}"']
    if segment.is_bold:
        attributes.append(f'font-weight="{BOLD_WEIGHT}"')
    if Style.ITALIC in segment.styles:
        attributes.append('font-style="italic"')
    decorations = _text_decorations(segment.styles)
    if decorations:
        attributes.append(f'text-decoration="{decorations}"')
    return f'<tspan {" ".join(attributes)}>{content}</tspan>'


def _style_color(theme: ThemeData, style: Style) -> str:
    colors: dict[Style, str] = {
        Style.HIGHLIGHT: theme["highlight"],
        Style.UNDERLINE: theme["underline"],
        Style.STRIKETHROUGH: theme["strikethrough"],
        Style.ITALIC: theme["italic"],
    }
    return colors[style]


def _text_decorations(styles: tuple[Style, ...]) -> str:
    decorations: list[str] = []
    if Style.UNDERLINE in styles:
        decorations.append("underline")
    if Style.STRIKETHROUGH in styles:
        decorations.append("line-through")
    return " ".join(decorations)


def format_cell_value(value: CellValue) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return TRUE_SYMBOL if value else FALSE_SYMBOL
    return str(value)


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    font_size: float
    cell_padding: float
    border_radius: float
    alignments: tuple[Alignment, ...]
    weights: tuple[float, ...]
    striped: bool
    row_dividers: bool
    column_dividers: bool
    highlighted_words: tuple[str, ...] = ()

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        total_weight = sum(self.weights)
        column_widths = [width * weight /
                         total_weight for weight in self.weights]
        column_lefts = _running_positions(left, column_widths)

        header = [
            [
                escape(line)
                for line in _wrap_bold_text(
                    name, self.font_size, column_width - 2 * self.cell_padding
                )
            ]
            for name, column_width in zip(self.columns, column_widths)
        ]
        body = [
            [
                self._body_cell(text, theme, column_width)
                for text, column_width in zip(row, column_widths)
            ]
            for row in self.rows
        ]
        table_rows = [header, *body]

        row_heights = [self._row_height(row) for row in table_rows]
        row_tops = _running_positions(top, row_heights)
        height = sum(row_heights)

        svg = (
            self._background_markup(
                theme, left, top, width, height, row_tops, row_heights)
            + self._dividers_markup(theme, left, top, width,
                                    height, column_lefts, row_tops, row_heights)
            + self._text_markup(theme, table_rows,
                                column_lefts, column_widths, row_tops)
            + self._border_markup(theme, left, top, width, height)
        )
        return RenderedComponent(svg=svg, height=height)

    def _body_cell(self, text: str, theme: ThemeData, column_width: float) -> list[str]:
        segments = parse_markup(text)
        lines = wrap_into_lines(segments, self.font_size,
                                column_width - 2 * self.cell_padding)
        return [_segments_markup(line, theme) for line in lines]

    def _row_height(self, row: list[list[str]]) -> float:
        line_count = max([1, *(len(cell) for cell in row)])
        return line_count * _line_height(self.font_size) + 2 * self.cell_padding

    def _background_markup(
        self, theme: ThemeData, left: float, top: float, width: float, height: float,
        row_tops: list[float], row_heights: list[float],
    ) -> str:
        clip_id = f"table-clip-{left:.0f}-{top:.0f}"
        clip = (
            f'<clipPath id="{clip_id}"><rect x="{left:.1f}" y="{top:.1f}" '
            f'width="{width:.1f}" height="{height:.1f}" rx="{self.border_radius:g}"/></clipPath>'
        )
        stripes = ""
        if self.striped:
            stripes = "".join(
                _filled_rect(left, row_tops[index], width, row_heights[index],
                             theme["table_stripe_background"])
                for index in range(2, len(row_tops), 2)
            )
        return (
            clip
            + f'<g clip-path="url(#{clip_id})">'
            + _filled_rect(left, top, width, height,
                           theme["table_background"])
            + _filled_rect(left, top, width,
                           row_heights[0], theme["table_header_background"])
            + stripes
            + "</g>"
        )

    def _dividers_markup(
        self, theme: ThemeData, left: float, top: float, width: float, height: float,
        column_lefts: list[float], row_tops: list[float], row_heights: list[float],
    ) -> str:
        color = theme["table_divider"]
        lines: list[str] = []
        for row_index in range(len(row_tops) - 1):
            if row_index == 0 or self.row_dividers:
                y = row_tops[row_index] + row_heights[row_index]
                lines.append(_line(left, y, left + width, y, color))
        if self.column_dividers:
            for column_left in column_lefts[1:]:
                lines.append(
                    _line(column_left, top, column_left, top + height, color))
        return "".join(lines)

    def _text_markup(
        self, theme: ThemeData, table_rows: list[list[list[str]]],
        column_lefts: list[float], column_widths: list[float], row_tops: list[float],
    ) -> str:
        parts: list[str] = []
        for row_index, row in enumerate(table_rows):
            is_header = row_index == 0
            fill = theme["table_header_text"] if is_header else theme["table_text"]
            for column_index, line_markups in enumerate(row):
                alignment = self.alignments[column_index]
                parts.append(
                    _cell_lines_markup(
                        line_markups,
                        x=self._text_x(
                            alignment, column_lefts[column_index], column_widths[column_index]),
                        top=row_tops[row_index] + self.cell_padding,
                        font_size=self.font_size,
                        fill=fill,
                        anchor=_TEXT_ANCHORS[alignment],
                        bold=is_header,
                    )
                )
        return "".join(parts)

    def _text_x(self, alignment: Alignment, column_left: float, column_width: float) -> float:
        if alignment == "left":
            return column_left + self.cell_padding
        if alignment == "right":
            return column_left + column_width - self.cell_padding
        return column_left + column_width / 2

    def _border_markup(
        self, theme: ThemeData, left: float, top: float, width: float, height: float
    ) -> str:
        inset = TABLE_LINE_WIDTH / 2
        return (
            f'<rect x="{left + inset:.1f}" y="{top + inset:.1f}" '
            f'width="{width - TABLE_LINE_WIDTH:.1f}" height="{height - TABLE_LINE_WIDTH:.1f}" '
            f'rx="{self.border_radius:g}" fill="none" stroke="{theme["table_border"]}" '
            f'stroke-width="{TABLE_LINE_WIDTH}"/>'
        )


def _running_positions(start: float, sizes: list[float]) -> list[float]:
    positions: list[float] = []
    current = start
    for size in sizes:
        positions.append(current)
        current += size
    return positions


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
    contents: list[str], x: float, top: float, font_size: float,
    fill: str, anchor: str, bold: bool,
) -> str:
    line_height = _line_height(font_size)
    return "".join(
        _text_element(
            x=x,
            baseline=_baseline(top + index * line_height, font_size),
            font_size=font_size,
            fill=fill,
            content=content,
            bold=bold,
            anchor=anchor,
        )
        for index, content in enumerate(contents)
    )


DIVIDER_THICKNESS = 2
DIVIDER_COVERAGE = 1


@dataclass(frozen=True)
class Divider:
    coverage: float

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_width = width * self.coverage
        line_left = left + (width - line_width) / 2
        svg = (
            f'<rect x="{line_left:.1f}" y="{top:.1f}" width="{line_width:.1f}" '
            f'height="{DIVIDER_THICKNESS}" rx="{DIVIDER_THICKNESS / 2:g}" '
            f'fill="{theme["divider"]}"/>'
        )
        return RenderedComponent(svg=svg, height=DIVIDER_THICKNESS)
