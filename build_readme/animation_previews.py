from dataclasses import dataclass
from functools import partial

from src.svgblock import BaseAnimation, Block, FadeIn, Hide, Sequence, Show
from src.svgblock.components import animations

from .shared import DOC_THEME, register_asset

ANIMATION_CLASSES_BY_NAME: dict[str, type] = {
    name: value
    for name, value in vars(animations).items()
    if isinstance(value, type)
}

PREVIEW_WIDTH = 400
PREVIEW_REST_SECONDS = 3
PREVIEW_HIDDEN_SECONDS = 1
PREVIEW_RETURN_SECONDS = 0.5


@dataclass(frozen=True)
class AnimationExample:
    """A preview box in the Animations section.

    The code is run to build the animation, so what the box shows is always
    what the preview does. With replay=True the preview adds a rest and
    starts over by itself, so nobody needs to reload the page. With
    leave=True the preview starts visible, plays the exit, stays hidden for a
    moment and comes back with a short fade.
    """

    slug: str
    title: str
    code: str
    replay: bool = False
    leave: bool = False


ENTRANCE_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample("fade_in", "FADE IN", "FadeIn()", replay=True),
    AnimationExample("focus_in", "FOCUS IN", "FocusIn()", replay=True),
    AnimationExample("rise_in", "RISE IN", "RiseIn()", replay=True),
    AnimationExample("drop_in", "DROP IN", "DropIn()", replay=True),
    AnimationExample("slide_in", "SLIDE IN", "SlideIn()", replay=True),
    AnimationExample("pop_in", "POP IN", "PopIn()", replay=True),
    AnimationExample("zoom_in", "ZOOM IN", "ZoomIn()", replay=True),
    AnimationExample("spin_in", "SPIN IN", "SpinIn()", replay=True),
    AnimationExample("flip_in", "FLIP IN", "FlipIn()", replay=True),
    AnimationExample("unfold_in", "UNFOLD IN", "UnfoldIn()", replay=True),
    AnimationExample("flicker_in", "FLICKER IN", "FlickerIn()", replay=True),
    AnimationExample("glitch_in", "GLITCH IN", "GlitchIn()", replay=True),
)

EXIT_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample("fade_out", "FADE OUT", "FadeOut()", leave=True),
    AnimationExample("focus_out", "FOCUS OUT", "FocusOut()", leave=True),
    AnimationExample("rise_out", "RISE OUT", "RiseOut()", leave=True),
    AnimationExample("drop_out", "DROP OUT", "DropOut()", leave=True),
    AnimationExample("slide_out", "SLIDE OUT", "SlideOut()", leave=True),
    AnimationExample("pop_out", "POP OUT", "PopOut()", leave=True),
    AnimationExample("zoom_out", "ZOOM OUT", "ZoomOut()", leave=True),
    AnimationExample("spin_out", "SPIN OUT", "SpinOut()", leave=True),
    AnimationExample("flip_out", "FLIP OUT", "FlipOut()", leave=True),
    AnimationExample("unfold_out", "UNFOLD OUT", "UnfoldOut()", leave=True),
    AnimationExample("flicker_out", "FLICKER OUT", "FlickerOut()", leave=True),
    AnimationExample("glitch_out", "GLITCH OUT", "GlitchOut()", leave=True),
)

AMBIENT_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample("pulse", "PULSE", "Pulse(loop_limit=None)"),
    AnimationExample("float", "FLOAT", "Float(loop_limit=None)"),
    AnimationExample("sway", "SWAY", "Sway(loop_limit=None)"),
    AnimationExample("rotate", "ROTATE", "Rotate(loop_limit=None)"),
    AnimationExample("drift", "DRIFT", "Drift(loop_limit=None)"),
    AnimationExample("shake", "SHAKE", "Shake()", replay=True),
    AnimationExample("jelly", "JELLY", "Jelly()", replay=True),
)

CUSTOMIZED_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "rise_in_custom", "RISE IN, CUSTOMIZED",
        "RiseIn(distance=80, duration=1.6, fade=False)", replay=True),
    AnimationExample(
        "drop_in_custom", "DROP IN, CUSTOMIZED",
        "DropIn(distance=20, duration=0.4)", replay=True),
    AnimationExample(
        "slide_in_custom", "SLIDE IN, CUSTOMIZED",
        'SlideIn(direction="left", distance=120)', replay=True),
    AnimationExample(
        "pop_in_custom", "POP IN, CUSTOMIZED",
        "PopIn(start_scale=0.3, duration=1.2)", replay=True),
    AnimationExample(
        "spin_in_custom", "SPIN IN, CUSTOMIZED",
        "SpinIn(angle=-120, focus=True)", replay=True),
    AnimationExample(
        "flip_in_custom", "FLIP IN, CUSTOMIZED",
        'FlipIn(axis="vertical")', replay=True),
    AnimationExample(
        "unfold_in_custom", "UNFOLD IN, CUSTOMIZED",
        'UnfoldIn(edge="left", fade=True)', replay=True),
    AnimationExample(
        "focus_in_custom", "FOCUS IN, CUSTOMIZED",
        "FocusIn(blur=16, duration=1.6)", replay=True),
    AnimationExample(
        "pulse_custom", "PULSE, CUSTOMIZED",
        "Pulse(amount=0.1, duration=1, loop_limit=4)", replay=True),
    AnimationExample(
        "sway_custom", "SWAY, CUSTOMIZED",
        'Sway(angle=8, pivot="bottom", loop_limit=None)'),
    AnimationExample(
        "shake_custom", "SHAKE, CUSTOMIZED",
        "Shake(amount=16, shakes=10)", replay=True),
)

EASING_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "easing_back", "OVERSHOOT",
        "RiseIn(easing=EaseOutBack())", replay=True),
    AnimationExample(
        "easing_bezier", "CUSTOM CURVE",
        "RiseIn(easing=CubicBezier(0.4, 0, 0.2, 1))", replay=True),
    AnimationExample(
        "easing_steps", "STEPS",
        "RiseIn(easing=Steps(10))", replay=True),
    AnimationExample(
        "easing_spring", "SPRING",
        "RiseIn(easing=Spring(), duration=1.4)", replay=True),
    AnimationExample(
        "easing_bounce", "BOUNCE",
        "DropIn(distance=120, fade=False, easing=Bounce(), duration=1.4)",
        replay=True),
)

SEQUENCE_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "seq_pop_show", "POP SHOW",
        "Sequence(PopIn(), Show(3), loop_limit=None)"),
    AnimationExample(
        "seq_hide_pulse_show", "HIDE, PULSE, SHOW",
        "Sequence(Hide(0.5), RiseIn(), Pulse(loop_limit=1), Show(2), loop_limit=None)"),
    AnimationExample(
        "seq_rise_float", "RISE, FLOAT, RISE",
        "Sequence(RiseIn(), Float(loop_limit=2), RiseOut(), loop_limit=None)"),
    AnimationExample(
        "seq_zoom_in_out", "ZOOM IN, ZOOM OUT",
        "Sequence(ZoomIn(), Show(2), ZoomOut(), Hide(0.5), loop_limit=None)"),
)

ALL_ANIMATION_EXAMPLES: tuple[AnimationExample, ...] = (
    ENTRANCE_EXAMPLES + EXIT_EXAMPLES + AMBIENT_EXAMPLES
    + CUSTOMIZED_EXAMPLES + EASING_EXAMPLES + SEQUENCE_EXAMPLES
)


def evaluate_animation_code(code: str) -> BaseAnimation:
    """Run the code shown in a preview box, so the box always matches what the preview does."""
    return eval(code, {"__builtins__": {}, **ANIMATION_CLASSES_BY_NAME})


def build_preview_animation(example: AnimationExample) -> BaseAnimation:
    """Wrap the example's animation in the sequence that makes its preview repeat by itself."""
    animation = evaluate_animation_code(example.code)
    if example.leave:
        return Sequence(
            Show(PREVIEW_REST_SECONDS), animation,
            Hide(PREVIEW_HIDDEN_SECONDS),
            FadeIn(duration=PREVIEW_RETURN_SECONDS),
            loop_limit=None)
    if example.replay:
        return Sequence(
            animation, Show(PREVIEW_REST_SECONDS), loop_limit=None)
    return animation


def build_animation_preview_block(example: AnimationExample) -> Block:
    """Build the small block that plays an example's animation and shows the code behind it."""
    return (
        Block(DOC_THEME, PREVIEW_WIDTH,
              animation=build_preview_animation(example))
        .title(example.title)
        .text(f"**__{example.code}__**", font_size=14)
    )


for example in ALL_ANIMATION_EXAMPLES:
    register_asset(f"animation_{example.slug}.svg",
                   partial(build_animation_preview_block, example))
