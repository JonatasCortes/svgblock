import xml.etree.ElementTree as ET
from typing import Any

import pytest

from svgblock.components import Column, Theme

from .shared import LEFT, SVG_NAMESPACE, TOP, WIDTH, parse_svg_fragment, render_column

THEME = Theme.NEON.value
DEFAULT_PADDING = 8
HEADER = ["name", "value"]
BODY = [["a", "1"], ["b", "2"], ["c", "3"]]


def render_table_svg(
    columns: list[str], rows: list[list[Any]], width: float = WIDTH, **options: Any
) -> str:
    """Render a table inside a column and return its SVG."""
    return render_column(Column().table(columns, rows, **options), width=width).svg


def measure_table_height(
    columns: list[str], rows: list[list[Any]], width: float = WIDTH, **options: Any
) -> float:
    """Render a table inside a column and return its height."""
    return render_column(Column().table(columns, rows, **options), width=width).height


def find_all(svg: str, tag: str) -> list[ET.Element]:
    """Return every element with the given tag found in an SVG fragment."""
    return parse_svg_fragment(svg).findall(f".//{{{SVG_NAMESPACE}}}{tag}")


def read_text(svg: str) -> str:
    """Return all text nodes of an SVG fragment joined."""
    return "".join(parse_svg_fragment(svg).itertext())


def count_stripes(svg: str) -> int:
    """Count the rectangles painted with the stripe color."""
    stripe = THEME["table_stripe_background"]
    return sum(1 for rect in find_all(svg, "rect") if rect.attrib.get("fill") == stripe)


class TestCellValues:
    def test_none_cell_renders_no_text(self) -> None:
        content = read_text(render_table_svg(["h"], [[None]]))

        assert "None" not in content

    def test_true_cell_renders_a_check_mark(self) -> None:
        assert "✓" in read_text(render_table_svg(["h"], [[True]]))

    def test_false_cell_renders_a_cross_mark(self) -> None:
        assert "✗" in read_text(render_table_svg(["h"], [[False]]))

    def test_booleans_are_not_rendered_as_numbers(self) -> None:
        content = read_text(render_table_svg(["a", "b"], [[True, False]]))

        assert "True" not in content
        assert "False" not in content

    @pytest.mark.parametrize("number", [0, 1])
    def test_integers_zero_and_one_are_not_confused_with_booleans(
        self, number: int
    ) -> None:
        content = read_text(render_table_svg(["h"], [[number]]))

        assert str(number) in content
        assert "✓" not in content
        assert "✗" not in content


class TestStripes:
    def test_striped_table_paints_every_second_body_row(self) -> None:
        rows = [["x", "y"]] * 6

        striped = count_stripes(render_table_svg(HEADER, rows, striped=True))
        plain = count_stripes(render_table_svg(HEADER, rows, striped=False))

        assert striped - plain == 3

    def test_stripes_are_enabled_by_default(self) -> None:
        default = render_table_svg(HEADER, BODY)

        assert default == render_table_svg(HEADER, BODY, striped=True)

    def test_table_with_a_single_body_row_has_no_stripes(self) -> None:
        striped = count_stripes(render_table_svg(
            HEADER, BODY[:1], striped=True))
        plain = count_stripes(render_table_svg(
            HEADER, BODY[:1], striped=False))

        assert striped == plain


class TestDividers:
    def test_row_dividers_separate_the_header_and_every_body_row(self) -> None:
        svg = render_table_svg(HEADER, BODY, row_dividers=True)

        assert len(find_all(svg, "line")) == len(BODY)

    def test_disabled_row_dividers_keep_only_the_line_below_the_header(self) -> None:
        svg = render_table_svg(HEADER, BODY, row_dividers=False)

        assert len(find_all(svg, "line")) == 1

    def test_header_only_table_has_no_horizontal_dividers(self) -> None:
        assert find_all(render_table_svg(HEADER, []), "line") == []

    def test_column_dividers_are_disabled_by_default(self) -> None:
        svg = render_table_svg(HEADER, BODY)

        assert all(
            line.attrib["x1"] != line.attrib["x2"] is False
            for line in find_all(svg, "line")
        ) or all(line.attrib["y1"] == line.attrib["y2"] for line in find_all(svg, "line"))

    def test_column_dividers_add_one_vertical_line_between_each_pair_of_columns(
        self,
    ) -> None:
        svg = render_table_svg(["a", "b", "c"], BODY_3, column_dividers=True)

        vertical = [
            line for line in find_all(svg, "line") if line.attrib["x1"] == line.attrib["x2"]
        ]

        assert len(vertical) == 2

    def test_column_dividers_are_placed_at_the_column_boundaries(self) -> None:
        svg = render_table_svg(
            HEADER, BODY, column_dividers=True, weights=[1, 3]
        )

        vertical = [
            line for line in find_all(svg, "line") if line.attrib["x1"] == line.attrib["x2"]
        ]

        assert [float(line.attrib["x1"]) for line in vertical] == pytest.approx(
            [LEFT + WIDTH / 4]
        )

    def test_column_dividers_span_the_whole_table_height(self) -> None:
        svg = render_table_svg(HEADER, BODY, column_dividers=True)
        height = measure_table_height(HEADER, BODY)

        vertical = [
            line for line in find_all(svg, "line") if line.attrib["x1"] == line.attrib["x2"]
        ][0]

        assert float(vertical.attrib["y1"]) == pytest.approx(TOP)
        assert float(vertical.attrib["y2"]) == pytest.approx(TOP + height)


BODY_3 = [["x", "y", "z"]]


class TestAlignment:
    @pytest.mark.parametrize(
        "alignment, anchor, expected_x",
        [
            ("left", None, LEFT + DEFAULT_PADDING),
            ("center", "middle", LEFT + WIDTH / 2),
            ("right", "end", LEFT + WIDTH - DEFAULT_PADDING),
        ],
    )
    def test_alignment_sets_the_anchor_and_the_horizontal_position(
        self, alignment: str, anchor: str | None, expected_x: float
    ) -> None:
        svg = render_table_svg(["h"], [["c"]], align=[alignment])

        for text in find_all(svg, "text"):
            assert text.attrib.get("text-anchor") == anchor
            assert float(text.attrib["x"]) == pytest.approx(expected_x)

    def test_default_alignment_is_left(self) -> None:
        assert render_table_svg(["h"], [["c"]]) == render_table_svg(
            ["h"], [["c"]], align=["left"]
        )

    def test_each_column_uses_its_own_alignment(self) -> None:
        svg = render_table_svg(["a", "b"], [["x", "y"]],
                               align=["left", "right"])

        anchors = [text.attrib.get("text-anchor")
                   for text in find_all(svg, "text")]

        assert anchors == [None, "end", None, "end"]


class TestStyleOptions:
    def test_cell_padding_offsets_the_text_from_the_cell_edge(self) -> None:
        svg = render_table_svg(["h"], [["c"]], cell_padding=20)

        assert float(find_all(svg, "text")[
                     0].attrib["x"]) == pytest.approx(LEFT + 20)

    def test_cell_padding_is_added_above_and_below_every_row(self) -> None:
        compact = measure_table_height(["h"], [["c"]], cell_padding=8)
        spacious = measure_table_height(["h"], [["c"]], cell_padding=20)

        assert spacious - compact == pytest.approx(2 * 2 * (20 - 8))

    def test_larger_font_size_produces_a_taller_table(self) -> None:
        small = measure_table_height(HEADER, BODY, font_size=10)
        large = measure_table_height(HEADER, BODY, font_size=30)

        assert large > small

    def test_font_size_is_written_to_the_text_elements(self) -> None:
        svg = render_table_svg(HEADER, BODY, font_size=22)

        assert all(float(text.attrib["font-size"])
                   == 22 for text in find_all(svg, "text"))

    def test_border_radius_is_applied_to_the_clip_and_to_the_border(self) -> None:
        svg = render_table_svg(HEADER, BODY, border_radius=12)

        rounded = [rect for rect in find_all(
            svg, "rect") if "rx" in rect.attrib]

        assert len(rounded) == 2
        assert all(float(rect.attrib["rx"]) == 12 for rect in rounded)

    def test_border_covers_the_table_inset_by_half_the_line_width(self) -> None:
        svg = render_table_svg(HEADER, BODY)
        height = measure_table_height(HEADER, BODY)

        border = [rect for rect in find_all(
            svg, "rect") if rect.attrib.get("fill") == "none"][0]

        assert float(border.attrib["x"]) == pytest.approx(LEFT + 0.5)
        assert float(border.attrib["y"]) == pytest.approx(TOP + 0.5)
        assert float(border.attrib["width"]) == pytest.approx(WIDTH - 1)
        assert float(border.attrib["height"]) == pytest.approx(height - 1)


class TestLayout:
    def test_header_is_bold_and_body_is_not(self) -> None:
        texts = find_all(render_table_svg(["h"], [["c"]]), "text")

        assert texts[0].attrib.get("font-weight") == "700"
        assert "font-weight" not in texts[1].attrib

    def test_header_and_body_use_different_text_colors(self) -> None:
        texts = find_all(render_table_svg(["h"], [["c"]]), "text")

        assert texts[0].attrib["fill"] == THEME["table_header_text"]
        assert texts[1].attrib["fill"] == THEME["table_text"]

    def test_height_grows_by_the_same_amount_for_each_equal_row(self) -> None:
        heights = [measure_table_height(
            HEADER, [["x", "y"]] * count) for count in (1, 2, 3)]

        assert heights[1] - \
            heights[0] == pytest.approx(heights[2] - heights[1])
        assert heights[1] > heights[0]

    def test_reported_height_matches_the_painted_background(self) -> None:
        svg = render_table_svg(HEADER, BODY)
        height = measure_table_height(HEADER, BODY)

        background = find_all(svg, "rect")[1]

        assert float(background.attrib["height"]) == pytest.approx(height)

    def test_weights_distribute_the_width_between_the_columns(self) -> None:
        svg = render_table_svg(["a", "b"], [["x", "y"]], weights=[1, 3])

        second_column_header = find_all(svg, "text")[1]

        assert float(second_column_header.attrib["x"]) == pytest.approx(
            LEFT + WIDTH / 4 + DEFAULT_PADDING
        )

    def test_long_cell_text_wraps_and_makes_the_row_taller(self) -> None:
        short = measure_table_height(["h"], [["short"]], width=150)
        long = measure_table_height(["h"], [["word " * 30]], width=150)

        assert long > short

    def test_long_header_wraps_and_makes_the_header_taller(self) -> None:
        short = measure_table_height(["h"], [], width=150)
        long = measure_table_height(["header " * 30], [], width=150)

        assert long > short

    def test_wrapped_cell_text_is_not_lost(self) -> None:
        words = [f"word{index}" for index in range(30)]

        content = read_text(render_table_svg(
            ["h"], [[" ".join(words)]], width=150))

        assert all(word in content for word in words)


class TestCellMarkup:
    def test_markup_in_a_body_cell_produces_a_styled_span(self) -> None:
        spans = find_all(render_table_svg(["h"], [["**cell**"]]), "tspan")

        assert [span.text for span in spans] == ["cell"]

    def test_markup_in_a_header_is_rendered_literally(self) -> None:
        svg = render_table_svg(["**title**"], [])

        assert find_all(svg, "tspan") == []
        assert "**title**" in read_text(svg)

    def test_unclosed_marker_in_a_body_cell_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unclosed marker"):
            render_table_svg(["h"], [["**open"]])

    def test_unclosed_marker_in_a_header_does_not_raise(self) -> None:
        assert "**open" in read_text(render_table_svg(["**open"], []))
