"""``Steps``: validation, mirroring and the shape of each jump mode."""

import math
from typing import Literal

import pytest
from svgblock import Steps

from .shared import timing_function, unchecked

Jump = Literal["start", "end", "none", "both"]

JUMPS: list[Jump] = ["start", "end", "none", "both"]
PROBES = (0.1, 0.3, 0.6, 0.9)


@pytest.mark.parametrize("count", [1, 2, 4, 100])
def test_count_accepts_whole_numbers_of_one_or_more(count: int) -> None:
    """A step count is a positive whole number."""
    assert Steps(count).count == count


@pytest.mark.parametrize("count", [0, -1, -10])
def test_count_below_one_is_rejected(count: int) -> None:
    """Zero or negative counts cannot divide the animation into steps."""
    with pytest.raises(ValueError, match="count"):
        Steps(count)


@pytest.mark.parametrize("count", [True, False], ids=["True", "False"])
def test_count_rejects_booleans(count: bool) -> None:
    """``bool`` is an ``int`` subclass but is never a meaningful count."""
    with pytest.raises(ValueError, match="count"):
        Steps(count)


@pytest.mark.parametrize(
    "count", [2.5, 3.0, math.nan, math.inf], ids=["2.5", "3.0", "nan", "inf"])
def test_count_rejects_values_that_are_not_integers(count: float) -> None:
    """CSS requires an integer count, so the constructor must enforce it."""
    with pytest.raises(ValueError, match="count"):
        Steps(unchecked(count))


def test_jump_defaults_to_end() -> None:
    """Omitting ``jump`` matches the CSS default."""
    assert Steps(3).jump == "end"


@pytest.mark.parametrize("jump", JUMPS)
def test_jump_accepts_every_documented_mode(jump: Jump) -> None:
    """All four jump modes are valid for a count of at least two."""
    assert Steps(2, jump).jump == jump


@pytest.mark.parametrize(
    "jump", ["middle", "", "END", "jump-end", None],
    ids=["middle", "empty", "uppercase", "css-prefixed", "None"])
def test_unknown_jump_is_rejected(jump: object) -> None:
    """Only the four documented keywords are accepted."""
    with pytest.raises(ValueError, match="jump"):
        Steps(3, unchecked(jump))


def test_jump_none_requires_at_least_two_steps() -> None:
    """With ``jump-none`` a single step would divide by zero jumps."""
    with pytest.raises(ValueError, match="count"):
        Steps(1, "none")


def test_jump_none_accepts_two_steps() -> None:
    """Two is the smallest valid count for ``jump-none``."""
    assert Steps(2, "none").count == 2


@pytest.mark.parametrize(
    "jump", ["start", "end", "both"])
def test_single_step_is_valid_for_the_other_jumps(jump: Jump) -> None:
    """One step is a plain jump, valid unless ``jump`` is ``none``."""
    assert Steps(1, jump).count == 1


@pytest.mark.parametrize(
    ("jump", "expected"),
    [("start", "end"), ("end", "start"), ("none", "none"), ("both", "both")],
)
def test_mirrored_swaps_start_and_end_and_keeps_count(
    jump: Jump, expected: Jump,
) -> None:
    """Reversing time turns a jump at the start into one at the end."""
    assert Steps(4, jump).mirrored() == Steps(4, expected)


@pytest.mark.parametrize(
    ("jump", "expected"),
    [
        ("end", [0.0, 0.25, 0.5, 0.75]),
        ("start", [0.25, 0.5, 0.75, 1.0]),
        ("none", [0.0, 1 / 3, 2 / 3, 1.0]),
        ("both", [0.2, 0.4, 0.6, 0.8]),
    ],
)
def test_four_steps_produce_the_expected_levels(
    jump: Jump, expected: list[float],
) -> None:
    """Each mode holds its levels over the quarters of the animation."""
    progress = timing_function(Steps(4, jump))

    assert [progress(t) for t in PROBES] == pytest.approx(expected)


@pytest.mark.parametrize(
    ("jump", "expected"),
    [("end", 0.0), ("start", 1.0), ("both", 0.5)],
)
def test_single_step_holds_one_level_until_the_end(
    jump: Jump, expected: float,
) -> None:
    """With one step the output stays flat and only jumps at an end."""
    progress = timing_function(Steps(1, jump))

    assert progress(0.5) == expected
    assert progress(1.0) == 1.0


def test_two_steps_without_end_jumps_split_the_animation_in_half() -> None:
    """``jump-none`` with two steps is 0 for the first half, 1 for the rest."""
    progress = timing_function(Steps(2, "none"))

    assert (progress(0.25), progress(0.75)) == (0.0, 1.0)


@pytest.mark.parametrize("jump", JUMPS)
def test_every_mode_finishes_at_one(jump: Jump) -> None:
    """Whatever the jump mode, the animation ends at full progress."""
    assert timing_function(Steps(4, jump))(1.0) == 1.0


def test_equal_arguments_make_equal_easings() -> None:
    """Easings are value objects, and ``end`` is the default jump."""
    assert Steps(3) == Steps(3, "end")
    assert hash(Steps(3)) == hash(Steps(3, "end"))


def test_different_jump_makes_a_different_easing() -> None:
    """The jump mode takes part in equality."""
    assert Steps(3, "start") != Steps(3)
