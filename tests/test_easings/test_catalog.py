"""Consistency tests for the easing catalogues in ``shared.py``.

These tests protect the suite itself: they fail when a new easing is exported
but never registered, or when a catalogue refers to something that does not
exist.
"""

import inspect
from collections.abc import Mapping

import pytest
import svgblock
from svgblock import Easing

from .shared import (
    EVERY_EASING,
    FAMILIES,
    JUMPS_AT_START,
    MIRROR_PAIRS,
    NON_MONOTONIC,
    OVERSHOOTING,
    SELF_MIRRORED,
    Catalog,
)


def exported_easing_types() -> set[type[Easing]]:
    """Collect the concrete easing classes exported by the public API.

    Returns
    -------
    set[type[Easing]]
        Every non-abstract ``Easing`` subclass listed in ``svgblock.__all__``.
    """
    exported = (getattr(svgblock, name) for name in svgblock.__all__)
    return {
        candidate for candidate in exported
        if inspect.isclass(candidate)
        and issubclass(candidate, Easing)
        and not inspect.isabstract(candidate)
    }


def test_every_exported_easing_is_registered() -> None:
    """Every exported easing class must have at least one catalogue entry."""
    registered = {type(easing) for easing in EVERY_EASING.values()}

    missing = {cls.__name__ for cls in exported_easing_types() - registered}

    assert not missing, f"easings missing from shared.py: {sorted(missing)}"


def test_every_easing_belongs_to_exactly_one_family() -> None:
    """Families must not overlap, otherwise ``EVERY_EASING`` loses entries."""
    total = sum(len(family) for family in FAMILIES.values())

    assert len(EVERY_EASING) == total


@pytest.mark.parametrize(
    "catalog",
    [SELF_MIRRORED, OVERSHOOTING, NON_MONOTONIC, JUMPS_AT_START],
    ids=["SELF_MIRRORED", "OVERSHOOTING", "NON_MONOTONIC", "JUMPS_AT_START"],
)
def test_trait_collections_only_hold_registered_easings(
    catalog: Catalog,
) -> None:
    """Trait collections must be subsets of ``EVERY_EASING``."""
    unknown = set(catalog) - set(EVERY_EASING)
    assert not unknown, f"not registered in any family: {sorted(unknown)}"


def test_overshooting_easings_are_not_monotonic() -> None:
    """Leaving the unit interval and returning implies reversing direction."""
    assert set(OVERSHOOTING) <= set(NON_MONOTONIC)


@pytest.mark.parametrize(
    "pairs", [MIRROR_PAIRS], ids=["MIRROR_PAIRS"])
def test_mirror_pairs_only_hold_registered_easings(
    pairs: Mapping[str, tuple[Easing, Easing]],
) -> None:
    """Both members of every mirror pair must be registered."""
    members = {repr(member) for pair in pairs.values() for member in pair}
    unknown = members - set(EVERY_EASING)
    assert not unknown, f"not registered in any family: {sorted(unknown)}"
