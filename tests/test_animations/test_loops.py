"""Behaviour of looping animations and of the ``loop_limit`` contract."""

from typing import Literal
import pytest
from svgblock import BaseAnimation, Drift, Float, Jelly, Pulse, Rotate, Shake, Sway
from tests.test_animations.shared import (
    LOOP_FACTORIES,
    SEAMLESS_LOOPS,
    AnimationFactory,
    each,
    each_factory,
)


@each_factory(LOOP_FACTORIES)
def test_loop_plays_once_by_default(factory: AnimationFactory) -> None:
    """Looping animations are opt-in: without ``loop_limit`` they play once."""
    animation = factory()

    assert animation.iterations == 1
    assert not animation.is_infinite


@pytest.mark.parametrize("loop_limit", [0, 1, 3, 1000])
@each_factory(LOOP_FACTORIES)
def test_loop_limit_counts_repetitions_after_the_first_play(
        factory: AnimationFactory, loop_limit: int) -> None:
    """``loop_limit=n`` means n repetitions, so n + 1 plays in total."""
    assert factory(loop_limit=loop_limit).iterations == loop_limit + 1


@each_factory(LOOP_FACTORIES)
def test_loop_limit_none_repeats_forever(factory: AnimationFactory) -> None:
    """``None`` is the documented way to ask for an endless loop."""
    animation = factory(loop_limit=None)

    assert animation.iterations is None
    assert animation.is_infinite


@pytest.mark.parametrize(
    ("loop_limit", "message"),
    [(-1, "loop_limit must be 0 or more"),
     (1001, "loop_limit must be at most 1000")],
)
@each_factory(LOOP_FACTORIES)
def test_loop_limit_outside_the_supported_range_is_rejected(
        factory: AnimationFactory, loop_limit: int, message: str) -> None:
    """Out-of-range limits must fail early with a message naming the limit."""
    with pytest.raises(ValueError, match=message):
        factory(loop_limit=loop_limit)


@each_factory(LOOP_FACTORIES)
def test_expand_repeats_the_cycle_once_per_play(factory: AnimationFactory) -> None:
    """Expanding a finite loop must unroll every play into its own segment."""
    animation = factory(loop_limit=2)
    expansion = animation.expand()

    assert expansion.cycle is None
    assert len(expansion.head) == 3
    assert expansion.playing_time == pytest.approx(3 * animation.duration)


@each_factory(LOOP_FACTORIES)
def test_expand_of_an_endless_loop_is_one_repeating_cycle(
        factory: AnimationFactory) -> None:
    """An endless loop has no head, only a cycle lasting one play."""
    animation = factory(loop_limit=None)
    expansion = animation.expand()

    assert expansion.head == ()
    assert expansion.cycle is not None
    assert [segment.duration for segment in expansion.cycle] == [
        animation.duration]


@each(SEAMLESS_LOOPS)
def test_loop_ends_in_the_pose_it_starts_from(animation: BaseAnimation) -> None:
    """Otherwise every repetition would visibly jump when it restarts."""
    frames = animation.keyframes()

    assert frames[-1].pose == frames[0].pose


@pytest.mark.parametrize("angle", [90.0, -45.0, 720.0])
def test_rotate_ends_turned_by_exactly_the_requested_angle(angle: float) -> None:
    """``angle`` is the total rotation, signed, and may exceed a full turn."""
    frames = Rotate(angle=angle).keyframes()

    assert frames[0].pose.rotate == 0
    assert frames[-1].pose.rotate == angle


def test_full_turn_rotation_ends_visually_where_it_started() -> None:
    """The default rotation must loop seamlessly, being a whole number of turns."""
    assert Rotate().keyframes()[-1].pose.rotate % 360 == 0


@pytest.mark.parametrize("amount", [0.06, 0.2])
def test_pulse_swells_by_the_requested_fraction_then_returns(amount: float) -> None:
    """``amount`` is the relative growth at the pulse's peak."""
    scales = [frame.pose.scale for frame in Pulse(amount=amount).keyframes()]

    assert max(scales) == pytest.approx(1 + amount)
    assert min(scales) == 1


@pytest.mark.parametrize("amount", [4.0, 8.0, 25.0])
def test_float_bobs_equally_above_and_below_its_resting_position(
        amount: float) -> None:
    """``amount`` is the vertical excursion in pixels on both sides of rest."""
    animation = Float(amount=amount)

    assert animation.extent("y") == pytest.approx((-amount, amount))
    assert animation.extent("x") == (0, 0)


@pytest.mark.parametrize("angle", [1.0, 3.0, 15.0])
def test_sway_swings_equally_to_both_sides(angle: float) -> None:
    """``angle`` is the maximum tilt, in degrees, in each direction."""
    assert Sway(angle=angle).extent("rotate") == pytest.approx((-angle, angle))


@pytest.mark.parametrize(
    ("pivot", "origin"),
    [("top", (0.5, 0.0)), ("center", (0.5, 0.5)), ("bottom", (0.5, 1.0))],
)
def test_sway_rotates_around_the_requested_pivot(
        pivot: Literal["top", "center", "bottom"],
        origin: tuple[float, float]) -> None:
    """The pivot decides which point of the element stays still."""
    assert Sway(pivot=pivot).origins == {origin}


def _shake_displacements(shakes: int, amount: float = 8.0) -> list[float]:
    frames = Shake(amount=amount, shakes=shakes).keyframes()
    return [frame.pose.x for frame in frames[1:-1]]


@pytest.mark.parametrize("shakes", [1, 4, 9])
def test_shake_jolts_as_many_times_as_requested(shakes: int) -> None:
    """Each requested shake must appear as one displacement keyframe."""
    assert len(_shake_displacements(shakes)) == shakes


@pytest.mark.parametrize("shakes", [2, 6, 9])
def test_shake_changes_direction_on_every_jolt(shakes: int) -> None:
    """A shake swings left and right, never twice to the same side in a row."""
    offsets = _shake_displacements(shakes)

    assert all(first * second < 0 for first,
               second in zip(offsets, offsets[1:]))


@pytest.mark.parametrize("shakes", [2, 6, 9])
def test_shake_loses_strength_with_every_jolt(shakes: int) -> None:
    """The shake must fade out like a damped oscillation."""
    strengths = [abs(offset) for offset in _shake_displacements(shakes)]

    assert all(first > second for first,
               second in zip(strengths, strengths[1:]))


@pytest.mark.parametrize("amount", [3.0, 8.0, 20.0])
def test_shake_first_jolt_reaches_the_requested_amount(amount: float) -> None:
    """``amount`` is the peak displacement in pixels."""
    assert abs(_shake_displacements(6, amount)[0]) == pytest.approx(amount)


def test_shake_moves_only_along_the_horizontal_axis() -> None:
    """A shake must not bounce the element vertically."""
    assert Shake().extent("y") == (0, 0)


def _jelly_deviations(wobbles: int, amount: float = 0.15) -> list[tuple[float, float]]:
    frames = Jelly(amount=amount, wobbles=wobbles).keyframes()
    return [(frame.pose.scale_x - 1, frame.pose.scale_y - 1) for frame in frames[1:-1]]


@pytest.mark.parametrize("wobbles", [1, 4, 9])
def test_jelly_wobbles_as_many_times_as_requested(wobbles: int) -> None:
    """Each requested wobble must appear as one deformation keyframe."""
    assert len(_jelly_deviations(wobbles)) == wobbles


@pytest.mark.parametrize("wobbles", [1, 4, 9])
def test_jelly_stretches_one_axis_exactly_as_much_as_it_squashes_the_other(
        wobbles: int) -> None:
    """Squash and stretch must compensate each other, like a soft volume."""
    for horizontal, vertical in _jelly_deviations(wobbles):
        assert horizontal == pytest.approx(-vertical)


@pytest.mark.parametrize("wobbles", [2, 4, 9])
def test_jelly_alternates_between_wide_and_tall_and_calms_down(
        wobbles: int) -> None:
    """Successive wobbles flip orientation while their strength decays."""
    horizontals = [horizontal for horizontal, _ in _jelly_deviations(wobbles)]

    assert all(first * second < 0 for first,
               second in zip(horizontals, horizontals[1:]))
    assert all(abs(first) > abs(second)
               for first, second in zip(horizontals, horizontals[1:]))


@pytest.mark.parametrize("amount", [0.05, 0.15, 0.5])
def test_jelly_first_wobble_deforms_by_the_requested_amount(amount: float) -> None:
    """``amount`` is the relative deformation at the strongest wobble."""
    assert abs(_jelly_deviations(4, amount)[0][0]) == pytest.approx(amount)


@pytest.mark.parametrize("radius", [2.0, 8.0, 30.0])
def test_drift_reaches_the_requested_radius_horizontally(radius: float) -> None:
    """``radius`` is the horizontal reach, in pixels, either side of rest."""
    assert Drift(radius=radius).extent("x") == pytest.approx((-radius, radius))


@pytest.mark.parametrize("radius", [2.0, 8.0, 30.0])
def test_drift_never_strays_further_than_its_radius_vertically(radius: float) -> None:
    """The vertical wander must stay within the declared radius."""
    low, high = Drift(radius=radius).extent("y")

    assert -radius <= low
    assert high <= radius
