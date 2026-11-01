from src.svgblock import Block

from .shared import default_block, register_block_builder


@register_block_builder("animations.svg")
def build_animations_overview() -> Block:
    """Build the block that introduces animations, their kinds and how to choose one."""
    return (
        default_block()
        .title("Animations")
        .text("An animation moves the whole block when the image is displayed. You create it "
              "from one of the animation classes and hand it to the block with the "
              "**animation** parameter. Without the parameter, the block is static.")
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
                 "The block sharpens from a blur as it appears, or blurs as it leaves."],
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
        .subsection("Utilities")
        .table(
            ["Animation", "What it does"],
            [
                ["Show(duration)", "The block stays visible and still for a while."],
                ["Hide(duration)", "The block stays hidden for a while."],
                ["Sequence(...)", "Plays several animations one after another."],
            ],
            weights=(4, 8),
        )
        .subsection("Three ways to choose an animation")
        .table(
            ["Form", "Example", "Use it to"],
            [
                ["Default values", "animation=RiseIn()",
                 "Get an animation exactly as it comes."],
                ["A configured animation", "animation=RiseIn(distance=80)",
                 "Adjust durations, distances, sizes, curves and repetitions."],
                ["A sequence", "animation=Sequence(...)",
                 "Chain animations, add waiting times and repeat the whole thing."],
            ],
            weights=(2, 5, 4),
        )
        .divider()
        .text("People who turned on reduce motion in their system settings see the "
              "block without any animation.")
    )


@register_block_builder("animations_base.svg")
def build_base_animations() -> Block:
    """Build the block that introduces the previews of entrances, exits and ambient animations."""
    return (
        default_block()
        .title("Base Animations")
        .text("These are the animations with their default values. The previews below replay "
              "by themselves, so you do not need to reload the page.")
        .subsection("Entrances")
        .text("Every name ending in **In** starts hidden or away from its place and ends in "
              "place. They play once, when the image loads.")
        .subsection("Exits")
        .text("Every entrance has an exit with **Out** in place of **In**. The block starts in "
              "place and ends hidden. Most exits are the entrance played backwards, but "
              "**RiseOut**, **DropOut**, **SlideOut** and **SpinOut** keep going the same way "
              "instead of returning. A rise comes in moving up and leaves moving up. To leave "
              "the way it came, use the opposite exit: **Sequence(RiseIn(), DropOut())**.")
        .text("The previews of exits start visible, play the exit, wait hidden for a moment "
              "and come back with a short fade.")
        .text("In the previews, each row shows an entrance on the left and its exit on the right.")
        .subsection("Ambient")
        .text("**Pulse**, **Float**, **Sway**, **Shake**, **Rotate**, **Drift** and **Jelly** "
              "keep the block visible, with a continuous movement. They play once by default: "
              "use **loop_limit** to repeat them, or to make them infinite. **Shake** and "
              "**Jelly** lose strength until they stop. **Rotate** and **Drift** use a linear "
              "easing, so the loop has no jolt where it restarts.")
        .divider()
        .subsection("Browser Limitations")
        .text("**Safari** doesn't render blur, so __FocusIn__ and __FocusOut__ may apear identical to __FadeIn__ and __FadeOut__")
    )


@register_block_builder("animations_parameters.svg")
def build_animation_parameters() -> Block:
    """Build the block that lists every animation's default parameters and what each parameter does."""
    return (
        default_block()
        .title("Parameters")
        .text("Every parameter is optional and passed by name, as in "
              "**RiseIn(distance=60)**. The only values passed by position are the duration "
              "of **Show** and **Hide**, which is required, and the animations of a "
              "**Sequence**. An exit takes the same parameters as its entrance.")
        .subsection("Defaults")
        .table(
            ["Animation", "Parameters and default values"],
            [
                ["FadeIn", "duration=0.8, easing=EaseOut()"],
                ["FadeOut", "duration=0.8, easing=EaseIn()"],
                ["FocusIn", "blur=8, fade=True, duration=0.8, easing=EaseOut()"],
                ["FocusOut", "blur=8, fade=True, duration=0.8, easing=EaseIn()"],
                ["RiseIn, DropIn",
                 "distance=40, fade=True, focus=False, duration=0.8, easing=EaseOutQuint()"],
                ["RiseOut, DropOut",
                 "distance=40, fade=True, focus=False, duration=0.8, easing=EaseInQuint()"],
                ["SlideIn",
                 'direction="right", distance=40, fade=True, focus=False, duration=0.8, '
                 "easing=EaseOutQuint()"],
                ["SlideOut",
                 'direction="right", distance=40, fade=True, focus=False, duration=0.8, '
                 "easing=EaseInQuint()"],
                ["PopIn, PopOut",
                 "start_scale=0.8, fade=True, focus=False, duration=0.6 (no easing parameter)"],
                ["ZoomIn",
                 "scale=0.5, fade=True, focus=False, duration=0.8, easing=EaseOutQuint()"],
                ["ZoomOut",
                 "scale=0.5, fade=True, focus=False, duration=0.8, easing=EaseInQuint()"],
                ["SpinIn",
                 "angle=45, fade=True, focus=False, duration=0.8, easing=EaseOutQuint()"],
                ["SpinOut",
                 "angle=45, fade=True, focus=False, duration=0.8, easing=EaseInQuint()"],
                ["FlipIn",
                 'axis="horizontal", fade=True, focus=False, duration=0.8, '
                 "easing=EaseOutCubic()"],
                ["FlipOut",
                 'axis="horizontal", fade=True, focus=False, duration=0.8, '
                 "easing=EaseInCubic()"],
                ["UnfoldIn",
                 'edge="top", fade=False, focus=False, duration=0.8, easing=EaseOutQuint()'],
                ["UnfoldOut",
                 'edge="top", fade=False, focus=False, duration=0.8, easing=EaseInQuint()'],
                ["FlickerIn, FlickerOut",
                 "flickers=3, duration=1 (no easing parameter)"],
                ["GlitchIn, GlitchOut",
                 "intensity=12, duration=0.6 (no easing parameter)"],
                ["Pulse", "amount=0.06, duration=2, easing=EaseInOut(), loop_limit=0"],
                ["Float", "amount=8, duration=3, easing=EaseInOut(), loop_limit=0"],
                ["Sway",
                 'angle=3, pivot="top", duration=4, easing=EaseInOut(), loop_limit=0'],
                ["Shake",
                 "amount=8, shakes=6, duration=0.6, easing=EaseInOut(), loop_limit=0"],
                ["Rotate", "angle=360, duration=6, easing=Linear(), loop_limit=0"],
                ["Drift", "radius=8, duration=6, easing=Linear(), loop_limit=0"],
                ["Jelly",
                 "amount=0.15, wobbles=4, duration=0.9, easing=EaseInOut(), loop_limit=0"],
                ["Show", "duration (required)"],
                ["Hide", "duration (required)"],
                ["Sequence", "the animations, in order, and loop_limit=0"],
            ],
            weights=(1, 4),
        )
        .subsection("What each parameter does")
        .table(
            ["Parameter", "Accepts", "What it does"],
            [
                ["duration", "A number greater than 0",
                 "How many seconds one run takes. In **Show** and **Hide**, how long "
                 "they last."],
                ["easing", "An easing, such as EaseOut()",
                 "How the speed changes during the run. See Easings. Not accepted by "
                 "**PopIn**, **PopOut**, **FlickerIn**, **FlickerOut**, **GlitchIn**, "
                 "**GlitchOut**, **Show** and **Hide**."],
                ["distance", "A number, 0 or more",
                 "How many pixels the block travels in **RiseIn**, **DropIn**, **SlideIn** "
                 "and their exits. With 0 the block does not move."],
                ["direction", '"left" or "right"',
                 "The way **SlideIn** and **SlideOut** move: with **right** the block "
                 "comes from the left and moves to the right."],
                ["fade", "True or False",
                 "Whether the entrance or exit also fades. With False the block is fully "
                 "visible while it moves. **UnfoldIn** and **UnfoldOut** default to False, "
                 "and **FadeIn** and **FadeOut** have no such parameter."],
                ["focus", "True or False",
                 "Whether the block also starts out of focus, with a blur that clears as "
                 "it appears. The exit blurs it again. __Safari does not draw the blur, so there the block only fades.__"],
                ["blur", "A number greater than 0",
                 "How many pixels of blur **FocusIn** and **FocusOut** start or end with."
                 "__Safari does not draw it: **FocusIn** and **FocusOut** only fade there.__"],
                ["start_scale", "A number greater than 0 and at most 1",
                 "The size **PopIn** starts from and **PopOut** ends at, where 1 is the "
                 "normal size: 0.8 is 80%."],
                ["scale", "A number greater than 0",
                 "The size **ZoomIn** starts from and **ZoomOut** ends at: 0.5 is half "
                 "the size."],
                ["angle", "A number of degrees",
                 "How far the block turns. In **SpinIn** and **SpinOut**, positive is "
                 "clockwise. In **Sway**, how far it swings to each side. In **Rotate**, "
                 "the size of the turn: 360 is a full turn, and a negative value turns "
                 "counterclockwise."],
                ["axis", '"horizontal" or "vertical"',
                 "What **FlipIn** and **FlipOut** flip. With horizontal the block is "
                 "mirrored left to right, passing through zero width. With vertical, "
                 "top to bottom, passing through zero height."],
                ["edge", '"top", "bottom", "left" or "right"',
                 "The edge that **UnfoldIn** and **UnfoldOut** hinge the block to."],
                ["pivot", '"top", "center" or "bottom"',
                 "The point **Sway** swings from."],
                ["flickers", "A whole number of 1 or more",
                 "How many times **FlickerIn** and **FlickerOut** blink."],
                ["intensity", "A number greater than 0",
                 "How many pixels **GlitchIn** and **GlitchOut** jump sideways."],
                ["amount", "A number greater than 0",
                 "How strong the movement is. In **Pulse**, the growth at its peak: 0.06 is "
                 "6% bigger. In **Float** and **Shake**, the distance in pixels. In "
                 "**Jelly**, the stretch, between 0 and 1: 0.15 is 15%."],
                ["shakes", "A whole number of 1 or more",
                 "How many times **Shake** swings before it stops."],
                ["wobbles", "A whole number of 1 or more",
                 "How many times **Jelly** stretches and squashes before it stops."],
                ["radius", "A number greater than 0",
                 "How wide, in pixels, the figure eight of **Drift** is."],
                ["loop_limit", "A whole number from 0 to 1000, or None",
                 "How many times an ambient animation or a **Sequence** runs again after its "
                 "first run. None means no limit. See Repeating."],
            ],
            weights=(2, 3, 6),
        )
        .text("Customized animations are shown below. Each box shows the code that produced it.")
    )


@register_block_builder("animations_easings.svg")
def build_easings() -> Block:
    """Build the block that explains easings: basic, families, physical and custom curves."""
    return (
        default_block()
        .title("Easings")
        .text("An easing sets how the speed changes while an animation runs: it can start "
              "slow, end slow, go past the final position and come back, bounce, or move in "
              "jumps. Pass one to the **easing** parameter of an animation, as in "
              "**RiseIn(easing=EaseInOut())**. The default of each animation is in "
              "Parameters.")
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
                ["Steps(count, jump)",
                 "Jumps between that many equal steps instead of moving smoothly. "
                 "**jump** is where the jumps happen: **end** (the default), **start**, "
                 "**none** or **both**."],
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
                ["Spring(bounce)",
                 "Overshoots the end and oscillates around it until it settles, like a "
                 "spring. **bounce** is between 0 and 0.9 (default 0.5): a larger value "
                 "oscillates more."],
                ["Bounce(bounces, rebound)",
                 "Reaches the end and bounces back from it, like a dropped ball. **bounces** "
                 "is how many bounces (default 3) and **rebound** is how much of the height "
                 "each one keeps, between 0 and 1 (default 0.5)."],
            ],
            weights=(4, 7),
        )
        .subsection("Custom curves")
        .text("Picture a graph where the horizontal axis is time (0 is the start, 1 is the "
              "end) and the vertical axis is progress (0 is where the animation starts, 1 is "
              "where it ends). The curve goes from the bottom left to the top right and is "
              "bent by two control points: **(x1, y1)** pulls the beginning of the curve and "
              "**(x2, y2)** pulls its end.")
        .text("• **x1** and **x2** must be between 0 and 1.")
        .text("• **y1** and **y2** can be any number. A value below 0 or above 1 makes the "
              "animation go past its limits and come back.")
        .text("• **CubicBezier(0, 0, 1, 1)** is a straight line, the same as Linear().")
        .subsection("Good to know")
        .text("• An easing is an object, never a text: write easing=EaseOut(), not "
              "easing=\"ease-out\".")
        .text("• In a sequence, each step keeps its own easing. **Show** and **Hide** have "
              "none.")
        .text("• Easings that go past their limits, such as the Back family and Spring, "
              "cannot be used where the blur would go below 0: **FocusIn**, **FocusOut** "
              "and animations with focus=True raise a ValueError.")
        .text("• **Spring** and **Bounce** are drawn with the CSS linear() function, so "
              "they need a recent browser.")
        .divider()
        .text("Examples are shown below. Each box shows the code that produced it.")
    )


@register_block_builder("animations_repeating.svg")
def build_repeating_animations() -> Block:
    """Build the block that explains loop_limit and which animations can repeat."""
    return (
        default_block()
        .title("Repeating")
        .text("Animations that can repeat take **loop_limit**: the number of times they run "
              "again after the first run. The default is 0, which means they run once.")
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
        .text("None means there is no limit, so the animation is **infinite**. Infinite "
              "animations have rules inside sequences: see Sequences.")
        .text("The largest finite value is 1000. For more than that, use None.")
        .subsection("Which animations repeat")
        .text("• **Pulse**, **Float**, **Sway**, **Shake**, **Rotate**, **Drift**, **Jelly** and "
              "**Sequence** accept loop_limit.")
        .text("• Entrances and exits play once and do not accept it. To replay an entrance, put it "
              "in a **Sequence** with a **Show** step and make the sequence infinite. To replay an "
              "entrance and its exit, put both in the sequence.")
    )


@register_block_builder("animations_sequence.svg")
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
        .table(
            ["Where loop_limit is", "What it repeats"],
            [
                ["On an animation inside the sequence",
                 "Only that animation, every time the sequence runs."],
                ["On the sequence", "The whole sequence, from its first step."],
            ],
            weights=(3, 4),
        )
        .text("For example, a sequence with loop_limit=2 runs three times, and a Pulse with "
              "loop_limit=4 inside it pulses five times in each run.")
        .subsection("Steps are not blended")
        .text("Each step starts from its own starting state, and svgblock does not smooth the "
              "connection between steps. After a RiseIn the block is in place, so a second "
              "entrance right after it makes the block jump back to its starting state and "
              "enter again. An exit leaves the block hidden, so a step that starts visible "
              "makes it reappear at once. You choose steps that fit together, and **Show** is "
              "the natural way to separate them.")
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
        .subsection("Nesting, empty and large sequences")
        .text("• A sequence can be a step of another sequence. Each one keeps its own "
              "loop_limit.")
        .text("• A sequence with no steps is valid and does nothing: the block is shown "
              "static.")
        .text("• The repetitions are counted one by one, and a sequence cannot have more than "
              "10,000 of them in total. To repeat without a limit, use loop_limit=None "
              "instead of a very large number.")
        .subsection("When it ends")
        .text("After its last step, a finite sequence leaves the block in the final state of "
              "that step. If the last step is **Hide** or an exit, the block stays hidden.")
        .divider()
        .text("Combined animations are shown below. Each box shows the code that produced it.")
    )


@register_block_builder("animations_errors.svg")
def build_animation_errors() -> Block:
    """Build the block that lists the errors animations raise and the notes about their limits."""
    return (
        default_block()
        .title("Errors")
        .table(
            ["Situation", "What happens"],
            [
                ["duration is 0 or negative", "ValueError."],
                ["distance is negative", "ValueError."],
                ["start_scale is 0, negative or greater than 1", "ValueError."],
                ["scale, amount, intensity, radius, blur or the angle of Sway is 0 "
                 "or negative", "ValueError."],
                ["amount of Jelly is not between 0 and 1", "ValueError."],
                ["angle of Rotate is 0", "ValueError."],
                ["flickers, shakes or wobbles is not a whole number of 1 or more",
                 "ValueError."],
                ["axis, edge, pivot or direction is not one of its listed values",
                 "ValueError."],
                ["loop_limit is negative or greater than 1000", "ValueError."],
                ["x1 or x2 of CubicBezier is outside 0 to 1", "ValueError."],
                ["count of Steps is not a whole number of 1 or more, or jump is not "
                 "start, end, none or both", "ValueError."],
                ["bounce of Spring, or bounces or rebound of Bounce, is out of range",
                 "ValueError."],
                ["An overshooting easing on an animation with blur",
                 "ValueError: the blur would go below 0."],
                ["loop_limit passed to an entrance, an exit, Show or Hide",
                 "TypeError: these animations do not accept it."],
                ["easing passed to PopIn, PopOut, FlickerIn, FlickerOut, GlitchIn, "
                 "GlitchOut, Show or Hide",
                 "TypeError: their timing is fixed."],
                ["fade or focus passed to an animation that has no such parameter, "
                 "such as FadeIn", "TypeError."],
                ['An easing that is not an easing object, such as easing="ease-out" '
                 "or easing=EaseOut",
                 "TypeError."],
                ["A sequence step that is not an animation, such as RiseIn without "
                 "parentheses",
                 "TypeError."],
                ["An infinite animation that is not the last step of a sequence",
                 "ValueError: the steps after it would never play."],
                ["A sequence that, once unrolled, has more than 10,000 steps",
                 "ValueError: reduce a loop_limit or use None."],
            ],
            weights=(5, 5),
        )
        .subsection("Good to know")
        .text("• The animation moves the whole block, border and content together. With "
              "hide_frame=True, only the content moves.")
        .text("• The block is only visible inside the image. Entrances and exits come from "
              "outside it, so they can start or end cropped by its edge. With fade=False "
              "and a large distance, the block slides in from the edge. The blur of an "
              "entrance or exit can also be cropped by the edge of the image.")
        .text("• Animations that make the block bigger than its normal size get room inside "
              "the image, so the block rests slightly smaller than width and is never "
              "cropped. This includes **Pulse**, **Jelly**, **GlitchIn** and **GlitchOut** "
              "(which stretch the block by 5%), and **ZoomIn** or **ZoomOut** with a scale "
              "above 1.")
        .text("• Ambient animations are always in view, so they also get room for their "
              "movement, rotation and blur, and the block rests smaller than width. A "
              "**Rotate** needs room for a whole circle, so the block rests noticeably "
              "smaller and the image gets taller. In a sequence, the room fits the step "
              "that needs the most. The image keeps the width you passed.")
        .text("• Without a loop, an animation plays once when the image loads. Reload the "
              "page to see it again.")
        .text("• Some image viewers and editors do not run animations. Open the file in a "
              "browser to check.")
        .text("• The blur of **FocusIn**, **FocusOut** and focus=True is not drawn by Safari. The "
              "rest of the animation still plays, so use a fade or another animation if the blur "
              "matters to you.")
    )
