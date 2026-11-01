from src.svgblock import Block

from .shared import default_block, register_block_builder


@register_block_builder("troubleshooting.svg")
def build_troubleshooting() -> Block:
    """Build the block that lists common problems and what to check for each one."""
    return (
        default_block()
        .title("Troubleshooting")
        .table(
            ["Problem", "What to check"],
            [
                ["Errors about the | symbol in type hints",
                 "You are using a Python older than 3.10. Update Python and install again."],
                ["NameError: name 'RiseIn' is not defined",
                 "Animations and easings must be imported, as in from svgblock import RiseIn, "
                 "Sequence, EaseOut."],
                ["ValueError: Unclosed marker",
                 r"A marker (\*\*, \_\_, \-\-, \#\#) was opened and never closed. Every marker "
                 r"needs a closing twin. To write a literal one, put a backslash before each of its characters."],
                ["A style appears or vanishes where it should not",
                 r"Text that contains \*\*, \_\_, \-\- or \#\# toggles a style, even a double hyphen "
                 r"used as a dash or a name like \_\_init\_\_. Escape those characters with a backslash."],
                ["Markers show up literally in a title or a table header",
                 "Only paragraphs and table cells read markers. Titles, subsections and table "
                 "headers are drawn as plain bold text."],
                ["SyntaxWarning: invalid escape sequence",
                 "Python is warning about the backslash. Use a raw string (an r before the opening "
                 "quote) or write the backslash twice."],
                ["ValueError from table, columns, divider or image",
                 "Every table row needs as many cells as columns, align and weights need one value "
                 "per column, a divider coverage must be between 0 and 1 and an image width must be "
                 "greater than zero."],
                ["The image is missing or fails to load",
                 "The path is read when you run the script, relative to the folder you run it from. "
                 "Check that the file exists there."],
                ["A title, a subsection or a very long word goes past the border",
                 "Titles and subsections stay on a single line, and a word bigger than its space "
                 "cannot fit. Shorten the text, reduce the font_size or increase the width."],
                ["Words are broken in the middle inside a table or a column",
                 "A narrow column cannot fit a long word, so it is broken. Give that column a larger "
                 "weight, shorten the text or increase the width of the block."],
                ["Lines break earlier or later than expected",
                 "The width of the text is estimated with the Arial font. On a system without Arial "
                 "the browser uses another font, so lines can look slightly different. Emojis and "
                 "curly quotes are measured as a full letter wide."],
                ["ValueError about duration, distance, start_scale or amount",
                 "Durations, sizes and amounts must be greater than 0, and distance must be "
                 "0 or more. start_scale also cannot be greater than 1, and the amount of Jelly "
                 "must be between 0 and 1."],
                ["ValueError about loop_limit",
                 "loop_limit must be from 0 to 1000, or None for no limit. In a sequence, "
                 "only the last step can be infinite."],
                ["ValueError about x1, x2, count or bounce",
                 "In CubicBezier, x1 and x2 must be between 0 and 1. In Steps, count must be "
                 "a whole number of 1 or more. In Spring, bounce must be greater than 0 and "
                 "at most 0.9."],
                ["ValueError: the blur would go below 0",
                 "An easing that goes past its limits, such as EaseOutBack() or Spring(), pushed "
                 "the blur of FocusIn, FocusOut or focus=True below 0. Use an easing that does "
                 "not overshoot."],
                ["TypeError: unexpected keyword argument 'loop_limit'",
                 "Only ambient animations (Pulse, Float, Sway, Shake, Rotate, Drift and Jelly) "
                 "and Sequence accept loop_limit. Entrances and exits play once. To repeat "
                 "them, put them in a Sequence."],
                ["TypeError: unexpected keyword argument 'easing'",
                 "PopIn, PopOut, FlickerIn, FlickerOut, GlitchIn, GlitchOut, Show and Hide have "
                 "a fixed timing. To control it, change the duration."],
                ["TypeError: unexpected keyword argument 'fade' or 'focus'",
                 "FadeIn and FadeOut have neither. FocusIn and FocusOut have fade, and blur sets "
                 "their focus. Flicker and Glitch have neither."],
                ["TypeError: a step must be an animation, or easing must be an Easing",
                 "Animations and easings are objects, so they need parentheses: RiseIn(), not "
                 "RiseIn, and EaseOut(), not EaseOut. Names in quotes, such as \"rise\" or "
                 "\"ease-out\", are not accepted."],
                ["ValueError: Step N of the sequence would never play",
                 "An earlier step has loop_limit=None and never ends, so nothing after it can "
                 "play. Move the infinite step to the end of the sequence."],
                ["The loop_limit of my sequence does nothing",
                 "When the last step is infinite, the sequence never reaches its end, so it "
                 "cannot repeat. Use a finite last step."],
                ["ValueError: This sequence repeats too much",
                 "The repetitions of a sequence are counted one by one and cannot pass 10,000. "
                 "Reduce a loop_limit or use None."],
                ["The animation does not play",
                 "An animation without a loop plays once, when the image loads, so reload the "
                 "page to see it again. To replay an entrance, use a Sequence with a Show step "
                 "and loop_limit=None. Nothing plays for people who turned on reduce motion, "
                 "or in viewers that do not run animations. Open the file in a browser to "
                 "check."],
                ["My pulse only pulses once",
                 "loop_limit is 0 by default, which means a single run. Use loop_limit=4 for "
                 "five pulses or loop_limit=None for no limit."],
                ["Shake or Jelly stops moving after a while",
                 "They lose strength on purpose and stop after a few swings. Use shakes or "
                 "wobbles to lengthen them, or loop_limit to repeat them."],
                ["The block disappears and never comes back",
                 "An exit ends with the block hidden. To bring it back, put an entrance after "
                 "it in a Sequence, or make the sequence infinite with loop_limit=None."],
                ["The exit goes the opposite way from what I expected",
                 "RiseOut, DropOut, SlideOut and SpinOut keep going the way their entrance was "
                 "moving. To leave the way it came, use the opposite exit: "
                 "Sequence(RiseIn(), DropOut())."],
                ["The block jumps between two steps of a sequence",
                 "svgblock does not blend steps: each one starts from its own state. After an "
                 "entrance the block is in place, and a new entrance starts from its beginning. "
                 "The same applies after an exit, which leaves the block hidden. Choose steps "
                 "that fit together, or separate them with a Show step."],
                ["The block is cropped while it moves",
                 "The block is only visible inside the image. Entrances and exits come from "
                 "outside it, so they can start or end cropped. With fade=False, a large "
                 "distance makes the block start outside the image. Reduce the distance or "
                 "keep the fade on."],
                ["The block looks smaller than width",
                 "Animations that make the block bigger than normal (Pulse, Jelly, Glitch, or Zoom with "
                 "a scale above 1) and ambient animations that move, turn or blur it get room inside "
                 "the image, so the block rests smaller than width and is never cropped. Rotate asks "
                 "for the most."],
                ["The image is much taller with Rotate",
                 "A full turn needs room for a whole circle, so the image makes space above and "
                 "below the block. Use a smaller angle, as in Rotate(angle=30), or Sway."],
                ["Spring or Bounce does not look right",
                 "They use the CSS linear() function. In an old browser or viewer, the easing "
                 "may be ignored. Open the file in a recent browser to check."],
                ["The blur of FocusIn or focus=True does not show in Safari",
                 "Safari does not draw the blur on SVG. The animation still plays without it, "
                 "so the block only fades. Open the file in another browser to see the blur."],
                ["AttributeError: Theme has no attribute ...",
                 "The theme does not exist in the Theme enum. Names are uppercase, exactly as "
                 "shown in the Themes section (for example Theme.NEON). To use a color scheme "
                 "that is not there, create your own ThemeData."],
                ["An error that names a color, such as KeyError: 'divider'",
                 "Your ThemeData is missing that color. Every theme needs all of them. See the "
                 "list in Creating Your Own Theme, or start from a copy of a ready-made theme."],
                ["A theme changed in blocks where I did not expect it",
                 "Theme.NAME.value.update(...) changes the shared theme for the whole program. "
                 "To change only one block, use Theme.NAME.value.copy(), edit the copy and pass "
                 "it to that block."],
                ["My theme edit has no effect",
                 "Make the change before the blocks that use it are drawn, and check that the "
                 "color name is spelled exactly as in the list of theme colors."],
                ["The block does not show on my page",
                 "Check that the path in the img tag matches the file name exactly (paths are case "
                 "sensitive on most servers, including GitHub) and that the .svg file is "
                 "published together with the page."],
            ],
            weights=(2, 5),
        )
    )
