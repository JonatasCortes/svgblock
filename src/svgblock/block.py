from pathlib import Path
from .animations import BaseAnimation, build_animation_css
from .composition import Composer
from .frame import build_frame
from .themes import Theme, ThemeData


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

    def render(self) -> str:
        if self._animation is None:
            growth = 1.0
            left = top = right = bottom = 0.0
        else:
            growth = self._animation.max_scale
            left, top, right, bottom = self._animation.overflow

        available_width = self._width - left - right
        if available_width <= 0:
            raise ValueError(
                f"Animation moves the block {left + right:g}px sideways, "
                f"which does not fit in width {self._width:g}."
            )

        block_width = available_width / growth
        content_width = block_width - 2 * self._padding
        rendered = self._render_components(
            self._theme, self._padding, self._padding, content_width
        )
        block_height = rendered.height + 2 * self._padding

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
