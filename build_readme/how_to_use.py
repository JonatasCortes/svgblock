from src.svgblock import Block

from .shared import default_block, register_block_builder


@register_block_builder("use_overview.svg")
def build_how_to_use_overview() -> Block:
    """Build the opening block of the "How to Use" section."""
    return (
        default_block()
        .title("How to Use")
        .text("Install svgblock, describe a block in Python and save it. The result is an "
              "ordinary **.svg** file that you can use anywhere an image works.")
    )


@register_block_builder("use_step_1.svg")
def build_step_install_svgblock() -> Block:
    """Build the block that explains how to install svgblock with pip."""
    return (
        default_block()
        .title("Step 1: Install svgblock")
        .text("svgblock is published on PyPI and needs **Python 3.10 or newer**. Install it "
              "with pip:")
    )


@register_block_builder("use_step_2.svg")
def build_step_write_first_block() -> Block:
    """Build the block that introduces the first example script."""
    return (
        default_block()
        .title("Step 2: Write your first block")
        .text("Create a file called **generate_blocks.py** with the code below. Every line of "
              "the chain adds something to the block, in order. The last one, .save(...), "
              "writes the file and creates the folder if it does not exist.")
    )


@register_block_builder("use_step_3.svg")
def build_step_run_script() -> Block:
    """Build the block that explains how to run the script and open the result."""
    return (
        default_block()
        .title("Step 3: Run the script")
        .text("When it finishes, the file **assets/block.svg** is ready. Open it in your "
              "browser to see the result and the animation. Reload the page to watch "
              "the animation again.")
    )


@register_block_builder("use_step_4.svg")
def build_step_use_the_svg() -> Block:
    """Build the block that explains how to reference the generated SVG."""
    return (
        default_block()
        .title("Step 4: Use the SVG")
        .text("Reference the file wherever you show images: an HTML page, a Markdown file, a "
              "README or a documentation site.")
        .divider()
        .text("The width in the HTML only resizes the image. The real size of the block is the "
              "width you passed to Block(...). Use the same value, or a smaller one, to keep "
              "the text readable.")
    )


@register_block_builder("use_more.svg")
def build_optional_add_more_blocks() -> Block:
    """Build the optional block about creating several blocks in one script."""
    return (
        default_block()
        .subsection("Optional: add more blocks")
        .text("A single script can create as many blocks as you want, each saved in its own "
              "file, with its own theme and animation.")
    )


@register_block_builder("use_local.svg")
def build_optional_use_repository_locally() -> Block:
    """Build the optional block about installing the repository in editable mode."""
    return (
        default_block()
        .subsection("Optional: use the repository locally")
        .text("To work with the source code, clone the repository and install it in "
              "**editable mode**. Changes you make to the code take effect right away. "
              "You do not need this to edit or create themes: that works with the "
              "regular pip installation.")
    )
