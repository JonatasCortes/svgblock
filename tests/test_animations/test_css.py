"""Stylesheets produced by ``build_animation_css``."""

from typing import Literal

import pytest

from svgblock import (
    BaseAnimation,
    FadeIn,
    FlipIn,
    FocusIn,
    GlitchIn,
    Pulse,
    RiseIn,
    Rotate,
    Sequence,
    Show,
    SlideIn,
    UnfoldIn,
    build_animation_css,
)
from tests.test_animations.shared import (
    EVERY_ANIMATION,
    animation_value,
    each,
    parse_css_keyframes,
)

SEQUENCES: dict[str, BaseAnimation] = {
    "finite-sequence": Sequence(FadeIn(duration=1.0), Show(duration=2.0)),
    "repeated-sequence": Sequence(FadeIn(), Show(duration=1.0), loop_limit=2),
    "intro-then-endless-loop": Sequence(FadeIn(), Pulse(loop_limit=None)),
    "endless-loop-only": Sequence(Pulse(loop_limit=None)),
}

EVERY_STYLESHEET_SOURCE: dict[str, BaseAnimation] = {
    **EVERY_ANIMATION, **SEQUENCES}


@each(EVERY_STYLESHEET_SOURCE)
def test_rule_selector_is_the_animation_css_name(animation: BaseAnimation) -> None:
    """Users attach the animation to an element through this class name."""
    assert f".{animation.css_name} {{" in build_animation_css(animation)


@each(EVERY_STYLESHEET_SOURCE)
def test_one_keyframes_rule_is_emitted_per_layer(animation: BaseAnimation) -> None:
    """Each layer needs its own ``@keyframes``, named after the layer."""
    rules = parse_css_keyframes(build_animation_css(animation))

    assert set(rules) == {layer.name for layer in animation.layers()}


@each(EVERY_STYLESHEET_SOURCE)
def test_animation_shorthand_references_every_keyframes_rule(
        animation: BaseAnimation) -> None:
    """A rule that the shorthand never mentions would never play."""
    value = animation_value(build_animation_css(animation))

    assert all(layer.name in value for layer in animation.layers())


@each(EVERY_STYLESHEET_SOURCE)
def test_keyframes_start_at_zero_percent_and_end_at_one_hundred(
        animation: BaseAnimation) -> None:
    """Every rule must define both ends of its timeline."""
    for steps in parse_css_keyframes(build_animation_css(animation)).values():
        assert steps[0].percent == 0
        assert steps[-1].percent == pytest.approx(100)


@each(EVERY_STYLESHEET_SOURCE)
def test_keyframe_percentages_never_decrease(animation: BaseAnimation) -> None:
    """Out-of-order steps would be reordered by browsers and change the motion."""
    for steps in parse_css_keyframes(build_animation_css(animation)).values():
        percents = [step.percent for step in steps]
        assert percents == sorted(percents)


@each(EVERY_STYLESHEET_SOURCE)
def test_reduced_motion_preference_disables_the_animation(
        animation: BaseAnimation) -> None:
    """Respecting ``prefers-reduced-motion`` is an accessibility requirement."""
    css = build_animation_css(animation)

    assert "@media (prefers-reduced-motion: reduce)" in css
    assert f".{animation.css_name} {{ animation: none; }}" in css


@each(EVERY_STYLESHEET_SOURCE)
def test_transforms_are_relative_to_the_elements_own_box(
        animation: BaseAnimation) -> None:
    """Without ``fill-box`` SVG transforms pivot around the canvas origin."""
    assert "transform-box: fill-box;" in build_animation_css(animation)


@each(EVERY_STYLESHEET_SOURCE)
def test_output_is_deterministic(animation: BaseAnimation) -> None:
    """Regenerating a profile must not produce a diff."""
    assert build_animation_css(animation) == build_animation_css(animation)


def test_empty_sequence_produces_no_css_at_all() -> None:
    """There is nothing to animate, so nothing should be emitted."""
    assert build_animation_css(Sequence()) == ""


def test_shorthand_reports_duration_iterations_and_fill() -> None:
    """The shorthand ends with delay, iteration count and fill mode."""
    tokens = animation_value(build_animation_css(FadeIn(duration=2.0))).split()

    assert tokens[1] == "2s"
    assert tokens[-3:] == ["0s", "1", "both"]


def test_shorthand_counts_every_play_of_a_finite_loop() -> None:
    """``loop_limit=2`` must ask the browser for three iterations."""
    tokens = animation_value(build_animation_css(Pulse(loop_limit=2))).split()

    assert tokens[-2] == "3"


def test_shorthand_requests_infinite_iterations_for_an_endless_loop() -> None:
    """``loop_limit=None`` must map to CSS ``infinite``."""
    tokens = animation_value(build_animation_css(
        Pulse(loop_limit=None))).split()

    assert tokens[-2] == "infinite"


def test_intro_and_loop_layers_are_comma_separated_in_one_shorthand() -> None:
    """Both layers must run from the same rule, the loop starting after a delay."""
    sequence = Sequence(FadeIn(duration=1.0), Pulse(loop_limit=None))
    layers = animation_value(build_animation_css(sequence)).split(", ")

    assert len(layers) == 2
    assert layers[1].startswith(f"{sequence.css_name}-loop ")
    assert " 1s infinite " in layers[1]


def test_rise_in_css_moves_the_element_from_below_to_rest() -> None:
    """Positive y is downwards in SVG, so a rising element starts below."""
    animation = RiseIn(distance=40)
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert "translate(0px, 40px)" in steps[0].declarations
    assert "translate(0px, 0px)" in steps[-1].declarations


def test_slide_in_from_the_left_css_starts_with_a_negative_x_offset() -> None:
    """A rightward slide must start left of its resting place."""
    animation = SlideIn(distance=30, direction="right")
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert "translate(-30px, 0px)" in steps[0].declarations


def test_flip_in_css_mirrors_the_element_with_a_negative_scale() -> None:
    """Mirroring is written as a negative scale on the flipped axis."""
    animation = FlipIn(axis="horizontal")
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert "scale(-1, 1)" in steps[0].declarations


def test_rotation_is_written_in_degrees() -> None:
    """The rotation unit must match the angle the user supplied."""
    animation = Rotate(angle=90.0)
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert "rotate(90deg)" in steps[-1].declarations


def test_opacity_is_written_in_every_keyframe() -> None:
    """Omitting opacity would let a keyframe inherit the wrong value."""
    animation = FadeIn()
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert steps[0].declarations.startswith("opacity: 0;")
    assert steps[-1].declarations.startswith("opacity: 1;")


def test_blur_filter_is_omitted_when_the_animation_never_blurs() -> None:
    """A needless filter forces costly offscreen rendering."""
    assert "filter" not in build_animation_css(FadeIn())


def test_blur_filter_is_written_when_the_animation_blurs() -> None:
    """Blur must reach the CSS or the focus effect would silently vanish."""
    animation = FocusIn(blur=6.0)
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert "filter: blur(6px);" in steps[0].declarations
    assert "filter: blur(0px);" in steps[-1].declarations


def test_blur_is_written_in_every_keyframe_once_any_keyframe_blurs() -> None:
    """A keyframe missing the property would not interpolate back to sharp."""
    sequence = Sequence(FocusIn(), Show(duration=1.0))
    steps = parse_css_keyframes(build_animation_css(sequence))[
        sequence.css_name]

    assert all("filter: blur(" in step.declarations for step in steps)


def test_transform_origin_is_not_repeated_in_keyframes_for_centred_animations() -> None:
    """Only the rule's own centred origin is needed when nothing pivots elsewhere."""
    assert build_animation_css(FadeIn()).count("transform-origin") == 1


@pytest.mark.parametrize(
    ("edge", "origin"),
    [("top", "50% 0%"), ("bottom", "50% 100%"),
     ("left", "0% 50%"), ("right", "100% 50%")],
)
def test_unfold_css_pivots_around_the_requested_edge(
        edge: Literal["top", "bottom", "left", "right"], origin: str) -> None:
    """The chosen edge is written as a percentage transform origin."""
    animation = UnfoldIn(edge=edge)
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert f"transform-origin: {origin};" in steps[0].declarations


def test_transform_origin_is_written_in_every_keyframe_once_any_keyframe_pivots() -> None:
    """Mixing pivots requires each keyframe to state its own."""
    sequence = Sequence(UnfoldIn(), FadeIn())
    steps = parse_css_keyframes(build_animation_css(sequence))[
        sequence.css_name]

    assert all("transform-origin:" in step.declarations for step in steps)


def test_animation_wide_easing_is_not_repeated_on_keyframes_without_their_own() -> None:
    """Plain animations ease through the shorthand, not through each keyframe."""
    assert "animation-timing-function" not in build_animation_css(FadeIn())


def test_keyframe_level_easing_is_written_except_on_the_last_keyframe() -> None:
    """Steps with their own easing need it in the CSS; the final step needs none."""
    animation = GlitchIn()
    steps = parse_css_keyframes(build_animation_css(animation))[
        animation.css_name]

    assert all(
        "animation-timing-function" in step.declarations for step in steps[:-1])
    assert "animation-timing-function" not in steps[-1].declarations
