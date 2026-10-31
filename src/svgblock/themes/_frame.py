from ._data import ThemeData

_BACKGROUND_GRADIENT_ID = "background"
_BORDER_GRADIENT_ID = "border"

_BORDER_WIDTH = 2
_CORNER_RADIUS = 15
_BACKGROUND_GLOW_RADIUS = 0.7


def build_frame(theme: ThemeData, width: float, height: float) -> str:
    return (
        _build_gradient_definitions(theme)
        + _build_rectangle(width, height,
                           fill=f"url(#{_BACKGROUND_GRADIENT_ID})", stroke="none")
        + _build_rectangle(width, height, fill="none",
                           stroke=f"url(#{_BORDER_GRADIENT_ID})")
    )


def _build_gradient_definitions(theme: ThemeData) -> str:
    return (
        "<defs>"
        f'<radialGradient id="{_BACKGROUND_GRADIENT_ID}" cx="0.5" cy="0.5" '
        f'r="{_BACKGROUND_GLOW_RADIUS}">'
        f'<stop offset="0" stop-color="{theme["background_center"]}"/>'
        f'<stop offset="1" stop-color="{theme["background_edge"]}"/>'
        "</radialGradient>"
        f'<linearGradient id="{_BORDER_GRADIENT_ID}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{theme["border_start"]}"/>'
        f'<stop offset="1" stop-color="{theme["border_end"]}"/>'
        "</linearGradient>"
        "</defs>"
    )


def _build_rectangle(width: float, height: float, fill: str, stroke: str) -> str:
    inset = _BORDER_WIDTH / 2
    return (
        f'<rect x="{inset:g}" y="{inset:g}" '
        f'width="{width - _BORDER_WIDTH:g}" height="{height - _BORDER_WIDTH:g}" '
        f'rx="{_CORNER_RADIUS}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{_BORDER_WIDTH}"/>'
    )
