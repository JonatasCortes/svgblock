from src.svgblock import Block, Animation, THEMES

BLOCK_WIDTH = 500
for theme in THEMES:
    (
        Block(theme, BLOCK_WIDTH, Animation.SLIDE_DOWN)
        .title("MAKE YOUR CUSTOM SVG BLOCKS")
        .text("write beautyfull components for your **README.md**.")
        .text("make texts bigger...", font_size=20)
        .text("or smaller...", font_size=12)
        .subsection("Add subsections")
        .text("test different themes and animations, be free to enjoy!")
        .save(f"assets/block_{theme}.svg")
    )
