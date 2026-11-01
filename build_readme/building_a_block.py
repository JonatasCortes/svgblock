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
                ["theme", "Theme.NEON",
                 "A member of the Theme enum, or your own ThemeData. It defines every color. "
                 "See Themes."],
                ["width", 800, "The width of the block, in pixels. The height is calculated for you."],
                ["padding", 24,
                 "The space between the border and the content, in pixels. It is 0 when "
                 "hide_frame is True."],
                ["animation", "None",
                 "How the block moves: an animation such as RiseIn() or a Sequence(...). "
                 "Without it the block is static. See Animations."],
                ["hide_frame", "False",
                 "Hides the border and the background. With True, only the content is drawn."],
            ],
            align=("left", "center", "left"),
            weights=(2, 2, 5),
        )
        .text("Every parameter is optional: Block() alone gives you a static block. Pass "
              "them by name, as in Block(width=900, animation=RiseIn()).")
    )


@register_block_builder("building_content.svg")
def build_adding_content() -> Block:
    """Build the block that lists the methods used to add content and demonstrates dividers."""
    return (
        default_block()
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


@register_block_builder("markers.svg")
def build_text_markers() -> Block:
    """Build the block that explains the inline text markers, combining and escaping them."""
    return (
        default_block()
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


@register_block_builder("columns.svg")
def build_columns() -> Block:
    """Build the block that explains columns and shows a live two-column example."""
    return (
        default_block()
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


@register_block_builder("tables.svg")
def build_tables() -> Block:
    """Build the block that lists the table options and shows a live example."""
    return (
        default_block()
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


@register_block_builder("images.svg")
def build_images() -> Block:
    """Build the block that explains images and shows an image beside some text."""
    return (
        default_block()
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


@register_block_builder("saving.svg")
def build_saving_the_result() -> Block:
    """Build the block that lists the methods used to save or render a block."""
    return (
        default_block()
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
