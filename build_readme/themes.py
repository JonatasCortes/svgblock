from dataclasses import dataclass
from functools import partial

from src.svgblock import Block, DropIn, Theme

from .shared import default_block, register_asset, register_block_builder

THEME_SHOWCASE_WIDTH = 500


@dataclass(frozen=True)
class ThemeCategory:
    """A group of themes shown together in the README.

    The themes are the lowercase names of members of the Theme enum.
    """

    slug: str
    title: str
    description: str
    themes: tuple[str, ...]


THEME_CATEGORIES: tuple[ThemeCategory, ...] = (
    ThemeCategory("dark", "Dark Colors", "Simple, bold, and deep classic colors.",
                  ("red", "orange", "yellow", "green", "blue", "purple", "pink", "obsidian")),
    ThemeCategory("light", "Light Colors (Pastels)",
                  "Beautifully tinted light backgrounds for a clean and fresh look.",
                  ("mint", "chocomint", "lavender", "peach", "sky")),
    ThemeCategory("seasons", "Seasons", "Earthy and atmospheric palettes inspired by the natural world.",
                  ("spring", "summer", "autumn", "winter")),
    ThemeCategory("drinks", "Drinks", "Warm tones and aesthetics inspired by classic beverages.",
                  ("wine", "beer", "coffee", "matcha", "berrymatcha", "latte")),
    ThemeCategory("countries", "Countries & Geography", "Colors inspired by flags and cultural landmarks.",
                  ("brazil", "usa", "miami", "france", "japandark", "japanlight", "sakura",
                   "india", "china", "mexico", "fiesta", "greece", "egypt")),
    ThemeCategory("aesthetics", "Aesthetics & Culture",
                  "Highly stylized themes based on internet cultures and artistic movements.",
                  ("neon", "cyberpunk", "steampunk", "synthwave", "lofi")),
    ThemeCategory("dev", "Classical UI (Dev Themes)",
                  "Beloved themes from your favorite code editors and IDEs.",
                  ("dracula", "mocha", "nord", "solarizeddark", "solarizedlight", "atlas")),
    ThemeCategory("mythology", "Mythology & Concepts", "Epic, concept-driven abstract aesthetics.",
                  ("heaven", "hell", "abyss")),
)

THEME_DISPLAY_NAME_OVERRIDES: dict[str, str] = {
    "chocomint": "Choco Mint",
    "berrymatcha": "Berry Matcha",
    "japandark": "Japan Dark",
    "japanlight": "Japan Light",
    "solarizeddark": "Solarized Dark",
    "solarizedlight": "Solarized Light",
}


def validate_theme_categories() -> None:
    """Raise a ValueError if THEME_CATEGORIES and the members of the Theme enum are out of sync."""
    all_themes = {theme.name.lower() for theme in Theme}
    listed = [theme for category in THEME_CATEGORIES for theme in category.themes]
    missing = all_themes - set(listed)
    unknown = set(listed) - all_themes
    duplicated = {theme for theme in listed if listed.count(theme) > 1}
    if missing or unknown or duplicated:
        raise ValueError(
            f"THEME_CATEGORIES out of sync with Theme: missing={sorted(missing)}, "
            f"unknown={sorted(unknown)}, duplicated={sorted(duplicated)}"
        )


@register_block_builder("themes_overview.svg")
def build_themes_overview() -> Block:
    """Build the block that introduces themes and how to use a ready-made one."""
    return (
        default_block()
        .title("Themes")
        .text("A theme defines every color of a block: the border gradient, the glowing "
              "background, titles, subsections, text, inline styles, tables and dividers.")
        .text("The ready-made themes are the members of the **Theme** enum. To use one, pass it "
              "to the block: **__theme=Theme.NAME__**.")
        .text("Want to tweak a theme or build your own? See Customization.")
    )


def build_theme_category_header_block(category_number: int, category: ThemeCategory) -> Block:
    """Build the header block of a category, with its number, description and theme names."""
    theme_keys = ", ".join(f"**{key.upper()}**" for key in category.themes)
    return (
        default_block()
        .title(f"{category_number}. {category.title}")
        .text(category.description)
        .text(f"Available themes: {theme_keys}")
    )


def build_theme_showcase_block(theme: Theme) -> Block:
    """Build the sample block painted with a single theme, showing each of its colored elements."""
    key = theme.name.lower()
    display_name = THEME_DISPLAY_NAME_OVERRIDES.get(key, key.title())
    return (
        Block(theme, THEME_SHOWCASE_WIDTH, animation=DropIn())
        .title(f"{display_name.upper()} THEME")
        .text(f"Use it with theme=Theme.{theme.name}.")
        .subsection("Subsection")
        .text("Body text with **highlight**, __underline__, --strikethrough--, ##italic## "
              "and **__combined__**.")
        .divider()
        .table(
            ["Language", "Level"],
            [
                ["Python", "**Advanced**"],
                ["Rust", "##Learning##"],
                ["COBOL", "--Retired--"],
            ],
            weights=(2, 2),
        )
    )


for category_number, theme_category in enumerate(THEME_CATEGORIES, start=1):
    register_asset(f"category_{theme_category.slug}.svg",
                   partial(build_theme_category_header_block, category_number, theme_category))

for theme in Theme:
    register_asset(f"block_{theme.name.lower()}.svg",
                   partial(build_theme_showcase_block, theme))
