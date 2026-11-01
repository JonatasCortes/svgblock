from src.svgblock import Block, ThemeData

from .shared import default_block, register_block_builder

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


def validate_documented_theme_colors() -> None:
    """Raise a ValueError if THEME_COLORS and the fields of ThemeData are out of sync."""
    documented = {name for name, _ in THEME_COLORS}
    declared = set(ThemeData.__annotations__)
    if documented != declared:
        raise ValueError(
            f"THEME_COLORS out of sync with ThemeData: "
            f"missing={sorted(declared - documented)}, "
            f"unknown={sorted(documented - declared)}"
        )


@register_block_builder("customization.svg")
def build_customization_overview() -> Block:
    """Build the block that maps each thing you can change to how and where to change it."""
    return (
        default_block()
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


@register_block_builder("custom_theme.svg")
def build_creating_your_own_theme() -> Block:
    """Build the block that explains ThemeData and lists the colors every theme needs."""
    return (
        default_block()
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


@register_block_builder("edit_theme.svg")
def build_editing_a_theme() -> Block:
    """Build the block that explains how to change or copy a ready-made theme."""
    return (
        default_block()
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


@register_block_builder("constants.svg")
def build_constants_reference() -> Block:
    """Build the block that lists the layout constants of each file in the svgblock folder."""
    return (
        default_block()
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
