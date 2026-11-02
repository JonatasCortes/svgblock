"""Behaviour of entrance and exit animations."""

from typing import Literal

import pytest

from svgblock import (
    BaseAnimation,
    DropIn,
    DropOut,
    EaseIn,
    EaseInCubic,
    EaseInQuint,
    EaseOut,
    EaseOutCubic,
    EaseOutQuint,
    FadeIn,
    FadeOut,
    FlickerIn,
    FlickerOut,
    FlipIn,
    FlipOut,
    FocusIn,
    FocusOut,
    GlitchIn,
    GlitchOut,
    PopIn,
    PopOut,
    RiseIn,
    RiseOut,
    SlideIn,
    SlideOut,
    SpinIn,
    SpinOut,
    UnfoldIn,
    UnfoldOut,
    ZoomIn,
    ZoomOut,
)
from tests.test_animations.shared import (
    ENTRANCES,
    EXITS,
    FADING_ENTRANCE_FACTORIES,
    FADING_EXIT_FACTORIES,
    SELF_EASED_EFFECTS,
    AnimationFactory,
    count_dips,
    each,
    each_factory,
    is_at_rest,
    peaks,
)

DECELERATING = (EaseOut, EaseOutQuint, EaseOutCubic)
ACCELERATING = (EaseIn, EaseInQuint, EaseInCubic)


@each(ENTRANCES)
def test_entrance_ends_in_the_natural_state(animation: BaseAnimation) -> None:
    """After an entrance the element must look exactly as authored."""
    assert is_at_rest(animation.keyframes()[-1].pose)


@each(ENTRANCES)
def test_entrance_starts_away_from_the_natural_state(
        animation: BaseAnimation) -> None:
    """An entrance that starts at rest would animate nothing."""
    assert not is_at_rest(animation.keyframes()[0].pose)


@each(EXITS)
def test_exit_starts_from_the_natural_state(animation: BaseAnimation) -> None:
    """An exit must begin from the element as authored, without a jump."""
    assert is_at_rest(animation.keyframes()[0].pose)


@each(EXITS)
def test_exit_ends_away_from_the_natural_state(animation: BaseAnimation) -> None:
    """An exit that ends at rest would animate nothing."""
    assert not is_at_rest(animation.keyframes()[-1].pose)


@each({k: v for k, v in ENTRANCES.items() if k not in SELF_EASED_EFFECTS})
def test_entrance_default_easing_decelerates(animation: BaseAnimation) -> None:
    """Entrances should arrive softly, so their default easing eases out."""
    assert isinstance(animation.easing, DECELERATING)


@each({k: v for k, v in EXITS.items() if k not in SELF_EASED_EFFECTS})
def test_exit_default_easing_accelerates(animation: BaseAnimation) -> None:
    """Exits should leave gently and speed up, so their default easing eases in."""
    assert isinstance(animation.easing, ACCELERATING)


@pytest.mark.parametrize(
    ("entrance", "exit_"),
    [
        pytest.param(FadeIn(), FadeOut(), id="fade"),
        pytest.param(FocusIn(), FocusOut(), id="focus"),
        pytest.param(ZoomIn(), ZoomOut(), id="zoom"),
        pytest.param(FlipIn(), FlipOut(), id="flip"),
        pytest.param(UnfoldIn(), UnfoldOut(), id="unfold"),
        pytest.param(PopIn(), PopOut(), id="pop"),
        pytest.param(FlickerIn(), FlickerOut(), id="flicker"),
        pytest.param(GlitchIn(), GlitchOut(), id="glitch"),
    ],
)
def test_exit_ends_in_the_state_its_entrance_starts_from(
        entrance: BaseAnimation, exit_: BaseAnimation) -> None:
    """Symmetric effects must disappear into the state they appear from."""
    assert exit_.keyframes()[-1].pose == entrance.keyframes()[0].pose


@pytest.mark.parametrize(
    ("entrance", "exit_"),
    [
        pytest.param(PopIn(), PopOut(), id="pop"),
        pytest.param(FlickerIn(), FlickerOut(), id="flicker"),
        pytest.param(GlitchIn(), GlitchOut(), id="glitch"),
    ],
)
def test_exit_of_a_scripted_effect_is_its_entrance_played_backwards(
        entrance: BaseAnimation, exit_: BaseAnimation) -> None:
    """Pop, flicker and glitch exits must mirror their entrance frame by frame."""
    forward = entrance.keyframes()
    backward = exit_.keyframes()

    assert [frame.pose for frame in backward] == [
        frame.pose for frame in reversed(forward)]
    assert [frame.at for frame in backward] == pytest.approx(
        [1 - frame.at for frame in reversed(forward)])


@pytest.mark.parametrize(
    ("entrance", "exit_", "displacement"),
    [
        pytest.param(RiseIn(distance=30), RiseOut(
            distance=30), (0.0, -30.0), id="rise"),
        pytest.param(DropIn(distance=30), DropOut(
            distance=30), (0.0, 30.0), id="drop"),
        pytest.param(SlideIn(distance=30, direction="right"),
                     SlideOut(distance=30, direction="right"), (30.0, 0.0), id="slide-right"),
        pytest.param(SlideIn(distance=30, direction="left"),
                     SlideOut(distance=30, direction="left"), (-30.0, 0.0), id="slide-left"),
    ],
)
def test_entrance_and_exit_move_the_element_in_the_same_direction(
        entrance: BaseAnimation, exit_: BaseAnimation,
        displacement: tuple[float, float]) -> None:
    """Rise, drop and slide describe one direction of motion for both phases."""
    entering = entrance.keyframes()
    leaving = exit_.keyframes()

    assert (entering[-1].pose.x - entering[0].pose.x,
            entering[-1].pose.y - entering[0].pose.y) == pytest.approx(displacement)
    assert (leaving[-1].pose.x - leaving[0].pose.x,
            leaving[-1].pose.y - leaving[0].pose.y) == pytest.approx(displacement)


@pytest.mark.parametrize("distance", [0.0, 12.5, 200.0])
def test_travel_distance_is_the_offset_of_the_hidden_state(distance: float) -> None:
    """``distance`` must be the exact pixel offset the element travels."""
    start = RiseIn(distance=distance).keyframes()[0].pose

    assert abs(start.y) == distance
    assert start.x == 0


@each_factory(FADING_ENTRANCE_FACTORIES)
def test_fading_entrance_starts_transparent_when_fade_is_enabled(
        factory: AnimationFactory) -> None:
    """With ``fade=True`` the element must appear from invisible."""
    frames = factory(fade=True).keyframes()

    assert frames[0].pose.opacity == 0
    assert frames[-1].pose.opacity == 1


@each_factory(FADING_EXIT_FACTORIES)
def test_fading_exit_ends_transparent_when_fade_is_enabled(
        factory: AnimationFactory) -> None:
    """With ``fade=True`` the element must disappear completely."""
    frames = factory(fade=True).keyframes()

    assert frames[0].pose.opacity == 1
    assert frames[-1].pose.opacity == 0


@each_factory({**FADING_ENTRANCE_FACTORIES, **FADING_EXIT_FACTORIES})
def test_element_stays_fully_opaque_when_fade_is_disabled(
        factory: AnimationFactory) -> None:
    """With ``fade=False`` only the motion may change, never the opacity."""
    assert all(frame.pose.opacity ==
               1 for frame in factory(fade=False).keyframes())


@each_factory(FADING_ENTRANCE_FACTORIES)
def test_focus_option_blurs_the_hidden_state_of_an_entrance(
        factory: AnimationFactory) -> None:
    """``focus=True`` must start the entrance blurred and end it sharp."""
    animation = factory(focus=True)
    frames = animation.keyframes()

    assert frames[0].pose.blur > 0
    assert frames[-1].pose.blur == 0
    assert animation.max_blur > 0


@each_factory(FADING_EXIT_FACTORIES)
def test_focus_option_blurs_the_hidden_state_of_an_exit(
        factory: AnimationFactory) -> None:
    """``focus=True`` must start the exit sharp and end it blurred."""
    animation = factory(focus=True)
    frames = animation.keyframes()

    assert frames[0].pose.blur == 0
    assert frames[-1].pose.blur > 0
    assert animation.max_blur > 0


@each_factory({**FADING_ENTRANCE_FACTORIES, **FADING_EXIT_FACTORIES})
def test_blur_is_off_by_default(factory: AnimationFactory) -> None:
    """Blur is costly to render, so it must be opt-in."""
    assert factory().max_blur == 0


def test_fade_in_changes_nothing_but_opacity() -> None:
    """A plain fade must not move, scale, rotate or blur the element."""
    start, end = FadeIn().keyframes()[0].pose, FadeIn().keyframes()[-1].pose

    assert (start.opacity, end.opacity) == (0, 1)
    assert (start.x, start.y, start.scale,
            start.rotate, start.blur) == (0, 0, 1, 0, 0)


def test_fade_out_changes_nothing_but_opacity() -> None:
    """A plain fade must not move, scale, rotate or blur the element."""
    start, end = FadeOut().keyframes()[0].pose, FadeOut().keyframes()[-1].pose

    assert (start.opacity, end.opacity) == (1, 0)
    assert (end.x, end.y, end.scale, end.rotate, end.blur) == (0, 0, 1, 0, 0)


@pytest.mark.parametrize("blur", [2.0, 8.0, 20.0])
def test_focus_in_starts_with_the_requested_blur(blur: float) -> None:
    """``blur`` is the radius in pixels of the out-of-focus starting state."""
    assert FocusIn(blur=blur).keyframes()[0].pose.blur == blur


@pytest.mark.parametrize("blur", [2.0, 8.0, 20.0])
def test_focus_out_ends_with_the_requested_blur(blur: float) -> None:
    """``blur`` is the radius in pixels of the out-of-focus final state."""
    assert FocusOut(blur=blur).keyframes()[-1].pose.blur == blur


def test_focus_in_without_fade_keeps_the_element_opaque() -> None:
    """Disabling the fade must leave focus as the only visible change."""
    assert FocusIn(fade=False).keyframes()[0].pose.opacity == 1


@pytest.mark.parametrize(("scale", "peak"), [(0.5, 1.0), (0.1, 1.0), (2.0, 2.0)])
def test_zoom_in_starts_at_the_requested_scale(scale: float, peak: float) -> None:
    """``scale`` is the size the element zooms from, and sizing reports its peak."""
    animation = ZoomIn(scale=scale)

    assert animation.keyframes()[0].pose.scale == scale
    assert animation.max_scale == peak


def test_zoom_out_ends_at_the_requested_scale() -> None:
    """Zooming out must shrink to the same size zooming in grows from."""
    assert ZoomOut(scale=0.3).keyframes()[-1].pose.scale == 0.3


@pytest.mark.parametrize("angle", [45.0, 90.0, -30.0])
def test_spin_in_and_out_turn_in_the_same_direction(angle: float) -> None:
    """Spin in and spin out must keep turning the same way, as one gesture."""
    entering = SpinIn(angle=angle).keyframes()
    leaving = SpinOut(angle=angle).keyframes()

    assert entering[-1].pose.rotate - \
        entering[0].pose.rotate == pytest.approx(angle)
    assert leaving[-1].pose.rotate - \
        leaving[0].pose.rotate == pytest.approx(angle)


@pytest.mark.parametrize(
    ("axis", "mirrored_scale"),
    [("horizontal", (-1.0, 1.0)), ("vertical", (1.0, -1.0))],
)
def test_flip_in_starts_mirrored_on_the_requested_axis(
        axis: Literal["horizontal", "vertical"],
        mirrored_scale: tuple[float, float]) -> None:
    """A horizontal flip mirrors the x axis, a vertical flip the y axis."""
    pose = FlipIn(axis=axis).keyframes()[0].pose

    assert (pose.scale_x, pose.scale_y) == mirrored_scale


def test_flip_does_not_count_as_an_enlargement() -> None:
    """Mirroring passes through zero width but never grows the element."""
    assert FlipIn().max_scale == 1


@pytest.mark.parametrize(
    ("edge", "origin", "collapsed_scale"),
    [
        ("top", (0.5, 0.0), (1.0, 0.0)),
        ("bottom", (0.5, 1.0), (1.0, 0.0)),
        ("left", (0.0, 0.5), (0.0, 1.0)),
        ("right", (1.0, 0.5), (0.0, 1.0)),
    ],
)
def test_unfold_in_grows_from_the_requested_edge(
        edge: Literal["top", "bottom", "left", "right"],
        origin: tuple[float, float],
        collapsed_scale: tuple[float, float]) -> None:
    """The element must be flat along one axis and anchored to the chosen edge."""
    animation = UnfoldIn(edge=edge)
    pose = animation.keyframes()[0].pose

    assert animation.origins == {origin}
    assert (pose.scale_x, pose.scale_y) == collapsed_scale


@pytest.mark.parametrize("edge", ["top", "bottom", "left", "right"])
def test_unfold_out_collapses_towards_the_edge_it_unfolds_from(
        edge: Literal["top", "bottom", "left", "right"]) -> None:
    """Unfolding in and out must share the same anchor edge."""
    assert UnfoldOut(edge=edge).origins == UnfoldIn(edge=edge).origins


@pytest.mark.parametrize("start_scale", [0.5, 0.8, 0.95])
def test_pop_in_starts_at_the_requested_scale(start_scale: float) -> None:
    """``start_scale`` is the size the pop begins from."""
    assert PopIn(start_scale=start_scale).keyframes()[
        0].pose.scale == start_scale


@pytest.mark.parametrize("animation", [PopIn(), PopOut(), PopIn(start_scale=0.2)],
                         ids=["in", "out", "small-start"])
def test_pop_never_exceeds_the_natural_size(animation: BaseAnimation) -> None:
    """A pop is meant to be subtle: it must never overshoot the authored size."""
    assert max(frame.pose.scale for frame in animation.keyframes()) <= 1


def test_pop_in_swells_to_full_size_then_dips_once_before_settling() -> None:
    """The pop's soft landing is a single dip between full size and rest."""
    scales = [frame.pose.scale for frame in PopIn().keyframes()]

    assert count_dips(scales) == 1


@pytest.mark.parametrize("flickers", [1, 3, 8])
def test_flicker_in_flashes_as_many_times_as_requested(flickers: int) -> None:
    """Each requested flicker must appear as exactly one dip in opacity."""
    opacities = [frame.pose.opacity for frame in FlickerIn(
        flickers=flickers).keyframes()]

    assert count_dips(opacities) == flickers


@pytest.mark.parametrize("flickers", [2, 3, 8])
def test_flicker_in_flashes_get_brighter_until_the_light_stabilises(
        flickers: int) -> None:
    """Every flash must be brighter than the previous one."""
    opacities = [frame.pose.opacity for frame in FlickerIn(
        flickers=flickers).keyframes()]
    flashes = peaks(opacities)

    assert len(flashes) == flickers
    assert all(earlier < later for earlier, later in zip(flashes, flashes[1:]))


@pytest.mark.parametrize("flickers", [1, 3, 8, 50])
def test_flicker_in_keyframes_never_collide_even_with_many_flickers(
        flickers: int) -> None:
    """Many flickers must still produce strictly ordered, distinct keyframes."""
    times = [frame.at for frame in FlickerIn(flickers=flickers).keyframes()]

    assert all(earlier < later for earlier, later in zip(times, times[1:]))


@pytest.mark.parametrize("intensity", [4.0, 12.0, 30.0])
def test_glitch_in_peak_displacement_equals_the_requested_intensity(
        intensity: float) -> None:
    """``intensity`` is the maximum horizontal jitter, in pixels."""
    offsets = [abs(frame.pose.x)
               for frame in GlitchIn(intensity=intensity).keyframes()]

    assert max(offsets) == pytest.approx(intensity)


def test_glitch_in_has_settled_before_its_final_frame() -> None:
    """The jitter must stop before the end, so the last step is not a visible jump."""
    assert is_at_rest(GlitchIn().keyframes()[-2].pose)
