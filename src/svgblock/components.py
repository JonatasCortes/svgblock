from dataclasses import dataclass
from xml.sax.saxutils import escape

from svgblock.line_parser import wrap_into_lines
from svgblock.markup import TextSegment, parse_highlights
from svgblock.themes import Theme

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


@dataclass(frozen=True)
class Title:
    text: str
    font_size: float

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
        line_height = _line_height(self.font_size)
        bar_height = self.font_size * TITLE_BAR_HEIGHT_RATIO
        bar_top = top + (line_height - bar_height) / 2
        bar = (
            f'<rect x="{left:.1f}" y="{bar_top:.1f}" width="{TITLE_BAR_WIDTH}" '
            f'height="{bar_height:.1f}" rx="{TITLE_BAR_WIDTH / 2:g}" fill="{theme["title_bar"]}"/>'
        )
        text = _text_element(
            x=left + TITLE_BAR_WIDTH + TITLE_BAR_GAP,
            baseline=_baseline(top, self.font_size),
            font_size=self.font_size,
            fill=theme["title_text"],
            content=escape(self.text),
            bold=True,
        )
        return RenderedComponent(svg=bar + text, height=line_height)


@dataclass(frozen=True)
class Subsection:
    text: str
    font_size: float

    def render(self, theme: Theme, left: float, top: float, width: float) -> RenderedComponent:
        line_height = _line_height(self.font_size)
        radius = self.font_size * SUBSECTION_MARKER_RADIUS_RATIO
        marker = (
            f'<circle cx="{left + radius:.1f}" cy="{top + line_height / 2:.1f}" '
            f'r="{radius:.1f}" fill="{theme["subsection_marker"]}"/>'
        )
        text = _text_element(
            x=left + 2 * radius + SUBSECTION_MARKER_GAP,
            baseline=_baseline(top, self.font_size),
            font_size=self.font_size,
            fill=theme["subsection_text"],
            content=escape(self.text),
            bold=True,
        )
        return RenderedComponent(svg=marker + text, height=line_height)


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


Component = Title | Subsection | Paragraph


def _line_height(font_size: float) -> float:
    return font_size * LINE_HEIGHT_RATIO


def _baseline(top: float, font_size: float) -> float:
    return top + font_size * BASELINE_RATIO


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
