import xml.etree.ElementTree as ET
import pytest
from svgblock import Column
from .shared import make_column_with_dividers, measure_component_gap, render_column

SVG_WRAPPER = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink">{content}</svg>'
)
SPECIAL_CHARACTERS_TEXT = "Tom & Jerry <3 \"quoted\" 'single'"


def read_text_content(svg: str) -> str:
    """Parse an SVG fragment as XML and return all of its text nodes joined."""
    root = ET.fromstring(SVG_WRAPPER.format(content=svg))
    return "".join(root.itertext())


class TestXmlEscaping:
    def test_title_preserves_special_characters(self) -> None:
        rendered = render_column(Column().title(SPECIAL_CHARACTERS_TEXT))

        assert SPECIAL_CHARACTERS_TEXT in read_text_content(rendered.svg)

    def test_subsection_preserves_special_characters(self) -> None:
        rendered = render_column(Column().subsection(SPECIAL_CHARACTERS_TEXT))

        assert SPECIAL_CHARACTERS_TEXT in read_text_content(rendered.svg)

    def test_text_preserves_special_characters(self) -> None:
        rendered = render_column(Column().text(SPECIAL_CHARACTERS_TEXT))

        assert SPECIAL_CHARACTERS_TEXT in read_text_content(rendered.svg)

    def test_table_header_preserves_special_characters(self) -> None:
        rendered = render_column(Column().table([SPECIAL_CHARACTERS_TEXT], []))

        assert SPECIAL_CHARACTERS_TEXT in read_text_content(rendered.svg)

    def test_table_cell_preserves_special_characters(self) -> None:
        rendered = render_column(
            Column().table(["header"], [[SPECIAL_CHARACTERS_TEXT]])
        )

        assert SPECIAL_CHARACTERS_TEXT in read_text_content(rendered.svg)

    def test_markup_like_text_is_not_interpreted_as_svg_elements(self) -> None:
        markup = "<script>alert(1)</script>"
        rendered = render_column(Column().text(markup))

        root = ET.fromstring(SVG_WRAPPER.format(content=rendered.svg))

        assert root.findall(".//{http://www.w3.org/2000/svg}script") == []
        assert markup in "".join(root.itertext())


class TestTableCellValues:
    def test_integer_cell_is_rendered_as_text(self) -> None:
        rendered = render_column(Column().table(["value"], [[42]]))

        assert "42" in read_text_content(rendered.svg)

    def test_float_cell_is_rendered_as_text(self) -> None:
        rendered = render_column(Column().table(["value"], [[3.5]]))

        assert "3.5" in read_text_content(rendered.svg)

    def test_cells_of_mixed_types_are_all_rendered(self) -> None:
        rendered = render_column(Column().table(
            ["a", "b", "c"], [["text", 7, 0.25]]))

        content = read_text_content(rendered.svg)

        assert "text" in content
        assert "7" in content
        assert "0.25" in content

    def test_table_renders_headers_before_rows(self) -> None:
        rendered = render_column(Column().table(["HEADER"], [["CELL"]]))

        content = read_text_content(rendered.svg)

        assert content.index("HEADER") < content.index("CELL")


class TestColumnsRow:
    def test_row_height_equals_the_tallest_column(self) -> None:
        row = Column().columns(
            make_column_with_dividers(1), make_column_with_dividers(3)
        )

        tallest = render_column(make_column_with_dividers(3)).height

        assert render_column(row).height == pytest.approx(tallest)

    def test_row_height_is_the_same_when_the_tallest_column_comes_first(self) -> None:
        tallest_last = Column().columns(
            make_column_with_dividers(1), make_column_with_dividers(3)
        )
        tallest_first = Column().columns(
            make_column_with_dividers(3), make_column_with_dividers(1)
        )

        assert render_column(tallest_first).height == pytest.approx(
            render_column(tallest_last).height
        )

    def test_empty_column_does_not_change_the_row_height(self) -> None:
        with_empty = Column().columns(make_column_with_dividers(2), Column())
        without_empty = Column().columns(make_column_with_dividers(2))

        assert render_column(with_empty).height == pytest.approx(
            render_column(without_empty).height
        )

    def test_row_counts_as_a_single_component_when_stacked(self) -> None:
        row = Column().columns(
            make_column_with_dividers(1), make_column_with_dividers(2)
        )
        row_height = render_column(row).height
        divider_height = render_column(Column().divider()).height

        stacked = Column().divider().columns(
            make_column_with_dividers(1), make_column_with_dividers(2)
        )

        assert render_column(stacked).height == pytest.approx(
            divider_height + measure_component_gap() + row_height
        )

    def test_columns_render_their_content_from_left_to_right(self) -> None:
        row = Column().columns(Column().text("LEFT"), Column().text("RIGHT"))

        content = read_text_content(render_column(row).svg)

        assert content.index("LEFT") < content.index("RIGHT")

    def test_every_column_content_is_rendered(self) -> None:
        row = Column().columns(
            Column().text("FIRST"), Column().text("SECOND"), Column().text("THIRD")
        )

        content = read_text_content(render_column(row).svg)

        assert all(label in content for label in ("FIRST", "SECOND", "THIRD"))
