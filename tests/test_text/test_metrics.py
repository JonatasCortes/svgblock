"""Tests for the public measurement helpers of the ``text`` package."""

import string
import pytest
from svgblock import calculate_baseline, calculate_line_height, measure_text_width

FONT_SIZE_WHERE_POINTS_EQUAL_FONT_UNITS = 1000.0
WIDTH_OF_AN_UNKNOWN_CHARACTER_IN_FONT_UNITS = 1000.0


class TestMeasureTextWidth:
    def test_empty_text_has_zero_width(self) -> None:
        assert measure_text_width("", 12.0) == 0.0

    def test_empty_bold_text_has_zero_width(self) -> None:
        assert measure_text_width("", 12.0, bold=True) == 0.0

    @pytest.mark.parametrize(
        "character, expected_font_units",
        [("i", 222), ("W", 944), (" ", 278), ("0", 556)],
    )
    def test_regular_characters_have_their_known_width_in_font_units(
        self, character: str, expected_font_units: int
    ) -> None:
        width = measure_text_width(
            character, FONT_SIZE_WHERE_POINTS_EQUAL_FONT_UNITS)

        assert width == pytest.approx(expected_font_units)

    @pytest.mark.parametrize(
        "character, expected_font_units",
        [("b", 611), ("W", 944), (" ", 278), ("i", 278)],
    )
    def test_bold_characters_have_their_known_width_in_font_units(
        self, character: str, expected_font_units: int
    ) -> None:
        width = measure_text_width(
            character, FONT_SIZE_WHERE_POINTS_EQUAL_FONT_UNITS, bold=True
        )

        assert width == pytest.approx(expected_font_units)

    def test_width_is_proportional_to_the_font_size(self) -> None:
        small = measure_text_width("Hello world", 10.0)
        large = measure_text_width("Hello world", 30.0)

        assert large == pytest.approx(3 * small)

    def test_zero_font_size_gives_zero_width(self) -> None:
        assert measure_text_width("Hello world", 0.0) == 0.0

    def test_width_of_a_concatenation_is_the_sum_of_the_widths_of_its_parts(
        self,
    ) -> None:
        first, second = "Hello ", "world!"

        combined = measure_text_width(first + second, 12.0)
        separate = measure_text_width(
            first, 12.0) + measure_text_width(second, 12.0)

        assert combined == pytest.approx(separate)

    def test_repeating_a_character_multiplies_its_width(self) -> None:
        single = measure_text_width("m", 12.0)

        assert measure_text_width("m" * 5, 12.0) == pytest.approx(5 * single)

    @pytest.mark.parametrize("letter", string.ascii_letters)
    def test_a_bold_letter_is_never_narrower_than_the_regular_letter(
        self, letter: str
    ) -> None:
        regular = measure_text_width(letter, 12.0)
        bold = measure_text_width(letter, 12.0, bold=True)

        assert bold >= regular

    @pytest.mark.parametrize("letter", ["b", "i", "m"])
    def test_a_bold_letter_can_be_strictly_wider_than_the_regular_letter(
        self, letter: str
    ) -> None:
        regular = measure_text_width(letter, 12.0)
        bold = measure_text_width(letter, 12.0, bold=True)

        assert bold > regular

    def test_a_bold_sentence_is_wider_than_the_same_regular_sentence(self) -> None:
        sentence = "The quick brown fox jumps over the lazy dog"

        regular = measure_text_width(sentence, 12.0)
        bold = measure_text_width(sentence, 12.0, bold=True)

        assert bold > regular

    @pytest.mark.parametrize(
        "accented_character, base_character",
        [("é", "e"), ("ç", "c"), ("ã", "a"), ("ü", "u"), ("Á", "A"), ("Ñ", "N")],
    )
    def test_an_accented_character_measures_like_its_base_character(
        self, accented_character: str, base_character: str
    ) -> None:
        accented_width = measure_text_width(accented_character, 12.0)
        base_width = measure_text_width(base_character, 12.0)

        assert accented_width == pytest.approx(base_width)

    @pytest.mark.parametrize(
        "accented_character, base_character",
        [("é", "e"), ("ç", "c"), ("Á", "A")],
    )
    def test_an_accented_bold_character_measures_like_its_bold_base_character(
        self, accented_character: str, base_character: str
    ) -> None:
        accented_width = measure_text_width(
            accented_character, 12.0, bold=True)
        base_width = measure_text_width(base_character, 12.0, bold=True)

        assert accented_width == pytest.approx(base_width)

    @pytest.mark.parametrize("unknown_character", ["中", "😀", "€", "­"])
    @pytest.mark.parametrize("bold", [False, True], ids=["regular", "bold"])
    def test_a_character_outside_the_font_table_has_the_unknown_character_width(
        self, unknown_character: str, bold: bool
    ) -> None:
        width = measure_text_width(
            unknown_character, FONT_SIZE_WHERE_POINTS_EQUAL_FONT_UNITS, bold=bold
        )

        assert width == pytest.approx(
            WIDTH_OF_AN_UNKNOWN_CHARACTER_IN_FONT_UNITS)


class TestCalculateLineHeight:
    def test_line_height_of_a_14_point_font_is_21_points(self) -> None:
        assert calculate_line_height(14.0) == pytest.approx(21.0)

    def test_line_height_is_proportional_to_the_font_size(self) -> None:
        assert calculate_line_height(30.0) == pytest.approx(
            3 * calculate_line_height(10.0)
        )

    def test_line_height_of_a_zero_font_size_is_zero(self) -> None:
        assert calculate_line_height(0.0) == 0.0

    @pytest.mark.parametrize("font_size", [8.0, 12.0, 16.0, 40.0])
    def test_line_height_is_larger_than_the_font_size(self, font_size: float) -> None:
        assert calculate_line_height(font_size) > font_size


class TestCalculateBaseline:
    def test_baseline_of_a_14_point_font_at_the_top_edge_is_15_point_4(self) -> None:
        assert calculate_baseline(
            top=0.0, font_size=14.0) == pytest.approx(15.4)

    def test_baseline_of_a_10_point_font_below_a_top_of_10_is_21(self) -> None:
        assert calculate_baseline(
            top=10.0, font_size=10.0) == pytest.approx(21.0)

    def test_moving_the_top_moves_the_baseline_by_the_same_distance(self) -> None:
        original = calculate_baseline(top=10.0, font_size=12.0)
        moved = calculate_baseline(top=15.0, font_size=12.0)

        assert moved - original == pytest.approx(5.0)

    def test_baseline_offset_from_the_top_is_proportional_to_the_font_size(
        self,
    ) -> None:
        small_offset = calculate_baseline(top=0.0, font_size=10.0)
        large_offset = calculate_baseline(top=0.0, font_size=30.0)

        assert large_offset == pytest.approx(3 * small_offset)

    def test_baseline_with_a_zero_font_size_is_the_top_itself(self) -> None:
        assert calculate_baseline(top=7.0, font_size=0.0) == pytest.approx(7.0)

    @pytest.mark.parametrize("font_size", [8.0, 12.0, 16.0, 40.0])
    def test_baseline_lies_between_the_top_and_the_bottom_of_the_line(
        self, font_size: float
    ) -> None:
        top = 100.0
        baseline = calculate_baseline(top=top, font_size=font_size)
        bottom = top + calculate_line_height(font_size)

        assert top < baseline < bottom
