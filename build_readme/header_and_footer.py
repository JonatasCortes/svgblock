from src.svgblock import Block, Theme

from .shared import LOGO_PATH, default_block, register_block_builder


@register_block_builder("hero.svg")
def build_hero_logo() -> Block:
    """Build the logo banner shown at the very top of the README."""
    return default_block().image(LOGO_PATH)


@register_block_builder("intro.svg")
def build_welcome_introduction() -> Block:
    """Build the welcome block that explains what svgblock is."""
    return (
        default_block()
        .title("Welcome to svgblock")
        .text("Themed, animated blocks of text, tables and images, saved as a single **.svg** "
              "file. Use them in READMEs, web pages, documentation, or anywhere an image fits.")
        .divider()
        .text("With a few lines of Python you get a block with a gradient border, a glowing "
              "background and an animation. You pick a **theme** and an **animation**, and "
              "svgblock takes care of colors, spacing, line breaks and the height of the block.")
        .text(f"It is plain Python with no external dependencies, and **{len(Theme)} "
              "ready-made themes** are included. You can also edit them or create your own "
              "without touching the library's code.")
        .text("##Every block in this README was made with svgblock itself.##")
    )


@register_block_builder("toc.svg")
def build_table_of_contents_title() -> Block:
    """Build the title block that sits above the table of contents."""
    return default_block().title("Table of Contents")


@register_block_builder("footer.svg")
def build_footer_message() -> Block:
    """Build the closing message shown at the very bottom of the README."""
    return default_block().text("Made with 💜. If you liked it, leave a ⭐ on the repository!")
