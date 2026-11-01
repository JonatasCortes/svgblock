from dataclasses import dataclass

from src.svgblock import Block

from .shared import (AnimationExample, default_block, register_animation_previews,
                     register_block_builder)

BASELINE_EASING_CODE = "Linear()"
RISE_ANIMATION_TEMPLATE = "RiseIn(distance=80, fade=False, duration=1.4, easing={easing})"
DROP_ANIMATION_TEMPLATE = "DropIn(distance=120, fade=False, duration=1.4, easing={easing})"


@dataclass(frozen=True)
class EasingComparison:
    """A pair of previews that run the same animation without easing and with an easing.

    The animation template has an {easing} slot that is filled with the baseline
    easing for the first preview and with easing_code for the second one.
    """

    slug: str
    title: str
    easing_code: str
    animation_template: str = RISE_ANIMATION_TEMPLATE


EASING_COMPARISONS: tuple[EasingComparison, ...] = (
    EasingComparison("ease_in", "EASE IN", "EaseIn()"),
    EasingComparison("ease_out", "EASE OUT", "EaseOut()"),
    EasingComparison("ease_in_out", "EASE IN OUT", "EaseInOut()"),
    EasingComparison("overshoot", "OVERSHOOT", "EaseOutBack()"),
    EasingComparison("custom_curve", "CUSTOM CURVE",
                     "CubicBezier(0.4, 0, 0.2, 1)"),
    EasingComparison("steps", "STEPS", "Steps(10)"),
    EasingComparison("spring", "SPRING", "Spring()"),
    EasingComparison("bounce", "BOUNCE", "Bounce()", DROP_ANIMATION_TEMPLATE),
)


def build_comparison_examples(
    comparison: EasingComparison,
) -> tuple[AnimationExample, AnimationExample]:
    """Build the preview without easing and the preview with the compared easing."""
    without_easing = AnimationExample(
        f"{comparison.slug}_without",
        "NO EASING",
        comparison.animation_template.format(easing=BASELINE_EASING_CODE),
        replay=True,
    )
    with_easing = AnimationExample(
        f"{comparison.slug}_with",
        comparison.title,
        comparison.animation_template.format(easing=comparison.easing_code),
        replay=True,
    )
    return without_easing, with_easing


@register_block_builder("easings.svg")
def build_easings() -> Block:
    """Build the block that explains easings: basic, families, physical and custom curves."""
    return (
        default_block()
        .title("Easings")
        .text("An easing sets how the speed changes while an animation runs: it can start "
              "slow, end slow, go past the final position and come back, bounce, or move in "
              "jumps. Pass one to the **easing** parameter of an animation, as in "
              "**RiseIn(easing=EaseInOut())**.")
        .subsection("Basic")
        .table(
            ["Easing", "What it does"],
            [
                ["Linear()", "Constant speed from start to end."],
                ["EaseIn()", "Starts slow and speeds up."],
                ["EaseOut()", "Starts fast and slows down until it stops."],
                ["EaseInOut()", "Slow at the start and at the end, fast in the middle."],
                ["CubicBezier(x1, y1, x2, y2)",
                 "A curve of your own. See below."],
                ["Steps(count)",
                 "Jumps between that many equal steps instead of moving smoothly."],
            ],
            weights=(4, 7),
        )
        .subsection("Families")
        .text("Each family comes in three forms: **In** starts slow, **Out** ends slow and "
              "**InOut** does both. The name is the family plus the form, as in "
              "**EaseOutCubic()** or **EaseInOutBack()**.")
        .table(
            ["Family", "Character"],
            [
                ["Sine", "The gentlest curve. Subtle and natural."],
                ["Cubic", "A moderate curve that suits most movements."],
                ["Quint", "A strong curve: the Out form starts very fast and settles slowly."],
                ["Expo", "The strongest: nearly all the movement happens in a short part "
                         "of the run."],
                ["Circ", "Follows a circular arc, so it speeds up or stops more abruptly "
                         "than Cubic."],
                ["Back", "Goes past the limit and comes back. **In** pulls back before "
                         "moving, **Out** overshoots the end."],
            ],
            weights=(1, 4),
        )
        .subsection("Physical")
        .table(
            ["Easing", "What it does"],
            [
                ["Spring()",
                 "Overshoots the end and oscillates around it until it settles, like a "
                 "spring."],
                ["Bounce()",
                 "Reaches the end and bounces back from it, like a dropped ball."],
            ],
            weights=(4, 7),
        )
        .subsection("Custom curves")
        .text("Picture a graph where the horizontal axis is time (0 is the start, 1 is the "
              "end) and the vertical axis is progress (0 is where the animation starts, 1 is "
              "where it ends). The curve goes from the bottom left to the top right and is "
              "bent by two control points: **(x1, y1)** pulls the beginning of the curve and "
              "**(x2, y2)** pulls its end.")
        .text("The x values stay between 0 and 1, while y1 and y2 can be any number: a value "
              "below 0 or above 1 makes the animation go past its limits and come back.")
        .subsection("Good to know")
        .text("• Easings that go past their limits, such as the Back family and Spring, "
              "cannot be used where the blur would go below 0: **FocusIn**, **FocusOut** "
              "and animations with focus=True raise a ValueError.")
        .text("• **Spring** and **Bounce** need a recent browser.")
        .divider()
        .text("Each pair below runs the same animation without easing (left) and with it (right).")
    )


EASING_EXAMPLES: tuple[AnimationExample, ...] = tuple(
    example
    for comparison in EASING_COMPARISONS
    for example in build_comparison_examples(comparison)
)

register_animation_previews(EASING_EXAMPLES, "easing_")
