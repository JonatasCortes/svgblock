from dataclasses import dataclass
from ._image_reader import ImageData
from .themes import ThemeData
from ._templates import RenderedComponent


@dataclass(frozen=True)
class Image:
    image: ImageData
    requested_width: float | None = None

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        target_width = self.requested_width or self.image.width
        final_width = min(target_width, width)
        if final_width <= 0:
            return RenderedComponent(svg="", height=0)

        final_height = final_width * self.image.height / self.image.width
        svg = (
            f'<image x="{left:.1f}" y="{top:.1f}" width="{final_width:.1f}" '
            f'height="{final_height:.1f}" href="{self.image.data_uri}"/>'
        )
        return RenderedComponent(svg=svg, height=final_height)
