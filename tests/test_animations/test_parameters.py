"""Rejection of invalid parameters and acceptance of boundary values."""

from collections.abc import Callable

import pytest

from svgblock import (
    BaseAnimation,
    Drift,
    DropIn,
    EaseInBack,
    EaseOutBack,
    FadeIn,
    FadeOut,
    Float,
    FlickerIn,
    FlickerOut,
    FlipIn,
    FocusIn,
    FocusOut,
    GlitchIn,
    Hide,
    Jelly,
    PopIn,
    Pulse,
    RiseIn,
    Rotate,
    Shake,
    Show,
    SlideIn,
    Sway,
    UnfoldIn,
    ZoomIn,
)
from tests.test_animations.shared import unchecked

Factory = Callable[[], BaseAnimation]

INVALID_PARAMETERS = [
    pytest.param(lambda: FadeIn(duration=0),
                 "duration must be greater than 0", id="fade-in-zero-duration"),
    pytest.param(lambda: FadeOut(duration=-1),
                 "duration must be greater than 0", id="fade-out-negative-duration"),
    pytest.param(lambda: Show(duration=0),
                 "duration must be greater than 0", id="show-zero-duration"),
    pytest.param(lambda: Hide(duration=-2),
                 "duration must be greater than 0", id="hide-negative-duration"),
    pytest.param(lambda: RiseIn(distance=-1),
                 "distance must be 0 or more", id="rise-negative-distance"),
    pytest.param(lambda: DropIn(distance=-0.5),
                 "distance must be 0 or more", id="drop-negative-distance"),
    pytest.param(lambda: SlideIn(direction=unchecked("up")),
                 "direction must be", id="slide-unknown-direction"),
    pytest.param(lambda: ZoomIn(scale=0),
                 "scale must be greater than 0", id="zoom-zero-scale"),
    pytest.param(lambda: ZoomIn(scale=-1),
                 "scale must be greater than 0", id="zoom-negative-scale"),
    pytest.param(lambda: FlipIn(axis=unchecked("diagonal")),
                 "axis must be", id="flip-unknown-axis"),
    pytest.param(lambda: UnfoldIn(edge=unchecked("middle")),
                 "edge must be", id="unfold-unknown-edge"),
    pytest.param(lambda: GlitchIn(intensity=0),
                 "intensity must be greater than 0", id="glitch-zero-intensity"),
    pytest.param(lambda: FlickerIn(
        flickers=0), "flickers must be a whole number", id="flicker-in-zero-flickers"),
    pytest.param(lambda: FlickerOut(flickers=-1),
                 "flickers must be a whole number", id="flicker-out-negative-flickers"),
    pytest.param(lambda: FlickerIn(flickers=True),
                 "flickers must be a whole number", id="flicker-boolean-flickers"),
    pytest.param(lambda: PopIn(start_scale=0),
                 "start_scale must be greater than 0", id="pop-zero-start-scale"),
    pytest.param(lambda: PopIn(start_scale=1.5),
                 "start_scale must be greater than 0 and at most 1", id="pop-oversized-start-scale"),
    pytest.param(lambda: FocusIn(blur=0),
                 "blur must be greater than 0", id="focus-in-zero-blur"),
    pytest.param(lambda: FocusOut(blur=-3), "blur must be",
                 id="focus-out-negative-blur"),
    pytest.param(lambda: Pulse(amount=0),
                 "amount must be greater than 0", id="pulse-zero-amount"),
    pytest.param(lambda: Float(amount=-1),
                 "amount must be greater than 0", id="float-negative-amount"),
    pytest.param(lambda: Shake(amount=0),
                 "amount must be greater than 0", id="shake-zero-amount"),
    pytest.param(lambda: Shake(shakes=0),
                 "shakes must be a whole number", id="shake-zero-shakes"),
    pytest.param(lambda: Sway(angle=0),
                 "angle must be greater than 0", id="sway-zero-angle"),
    pytest.param(lambda: Sway(angle=-3),
                 "angle must be greater than 0", id="sway-negative-angle"),
    pytest.param(lambda: Sway(pivot=unchecked("left")),
                 "pivot must be", id="sway-unknown-pivot"),
    pytest.param(lambda: Rotate(angle=0),
                 "angle must not be 0", id="rotate-zero-angle"),
    pytest.param(lambda: Drift(radius=0),
                 "radius must be greater than 0", id="drift-zero-radius"),
    pytest.param(lambda: Jelly(
        amount=0), "amount must be greater than 0 and less than 1", id="jelly-zero-amount"),
    pytest.param(lambda: Jelly(
        amount=1), "amount must be greater than 0 and less than 1", id="jelly-full-amount"),
    pytest.param(lambda: Jelly(wobbles=0),
                 "wobbles must be a whole number", id="jelly-zero-wobbles"),
    pytest.param(lambda: FocusIn(easing=EaseOutBack()),
                 "blur go below 0", id="focus-in-overshooting-easing"),
    pytest.param(lambda: FocusOut(easing=EaseInBack()),
                 "blur go below 0", id="focus-out-undershooting-easing"),
]

VALID_BOUNDARIES = [
    pytest.param(lambda: RiseIn(distance=0), id="zero-distance"),
    pytest.param(lambda: PopIn(start_scale=1.0), id="start-scale-at-peak"),
    pytest.param(lambda: Jelly(amount=0.999), id="jelly-just-below-one"),
    pytest.param(lambda: FlickerIn(flickers=1), id="single-flicker"),
    pytest.param(lambda: Shake(shakes=1), id="single-shake"),
    pytest.param(lambda: Jelly(wobbles=1), id="single-wobble"),
    pytest.param(lambda: Pulse(loop_limit=1000), id="maximum-loop-limit"),
    pytest.param(lambda: Rotate(angle=-90), id="negative-rotation"),
    pytest.param(lambda: ZoomIn(scale=3), id="zoom-from-larger"),
]


@pytest.mark.parametrize(("factory", "message"), INVALID_PARAMETERS)
def test_invalid_parameter_is_rejected_with_a_message_naming_it(
        factory: Factory, message: str) -> None:
    """Bad input must fail at construction, saying which parameter is wrong."""
    with pytest.raises(ValueError, match=message):
        factory()


@pytest.mark.parametrize("factory", VALID_BOUNDARIES)
def test_boundary_value_is_accepted(factory: Factory) -> None:
    """Values at the edge of the documented range must remain usable."""
    assert isinstance(factory(), BaseAnimation)


@pytest.mark.parametrize("factory", [lambda: Show(1.5), lambda: Hide(0.25)],
                         ids=["show", "hide"])
def test_hold_accepts_its_duration_as_a_positional_argument(
        factory: Factory) -> None:
    """Holds exist only for their duration, so it is the one required argument."""
    assert factory().duration in (1.5, 0.25)


@pytest.mark.parametrize("hold", [Show, Hide])
def test_hold_requires_a_duration(hold: Callable[..., BaseAnimation]) -> None:
    """A hold without a duration has no meaning."""
    with pytest.raises(TypeError):
        hold()


@pytest.mark.parametrize("hold", [Show, Hide])
def test_hold_does_not_accept_a_custom_easing(hold: Callable[..., BaseAnimation]) -> None:
    """Nothing interpolates during a hold, so an easing would be misleading."""
    with pytest.raises(TypeError):
        hold(duration=1.0, easing=EaseOutBack())


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda: FlickerIn(
            flickers=unchecked(2.5)), id="flickers"),
        pytest.param(lambda: Shake(shakes=unchecked(2.5)), id="shakes"),
        pytest.param(lambda: Jelly(wobbles=unchecked(2.5)), id="wobbles"),
    ],
)
def test_fractional_count_is_rejected_with_the_whole_number_message(
        factory: Factory) -> None:
    """A count of 2.5 must raise the same friendly error as a count of 0."""
    with pytest.raises(ValueError, match="whole number"):
        factory()


@pytest.mark.parametrize("duration", [float("nan"), float("inf")], ids=["nan", "inf"])
def test_non_finite_duration_is_rejected(duration: float) -> None:
    """A duration that is not a finite number cannot be rendered as CSS."""
    with pytest.raises(ValueError, match="duration"):
        FadeIn(duration=duration)
