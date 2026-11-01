from src.svgblock import Block

from .shared import default_block, register_block_builder


@register_block_builder("how_it_is_built.svg")
def build_how_a_block_is_built() -> Block:
    """Build the block that maps each visual part of a block to the way it is added."""
    return (
        default_block()
        .title("How a Block Is Built")
        .text("A block is a stack of **components** inside a frame. You choose what goes inside "
              "and in which order, and the theme provides the colors.")
        .table(
            ["What you see", "How to add it", "What it is"],
            [
                ["Title", ".title()",
                 "A bold line with a small rounded bar on its left. It stays on a single line, "
                 "so keep it short."],
                ["Subsection", ".subsection()",
                 "A smaller bold line with a dot on its left. It also stays on a single line."],
                ["Text", ".text()",
                 "A paragraph that breaks into lines by itself and accepts **inline styles**."],
                ["Table", ".table()",
                 "A grid with header, optional stripes and dividers. Cells accept inline styles too."],
                ["Image", ".image()",
                 "A picture embedded in the SVG, scaled to fit the available width."],
                ["Columns", ".columns()",
                 "Stacks of components side by side, sized by weight."],
                ["Divider", ".divider()",
                 "A thin line that separates parts of the block. It spans the full width by default."]
            ],
            weights=(2, 3, 6),
        )
    )
