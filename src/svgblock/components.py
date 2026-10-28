from dataclasses import dataclass
from typing import Protocol
from xml.sax.saxutils import escape

from .image_reader import ImageData
from .line_parser import wrap_into_lines
from .markup import TextSegment, parse_highlights
from .themes import Theme

LINE_HEIGHT_RATIO = 1.5
BASELINE_RATIO = 1.1
BOLD_WEIGHT = 700

TITLE_BAR_WIDTH = 4
TITLE_BAR_HEIGHT_RATIO = 1.2
TITLE_BAR_GAP = 11

SUBSECTION_MARKER_RADIUS_RATIO = 0.18
SUBSECTION_MARKER_GAP = 8


@dataclass(frozen=True)
class RenderedComponent:
    svg: str
    height: float


class Component(Protocol):
    def render(
        self, theme: Theme, left: float, top: float, width: float
    ) -> RenderedComponent: ...


@dataclass(frozen=True)
class Title:
    text: str
    font_size: float

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
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

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
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
    highlighted_words: tuple[str, ...] = ()

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
        segments = parse_highlights(self.text, self.highlighted_words)
        lines = wrap_into_lines(segments, self.font_size, width)
        line_height = _line_height(self.font_size)
        svg = "".join(
            _text_element(
                x=left,
                baseline=_baseline(top + index * line_height, self.font_size),
                font_size=self.font_size,
                fill=theme["text"],
                content=_segments_markup(line, theme["highlight"]),
            )
            for index, line in enumerate(lines)
        )
        return RenderedComponent(svg=svg, height=len(lines) * line_height)


@dataclass(frozen=True)
class Image:
    image: ImageData
    requested_width: float | None = None

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
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
    segments = [TextSegment(text=text, highlighted=False)]
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
    x: float, baseline: float, font_size: float, fill: str, content: str, bold: bool = False
) -> str:
    weight = f' font-weight="{BOLD_WEIGHT}"' if bold else ""
    return (
        f'<text x="{x:.1f}" y="{baseline:.1f}" font-size="{font_size:g}" '
        f'fill="{fill}"{weight}>{content}</text>'
    )


def _segments_markup(segments: list[TextSegment], highlight_color: str) -> str:
    return "".join(
        f'<tspan fill="{highlight_color}" font-weight="{BOLD_WEIGHT}">{escape(segment.text)}</tspan>'
        if segment.highlighted
        else escape(segment.text)
        for segment in segments
    )
