from pathlib import Path

from .animations import ENTRY_CLASS_NAME, Animation, build_animation_css
from .composition import Composer
from .frame import build_frame
from .themes import THEMES, Theme

DEFAULT_THEME_NAME = "red"
DEFAULT_WIDTH = 800
DEFAULT_ANIMATION = Animation.FADE

BLOCK_PADDING = 24

FONT_FAMILY = "Arial, Helvetica, sans-serif"


class Block(Composer):
    def __init__(
        self,
        theme: str = DEFAULT_THEME_NAME,
        width: float = DEFAULT_WIDTH,
        animation: Animation | str = DEFAULT_ANIMATION,
    ) -> None:
        super().__init__()
        self._theme = _find_theme(theme)
        self._width = width
        self._animation = _parse_animation(animation)

    def render(self) -> str:
        content_width = self._width - 2 * BLOCK_PADDING
        rendered = self._render_components(
            self._theme, BLOCK_PADDING, BLOCK_PADDING, content_width
        )
        height = rendered.height + 2 * BLOCK_PADDING
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self._width:g}" '
            f'height="{height:g}" viewBox="0 0 {self._width:g} {height:g}">'
            f"<style>{build_animation_css(self._animation)}</style>"
            f'<g class="{ENTRY_CLASS_NAME}">'
            f"{build_frame(self._theme, self._width, height)}"
            f'<g font-family="{FONT_FAMILY}">{rendered.svg}</g>'
            "</g></svg>"
        )

    def save(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(), encoding="utf-8")


def _find_theme(name: str) -> Theme:
    try:
        return THEMES[name.replace(" ", "").replace("-", "").replace("_", "")]
    except KeyError:
        raise ValueError(
            f"Unknown theme {name!r}. Available: {', '.join(THEMES)}") from None


def _parse_animation(animation: Animation | str) -> Animation:
    try:
        return Animation(animation)
    except ValueError:
        options = ", ".join(option.value for option in Animation)
        raise ValueError(
            f"Unknown animation {animation!r}. Available: {options}") from None
