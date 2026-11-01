from src.svgblock import Block

from .shared import (AnimationExample, default_block, register_animation_previews,
                     register_block_builder)

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


@register_block_builder("animations.svg")
def build_animations_overview() -> Block:
    """Build the block that introduces the animations and lists every entrance, exit and ambient one."""
    return (
        default_block()
        .title("Animations")
        .text("An animation moves the whole block when the image is displayed. You create it "
              "from one of the animation classes and hand it to the block with the "
              "**animation** parameter. Without it, the block is static.")
        .text("Animations come in four kinds. **Entrances** (names ending in **In**) start "
              "with the block hidden or away and end with it in place. **Exits** (names "
              "ending in **Out**) do the opposite: every entrance has an exit. **Ambient** "
              "animations keep the block in view and move it continuously. **Utilities** "
              "wait or chain other animations.")
        .subsection("Entrances and exits")
        .table(
            ["Pair", "What it does"],
            [
                ["FadeIn() / FadeOut()", "The block fades in, or out."],
                ["FocusIn() / FocusOut()",
                 "The block sharpens from a blur as it appears, or blurs as it leaves. Safari "
                 "does not draw the blur, so there the block only fades. The same applies to "
                 "focus=True in the other animations."],
                ["RiseIn() / RiseOut()",
                 "The block rises into place from below. The exit keeps rising and leaves "
                 "upwards."],
                ["DropIn() / DropOut()",
                 "The block drops into place from above. The exit keeps dropping and leaves "
                 "downwards."],
                ["SlideIn() / SlideOut()",
                 "The block slides in sideways. The exit keeps going the same way."],
                ["PopIn() / PopOut()",
                 "The block grows from a smaller size to its normal size, dips a little and "
                 "settles. It never gets bigger than normal. The exit is the entrance played "
                 "backwards."],
                ["ZoomIn() / ZoomOut()",
                 "The block grows from a smaller size, without a bounce. The exit shrinks back "
                 "to it."],
                ["SpinIn() / SpinOut()",
                 "The block turns while it appears. The exit keeps turning the same way."],
                ["FlipIn() / FlipOut()",
                 "The block flips like a card, passing through the point where it is edge-on. "
                 "The exit flips back."],
                ["UnfoldIn() / UnfoldOut()",
                 "The block opens like a panel hinged to an edge. The exit folds back to the "
                 "same edge."],
                ["FlickerIn() / FlickerOut()",
                 "The block switches on, or off, flickering like a neon sign."],
                ["GlitchIn() / GlitchOut()",
                 "Sharp jumps in position, width and opacity, with no smooth movement."],
            ],
            weights=(4, 8),
        )
        .text("To leave the way it came, use the opposite exit: "
              "**Sequence(RiseIn(), DropOut())**.")
        .subsection("Ambient")
        .table(
            ["Animation", "What it does"],
            [
                ["Pulse()", "The block grows and shrinks gently, staying in place."],
                ["Float()", "The block floats up and down."],
                ["Sway()", "The block swings like a pendulum."],
                ["Shake()", "The block shakes sideways and loses strength until it stops."],
                ["Rotate()", "The block turns, a full turn by default."],
                ["Drift()", "The block slides in a soft figure eight around its place."],
                ["Jelly()", "The block stretches and squashes in turns, like jelly, until it "
                            "settles."],
            ],
            weights=(4, 8),
        )
        .text("Ambient animations play once by default. Use **loop_limit** to repeat them or "
              "make them infinite: see Repeating.")
        .divider()
        .text("Each preview below shows the code that produced it and replays by itself. People "
              "who turned on reduce motion in their system settings see the block without any "
              "animation.")
    )


register_animation_previews(
    ENTRANCE_EXAMPLES + EXIT_EXAMPLES + AMBIENT_EXAMPLES, "animation_")
