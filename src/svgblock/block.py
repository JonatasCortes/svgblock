from collections.abc import Sequence
from pathlib import Path

from svgblock.animations import ENTRY_CLASS_NAME, Animation, build_animation_css
from svgblock.components import Component, Paragraph, Subsection, Title
from svgblock.frame import build_frame
from svgblock.themes import THEMES, Theme

DEFAULT_THEME_NAME = "red"
DEFAULT_WIDTH = 800
DEFAULT_ANIMATION = Animation.FADE

TITLE_FONT_SIZE = 20
SUBSECTION_FONT_SIZE = 17
TEXT_FONT_SIZE = 16

BLOCK_PADDING = 24
COMPONENT_GAP = 10

FONT_FAMILY = "Arial, Helvetica, sans-serif"


class Block:
    def __init__(
        self,
        theme: str = DEFAULT_THEME_NAME,
        width: float = DEFAULT_WIDTH,
        animation: Animation | str = DEFAULT_ANIMATION,
    ) -> None:
        self._theme = _find_theme(theme)
        self._width = width
        self._animation = _parse_animation(animation)
        self._components: list[Component] = []

    def title(self, text: str, font_size: float = TITLE_FONT_SIZE) -> "Block":
        self._components.append(Title(text, font_size))
        return self

    def subsection(self, text: str, font_size: float = SUBSECTION_FONT_SIZE) -> "Block":
        self._components.append(Subsection(text, font_size))
        return self

    def text(
        self,
        text: str,
        font_size: float = TEXT_FONT_SIZE,
        highlight: Sequence[str] = (),
    ) -> "Block":
        self._components.append(Paragraph(text, font_size, tuple(highlight)))
        return self

    def render(self) -> str:
        content, content_height = self._render_components()
        height = content_height + BLOCK_PADDING
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self._width:g}" '
            f'height="{height:g}" viewBox="0 0 {self._width:g} {height:g}">'
            f"<style>{build_animation_css(self._animation)}</style>"
            f'<g class="{ENTRY_CLASS_NAME}">'
            f"{build_frame(self._theme, self._width, height)}"
            f'<g font-family="{FONT_FAMILY}">{content}</g>'
            "</g></svg>"
        )

    def save(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(), encoding="utf-8")

    def _render_components(self) -> tuple[str, float]:
        content_width = self._width - 2 * BLOCK_PADDING
        top = BLOCK_PADDING
        parts: list[str] = []
        for index, component in enumerate(self._components):
            if index > 0:
                top += COMPONENT_GAP
            rendered = component.render(
                self._theme, BLOCK_PADDING, top, content_width)
            parts.append(rendered.svg)
            top += rendered.height
        return "".join(parts), top


def _find_theme(name: str) -> Theme:
    try:
        return THEMES[name]
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
