from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial

from src.svgblock import BaseAnimation, Block, FadeIn, Hide, Sequence, Show
from src.svgblock.components import animations

from .doc_style import DOC_THEME
from .registry import register_asset

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

    The slug names the generated file. The code is run to build the animation,
    so what the box shows is always what the preview does. With replay=True the
    preview adds a rest and starts over by itself, so nobody needs to reload the
    page. With leave=True the preview starts visible, plays the exit, stays
    hidden for a moment and comes back with a short fade.
    """

    slug: str
    title: str
    code: str
    replay: bool = False
    leave: bool = False


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


def register_animation_previews(
    examples: Iterable[AnimationExample], filename_prefix: str
) -> None:
    """Register one SVG per example, named after the prefix and the example's slug."""
    for example in examples:
        register_asset(f"{filename_prefix}{example.slug}.svg",
                       partial(build_animation_preview_block, example))
