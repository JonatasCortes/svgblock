import hashlib

from ._data import ThemeData

_BACKGROUND_GRADIENT_ID_PREFIX = "background"
_BORDER_GRADIENT_ID_PREFIX = "border"

_BORDER_WIDTH = 2
_CORNER_RADIUS = 15
_BACKGROUND_GLOW_RADIUS = 0.7


def build_frame(theme: ThemeData, width: float, height: float) -> str:
    _validate_size(width, height)
    background_id = _gradient_id(
        _BACKGROUND_GRADIENT_ID_PREFIX,
        theme["background_center"], theme["background_edge"])
    border_id = _gradient_id(
        _BORDER_GRADIENT_ID_PREFIX,
        theme["border_start"], theme["border_end"])
    return (
        _build_gradient_definitions(theme, background_id, border_id)
        + _build_rectangle(width, height,
                           fill=f"url(#{background_id})", stroke="none")
        + _build_rectangle(width, height, fill="none",
                           stroke=f"url(#{border_id})")
    )


def _gradient_id(prefix: str, *colors: str) -> str:
    digest = hashlib.sha256("|".join(colors).encode()).hexdigest()
    return f"{prefix}-{digest[:12]}"


def _validate_size(width: float, height: float) -> None:
    if not (width > _BORDER_WIDTH and height > _BORDER_WIDTH):
        raise ValueError(
            f"Frame size {width:g}x{height:g} must be larger than the "
            f"border width ({_BORDER_WIDTH}) in both dimensions"
        )


def _build_gradient_definitions(
    theme: ThemeData, background_id: str, border_id: str
) -> str:
    return (
        "<defs>"
        f'<radialGradient id="{background_id}" cx="0.5" cy="0.5" '
        f'r="{_BACKGROUND_GLOW_RADIUS}">'
        f'<stop offset="0" stop-color="{theme["background_center"]}"/>'
        f'<stop offset="1" stop-color="{theme["background_edge"]}"/>'
        "</radialGradient>"
        f'<linearGradient id="{border_id}" x1="0" y1="0" x2="1" y2="1">'
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
