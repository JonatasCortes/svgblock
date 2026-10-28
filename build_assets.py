from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from src.svgblock import Animation, Block, Column, THEMES

ASSETS_DIR = Path("assets")
LOGO_PATH = (ASSETS_DIR / "svgblock_logo.png").as_posix()

DOC_THEME = "neon"
DOC_WIDTH = 800
DOC_ANIMATION = Animation.FADE

THEME_WIDTH = 500
ANIMATION_WIDTH = 400
ANIMATION_LOOP_SECONDS = 4


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


def doc_block(animation: Animation = DOC_ANIMATION) -> Block:
    return Block(DOC_THEME, DOC_WIDTH, animation)


# ---------------------------------------------------------------------------
# Shared data
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Category:
    slug: str
    title: str
    description: str
    themes: tuple[str, ...]


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

ANIMATION_INFO: dict[str, str] = {
    "fade": "The block fades in. The most discreet one, and the default.",
    "slide-up": "The block fades in while moving up, entering from below.",
    "slide-down": "The block fades in while moving down, entering from above.",
    "slide-left": "The block fades in while moving left, entering from the right.",
    "slide-right": "The block fades in while moving right, entering from the left.",
    "pop": "The block fades in while growing slightly, from a bit smaller to its final size.",
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


def animation_name(animation: Animation) -> str:
    return animation.name.lower().replace("_", "-")


def validate_categories() -> None:
    listed = [theme for category in CATEGORIES for theme in category.themes]
    missing = set(THEMES) - set(listed)
    unknown = set(listed) - set(THEMES)
    duplicated = {theme for theme in listed if listed.count(theme) > 1}
    if missing or unknown or duplicated:
        raise ValueError(
            f"CATEGORIES out of sync with THEMES: missing={sorted(missing)}, "
            f"unknown={sorted(unknown)}, duplicated={sorted(duplicated)}"
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
        .text("Themed and animated text blocks, as **.svg** files, to make your GitHub "
              "profile README beautiful.")
        .divider()
        .text("Do you want your profile README to look like a designed page, instead of plain "
              "Markdown text? Then you are in the right place!")
        .text("svgblock turns a few lines of Python into a single **.svg** image: a block with a "
              "gradient border, a glowing background and an entrance animation. You pick a "
              "**theme** and an **animation**, and the library handles colors, spacing, line "
              "breaks and the height of the block.")
        .text("It is also as light as it can be: **plain Python, no external dependencies** "
              "(only the standard library).")
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
              "and in which order, and the theme chooses every color.")
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
                ["Entrance animation", "Optional. The whole block appears when the page loads, and can repeat on a timer. Chosen by you, never by the theme."],
            ],
            weights=(1, 3),
        )
        .divider()
        .subsection("Rules you should know")
        .text("• The **height** of the block is calculated automatically from its content.")
        .text("• Components appear in the order you add them. A block can have no title, or many.")
        .text("• **Text** breaks lines automatically, but **titles and subsections** stay on a single line.")
        .text("• Columns hold anything a block holds, even other columns.")
        .text("• The **font** is always Arial, falling back to Helvetica and then to the default "
              "sans-serif font. You choose only the size.")
        .text("• **Colors** are never set one by one. They always come from a theme.")
    )


# ---------------------------------------------------------------------------
# README: how to use
# ---------------------------------------------------------------------------

@pipeline.asset("use_overview.svg")
def use_overview() -> Block:
    return (
        doc_block()
        .title("How to Use")
        .text("Follow the steps below in order. In the end you will have a block in your profile.")
        .subsection("Where the files live")
        .text("The blocks are generated **once, on your computer**, and the .svg files are committed "
              "to your **profile repository**, the special repository named exactly like your "
              "GitHub username (for example, Bob/Bob). You do not need a GitHub Action or a token.")
    )


@pipeline.asset("use_step_1.svg")
def use_step_1() -> Block:
    return (
        doc_block()
        .title("Step 1: Install svgblock")
        .text("You need **Python 3.10 or newer**. Check your version, then install the library "
              "directly from the repository. If you prefer, clone the repository and install "
              "it from the folder.")
    )


@pipeline.asset("use_step_2.svg")
def use_step_2() -> Block:
    return (
        doc_block()
        .title("Step 2: Write your first block")
        .text("In the root of your profile repository, create a file called **generate_blocks.py** "
              "with the code below. Every line of the chain adds something to the block, in order. "
              "The last one, .save(...), writes the file and creates the assets folder if it does "
              "not exist.")
    )


@pipeline.asset("use_step_3.svg")
def use_step_3() -> Block:
    return (
        doc_block()
        .title("Step 3: Run the script")
        .text("When it finishes, the file **assets/block.svg** will exist. Open it in your browser "
              "to see the result and the entrance animation. Reload the page to watch the "
              "animation again.")
    )


@pipeline.asset("use_step_4.svg")
def use_step_4() -> Block:
    return (
        doc_block()
        .title("Step 4: Show the block in your profile")
        .text("Add the HTML below to your profile README.md, set the width that best suits it, then "
              "**commit and push** both the .svg file and the change in the README.")
        .divider()
        .text("The width in the HTML only resizes the image. The real size of the block is the "
              "width you passed to Block(...). Use the same value, or a smaller one, so the text "
              "stays readable.")
    )


@pipeline.asset("use_more.svg")
def use_more() -> Block:
    return (
        doc_block()
        .subsection("Optional: add more blocks")
        .text("You can create as many blocks as you want in the same script, each one saved in its "
              "own file and with its own theme and animation.")
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
                ["theme", '"red"',
                    "The name of the theme, which defines every color. See Themes."],
                ["width", 800, "The width of the block, in pixels. The height is calculated for you."],
                ["animation", "None", "The entrance animation. Optional: without it the block is static. See Animations."],
                ["animation_loop", "None",
                    "Seconds between replays of the animation. Without it the animation plays once. See Animations."],
                ["frame", True, "Draws the border and the background. With False, only the content is drawn."],
            ],
            align=("left", "center", "left"),
            weights=(2, 1, 5),
        )
        .text("All parameters are optional. Block() alone already works and gives you a static block.")
    )


@pipeline.asset("building_content.svg")
def building_content() -> Block:
    return (
        doc_block()
        .title("Adding Content")
        .text("You can call each method **any number of times and in any order**. Every method "
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
        .text("The line below is a divider with the default coverage, 100% of the width:")
        .divider()
        .text("And this one was created with a coverage of 0.6, so it is shorter and centered:")
        .divider(0.6)
        .text("The coverage must be at least 0 and at most 1.")
        .divider(0)
        .divider(0)
        .text('**__coverage=0__** can be used to "skip" a line, creating a larger gap between two pieces of text (as shown above).')
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
        .text("Python 3.12 warns about backslashes in normal strings, so use a raw string: put an "
              "r before the opening quote.")
        .subsection("Good to know")
        .text("• Every marker must be closed, otherwise svgblock raises a ValueError.")
        .text("• Markers work in .text() and in table cells. Titles, subsections and table headers "
              "are drawn as plain bold text, so markers show up literally there.")
        .text(r"• Text that contains these pairs by accident, such as a double hyphen used as a dash "
              r"or a name like \_\_init\_\_, needs the backslash too.")
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
                "A narrow column, good for short notes."),
            Column(2)
            .subsection("Weight 2")
            .text("A column twice as wide, ideal for the main text, which breaks its lines by itself."),
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
                ["striped", True, "Alternates the background of the rows."],
                ["row_dividers", True, "Draws a line between rows."],
                ["column_dividers", False, "Draws a line between columns."],
            ],
            align=("left", "center", "left"),
            weights=(2, 1, 4),
        )
        .subsection("Values")
        .text("Booleans become ✓ and ✗, None becomes an empty cell and numbers are converted to "
              "text. Every row needs as many cells as there are columns. Header names are always "
              "plain bold text, and long words are broken inside narrow columns.")
        .divider()
        .text("Live example, with the alignment changed per column:")
        .table(
            ["Language", "Level", "Typed"],
            [
                ["Python", "**Advanced**", True],
                ["Rust", "##Learning##", True],
                ["COBOL", "--Retired--", None],
                ["Brainf*ck", "__Just for fun__", False],
            ],
            align=("left", "center", "center"),
            weights=(2, 2, 1),
        )
    )


@pipeline.asset("images.svg")
def images() -> Block:
    return (
        doc_block()
        .title("Images")
        .text("Use .image(path, width) to embed a picture. The file is read when the script runs "
              "and embedded in the SVG, so the result is a single self-contained file.")
        .text("Without a width, the image uses its natural size. It is never wider than the "
              "available space and always keeps its aspect ratio. Large images make the .svg file "
              "larger, so prefer small files.")
        .divider()
        .text("Combine an image with columns to put a picture beside some text:")
        .columns(
            Column().divider(0).image(LOGO_PATH, 350).divider(0),
            Column()
            .subsection("A logo beside the text")
            .text("The image sits in a narrow column and the text takes the rest of the width. "
                  "The header of this README is built the same way."),
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


@pipeline.asset("animations.svg")
def animations() -> Block:
    return (
        doc_block()
        .title("Animations")
        .text("Animations are **optional**. By default a block is static. Choose an entrance "
              "animation with the **animation** parameter and it plays once, in 0.8 seconds, "
              "when the block appears. The theme never decides it.")
        .table(
            ["Name", "What it does"],
            [["None", "No animation. The block is static. This is the default."],
             *[[name, description] for name, description in ANIMATION_INFO.items()]],
            weights=(1, 4),
        )
        .text("You can pass the name as a string or use the Animation enum, which gives you "
              "autocomplete in your editor.")
        .divider()
        .subsection("Repeating the animation")
        .text("By default the entrance plays once. Pass **animation_loop** with a number of "
              "seconds to replay it over and over, without JavaScript, so it works inside a "
              "README image.")
        .table(
            ["Value", "Behavior"],
            [
                ["None", "The animation plays once. This is the default."],
                ["a number", "The animation repeats every that many seconds."],
            ],
            weights=(1, 4),
        )
        .text("The number is the length of the **whole cycle**, not just the pause. With "
              "animation_loop=5, the entrance takes 0.8 seconds and the block stays still and "
              "visible for the other 4.2, then disappears and enters again.")
        .text("• The value must be **greater than 0.8**, the duration of the entrance.")
        .text("• animation_loop needs an animation. Using it with animation=None raises a ValueError.")
        .text("• Short intervals leave little time to read, so prefer 5 seconds or more for "
              "blocks with a lot of text.")
        .divider()
        .text("People who turned on reduce motion in their system settings see the block with "
              f"no animation at all. The previews below repeat every {ANIMATION_LOOP_SECONDS:g} "
              "seconds, so you do not need to reload the page.")
    )


def animation_showcase(animation: Animation) -> Block:
    name = animation_name(animation)
    return (
        Block(DOC_THEME, ANIMATION_WIDTH, animation,
              animation_loop=ANIMATION_LOOP_SECONDS)
        .title(name.upper())
        .text(f'Use it with **__animation="{name}"__**.')
        .text(ANIMATION_INFO.get(name, "An entrance animation."))
    )


for _animation in Animation:
    pipeline.add(f"animation_{animation_name(_animation)}.svg",
                 partial(animation_showcase, _animation))


# ---------------------------------------------------------------------------
# README: customization
# ---------------------------------------------------------------------------

@pipeline.asset("customization.svg")
def customization() -> Block:
    return (
        doc_block()
        .title("Customization")
        .text("svgblock was made to be simple, so it has **a few things you can choose** and a clear "
              "place to change everything else.")
        .subsection("What you can change")
        .table(
            ["What", "How", "Where"],
            [
                ["Colors and visual style", "Pick a ready-made theme",
                    "theme= in Block(...)"],
                ["Entrance animation", "Pick one of the six options, or none",
                    "animation= in Block(...)"],
                ["Animation replay", "Set the seconds between replays",
                    "animation_loop= in Block(...)"],
                ["Width of the block", "Set a number of pixels",
                    "width= in Block(...)"],
                ["Size of the text", "Set a number of pixels",
                    "font_size= in .title(), .subsection() and .text()"],
                ["Look of a table", "Pass options to the table", "See Tables"],
                ["A new theme", "Add an entry to THEMES", "svgblock/themes.py"],
                ["Anything else", "Edit the constants", "See Constants Reference"],
            ],
            weights=(3, 3, 4),
        )
        .text("The font family is not customizable on purpose: the library measures text using "
              "the widths of the Arial font to break lines correctly, so it always asks for Arial "
              "first, then Helvetica, then the default sans-serif font.")
    )


@pipeline.asset("custom_theme.svg")
def custom_theme() -> Block:
    return (
        doc_block()
        .title("Creating Your Own Theme")
        .text("A theme is an entry in the THEMES dictionary, in the file **svgblock/themes.py**. "
              "The name must be lowercase and it is exactly what you pass to Block(theme=...). "
              f"Every entry needs these **{len(THEME_COLORS)} colors**, all written as "
              "hexadecimal values (#RRGGBB):")
        .table(["Color", "What it paints"], [list(color) for color in THEME_COLORS], weights=(2, 3))
        .divider()
        .text("The background is always a radial glow, so the two background colors need some "
              "difference between them. If you use the same color in both, the glow becomes invisible.")
        .text("Keep a good contrast between the text colors and the background, and remember that "
              "inline styles are drawn over the same background as regular text.")
    )


@pipeline.asset("constants.svg")
def constants() -> Block:
    return (
        doc_block()
        .title("Constants Reference")
        .text("Everything else is controlled by constants at the top of each file of the "
              "**svgblock/** folder. To edit them, install the library from a clone of the "
              "repository in editable mode, so your changes take effect right away.")
        .table(
            ["File", "Constants", "What it controls"],
            [
                ["block.py (defaults)", "DEFAULT_THEME_NAME, DEFAULT_WIDTH, DEFAULT_ANIMATION",
                 "The values used when you do not pass a parameter."],
                ["block.py (layout, font)", "BLOCK_PADDING, FONT_FAMILY",
                 "The space between the border and the content, and the font stack written in the SVG."],
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
                ["animation.py", "ANIMATION_DURATION_SECONDS, SLIDE_DISTANCE_PX, POP_START_SCALE",
                 "How long the entrance takes, how far the slides travel and how small the pop starts."],
            ],
            weights=(3, 5, 5),
        )
        .text("The easiest and most noticeable changes are **ANIMATION_DURATION_SECONDS** (a slower "
              "or faster entrance) and **BACKGROUND_GLOW_RADIUS** (a more concentrated or more "
              "spread glow).")
        .text("Be careful with **FONT_FAMILY**. The line breaks are calculated with the widths of "
              "the Arial font, so a very different font can make lines look too short or too long. "
              "If something looks wrong, restore the original values.")
    )


# ---------------------------------------------------------------------------
# README: themes
# ---------------------------------------------------------------------------

@pipeline.asset("themes_overview.svg")
def themes_overview() -> Block:
    return (
        doc_block()
        .title("Themes")
        .text("A theme defines **only colors**: the border gradient, the glowing background, "
              "titles, subsections, text, inline styles, tables and dividers. The layout, the "
              "font and the animation are the same in every theme, so you can switch themes "
              "without anything else moving.")
        .text('To use a theme, pass its name to the block: theme="japandark".')
        .text("Theme names are lowercase and written together, exactly as listed in each category. "
              "Every preview below shows everything a theme colors.")
        .table(
            ["Category", "Themes"],
            [[category.title, len(category.themes)]
             for category in CATEGORIES],
            align=("left", "center"),
            weights=(4, 1),
        )
    )


def category_header(index: int, category: Category) -> Block:
    keys = ", ".join(f"**{key}**" for key in category.themes)
    return (
        doc_block()
        .title(f"{index}. {category.title}")
        .text(category.description)
        .text(f"Available themes: {keys}")
    )


def theme_showcase(key: str) -> Block:
    name = DISPLAY_NAMES.get(key, key.title())
    return (
        Block(key, THEME_WIDTH, Animation.SLIDE_DOWN)
        .title(f"{name.upper()} THEME")
        .text(f'Use it with theme="{key}".')
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

for _key in THEMES:
    pipeline.add(f"block_{_key}.svg", partial(theme_showcase, _key))


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
                ["ValueError: Unknown theme",
                 "The theme name does not exist. The error message lists every available theme. "
                 "Names are lowercase, exactly as shown in the Themes section."],
                ["ValueError: Unknown animation",
                 "The animation name is wrong. The six valid names are fade, slide-up, slide-down, "
                 "slide-left, slide-right and pop. To have no animation, omit the parameter or pass None."],
                ["ValueError about animation_loop",
                 "animation_loop must be greater than 0.8 seconds, the duration of the entrance, "
                 "and it needs an animation. Pass animation=... together with it."],
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
                ["Errors about the | symbol in type hints",
                 "You are using a Python older than 3.10. Update Python and install again."],
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
                ["The block does not appear in my profile",
                 "Check that the .svg file was committed and pushed, and that the path in the img "
                 "tag matches the file name exactly (GitHub paths are case sensitive)."],
                ["The animation does not play",
                 "Blocks are static unless you pass animation. Without animation_loop the animation "
                 "plays once, when the image loads, so reload the page to see it again. It is "
                 "disabled for people who turned on reduce motion, and some image viewers and "
                 "editors do not run animations. Open the file in a browser to check."],
            ],
            weights=(2, 5),
        )
    )


@pipeline.asset("footer.svg")
def footer() -> Block:
    return doc_block().text("Made with 💜 for the community. If you liked it, leave a ⭐ on the repository!")


if __name__ == "__main__":
    validate_categories()
    pipeline.run()
