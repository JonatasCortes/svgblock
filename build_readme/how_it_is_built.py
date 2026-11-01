from src.svgblock import Block
from .shared import default_block, register_block_builder


@register_block_builder("how_it_is_built.svg")
def build_how_a_block_is_built() -> Block:
    """Build the block that lists the visual parts of a block and what each one means."""
    return (
        default_block()
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
                 "An optional motion of the whole block. It can enter, leave, move "
                 "continuously, wait and repeat, alone or in a sequence."],
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
