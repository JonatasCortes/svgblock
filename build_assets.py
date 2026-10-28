from src.svgblock import Block, Animation, THEMES

BLOCK_WIDTH = 500

for theme in THEMES:
    (
        Block(theme, BLOCK_WIDTH, Animation.SLIDE_DOWN)
        .title("BUILD BEAUTIFUL SVG BLOCKS")
        .text("Create stunning components for your **README.md**.")
        .text("Make your message stand out!", font_size=20)
        .text("Or keep things subtle and simple.", font_size=12)
        .subsection("Make It Your Own")
        .text("Explore different themes, animations, and styles.")
        .text("Customize every detail. **Create something unique!**")
        .save(f"assets/block_{theme}.svg")
    )
