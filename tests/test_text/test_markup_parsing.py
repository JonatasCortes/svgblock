"""Tests for the public markup API: ``parse_markup``, ``Style`` and ``TextSegment``."""

import re
from dataclasses import FrozenInstanceError
import pytest
from svgblock import Style, TextSegment, parse_markup
from .shared import (
    ALL_MARKUP_SYNTAXES,
    ESCAPABLE_CHARACTERS,
    ESCAPE_CHARACTER,
    MARKER_CHARACTERS,
    ORDERED_MARKUP_SYNTAX_PAIRS,
    MarkupSyntax,
    escape_every_character,
    markup_syntax_id,
    plain,
    styled,
    wrap_in,
)

every_markup_syntax = pytest.mark.parametrize(
    "syntax", ALL_MARKUP_SYNTAXES, ids=markup_syntax_id
)
every_ordered_markup_syntax_pair = pytest.mark.parametrize(
    "outer, inner",
    ORDERED_MARKUP_SYNTAX_PAIRS,
    ids=lambda syntax: markup_syntax_id(syntax),
)


class TestMarkupRegistryCoversPublicStyles:
    def test_every_style_member_has_a_registered_markup_syntax(self) -> None:
        """Fails when a ``Style`` is added without a matching entry in ``shared.py``."""
        registered_styles = {syntax.style for syntax in ALL_MARKUP_SYNTAXES}

        assert registered_styles == set(Style)

    def test_every_registered_marker_is_unique(self) -> None:
        markers = [syntax.marker for syntax in ALL_MARKUP_SYNTAXES]

        assert len(markers) == len(set(markers))

    def test_every_registered_style_is_unique(self) -> None:
        styles = [syntax.style for syntax in ALL_MARKUP_SYNTAXES]

        assert len(styles) == len(set(styles))


class TestParsingTextWithoutMarkup:
    def test_empty_text_produces_no_segments(self) -> None:
        assert parse_markup("") == []

    def test_text_without_markers_produces_one_segment_without_styles(self) -> None:
        assert parse_markup("hello world") == [plain("hello world")]

    def test_whitespace_only_text_is_preserved_as_a_single_unstyled_segment(
        self,
    ) -> None:
        assert parse_markup("   ") == [plain("   ")]

    @pytest.mark.parametrize("marker_character", MARKER_CHARACTERS)
    def test_a_single_marker_character_is_kept_as_literal_text(
        self, marker_character: str
    ) -> None:
        text = f"before{marker_character}after"

        assert parse_markup(text) == [plain(text)]

    def test_a_lone_backslash_before_ordinary_text_is_kept_as_literal_text(
        self,
    ) -> None:
        assert parse_markup("path\\name") == [plain("path\\name")]


class TestParsingSingleMarkup:
    @every_markup_syntax
    def test_text_between_markers_receives_the_style(
        self, syntax: MarkupSyntax
    ) -> None:
        assert parse_markup(wrap_in(syntax, "word")) == [
            styled("word", syntax.style)]

    @every_markup_syntax
    def test_text_around_markers_stays_unstyled(self, syntax: MarkupSyntax) -> None:
        text = f"before {wrap_in(syntax, 'middle')} after"

        assert parse_markup(text) == [
            plain("before "),
            styled("middle", syntax.style),
            plain(" after"),
        ]

    @every_markup_syntax
    def test_markers_without_surrounding_spaces_still_split_the_segments(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"a{wrap_in(syntax, 'b')}c"

        assert parse_markup(text) == [
            plain("a"),
            styled("b", syntax.style),
            plain("c"),
        ]

    @every_markup_syntax
    def test_markers_never_appear_in_the_resulting_text(
        self, syntax: MarkupSyntax
    ) -> None:
        segments = parse_markup(f"a {wrap_in(syntax, 'b')} c")

        assert all(syntax.marker not in segment.text for segment in segments)

    @every_markup_syntax
    def test_a_marker_pair_with_nothing_between_produces_no_segments(
        self, syntax: MarkupSyntax
    ) -> None:
        assert parse_markup(wrap_in(syntax, "")) == []

    @every_markup_syntax
    def test_whitespace_between_markers_is_preserved_inside_the_styled_segment(
        self, syntax: MarkupSyntax
    ) -> None:
        assert parse_markup(wrap_in(syntax, " ")) == [
            styled(" ", syntax.style)]

    @every_markup_syntax
    def test_the_same_markup_can_be_used_several_times_in_one_text(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"{wrap_in(syntax, 'one')} and {wrap_in(syntax, 'two')}"

        assert parse_markup(text) == [
            styled("one", syntax.style),
            plain(" and "),
            styled("two", syntax.style),
        ]

    def test_adjacent_ranges_with_the_same_style_are_merged_into_one_segment(
        self,
    ) -> None:
        highlight = ALL_MARKUP_SYNTAXES[0]
        text = f"{wrap_in(highlight, 'a')}{wrap_in(highlight, 'b')}"

        assert parse_markup(text) == [styled("ab", highlight.style)]


class TestParsingCombinedMarkups:
    @every_ordered_markup_syntax_pair
    def test_nested_markups_accumulate_styles_in_opening_order(
        self, outer: MarkupSyntax, inner: MarkupSyntax
    ) -> None:
        text = wrap_in(outer, wrap_in(inner, "x"))

        assert parse_markup(text) == [styled("x", outer.style, inner.style)]

    @every_ordered_markup_syntax_pair
    def test_text_around_a_nested_markup_keeps_only_the_outer_style(
        self, outer: MarkupSyntax, inner: MarkupSyntax
    ) -> None:
        text = wrap_in(outer, f"a{wrap_in(inner, 'b')}c")

        assert parse_markup(text) == [
            styled("a", outer.style),
            styled("b", outer.style, inner.style),
            styled("c", outer.style),
        ]

    @every_ordered_markup_syntax_pair
    def test_overlapping_markups_apply_each_style_only_while_it_is_open(
        self, outer: MarkupSyntax, inner: MarkupSyntax
    ) -> None:
        text = f"{outer.marker}x{inner.marker}y{outer.marker}z{inner.marker}"

        assert parse_markup(text) == [
            styled("x", outer.style),
            styled("y", outer.style, inner.style),
            styled("z", inner.style),
        ]

    def test_all_registered_markups_can_be_open_at_the_same_time(self) -> None:
        text = "".join(syntax.marker for syntax in ALL_MARKUP_SYNTAXES)
        text += "x"
        text += "".join(syntax.marker for syntax in reversed(ALL_MARKUP_SYNTAXES))
        every_style_in_opening_order = tuple(
            syntax.style for syntax in ALL_MARKUP_SYNTAXES
        )

        assert parse_markup(text) == [styled(
            "x", *every_style_in_opening_order)]


class TestEscapingMarkers:
    @every_markup_syntax
    def test_escaping_every_character_of_a_marker_produces_it_as_literal_text(
        self, syntax: MarkupSyntax
    ) -> None:
        text = escape_every_character(syntax.marker)

        assert parse_markup(text) == [plain(syntax.marker)]

    @every_markup_syntax
    def test_escaping_only_the_first_character_of_a_marker_prevents_it_from_toggling(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"{ESCAPE_CHARACTER}{syntax.marker}"

        assert parse_markup(text) == [plain(syntax.marker)]

    @every_markup_syntax
    def test_an_escaped_marker_inside_styled_text_stays_literal_and_styled(
        self, syntax: MarkupSyntax
    ) -> None:
        text = wrap_in(syntax, f"a{escape_every_character(syntax.marker)}b")

        assert parse_markup(text) == [styled(
            f"a{syntax.marker}b", syntax.style)]

    @every_markup_syntax
    def test_an_escaped_marker_does_not_close_an_open_markup(
        self, syntax: MarkupSyntax
    ) -> None:
        escaped_marker = escape_every_character(syntax.marker)
        text = f"{syntax.marker}a{escaped_marker}b{syntax.marker}"

        assert parse_markup(text) == [styled(
            f"a{syntax.marker}b", syntax.style)]

    @pytest.mark.parametrize("escapable_character", ESCAPABLE_CHARACTERS)
    def test_every_escapable_character_loses_its_escape_prefix(
        self, escapable_character: str
    ) -> None:
        text = f"{ESCAPE_CHARACTER}{escapable_character}"

        assert parse_markup(text) == [plain(escapable_character)]

    def test_an_escaped_backslash_produces_one_literal_backslash(self) -> None:
        assert parse_markup(ESCAPE_CHARACTER * 2) == [plain(ESCAPE_CHARACTER)]

    @every_markup_syntax
    def test_an_escaped_backslash_before_a_marker_leaves_the_marker_active(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"{ESCAPE_CHARACTER * 2}{wrap_in(syntax, 'x')}"

        assert parse_markup(text) == [
            plain(ESCAPE_CHARACTER),
            styled("x", syntax.style),
        ]

    def test_a_trailing_backslash_is_kept_as_literal_text(self) -> None:
        assert parse_markup(f"text{ESCAPE_CHARACTER}") == [
            plain(f"text{ESCAPE_CHARACTER}")
        ]

    def test_a_backslash_before_a_non_escapable_character_is_kept_as_literal_text(
        self,
    ) -> None:
        assert parse_markup(f"{ESCAPE_CHARACTER}n") == [
            plain(f"{ESCAPE_CHARACTER}n")]


class TestParsingUnclosedMarkers:
    @every_markup_syntax
    def test_a_marker_that_is_never_closed_raises_value_error_naming_the_marker(
        self, syntax: MarkupSyntax
    ) -> None:
        with pytest.raises(ValueError, match=re.escape(f"Unclosed marker '{syntax.marker}'")):
            parse_markup(f"{syntax.marker}text")

    @every_markup_syntax
    def test_the_error_message_contains_the_offending_text(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"{syntax.marker}text"

        with pytest.raises(ValueError, match=re.escape(repr(text))):
            parse_markup(text)

    @every_markup_syntax
    def test_the_error_message_suggests_escaping_the_marker(
        self, syntax: MarkupSyntax
    ) -> None:
        suggestion = f"use {ESCAPE_CHARACTER}{syntax.marker[0]} for a literal one"

        with pytest.raises(ValueError, match=re.escape(suggestion)):
            parse_markup(f"{syntax.marker}text")

    @every_ordered_markup_syntax_pair
    def test_the_error_names_the_marker_that_is_still_open_after_the_other_closed(
        self, outer: MarkupSyntax, inner: MarkupSyntax
    ) -> None:
        text = f"{outer.marker}a{inner.marker}b{outer.marker}c"

        with pytest.raises(ValueError, match=re.escape(f"Unclosed marker '{inner.marker}'")):
            parse_markup(text)

    @every_markup_syntax
    def test_an_odd_number_of_markers_raises_value_error(
        self, syntax: MarkupSyntax
    ) -> None:
        text = f"{wrap_in(syntax, 'a')} b {syntax.marker} c"

        with pytest.raises(ValueError):
            parse_markup(text)


class TestTextSegment:
    def test_a_segment_has_no_styles_by_default(self) -> None:
        assert TextSegment(text="abc").styles == ()

    def test_segments_with_the_same_text_and_styles_are_equal(self) -> None:
        assert styled("abc", Style.ITALIC) == styled("abc", Style.ITALIC)

    def test_segments_with_different_styles_are_not_equal(self) -> None:
        assert styled("abc", Style.ITALIC) != styled("abc", Style.UNDERLINE)

    def test_segments_with_the_same_styles_in_a_different_order_are_not_equal(
        self,
    ) -> None:
        first = styled("abc", Style.ITALIC, Style.UNDERLINE)
        second = styled("abc", Style.UNDERLINE, Style.ITALIC)

        assert first != second

    def test_equal_segments_have_equal_hashes(self) -> None:
        assert hash(styled("abc", Style.ITALIC)) == hash(
            styled("abc", Style.ITALIC))

    @pytest.mark.parametrize("attribute_name", ["text", "styles"])
    def test_segments_are_immutable(self, attribute_name: str) -> None:
        segment = plain("abc")

        with pytest.raises(FrozenInstanceError):
            setattr(segment, attribute_name, "other")

    def test_a_segment_without_styles_is_not_bold(self) -> None:
        assert plain("abc").is_bold is False

    def test_a_segment_with_the_highlight_style_is_bold(self) -> None:
        assert styled("abc", Style.HIGHLIGHT).is_bold is True

    @pytest.mark.parametrize(
        "other_style",
        [style for style in Style if style is not Style.HIGHLIGHT],
        ids=lambda style: style.name.lower(),
    )
    def test_a_segment_with_only_a_non_highlight_style_is_not_bold(
        self, other_style: Style
    ) -> None:
        assert styled("abc", other_style).is_bold is False

    @pytest.mark.parametrize(
        "other_style",
        [style for style in Style if style is not Style.HIGHLIGHT],
        ids=lambda style: style.name.lower(),
    )
    def test_a_segment_combining_highlight_with_another_style_is_bold(
        self, other_style: Style
    ) -> None:
        assert styled("abc", other_style, Style.HIGHLIGHT).is_bold is True


class TestParsingRealisticSentences:
    def test_a_sentence_with_highlight_and_underline_is_split_into_five_segments(
        self,
    ) -> None:
        text = "Olá **mundo** e __você__!"

        assert parse_markup(text) == [
            plain("Olá "),
            styled("mundo", Style.HIGHLIGHT),
            plain(" e "),
            styled("você", Style.UNDERLINE),
            plain("!"),
        ]

    def test_a_sentence_mixing_nested_styles_and_escaped_markers(self) -> None:
        text = r"Use \*\* for **bold and ##italic## text**"

        assert parse_markup(text) == [
            plain("Use ** for "),
            styled("bold and ", Style.HIGHLIGHT),
            styled("italic", Style.HIGHLIGHT, Style.ITALIC),
            styled(" text", Style.HIGHLIGHT),
        ]
