"""``Bounce``: validation of ``bounces`` and ``rebound`` and the bouncing curve."""

import math

import pytest
from svgblock import Bounce

from .shared import TOLERANCE, is_valid_timing_function, sample, unchecked

FINE_POINTS: tuple[float, ...] = tuple(index / 4000 for index in range(4001))
CSS_NODES: tuple[float, ...] = tuple(index / 96 for index in range(0, 97, 8))
MIN_DIP = 1e-4


def dips(bounce: Bounce) -> list[float]:
    """Return the local minima below 1 of a bounce, in time order."""
    values = [bounce.value(point) for point in FINE_POINTS]
    return [
        current
        for before, current, after in zip(values, values[1:], values[2:])
        if current < before and current <= after and current < 1 - MIN_DIP
    ]


def test_defaults() -> None:
    """A bounce without arguments has three bounces and rebound 0.5."""
    assert Bounce().bounces == 3
    assert Bounce().rebound == 0.5


@pytest.mark.parametrize("bounces", [1, 2, 3, 10])
@pytest.mark.parametrize("rebound", [0.1, 0.5, 0.9, 0.999])
def test_valid_arguments_make_a_valid_timing_function(
    bounces: int, rebound: float,
) -> None:
    """Whole bounces of 1 or more and rebound inside (0, 1) are accepted."""
    assert is_valid_timing_function(Bounce(bounces, rebound).css())


@pytest.mark.parametrize("bounces", [0, -1, -10, True, False])
def test_invalid_bounces_are_rejected(bounces: int) -> None:
    """Bounces must be a whole number of 1 or more, never a boolean."""
    with pytest.raises(ValueError, match="bounces"):
        Bounce(unchecked(bounces))


@pytest.mark.parametrize(
    "bounces",
    [
        pytest.param(value,)
        for value in (2.5, 3.0, math.nan, math.inf)
    ],
    ids=["2.5", "3.0", "nan", "inf"],
)
def test_non_integer_bounces_are_rejected(bounces: float) -> None:
    """A fractional, float or non-finite number of bounces is invalid."""
    with pytest.raises(ValueError, match="bounces"):
        Bounce(unchecked(bounces)).css()


@pytest.mark.parametrize(
    "rebound",
    [0.0, -0.1, 1.0, 1.5, math.nan, math.inf, -math.inf],
    ids=["0", "-0.1", "1", "1.5", "nan", "inf", "-inf"],
)
def test_rebound_outside_the_open_unit_interval_is_rejected(
    rebound: float,
) -> None:
    """A ball must lose some energy and keep some."""
    with pytest.raises(ValueError, match="rebound"):
        Bounce(3, rebound)


@pytest.mark.parametrize("bounces", [1, 3, 6])
@pytest.mark.parametrize("rebound", [0.2, 0.5, 0.8])
def test_value_stays_within_the_unit_interval(
    bounces: int, rebound: float,
) -> None:
    """The ball never goes past its target nor below its start."""
    bounce = Bounce(bounces, rebound)
    values = [bounce.value(point) for point in FINE_POINTS]

    assert max(values) <= 1 + 1e-12
    assert min(values) >= -1e-12
    assert bounce.bounds[1] <= 1 + 1e-12


@pytest.mark.parametrize("bounces", [1, 3, 6])
def test_curve_starts_at_zero_and_ends_at_one(bounces: int) -> None:
    """The animation covers the whole path."""
    bounce = Bounce(bounces)

    assert bounce.value(0) == pytest.approx(0, abs=1e-9)
    assert bounce.value(1) == pytest.approx(1, abs=1e-9)


@pytest.mark.parametrize("bounces", [1, 2, 3, 5])
def test_number_of_dips_matches_bounces(bounces: int) -> None:
    """Each bounce leaves the target once and comes back."""
    assert len(dips(Bounce(bounces, 0.5))) == bounces


@pytest.mark.parametrize("rebound", [0.3, 0.5, 0.7])
def test_first_dip_depth_is_the_squared_rebound(rebound: float) -> None:
    """The first bounce rises by ``rebound ** 2`` of the distance."""
    assert dips(Bounce(3, rebound))[0] == pytest.approx(
        1 - rebound ** 2, abs=1e-3)


@pytest.mark.parametrize("rebound", [0.3, 0.5, 0.7])
def test_each_bounce_is_smaller_than_the_previous_one(
    rebound: float,
) -> None:
    """Energy is lost at every impact, so the dips get shallower."""
    found = dips(Bounce(3, rebound))

    assert len(found) == 3
    assert found == sorted(found)
    assert len(set(found)) == len(found)


def test_more_rebound_means_deeper_first_dip() -> None:
    """A livelier ball goes further from the target."""
    firsts = [dips(Bounce(3, rebound))[0] for rebound in (0.3, 0.5, 0.7)]

    assert firsts == sorted(firsts, reverse=True)
    assert len(set(firsts)) == len(firsts)


@pytest.mark.parametrize("bounces,rebound", [(1, 0.5), (3, 0.5), (5, 0.3)])
def test_css_matches_value_at_its_nodes(
    bounces: int, rebound: float,
) -> None:
    """The generated ``linear()`` reproduces ``value`` where it is sampled."""
    bounce = Bounce(bounces, rebound)

    assert sample(bounce, CSS_NODES) == pytest.approx(
        [bounce.value(point) for point in CSS_NODES], abs=TOLERANCE)


def test_mirrored_stays_within_the_unit_interval() -> None:
    """The reflected bounce keeps the same bounds and endpoints."""
    mirrored = Bounce().mirrored()
    values = sample(mirrored, FINE_POINTS)

    assert is_valid_timing_function(mirrored.css())
    assert min(values) >= -TOLERANCE
    assert max(values) <= 1 + TOLERANCE
    assert values[0] == pytest.approx(0, abs=TOLERANCE)
    assert values[-1] == pytest.approx(1, abs=TOLERANCE)


def test_mirroring_twice_returns_the_same_bounce() -> None:
    """Mirroring is an involution and gives back an equal easing."""
    assert Bounce(4, 0.3).mirrored().mirrored() == Bounce(4, 0.3)


def test_equal_arguments_make_equal_bounces() -> None:
    """Bounces are value objects: same arguments, same easing and hash."""
    assert Bounce() == Bounce(3, 0.5)
    assert hash(Bounce()) == hash(Bounce(3, 0.5))


def test_different_arguments_make_different_bounces() -> None:
    """Both arguments take part in equality."""
    assert Bounce(3, 0.5) != Bounce(4, 0.5)
    assert Bounce(3, 0.5) != Bounce(3, 0.4)
