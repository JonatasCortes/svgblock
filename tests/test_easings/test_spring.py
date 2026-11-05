"""``Spring``: validation of ``bounce`` and the physics of the curve."""

import math
from collections.abc import Sequence
from contextlib import suppress

import pytest
from svgblock import Spring

from .shared import TOLERANCE, is_valid_timing_function, sample

MAX_BOUNCE = 0.9
FINE_POINTS: tuple[float, ...] = tuple(index / 400 for index in range(401))
SETTLING_POINTS: tuple[float, ...] = tuple(
    0.95 + index / 400 for index in range(21))


def overshoot(bounce: float) -> float:
    """Measure how far a spring goes beyond its target.

    Parameters
    ----------
    bounce : float
        Bounce of the spring.

    Returns
    -------
    float
        Highest output of the spring minus 1.
    """
    return max(sample(Spring(bounce), FINE_POINTS)) - 1


def upward_crossings(bounce: float) -> int:
    """Count how many times a spring rises through its target.

    Parameters
    ----------
    bounce : float
        Bounce of the spring.

    Returns
    -------
    int
        Number of consecutive samples going from below 1 to 1 or above.
    """
    values = sample(Spring(bounce), FINE_POINTS)
    return sum(1 for before, after in zip(values, values[1:])
               if before < 1 <= after)


def peaks_above_target(values: Sequence[float]) -> list[float]:
    """Return the local maxima of a series that are above 1.

    Parameters
    ----------
    values : Sequence[float]
        Series to inspect.

    Returns
    -------
    list[float]
        Interior values higher than both neighbours and than 1, in order.
    """
    return [
        current
        for before, current, after in zip(values, values[1:], values[2:])
        if current > before and current > after and current > 1
    ]


def theoretical_overshoot(bounce: float) -> float:
    """Return the first peak of an underdamped spring above its target.

    Parameters
    ----------
    bounce : float
        Bounce of the spring, where the damping ratio is ``1 - bounce``.

    Returns
    -------
    float
        ``exp(-pi * z / sqrt(1 - z ** 2))`` with ``z = 1 - bounce``.
    """
    damping = 1 - bounce
    return math.exp(-math.pi * damping / math.sqrt(1 - damping ** 2))


def test_bounce_defaults_to_one_half() -> None:
    """A spring without arguments is a medium bounce."""
    assert Spring().bounce == 0.5


@pytest.mark.parametrize("bounce", [1e-6, 0.1, 0.5, 0.9])
def test_bounce_accepts_values_up_to_the_maximum(bounce: float) -> None:
    """Any bounce above 0 and up to 0.9, inclusive, is valid."""
    assert is_valid_timing_function(Spring(bounce).css())


@pytest.mark.parametrize(
    "bounce",
    [0.0, -0.1, MAX_BOUNCE + 1e-9, 1.0, 1.5, math.nan, math.inf, -math.inf],
    ids=["0", "-0.1", "0.9+1e-9", "1", "1.5", "nan", "inf", "-inf"],
)
def test_bounce_outside_the_range_is_rejected(bounce: float) -> None:
    """A spring needs some bounce, and not so much that it never settles."""
    with pytest.raises(ValueError, match="bounce"):
        Spring(bounce)


def test_extremely_small_bounce_is_rejected_or_usable() -> None:
    """A positive bounce must never crash later: reject it or make it work."""
    with suppress(ValueError):
        assert is_valid_timing_function(Spring(1e-17).css())


@pytest.mark.parametrize("bounce", [0.25, 0.5, 0.9])
def test_bouncy_spring_overshoots_its_target(bounce: float) -> None:
    """A spring with enough bounce passes the target before settling."""
    assert overshoot(bounce) > 0.01


def test_gentle_spring_settles_without_visible_overshoot() -> None:
    """With little bounce the first peak would come after the animation."""
    assert overshoot(0.1) < 0.01


@pytest.mark.parametrize("bounce", [0.25, 0.5, 0.75])
def test_first_overshoot_matches_the_damped_oscillator(
    bounce: float,
) -> None:
    """The first peak follows the classic underdamped spring formula."""
    assert overshoot(bounce) == pytest.approx(
        theoretical_overshoot(bounce), abs=0.01)


def test_more_bounce_means_more_overshoot() -> None:
    """Overshoot grows with the bounce."""
    overshoots = [overshoot(bounce) for bounce in (0.1, 0.25, 0.5, 0.75, 0.9)]

    assert overshoots == sorted(overshoots)
    assert len(set(overshoots)) == len(overshoots)


def test_more_bounce_means_more_oscillations() -> None:
    """A bouncier spring crosses its target more times before settling."""
    counts = [upward_crossings(bounce) for bounce in (0.25, 0.5, 0.9)]

    assert counts == sorted(counts)
    assert len(set(counts)) == len(counts)


def test_each_oscillation_is_smaller_than_the_previous_one() -> None:
    """Damping makes every peak lower than the one before."""
    peaks = peaks_above_target(sample(Spring(0.9), FINE_POINTS))

    assert len(peaks) > 2
    assert peaks == sorted(peaks, reverse=True)


@pytest.mark.parametrize("bounce", [0.1, 0.5, 0.9])
def test_spring_has_settled_before_the_end(bounce: float) -> None:
    """In the last stretch the spring rests on its target."""
    values = sample(Spring(bounce), SETTLING_POINTS)

    assert values == pytest.approx([1.0] * len(values), abs=0.01)


@pytest.mark.parametrize("bounce", [0.1, 0.5, 0.9])
def test_spring_never_goes_below_its_starting_point(bounce: float) -> None:
    """A spring released from rest only moves towards the target at first."""
    assert min(sample(Spring(bounce), FINE_POINTS)) >= -TOLERANCE


def test_mirrored_spring_pulls_back_before_moving() -> None:
    """The reflected spring anticipates: it dips below its starting point."""
    values = sample(Spring().mirrored(), FINE_POINTS)

    assert min(values) < -0.05


def test_mirroring_twice_returns_the_same_spring() -> None:
    """Mirroring is an involution and gives back an equal easing."""
    assert Spring(0.3).mirrored().mirrored() == Spring(0.3)


def test_equal_bounce_makes_equal_springs() -> None:
    """Springs are value objects: same bounce, same easing and hash."""
    assert Spring() == Spring(0.5)
    assert hash(Spring()) == hash(Spring(0.5))


def test_different_bounce_makes_different_springs() -> None:
    """The bounce takes part in equality."""
    assert Spring(0.3) != Spring(0.4)
