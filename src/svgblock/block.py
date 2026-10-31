from pathlib import Path
from .animations import BaseAnimation, build_animation_css
from .composition import Composer
from .frame import build_frame
from .themes import Theme, ThemeData

MARGIN_TOLERANCE = 0.5
MAX_LAYOUT_PASSES = 8


class Block(Composer):

    def __init__(
        self,
        theme: ThemeData | Theme = Theme.NEON,
        width: float = 800,
        padding: int = 24,
        animation: BaseAnimation | None = None,
        hide_frame: bool = False,
    ) -> None:
        super().__init__()
        if isinstance(theme, Theme):
            theme = theme.value
        self._theme = theme
        self._width = width
        self._padding = padding if not hide_frame else 0
        self._animation = animation
        self._hide_frame = hide_frame

    def _layout(self, growth: float, margins: tuple[float, ...]):
        left, _, right, _ = margins
        available_width = self._width - left - right
        if available_width <= 0:
            raise ValueError(
                f"Animation needs {left + right:g}px of side margin, "
                f"which does not fit in width {self._width:g}."
            )
        block_width = available_width / growth
        content_width = block_width - 2 * self._padding
        rendered = self._render_components(
            self._theme, self._padding, self._padding, content_width
        )
        block_height = rendered.height + 2 * self._padding
        return block_width, block_height, rendered

    def render(self) -> str:
        if self._animation is None:
            growth = 1.0
            margins: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)
            block_width, block_height, rendered = self._layout(growth, margins)
        else:
            growth = self._animation.max_scale
            margins: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)
            for _ in range(MAX_LAYOUT_PASSES):
                block_width, block_height, rendered = self._layout(
                    growth, margins)
                needed = self._animation.margins(block_width, block_height)
                merged = tuple(max(a, b) for a, b in zip(margins, needed))
                stable = all(
                    abs(new - old) <= MARGIN_TOLERANCE
                    for new, old in zip(merged, margins)
                )
                margins = merged
                if stable:
                    break
            else:
                block_width, block_height, rendered = self._layout(
                    growth, margins)

        left, top, _, bottom = margins
        scaled_height = block_height * growth
        height = scaled_height + top + bottom

        margin_x = left + (block_width * growth - block_width) / 2
        margin_y = top + (scaled_height - block_height) / 2

        frame_markup = (
            build_frame(self._theme, block_width, block_height)
            if not self._hide_frame else ""
        )
        if self._animation is None:
            style = ""
            open_group = "<g>"
        else:
            css = build_animation_css(self._animation)
            style = f"<style>{css}</style>"
            open_group = f'<g class="{self._animation.css_name}">'

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self._width:g}" '
            f'height="{height:g}" viewBox="0 0 {self._width:g} {height:g}">'
            f"{style}"
            f'<g transform="translate({margin_x:g} {margin_y:g})">'
            f"{open_group}"
            f"{frame_markup}"
            f'<g font-family="Arial, Helvetica, sans-serif">{rendered.svg}</g>'
            "</g></g></svg>"
        )

    def save(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(), encoding="utf-8")
