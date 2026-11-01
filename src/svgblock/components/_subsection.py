from dataclasses import dataclass, field
from .text import wrap_bold_text, calculate_line_height
from ._stylized_markup import bold_lines_markup
from ._templates import RenderedComponent
from .themes import ThemeData


@dataclass(frozen=True)
class Subsection:
    text: str
    font_size: float
    SUBSECTION_MARKER_RADIUS_RATIO: float = field(default=0.18, init=False)
    SUBSECTION_MARKER_GAP: int = field(default=8, init=False)

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_height = calculate_line_height(self.font_size)
        radius = self.font_size * self.SUBSECTION_MARKER_RADIUS_RATIO
        text_offset = 2 * radius + self.SUBSECTION_MARKER_GAP
        lines = wrap_bold_text(self.text, self.font_size, width - text_offset)

        marker = (
            f'<circle cx="{left + radius:.1f}" cy="{top + line_height / 2:.1f}" '
            f'r="{radius:.1f}" fill="{theme["subsection_marker"]}"/>'
        )
        text = bold_lines_markup(
            lines,
            x=left + text_offset,
            top=top,
            font_size=self.font_size,
            fill=theme["subsection_text"],
        )
        return RenderedComponent(svg=marker + text, height=len(lines) * line_height)
