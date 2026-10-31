from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from src.svgblock import (Block, Column, Theme, ThemeData, BaseAnimation,
                          Drop, Fade, Sequence, Show, animations)

ANIMATION_NAMES = {
    name: value
    for name, value in vars(animations).items()
    if isinstance(value, type)
}

ASSETS_DIR = Path("assets")
LOGO_PATH = (ASSETS_DIR / "svgblock_logo.png").as_posix()

DOC_THEME = Theme.NEON
DOC_WIDTH = 800
DOC_ANIMATION = Fade()

THEME_WIDTH = 500
ANIMATION_WIDTH = 400
PREVIEW_REST_SECONDS = 3

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

Builder = Callable[[], Block]


@dataclass(frozen=True)
class Asset:
    filename: str
    build: Builder


class Pipeline:
    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._assets: list[Asset] = []

    def add(self, filename: str, build: Builder) -> None:
        if any(asset.filename == filename for asset in self._assets):
            raise ValueError(f"Asset '{filename}' is already registered.")
        self._assets.append(Asset(filename, build))

    def asset(self, filename: str) -> Callable[[Builder], Builder]:
        """Decorator that registers a zero-argument function returning a Block."""

        def register(build: Builder) -> Builder:
            self.add(filename, build)
            return build

        return register

    def run(self) -> None:
        for asset in self._assets:
            path = (self._output_dir / asset.filename).as_posix()
            asset.build().save(path)
            print(f"  ✓ {asset.filename}")
        print(f"{len(self._assets)} assets written to {self._output_dir}/")


pipeline = Pipeline(ASSETS_DIR)


def doc_block(animation: BaseAnimation | None = DOC_ANIMATION) -> Block:
    return Block(DOC_THEME, DOC_WIDTH, animation=animation)


# ---------------------------------------------------------------------------
# Shared data
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Category:
    slug: str
    title: str
    description: str
    themes: tuple[str, ...]  # lowercase names of Theme members


CATEGORIES: tuple[Category, ...] = (
    Category("dark", "Dark Colors", "Simple, bold, and deep classic colors.",
             ("red", "orange", "yellow", "green", "blue", "purple", "pink", "obsidian")),
    Category("light", "Light Colors (Pastels)",
             "Beautifully tinted light backgrounds for a clean and fresh look.",
             ("mint", "chocomint", "lavender", "peach", "sky")),
    Category("seasons", "Seasons", "Earthy and atmospheric palettes inspired by the natural world.",
             ("spring", "summer", "autumn", "winter")),
    Category("drinks", "Drinks", "Warm tones and aesthetics inspired by classic beverages.",
             ("wine", "beer", "coffee", "matcha", "berrymatcha", "latte")),
    Category("countries", "Countries & Geography", "Colors inspired by flags and cultural landmarks.",
             ("brazil", "usa", "miami", "france", "japandark", "japanlight", "sakura",
              "india", "china", "mexico", "fiesta", "greece", "egypt")),
    Category("aesthetics", "Aesthetics & Culture",
             "Highly stylized themes based on internet cultures and artistic movements.",
             ("neon", "cyberpunk", "steampunk", "synthwave", "lofi")),
    Category("dev", "Classical UI (Dev Themes)",
             "Beloved themes from your favorite code editors and IDEs.",
             ("dracula", "mocha", "nord", "solarizeddark", "solarizedlight", "atlas")),
    Category("mythology", "Mythology & Concepts", "Epic, concept-driven abstract aesthetics.",
             ("heaven", "hell", "abyss")),
)

DISPLAY_NAMES: dict[str, str] = {
    "chocomint": "Choco Mint",
    "berrymatcha": "Berry Matcha",
    "japandark": "Japan Dark",
    "japanlight": "Japan Light",
    "solarizeddark": "Solarized Dark",
    "solarizedlight": "Solarized Light",
}

THEME_COLORS: tuple[tuple[str, str], ...] = (
    ("background_center", "The center of the radial glow in the background."),
    ("background_edge", "The outer color of the background, at the edges of the block."),
    ("border_start", "The start of the border gradient (top left)."),
    ("border_end", "The end of the border gradient (bottom right)."),
    ("title_text", "The text of titles."),
    ("title_bar", "The bar on the left of titles."),
    ("subsection_text", "The text of subsections."),
    ("subsection_marker", "The dot on the left of subsections."),
    ("text", "Regular paragraphs."),
    ("highlight", "Highlighted words (also drawn in bold)."),
    ("underline", "Underlined words."),
    ("strikethrough", "Struck-through words."),
    ("italic", "Italic words."),
    ("table_background", "The background of the table body."),
    ("table_header_background", "The background of the table header row."),
    ("table_header_text", "The text of the table header."),
    ("table_text", "The text of table cells."),
    ("table_divider", "The lines between rows and columns."),
    ("table_stripe_background", "The background of striped rows."),
    ("table_border", "The outer border of the table."),
    ("divider", "The line drawn by the divider component."),
)


@dataclass(frozen=True)
class AnimationExample:
    """A preview box in the Animations section.

    The code is run to build the animation, so what the box shows is always
    what the preview does. With replay=True the preview adds a rest and
    starts over by itself, so nobody needs to reload the page.
    """

    slug: str
    title: str
    code: str
    replay: bool = False


BASE_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "fade", "FADE",
        "Fade()", replay=True),
    AnimationExample(
        "rise", "RISE",
        "Rise()", replay=True),
    AnimationExample(
        "drop", "DROP",
        "Drop()", replay=True),
    AnimationExample(
        "pop", "POP",
        "Pop()", replay=True),
    AnimationExample(
        "pulse", "PULSE",
        "Pulse(loop_limit=None)"),
)

CUSTOM_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "rise_custom", "RISE, CUSTOMIZED",
        "Rise(distance=80, duration=1.6, fade=False)", replay=True),
    AnimationExample(
        "drop_custom", "DROP, CUSTOMIZED",
        "Drop(distance=20, duration=0.4)", replay=True),
    AnimationExample(
        "pop_custom", "POP, CUSTOMIZED",
        "Pop(start_scale=0.3, duration=1.2)", replay=True),
    AnimationExample(
        "pulse_custom", "PULSE, CUSTOMIZED",
        "Pulse(amount=0.1, duration=1, loop_limit=4)", replay=True),
)

EASING_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "easing_back", "OVERSHOOT",
        "Rise(easing=EaseOutBack())", replay=True),
    AnimationExample(
        "easing_bezier", "CUSTOM CURVE",
        "Rise(easing=CubicBezier(0.4, 0, 0.2, 1))", replay=True),
    AnimationExample(
        "easing_steps", "STEPS",
        "Rise(easing=Steps(10))", replay=True),
)

COMBO_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample(
        "seq_pop_show", "POP SHOW",
        "Sequence(Pop(), Show(3), loop_limit=None)"),
    AnimationExample(
        "seq_hide_pulse_show", "HIDE, PULSE, SHOW",
        "Sequence(Hide(0.5), Rise(), Pulse(loop_limit=1), Show(2), loop_limit=None)")
)

ANIMATION_EXAMPLES: tuple[AnimationExample, ...] = (
    BASE_EXAMPLES + CUSTOM_EXAMPLES + EASING_EXAMPLES + COMBO_EXAMPLES
)


def validate_categories() -> None:
    all_themes = {theme.name.lower() for theme in Theme}
    listed = [theme for category in CATEGORIES for theme in category.themes]
    missing = all_themes - set(listed)
    unknown = set(listed) - all_themes
    duplicated = {theme for theme in listed if listed.count(theme) > 1}
    if missing or unknown or duplicated:
        raise ValueError(
            f"CATEGORIES out of sync with Theme: missing={sorted(missing)}, "
            f"unknown={sorted(unknown)}, duplicated={sorted(duplicated)}"
        )


def validate_theme_colors() -> None:
    documented = {name for name, _ in THEME_COLORS}
    declared = set(ThemeData.__annotations__)
    if documented != declared:
        raise ValueError(
            f"THEME_COLORS out of sync with ThemeData: "
            f"missing={sorted(declared - documented)}, "
            f"unknown={sorted(documented - declared)}"
        )


# ---------------------------------------------------------------------------
# README: header
# ---------------------------------------------------------------------------


@pipeline.asset("hero.svg")
def hero() -> Block:
    return doc_block().image(LOGO_PATH)


@pipeline.asset("intro.svg")
def intro() -> Block:
    return (
        doc_block()
        .title("Welcome to svgblock")
        .text("Themed, animated blocks of text, tables and images, saved as a single **.svg** "
              "file. Use them in READMEs, web pages, documentation, or anywhere an image fits.")
        .divider()
        .text("With a few lines of Python you get a block with a gradient border, a glowing "
              "background and an animation. You pick a **theme** and an **animation**, and "
              "svgblock takes care of colors, spacing, line breaks and the height of the block.")
        .text("It is plain Python with no external dependencies, and **50 ready-made themes** "
              "are included. You can also edit them or create your own without touching the "
              "library's code.")
        .text("##Every block in this README was made with svgblock itself.##")
    )


@pipeline.asset("toc.svg")
def toc() -> Block:
    return doc_block().title("Table of Contents")


# ---------------------------------------------------------------------------
# README: how a block is built
# ---------------------------------------------------------------------------


@pipeline.asset("how_it_is_built.svg")
def how_it_is_built() -> Block:
    return (
        doc_block()
        .title("How a Block Is Built")
        .text("A block is a stack of **components** inside a frame. You choose what goes inside "
              "and in which order, and the theme provides the colors.")
        .table(
            ["What you see", "What it means"],
            [
                ["Border", "A diagonal gradient between two theme colors, with rounded corners."],
                ["Background", "A radial glow: bright in the center, darker at the edges."],
                ["Title", "A bold line with a small rounded bar on its left."],
                ["Subsection", "A smaller bold line with a dot on its left."],
                ["Text", "A paragraph that breaks into lines by itself and accepts **inline styles**."],
                ["Table", "A grid with header, optional stripes and dividers. Cells accept inline styles too."],
                ["Image", "A picture embedded in the SVG, scaled to fit the available width."],
                ["Columns", "Stacks of components side by side, sized by weight."],
                ["Divider", "A thin line that separates parts of the block. It spans the full width by default."],
                ["Animation",
                    "An optional motion of the whole block. It can enter, pulse, wait and repeat, "
                    "alone or in a sequence."],
            ],
            weights=(1, 3),
        )
        .divider()
        .subsection("Good to know")
        .text("• The **height** of the block is calculated from its content.")
        .text("• Components appear in the order you add them. A block can have any number of titles.")
        .text("• **Text** breaks lines automatically. **Titles and subsections** stay on a single line.")
        .text("• Columns hold anything a block holds, even other columns.")
        .text("• Text is set in Arial, falling back to Helvetica and then to the default "
              "sans-serif font. You choose the size.")
    )


# ---------------------------------------------------------------------------
# README: how to use
# ---------------------------------------------------------------------------


@pipeline.asset("use_overview.svg")
def use_overview() -> Block:
    return (
        doc_block()
        .title("How to Use")
        .text("Install svgblock, describe a block in Python and save it. The result is an "
              "ordinary **.svg** file that you can use anywhere an image works.")
    )


@pipeline.asset("use_step_1.svg")
def use_step_1() -> Block:
    return (
        doc_block()
        .title("Step 1: Install svgblock")
        .text("svgblock is published on PyPI and needs **Python 3.10 or newer**. Install it "
              "with pip:")
    )


@pipeline.asset("use_step_2.svg")
def use_step_2() -> Block:
    return (
        doc_block()
        .title("Step 2: Write your first block")
        .text("Create a file called **generate_blocks.py** with the code below. Every line of "
              "the chain adds something to the block, in order. The last one, .save(...), "
              "writes the file and creates the folder if it does not exist.")
    )


@pipeline.asset("use_step_3.svg")
def use_step_3() -> Block:
    return (
        doc_block()
        .title("Step 3: Run the script")
        .text("When it finishes, the file **assets/block.svg** is ready. Open it in your "
              "browser to see the result and the animation. Reload the page to watch "
              "the animation again.")
    )


@pipeline.asset("use_step_4.svg")
def use_step_4() -> Block:
    return (
        doc_block()
        .title("Step 4: Use the SVG")
        .text("Reference the file wherever you show images: an HTML page, a Markdown file, a "
              "README or a documentation site.")
        .divider()
        .text("The width in the HTML only resizes the image. The real size of the block is the "
              "width you passed to Block(...). Use the same value, or a smaller one, to keep "
              "the text readable.")
    )


@pipeline.asset("use_more.svg")
def use_more() -> Block:
    return (
        doc_block()
        .subsection("Optional: add more blocks")
        .text("A single script can create as many blocks as you want, each saved in its own "
              "file, with its own theme and animation.")
    )


@pipeline.asset("use_local.svg")
def use_local() -> Block:
    return (
        doc_block()
        .subsection("Optional: use the repository locally")
        .text("To work with the source code, clone the repository and install it in "
              "**editable mode**. Changes you make to the code take effect right away. "
              "You do not need this to edit or create themes: that works with the "
              "regular pip installation.")
    )


# ---------------------------------------------------------------------------
# README: building a block
# ---------------------------------------------------------------------------


@pipeline.asset("building_create.svg")
def building_create() -> Block:
    return (
        doc_block()
        .title("Building a Block")
        .text("Everything in svgblock revolves around one class, **Block**. You create it, add "
              "content with chained methods and save it.")
        .subsection("Creating a block")
        .table(
            ["Parameter", "Default", "What it does"],
            [
                ["theme", "Theme.NEON",
                 "A member of the Theme enum, or your own ThemeData. It defines every color. "
                 "See Themes."],
                ["width", 800, "The width of the block, in pixels. The height is calculated for you."],
                ["padding", 24,
                 "The space between the border and the content, in pixels. It is 0 when "
                 "hide_frame is True."],
                ["animation", "None",
                 "How the block moves: an animation such as Rise() or a Sequence(...). "
                 "Without it the block is static. See Animations."],
                ["hide_frame", "False",
                 "Hides the border and the background. With True, only the content is drawn."],
            ],
            align=("left", "center", "left"),
            weights=(2, 2, 5),
        )
        .text("Every parameter is optional: Block() alone gives you a static block. Pass "
              "them by name, as in Block(width=900, animation=Rise()).")
    )


@pipeline.asset("building_content.svg")
def building_content() -> Block:
    return (
        doc_block()
        .title("Adding Content")
        .text("Call each method **any number of times and in any order**. Every method "
              "returns the block, so they can be chained.")
        .table(
            ["Method", "What it adds", "Default"],
            [
                [".title(text, font_size)",
                 "A bold title with the side bar.", "20"],
                [".subsection(text, font_size)",
                 "A bold subsection title with a dot.", "17"],
                [".text(text, font_size)",
                 "A paragraph that breaks lines by itself and accepts markers.", "16"],
                [".image(path, width)",
                 "An image embedded in the SVG.", "natural width"],
                [".table(columns, rows, ...)",
                 "A themed table.", "see Tables"],
                [".columns(*columns)",
                 "Columns of components side by side.", "see Columns"],
                [".divider(coverage)",
                 "A thin line that separates parts of the block.", "1"],
            ],
            align=("left", "left", "center"),
            weights=(3, 4, 2),
        )
        .subsection("About dividers")
        .text("The coverage is the share of the width the line occupies, from 0 to 1. The line "
              "below uses the default, 100%:")
        .divider()
        .text("And this one uses a coverage of 0.6, so it is shorter and centered:")
        .divider(0.6)
        .text("A coverage of 0 draws nothing, which makes it a handy way to add a larger gap "
              "between two pieces of text, as in the space right below.")
        .divider(0)
        .divider(0)
        .text("Back to normal spacing.")
    )


@pipeline.asset("markers.svg")
def markers() -> Block:
    return (
        doc_block()
        .title("Text Markers")
        .text("Wrap words in markers to style them inline. Each style has its own color in the theme.")
        .table(
            ["Marker", "Style", "Theme color", "Result"],
            [
                [r"\*\*word\*\*", "Highlight (bold)", "highlight", "**word**"],
                [r"\_\_word\_\_", "Underline", "underline", "__word__"],
                [r"\-\-word\-\-", "Strikethrough", "strikethrough", "--word--"],
                [r"\#\#word\#\#", "Italic", "italic", "##word##"],
            ],
            align=("left", "left", "left", "center"),
            weights=(3, 3, 3, 2),
        )
        .subsection("Combining markers")
        .text("Markers can be combined and nested: **highlight and __underline__ together**, or "
              "##italic with --strikethrough-- inside##. A word with several markers is drawn in "
              "the color of the innermost one, and highlight always adds bold.")
        .subsection("Escaping")
        .text(r"To show a literal marker, put a backslash before each of its characters: type "
              r"\\\*\\\* to get \*\*. A backslash before any other character stays as it is.")
        .text("Use a raw string (an r before the opening quote) so Python does not read the "
              "backslashes as escape sequences.")
        .subsection("Good to know")
        .text("• Every marker must be closed, otherwise svgblock raises a ValueError.")
        .text("• Markers work in .text() and in table cells. Titles, subsections and table "
              "headers are drawn as plain bold text, so markers show up literally there.")
        .text(r"• Text that contains these pairs by accident, such as a double hyphen used as a "
              r"dash or a name like \_\_init\_\_, needs the backslash too.")
    )


@pipeline.asset("columns.svg")
def columns() -> Block:
    return (
        doc_block()
        .title("Columns")
        .text("Use .columns() to place stacks of components side by side. Each Column takes a "
              "**weight** that sets its share of the width (the default is 1).")
        .text("A column holds anything a block holds: titles, text, tables, images, dividers and "
              "even other columns. The row is as tall as its tallest column.")
        .divider()
        .text("Live example, with weights 1 and 2:")
        .columns(
            Column(1).subsection("Weight 1").text(
                "A narrow column."),
            Column(2)
            .subsection("Weight 2")
            .text("A column twice as wide."),
        )
    )


@pipeline.asset("tables.svg")
def tables() -> Block:
    return (
        doc_block()
        .title("Tables")
        .text("Use .table(columns, rows) to draw a themed table with a header, optional stripes, "
              "dividers and rounded borders. Cells accept **inline styles**.")
        .subsection("Options")
        .table(
            ["Option", "Default", "What it does"],
            [
                ["font_size", 14, "The size of the table text."],
                ["cell_padding", 8, "The space around the text of each cell."],
                ["border_radius", 8, "How rounded the corners of the table are."],
                ["align", "left", "A list with left, center or right for each column."],
                ["weights", "equal", "The relative width of each column."],
                ["striped", "True", "Alternates the background of the rows."],
                ["row_dividers", "True", "Draws a line between rows."],
                ["column_dividers", "False", "Draws a line between columns."],
            ],
            align=("left", "center", "center"),
            weights=(2, 1, 4),
        )
        .subsection("Values")
        .text("Booleans become ✓ and ✗, None becomes an empty cell and numbers are converted to "
              "text. Every row needs as many cells as there are columns. Long words are broken "
              "inside narrow columns.")
        .divider()
        .text("Live example, with the alignment set per column:")
        .table(
            ["Language", "Level", "Typed"],
            [
                ["Python", "**Advanced**", True],
                ["Rust", "##Learning##", True],
                ["COBOL", "--Retired--", None],
            ],
            align=("left", "center", "center"),
            weights=(2, 2, 1),
            striped=True,
            row_dividers=True,
            column_dividers=True,
        )
    )


@pipeline.asset("images.svg")
def images() -> Block:
    return (
        doc_block()
        .title("Images")
        .text("Use .image(path, width) to embed a picture. The file is read when the script runs "
              "and embedded in the SVG, so the result is a single self-contained file.")
        .text("Without a width, the image uses its natural size. It always fits the available "
              "space and keeps its aspect ratio. Large images make the .svg file larger, so "
              "small files work best.")
        .divider()
        .text("Combine an image with columns to put a picture beside some text:")
        .columns(
            Column().divider(0).image(LOGO_PATH, 350).divider(0),
            Column()
            .subsection("A logo beside the text")
            .text("The image sits in a column and the text takes the rest of the width."),
        )
    )


@pipeline.asset("saving.svg")
def saving() -> Block:
    return (
        doc_block()
        .title("Saving the Result")
        .table(
            ["Method", "What it does"],
            [
                [".save(path)", "Writes the .svg file, creating the folders of the path if needed."],
                [".render()", "Returns the SVG as a string, without writing any file."],
            ],
            weights=(1, 3),
        )
    )


# ---------------------------------------------------------------------------
# README: animations
# ---------------------------------------------------------------------------


@pipeline.asset("animations.svg")
def animations_overview() -> Block:
    return (
        doc_block()
        .title("Animations")
        .text("An animation moves the whole block when the image is displayed. You create it "
              "from one of the animation classes and hand it to the block with the "
              "**animation** parameter. Without the parameter, the block is static.")
        .table(
            ["Animation", "Kind", "What it does"],
            [
                ["Fade()", "entrance", "The block fades in."],
                ["Rise()", "entrance",
                 "The block rises from below while fading in."],
                ["Drop()", "entrance",
                 "The block drops from above while fading in."],
                ["Pop()", "entrance",
                 "The block grows from a smaller size while fading in."],
                ["Pulse()", "ambient",
                 "The block grows and shrinks gently, staying in place."],
                ["Show(duration)", "utility",
                 "The block stays visible and still for a while. Used inside a sequence."],
                ["Hide(duration)", "utility",
                 "The block stays hidden for a while. Used inside a sequence."],
                ["Sequence(...)", "utility",
                 "Plays several animations one after another."],
            ],
            weights=(4, 2, 6),
        )
        .subsection("Three ways to choose an animation")
        .table(
            ["Form", "Example", "Use it to"],
            [
                ["Default values", "animation=Rise()",
                 "Get an animation exactly as it comes."],
                ["A configured animation", "animation=Rise(distance=80)",
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


@pipeline.asset("animations_base.svg")
def animations_base() -> Block:
    return (
        doc_block()
        .title("Base Animations")
        .text("These are the animations with their default values. The previews below replay "
              "by themselves, so you do not need to reload the page.")
        .subsection("Entrances")
        .text("**Fade**, **Rise**, **Drop** and **Pop** start hidden or away from their place "
              "and end in place. They play once, when the image loads.")
        .subsection("Ambient")
        .text("**Pulse** keeps the block visible and in place, with a gentle movement. It plays "
              "once by default: use **loop_limit** to repeat it, or to make it infinite.")
    )


@pipeline.asset("animations_parameters.svg")
def animations_parameters() -> Block:
    return (
        doc_block()
        .title("Parameters")
        .text("Every parameter is optional and passed by name, as in "
              "**Rise(distance=60)**. The only values passed by position are the duration "
              "of **Show** and **Hide**, which is required, and the animations of a "
              "**Sequence**.")
        .subsection("Defaults")
        .table(
            ["Animation", "Parameters and default values"],
            [
                ["Fade", "duration=0.8, easing=EaseOut()"],
                ["Rise", "distance=40, fade=True, duration=0.8, easing=EaseOutQuint()"],
                ["Drop", "distance=40, fade=True, duration=0.8, easing=EaseOutQuint()"],
                ["Pop", "start_scale=0.8, fade=True, duration=0.6, easing=EaseOutBack()"],
                ["Pulse", "amount=0.06, duration=2, easing=EaseInOut(), loop_limit=0"],
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
                 "How the speed changes during the run. See Easings."],
                ["distance", "A number, 0 or more",
                 "How many pixels the block travels in **Rise** and **Drop**. With 0 the "
                 "block does not move."],
                ["fade", "True or False",
                 "Whether **Rise**, **Drop** and **Pop** also fade in. With False the block "
                 "is fully visible while it moves."],
                ["start_scale", "A number greater than 0",
                 "The starting size in **Pop**, where 1 is the normal size: 0.8 starts at 80%."],
                ["amount", "A number greater than 0",
                 "How much **Pulse** grows at its peak: 0.06 means 6% bigger."],
                ["loop_limit", "A whole number from 0 to 1000, or None",
                 "How many times the animation runs again after its first run, in **Pulse** "
                 "and **Sequence**. None means no limit. See Repeating."],
            ],
            weights=(2, 3, 6),
        )
        .text("Customized animations are shown below. Each box shows the code that produced it.")
    )


@pipeline.asset("animations_easings.svg")
def animations_easings() -> Block:
    return (
        doc_block()
        .title("Easings")
        .text("An easing sets how the speed changes while an animation runs: it can start "
              "slow, end slow, go past the final position and come back, or move in jumps. "
              "Pass one to the **easing** parameter of any animation, as in "
              "**Rise(easing=EaseInOut())**.")
        .table(
            ["Easing", "What it does"],
            [
                ["Linear()", "Constant speed from start to end."],
                ["EaseIn()", "Starts slow and speeds up."],
                ["EaseOut()",
                 "Starts fast and slows down until it stops. The default of **Fade**."],
                ["EaseInOut()",
                 "Slow at the start and at the end, fast in the middle. The default of "
                 "**Pulse**."],
                ["EaseOutQuint()",
                 "Starts very fast and settles slowly, like a soft landing. The default of "
                 "**Rise** and **Drop**."],
                ["EaseOutBack()",
                 "Goes a little past the final value and then comes back. The default of "
                 "**Pop**."],
                ["CubicBezier(x1, y1, x2, y2)",
                 "A curve of your own. See below."],
                ["Steps(count)",
                 "Jumps between that many equal steps instead of moving smoothly."],
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
              "no easing.")
        .divider()
        .text("Examples are shown below. Each box shows the code that produced it.")
    )


@pipeline.asset("animations_repeating.svg")
def animations_repeating() -> Block:
    return (
        doc_block()
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
        .text("• **Pulse** and **Sequence** accept loop_limit.")
        .text("• **Fade**, **Rise**, **Drop** and **Pop** play once and do not accept it. To "
              "replay an entrance, put it in a **Sequence** with a **Show** step and make "
              "the sequence infinite.")
    )


@pipeline.asset("animations_sequence.svg")
def animations_sequence() -> Block:
    return (
        doc_block()
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
              "connection between steps. After a Rise the block is in place, so a second "
              "entrance right after it makes the block jump back to its starting state and "
              "enter again. You choose steps that fit together, and **Show** is the natural "
              "way to separate them.")
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
              "that step. If the last step is **Hide**, the block stays hidden.")
        .divider()
        .text("Combined animations are shown below. Each box shows the code that produced it.")
    )


@pipeline.asset("animations_errors.svg")
def animations_errors() -> Block:
    return (
        doc_block()
        .title("Errors")
        .table(
            ["Situation", "What happens"],
            [
                ["duration is 0 or negative", "ValueError."],
                ["distance is negative", "ValueError."],
                ["start_scale or amount is 0 or negative", "ValueError."],
                ["loop_limit is negative or greater than 1000", "ValueError."],
                ["x1 or x2 of CubicBezier is outside 0 to 1", "ValueError."],
                ["count of Steps is not a whole number of 1 or more", "ValueError."],
                ["loop_limit passed to Fade, Rise, Drop or Pop",
                 "TypeError: these animations do not accept it."],
                ['An easing that is not an easing object, such as easing="ease-out" '
                 "or easing=EaseOut",
                 "TypeError."],
                ["A sequence step that is not an animation, such as Rise without "
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
        .text("• The block is only visible inside the image. With fade=False and a large "
              "distance, the block starts outside the image and slides in from its edge.")
        .text("• Animations that make the block grow, such as Pulse, get room inside the "
              "image: the block rests slightly smaller than width, so it is never cropped. "
              "In a sequence, the room fits the step that grows the most. The image keeps "
              "the width you passed.")
        .text("• Without a loop, an animation plays once when the image loads. Reload the "
              "page to see it again.")
        .text("• Some image viewers and editors do not run animations. Open the file in a "
              "browser to check.")
    )


def build_animation(example: AnimationExample) -> BaseAnimation:
    animation = eval(
        example.code, {"__builtins__": {}, **ANIMATION_NAMES})
    if example.replay:
        return Sequence(
            animation, Show(PREVIEW_REST_SECONDS), loop_limit=None)
    return animation


def animation_showcase(example: AnimationExample) -> Block:
    return (
        Block(DOC_THEME, ANIMATION_WIDTH, animation=build_animation(example))
        .title(example.title)
        .text(f"**__{example.code}__**", font_size=14)
    )


for _example in ANIMATION_EXAMPLES:
    pipeline.add(f"animation_{_example.slug}.svg",
                 partial(animation_showcase, _example))


# ---------------------------------------------------------------------------
# README: customization
# ---------------------------------------------------------------------------


@pipeline.asset("customization.svg")
def customization() -> Block:
    return (
        doc_block()
        .title("Customization")
        .subsection("What you can change")
        .table(
            ["What", "How", "Where"],
            [
                ["Colors and visual style", "Pick a ready-made theme",
                 "theme=Theme.NAME in Block(...)"],
                ["A ready-made theme", "Change some of its colors",
                 "Theme.NAME.value.update(...). See Editing a Theme"],
                ["A new theme", "Create a ThemeData with every color",
                 "theme=your_theme in Block(...). See Creating Your Own Theme"],
                ["Animation", "Pick one, configure it or chain several",
                 "animation= in Block(...). See Animations"],
                ["How an animation accelerates", "Pick an easing curve",
                 "easing= in the animations. See Easings"],
                ["Width of the block", "Set a number of pixels",
                 "width= in Block(...)"],
                ["Space around the content", "Set a number of pixels",
                 "padding= in Block(...)"],
                ["Border and background", "Hide them",
                 "hide_frame=True in Block(...)"],
                ["Size of the text", "Set a number of pixels",
                 "font_size= in .title(), .subsection() and .text()"],
                ["Look of a table", "Pass options to the table", "See Tables"],
                ["Spacing and sizes", "Edit the constants",
                    "See Constants Reference"],
            ],
            weights=(3, 3, 5),
        )
    )


@pipeline.asset("custom_theme.svg")
def custom_theme() -> Block:
    return (
        doc_block()
        .title("Creating Your Own Theme")
        .text("A theme is a **ThemeData**: a dictionary that holds the colors of a block. Create "
              "one in your own code and pass it to **Block(theme=...)**, exactly like a "
              "ready-made theme.")
        .text(f"Every ThemeData has these **{len(THEME_COLORS)} colors**, written as "
              "hexadecimal values (#RRGGBB):")
        .table(["Color", "What it paints"], [list(color) for color in THEME_COLORS], weights=(2, 3))
        .divider()
        .subsection("Good to know")
        .text("• Give every color. Python does not check a ThemeData while the program runs, so "
              "a missing color only shows up as an error when the block is drawn. Editors with "
              "type checking point it out earlier.")
        .text("• The background is a radial glow, so give the two background colors some "
              "difference: with the same color in both, the glow is invisible.")
        .text("• Choose text colors with good contrast against the background. Inline styles are "
              "drawn over the same background as regular text.")
    )


@pipeline.asset("edit_theme.svg")
def edit_theme() -> Block:
    return (
        doc_block()
        .title("Editing a Theme")
        .text("Every ready-made theme is a member of the **Theme** enum, and its colors are in "
              "**.value**, which is a ThemeData. Change some of them with **.update(...)**, "
              "passing only the colors you want to replace. The library files stay untouched.")
        .subsection("The change applies to the whole program")
        .text("Ready-made themes are shared. After Theme.RED.value.update(...), every block that "
              "uses Theme.RED gets the new colors, until the program ends. Make the change "
              "**before** you build the blocks that use it.")
        .subsection("Keeping the original")
        .text("To get a variation and still use the original somewhere else, make a copy with "
              "**.value.copy()**, change the copy and pass it to Block. The ready-made theme is "
              "not affected.")
        .divider()
        .text("A copy is also the quickest way to create a theme: start from one that is close "
              "to what you want and change only the colors that differ.")
    )


@pipeline.asset("constants.svg")
def constants() -> Block:
    return (
        doc_block()
        .title("Constants Reference")
        .text("Constants at the top of each file of the **svgblock/** folder control the "
              "details of the layout. With the repository installed in editable mode, "
              "your changes take effect right away.")
        .table(
            ["File", "Constants", "What it controls"],
            [
                ["composer.py", "TITLE_FONT_SIZE, SUBSECTION_FONT_SIZE, TEXT_FONT_SIZE, COMPONENT_GAP, "
                                "COLUMN_GAP, DEFAULT_COLUMN_WEIGHT",
                 "Default font sizes, the space between components, the space between columns and the default column weight."],
                ["components.py (text)", "LINE_HEIGHT_RATIO, BASELINE_RATIO, BOLD_WEIGHT",
                 "The height of each line and the weight of bold text."],
                ["components.py (title, subsection)", "TITLE_BAR_WIDTH, TITLE_BAR_HEIGHT_RATIO, TITLE_BAR_GAP, "
                                                      "SUBSECTION_MARKER_RADIUS_RATIO, SUBSECTION_MARKER_GAP",
                 "The size of the title bar and the subsection dot, and their distance to the text."],
                ["components.py (table)", "TABLE_FONT_SIZE, TABLE_CELL_PADDING, TABLE_BORDER_RADIUS, "
                                          "TABLE_LINE_WIDTH, TRUE_SYMBOL, FALSE_SYMBOL",
                 "The default look of tables and the symbols drawn for booleans."],
                ["components.py (divider)", "DIVIDER_THICKNESS, DIVIDER_COVERAGE",
                 "The thickness of dividers and their default coverage."],
                ["frame.py", "BORDER_WIDTH, CORNER_RADIUS, BACKGROUND_GLOW_RADIUS",
                 "The border thickness, the rounded corners and how far the background glow spreads."],
            ],
            weights=(3, 5, 5),
        )
        .text("Two good starting points: **COMPONENT_GAP** (a tighter or looser block) and "
              "**BACKGROUND_GLOW_RADIUS** (a more concentrated or more spread glow). The space "
              "around the content and the look of animations are not constants: they are the "
              "**padding** parameter of Block and the parameters of Animation.")
        .text("Line breaks are calculated with the widths of the Arial font. If something "
              "looks off after a change, restore the original values.")
    )


# ---------------------------------------------------------------------------
# README: themes
# ---------------------------------------------------------------------------


@pipeline.asset("themes_overview.svg")
def themes_overview() -> Block:
    return (
        doc_block()
        .title("Themes")
        .text("A theme defines every color of a block: the border gradient, the glowing "
              "background, titles, subsections, text, inline styles, tables and dividers. ")
        .text("The ready-made themes are the members of the **Theme** enum. To use one, pass it "
              "to the block: **__theme=Theme.NAME__**.")
        .text("Want to tweak a theme or build your own? See Customization.")
        .divider()
        .table(
            ["Category", "Themes"],
            [[category.title, len(category.themes)]
             for category in CATEGORIES],
            align=("left", "center"),
            weights=(4, 1),
        )
    )


def category_header(index: int, category: Category) -> Block:
    keys = ", ".join(f"**{key.upper()}**" for key in category.themes)
    return (
        doc_block()
        .title(f"{index}. {category.title}")
        .text(category.description)
        .text(f"Available themes: {keys}")
    )


def theme_showcase(theme: Theme) -> Block:
    key = theme.name.lower()
    name = DISPLAY_NAMES.get(key, key.title())
    return (
        Block(theme, THEME_WIDTH, animation=Drop())
        .title(f"{name.upper()} THEME")
        .text(f"Use it with theme=Theme.{theme.name}.")
        .subsection("Subsection: text and marker")
        .text("Body text has its own color. Inline styles have theirs: **highlight**, "
              "__underline__, --strikethrough--, ##italic## and **__combined__**.")
        .divider()
        .table(
            ["Element", "Colored by"],
            [
                ["Frame", "border and background"],
                ["Title", "text color and side bar"],
                ["**Words**", "highlight and inline styles"],
                ["Table", "header, stripes and lines"],
            ],
            weights=(2, 3),
        )
    )


for _index, _category in enumerate(CATEGORIES, start=1):
    pipeline.add(f"category_{_category.slug}.svg",
                 partial(category_header, _index, _category))

for _theme in Theme:
    pipeline.add(f"block_{_theme.name.lower()}.svg",
                 partial(theme_showcase, _theme))


# ---------------------------------------------------------------------------
# README: troubleshooting and footer
# ---------------------------------------------------------------------------


@pipeline.asset("troubleshooting.svg")
def troubleshooting() -> Block:
    return (
        doc_block()
        .title("Troubleshooting")
        .table(
            ["Problem", "What to check"],
            [
                ["Errors about the | symbol in type hints",
                 "You are using a Python older than 3.10. Update Python and install again."],
                ["NameError: name 'Rise' is not defined",
                 "Animations and easings must be imported, as in from svgblock import Rise, "
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
                 "0 or more."],
                ["ValueError about loop_limit",
                 "loop_limit must be from 0 to 1000, or None for no limit. In a sequence, "
                 "only the last step can be infinite."],
                ["ValueError about x1, x2 or count",
                 "In CubicBezier, x1 and x2 must be between 0 and 1. In Steps, count must be "
                 "a whole number of 1 or more."],
                ["TypeError: unexpected keyword argument 'loop_limit'",
                 "Only Pulse and Sequence accept loop_limit. Fade, Rise, Drop and Pop play "
                 "once. To repeat them, put them in a Sequence."],
                ["TypeError: a step must be an animation, or easing must be an Easing",
                 "Animations and easings are objects, so they need parentheses: Rise(), not "
                 "Rise, and EaseOut(), not EaseOut. Names in quotes, such as \"rise\" or "
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
                ["The block jumps between two steps of a sequence",
                 "svgblock does not blend steps: each one starts from its own state. After an "
                 "entrance the block is in place, and a new entrance starts from its beginning. "
                 "Choose steps that fit together, or separate them with a Show step."],
                ["The block is cropped while it moves",
                 "The block is only visible inside the image. With fade=False, a large "
                 "distance makes the block start outside the image. Reduce the distance or "
                 "keep the fade on."],
                ["The block looks smaller than width with Pulse",
                 "Animations that grow the block get room inside the image, so the block "
                 "rests slightly smaller than width and is never cropped."],
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


@pipeline.asset("footer.svg")
def footer() -> Block:
    return doc_block().text("Made with 💜. If you liked it, leave a ⭐ on the repository!")


if __name__ == "__main__":
    validate_categories()
    validate_theme_colors()
    pipeline.run()
