from src.svgblock import Block

from .shared import default_block, register_block_builder


@register_block_builder("troubleshooting.svg")
def build_troubleshooting() -> Block:
    """Build the block that lists the problems readers actually see and what to check for each one."""
    return (
        default_block()
        .title("Troubleshooting")
        .table(
            ["Problem", "What to check"],
            [
                ["Errors about the | symbol in type hints",
                 "You are using a Python older than 3.10. Update Python and install again."],
                ["ValueError: Unclosed marker, SyntaxWarning: invalid escape sequence, or "
                 "markers that show up literally or toggle a style by accident",
                 "See Text Markers: they only work in paragraphs and table cells, and a literal "
                 "marker needs a backslash before each of its characters, written in a raw "
                 "string."],
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
                 "the browser uses another font, so lines can look slightly different."],
                ["TypeError: unexpected keyword argument 'loop_limit', 'easing', 'fade' or 'focus'",
                 "Not every animation takes every parameter. Only ambient animations and Sequence "
                 "take loop_limit. PopIn, PopOut, FlickerIn, FlickerOut, GlitchIn, GlitchOut, Show "
                 "and Hide have a fixed timing and no easing: change the duration. FadeIn, "
                 "FadeOut, Flicker and Glitch have no fade or focus."],
                ["TypeError: a step must be an animation, or easing must be an Easing",
                 "Animations and easings are objects, so they need parentheses: RiseIn(), not "
                 "RiseIn, and EaseOut(), not EaseOut. Names in quotes, such as \"rise\" or "
                 "\"ease-out\", are not accepted."],
                ["The loop_limit of my sequence does nothing",
                 "When the last step is infinite, the sequence never reaches its end, so it "
                 "cannot repeat. Use a finite last step."],
                ["The animation does not play",
                 "Open the file in a browser and reload the page: without a loop, an animation "
                 "plays once when the image loads, and some image viewers do not play "
                 "animations. To replay it, see Repeating. Nothing plays for people who turned "
                 "on reduce motion."],
                ["An ambient animation plays once, or stops moving after a while",
                 "Ambient animations play once by default: use loop_limit=4 for five runs or "
                 "loop_limit=None for no limit. Shake and Jelly also lose strength on purpose and "
                 "stop after a few swings: use shakes or wobbles to lengthen them."],
                ["The block disappears and never comes back",
                 "An exit ends with the block hidden. To bring it back, put an entrance after "
                 "it in a Sequence, or make the sequence infinite with loop_limit=None."],
                ["The block jumps between two steps of a sequence",
                 "svgblock does not blend the steps of a sequence: each one starts from its own "
                 "state. Choose steps that fit together, or separate them with a Show step."],
                ["The block is cropped while it moves",
                 "The block is only visible inside the image. Entrances and exits come from "
                 "outside it, so they can start or end cropped. With fade=False, a large "
                 "distance makes the block start outside the image. Reduce the distance or "
                 "keep the fade on."],
                ["The block looks smaller than width, or the image is much taller with Rotate",
                 "Animations that make the block bigger than normal (Pulse, Jelly, Glitch, or Zoom "
                 "with a scale above 1) and ambient animations that move, turn or blur it get room "
                 "inside the image, so the block rests smaller than width and is never cropped. "
                 "Rotate asks for the most: a full turn needs room for a whole circle. Use a "
                 "smaller angle, as in Rotate(angle=30), or Sway."],
                ["A theme changed in blocks where I did not expect it, or my theme edit has no effect",
                 "Theme.NAME.value.update(...) changes the shared theme for the whole program, and "
                 "only blocks drawn after the change use the new colors. To change a single block, "
                 "edit a copy made with Theme.NAME.value.copy(). Check also that the color name is "
                 "spelled exactly as in ThemeData."],
                ["The block does not show on my page",
                 "Check that the path in the img tag matches the file name exactly (paths are case "
                 "sensitive on most servers, including GitHub) and that the .svg file is "
                 "published together with the page."],
            ],
            weights=(2, 5),
        )
    )
