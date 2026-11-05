from pathlib import Path
from typing import Literal
import pytest
from svgblock import Column
from .shared import render_column, write_minimal_png


def snapshot(column: Column) -> tuple[str, float]:
    """Return the rendered SVG and height of a column for later comparison."""
    rendered = render_column(column)
    return rendered.svg, rendered.height


class TestStateAfterFailedCalls:
    def test_image_with_invalid_width_leaves_the_column_unchanged(
        self, tmp_path: Path
    ) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(ValueError):
            column.image(write_minimal_png(tmp_path), width=0)

        assert snapshot(column) == before

    def test_image_with_missing_file_leaves_the_column_unchanged(
        self, tmp_path: Path
    ) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(OSError):
            column.image(tmp_path / "missing.png")

        assert snapshot(column) == before

    def test_columns_without_arguments_leaves_the_column_unchanged(self) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(ValueError):
            column.columns()

        assert snapshot(column) == before

    def test_table_with_malformed_row_leaves_the_column_unchanged(self) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(ValueError):
            column.table(["a", "b"], [["x", "y"], ["x"]])

        assert snapshot(column) == before

    def test_table_with_non_positive_weight_leaves_the_column_unchanged(self) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(ValueError):
            column.table(["a", "b"], [], weights=[1, 0])

        assert snapshot(column) == before

    def test_divider_with_invalid_coverage_leaves_the_column_unchanged(self) -> None:
        column = Column().divider()
        before = snapshot(column)

        with pytest.raises(ValueError):
            column.divider(coverage=2)

        assert snapshot(column) == before


class TestArgumentIsolation:
    def test_table_ignores_later_mutation_of_its_columns_and_rows(self) -> None:
        headers = ["name", "value"]
        rows = [["a", "1"]]
        column = Column().table(headers, rows)
        before = snapshot(column)

        headers[0] = "changed"
        rows[0][0] = "mutated"
        rows.append(["b", "2"])

        assert snapshot(column) == before

    def test_table_ignores_later_mutation_of_its_align_and_weights(self) -> None:
        align: list[Literal["left", "right"]] = ["left", "right"]
        weights = [1.0, 2.0]
        column = Column().table(
            ["a", "b"], [["x", "y"]], align=align, weights=weights)
        before = snapshot(column)

        align[0] = "right"
        weights[0] = 9.0

        assert snapshot(column) == before


class TestColumnNesting:
    def test_nested_columns_are_rendered(self) -> None:
        column = Column().columns(Column().columns(Column().divider()))

        assert render_column(column).height > 0

    def test_same_column_instance_can_be_placed_twice_in_one_row(self) -> None:
        shared = Column().divider()
        row = Column().columns(shared, shared)

        assert render_column(row).height == pytest.approx(
            render_column(Column().divider()).height
        )

    def test_columns_raises_value_error_when_column_contains_itself(self) -> None:
        column = Column()

        with pytest.raises(ValueError):
            column.columns(column)

    def test_columns_raises_value_error_when_columns_form_a_cycle(self) -> None:
        first = Column()
        second = Column().columns(first)

        with pytest.raises(ValueError):
            first.columns(second)


class TestNonFiniteNumbers:
    @pytest.mark.parametrize(
        "invalid_width",
        [
            pytest.param(float("nan"), id="nan"),
            pytest.param(float("inf"), id="inf"),
        ],
    )
    def test_image_raises_value_error_when_width_is_not_finite(
        self, tmp_path: Path, invalid_width: float
    ) -> None:
        with pytest.raises(ValueError):
            Column().image(write_minimal_png(tmp_path), width=invalid_width)

    @pytest.mark.parametrize(
        "invalid_weight",
        [
            pytest.param(float("nan"), id="nan"),
            pytest.param(float("inf"), id="inf"),
        ],
    )
    def test_table_raises_value_error_when_a_weight_is_not_finite(
        self, invalid_weight: float
    ) -> None:
        with pytest.raises(ValueError):
            Column().table(["a", "b"], [], weights=[1, invalid_weight])

    @pytest.mark.parametrize(
        "invalid_coverage", [float("nan"), float("inf"), float("-inf")]
    )
    def test_divider_raises_value_error_when_coverage_is_not_finite(
        self, invalid_coverage: float
    ) -> None:
        with pytest.raises(ValueError):
            Column().divider(coverage=invalid_coverage)
