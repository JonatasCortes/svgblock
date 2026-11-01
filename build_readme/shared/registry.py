from collections.abc import Callable
from src.svgblock import Block
from .doc_style import ASSETS_DIR, PROJECT_ROOT

BlockBuilder = Callable[[], Block]
_assets: dict[str, BlockBuilder] = {}


def register_asset(filename: str, build: BlockBuilder) -> None:
    if filename in _assets:
        raise ValueError(f"Asset '{filename}' is already registered.")
    _assets[filename] = build


def register_block_builder(filename: str) -> Callable[[BlockBuilder], BlockBuilder]:
    def register(build: BlockBuilder) -> BlockBuilder:
        register_asset(filename, build)
        return build
    return register


def save_assets() -> None:
    for filename, build in _assets.items():
        build().save((ASSETS_DIR / filename).as_posix())
        print(f"  ✓ {filename}")
    output_folder = ASSETS_DIR.relative_to(PROJECT_ROOT).as_posix()
    print(f"{len(_assets)} assets written to {output_folder}/")
