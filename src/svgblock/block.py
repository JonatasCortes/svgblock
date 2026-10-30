from pathlib import Path
from .animations import Animation, BaseAnimation, build_animation_css
from .composition import Composer
from .frame import build_frame
from .themes import Theme, ThemeData


class Block(Composer):

    def __init__(
        self,
        theme: ThemeData | Theme = Theme.NEON,
        width: float = 800,
        padding: int = 24,
        animation: BaseAnimation | str | None = None,
        visible: bool = True,
    ) -> None:
        super().__init__()
        if isinstance(theme, Theme):
            theme = theme.value
        self._theme = theme
        self._width = width
        self._padding = padding if visible else 0
        self._animation = Animation.resolve(animation)
        self._visible = visible

    def render(self) -> str:
        growth = 1.0 if self._animation is None else self._animation.max_scale

        block_width = self._width / growth
        content_width = block_width - 2 * self._padding
        rendered = self._render_components(
            self._theme, self._padding, self._padding, content_width
        )
        block_height = rendered.height + 2 * self._padding
        height = block_height * growth

        margin_x = (self._width - block_width) / 2
        margin_y = (height - block_height) / 2

        frame_markup = (
            build_frame(self._theme, block_width, block_height)
            if self._visible else ""
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
