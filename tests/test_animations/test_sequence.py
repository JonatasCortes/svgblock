"""Behaviour of ``Sequence``: chaining, timeline compilation and repetition."""

from dataclasses import FrozenInstanceError
import pytest
from svgblock import (
    BaseAnimation,
    EaseInCubic,
    EaseInOut,
    EaseOutCubic,
    EaseOutQuint,
    FadeIn,
    FadeOut,
    Float,
    FocusIn,
    FocusOut,
    Hide,
    Linear,
    PopIn,
    Pulse,
    RiseIn,
    Rotate,
    Sequence,
    Shake,
    Show,
)


def _intro_hold_outro() -> Sequence:
    return Sequence(
        FadeIn(duration=1.0), Show(duration=2.0), FadeOut(duration=1.0))


def test_duration_is_the_sum_of_the_step_durations() -> None:
    """The sequence lasts as long as its steps played back to back."""
    assert _intro_hold_outro().duration == pytest.approx(4.0)


def test_steps_are_kept_in_the_order_given() -> None:
    """Order defines playback order, so it must be preserved."""
    first, second = FadeIn(), FadeOut()

    assert Sequence(first, second).steps == (first, second)


def test_sequence_cannot_be_mutated_after_creation() -> None:
    """Its CSS name is derived from its parameters, so they must stay fixed."""
    with pytest.raises(FrozenInstanceError):
        setattr(_intro_hold_outro(), "loop_limit", 5)


def test_sequence_easing_is_linear_so_each_step_keeps_its_own_timing() -> None:
    """A non-linear sequence easing would distort every step inside it."""
    sequence = _intro_hold_outro()

    assert isinstance(sequence.easing, Linear)
    assert isinstance(sequence.layers()[0].easing, Linear)


def test_empty_sequence_plays_nothing() -> None:
    """An empty sequence is a harmless no-op, not an error."""
    empty = Sequence()

    assert empty.duration == 0
    assert empty.keyframes() == []
    assert empty.layers() == []


def test_empty_sequence_expands_to_no_segments_and_is_not_infinite() -> None:
    """Expanding nothing must give nothing, even when asked to loop forever."""
    expansion = Sequence(loop_limit=None).expand()

    assert expansion.head == ()
    assert expansion.cycle is None
    assert not Sequence(loop_limit=None).is_infinite


def test_empty_sequence_needs_no_room() -> None:
    """With no steps there is nothing to scale, blur or move."""
    empty = Sequence()

    assert empty.max_scale == 1
    assert empty.max_blur == 0
    assert empty.margins(100.0, 50.0) == (0, 0, 0, 0)


def test_keyframes_cover_the_timeline_in_order() -> None:
    """The compiled timeline must start at 0, end at 1 and never go backwards."""
    times = [frame.at for frame in _intro_hold_outro().keyframes()]

    assert times[0] == 0
    assert times[-1] == pytest.approx(1)
    assert times == sorted(times)


def test_every_step_keyframe_is_present_in_the_compiled_timeline() -> None:
    """Compilation must neither drop nor invent keyframes."""
    assert len(_intro_hold_outro().keyframes()) == 6


def test_each_step_starts_at_the_fraction_of_time_elapsed_before_it() -> None:
    """Steps of 1s, 2s and 1s must start at 0%, 25% and 75% of the timeline."""
    frames = _intro_hold_outro().keyframes()

    assert frames[0].at == 0
    assert frames[2].at == pytest.approx(0.25)
    assert frames[4].at == pytest.approx(0.75)


def test_a_step_ends_just_before_the_next_one_starts_so_the_cut_is_instant() -> None:
    """Consecutive steps must not overlap, nor leave a visible blend between them."""
    frames = _intro_hold_outro().keyframes()
    gap = frames[2].at - frames[1].at

    assert 0 < gap < 1e-3


def test_steps_that_do_not_match_at_their_boundary_cut_instead_of_blending() -> None:
    """A fade-in followed by a fade-in must restart from transparent, not blend."""
    frames = Sequence(FadeIn(duration=1.0), FadeIn(duration=1.0)).keyframes()
    around_cut = [frame for frame in frames if abs(frame.at - 0.5) < 1e-3]

    assert [frame.pose.opacity for frame in around_cut] == [1, 0]


def test_each_step_keeps_the_easing_it_was_created_with() -> None:
    """Easing is per step; the sequence must not flatten them into one curve."""
    frames = Sequence(
        FadeIn(duration=1.0, easing=EaseInCubic()),
        FadeOut(duration=1.0, easing=EaseOutCubic()),
    ).keyframes()

    assert isinstance(frames[0].easing, EaseInCubic)
    assert isinstance(frames[2].easing, EaseOutCubic)


def test_keyframe_level_easing_of_a_step_is_preserved() -> None:
    """Steps like Pop ease some keyframes individually; that must survive."""
    frames = Sequence(PopIn()).keyframes()

    assert isinstance(frames[0].easing, EaseOutQuint)
    assert isinstance(frames[1].easing, EaseInOut)


def test_hide_step_keeps_the_element_invisible_before_the_next_step() -> None:
    """Hide is the way to delay an entrance inside a sequence."""
    frames = Sequence(Hide(duration=1.0), FadeIn(duration=1.0)).keyframes()
    before_the_entrance = [frame for frame in frames if frame.at < 0.5 - 1e-3]

    assert all(frame.pose.opacity == 0 for frame in before_the_entrance)
    assert frames[-1].pose.opacity == 1


def test_nested_sequence_plays_exactly_like_its_steps_written_flat() -> None:
    """Grouping steps in a sub-sequence must not change the timeline."""
    intro, hold, outro = FadeIn(duration=1.0), Show(
        duration=2.0), FadeOut(duration=1.0)
    nested = Sequence(Sequence(intro, hold), outro)
    flat = Sequence(intro, hold, outro)

    assert nested.duration == flat.duration
    assert [(frame.at, frame.pose) for frame in nested.keyframes()] == [
        (frame.at, frame.pose) for frame in flat.keyframes()]


def test_inner_finite_loop_is_unrolled_into_the_duration() -> None:
    """A step that repeats 3 times must count 3 times towards the duration."""
    sequence = Sequence(Pulse(duration=2.0, loop_limit=2))

    assert sequence.duration == pytest.approx(6.0)
    assert sequence.layers()[0].iterations == 1


def test_sequence_loop_limit_replays_the_whole_sequence() -> None:
    """``loop_limit=2`` plays the whole sequence three times."""
    sequence = Sequence(FadeIn(duration=1.0), Show(duration=2.0), loop_limit=2)
    layer = sequence.layers()[0]

    assert layer.duration == pytest.approx(3.0)
    assert layer.iterations == 3
    assert sequence.expand().playing_time == pytest.approx(9.0)


def test_sequence_without_loops_is_not_infinite_and_plays_once() -> None:
    """Looping is opt-in for sequences too."""
    sequence = _intro_hold_outro()

    assert not sequence.is_infinite
    assert sequence.layers()[0].iterations == 1


def test_sequence_with_loop_limit_none_repeats_forever_in_one_layer() -> None:
    """Looping a finite sequence forever needs only one endless layer."""
    sequence = Sequence(FadeIn(duration=1.0), Show(
        duration=1.0), loop_limit=None)
    layers = sequence.layers()

    assert sequence.is_infinite
    assert len(layers) == 1
    assert layers[0].iterations is None


@pytest.mark.parametrize("loop_limit", [-1, 1001])
def test_sequence_rejects_a_loop_limit_outside_the_supported_range(
        loop_limit: int) -> None:
    """Sequences share the loop limit contract of the looping animations."""
    with pytest.raises(ValueError, match="loop_limit must be"):
        Sequence(FadeIn(), loop_limit=loop_limit)


def test_infinite_last_step_is_split_into_an_intro_layer_and_a_loop_layer() -> None:
    """The head plays once, then a second layer takes over and loops forever."""
    sequence = Sequence(FadeIn(duration=1.0), Pulse(
        duration=2.0, loop_limit=None))
    head, loop = sequence.layers()

    assert sequence.is_infinite
    assert head.iterations == 1
    assert loop.iterations is None
    assert loop.name != head.name
    assert loop.name.startswith(head.name)


def test_loop_layer_starts_exactly_when_the_intro_layer_ends() -> None:
    """Any gap or overlap would be a visible hiccup between intro and loop."""
    head, loop = Sequence(
        FadeIn(duration=1.0), Pulse(duration=2.0, loop_limit=None)).layers()

    assert loop.delay == pytest.approx(head.duration)


def test_loop_layer_does_not_apply_its_first_frame_before_it_starts() -> None:
    """Backwards fill would override the intro's final pose during the delay."""
    _, loop = Sequence(FadeIn(duration=1.0), Pulse(loop_limit=None)).layers()

    assert loop.fill in ("forwards", "none")


def test_sequence_made_only_of_an_endless_loop_has_a_single_undelayed_layer() -> None:
    """With no intro there is nothing to wait for."""
    layers = Sequence(Pulse(loop_limit=None)).layers()

    assert len(layers) == 1
    assert layers[0].iterations is None
    assert layers[0].delay == 0


def test_nested_endless_sequence_makes_the_outer_sequence_endless_too() -> None:
    """Endlessness must propagate outwards through grouping."""
    sequence = Sequence(FadeIn(), Sequence(Pulse(loop_limit=None)))

    assert sequence.is_infinite
    assert len(sequence.layers()) == 2


@pytest.mark.parametrize(
    "later_step",
    [
        pytest.param(FadeOut(), id="finite-step"),
        pytest.param(Float(loop_limit=None), id="another-endless-step"),
        pytest.param(Sequence(FadeOut()), id="nested-sequence"),
    ],
)
def test_step_placed_after_an_endless_step_is_rejected(
        later_step: BaseAnimation) -> None:
    """It could never play, so silently accepting it would hide a mistake."""
    with pytest.raises(ValueError, match="never play"):
        Sequence(Pulse(loop_limit=None), later_step)


def test_empty_sequence_after_an_endless_step_is_allowed() -> None:
    """An empty step plays nothing, so it cannot be 'unreachable'."""
    assert Sequence(Pulse(loop_limit=None), Sequence()).is_infinite


def test_unrolling_too_many_repetitions_is_rejected() -> None:
    """Ten steps of 1001 plays would exceed the CSS size the library allows."""
    with pytest.raises(ValueError, match="repeats too much"):
        Sequence(*[Pulse(loop_limit=1000)] * 10)


def test_moderate_repetition_is_accepted() -> None:
    """Typical loop counts must not trip the safety limit."""
    assert Sequence(*[Pulse(loop_limit=50)] * 10).duration > 0


def test_nested_repetition_that_multiplies_past_the_limit_is_rejected() -> None:
    """Loops inside loops multiply, and the product is what gets rendered."""
    inner = Sequence(Pulse(loop_limit=1000), loop_limit=1000)

    with pytest.raises(ValueError, match="repeats too much"):
        Sequence(inner)


def test_expanding_a_sequence_whose_repetitions_exceed_the_limit_is_rejected() -> None:
    """Expansion is where a sequence's loops are unrolled, so it enforces the limit."""
    with pytest.raises(ValueError, match="repeats too much"):
        Sequence(Pulse(loop_limit=1000), loop_limit=1000).expand()


def test_sequence_cannot_be_played_as_a_single_segment() -> None:
    """A sequence is made of segments; asking for one would lose its structure."""
    with pytest.raises(TypeError, match="expanded"):
        Sequence(FadeIn()).segment()


def test_scale_and_blur_requirements_are_the_largest_of_any_step() -> None:
    """Steps never overlap, so the demands of the hungriest step suffice."""
    sequence = Sequence(
        Pulse(amount=0.1), Pulse(amount=0.3), FocusIn(blur=4.0), FocusOut(blur=10.0))

    assert sequence.max_scale == pytest.approx(1.3)
    assert sequence.max_blur == pytest.approx(10.0)


def test_margins_are_the_per_side_maximum_over_all_steps() -> None:
    """Room is reused between steps, not added up."""
    steps = (Float(amount=8.0), Float(amount=12.0),
             Shake(amount=6.0), Shake(amount=12.0))
    per_step = [step.margins(100.0, 50.0) for step in steps]
    expected = tuple(max(side) for side in zip(*per_step))

    assert Sequence(*steps).margins(100.0, 50.0) == pytest.approx(expected)


@pytest.mark.parametrize(
    "step",
    [Float(amount=8.0), Shake(amount=12.0), Rotate(angle=90.0)],
    ids=["vertical", "horizontal", "rotating"],
)
def test_repeating_the_same_step_does_not_increase_the_margins(
        step: BaseAnimation) -> None:
    """Two identical steps one after the other need no more room than one."""
    assert Sequence(step, step).margins(100.0, 50.0) == pytest.approx(
        step.margins(100.0, 50.0))


def test_css_name_depends_on_the_steps() -> None:
    """Different sequences must not share a CSS class."""
    assert Sequence(FadeIn()).css_name != Sequence(RiseIn()).css_name


def test_css_name_is_identical_for_equal_sequences() -> None:
    """Rebuilding the same sequence must reproduce the same CSS class."""
    assert Sequence(FadeIn(), Show(duration=1.0)).css_name == Sequence(
        FadeIn(), Show(duration=1.0)).css_name


def test_iterations_is_none_when_an_inner_step_is_endless() -> None:
    """Consumers reading ``iterations`` must not be told the sequence plays once."""
    sequence = Sequence(FadeIn(), Pulse(loop_limit=None))

    assert sequence.is_infinite
    assert sequence.iterations is None
