from svgblock.themes import Theme

BACKGROUND_GRADIENT_ID = "background"
BORDER_GRADIENT_ID = "border"

BORDER_WIDTH = 2
CORNER_RADIUS = 15
BACKGROUND_GLOW_RADIUS = 0.7


def build_frame(theme: Theme, width: float, height: float) -> str:
    return (
        _build_gradient_definitions(theme)
        + _build_rectangle(width, height,
                           fill=f"url(#{BACKGROUND_GRADIENT_ID})", stroke="none")
        + _build_rectangle(width, height, fill="none",
                           stroke=f"url(#{BORDER_GRADIENT_ID})")
    )


def _build_gradient_definitions(theme: Theme) -> str:
    return (
        "<defs>"
        f'<radialGradient id="{BACKGROUND_GRADIENT_ID}" cx="0.5" cy="0.5" '
        f'r="{BACKGROUND_GLOW_RADIUS}">'
        f'<stop offset="0" stop-color="{theme["background_center"]}"/>'
        f'<stop offset="1" stop-color="{theme["background_edge"]}"/>'
        "</radialGradient>"
        f'<linearGradient id="{BORDER_GRADIENT_ID}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{theme["border_start"]}"/>'
        f'<stop offset="1" stop-color="{theme["border_end"]}"/>'
        "</linearGradient>"
        "</defs>"
    )


def _build_rectangle(width: float, height: float, fill: str, stroke: str) -> str:
    inset = BORDER_WIDTH / 2
    return (
        f'<rect x="{inset:g}" y="{inset:g}" '
        f'width="{width - BORDER_WIDTH:g}" height="{height - BORDER_WIDTH:g}" '
        f'rx="{CORNER_RADIUS}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{BORDER_WIDTH}"/>'
    )
