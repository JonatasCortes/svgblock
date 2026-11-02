"""Invariants that every non-sequence animation must satisfy."""

import re
from dataclasses import FrozenInstanceError, replace

import pytest

from svgblock import (
    BaseAnimation,
    EaseIn,
    EaseOut,
    FadeIn,
    FadeOut,
    Pulse,
    RiseIn,
)
from tests.test_animations.shared import (
    ENTRANCES,
    EVERY_ANIMATION,
    EXITS,
    HOLDS,
    each,
)


@each(EVERY_ANIMATION)
def test_keyframes_start_at_zero_and_end_at_one(animation: BaseAnimation) -> None:
    """Keyframes must cover the whole timeline, or the CSS leaves gaps."""
    frames = animation.keyframes()

    assert frames[0].at == 0
    assert frames[-1].at == 1


@each(EVERY_ANIMATION)
def test_keyframe_times_stay_in_range_and_never_go_backwards(
        animation: BaseAnimation) -> None:
    """Out-of-order keyframes would be silently reordered by browsers."""
    times = [frame.at for frame in animation.keyframes()]

    assert times == sorted(times)
    assert all(0 <= at <= 1 for at in times)


@each(EVERY_ANIMATION)
def test_layers_of_a_simple_animation_contain_exactly_one_layer(
        animation: BaseAnimation) -> None:
    """Only sequences with an infinite tail may need more than one layer."""
    assert len(animation.layers()) == 1


@each(EVERY_ANIMATION)
def test_layer_is_named_after_the_animation_css_name(
        animation: BaseAnimation) -> None:
    """The generated ``@keyframes`` must be reachable from the CSS selector."""
    assert animation.layers()[0].name == animation.css_name


@each(EVERY_ANIMATION)
def test_layer_timing_matches_the_animation_timing(
        animation: BaseAnimation) -> None:
    """A layer must play for as long, and as often, as its animation says."""
    layer = animation.layers()[0]

    assert layer.duration == animation.duration
    assert layer.iterations == animation.iterations
    assert layer.delay == 0


@each(EVERY_ANIMATION)
def test_layer_keyframes_carry_the_animation_times_and_poses(
        animation: BaseAnimation) -> None:
    """The layer must not drop, reorder or alter any keyframe."""
    layer_frames = [(frame.at, frame.pose)
                    for frame in animation.layers()[0].keyframes]
    own_frames = [(frame.at, frame.pose) for frame in animation.keyframes()]

    assert layer_frames == own_frames


@each(EVERY_ANIMATION)
def test_segment_carries_the_animation_duration_and_keyframes(
        animation: BaseAnimation) -> None:
    """A segment is the building block sequences are compiled from."""
    segment = animation.segment()

    assert segment.duration == animation.duration
    assert len(segment.keyframes) == len(animation.keyframes())


@each({**ENTRANCES, **EXITS, **HOLDS})
def test_non_looping_animation_plays_exactly_once(
        animation: BaseAnimation) -> None:
    """Entrances, exits and holds must never repeat on their own."""
    assert animation.iterations == 1
    assert not animation.is_infinite


@each({**ENTRANCES, **EXITS, **HOLDS})
def test_expand_of_a_non_looping_animation_is_a_single_segment(
        animation: BaseAnimation) -> None:
    """Expanding is how sequences chain steps; one play means one segment."""
    expansion = animation.expand()

    assert expansion.cycle is None
    assert len(expansion.head) == 1
    assert expansion.playing_time == animation.duration


@each(EVERY_ANIMATION)
def test_css_name_uses_class_name_prefix_and_eight_hex_digit_suffix(
        animation: BaseAnimation) -> None:
    """CSS class names must be valid identifiers and readable in the SVG."""
    prefix = re.escape(type(animation).__name__.lower())

    assert re.fullmatch(rf"{prefix}-[0-9a-f]{{8}}", animation.css_name)


@each(EVERY_ANIMATION)
def test_css_name_is_identical_for_equal_instances(
        animation: BaseAnimation) -> None:
    """Regenerating an SVG must not rename its CSS classes."""
    assert replace(animation).css_name == animation.css_name


def test_css_name_does_not_depend_on_easing_object_identity() -> None:
    """Equal easings built separately must yield the same name (reproducible SVGs)."""
    first = FadeIn(easing=EaseOut())
    second = FadeIn(easing=EaseOut())

    assert first.css_name == second.css_name


@pytest.mark.parametrize(
    ("first", "second"),
    [
        pytest.param(FadeIn(duration=1.0), FadeIn(
            duration=2.0), id="duration"),
        pytest.param(FadeIn(duration=1.0), FadeOut(duration=1.0), id="class"),
        pytest.param(RiseIn(distance=10), RiseIn(
            distance=20), id="own-parameter"),
        pytest.param(Pulse(loop_limit=1), Pulse(
            loop_limit=2), id="loop-limit"),
        pytest.param(FadeIn(easing=EaseOut()), FadeIn(
            easing=EaseIn()), id="easing"),
    ],
)
def test_css_name_differs_when_any_parameter_differs(
        first: BaseAnimation, second: BaseAnimation) -> None:
    """Different animations sharing one name would overwrite each other's CSS."""
    assert first.css_name != second.css_name


@each(EVERY_ANIMATION)
def test_animation_cannot_be_mutated_after_creation(
        animation: BaseAnimation) -> None:
    """The CSS name is derived from the parameters, so they must stay fixed."""
    with pytest.raises(FrozenInstanceError):
        setattr(animation, "duration", 99.0)
