import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from svgblock import Block
from svgblock.components import Column

from .shared import (
    LEFT,
    SVG_NAMESPACE,
    TOP,
    build_png_bytes,
    find_images,
    render_column,
    write_image,
)

NATURAL_WIDTH = 200
NATURAL_HEIGHT = 100
ROOMY_WIDTH = 1000.0


def write_wide_png(directory: Path) -> Path:
    """Write a 2:1 PNG used by every test in this module."""
    return write_image(
        directory, "wide.png", build_png_bytes(NATURAL_WIDTH, NATURAL_HEIGHT)
    )


def draw_image(
    path: Path,
    requested_width: float | None = None,
    available_width: float = ROOMY_WIDTH,
) -> tuple[float, float, float]:
    """Return the drawn width, drawn height and reported height of one image."""
    rendered = render_column(
        Column().image(path, width=requested_width), width=available_width
    )
    image = find_images(rendered.svg)[0]
    return float(image.attrib["width"]), float(image.attrib["height"]), rendered.height


class TestImageSizing:
    def test_image_keeps_its_natural_size_when_nothing_constrains_it(
        self, tmp_path: Path
    ) -> None:
        width, height, _ = draw_image(write_wide_png(tmp_path))

        assert (width, height) == (NATURAL_WIDTH, NATURAL_HEIGHT)

    @pytest.mark.parametrize("requested_width", [20, 50, 150, 400])
    def test_requested_width_is_applied_keeping_the_aspect_ratio(
        self, tmp_path: Path, requested_width: float
    ) -> None:
        width, height, _ = draw_image(
            write_wide_png(tmp_path), requested_width)

        assert width == pytest.approx(requested_width)
        assert height == pytest.approx(requested_width / 2)

    def test_image_is_shrunk_to_the_available_width(self, tmp_path: Path) -> None:
        width, height, _ = draw_image(
            write_wide_png(tmp_path), available_width=120)

        assert (width, height) == (120, 60)

    def test_requested_width_is_limited_by_the_available_width(
        self, tmp_path: Path
    ) -> None:
        width, height, _ = draw_image(
            write_wide_png(tmp_path), requested_width=400, available_width=120
        )

        assert (width, height) == (120, 60)

    def test_reported_height_equals_the_drawn_height(self, tmp_path: Path) -> None:
        _, drawn_height, reported_height = draw_image(
            write_wide_png(tmp_path), requested_width=50
        )

        assert reported_height == pytest.approx(drawn_height)

    def test_image_is_placed_at_the_given_left_and_top(self, tmp_path: Path) -> None:
        rendered = render_column(Column().image(write_wide_png(tmp_path)))

        image = find_images(rendered.svg)[0]

        assert float(image.attrib["x"]) == pytest.approx(LEFT)
        assert float(image.attrib["y"]) == pytest.approx(TOP)

    @pytest.mark.parametrize("available_width", [0, -1, -50])
    def test_nothing_is_drawn_when_there_is_no_available_width(
        self, tmp_path: Path, available_width: float
    ) -> None:
        rendered = render_column(
            Column().image(write_wide_png(tmp_path)), width=available_width
        )

        assert rendered.svg == ""
        assert rendered.height == 0


class TestImageInsideBlock:
    def test_images_share_the_row_width_according_to_the_columns(
        self, tmp_path: Path
    ) -> None:
        path = write_wide_png(tmp_path)
        block = Block().columns(*(Column().image(path) for _ in range(4)))

        images = ET.fromstring(block.render()).findall(
            f".//{{{SVG_NAMESPACE}}}image")

        assert [float(image.attrib["width"]) for image in images] == pytest.approx(
            [170.0] * 4
        )

    def test_columns_too_narrow_for_their_gaps_draw_no_image(
        self, tmp_path: Path
    ) -> None:
        path = write_wide_png(tmp_path)
        block = Block(width=100).columns(*(Column().image(path)
                                           for _ in range(4)))

        images = ET.fromstring(block.render()).findall(
            f".//{{{SVG_NAMESPACE}}}image")

        assert images == []
