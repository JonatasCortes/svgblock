"""Tests for ``build_frame``, parsed as XML so assertions do not depend on formatting."""

import re
from xml.etree import ElementTree as ET

import pytest

from svgblock.components.themes import Theme, build_frame

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
URL_REFERENCE = re.compile(r"url\(#([^)]+)\)")

DEFAULT_THEME: Theme = list(Theme)[0]
DEFAULT_WIDTH = 400.0
DEFAULT_HEIGHT = 300.0
FRAME_SIZES: tuple[tuple[float, float], ...] = (
    (400.0, 300.0),
    (100.5, 80.25),
    (1920.0, 1080.0),
    (30.5, 20.5),
)
SIZES_TOO_SMALL_TO_HOLD_THE_BORDER: tuple[tuple[float, float], ...] = (
    (1.0, 300.0),
    (400.0, 1.0),
    (0.0, 0.0),
    (-10.0, 300.0),
)

every_theme = pytest.mark.parametrize(
    "theme", list(Theme), ids=[theme.name for theme in Theme]
)
every_frame_size = pytest.mark.parametrize("width, height", FRAME_SIZES)


def svg_tag(name: str) -> str:
    """Return the namespaced tag of an SVG element."""
    return f"{{{SVG_NAMESPACE}}}{name}"


def parse_frame(theme: Theme, width: float, height: float) -> ET.Element:
    """Build a frame and wrap it in a root element so it can be parsed."""
    fragment = build_frame(theme.value, width, height)
    return ET.fromstring(f'<svg xmlns="{SVG_NAMESPACE}">{fragment}</svg>')


def attribute(element: ET.Element, name: str) -> str:
    """Return a required attribute of ``element``."""
    value = element.get(name)
    assert value is not None, f"<{element.tag}> has no attribute {name!r}"
    return value


def definitions_of(root: ET.Element) -> ET.Element:
    """Return the single ``<defs>`` element of a parsed frame."""
    definitions = root.find(svg_tag("defs"))
    assert definitions is not None, "the frame has no <defs> element"
    return definitions


def rectangles_of(root: ET.Element) -> list[ET.Element]:
    """Return the rectangles of a parsed frame in drawing order."""
    return root.findall(svg_tag("rect"))


def gradient_ids_of(root: ET.Element) -> set[str]:
    """Return the ids declared inside ``<defs>``."""
    return {attribute(child, "id") for child in definitions_of(root)}


def resolve_reference(root: ET.Element, reference: str) -> ET.Element:
    """Return the ``<defs>`` child targeted by a ``url(#id)`` reference."""
    match = URL_REFERENCE.fullmatch(reference)
    assert match is not None, f"{reference!r} is not a url(#id) reference"
    target_id = match.group(1)
    for child in definitions_of(root):
        if child.get("id") == target_id:
            return child
    raise AssertionError(f"no element with id {target_id!r} in <defs>")


def stops_of(gradient: ET.Element) -> list[tuple[float, str]]:
    """Return the ``(offset, color)`` pairs of a gradient."""
    return [
        (float(attribute(stop, "offset")), attribute(stop, "stop-color"))
        for stop in gradient.findall(svg_tag("stop"))
    ]


class TestFrameStructure:
    @every_theme
    def test_frame_is_a_well_formed_xml_fragment(self, theme: Theme) -> None:
        root = parse_frame(theme, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        assert len(root) > 0

    def test_frame_is_made_of_definitions_followed_by_two_rectangles(self) -> None:
        root = parse_frame(DEFAULT_THEME, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        assert [child.tag for child in root] == [
            svg_tag("defs"),
            svg_tag("rect"),
            svg_tag("rect"),
        ]

    def test_definitions_hold_one_radial_and_one_linear_gradient(self) -> None:
        root = parse_frame(DEFAULT_THEME, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        tags = sorted(child.tag for child in definitions_of(root))

        assert tags == [svg_tag("linearGradient"), svg_tag("radialGradient")]

    def test_every_definition_has_a_unique_id(self) -> None:
        root = parse_frame(DEFAULT_THEME, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        ids = [attribute(child, "id") for child in definitions_of(root)]

        assert len(ids) == len(set(ids))


class TestGradientReferences:
    def test_every_url_reference_points_to_an_existing_definition(self) -> None:
        root = parse_frame(DEFAULT_THEME, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        references = [
            value
            for rectangle in rectangles_of(root)
            for name in ("fill", "stroke")
            if (value := rectangle.get(name)) is not None
            and value.startswith("url(")
        ]

        assert len(references) == 2
        for reference in references:
            resolve_reference(root, reference)

    @every_theme
    def test_background_gradient_runs_from_the_center_color_to_the_edge_color(
        self, theme: Theme
    ) -> None:
        root = parse_frame(theme, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        background = rectangles_of(root)[0]

        gradient = resolve_reference(root, attribute(background, "fill"))

        assert stops_of(gradient) == [
            (0.0, theme.value["background_center"]),
            (1.0, theme.value["background_edge"]),
        ]

    @every_theme
    def test_border_gradient_runs_from_the_start_color_to_the_end_color(
        self, theme: Theme
    ) -> None:
        root = parse_frame(theme, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        border = rectangles_of(root)[1]

        gradient = resolve_reference(root, attribute(border, "stroke"))

        assert stops_of(gradient) == [
            (0.0, theme.value["border_start"]),
            (1.0, theme.value["border_end"]),
        ]


class TestRectangles:
    def test_the_filled_background_is_drawn_before_the_stroked_border(self) -> None:
        root = parse_frame(DEFAULT_THEME, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        background, border = rectangles_of(root)

        assert attribute(background, "fill").startswith("url(#")
        assert attribute(background, "stroke") == "none"
        assert attribute(border, "fill") == "none"
        assert attribute(border, "stroke").startswith("url(#")

    @every_frame_size
    def test_background_and_border_share_the_same_geometry(
        self, width: float, height: float
    ) -> None:
        root = parse_frame(DEFAULT_THEME, width, height)
        background, border = rectangles_of(root)

        for name in ("x", "y", "width", "height", "rx"):
            assert attribute(background, name) == attribute(border, name)

    @every_frame_size
    def test_the_border_stroke_fits_exactly_inside_the_canvas(
        self, width: float, height: float
    ) -> None:
        root = parse_frame(DEFAULT_THEME, width, height)
        border = rectangles_of(root)[1]
        half_stroke = float(attribute(border, "stroke-width")) / 2
        x = float(attribute(border, "x"))
        y = float(attribute(border, "y"))
        rectangle_width = float(attribute(border, "width"))
        rectangle_height = float(attribute(border, "height"))

        outer_bounds = (
            x - half_stroke,
            y - half_stroke,
            x + rectangle_width + half_stroke,
            y + rectangle_height + half_stroke,
        )

        assert outer_bounds == pytest.approx((0.0, 0.0, width, height))


class TestDeterminism:
    @every_theme
    def test_the_same_arguments_produce_the_same_frame(self, theme: Theme) -> None:
        first = build_frame(theme.value, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        second = build_frame(theme.value, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        assert first == second


class TestFrameSizeValidation:
    @pytest.mark.parametrize("width, height", SIZES_TOO_SMALL_TO_HOLD_THE_BORDER)
    def test_a_size_too_small_to_hold_the_border_is_rejected(
        self, width: float, height: float
    ) -> None:
        with pytest.raises(ValueError):
            build_frame(DEFAULT_THEME.value, width, height)


class TestDefinitionIdIsolation:
    def test_frames_with_different_gradient_colors_do_not_share_definition_ids(
        self,
    ) -> None:
        first = parse_frame(Theme.RED, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        second = parse_frame(Theme.ORANGE, DEFAULT_WIDTH, DEFAULT_HEIGHT)

        assert gradient_ids_of(first).isdisjoint(gradient_ids_of(second))
