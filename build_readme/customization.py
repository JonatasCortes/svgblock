from src.svgblock import Block, ThemeData
from .shared import (DOC_THEME, AnimationExample, default_block, register_animation_previews,
                     register_asset, register_block_builder)

SAMPLE_WIDTH = 400
CUSTOMIZED_PADDING = 48

AMBER_COLORS: dict[str, str] = {
    "border_start": "#ff9500",
    "border_end": "#ffd60a",
    "title_text": "#ffd60a",
    "title_bar": "#ff9500",
}
AMBER_UPDATE_ARGUMENTS = ", ".join(
    f'{name}="{color}"' for name, color in AMBER_COLORS.items())

ANIMATION_CUSTOMIZATION_EXAMPLES: tuple[AnimationExample, ...] = (
    AnimationExample("default", "DEFAULT ANIMATION", "RiseIn()", replay=True),
    AnimationExample(
        "customized", "CUSTOMIZED ANIMATION",
        "RiseIn(distance=80, duration=1.6, fade=False)", replay=True),
)


def build_amber_theme() -> ThemeData:
    """Build a copy of the documentation theme with the border and title colors replaced."""
    theme = DOC_THEME.value.copy()
    theme.update(**AMBER_COLORS)
    return theme


def build_customization_sample(block: Block, title: str, code_lines: tuple[str, ...]) -> Block:
    """Fill a block with the sample content shared by every default and customized example."""
    sample = block.title(title)
    for code_line in code_lines:
        sample = sample.text(f"**__{code_line}__**", font_size=14)
    return sample.text("Body text with **highlight**, __underline__ and ##italic##.")


def build_default_theme_sample() -> Block:
    """Build the sample block painted with the unchanged documentation theme."""
    return build_customization_sample(
        Block(DOC_THEME, SAMPLE_WIDTH),
        "DEFAULT THEME",
        (f"Block(theme=Theme.{DOC_THEME.name})",),
    )


def build_amber_theme_sample() -> Block:
    """Build the sample block painted with the customized copy of the documentation theme."""
    return build_customization_sample(
        Block(build_amber_theme(), SAMPLE_WIDTH),
        "CUSTOMIZED THEME",
        (
            f"theme = Theme.{DOC_THEME.name}.value.copy()",
            f"theme.update({AMBER_UPDATE_ARGUMENTS})",
            "Block(theme=theme)",
        ),
    )


def build_default_spacing_sample() -> Block:
    """Build the sample block with the default padding."""
    return build_customization_sample(
        Block(DOC_THEME, SAMPLE_WIDTH),
        "DEFAULT SPACING",
        (f"Block(width={SAMPLE_WIDTH})",),
    )


def build_roomy_spacing_sample() -> Block:
    """Build the sample block with a larger padding and the same width."""
    return build_customization_sample(
        Block(DOC_THEME, SAMPLE_WIDTH, padding=CUSTOMIZED_PADDING),
        "CUSTOMIZED SPACING",
        (f"Block(width={SAMPLE_WIDTH}, padding={CUSTOMIZED_PADDING})",),
    )


@register_block_builder("customization.svg")
def build_customization_overview() -> Block:
    """Build the block that opens the Customization section."""
    return (
        default_block()
        .title("Customization")
        .text("Colors, spacing and animation can all be changed. Each example shows the "
              "default block next to the same block customized.")
    )


@register_block_builder("edit_theme.svg")
def build_editing_a_theme() -> Block:
    """Build the block that explains how to change the colors of a ready-made theme."""
    return (
        default_block()
        .title("Editing a Theme")
        .text("Every ready-made theme is a member of the **Theme** enum, and its colors are in "
              "**.value**, which is a ThemeData. To get a variation, make a copy with "
              "**.value.copy()**, change the copy with **.update(...)**, passing only the "
              "colors you want to replace, and pass it to Block. The ready-made theme is not "
              "affected.")
        .text("Calling **.update(...)** directly on Theme.NAME.value changes the shared theme "
              "for the whole program: every block that uses it gets the new colors, so make "
              "the change **before** you build the blocks.")
    )


@register_block_builder("custom_theme.svg")
def build_creating_your_own_theme() -> Block:
    """Build the block that explains ThemeData and how to start a theme of your own."""
    return (
        default_block()
        .title("Creating Your Own Theme")
        .text(f"A theme is a **ThemeData**: a dictionary that holds the "
              f"**{len(ThemeData.__annotations__)} colors** of a block, written as hexadecimal "
              "values (#RRGGBB). Create one in your own code and pass it to "
              "**Block(theme=...)**, exactly like a ready-made theme. The quickest way is to "
              "start from a copy of a theme that is close to what you want and change only "
              "the colors that differ.")
        .subsection("Good to know")
        .text("• Give every color: a missing one only shows up as an error when the block is "
              "drawn.")
        .text("• The background is a radial glow, so give the two background colors some "
              "difference: with the same color in both, the glow is invisible.")
    )


@register_block_builder("customization_spacing.svg")
def build_customizing_spacing() -> Block:
    """Build the block that introduces the spacing example."""
    return (
        default_block()
        .title("Customizing Spacing")
        .text("The space between the border and the content is the **padding** parameter of "
              "Block. The two blocks below have the same width and different padding.")
    )


@register_block_builder("customization_animation.svg")
def build_customizing_an_animation() -> Block:
    """Build the block that introduces the animation example."""
    return (
        default_block()
        .title("Customizing an Animation")
        .text("Every animation takes parameters that adjust it. The two previews below run "
              "the same entrance, first with its defaults and then customized. Easings change "
              "how the speed varies, and sequences chain several animations.")
    )


register_asset("customization_theme_default.svg", build_default_theme_sample)
register_asset("customization_theme_customized.svg", build_amber_theme_sample)
register_asset("customization_spacing_default.svg",
               build_default_spacing_sample)
register_asset("customization_spacing_customized.svg",
               build_roomy_spacing_sample)
register_animation_previews(
    ANIMATION_CUSTOMIZATION_EXAMPLES, "customization_animation_")
