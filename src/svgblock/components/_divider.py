from dataclasses import dataclass, field
from .themes import ThemeData
from ._templates import RenderedComponent


@dataclass(frozen=True)
class Divider:
    coverage: float
    DEFAULT_THICKNESS: int = field(default=2, init=False)

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        line_width = width * self.coverage
        line_left = left + (width - line_width) / 2
        svg = (
            f'<rect x="{line_left:.1f}" y="{top:.1f}" width="{line_width:.1f}" '
            f'height="{self.DEFAULT_THICKNESS}" rx="{self.DEFAULT_THICKNESS / 2:g}" '
            f'fill="{theme["divider"]}"/>'
        )
        return RenderedComponent(svg=svg, height=self.DEFAULT_THICKNESS)
