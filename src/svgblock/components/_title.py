from dataclasses import dataclass, field
from .themes import ThemeData
from .text import wrap_bold_text, calculate_line_height
from ._stylized_markup import bold_lines_markup
from ._templates import RenderedComponent


@dataclass(frozen=True)
class Title:
    text: str
    font_size: float
    TITLE_BAR_WIDTH: int = field(default=4, init=False)
    TITLE_BAR_HEIGHT_RATIO: float = field(default=1.2, init=False)
    TITLE_BAR_GAP: int = field(default=11, init=False)

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_height = calculate_line_height(self.font_size)
        text_offset = self.TITLE_BAR_WIDTH + self.TITLE_BAR_GAP
        lines = wrap_bold_text(self.text, self.font_size, width - text_offset)

        single_bar_height = self.font_size * self.TITLE_BAR_HEIGHT_RATIO
        bar_top = top + (line_height - single_bar_height) / 2
        bar_height = single_bar_height + (len(lines) - 1) * line_height
        bar = (
            f'<rect x="{left:.1f}" y="{bar_top:.1f}" width="{self.TITLE_BAR_WIDTH}" '
            f'height="{bar_height:.1f}" rx="{self.TITLE_BAR_WIDTH / 2:g}" fill="{theme["title_bar"]}"/>'
        )
        text = bold_lines_markup(
            lines,
            x=left + text_offset,
            top=top,
            font_size=self.font_size,
            fill=theme["title_text"],
        )
        return RenderedComponent(svg=bar + text, height=len(lines) * line_height)
