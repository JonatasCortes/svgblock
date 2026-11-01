from pathlib import Path

from src.svgblock import Block, FadeIn, Theme

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
LOGO_DIR: Path = PROJECT_ROOT / "logos"
LOGO_PATH: str = (LOGO_DIR / "svgblock_logo.png").as_posix()

DOC_THEME: Theme = Theme.NEON
DOC_WIDTH: int = 800


def default_block() -> Block:
    return Block(DOC_THEME, DOC_WIDTH, animation=FadeIn())
