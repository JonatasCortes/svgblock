from pathlib import Path

from .animations import (
    ENTRY_CLASS_NAME,
    Animation,
    build_animation_css,
    validate_animation_loop,
)
from .composition import Composer
from .frame import build_frame
from .themes import Theme, ThemeData

DEFAULT_THEME_NAME = "red"
DEFAULT_WIDTH = 800
DEFAULT_ANIMATION = None

BLOCK_PADDING = 24

FONT_FAMILY = "Arial, Helvetica, sans-serif"


class Block(Composer):

    def __init__(
        self,
        theme: ThemeData | Theme = Theme.NEON,
        width: float = DEFAULT_WIDTH,
        animation: Animation | str | None = DEFAULT_ANIMATION,
        frame: bool = True,
        animation_loop: float | None = None,
    ) -> None:
        super().__init__()
        if isinstance(theme, Theme):
            theme = theme.value
        self._theme = theme
        self._width = width
        self._animation = _parse_animation(animation)
        if animation_loop is not None and self._animation is None:
            raise ValueError(
                "animation_loop needs an animation. Pass animation=... too.")
        validate_animation_loop(animation_loop)
        self._animation_loop = animation_loop
        self._frame = frame

    def render(self) -> str:
        padding = BLOCK_PADDING if self._frame else 0
        content_width = self._width - 2 * padding
        rendered = self._render_components(
            self._theme, padding, padding, content_width
        )
        height = rendered.height + 2 * padding
        frame_markup = (
            build_frame(self._theme, self._width,
                        height) if self._frame else ""
        )
        if self._animation is None:
            style = ""
            open_group = "<g>"
        else:
            css = build_animation_css(self._animation, self._animation_loop)
            style = f"<style>{css}</style>"
            open_group = f'<g class="{ENTRY_CLASS_NAME}">'

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self._width:g}" '
            f'height="{height:g}" viewBox="0 0 {self._width:g} {height:g}">'
            f"{style}"
            f"{open_group}"
            f"{frame_markup}"
            f'<g font-family="{FONT_FAMILY}">{rendered.svg}</g>'
            "</g></svg>"
        )

    def save(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(), encoding="utf-8")


def _parse_animation(animation: Animation | str | None) -> Animation | None:
    if animation is None:
        return None
    try:
        return Animation(animation)
    except ValueError:
        options = ", ".join(option.value for option in Animation)
        raise ValueError(
            f"Unknown animation {animation!r}. Available: {options}") from None
