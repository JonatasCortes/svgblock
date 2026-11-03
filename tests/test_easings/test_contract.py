"""Contract that every easing must honour, whatever its family."""

import dataclasses

import pytest
from svgblock import Easing

from .shared import (
    EVERY_EASING,
    JUMPS_AT_START,
    MONOTONIC,
    NON_MONOTONIC,
    NON_OVERSHOOTING,
    OVERSHOOTING,
    SAMPLE_POINTS,
    STARTS_AT_ZERO,
    TOLERANCE,
    each,
    is_valid_timing_function,
    sample,
    timing_function,
)

FINE_POINTS: tuple[float, ...] = tuple(index / 400 for index in range(401))


@each(EVERY_EASING)
def test_is_an_easing(easing: Easing) -> None:
    """Every registered object is an ``Easing``."""
    assert isinstance(easing, Easing)


@each(EVERY_EASING)
def test_css_is_a_valid_timing_function(easing: Easing) -> None:
    """The generated CSS must be accepted by a browser."""
    assert is_valid_timing_function(easing.css())


@each(EVERY_EASING)
def test_css_is_deterministic(easing: Easing) -> None:
    """Calling ``css()`` repeatedly returns the same text."""
    assert easing.css() == easing.css()


@each(STARTS_AT_ZERO)
def test_progress_starts_at_zero(easing: Easing) -> None:
    """Without a jump at the start, the animation begins at 0."""
    assert timing_function(easing)(0.0) == pytest.approx(0.0, abs=TOLERANCE)


@each(JUMPS_AT_START)
def test_progress_jumps_above_zero_at_start(easing: Easing) -> None:
    """A jump at the start lifts the first output above 0, by design."""
    assert timing_function(easing)(0.0) > 0.0


@each(EVERY_EASING)
def test_progress_ends_at_one(easing: Easing) -> None:
    """Every easing must finish exactly where the animation ends."""
    assert timing_function(easing)(1.0) == pytest.approx(1.0, abs=TOLERANCE)


@each(EVERY_EASING)
def test_mirrored_is_the_point_reflection_of_the_curve(
    easing: Easing,
) -> None:
    """``mirrored()`` must satisfy ``g(t) = 1 - f(1 - t)``."""
    mirrored = sample(easing.mirrored())
    reflected = [1 - value for value in
                 sample(easing, [1 - point for point in SAMPLE_POINTS])]

    assert mirrored == pytest.approx(reflected, abs=TOLERANCE)


@each(EVERY_EASING)
def test_mirroring_twice_restores_the_easing(easing: Easing) -> None:
    """``mirrored()`` is an involution on the generated CSS and bounds."""
    restored = easing.mirrored().mirrored()

    assert restored.css() == easing.css()
    assert restored.bounds == pytest.approx(easing.bounds)


@each(EVERY_EASING)
def test_mirrored_bounds_are_the_inverted_bounds(easing: Easing) -> None:
    """The range of the mirrored easing is ``(1 - max, 1 - min)``."""
    lowest, highest = easing.bounds

    assert easing.mirrored().bounds == pytest.approx(
        (1 - highest, 1 - lowest), abs=TOLERANCE)


@each(EVERY_EASING)
def test_bounds_contain_the_unit_interval(easing: Easing) -> None:
    """Progress starts at 0 and ends at 1, so both must be inside the range."""
    lowest, highest = easing.bounds

    assert lowest <= 0.0
    assert highest >= 1.0


@each(EVERY_EASING)
def test_bounds_contain_every_output(easing: Easing) -> None:
    """No output may fall outside the advertised ``bounds``."""
    lowest, highest = easing.bounds
    values = sample(easing, FINE_POINTS)

    assert min(values) >= lowest - TOLERANCE
    assert max(values) <= highest + TOLERANCE


@each(MONOTONIC)
def test_monotonic_easings_never_go_backwards(easing: Easing) -> None:
    """Progress of a monotonic easing never decreases."""
    values = sample(easing, FINE_POINTS)

    assert all(after >= before - TOLERANCE
               for before, after in zip(values, values[1:]))


@each(NON_MONOTONIC)
def test_non_monotonic_easings_go_backwards_somewhere(
    easing: Easing,
) -> None:
    """Easings declared as non-monotonic must really reverse direction."""
    values = sample(easing, FINE_POINTS)

    assert any(after < before - TOLERANCE
               for before, after in zip(values, values[1:]))


@each(OVERSHOOTING)
def test_overshooting_easings_leave_the_unit_interval(
    easing: Easing,
) -> None:
    """Overshoot is deliberate: outputs go below 0 or above 1."""
    values = sample(easing, FINE_POINTS)

    assert min(values) < -TOLERANCE or max(values) > 1 + TOLERANCE


@each(NON_OVERSHOOTING)
def test_other_easings_stay_inside_the_unit_interval(
    easing: Easing,
) -> None:
    """Easings without overshoot never leave ``[0, 1]``."""
    values = sample(easing, FINE_POINTS)

    assert min(values) >= -TOLERANCE
    assert max(values) <= 1 + TOLERANCE


@each(EVERY_EASING)
def test_easing_is_immutable(easing: Easing) -> None:
    """Easings are value objects and must reject attribute assignment."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(easing, "injected", 1)


@each(EVERY_EASING)
def test_easing_is_hashable_and_equal_to_itself(easing: Easing) -> None:
    """Easings can be used as dictionary keys and in sets."""
    assert easing == easing
    assert len({easing, easing}) == 1
    assert hash(easing) == hash(easing)
