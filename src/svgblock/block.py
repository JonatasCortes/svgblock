import math
from pathlib import Path

from .components._composer import Composer
from .components.animations import BaseAnimation, build_animation_css
from .components.themes import Theme, ThemeData, build_frame


def _format_number(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


class Block(Composer):
    _margin_tolerance: float = 0.5
    _max_layout_passes: int = 8

    def __init__(
        self,
        theme: ThemeData | Theme = Theme.NEON,
        width: float = 800,
        padding: int = 24,
        animation: BaseAnimation | None = None,
        hide_frame: bool = False,
    ) -> None:
        super().__init__()
        if not math.isfinite(width) or width <= 0:
            raise ValueError(
                f"Block width must be a positive finite number, got {width!r}."
            )
        if not math.isfinite(padding) or padding < 0:
            raise ValueError(
                f"Block padding must be a non-negative finite number, got {padding!r}."
            )
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
        if content_width <= 0:
            raise ValueError(
                f"Padding of {self._padding:g}px on each side leaves no room "
                f"for content in a block of width {block_width:g}."
            )
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
            margins = (0.0, 0.0, 0.0, 0.0)
            for _ in range(self._max_layout_passes):
                block_width, block_height, rendered = self._layout(
                    growth, margins)
                needed = self._animation.margins(block_width, block_height)
                merged = tuple(max(a, b) for a, b in zip(margins, needed))
                stable = all(
                    abs(new - old) <= self._margin_tolerance
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

        width_text = _format_number(self._width)
        height_text = _format_number(height)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_text}" '
            f'height="{height_text}" viewBox="0 0 {width_text} {height_text}">'
            f"{style}"
            f'<g transform="translate({_format_number(margin_x)} '
            f'{_format_number(margin_y)})">'
            f"{open_group}"
            f"{frame_markup}"
            f'<g font-family="Arial, Helvetica, sans-serif">{rendered.svg}</g>'
            "</g></g></svg>"
        )

    def save(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(), encoding="utf-8")
