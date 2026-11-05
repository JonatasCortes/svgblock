import re
from pathlib import Path
from typing import Literal
import pytest
from svgblock import Column, Composer
from .shared import write_minimal_png


@pytest.fixture
def composer() -> Composer:
    return Composer()


@pytest.fixture
def image_path(tmp_path: Path) -> Path:
    return write_minimal_png(tmp_path)


class TestImageValidation:
    @pytest.mark.parametrize("invalid_width", [0, -1, -0.5])
    def test_image_raises_value_error_when_width_is_not_positive(
        self, composer: Composer, image_path: Path, invalid_width: float
    ) -> None:
        with pytest.raises(ValueError, match=re.escape(f"got {invalid_width!r}")):
            composer.image(image_path, width=invalid_width)

    def test_image_error_message_states_width_must_be_greater_than_zero(
        self, composer: Composer, image_path: Path
    ) -> None:
        with pytest.raises(ValueError, match="greater than zero"):
            composer.image(image_path, width=0)

    @pytest.mark.parametrize("valid_width", [None, 1, 0.5, 250])
    def test_image_accepts_valid_width(
        self, composer: Composer, image_path: Path, valid_width: float | None
    ) -> None:
        composer.image(image_path, width=valid_width)

    def test_image_accepts_path_as_string(
        self, composer: Composer, image_path: Path
    ) -> None:
        composer.image(str(image_path))


class TestColumnsValidation:
    def test_columns_raises_value_error_when_called_without_columns(
        self, composer: Composer
    ) -> None:
        with pytest.raises(ValueError, match="at least one Column"):
            composer.columns()

    def test_columns_accepts_a_single_column(self, composer: Composer) -> None:
        composer.columns(Column().divider())

    def test_columns_accepts_multiple_columns(self, composer: Composer) -> None:
        composer.columns(Column().divider(), Column(weight=2).divider())


class TestTableValidation:
    def test_table_raises_value_error_when_columns_are_empty(
        self, composer: Composer
    ) -> None:
        with pytest.raises(ValueError, match="at least one column"):
            composer.table(columns=[], rows=[])

    @pytest.mark.parametrize(
        "invalid_row, received_cells",
        [
            (["only"], 1),
            (["first", "second", "third"], 3),
            ([], 0),
        ],
    )
    def test_table_raises_value_error_when_row_cell_count_differs_from_columns(
        self, composer: Composer, invalid_row: list[str], received_cells: int
    ) -> None:
        with pytest.raises(
            ValueError,
            match=f"Every row needs 2 cells, got {received_cells}",
        ):
            composer.table(columns=["a", "b"], rows=[invalid_row])

    def test_table_raises_value_error_when_only_a_later_row_is_malformed(
        self, composer: Composer
    ) -> None:
        with pytest.raises(ValueError, match="Every row needs 2 cells"):
            composer.table(
                columns=["a", "b"],
                rows=[["x", "y"], ["x", "y"], ["x"]],
            )

    @pytest.mark.parametrize("alignments", [["left"], ["left", "right", "left"], []])
    def test_table_raises_value_error_when_align_length_differs_from_columns(
        self, composer: Composer, alignments: list[Literal["left", "right"]]
    ) -> None:
        with pytest.raises(
            ValueError,
            match=f"align needs 2 values, got {len(alignments)}",
        ):
            composer.table(columns=["a", "b"], rows=[], align=alignments)

    @pytest.mark.parametrize("weights", [[1], [1, 1, 1], []])
    def test_table_raises_value_error_when_weights_length_differs_from_columns(
        self, composer: Composer, weights: list[float]
    ) -> None:
        with pytest.raises(
            ValueError,
            match=f"weights needs 2 values, got {len(weights)}",
        ):
            composer.table(columns=["a", "b"], rows=[], weights=weights)

    @pytest.mark.parametrize("weights", [[1, 0], [0, 0], [1, -1], [-0.5, 2]])
    def test_table_raises_value_error_when_any_weight_is_not_positive(
        self, composer: Composer, weights: list[float]
    ) -> None:
        with pytest.raises(ValueError, match="weights must be greater than zero"):
            composer.table(columns=["a", "b"], rows=[], weights=weights)

    def test_table_accepts_empty_rows(self, composer: Composer) -> None:
        composer.table(columns=["a", "b"], rows=[])

    def test_table_accepts_rows_matching_column_count(
        self, composer: Composer
    ) -> None:
        composer.table(columns=["a", "b"], rows=[["x", "y"], ["z", "w"]])

    def test_table_accepts_rows_and_columns_as_tuples(
        self, composer: Composer
    ) -> None:
        composer.table(columns=("a", "b"), rows=(("x", "y"),))

    def test_table_accepts_valid_alignments_and_weights(
        self, composer: Composer
    ) -> None:
        composer.table(
            columns=["a", "b"],
            rows=[["x", "y"]],
            align=["left", "right"],
            weights=[1, 2.5],
        )

    def test_table_accepts_fractional_positive_weights(
        self, composer: Composer
    ) -> None:
        composer.table(columns=["a", "b"], rows=[], weights=[0.1, 0.2])


class TestDividerValidation:
    @pytest.mark.parametrize("invalid_coverage", [-0.01, -1, 1.01, 2])
    def test_divider_raises_value_error_when_coverage_is_outside_unit_interval(
        self, composer: Composer, invalid_coverage: float
    ) -> None:
        with pytest.raises(ValueError, match=re.escape(f"got {invalid_coverage!r}")):
            composer.divider(coverage=invalid_coverage)

    def test_divider_error_message_states_valid_interval(
        self, composer: Composer
    ) -> None:
        with pytest.raises(ValueError, match="between 0 and 1"):
            composer.divider(coverage=3)

    @pytest.mark.parametrize("boundary_coverage", [0, 1, 0.0, 1.0])
    def test_divider_accepts_boundary_coverage(
        self, composer: Composer, boundary_coverage: float
    ) -> None:
        composer.divider(coverage=boundary_coverage)

    @pytest.mark.parametrize("inner_coverage", [0.25, 0.5, 0.999])
    def test_divider_accepts_coverage_inside_interval(
        self, composer: Composer, inner_coverage: float
    ) -> None:
        composer.divider(coverage=inner_coverage)

    def test_divider_accepts_default_coverage(self, composer: Composer) -> None:
        composer.divider()
