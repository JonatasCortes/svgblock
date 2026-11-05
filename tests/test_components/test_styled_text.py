import xml.etree.ElementTree as ET

import pytest

from svgblock.components import Column, Theme

from .shared import SVG_NAMESPACE, parse_svg_fragment, render_column

THEME = Theme.NEON.value


def find_spans(svg: str) -> list[ET.Element]:
    """Return every tspan element found in an SVG fragment."""
    return parse_svg_fragment(svg).findall(f".//{{{SVG_NAMESPACE}}}tspan")


def render_text(content: str) -> str:
    """Render a paragraph and return its SVG."""
    return render_column(Column().text(content)).svg


def only_span(content: str) -> ET.Element:
    """Render a paragraph that must produce exactly one styled span."""
    spans = find_spans(render_text(content))
    assert len(spans) == 1
    return spans[0]


class TestPlainText:
    def test_text_without_markup_produces_no_styled_spans(self) -> None:
        assert find_spans(render_text("plain words")) == []

    def test_text_without_markup_is_preserved(self) -> None:
        text = "".join(parse_svg_fragment(
            render_text("plain words")).itertext())

        assert "plain words" in text


class TestSingleStyles:
    def test_highlight_is_bold_and_uses_the_highlight_color(self) -> None:
        span = only_span("**marked**")

        assert span.attrib["fill"] == THEME["highlight"]
        assert span.attrib["font-weight"] == "700"
        assert span.text == "marked"

    def test_underline_uses_its_color_and_decoration(self) -> None:
        span = only_span("__marked__")

        assert span.attrib["fill"] == THEME["underline"]
        assert span.attrib["text-decoration"] == "underline"
        assert "font-weight" not in span.attrib

    def test_strikethrough_uses_its_color_and_decoration(self) -> None:
        span = only_span("--marked--")

        assert span.attrib["fill"] == THEME["strikethrough"]
        assert span.attrib["text-decoration"] == "line-through"
        assert "font-weight" not in span.attrib

    def test_italic_uses_its_color_and_font_style(self) -> None:
        span = only_span("##marked##")

        assert span.attrib["fill"] == THEME["italic"]
        assert span.attrib["font-style"] == "italic"
        assert "text-decoration" not in span.attrib
        assert "font-weight" not in span.attrib


class TestCombinedStyles:
    def test_underline_and_strikethrough_are_combined_in_one_decoration(self) -> None:
        span = only_span("__--marked--__")

        assert span.attrib["text-decoration"] == "underline line-through"

    def test_decoration_order_does_not_depend_on_marker_order(self) -> None:
        span = only_span("--__marked__--")

        assert span.attrib["text-decoration"] == "underline line-through"

    def test_nested_highlight_keeps_bold_weight(self) -> None:
        span = only_span("**##marked##**")

        assert span.attrib["font-weight"] == "700"
        assert span.attrib["font-style"] == "italic"

    def test_color_comes_from_the_innermost_style(self) -> None:
        span = only_span("**__marked__**")

        assert span.attrib["fill"] == THEME["underline"]

    def test_color_follows_the_innermost_style_when_order_is_reversed(self) -> None:
        span = only_span("__**marked**__")

        assert span.attrib["fill"] == THEME["highlight"]


class TestMixedContent:
    def test_plain_and_styled_parts_keep_their_order(self) -> None:
        svg = render_text("before **middle** after")

        text = "".join(parse_svg_fragment(svg).itertext())

        assert text.index("before") < text.index(
            "middle") < text.index("after")

    def test_only_the_marked_part_becomes_a_span(self) -> None:
        spans = find_spans(render_text("before **middle** after"))

        assert [span.text for span in spans] == ["middle"]

    def test_several_styled_parts_become_several_spans(self) -> None:
        spans = find_spans(render_text("**one** and __two__ and --three--"))

        assert [span.text for span in spans] == ["one", "two", "three"]

    def test_special_characters_inside_styled_text_are_escaped(self) -> None:
        span = only_span("**Tom & Jerry <3**")

        assert span.text == "Tom & Jerry <3"

    def test_escaped_marker_is_rendered_literally_without_a_span(self) -> None:
        svg = render_text("\\**literal\\**")

        assert find_spans(svg) == []
        assert "**literal**" in "".join(parse_svg_fragment(svg).itertext())


class TestHeadingsIgnoreMarkup:
    @pytest.mark.parametrize("method", ["title", "subsection"])
    @pytest.mark.parametrize("content", ["**marked**", "__marked__", "--marked--", "##marked##"])
    def test_marker_characters_are_rendered_literally(
        self, method: str, content: str
    ) -> None:
        svg = render_column(getattr(Column(), method)(content)).svg

        assert content in "".join(parse_svg_fragment(svg).itertext())

    @pytest.mark.parametrize("method", ["title", "subsection"])
    def test_markup_does_not_produce_styled_spans(self, method: str) -> None:
        svg = render_column(getattr(Column(), method)("**marked**")).svg

        assert find_spans(svg) == []

    @pytest.mark.parametrize("method", ["title", "subsection"])
    def test_unclosed_marker_does_not_raise(self, method: str) -> None:
        svg = render_column(getattr(Column(), method)("**open")).svg

        assert "**open" in "".join(parse_svg_fragment(svg).itertext())


class TestInvalidMarkup:
    @pytest.mark.parametrize("content", ["**open", "__open", "--open", "##open"])
    def test_unclosed_marker_raises_value_error(self, content: str) -> None:
        with pytest.raises(ValueError, match="Unclosed marker"):
            render_text(content)
