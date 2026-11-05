import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol
import pytest
from svgblock import (
    BaseAnimation,
    Drift,
    DropIn,
    DropOut,
    FadeIn,
    FadeOut,
    Float,
    FlickerIn,
    FlickerOut,
    FlipIn,
    FlipOut,
    FocusIn,
    FocusOut,
    GlitchIn,
    GlitchOut,
    Hide,
    Jelly,
    PopIn,
    PopOut,
    Pulse,
    RiseIn,
    RiseOut,
    Rotate,
    Shake,
    Show,
    SlideIn,
    SlideOut,
    SpinIn,
    SpinOut,
    Sway,
    UnfoldIn,
    UnfoldOut,
    ZoomIn,
    ZoomOut,
)

AnimationFactory = Callable[..., BaseAnimation]


class PoseView(Protocol):
    """Read-only view of the pose attached to a keyframe."""

    @property
    def opacity(self) -> float: ...

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    @property
    def scale(self) -> float: ...

    @property
    def scale_x(self) -> float: ...

    @property
    def scale_y(self) -> float: ...

    @property
    def rotate(self) -> float: ...

    @property
    def blur(self) -> float: ...

    @property
    def origin(self) -> tuple[float, float]: ...


class KeyframeView(Protocol):
    """Read-only view of a keyframe returned by ``keyframes()``."""

    @property
    def at(self) -> float: ...

    @property
    def pose(self) -> PoseView: ...

    @property
    def easing(self) -> object | None: ...


class SegmentView(Protocol):
    """Read-only view of a segment returned by ``segment()``/``expand()``."""

    @property
    def duration(self) -> float: ...

    @property
    def keyframes(self) -> Sequence[KeyframeView]: ...


@dataclass(frozen=True)
class CssKeyframe:
    """A single ``<percent>% { ... }`` step parsed from generated CSS."""

    percent: float
    declarations: str


ENTRANCES: dict[str, BaseAnimation] = {
    "FadeIn": FadeIn(),
    "FocusIn": FocusIn(),
    "RiseIn": RiseIn(),
    "DropIn": DropIn(),
    "SlideIn": SlideIn(),
    "ZoomIn": ZoomIn(),
    "SpinIn": SpinIn(),
    "FlipIn": FlipIn(),
    "UnfoldIn": UnfoldIn(),
    "PopIn": PopIn(),
    "FlickerIn": FlickerIn(),
    "GlitchIn": GlitchIn(),
}

EXITS: dict[str, BaseAnimation] = {
    "FadeOut": FadeOut(),
    "FocusOut": FocusOut(),
    "RiseOut": RiseOut(),
    "DropOut": DropOut(),
    "SlideOut": SlideOut(),
    "ZoomOut": ZoomOut(),
    "SpinOut": SpinOut(),
    "FlipOut": FlipOut(),
    "UnfoldOut": UnfoldOut(),
    "PopOut": PopOut(),
    "FlickerOut": FlickerOut(),
    "GlitchOut": GlitchOut(),
}

LOOPS: dict[str, BaseAnimation] = {
    "Pulse": Pulse(),
    "Float": Float(),
    "Sway": Sway(),
    "Shake": Shake(),
    "Rotate": Rotate(),
    "Drift": Drift(),
    "Jelly": Jelly(),
}

SEAMLESS_LOOPS: dict[str, BaseAnimation] = {
    name: animation for name, animation in LOOPS.items() if name != "Rotate"
}

HOLDS: dict[str, BaseAnimation] = {
    "Show": Show(duration=1.0),
    "Hide": Hide(duration=1.0),
}

EVERY_ANIMATION: dict[str, BaseAnimation] = {
    **ENTRANCES,
    **EXITS,
    **LOOPS,
    **HOLDS,
}

LOOP_FACTORIES: dict[str, AnimationFactory] = {
    "Pulse": Pulse,
    "Float": Float,
    "Sway": Sway,
    "Shake": Shake,
    "Rotate": Rotate,
    "Drift": Drift,
    "Jelly": Jelly,
}

FADING_ENTRANCE_FACTORIES: dict[str, AnimationFactory] = {
    "RiseIn": RiseIn,
    "DropIn": DropIn,
    "SlideIn": SlideIn,
    "ZoomIn": ZoomIn,
    "SpinIn": SpinIn,
    "FlipIn": FlipIn,
    "UnfoldIn": UnfoldIn,
    "PopIn": PopIn,
}

FADING_EXIT_FACTORIES: dict[str, AnimationFactory] = {
    "RiseOut": RiseOut,
    "DropOut": DropOut,
    "SlideOut": SlideOut,
    "ZoomOut": ZoomOut,
    "SpinOut": SpinOut,
    "FlipOut": FlipOut,
    "UnfoldOut": UnfoldOut,
    "PopOut": PopOut,
}

SELF_EASED_EFFECTS = frozenset({"PopIn", "PopOut", "FlickerIn", "FlickerOut",
                                "GlitchIn", "GlitchOut"})


def each(catalog: Mapping[str, object]) -> pytest.MarkDecorator:
    """Parametrize a test over ``animation`` using the catalogue keys as ids.

    Parameters
    ----------
    catalog : Mapping[str, object]
        Animations keyed by a human readable test id.

    Returns
    -------
    pytest.MarkDecorator
        A ``parametrize`` mark that feeds the ``animation`` argument.
    """
    return pytest.mark.parametrize(
        "animation", list(catalog.values()), ids=list(catalog))


def each_factory(catalog: Mapping[str, AnimationFactory]) -> pytest.MarkDecorator:
    """Parametrize a test over ``factory`` using the catalogue keys as ids.

    Parameters
    ----------
    catalog : Mapping[str, AnimationFactory]
        Animation constructors keyed by a human readable test id.

    Returns
    -------
    pytest.MarkDecorator
        A ``parametrize`` mark that feeds the ``factory`` argument.
    """
    return pytest.mark.parametrize(
        "factory", list(catalog.values()), ids=list(catalog))


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


def is_at_rest(pose: PoseView) -> bool:
    """Tell whether a pose is the element's natural, untouched appearance.

    Parameters
    ----------
    pose : PoseView
        Pose to inspect.

    Returns
    -------
    bool
        ``True`` when opacity, translation, scale, rotation and blur are neutral.
    """
    return (pose.opacity == 1 and pose.x == 0 and pose.y == 0
            and pose.scale == 1 and pose.scale_x == 1 and pose.scale_y == 1
            and pose.rotate == 0 and pose.blur == 0)


def count_dips(values: Sequence[float]) -> int:
    """Count interior values strictly lower than both of their neighbours.

    Parameters
    ----------
    values : Sequence[float]
        Series to inspect.

    Returns
    -------
    int
        Number of local minima.
    """
    return sum(1 for before, current, after in zip(values, values[1:], values[2:])
               if current < before and current < after)


def peaks(values: Sequence[float]) -> list[float]:
    """Return interior values strictly higher than both of their neighbours.

    Parameters
    ----------
    values : Sequence[float]
        Series to inspect.

    Returns
    -------
    list[float]
        Local maxima, in order of appearance.
    """
    return [current for before, current, after in zip(values, values[1:], values[2:])
            if current > before and current > after]


_KEYFRAMES_RULE = re.compile(
    r"@keyframes (?P<name>[\w-]+) \{\n(?P<steps>.*?)\n\}", re.DOTALL)
_KEYFRAME_STEP = re.compile(
    r"(?P<percent>\d+(?:\.\d+)?)% \{ (?P<body>[^}]*)\}")
_ANIMATION_RULE = re.compile(
    r"\.[\w-]+ \{\s*animation: (?P<value>[^;]+);")


def parse_css_keyframes(css: str) -> dict[str, list[CssKeyframe]]:
    """Parse every ``@keyframes`` rule of a generated stylesheet.

    Parameters
    ----------
    css : str
        Output of ``build_animation_css``.

    Returns
    -------
    dict[str, list[CssKeyframe]]
        Steps of each rule, keyed by the rule name.
    """
    rules: dict[str, list[CssKeyframe]] = {}
    for rule in _KEYFRAMES_RULE.finditer(css):
        rules[rule.group("name")] = [
            CssKeyframe(float(step.group("percent")), step.group("body"))
            for step in _KEYFRAME_STEP.finditer(rule.group("steps"))
        ]
    return rules


def animation_value(css: str) -> str:
    """Extract the value of the ``animation`` declaration of the main rule.

    Parameters
    ----------
    css : str
        Output of ``build_animation_css``.

    Returns
    -------
    str
        Text between ``animation:`` and the closing semicolon.
    """
    match = _ANIMATION_RULE.search(css)
    assert match is not None, "generated CSS has no animation declaration"
    return match.group("value")
