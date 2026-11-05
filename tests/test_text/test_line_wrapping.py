"""Tests for the public line-wrapping API: ``wrap_into_lines`` and ``wrap_bold_text``.

All widths are expressed in font units: with ``FONT_SIZE`` equal to 1000 a
width in points is numerically equal to the width in font units, which keeps
every comparison exact.
"""

import pytest
from svgblock import Style, TextSegment, measure_text_width, wrap_bold_text, wrap_into_lines
from .shared import plain, styled

FONT_SIZE = 1000.0
UNLIMITED_WIDTH = 1_000_000.0

SAMPLE_TEXTS: tuple[str, ...] = (
    "The quick brown fox jumps over the lazy dog",
    "Supercalifragilisticexpialidocious is a long word",
    "a b c d e f g h",
    "WWWW iiii MMMM llll",
    "Olá, você já viu o João? Ação é coração.",
)
SAMPLE_WIDTHS: tuple[float, ...] = (1.0, 500.0, 2000.0, 5000.0, 20000.0)
WIDTHS_FITTING_THE_WIDEST_WORD_OF_THE_FIRST_SAMPLE: tuple[float, ...] = (
    2723.0,
    4000.0,
    8000.0,
)

every_style = pytest.mark.parametrize(
    "style", list(Style), ids=lambda style: style.name.lower()
)
every_style_except_highlight = pytest.mark.parametrize(
    "style",
    [style for style in Style if style is not Style.HIGHLIGHT],
    ids=lambda style: style.name.lower(),
)
every_sample_text = pytest.mark.parametrize("text", SAMPLE_TEXTS)
every_sample_width = pytest.mark.parametrize("max_width", SAMPLE_WIDTHS)


def width_of(text: str, bold: bool = False) -> float:
    """Measure ``text`` at ``FONT_SIZE``."""
    return measure_text_width(text, FONT_SIZE, bold=bold)


def wrap(
    segments: list[TextSegment], max_width: float, bold: bool = False
) -> list[list[TextSegment]]:
    """Wrap ``segments`` at ``FONT_SIZE``."""
    return wrap_into_lines(segments, FONT_SIZE, max_width, bold)


def line_texts(lines: list[list[TextSegment]]) -> list[str]:
    """Return the concatenated text of every line."""
    return ["".join(segment.text for segment in line) for line in lines]


def line_width(line: list[TextSegment], bold: bool = False) -> float:
    """Measure a wrapped line segment by segment."""
    return sum(
        width_of(segment.text, bold=bold or segment.is_bold) for segment in line
    )


class TestWrappingPlainText:
    def test_no_segments_produce_no_lines(self) -> None:
        assert wrap([], UNLIMITED_WIDTH) == []

    def test_text_that_fits_stays_on_a_single_line(self) -> None:
        assert wrap([plain("hello world")], UNLIMITED_WIDTH) == [
            [plain("hello world")]]

    def test_a_single_word_that_fits_stays_on_a_single_line(self) -> None:
        assert wrap([plain("hello")], UNLIMITED_WIDTH) == [[plain("hello")]]

    def test_text_breaks_at_the_last_space_that_still_fits(self) -> None:
        max_width = width_of("aa bb")

        assert line_texts(wrap([plain("aa bb cc")], max_width)) == [
            "aa bb", "cc"]

    def test_every_word_gets_its_own_line_when_no_two_words_fit_together(self) -> None:
        max_width = width_of("aa")

        assert line_texts(wrap([plain("aa bb cc")], max_width)) == [
            "aa", "bb", "cc"]

    def test_a_line_that_fills_the_width_exactly_is_not_broken(self) -> None:
        max_width = width_of("aa bb")

        assert line_texts(wrap([plain("aa bb")], max_width)) == ["aa bb"]

    def test_a_line_that_exceeds_the_width_by_a_single_unit_is_broken(self) -> None:
        max_width = width_of("aa bb") - 1

        assert line_texts(wrap([plain("aa bb")], max_width)) == ["aa", "bb"]

    def test_the_space_at_a_line_break_is_removed_from_both_lines(self) -> None:
        lines = line_texts(wrap([plain("aa bb")], width_of("aa")))

        assert lines == ["aa", "bb"]

    def test_trailing_whitespace_at_the_end_of_the_text_is_removed(self) -> None:
        assert line_texts(wrap([plain("hello   ")], UNLIMITED_WIDTH)) == [
            "hello"]

    def test_several_spaces_inside_a_line_are_preserved(self) -> None:
        assert line_texts(wrap([plain("a  b")], UNLIMITED_WIDTH)) == ["a  b"]

    def test_the_input_segments_are_not_modified(self) -> None:
        segments = [plain("aa "), styled("bb cc", Style.ITALIC)]
        snapshot = list(segments)

        wrap(segments, width_of("aa"))

        assert segments == snapshot


class TestWrappingStyledText:
    @every_style
    def test_a_style_is_kept_on_every_line_after_a_break(self, style: Style) -> None:
        lines = wrap([styled("aa aa", style)], width_of("aa", bold=True))

        assert lines == [[styled("aa", style)], [styled("aa", style)]]

    def test_styles_stay_attached_to_the_words_they_were_applied_to(self) -> None:
        segments = [plain("a "), styled("b", Style.ITALIC)]

        assert wrap(segments, UNLIMITED_WIDTH) == [
            [plain("a "), styled("b", Style.ITALIC)]
        ]

    def test_adjacent_segments_with_the_same_styles_are_merged_within_a_line(
        self,
    ) -> None:
        segments = [plain("a "), plain("b")]

        assert wrap(segments, UNLIMITED_WIDTH) == [[plain("a b")]]

    def test_adjacent_segments_with_different_styles_are_kept_apart_within_a_line(
        self,
    ) -> None:
        segments = [styled("a ", Style.ITALIC), styled("b", Style.UNDERLINE)]

        assert wrap(segments, UNLIMITED_WIDTH) == [
            [styled("a ", Style.ITALIC), styled("b", Style.UNDERLINE)]
        ]

    def test_a_word_spanning_two_styles_is_never_split_at_the_style_boundary(
        self,
    ) -> None:
        segments = [plain("x ne"), styled("gro", Style.HIGHLIGHT), plain(" y")]
        max_width = width_of("ne") + width_of("gro", bold=True)

        assert wrap(segments, max_width) == [
            [plain("x")],
            [plain("ne"), styled("gro", Style.HIGHLIGHT)],
            [plain("y")],
        ]

    def test_text_in_a_highlighted_segment_is_measured_as_bold(self) -> None:
        max_width = width_of("bbbb bbbb")

        regular_lines = wrap([plain("bbbb bbbb")], max_width)
        highlighted_lines = wrap(
            [styled("bbbb bbbb", Style.HIGHLIGHT)], max_width)

        assert len(regular_lines) == 1
        assert len(highlighted_lines) == 2

    @every_style_except_highlight
    def test_styles_other_than_highlight_do_not_change_where_lines_break(
        self, style: Style
    ) -> None:
        max_width = width_of("bbbb bbbb")

        assert line_texts(wrap([styled("bbbb bbbb", style)], max_width)) == [
            "bbbb bbbb"
        ]

    def test_the_bold_flag_measures_unstyled_text_as_bold(self) -> None:
        max_width = width_of("bbbb bbbb")

        regular_lines = wrap([plain("bbbb bbbb")], max_width, bold=False)
        forced_bold_lines = wrap([plain("bbbb bbbb")], max_width, bold=True)

        assert len(regular_lines) == 1
        assert len(forced_bold_lines) == 2

    def test_the_bold_flag_does_not_add_styles_to_the_returned_segments(self) -> None:
        lines = wrap([plain("aa aa")], width_of("aa", bold=True), bold=True)

        assert lines == [[plain("aa")], [plain("aa")]]


class TestWrappingWordsLongerThanTheLine:
    def test_a_word_longer_than_the_line_is_broken_between_characters(self) -> None:
        max_width = width_of("aa")

        assert line_texts(wrap([plain("aaaaaa")], max_width)) == [
            "aa", "aa", "aa"]

    def test_a_word_that_fits_exactly_is_not_broken(self) -> None:
        assert line_texts(wrap([plain("aa")], width_of("aa"))) == ["aa"]

    def test_a_word_that_exceeds_the_width_by_a_single_unit_is_broken(self) -> None:
        assert line_texts(
            wrap([plain("aa")], width_of("aa") - 1)) == ["a", "a"]

    def test_the_last_fragment_of_a_broken_word_keeps_the_remaining_characters(
        self,
    ) -> None:
        max_width = width_of("aa")

        assert line_texts(wrap([plain("aaaaa")], max_width)) == [
            "aa", "aa", "a"]

    def test_words_around_a_broken_word_are_kept_on_their_own_lines(self) -> None:
        max_width = width_of("aa")

        assert line_texts(wrap([plain("x aaaaaa y")], max_width)) == [
            "x",
            "aa",
            "aa",
            "aa",
            "y",
        ]

    def test_styles_of_each_character_are_kept_when_a_word_is_broken(self) -> None:
        segments = [plain("mm"), styled("mmmm", Style.ITALIC)]

        assert wrap(segments, width_of("mm")) == [
            [plain("mm")],
            [styled("mm", Style.ITALIC)],
            [styled("mm", Style.ITALIC)],
        ]

    def test_a_broken_word_can_contain_characters_with_different_styles_in_one_line(
        self,
    ) -> None:
        segments = [plain("m"), styled("m", Style.ITALIC)]

        assert wrap(segments, width_of("mm")) == [
            [plain("m"), styled("m", Style.ITALIC)]
        ]

    @pytest.mark.parametrize("max_width", [0.0, 1.0, 100.0])
    def test_a_width_smaller_than_every_character_produces_one_character_per_line(
        self, max_width: float
    ) -> None:
        assert line_texts(wrap([plain("abc")], max_width)) == ["a", "b", "c"]


class TestWrappingInvariants:
    @every_sample_text
    @every_sample_width
    @pytest.mark.parametrize("bold", [False, True], ids=["regular", "bold"])
    def test_no_line_is_wider_than_the_maximum_unless_it_is_a_single_character(
        self, text: str, max_width: float, bold: bool
    ) -> None:
        lines = wrap([plain(text)], max_width, bold=bold)

        for line in lines:
            is_single_character = len("".join(s.text for s in line)) == 1
            assert line_width(
                line, bold=bold) <= max_width or is_single_character

    @every_sample_text
    @every_sample_width
    def test_joining_the_lines_restores_the_text_without_its_spaces(
        self, text: str, max_width: float
    ) -> None:
        lines = wrap([plain(text)], max_width)

        assert "".join(line_texts(lines)).replace(
            " ", "") == text.replace(" ", "")

    @pytest.mark.parametrize(
        "max_width", WIDTHS_FITTING_THE_WIDEST_WORD_OF_THE_FIRST_SAMPLE
    )
    def test_joining_the_lines_with_a_space_restores_the_original_text(
        self, max_width: float
    ) -> None:
        text = SAMPLE_TEXTS[0]

        lines = line_texts(wrap([plain(text)], max_width))

        assert " ".join(lines) == text

    @every_sample_text
    @every_sample_width
    def test_no_line_is_empty_or_starts_or_ends_with_a_space(
        self, text: str, max_width: float
    ) -> None:
        for line_text in line_texts(wrap([plain(text)], max_width)):
            assert line_text != ""
            assert not line_text.startswith(" ")
            assert not line_text.endswith(" ")

    @pytest.mark.parametrize(
        "max_width", WIDTHS_FITTING_THE_WIDEST_WORD_OF_THE_FIRST_SAMPLE
    )
    def test_words_that_fit_on_a_line_are_never_split(self, max_width: float) -> None:
        text = SAMPLE_TEXTS[0]
        lines = line_texts(wrap([plain(text)], max_width))

        words_in_lines = [word for line in lines for word in line.split(" ")]

        assert words_in_lines == text.split(" ")

    @every_sample_text
    @every_sample_width
    def test_wrapping_the_same_segments_twice_gives_the_same_lines(
        self, text: str, max_width: float
    ) -> None:
        segments = [plain(text)]

        assert wrap(segments, max_width) == wrap(segments, max_width)


class TestWrapBoldText:
    def test_empty_text_produces_a_single_empty_line(self) -> None:
        assert wrap_bold_text("", FONT_SIZE, UNLIMITED_WIDTH) == [""]

    def test_text_that_fits_is_returned_as_a_single_string(self) -> None:
        assert wrap_bold_text("hello world", FONT_SIZE, UNLIMITED_WIDTH) == [
            "hello world"
        ]

    def test_text_is_measured_as_bold_when_deciding_where_to_break(self) -> None:
        max_width = width_of("bbbb bbbb")

        assert line_texts(wrap([plain("bbbb bbbb")], max_width)) == [
            "bbbb bbbb"]
        assert wrap_bold_text("bbbb bbbb", FONT_SIZE, max_width) == [
            "bbbb", "bbbb"]

    @every_sample_text
    @every_sample_width
    def test_result_equals_the_text_of_the_bold_wrapped_lines(
        self, text: str, max_width: float
    ) -> None:
        expected = line_texts(wrap([plain(text)], max_width, bold=True))

        assert wrap_bold_text(text, FONT_SIZE, max_width) == expected

    def test_markup_markers_are_treated_as_ordinary_text(self) -> None:
        assert wrap_bold_text("**a**", FONT_SIZE, UNLIMITED_WIDTH) == ["**a**"]

    def test_a_word_longer_than_the_line_is_broken_between_characters(self) -> None:
        max_width = width_of("aa", bold=True)

        assert wrap_bold_text("aaaaaa", FONT_SIZE, max_width) == [
            "aa", "aa", "aa"]


class TestWhitespaceHandling:

    def test_whitespace_split_across_two_segments_is_preserved(self) -> None:
        segments = [plain("a "), plain(" b")]

        assert line_texts(wrap(segments, UNLIMITED_WIDTH)) == ["a  b"]

    def test_leading_whitespace_of_the_text_is_preserved(self) -> None:
        assert line_texts(wrap([plain("  indented")], UNLIMITED_WIDTH)) == [
            "  indented"
        ]

    def test_a_tab_between_words_occupies_the_width_of_a_space(self) -> None:
        max_width = width_of("a b")

        assert line_texts(wrap([plain("a\tb")], max_width)) == ["a\tb"]
