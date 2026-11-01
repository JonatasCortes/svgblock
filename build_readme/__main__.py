from .customization import validate_documented_theme_colors
from .shared import save_assets
from .themes import validate_theme_categories


def main() -> None:
    """Check that the documented data is up to date and write every README SVG to assets/."""
    validate_theme_categories()
    validate_documented_theme_colors()
    save_assets()


if __name__ == "__main__":
    main()
