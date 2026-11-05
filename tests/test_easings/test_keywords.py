"""Keyword easings: ``Linear``, ``EaseIn``, ``EaseOut`` and ``EaseInOut``."""

import pytest
from svgblock import EaseIn, EaseInOut, EaseOut, Easing, Linear
from .shared import KEYWORDS, TOLERANCE, each, timing_function

EXPECTED_CSS: dict[str, Easing] = {
    "linear": Linear(),
    "ease-in": EaseIn(),
    "ease-out": EaseOut(),
    "ease-in-out": EaseInOut(),
}


@pytest.mark.parametrize(
    ("expected", "easing"), list(EXPECTED_CSS.items()),
    ids=list(EXPECTED_CSS))
def test_css_is_the_css_keyword(expected: str, easing: Easing) -> None:
    """Each class maps to the CSS keyword of the same name."""
    assert easing.css() == expected


@each(KEYWORDS)
def test_bounds_are_the_unit_interval(easing: Easing) -> None:
    """Keyword easings never leave ``[0, 1]``."""
    assert easing.bounds == (0.0, 1.0)


def test_ease_in_mirrors_to_ease_out() -> None:
    """Reversing a slow start gives a slow end."""
    assert EaseIn().mirrored() == EaseOut()


def test_ease_out_mirrors_to_ease_in() -> None:
    """Reversing a slow end gives a slow start."""
    assert EaseOut().mirrored() == EaseIn()


@pytest.mark.parametrize(
    "easing", [Linear(), EaseInOut()], ids=["Linear", "EaseInOut"])
def test_symmetric_easings_mirror_to_themselves(easing: Easing) -> None:
    """Easings that are symmetric around the centre are their own mirror."""
    assert easing.mirrored() == easing


def test_linear_progress_equals_time() -> None:
    """Linear progress is the identity function."""
    progress = timing_function(Linear())

    assert [progress(t) for t in (0.1, 0.5, 0.9)] == pytest.approx(
        [0.1, 0.5, 0.9], abs=TOLERANCE)


def test_ease_in_is_slower_than_linear_at_the_start() -> None:
    """A slow start means less progress than linear in the first half."""
    progress = timing_function(EaseIn())

    assert progress(0.25) < 0.25
    assert progress(0.5) < 0.5


def test_ease_out_is_faster_than_linear_at_the_start() -> None:
    """A slow end means more progress than linear in the first half."""
    progress = timing_function(EaseOut())

    assert progress(0.25) > 0.25
    assert progress(0.5) > 0.5


def test_ease_in_out_is_slow_at_both_ends() -> None:
    """Progress lags at the start, crosses the centre, and leads at the end."""
    progress = timing_function(EaseInOut())

    assert progress(0.25) < 0.25
    assert progress(0.5) == pytest.approx(0.5, abs=TOLERANCE)
    assert progress(0.75) > 0.75


def test_different_keywords_are_not_equal() -> None:
    """Distinct classes with no fields must not compare equal."""
    assert len(set(KEYWORDS.values())) == len(KEYWORDS)


def test_instances_of_the_same_keyword_are_equal() -> None:
    """Keyword easings carry no state, so any two instances are equal."""
    assert EaseIn() == EaseIn()
    assert hash(EaseIn()) == hash(EaseIn())
