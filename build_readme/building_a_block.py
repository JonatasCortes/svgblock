from src.svgblock import Block, Column

from .shared import LOGO_PATH, default_block, register_block_builder


@register_block_builder("building_create.svg")
def build_creating_a_block() -> Block:
    """Build the block that opens the section and lists the parameters of Block."""
    return (
        default_block()
        .title("Building a Block")
        .text("Everything in svgblock revolves around one class, **Block**. You create it, add "
              "content with chained methods and save it.")
        .subsection("Creating a block")
        .table(
            ["Parameter", "Default", "What it does"],
            [
                ["theme", "Theme.NEON", "Defines every color in the Block"],
                ["width", 800, "The width of the block, in pixels."],
                ["padding", 24, "The space between the border and the content, in pixels."],
                ["animation", "None", "How the block moves"],
                ["hide_frame", "False",
                 "Hides the border and the background. With True, only the components are drawn."],
            ],
            align=("left", "center", "left"),
            weights=(2, 2, 5),
        )
        .text("Every parameter is optional: Block() alone gives you a static block.")
    )


@register_block_builder("dividers.svg")
def build_dividers() -> Block:
    """Build the block that shows the default divider and a shorter one."""
    return (
        default_block()
        .title("Dividers")
        .text("Use .divider(coverage) to separate parts of a block with a thin line. The coverage "
              "is the share of the width the line occupies, from 0 to 1. The line below uses the "
              "default, 100%:")
        .divider()
        .text("And this one uses a coverage of 0.6, so it is shorter and centered:")
        .divider(0.6)
        .text("A coverage of 0 draws nothing, which is a handy way to add a larger gap between "
              "two pieces of text.")
    )


@register_block_builder("markers.svg")
def build_text_markers() -> Block:
    """Build the block that explains the inline text markers, combining and escaping them."""
    return (
        default_block()
        .title("Text Markers")
        .text("Wrap words in markers to style them inline. Each style has its own color in the "
              "theme. They work in paragraphs and table cells. Titles, subsections and table "
              "headers are drawn as plain bold text, so markers show up literally there.")
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
        .text(r"Text that contains these pairs by accident, such as a double hyphen used as a "
              r"dash or a name like \_\_init\_\_, needs the backslash too.")
        .text("Use a raw string (an r before the opening quote) so Python does not read the "
              "backslashes as escape sequences.")
    )


@register_block_builder("columns.svg")
def build_columns() -> Block:
    """Build the block that explains columns and shows a live two-column example."""
    return (
        default_block()
        .title("Columns")
        .text("Use .columns() to place stacks of components side by side. Each Column takes a "
              "**weight** that sets its share of the width (the default is 1).")
        .text("A column holds anything a block holds, even other columns.")
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


@register_block_builder("tables.svg")
def build_tables() -> Block:
    """Build the block that explains tables and shows a live example."""
    return (
        default_block()
        .title("Tables")
        .text("Use .table(columns, rows) to draw a themed table with a header, optional stripes, "
              "dividers and rounded borders. Cells accept **inline styles**.")
        .text("Booleans become ✓ and ✗, and None becomes an empty cell. Alignment, column "
              "widths, stripes and dividers are set with options such as align, weights, "
              "striped, row_dividers and column_dividers.")
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


@register_block_builder("images.svg")
def build_images() -> Block:
    """Build the block that explains images and shows an image beside some text."""
    return (
        default_block()
        .title("Images")
        .text("Use .image(path, width) to embed a picture. The file is read when the script runs "
              "and embedded in the SVG, so the result is a single self-contained file.")
        .text("Large images make the .svg file larger, so small files work best.")
        .divider()
        .text("Combine an image with columns to put a picture beside some text:")
        .columns(
            Column().divider(0).image(LOGO_PATH, 350).divider(0),
            Column()
            .subsection("A logo beside the text")
            .text("The image sits in a column and the text takes the rest of the width."),
        )
    )
