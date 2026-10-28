from enum import Enum

ANIMATION_DURATION_SECONDS = 0.8
SLIDE_DISTANCE_PX = 24
POP_START_SCALE = 0.92


class Animation(str, Enum):
    FADE = "fade"
    SLIDE_UP = "slide-up"
    SLIDE_DOWN = "slide-down"
    SLIDE_LEFT = "slide-left"
    SLIDE_RIGHT = "slide-right"
    POP = "pop"


ENTRY_CLASS_NAME = "entry"

_START_STATES: dict[Animation, str] = {
    Animation.FADE: "opacity: 0;",
    Animation.SLIDE_UP: f"opacity: 0; transform: translateY({SLIDE_DISTANCE_PX}px);",
    Animation.SLIDE_DOWN: f"opacity: 0; transform: translateY(-{SLIDE_DISTANCE_PX}px);",
    Animation.SLIDE_LEFT: f"opacity: 0; transform: translateX({SLIDE_DISTANCE_PX}px);",
    Animation.SLIDE_RIGHT: f"opacity: 0; transform: translateX(-{SLIDE_DISTANCE_PX}px);",
    Animation.POP: f"opacity: 0; transform: scale({POP_START_SCALE});",
}

_END_STATE = "opacity: 1; transform: none;"


def build_animation_css(animation: Animation) -> str:
    return f"""
@keyframes entry {{
  from {{ {_START_STATES[animation]} }}
  to {{ {_END_STATE} }}
}}
.{ENTRY_CLASS_NAME} {{
  animation: entry {ANIMATION_DURATION_SECONDS}s ease-out both;
  transform-box: fill-box;
  transform-origin: center;
}}
@media (prefers-reduced-motion: reduce) {{
  .{ENTRY_CLASS_NAME} {{ animation: none; }}
}}
"""
