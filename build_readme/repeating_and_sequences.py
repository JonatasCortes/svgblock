from src.svgblock import Block

from .shared import (AnimationExample, default_block, register_animation_previews,
                     register_block_builder)

SEQUENCE_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "appear_stay_leave", "APPEAR, STAY, LEAVE",
        "Sequence(PopIn(), Show(2), PopOut(), Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "leave_the_way_it_came", "LEAVE THE WAY IT CAME",
        "Sequence(RiseIn(), Show(2), DropOut(), Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "rise_float_leave", "RISE, FLOAT, LEAVE",
        "Sequence(RiseIn(), Float(loop_limit=2), RiseOut(), loop_limit=None)"),
    AnimationExample(
        "land_and_wobble", "LAND AND WOBBLE",
        "Sequence(DropIn(), Jelly(), Show(2), DropOut(), Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "neon_sign", "NEON SIGN",
        "Sequence(FlickerIn(), Pulse(amount=0.03, loop_limit=2), FlickerOut(), "
        "Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "glitch_alert", "GLITCH ALERT",
        "Sequence(GlitchIn(), Shake(), Show(1.5), GlitchOut(), Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "keep_turning", "KEEP TURNING",
        "Sequence(SpinIn(), Show(2), SpinOut(), Hide(0.5), loop_limit=None)"),
    AnimationExample(
        "fade_in_then_breathe", "FADE IN, THEN BREATHE",
        "Sequence(FadeIn(), Pulse(loop_limit=None))"),
)


@register_block_builder("repeating.svg")
def build_repeating_animations() -> Block:
    """Build the block that explains loop_limit and how to replay entrances and exits."""
    return (
        default_block()
        .title("Repeating")
        .text("The ambient animations (**Pulse**, **Float**, **Sway**, **Shake**, **Rotate**, "
              "**Drift** and **Jelly**) and **Sequence** take **loop_limit**: the number of "
              "times they run again after the first run. The default is 0, which means they "
              "run once.")
        .table(
            ["loop_limit", "Total runs"],
            [
                ["0 (default)", "1"],
                ["1", "2"],
                ["4", "5"],
                ["None", "No limit: it never stops"],
            ],
            weights=(1, 3),
        )
        .text("Entrances and exits play once and do not take loop_limit. To replay one, put it "
              "in a **Sequence** with a **Show** step and make the sequence infinite with "
              "loop_limit=None. To replay an entrance and its exit, put both in the sequence.")
    )


@register_block_builder("sequences.svg")
def build_sequences() -> Block:
    """Build the block that explains how to chain animations with Sequence, Show and Hide."""
    return (
        default_block()
        .title("Sequences")
        .text("**Sequence(...)** plays animations one after another: each one starts when "
              "the previous one ends. Pass the animations in order and, if you want, "
              "**loop_limit** to repeat the whole sequence. A step can be any animation, "
              "including another sequence.")
        .subsection("Waiting")
        .text("**Show(duration)** keeps the block still for a while, looking exactly as it "
              "normally does. **Hide(duration)** hides the block for a while. Use them to "
              "delay or to separate steps.")
        .subsection("Two levels of repetition")
        .text("A loop_limit on an animation inside the sequence repeats only that animation, "
              "every time the sequence runs. On the sequence, it repeats the whole thing from "
              "its first step. For example, a sequence with loop_limit=2 runs three times, and "
              "a Pulse with loop_limit=4 inside it pulses five times in each run.")
        .subsection("Steps are not blended")
        .text("Each step starts from its own starting state, and svgblock does not smooth the "
              "connection between steps. After a RiseIn the block is in place, so a second "
              "entrance right after it makes the block jump back to its starting state and "
              "enter again. An exit leaves the block hidden, so a step that starts visible "
              "makes it reappear at once. Choose steps that fit together, and use **Show** to "
              "separate them.")
        .subsection("Entering and leaving")
        .text("A common shape is an entrance, an ambient animation and an exit, such as "
              "**Sequence(RiseIn(), Float(loop_limit=3), RiseOut())**. An exit ends hidden and an "
              "entrance starts hidden, so with **loop_limit=None** the sequence starts over "
              "without anyone seeing the join. That holds while fade is on: with fade=False the "
              "block would jump from where the exit ended to where the entrance starts.")
        .subsection("Infinite steps")
        .text("• An animation with loop_limit=None never ends, so only the **last** step of a "
              "sequence can be infinite: anything after it would never play.")
        .text("• When the last step is infinite, the sequence never reaches its end, so its "
              "own loop_limit has no effect.")
        .divider()
        .text("A few combinations to start from:")
    )


register_animation_previews(SEQUENCE_EXAMPLES, "sequence_")
