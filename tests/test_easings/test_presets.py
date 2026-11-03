"""Named presets: Sine, Cubic, Quint, Expo, Circ and Back."""

import pytest
from svgblock import (
    EaseIn,
    EaseInBack,
    EaseInCirc,
    EaseInCubic,
    EaseInExpo,
    EaseInOutBack,
    EaseInOutCirc,
    EaseInOutCubic,
    EaseInOutExpo,
    EaseInOutQuint,
    EaseInOutSine,
    EaseInQuint,
    EaseInSine,
    Easing,
    EaseOutBack,
    EaseOutCirc,
    EaseOutCubic,
    EaseOutExpo,
    EaseOutQuint,
    EaseOutSine,
)

from .shared import (
    BACK_PRESETS,
    MIRROR_PAIRS,
    PRESETS,
    SELF_MIRRORED,
    MirrorPair,
    TOLERANCE,
    each,
    each_pair,
    excluding,
    timing_function,
)

EXPECTED_CSS: dict[Easing, str] = {
    EaseInSine(): "cubic-bezier(0.12, 0, 0.39, 0)",
    EaseOutSine(): "cubic-bezier(0.61, 1, 0.88, 1)",
    EaseInOutSine(): "cubic-bezier(0.37, 0, 0.63, 1)",
    EaseInCubic(): "cubic-bezier(0.32, 0, 0.67, 0)",
    EaseOutCubic(): "cubic-bezier(0.33, 1, 0.68, 1)",
    EaseInOutCubic(): "cubic-bezier(0.65, 0, 0.35, 1)",
    EaseInQuint(): "cubic-bezier(0.64, 0, 0.78, 0)",
    EaseOutQuint(): "cubic-bezier(0.22, 1, 0.36, 1)",
    EaseInOutQuint(): "cubic-bezier(0.83, 0, 0.17, 1)",
    EaseInExpo(): "cubic-bezier(0.7, 0, 0.84, 0)",
    EaseOutExpo(): "cubic-bezier(0.16, 1, 0.3, 1)",
    EaseInOutExpo(): "cubic-bezier(0.87, 0, 0.13, 1)",
    EaseInCirc(): "cubic-bezier(0.55, 0, 1, 0.45)",
    EaseOutCirc(): "cubic-bezier(0, 0.55, 0.45, 1)",
    EaseInOutCirc(): "cubic-bezier(0.85, 0, 0.15, 1)",
    EaseInBack(): "cubic-bezier(0.36, 0, 0.66, -0.56)",
    EaseOutBack(): "cubic-bezier(0.34, 1.56, 0.64, 1)",
    EaseInOutBack(): "cubic-bezier(0.68, -0.6, 0.32, 1.6)",
}

PRESET_PAIRS: dict[str, MirrorPair] = {
    key: pair for key, pair in MIRROR_PAIRS.items()
    if repr(pair[0]) in PRESETS and repr(pair[1]) in PRESETS
}

SELF_MIRRORED_PRESETS = {
    key: easing for key, easing in SELF_MIRRORED.items() if key in PRESETS
}

SMOOTH_PRESETS = excluding(PRESETS, BACK_PRESETS)


@each(PRESETS)
def test_css_matches_the_reference_curve(easing: Easing) -> None:
    """Each preset must be the well known curve it is named after."""
    assert easing in EXPECTED_CSS, "preset missing from the reference table"
    assert easing.css() == EXPECTED_CSS[easing]


def test_reference_table_has_no_unregistered_preset() -> None:
    """The reference table and the catalogue must describe the same set."""
    assert {repr(easing) for easing in EXPECTED_CSS} == set(PRESETS)


@each(SMOOTH_PRESETS)
def test_smooth_presets_stay_inside_the_unit_interval(
    easing: Easing,
) -> None:
    """Only the ``Back`` presets are allowed to overshoot."""
    assert easing.bounds == pytest.approx((0.0, 1.0), abs=TOLERANCE)


def test_ease_in_back_dips_below_zero_but_never_exceeds_one() -> None:
    """Anticipation: the curve pulls back before moving forward."""
    lowest, highest = EaseInBack().bounds

    assert lowest < -0.05
    assert highest == pytest.approx(1.0, abs=TOLERANCE)


def test_ease_out_back_exceeds_one_but_never_dips_below_zero() -> None:
    """Overshoot: the curve passes the target before settling on it."""
    lowest, highest = EaseOutBack().bounds

    assert lowest == pytest.approx(0.0, abs=TOLERANCE)
    assert highest > 1.05


def test_ease_in_out_back_overshoots_on_both_sides() -> None:
    """The curve anticipates at the start and overshoots at the end."""
    lowest, highest = EaseInOutBack().bounds

    assert lowest < -0.05
    assert highest > 1.05


@each_pair(PRESET_PAIRS)
def test_in_and_out_presets_mirror_each_other(
    easing: Easing, mirror: Easing,
) -> None:
    """The ``In`` and ``Out`` variants are reflections of one another."""
    assert easing.mirrored().css() == mirror.css()
    assert mirror.mirrored().css() == easing.css()


@each(SELF_MIRRORED_PRESETS)
def test_in_out_presets_are_symmetric(easing: Easing) -> None:
    """The ``InOut`` variants are their own reflection."""
    assert easing.mirrored().css() == easing.css()


def test_stronger_ease_in_presets_start_slower() -> None:
    """Progress at the midpoint falls as the exponent of the curve grows."""
    midpoints = [
        timing_function(easing)(0.5)
        for easing in (EaseInSine(), EaseInCubic(), EaseInQuint(),
                       EaseInExpo())
    ]

    assert midpoints == sorted(midpoints, reverse=True)


def test_presets_differ_from_the_plain_keywords() -> None:
    """A preset must not silently collapse into the CSS ``ease-in``."""
    assert EaseInSine().css() != EaseIn().css()
