import re

import pytest

from svgblock.components import Column, Composer

from .shared import DEFAULT_COLUMN_WEIGHT


class TestWeight:
    def test_default_weight_matches_the_default_column_weight(self) -> None:
        assert Column().weight == DEFAULT_COLUMN_WEIGHT

    @pytest.mark.parametrize("weight", [1, 0.1, 2.5, 100])
    def test_weight_exposes_the_value_given_at_construction(
        self, weight: float
    ) -> None:
        assert Column(weight=weight).weight == weight

    def test_weight_accepts_a_positional_argument(self) -> None:
        assert Column(3).weight == 3

    def test_weight_is_unchanged_by_adding_components(self) -> None:
        column = Column(weight=2.5).title("Heading").divider().text("Body")

        assert column.weight == 2.5

    def test_weight_is_read_only(self) -> None:
        column = Column(weight=2)

        with pytest.raises(AttributeError):
            column.weight = 5  # type: ignore[misc]


class TestWeightValidation:
    @pytest.mark.parametrize("invalid_weight", [0, -1, -0.5])
    def test_constructor_raises_value_error_when_weight_is_not_positive(
        self, invalid_weight: float
    ) -> None:
        with pytest.raises(ValueError, match="greater than zero"):
            Column(weight=invalid_weight)

    @pytest.mark.parametrize("invalid_weight", [0, -1, -0.5])
    def test_constructor_error_message_contains_the_received_weight(
        self, invalid_weight: float
    ) -> None:
        with pytest.raises(ValueError, match=re.escape(f"got {invalid_weight!r}")):
            Column(weight=invalid_weight)

    @pytest.mark.parametrize(
        "invalid_weight",
        [
            pytest.param(float("nan"), id="nan"),
            pytest.param(float("inf"), id="inf"),
        ],
    )
    def test_constructor_raises_value_error_when_weight_is_not_finite(
        self, invalid_weight: float
    ) -> None:
        with pytest.raises(ValueError):
            Column(weight=invalid_weight)


class TestInheritance:
    def test_column_is_a_composer(self) -> None:
        assert isinstance(Column(), Composer)
