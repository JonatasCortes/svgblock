import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import pytest

from svgblock import Block
from svgblock.components import Pulse, Show, build_animation_css

from .shared import SVG_NAMESPACE, make_column_with_dividers, render_column

Margins = tuple[float, float, float, float]

PULSE_AMOUNT = 0.1
GROWTH = 1 + PULSE_AMOUNT
DEFAULT_WIDTH = 800
DEFAULT_PADDING = 24
LAYOUT_PASS_LIMIT = 8
STABLE_MARGINS: Margins = (20.0, 10.0, 30.0, 40.0)


@dataclass(frozen=True, kw_only=True)
class FixedMarginsPulse(Pulse):
    """Pulse that reports constant margins and counts how often they are asked."""

    fixed_margins: Margins = (0.0, 0.0, 0.0, 0.0)
    calls: list[int] = field(default_factory=list,  # type: ignore
                             repr=False, compare=False)

    def margins(self, width: float, height: float) -> Margins:
        self.calls.append(1)
        return self.fixed_margins


@dataclass(frozen=True, kw_only=True)
class GrowingMarginsPulse(Pulse):
    """Pulse whose left margin grows on every call, so layout never converges."""

    calls: list[int] = field(default_factory=list,  # type: ignore
                             repr=False, compare=False)

    def margins(self, width: float, height: float) -> Margins:
        self.calls.append(1)
        return (10.0 * len(self.calls), 0.0, 0.0, 0.0)


def read_height(svg: str) -> float:
    """Return the height attribute of the root svg element."""
    return float(ET.fromstring(svg).attrib["height"])


def read_translation(svg: str) -> tuple[float, float]:
    """Return the translation applied to the outermost group."""
    group = ET.fromstring(svg).find(f"{{{SVG_NAMESPACE}}}g")
    assert group is not None
    match = re.fullmatch(
        r"translate\(([-\d.]+) ([-\d.]+)\)", group.attrib["transform"])
    assert match is not None
    return float(match.group(1)), float(match.group(2))


def divider_block_height() -> float:
    """Return the frame height of a block holding a single divider."""
    return render_column(make_column_with_dividers(1)).height + 2 * DEFAULT_PADDING


class TestAnimationMarkup:
    def test_block_without_animation_has_no_style_element(self) -> None:
        assert "<style" not in Block().divider().render()

    def test_block_with_animation_embeds_its_css(self) -> None:
        animation = Show(duration=1)

        svg = Block(animation=animation).divider().render()

        assert f"<style>{build_animation_css(animation)}</style>" in svg

    def test_animated_group_carries_the_animation_css_name(self) -> None:
        animation = Show(duration=1)

        svg = Block(animation=animation).divider().render()

        assert f'<g class="{animation.css_name}">' in svg

    def test_animated_document_is_well_formed_xml(self) -> None:
        svg = Block(animation=Pulse()).title("Heading").divider().render()

        assert ET.fromstring(svg).tag == f"{{{SVG_NAMESPACE}}}svg"

    def test_animation_works_with_a_hidden_frame(self) -> None:
        svg = Block(animation=Show(duration=1),
                    hide_frame=True).divider().render()

        assert read_height(svg) == pytest.approx(
            render_column(make_column_with_dividers(1)).height
        )


class TestAnimationWithoutMargins:
    def test_animation_without_growth_or_margins_keeps_the_static_height(self) -> None:
        animated = Block(animation=Show(duration=1)).divider().render()
        static = Block().divider().render()

        assert read_height(animated) == pytest.approx(read_height(static))

    def test_width_attribute_is_not_changed_by_a_growing_animation(self) -> None:
        svg = Block(animation=Pulse(amount=PULSE_AMOUNT)).divider().render()

        assert float(ET.fromstring(svg).attrib["width"]) == DEFAULT_WIDTH

    def test_growing_animation_scales_the_height_by_the_growth(self) -> None:
        svg = Block(animation=FixedMarginsPulse(
            amount=PULSE_AMOUNT)).divider().render()

        assert read_height(svg) == pytest.approx(
            divider_block_height() * GROWTH, abs=1e-3
        )

    def test_growing_animation_centers_the_block_horizontally(self) -> None:
        svg = Block(animation=FixedMarginsPulse(
            amount=PULSE_AMOUNT)).divider().render()

        block_width = DEFAULT_WIDTH / GROWTH
        expected_x = (DEFAULT_WIDTH - block_width) / 2

        assert read_translation(svg)[0] == pytest.approx(expected_x, abs=1e-3)


class TestAnimationMargins:
    def _render(self) -> tuple[str, FixedMarginsPulse]:
        animation = FixedMarginsPulse(
            amount=PULSE_AMOUNT, fixed_margins=STABLE_MARGINS)
        return Block(animation=animation).divider().render(), animation

    def test_vertical_margins_are_added_to_the_height(self) -> None:
        svg, _ = self._render()
        _, top, _, bottom = STABLE_MARGINS

        assert read_height(svg) == pytest.approx(
            divider_block_height() * GROWTH + top + bottom, abs=1e-3
        )

    def test_block_is_translated_by_the_margins_and_growth_offset(self) -> None:
        svg, _ = self._render()
        left, top, right, _ = STABLE_MARGINS
        block_width = (DEFAULT_WIDTH - left - right) / GROWTH
        block_height = divider_block_height()

        x, y = read_translation(svg)

        assert x == pytest.approx(
            left + (block_width * GROWTH - block_width) / 2, abs=1e-3
        )
        assert y == pytest.approx(
            top + (block_height * GROWTH - block_height) / 2, abs=1e-3
        )

    def test_layout_stops_as_soon_as_the_margins_are_stable(self) -> None:
        _, animation = self._render()

        assert len(animation.calls) == 2

    def test_layout_gives_up_after_the_pass_limit_when_margins_keep_growing(
        self,
    ) -> None:
        animation = GrowingMarginsPulse(amount=PULSE_AMOUNT)

        svg = Block(animation=animation).divider().render()

        assert len(animation.calls) == LAYOUT_PASS_LIMIT
        assert ET.fromstring(svg).tag == f"{{{SVG_NAMESPACE}}}svg"

    def test_final_layout_uses_the_margins_reached_after_the_pass_limit(self) -> None:
        animation = GrowingMarginsPulse(amount=PULSE_AMOUNT)

        svg = Block(animation=animation).divider().render()

        final_left = 10.0 * LAYOUT_PASS_LIMIT
        block_width = (DEFAULT_WIDTH - final_left) / GROWTH
        expected_x = final_left + (block_width * GROWTH - block_width) / 2
        assert read_translation(svg)[0] == pytest.approx(expected_x, abs=1e-3)


class TestAnimationSideMargins:
    def test_side_margins_wider_than_the_block_raise_value_error(self) -> None:
        animation = FixedMarginsPulse(
            amount=PULSE_AMOUNT, fixed_margins=(500.0, 0.0, 400.0, 0.0)
        )

        with pytest.raises(ValueError, match="Animation needs 900px of side margin"):
            Block(animation=animation).divider().render()

    def test_error_message_states_the_block_width(self) -> None:
        animation = FixedMarginsPulse(
            amount=PULSE_AMOUNT, fixed_margins=(500.0, 0.0, 400.0, 0.0)
        )

        with pytest.raises(ValueError, match="width 800"):
            Block(animation=animation).divider().render()

    def test_side_margins_equal_to_the_width_raise_value_error(self) -> None:
        animation = FixedMarginsPulse(
            amount=PULSE_AMOUNT, fixed_margins=(400.0, 0.0, 400.0, 0.0)
        )

        with pytest.raises(ValueError, match="Animation needs"):
            Block(animation=animation).divider().render()
