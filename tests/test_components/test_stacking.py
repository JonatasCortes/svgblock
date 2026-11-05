import pytest
from svgblock import Column
from .shared import make_column_with_dividers, measure_component_gap, render_column


class TestEmptyComposer:
    def test_empty_column_renders_empty_svg(self) -> None:
        assert render_column(Column()).svg == ""

    def test_empty_column_renders_zero_height(self) -> None:
        assert render_column(Column()).height == 0


class TestHeightAccumulation:
    def test_single_component_height_has_no_gap(self) -> None:
        single = render_column(make_column_with_dividers(1)).height

        assert single > 0
        assert render_column(
            Column().divider()).height == pytest.approx(single)

    @pytest.mark.parametrize("count", [2, 3, 5, 10])
    def test_height_equals_component_heights_plus_gaps_between_them(
        self, count: int
    ) -> None:
        single = render_column(make_column_with_dividers(1)).height
        gap = measure_component_gap()

        stacked = render_column(make_column_with_dividers(count)).height

        assert stacked == pytest.approx(count * single + (count - 1) * gap)

    def test_height_of_mixed_components_is_independent_of_insertion_order(
        self,
    ) -> None:
        title_first = Column().title("Heading").divider().text("Body")
        divider_first = Column().divider().text("Body").title("Heading")

        assert render_column(title_first).height == pytest.approx(
            render_column(divider_first).height
        )

    def test_height_of_mixed_components_equals_standalone_heights_plus_gaps(
        self,
    ) -> None:
        title = render_column(Column().title("Heading")).height
        divider = render_column(Column().divider()).height
        text = render_column(Column().text("Body")).height
        gap = measure_component_gap()

        stacked = render_column(Column().title(
            "Heading").divider().text("Body"))

        assert stacked.height == pytest.approx(
            title + divider + text + 2 * gap)


class TestComponentOrder:
    def test_svg_depends_on_insertion_order(self) -> None:
        title_first = render_column(Column().title("Heading").divider()).svg
        divider_first = render_column(Column().divider().title("Heading")).svg
        assert title_first != divider_first


class TestRenderDeterminism:
    def test_rendering_the_same_column_twice_yields_identical_results(self) -> None:
        column = Column().title("Heading").divider().text("Body")

        first = render_column(column)
        second = render_column(column)

        assert first.svg == second.svg
        assert first.height == second.height

    def test_rendering_does_not_alter_the_column_for_later_additions(self) -> None:
        column = Column().divider()
        before = render_column(column).height

        column.divider()

        assert render_column(column).height > before
