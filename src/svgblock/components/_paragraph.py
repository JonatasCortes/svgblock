from dataclasses import dataclass
from ._templates import RenderedComponent
from ._stylized_markup import svg_text_markup, segments_markup
from .text import parse_markup, wrap_into_lines, calculate_line_height, calculate_baseline
from .themes import ThemeData


@dataclass(frozen=True)
class Paragraph:
    text: str
    font_size: float

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        segments = parse_markup(self.text)
        lines = wrap_into_lines(segments, self.font_size, width)
        line_height = calculate_line_height(self.font_size)
        svg = "".join(
            svg_text_markup(
                x=left,
                baseline=calculate_baseline(top + index * line_height,
                                            self.font_size),
                font_size=self.font_size,
                fill=theme["text"],
                content=segments_markup(line, theme),
            )
            for index, line in enumerate(lines)
        )
        return RenderedComponent(svg=svg, height=len(lines) * line_height)
