"""Space an animation needs around an element: extent, scale, blur and margins."""

from typing import Literal

import pytest

from svgblock import (
    BaseAnimation,
    DropIn,
    EaseInBack,
    EaseOutBack,
    FadeIn,
    Float,
    FocusIn,
    Jelly,
    Pulse,
    RiseIn,
    RiseOut,
    Rotate,
    Shake,
    SlideIn,
    Sway,
)
from tests.test_animations.shared import ENTRANCES, EVERY_ANIMATION, EXITS, each

SQUARE_SWEEP = 50 * (2 ** 0.5) - 50


@each(EVERY_ANIMATION)
def test_max_scale_is_never_below_the_natural_size(animation: BaseAnimation) -> None:
    """Reserved space must never be smaller than the element itself."""
    assert animation.max_scale >= 1


@each(EVERY_ANIMATION)
def test_max_blur_is_never_negative(animation: BaseAnimation) -> None:
    """A negative blur radius is meaningless and would break the filter."""
    assert animation.max_blur >= 0


@each(EVERY_ANIMATION)
def test_margins_are_never_negative(animation: BaseAnimation) -> None:
    """Margins only ever add room; they can't shrink the element's box."""
    assert all(side >= 0 for side in animation.margins(120.0, 40.0))


@each(EVERY_ANIMATION)
def test_sweep_is_never_negative(animation: BaseAnimation) -> None:
    """A rotation sweep only ever adds room around the element."""
    assert all(side >= 0 for side in animation.sweep(120.0, 40.0))


@each({**ENTRANCES, **EXITS})
def test_easings_without_overshoot_cause_no_overflow(animation: BaseAnimation) -> None:
    """Overflow exists only to cover easings that go past their keyframes."""
    assert animation.overflow == (0, 0, 0, 0)


def test_extent_reports_the_range_an_attribute_reaches() -> None:
    """``extent`` is the min/max an attribute takes over the whole animation."""
    assert FadeIn().extent("opacity") == (0, 1)
    assert Float(amount=8.0).extent("y") == pytest.approx((-8.0, 8.0))


def test_extent_includes_the_overshoot_of_the_easing() -> None:
    """An overshooting easing carries the element past its last keyframe."""
    low, high = RiseIn(distance=40, easing=EaseOutBack()).extent("y")

    assert low < 0
    assert high == pytest.approx(40)


@pytest.mark.parametrize(
    ("animation", "side"),
    [
        pytest.param(RiseIn(easing=EaseOutBack()),
                     1, id="rise-overshoots-above"),
        pytest.param(DropIn(easing=EaseOutBack()),
                     3, id="drop-overshoots-below"),
        pytest.param(SlideIn(direction="right", easing=EaseOutBack()), 2,
                     id="slide-right-overshoots-to-the-right"),
        pytest.param(SlideIn(direction="left", easing=EaseOutBack()), 0,
                     id="slide-left-overshoots-to-the-left"),
        pytest.param(RiseOut(easing=EaseInBack()), 3,
                     id="exit-undershoots-opposite-way"),
    ],
)
def test_overshooting_easing_reserves_room_on_the_side_it_overshoots(
        animation: BaseAnimation, side: int) -> None:
    """Margins are ordered left, top, right, bottom; overshoot needs room there."""
    assert animation.margins(100.0, 50.0)[side] > 0


def test_larger_overshoot_reserves_more_room() -> None:
    """Margin must grow with the distance the element overshoots."""
    near = RiseIn(distance=20, easing=EaseOutBack()).margins(100.0, 50.0)[1]
    far = RiseIn(distance=80, easing=EaseOutBack()).margins(100.0, 50.0)[1]

    assert far == pytest.approx(4 * near)


@pytest.mark.parametrize(
    ("animation", "expected"),
    [
        pytest.param(RiseIn(distance=40), (0.0, 0.0, 0.0, 40.0),
                     id="rise-starts-below"),
        pytest.param(DropIn(distance=40), (0.0, 40.0, 0.0, 0.0),
                     id="drop-starts-above"),
        pytest.param(SlideIn(distance=40, direction="right"), (40.0, 0.0, 0.0, 0.0),
                     id="slide-right-starts-on-the-left"),
        pytest.param(SlideIn(distance=40, direction="left"), (0.0, 0.0, 40.0, 0.0),
                     id="slide-left-starts-on-the-right"),
        pytest.param(Float(amount=8.0), (0.0, 8.0, 0.0, 8.0),
                     id="float-both-ways"),
    ],
)
def test_travel_is_the_distance_the_element_strays_on_each_side(
        animation: BaseAnimation, expected: tuple[float, float, float, float]) -> None:
    """Travel is ordered left, top, right, bottom and measured from the rest box."""
    assert animation.travel == pytest.approx(expected)


def test_float_reserves_room_equal_to_its_vertical_excursion() -> None:
    """A bobbing element needs ``amount`` pixels above and below, nothing sideways."""
    assert Float(amount=12.0).margins(
        100.0, 50.0) == pytest.approx((0.0, 12.0, 0.0, 12.0))


def test_shake_reserves_room_only_horizontally_and_covering_its_whole_range() -> None:
    """Margins must exactly cover the horizontal range the shake reaches."""
    shake = Shake(amount=12.0)
    low, high = shake.extent("x")
    left, top, right, bottom = shake.margins(100.0, 50.0)

    assert (left, right) == pytest.approx((-low, high))
    assert (top, bottom) == (0, 0)


def test_pulse_needs_no_translation_margin_because_it_reports_max_scale() -> None:
    """Growth is reported through ``max_scale``, not through margins."""
    assert Pulse().margins(100.0, 50.0) == (0, 0, 0, 0)


@pytest.mark.parametrize(
    ("animation", "expected"),
    [
        pytest.param(Pulse(amount=0.06), 1.06, id="pulse"),
        pytest.param(Pulse(amount=0.5), 1.5, id="strong-pulse"),
        pytest.param(Jelly(amount=0.2), 1.2, id="jelly-stretches-one-axis"),
    ],
)
def test_max_scale_reports_the_largest_size_reached(
        animation: BaseAnimation, expected: float) -> None:
    """``max_scale`` is what the element is multiplied by at its largest."""
    assert animation.max_scale == pytest.approx(expected)


def test_max_scale_ignores_animations_that_only_shrink() -> None:
    """Starting small is not a reason to reserve extra room."""
    assert FadeIn().max_scale == 1


@pytest.mark.parametrize("blur", [2.0, 8.0, 20.0])
def test_max_blur_reports_the_strongest_blur_reached(blur: float) -> None:
    """``max_blur`` lets the renderer size its filter region."""
    assert FocusIn(blur=blur).max_blur == blur


def test_max_blur_is_zero_without_any_blur() -> None:
    """Animations without blur must not ask for a filter region."""
    assert FadeIn().max_blur == 0


def test_blur_margin_is_even_on_every_side_and_grows_with_the_blur() -> None:
    """Blur spreads in all directions, proportionally to its radius."""
    soft = FocusIn(blur=4.0).blur_margin
    strong = FocusIn(blur=8.0).blur_margin

    assert len(set(soft)) == 1
    assert soft[0] > 0
    assert strong == pytest.approx(tuple(2 * side for side in soft))


def test_blur_margin_is_zero_without_blur() -> None:
    """No blur means no extra room."""
    assert FadeIn().blur_margin == (0, 0, 0, 0)


@pytest.mark.parametrize("pivot", ["top", "center", "bottom"])
def test_sway_origins_hold_the_single_pivot_it_rotates_around(
        pivot: Literal["top", "center", "bottom"]) -> None:
    """Rotation margins depend on the pivot, so exactly one must be reported."""
    assert len(Sway(pivot=pivot).origins) == 1


def test_animations_without_a_pivot_rotate_around_the_centre() -> None:
    """The default transform origin is the middle of the element."""
    assert FadeIn().origins == {(0.5, 0.5)}


@pytest.mark.parametrize("angle", [90.0, -90.0, 360.0, -360.0])
def test_square_rotated_around_its_centre_sweeps_its_diagonal_on_every_side(
        angle: float) -> None:
    """At 45 degrees a square's bounding box reaches half its diagonal."""
    assert Rotate(angle=angle).sweep(100.0, 100.0) == pytest.approx(
        (SQUARE_SWEEP,) * 4, abs=1e-3)


def test_sweep_of_a_wide_box_is_larger_vertically_than_horizontally() -> None:
    """Turning a 200x100 box a quarter turn pokes out far more above and below."""
    left, top, right, bottom = Rotate(angle=90.0).sweep(200.0, 100.0)

    assert (left, right) == pytest.approx((11.80, 11.80), abs=0.05)
    assert (top, bottom) == pytest.approx((61.80, 61.80), abs=0.05)


def test_sweep_beyond_a_full_turn_adds_no_room() -> None:
    """Geometry repeats every 360 degrees, so extra turns need no extra space."""
    assert Rotate(angle=720.0).sweep(100.0, 60.0) == pytest.approx(
        Rotate(angle=360.0).sweep(100.0, 60.0), abs=1e-3)


@pytest.mark.parametrize("animation", [FadeIn(), RiseIn(), Float(), Pulse(), Shake()],
                         ids=["fade", "rise", "float", "pulse", "shake"])
def test_sweep_is_zero_when_the_element_never_rotates(animation: BaseAnimation) -> None:
    """Without rotation no sweep room should be reserved."""
    assert animation.sweep(100.0, 50.0) == (0, 0, 0, 0)


def test_larger_tilt_sweeps_at_least_as_much_on_every_side() -> None:
    """Margins can only grow when the tilt angle grows."""
    small = Sway(angle=3.0).sweep(100.0, 50.0)
    large = Sway(angle=12.0).sweep(100.0, 50.0)

    assert all(big >= little for big, little in zip(large, small))
    assert sum(large) > sum(small)


def test_sway_margins_mirror_between_top_and_bottom_pivots() -> None:
    """Hanging from the top or from the bottom is the same shape flipped."""
    top_left, top_top, top_right, top_bottom = Sway(
        pivot="top").sweep(100.0, 50.0)
    bottom_left, bottom_top, bottom_right, bottom_bottom = Sway(
        pivot="bottom").sweep(100.0, 50.0)

    assert (top_left, top_top, top_right, top_bottom) == pytest.approx(
        (bottom_left, bottom_bottom, bottom_right, bottom_top))


def test_sway_swings_symmetrically_left_and_right_around_a_centred_pivot() -> None:
    """A centred pivot with a symmetric swing needs equal room on both sides."""
    left, _, right, _ = Sway(pivot="top").sweep(100.0, 50.0)

    assert left == pytest.approx(right)


def test_rotating_repeatable_reserves_the_sweep_in_its_margins() -> None:
    """Loops that rotate must include their sweep in the reserved margins."""
    rotate = Rotate(angle=90.0)

    assert rotate.margins(100.0, 100.0) == pytest.approx(
        rotate.sweep(100.0, 100.0))
