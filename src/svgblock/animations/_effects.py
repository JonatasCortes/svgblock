import math
from abc import ABC
from dataclasses import dataclass, field, replace
from typing import Literal

from ._base import (
    ORIGIN_BOTTOM,
    ORIGIN_CENTER,
    ORIGIN_LEFT,
    ORIGIN_RIGHT,
    ORIGIN_TOP,
    REST,
    Keyframe,
    Origin,
    Pose,
    RepeatableAnimation,
    at_rest,
)
from ._presets import (
    EnterAnimation,
    ExitAnimation,
    Effect,
    Fading,
    reverse_keyframes,
)
from ._easing import (
    EaseInCubic,
    EaseInOut,
    EaseInQuint,
    EaseOutCubic,
    EaseOutQuint,
    Easing,
    Linear,
    Steps,
)

_FLICKER_PHASE = 0.8
_FLICKER_SETTLE = 0.85
_FLICKER_DIM = 0.1

# Each entry: (at, shift, opacity, stretch). The shift is multiplied by the
# intensity; the last entry before the end is already at rest.
_GLITCH_PATTERN: tuple[tuple[float, float, float, float], ...] = (
    (0.10, -1.0, 1.0, 1.00),
    (0.18, 0.6, 0.4, 1.05),
    (0.28, -0.3, 1.0, 1.00),
    (0.40, 0.9, 0.2, 1.04),
    (0.52, -0.5, 1.0, 1.00),
    (0.66, 0.2, 0.7, 1.03),
    (0.84, 0.0, 1.0, 1.00),
)

_DRIFT_POINTS = 24

_EDGE_ORIGIN: dict[str, Origin] = {
    "top": ORIGIN_TOP,
    "bottom": ORIGIN_BOTTOM,
    "left": ORIGIN_LEFT,
    "right": ORIGIN_RIGHT,
}

_PIVOT_ORIGIN: dict[str, Origin] = {
    "top": ORIGIN_TOP,
    "center": ORIGIN_CENTER,
    "bottom": ORIGIN_BOTTOM,
}


def _decay(count: int) -> list[tuple[float, float]]:
    return [
        (index / (count + 1), (-1) ** (index + 1) * (1 - (index - 1) / count))
        for index in range(1, count + 1)
    ]


def _check_count(name: str, value: int) -> None:
    if isinstance(value, bool) or value < 1:
        raise ValueError(
            f"{name} must be a whole number of 1 or more, got {value!r}.")


@dataclass(frozen=True, kw_only=True)
class _Zoom(Fading, ABC):
    scale: float = 0.5

    def __post_init__(self) -> None:
        if self.scale <= 0:
            raise ValueError(
                f"scale must be greater than 0, got {self.scale!r}.")
        super().__post_init__()

    def enter_from(self) -> Pose:
        return self._hidden(scale=self.scale)


@dataclass(frozen=True, kw_only=True)
class ZoomIn(_Zoom, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class ZoomOut(_Zoom, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Spin(Fading, ABC):
    angle: float = 45.0

    def enter_from(self) -> Pose:
        return replace(self._hidden(), rotate=-self.angle)

    def exit_to(self) -> Pose:
        return replace(self._hidden(), rotate=self.angle)


@dataclass(frozen=True, kw_only=True)
class SpinIn(_Spin, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class SpinOut(_Spin, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Flip(Fading, ABC):
    axis: Literal["horizontal", "vertical"] = "horizontal"

    def __post_init__(self) -> None:
        if self.axis not in ("horizontal", "vertical"):
            raise ValueError(
                f"axis must be 'horizontal' or 'vertical', got {self.axis!r}.")
        super().__post_init__()

    def enter_from(self) -> Pose:
        if self.axis == "horizontal":
            return replace(self._hidden(), scale_x=-1.0)
        return replace(self._hidden(), scale_y=-1.0)


@dataclass(frozen=True, kw_only=True)
class FlipIn(_Flip, EnterAnimation):
    easing: Easing = EaseOutCubic()


@dataclass(frozen=True, kw_only=True)
class FlipOut(_Flip, ExitAnimation):
    easing: Easing = EaseInCubic()


@dataclass(frozen=True, kw_only=True)
class _Unfold(Fading, ABC):
    edge: Literal["top", "bottom", "left", "right"] = "top"
    fade: bool = False

    def __post_init__(self) -> None:
        if self.edge not in _EDGE_ORIGIN:
            raise ValueError(
                "edge must be 'top', 'bottom', 'left' or 'right', "
                f"got {self.edge!r}.")
        super().__post_init__()

    def enter_from(self) -> Pose:
        away = replace(self._hidden(), origin=_EDGE_ORIGIN[self.edge])
        if self.edge in ("top", "bottom"):
            return replace(away, scale_y=0.0)
        return replace(away, scale_x=0.0)


@dataclass(frozen=True, kw_only=True)
class UnfoldIn(_Unfold, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class UnfoldOut(_Unfold, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Flicker(Effect, ABC):
    flickers: int = 3
    duration: float = 1.0
    easing: Easing = field(default=Linear(), init=False)

    def __post_init__(self) -> None:
        _check_count("flickers", self.flickers)
        super().__post_init__()

    def enter_from(self) -> Pose:
        return Pose(opacity=0)

    def frames_in(self) -> list[Keyframe]:
        count = self.flickers
        frames = [Keyframe(0, Pose(opacity=0))]
        for index in range(count):
            lit = _FLICKER_PHASE * (index + 0.15) / count
            dim = _FLICKER_PHASE * (index + 0.6) / count
            brightness = 0.6 + 0.4 * (index + 1) / count
            frames.append(Keyframe(lit, Pose(opacity=brightness)))
            frames.append(Keyframe(dim, Pose(opacity=_FLICKER_DIM)))
        frames.append(Keyframe(_FLICKER_SETTLE, REST))
        frames.append(Keyframe(1, REST))
        return frames

    def frames_out(self) -> list[Keyframe]:
        return reverse_keyframes(self.frames_in(), self.easing)


@dataclass(frozen=True, kw_only=True)
class FlickerIn(_Flicker, EnterAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class FlickerOut(_Flicker, ExitAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class _Glitch(Effect, ABC):
    intensity: float = 12.0
    duration: float = 0.6
    easing: Easing = field(default=Linear(), init=False)

    def __post_init__(self) -> None:
        if self.intensity <= 0:
            raise ValueError(
                f"intensity must be greater than 0, got {self.intensity!r}.")
        super().__post_init__()

    def enter_from(self) -> Pose:
        return Pose(opacity=0)

    def frames_in(self) -> list[Keyframe]:
        hold = Steps(1)
        frames = [Keyframe(0, Pose(opacity=0), hold)]
        for at, shift, opacity, stretch in _GLITCH_PATTERN:
            pose = Pose(
                opacity=opacity, x=shift * self.intensity, scale_x=stretch)
            frames.append(Keyframe(at, pose, hold))
        frames.append(Keyframe(1, REST))
        return frames

    def frames_out(self) -> list[Keyframe]:
        return reverse_keyframes(self.frames_in(), self.easing)


@dataclass(frozen=True, kw_only=True)
class GlitchIn(_Glitch, EnterAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class GlitchOut(_Glitch, ExitAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class Float(RepeatableAnimation):
    amount: float = 8.0
    duration: float = 3.0
    easing: Easing = EaseInOut()

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError(
                f"amount must be greater than 0, got {self.amount!r}.")
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        return [
            Keyframe(0, REST),
            Keyframe(0.25, Pose(y=-self.amount)),
            Keyframe(0.75, Pose(y=self.amount)),
            Keyframe(1, REST),
        ]


@dataclass(frozen=True, kw_only=True)
class Sway(RepeatableAnimation):
    angle: float = 3.0
    pivot: Literal["top", "center", "bottom"] = "top"
    duration: float = 4.0
    easing: Easing = EaseInOut()

    def __post_init__(self) -> None:
        if self.angle <= 0:
            raise ValueError(
                f"angle must be greater than 0, got {self.angle!r}.")
        if self.pivot not in _PIVOT_ORIGIN:
            raise ValueError(
                f"pivot must be 'top', 'center' or 'bottom', got {self.pivot!r}.")
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        origin = _PIVOT_ORIGIN[self.pivot]
        return [
            Keyframe(0, at_rest(origin)),
            Keyframe(0.25, Pose(rotate=self.angle, origin=origin)),
            Keyframe(0.75, Pose(rotate=-self.angle, origin=origin)),
            Keyframe(1, at_rest(origin)),
        ]


@dataclass(frozen=True, kw_only=True)
class Shake(RepeatableAnimation):
    amount: float = 8.0
    shakes: int = 6
    duration: float = 0.6
    easing: Easing = EaseInOut()

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError(
                f"amount must be greater than 0, got {self.amount!r}.")
        _check_count("shakes", self.shakes)
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        frames = [Keyframe(0, REST)]
        for at, factor in _decay(self.shakes):
            frames.append(Keyframe(at, Pose(x=self.amount * factor)))
        frames.append(Keyframe(1, REST))
        return frames


@dataclass(frozen=True, kw_only=True)
class Rotate(RepeatableAnimation):
    angle: float = 360.0
    duration: float = 6.0
    easing: Easing = Linear()

    def __post_init__(self) -> None:
        if self.angle == 0:
            raise ValueError("angle must not be 0.")
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        return [Keyframe(0, REST), Keyframe(1, Pose(rotate=self.angle))]


@dataclass(frozen=True, kw_only=True)
class Drift(RepeatableAnimation):
    radius: float = 8.0
    duration: float = 6.0
    easing: Easing = Linear()

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError(
                f"radius must be greater than 0, got {self.radius!r}.")
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        frames: list[Keyframe] = []
        for index in range(_DRIFT_POINTS + 1):
            turn = 2 * math.pi * index / _DRIFT_POINTS
            x = round(self.radius * math.sin(turn), 4) + 0.0
            y = round(self.radius / 2 * math.sin(2 * turn), 4) + 0.0
            frames.append(Keyframe(index / _DRIFT_POINTS, Pose(x=x, y=y)))
        return frames


@dataclass(frozen=True, kw_only=True)
class Jelly(RepeatableAnimation):
    amount: float = 0.15
    wobbles: int = 4
    duration: float = 0.9
    easing: Easing = EaseInOut()

    def __post_init__(self) -> None:
        if not 0 < self.amount < 1:
            raise ValueError(
                "amount must be greater than 0 and less than 1, "
                f"got {self.amount!r}.")
        _check_count("wobbles", self.wobbles)
        super().__post_init__()

    def keyframes(self) -> list[Keyframe]:
        frames = [Keyframe(0, REST)]
        for at, factor in _decay(self.wobbles):
            pose = Pose(
                scale_x=1 + self.amount * factor,
                scale_y=1 - self.amount * factor,
            )
            frames.append(Keyframe(at, pose))
        frames.append(Keyframe(1, REST))
        return frames
