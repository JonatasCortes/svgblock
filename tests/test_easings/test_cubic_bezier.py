"""``CubicBezier``: validation, range of values and mirroring."""

import math
import pytest
from svgblock import CubicBezier
from .shared import TOLERANCE

NON_FINITE = [math.nan, math.inf, -math.inf]
NON_FINITE_IDS = ["nan", "inf", "-inf"]
OUT_OF_UNIT_RANGE = [-0.1, -1e-9, 1.0 + 1e-9, 1.1, 100.0, *NON_FINITE]
OUT_OF_UNIT_RANGE_IDS = [
    "-0.1", "-1e-9", "1+1e-9", "1.1", "100", *NON_FINITE_IDS]


def build(**overrides: float) -> CubicBezier:
    """Build a valid ``CubicBezier`` replacing only the given coordinates.

    Parameters
    ----------
    **overrides : float
        Coordinates among ``x1``, ``y1``, ``x2`` and ``y2`` to replace.

    Returns
    -------
    CubicBezier
        The resulting easing.
    """
    coordinates = {"x1": 0.25, "y1": 0.1, "x2": 0.25, "y2": 1.0}
    coordinates.update(overrides)
    return CubicBezier(**coordinates)


@pytest.mark.parametrize("name", ["x1", "x2"])
@pytest.mark.parametrize("value", [0.0, 0.5, 1.0])
def test_x_coordinates_accept_the_unit_interval_including_its_edges(
    name: str, value: float,
) -> None:
    """Time coordinates may be anywhere in ``[0, 1]``, edges included."""
    easing = build(**{name: value})

    assert getattr(easing, name) == value


@pytest.mark.parametrize("name", ["x1", "x2"])
@pytest.mark.parametrize(
    "value", OUT_OF_UNIT_RANGE, ids=OUT_OF_UNIT_RANGE_IDS)
def test_x_coordinates_outside_the_unit_interval_are_rejected(
    name: str, value: float,
) -> None:
    """CSS rejects ``cubic-bezier()`` with x outside ``[0, 1]``."""
    with pytest.raises(ValueError, match=name):
        build(**{name: value})


@pytest.mark.parametrize("name", ["y1", "y2"])
@pytest.mark.parametrize("value", [-10.0, -0.5, 0.0, 0.5, 1.0, 1.5, 10.0])
def test_y_coordinates_accept_any_finite_number(
    name: str, value: float,
) -> None:
    """Progress coordinates may overshoot, so any finite value is valid."""
    easing = build(**{name: value})

    assert getattr(easing, name) == value


@pytest.mark.parametrize("name", ["y1", "y2"])
@pytest.mark.parametrize("value", NON_FINITE, ids=NON_FINITE_IDS)
def test_y_coordinates_that_are_not_finite_are_rejected(
    name: str, value: float,
) -> None:
    """``nan`` and infinities can never form a valid timing function."""
    with pytest.raises(ValueError, match=name):
        build(**{name: value})


def test_coordinates_are_stored_as_given() -> None:
    """Positional arguments map to ``x1, y1, x2, y2`` in that order."""
    easing = CubicBezier(0.1, 0.2, 0.3, 0.4)

    assert (easing.x1, easing.y1, easing.x2, easing.y2) == (
        0.1, 0.2, 0.3, 0.4)


def test_bounds_of_a_diagonal_are_the_unit_interval() -> None:
    """A straight diagonal never leaves ``[0, 1]``."""
    assert CubicBezier(0, 0, 1, 1).bounds == pytest.approx(
        (0.0, 1.0), abs=TOLERANCE)


def test_bounds_of_a_monotonic_curve_are_the_unit_interval() -> None:
    """Control values inside ``[0, 1]`` keep the curve inside it."""
    assert build().bounds == pytest.approx((0.0, 1.0), abs=TOLERANCE)


def test_bounds_report_the_overshoot() -> None:
    """Control values beyond the unit interval widen the bounds."""
    lowest, highest = CubicBezier(0.5, -0.5, 0.5, 1.5).bounds

    assert lowest < -0.02
    assert highest > 1.02


def test_bounds_do_not_depend_on_the_x_coordinates() -> None:
    """Bounds describe progress only, so time coordinates cannot alter them."""
    assert build(x1=0.0, x2=1.0).bounds == build(x1=0.9, x2=0.1).bounds


def test_mirrored_reflects_every_coordinate() -> None:
    """Point reflection swaps the handles and inverts each coordinate."""
    mirrored = CubicBezier(0.25, 0.1, 0.25, 1).mirrored()

    assert isinstance(mirrored, CubicBezier)
    assert (mirrored.x1, mirrored.y1, mirrored.x2, mirrored.y2) == (
        pytest.approx((0.75, 0.0, 0.75, 0.9)))


@pytest.mark.parametrize("name", ["x1", "x2"])
@pytest.mark.parametrize("value", [0.0, 1.0])
def test_mirrored_stays_valid_at_the_edges(name: str, value: float) -> None:
    """Reflecting an edge coordinate must not leave the unit interval."""
    mirrored = build(**{name: value}).mirrored()

    assert isinstance(mirrored, CubicBezier)


def test_equal_coordinates_make_equal_easings() -> None:
    """Easings are value objects: same coordinates, same easing and hash."""
    assert build() == build()
    assert hash(build()) == hash(build())


def test_different_coordinates_make_different_easings() -> None:
    """Any differing coordinate makes the easings unequal."""
    assert build() != build(y2=0.9)
