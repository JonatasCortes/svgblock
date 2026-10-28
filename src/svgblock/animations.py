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


def validate_animation_loop(animation_loop: float | None) -> None:
    if animation_loop is None:
        return
    if animation_loop <= ANIMATION_DURATION_SECONDS:
        raise ValueError(
            f"animation_loop must be greater than {ANIMATION_DURATION_SECONDS} "
            f"seconds (the duration of the animation), got {animation_loop!r}."
        )


def build_animation_css(animation: Animation, loop: float | None = None) -> str:
    if loop is None:
        keyframes = (
            f"from {{ {_START_STATES[animation]} }} "
            f"to {{ {_END_STATE} }}"
        )
        rule = f"animation: entry {ANIMATION_DURATION_SECONDS}s ease-out both;"
    else:
        percent = ANIMATION_DURATION_SECONDS / loop * 100
        keyframes = (
            f"0% {{ {_START_STATES[animation]} }} "
            f"{percent:.3f}% {{ {_END_STATE} }} "
            f"100% {{ {_END_STATE} }}"
        )
        rule = f"animation: entry {loop:g}s ease-out infinite;"

    return f"""
@keyframes entry {{
  {keyframes}
}}
.{ENTRY_CLASS_NAME} {{
  {rule}
  transform-box: fill-box;
  transform-origin: center;
}}
@media (prefers-reduced-motion: reduce) {{
  .{ENTRY_CLASS_NAME} {{ animation: none; }}
}}
"""
