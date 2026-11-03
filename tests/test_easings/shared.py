"""Shared catalogues, helpers and a timing function evaluator for easing tests.

Easings are described only through the public API of ``svgblock``. To check the
behaviour a user actually receives, the evaluator below turns the output of
``Easing.css()`` into a plain ``f(t)`` function that follows the CSS Easing
specification, so the tests never reach into private attributes.

Registering a new easing takes one step: import it and add it to the family
collection it belongs to. The collections that describe special traits
(``MIRROR_PAIRS``, ``SELF_MIRRORED``, ``OVERSHOOTING``, ``NON_MONOTONIC``) only
need an entry when the new easing has that trait.
"""

import math
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import pytest
from svgblock import (
    Bounce,
    CubicBezier,
    EaseIn,
    EaseInBack,
    EaseInCirc,
    EaseInCubic,
    EaseInExpo,
    EaseInOut,
    EaseInOutBack,
    EaseInOutCirc,
    EaseInOutCubic,
    EaseInOutExpo,
    EaseInOutQuint,
    EaseInOutSine,
    EaseInQuint,
    EaseInSine,
    EaseOut,
    EaseOutBack,
    EaseOutCirc,
    EaseOutCubic,
    EaseOutExpo,
    EaseOutQuint,
    EaseOutSine,
    Easing,
    Linear,
    Spring,
    Steps,
)

Catalog = dict[str, Easing]
MirrorPair = tuple[Easing, Easing]
TimingFunction = Callable[[float], float]

SAMPLE_POINTS: tuple[float, ...] = tuple(
    (2 * index + 1) / 64 for index in range(32))
"""Odd multiples of 1/64, which never fall on a step boundary of ``Steps``
easings whose count is below 64, where the mirror identity is ambiguous."""

TOLERANCE = 2e-4
"""Absolute tolerance that absorbs the four decimal rounding of ``linear()``."""

_BISECTION_STEPS = 50

_NUMBER = r"[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?"
_NUMBER_PATTERN = re.compile(_NUMBER)
_CUBIC_BEZIER_CALL = re.compile(
    rf"cubic-bezier\(({_NUMBER}),\s*({_NUMBER}),\s*({_NUMBER}),\s*({_NUMBER})\)")
_STEPS_CALL = re.compile(
    r"steps\((\d+)(?:,\s*(jump-start|jump-end|jump-none|jump-both|start|end))?\)")
_LINEAR_CALL = re.compile(rf"linear\(({_NUMBER}(?:,\s*{_NUMBER})+)\)")

_KEYWORD_BEZIERS: dict[str, tuple[float, float, float, float]] = {
    "ease": (0.25, 0.1, 0.25, 1.0),
    "ease-in": (0.42, 0.0, 1.0, 1.0),
    "ease-out": (0.0, 0.0, 0.58, 1.0),
    "ease-in-out": (0.42, 0.0, 0.58, 1.0),
}


def collect(*easings: Easing) -> Catalog:
    """Build a catalogue keyed by the ``repr`` of each easing.

    Parameters
    ----------
    *easings : Easing
        Easings to register.

    Returns
    -------
    dict[str, Easing]
        Easings keyed by a unique, human readable test id.

    Raises
    ------
    ValueError
        If two easings share the same ``repr``.
    """
    catalog: Catalog = {}
    for easing in easings:
        key = repr(easing)
        if key in catalog:
            raise ValueError(f"duplicated easing in catalogue: {key}")
        catalog[key] = easing
    return catalog


def pair_up(*pairs: MirrorPair) -> dict[str, MirrorPair]:
    """Build a catalogue of mirror pairs keyed by both ``repr`` values.

    Parameters
    ----------
    *pairs : tuple[Easing, Easing]
        Pairs of easings that must mirror each other.

    Returns
    -------
    dict[str, tuple[Easing, Easing]]
        Pairs keyed by a unique, human readable test id.

    Raises
    ------
    ValueError
        If two pairs share the same id.
    """
    catalog: dict[str, MirrorPair] = {}
    for first, second in pairs:
        key = f"{first!r} <-> {second!r}"
        if key in catalog:
            raise ValueError(f"duplicated pair in catalogue: {key}")
        catalog[key] = (first, second)
    return catalog


def excluding(
    source: Mapping[str, Easing], excluded: Mapping[str, Easing]
) -> Catalog:
    """Return the entries of a catalogue that are absent from another one.

    Parameters
    ----------
    source : Mapping[str, Easing]
        Catalogue to filter.
    excluded : Mapping[str, Easing]
        Catalogue whose keys are removed from ``source``.

    Returns
    -------
    dict[str, Easing]
        Entries of ``source`` whose key is not in ``excluded``.
    """
    return {key: easing for key, easing in source.items()
            if key not in excluded}


KEYWORDS: Catalog = collect(Linear(), EaseIn(), EaseOut(), EaseInOut())

BACK_PRESETS: Catalog = collect(
    EaseInBack(), EaseOutBack(), EaseInOutBack())

PRESETS: Catalog = collect(
    EaseInSine(), EaseOutSine(), EaseInOutSine(),
    EaseInCubic(), EaseOutCubic(), EaseInOutCubic(),
    EaseInQuint(), EaseOutQuint(), EaseInOutQuint(),
    EaseInExpo(), EaseOutExpo(), EaseInOutExpo(),
    EaseInCirc(), EaseOutCirc(), EaseInOutCirc(),
    *BACK_PRESETS.values(),
)

OVERSHOOTING_BEZIERS: Catalog = collect(CubicBezier(0.5, -0.5, 0.5, 1.5))

CUBIC_BEZIERS: Catalog = {
    **collect(
        CubicBezier(0.25, 0.1, 0.25, 1),
        CubicBezier(0.75, 0, 0.75, 0.9),
        CubicBezier(0.55, 0.085, 0.68, 0.53),
        CubicBezier(0, 0, 1, 1),
    ),
    **OVERSHOOTING_BEZIERS,
}

STEPPED: Catalog = collect(
    Steps(1), Steps(1, "start"),
    Steps(4), Steps(4, "start"), Steps(4, "none"), Steps(4, "both"),
    Steps(2, "none"),
)

SPRINGS: Catalog = collect(
    Spring(), Spring(0.25), Spring(0.9), Spring().mirrored())

BOUNCES: Catalog = collect(
    Bounce(), Bounce(1), Bounce(5, 0.3), Bounce().mirrored())

CURVES: Catalog = {**SPRINGS, **BOUNCES}

FAMILIES: dict[str, Catalog] = {
    "keywords": KEYWORDS,
    "presets": PRESETS,
    "cubic_beziers": CUBIC_BEZIERS,
    "stepped": STEPPED,
    "curves": CURVES,
}

EVERY_EASING: Catalog = {
    key: easing
    for family in FAMILIES.values()
    for key, easing in family.items()
}

MIRROR_PAIRS: dict[str, MirrorPair] = pair_up(
    (EaseIn(), EaseOut()),
    (EaseInSine(), EaseOutSine()),
    (EaseInCubic(), EaseOutCubic()),
    (EaseInQuint(), EaseOutQuint()),
    (EaseInExpo(), EaseOutExpo()),
    (EaseInCirc(), EaseOutCirc()),
    (EaseInBack(), EaseOutBack()),
    (CubicBezier(0.25, 0.1, 0.25, 1), CubicBezier(0.75, 0, 0.75, 0.9)),
    (Steps(1), Steps(1, "start")),
    (Steps(4), Steps(4, "start")),
)

SELF_MIRRORED: Catalog = collect(
    Linear(), EaseInOut(),
    EaseInOutSine(), EaseInOutCubic(), EaseInOutQuint(),
    EaseInOutExpo(), EaseInOutCirc(), EaseInOutBack(),
    CubicBezier(0, 0, 1, 1), CubicBezier(0.5, -0.5, 0.5, 1.5),
    Steps(2, "none"), Steps(4, "none"), Steps(4, "both"),
)

OVERSHOOTING: Catalog = {
    **BACK_PRESETS,
    **OVERSHOOTING_BEZIERS,
    **SPRINGS,
}

NON_MONOTONIC: Catalog = {**OVERSHOOTING, **BOUNCES}

MONOTONIC: Catalog = excluding(EVERY_EASING, NON_MONOTONIC)

NON_OVERSHOOTING: Catalog = excluding(EVERY_EASING, OVERSHOOTING)

JUMPS_AT_START: Catalog = {
    key: easing
    for key, easing in STEPPED.items()
    if isinstance(easing, Steps) and easing.jump in ("start", "both")
}

STARTS_AT_ZERO: Catalog = excluding(EVERY_EASING, JUMPS_AT_START)


def each(catalog: Mapping[str, Easing]) -> pytest.MarkDecorator:
    """Parametrize a test over ``easing`` using the catalogue keys as ids.

    Parameters
    ----------
    catalog : Mapping[str, Easing]
        Easings keyed by a human readable test id.

    Returns
    -------
    pytest.MarkDecorator
        A ``parametrize`` mark that feeds the ``easing`` argument.
    """
    return pytest.mark.parametrize(
        "easing", list(catalog.values()), ids=list(catalog))


def each_pair(pairs: Mapping[str, MirrorPair]) -> pytest.MarkDecorator:
    """Parametrize a test over ``easing`` and ``mirror`` using pair ids.

    Parameters
    ----------
    pairs : Mapping[str, tuple[Easing, Easing]]
        Mirror pairs keyed by a human readable test id.

    Returns
    -------
    pytest.MarkDecorator
        A ``parametrize`` mark that feeds the ``easing`` and ``mirror``
        arguments.
    """
    return pytest.mark.parametrize(
        ("easing", "mirror"), list(pairs.values()), ids=list(pairs))


def unchecked(value: object) -> Any:
    """Hide a value's type so invalid arguments can be passed on purpose.

    Parameters
    ----------
    value : object
        Any value.

    Returns
    -------
    Any
        The same value, typed as ``Any``.
    """
    return value


def _identity(t: float) -> float:
    """Return the progress unchanged."""
    return t


def _cubic_bezier_function(
    x1: float, y1: float, x2: float, y2: float
) -> TimingFunction:
    """Build the timing function of a CSS ``cubic-bezier()``."""

    def coordinate(parameter: float, first: float, second: float) -> float:
        return (3 * (1 - parameter) ** 2 * parameter * first
                + 3 * (1 - parameter) * parameter ** 2 * second
                + parameter ** 3)

    def function(t: float) -> float:
        low, high = 0.0, 1.0
        for _ in range(_BISECTION_STEPS):
            middle = (low + high) / 2
            if coordinate(middle, x1, x2) < t:
                low = middle
            else:
                high = middle
        return coordinate((low + high) / 2, y1, y2)

    return function


def _steps_function(count: int, jump: str) -> TimingFunction:
    """Build the timing function of a CSS ``steps()`` following the spec."""
    jumps = {
        "start": count, "end": count, "none": count - 1, "both": count + 1,
    }[jump]
    offset = 1 if jump in ("start", "both") else 0

    def function(t: float) -> float:
        step = min(max(math.floor(t * count) + offset, 0), jumps)
        return step / jumps

    return function


def _linear_function(points: Sequence[float]) -> TimingFunction:
    """Build the timing function of a CSS ``linear()`` with even spacing."""
    last = len(points) - 1

    def function(t: float) -> float:
        position = t * last
        index = min(math.floor(position), last - 1)
        fraction = position - index
        return points[index] + (points[index + 1] - points[index]) * fraction

    return function


def _parse(css: str) -> TimingFunction | None:
    """Parse a CSS timing function, returning ``None`` when it is invalid."""
    if css == "linear":
        return _identity
    if css in _KEYWORD_BEZIERS:
        return _cubic_bezier_function(*_KEYWORD_BEZIERS[css])
    bezier = _CUBIC_BEZIER_CALL.fullmatch(css)
    if bezier is not None:
        x1, y1, x2, y2 = (float(group) for group in bezier.groups())
        if (0.0 <= x1 <= 1.0 and 0.0 <= x2 <= 1.0
                and math.isfinite(y1) and math.isfinite(y2)):
            return _cubic_bezier_function(x1, y1, x2, y2)
        return None
    steps = _STEPS_CALL.fullmatch(css)
    if steps is not None:
        count = int(steps.group(1))
        jump = (steps.group(2) or "jump-end").removeprefix("jump-")
        minimum = 2 if jump == "none" else 1
        return _steps_function(count, jump) if count >= minimum else None
    linear = _LINEAR_CALL.fullmatch(css)
    if linear is not None:
        points = [float(value)
                  for value in _NUMBER_PATTERN.findall(linear.group(1))]
        if all(math.isfinite(point) for point in points):
            return _linear_function(points)
    return None


def is_valid_timing_function(css: str) -> bool:
    """Tell whether a string is a valid CSS easing function.

    Parameters
    ----------
    css : str
        Text produced by ``Easing.css()``.

    Returns
    -------
    bool
        ``True`` for a CSS keyword, a ``cubic-bezier()`` whose x coordinates
        lie in the unit interval and whose numbers are finite, a ``steps()``
        with a whole count of 1 or more (2 or more with ``jump-none``), or a
        ``linear()`` with at least two finite points.
    """
    return _parse(css) is not None


def timing_function(easing: Easing) -> TimingFunction:
    """Turn the ``css()`` of an easing into a plain ``f(t)`` function.

    Parameters
    ----------
    easing : Easing
        Easing to evaluate.

    Returns
    -------
    Callable[[float], float]
        Function mapping time progress to output progress, as a browser
        would compute it from the generated CSS.

    Raises
    ------
    ValueError
        If the ``css()`` of the easing is not a valid timing function.
    """
    css = easing.css()
    function = _parse(css)
    if function is None:
        raise ValueError(
            f"{easing!r} produced an invalid timing function: {css!r}")
    return function


def sample(
    easing: Easing, points: Sequence[float] = SAMPLE_POINTS
) -> list[float]:
    """Evaluate an easing at several moments.

    Parameters
    ----------
    easing : Easing
        Easing to evaluate.
    points : Sequence[float], default SAMPLE_POINTS
        Time progress values in the ``[0, 1]`` interval.

    Returns
    -------
    list[float]
        Output progress for each point, in order.
    """
    function = timing_function(easing)
    return [function(point) for point in points]
