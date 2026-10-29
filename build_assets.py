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
    "fade": "The block fades in. This is the simplest of all and the default value for __animation__",
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
        .text("Themed, animated blocks of text, tables and images, saved as a single **.svg** "
              "file. Use them in READMEs, web pages, documentation, or anywhere an image fits.")
        .divider()
        .text("With a few lines of Python you get a block with a gradient border, a glowing "
              "background and an entrance animation. You pick a **theme** and an "
              "**animation**, and svgblock takes care of colors, spacing, line breaks and "
              "the height of the block.")
        .text("It is plain Python with no external dependencies, and **50 ready-made themes** "
              "are included.")
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
                ["Entrance animation",
                    "The whole block appears when the image loads, and can replay on a timer."],
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
              "browser to see the result and the entrance animation. Reload the page to watch "
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
              "**editable mode**. Changes you make to the code take effect right away, which "
              "is also how you add your own themes and edit the constants.")
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
                ["animation", "None",
                    "The entrance animation. Without it the block is static. See Animations."],
                ["animation_loop", "None",
                 "Seconds between replays of the animation. Without it the animation plays once."],
                ["frame", "True", "Draws the border and the background. With False, only the content is drawn."],
            ],
            align=("left", "center", "left"),
            weights=(2, 1, 5),
        )
        .text("Every parameter is optional: Block() alone gives you a static block.")
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


@pipeline.asset("animations.svg")
def animations() -> Block:
    return (
        doc_block()
        .title("Animations")
        .text("Choose an entrance animation with the **animation** parameter. It plays once, "
              "in 0.8 seconds, when the block appears. Without the parameter the block is static.")
        .table(
            ["Name", "What it does"],
            [*[[name, description]
                for name, description in ANIMATION_INFO.items()]],
            weights=(1, 4),
        )
        .text("Pass the name as a string or use the Animation enum, which gives you "
              "autocomplete in your editor.")
        .divider()
        .subsection("Repeating the animation")
        .text("Pass **animation_loop** with a number of seconds to replay the entrance over and "
              "over. It works without JavaScript, so it also runs inside an image shown in a "
              "README.")
        .text("The number is the length of the **whole cycle**. With animation_loop=5, the "
              "entrance takes 0.8 seconds and the block stays visible for the other 4.2, then "
              "enters again.")
        .text("• The value must be **greater than 0.8**, the duration of the entrance.")
        .text("• animation_loop is used together with an animation.")
        .text("• For blocks with a lot of text, 5 seconds or more leaves time to read.")
        .divider()
        .text("People who turned on reduce motion in their system settings see the block with "
              f"no animation. The previews below repeat every {ANIMATION_LOOP_SECONDS:g} "
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
        .text("Most choices are parameters of **Block** and its methods. For anything deeper, "
              "the source code has clear places to edit.")
        .subsection("What you can change")
        .table(
            ["What", "How", "Where"],
            [
                ["Colors and visual style", "Pick a ready-made theme",
                 "theme= in Block(...)"],
                ["Entrance animation", "Pick one of the six options",
                 "animation= in Block(...)"],
                ["Animation replay", "Set the seconds between replays",
                 "animation_loop= in Block(...)"],
                ["Width of the block", "Set a number of pixels",
                 "width= in Block(...)"],
                ["Size of the text", "Set a number of pixels",
                 "font_size= in .title(), .subsection() and .text()"],
                ["Look of a table", "Pass options to the table", "See Tables"],
                ["A new theme", "Add an entry to THEMES", "svgblock/themes.py"],
                ["Spacing, sizes, durations", "Edit the constants",
                    "See Constants Reference"],
            ],
            weights=(3, 3, 4),
        )
        .text("New themes and constants live in the source code, so install the repository in "
              "editable mode first (see How to Use).")
    )


@pipeline.asset("custom_theme.svg")
def custom_theme() -> Block:
    return (
        doc_block()
        .title("Creating Your Own Theme")
        .text("A theme is an entry in the THEMES dictionary, in the file **svgblock/themes.py**. "
              "The name is lowercase and is exactly what you pass to Block(theme=...). "
              f"Every entry has these **{len(THEME_COLORS)} colors**, written as "
              "hexadecimal values (#RRGGBB):")
        .table(["Color", "What it paints"], [list(color) for color in THEME_COLORS], weights=(2, 3))
        .divider()
        .text("The background is a radial glow, so give the two background colors some "
              "difference: with the same color in both, the glow is invisible.")
        .text("Choose text colors with good contrast against the background. Inline styles are "
              "drawn over the same background as regular text.")
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
        .text("Two good starting points: **ANIMATION_DURATION_SECONDS** (a slower or faster "
              "entrance) and **BACKGROUND_GLOW_RADIUS** (a more concentrated or more spread glow).")
        .text("Line breaks are calculated with the widths of the Arial font, so keep "
              "**FONT_FAMILY** starting with Arial for accurate wrapping. If something looks "
              "off, restore the original values.")
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
        .text('To use a theme, pass its name to the block: **__theme="theme-name"__**.')
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
                 "The valid names are fade, slide-up, slide-down, slide-left, slide-right and "
                 "pop. For a static block, omit the parameter or pass None."],
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
                ["The block does not show on my page",
                 "Check that the path in the img tag matches the file name exactly (paths are case "
                 "sensitive on most servers, including GitHub) and that the .svg file is "
                 "published together with the page."],
                ["The animation does not play",
                 "Without animation_loop the animation plays once, when the image loads, so reload "
                 "the page to see it again. It is disabled for people who turned on reduce motion, "
                 "and some image viewers and editors do not run animations. Open the file in a "
                 "browser to check."],
            ],
            weights=(2, 5),
        )
    )


@pipeline.asset("footer.svg")
def footer() -> Block:
    return doc_block().text("Made with 💜. If you liked it, leave a ⭐ on the repository!")


if __name__ == "__main__":
    validate_categories()
    pipeline.run()
