from dataclasses import dataclass, field

from ._base import HIDDEN, REST, BaseAnimation, Keyframe, Pose, RepeatableAnimation
from ._easing import EaseInOut, EaseOutQuint, Easing, Linear

_POP_PEAK = 1.0
_POP_DIP_FRACTION = 0.25


def _enter_from(start: Pose) -> list[Keyframe]:
    return [Keyframe(0, start), Keyframe(1, REST)]


@dataclass(frozen=True)
class Show(BaseAnimation):
    duration: float = field()
    easing: Easing = field(default=Linear(), init=False)

    def keyframes(self) -> list[Keyframe]:
        return [Keyframe(0, REST), Keyframe(1, REST)]


@dataclass(frozen=True)
class Hide(BaseAnimation):
    duration: float = field()
    easing: Easing = field(default=Linear(), init=False)

    def keyframes(self) -> list[Keyframe]:
        return [Keyframe(0, HIDDEN), Keyframe(1, HIDDEN)]


@dataclass(frozen=True, kw_only=True)
class Fade(BaseAnimation):
    def keyframes(self) -> list[Keyframe]:
        return _enter_from(Pose(opacity=0))


@dataclass(frozen=True, kw_only=True)
class Rise(BaseAnimation):
    distance: float = 40
    fade: bool = True
    easing: Easing = EaseOutQuint()

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.distance < 0:
            raise ValueError(
                f"distance must be 0 or more, got {self.distance!r}.")

    def keyframes(self) -> list[Keyframe]:
        opacity = 0 if self.fade else 1
        return _enter_from(Pose(opacity=opacity, y=self.distance))


@dataclass(frozen=True, kw_only=True)
class Drop(BaseAnimation):
    distance: float = 40
    fade: bool = True
    easing: Easing = EaseOutQuint()

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.distance < 0:
            raise ValueError(
                f"distance must be 0 or more, got {self.distance!r}.")

    def keyframes(self) -> list[Keyframe]:
        opacity = 0 if self.fade else 1
        return _enter_from(Pose(opacity=opacity, y=-self.distance))


@dataclass(frozen=True, kw_only=True)
class Pop(BaseAnimation):
    start_scale: float = 0.8
    fade: bool = True
    duration: float = 0.6
    easing: Easing = field(default=Linear(), init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 0 < self.start_scale <= _POP_PEAK:
            raise ValueError(
                f"start_scale must be greater than 0 and at most {_POP_PEAK:g}, "
                f"got {self.start_scale!r}."
            )
        if self.max_scale > _POP_PEAK:
            raise ValueError(
                f"Pop must never exceed scale {_POP_PEAK:g}, got {self.max_scale!r}."
            )

    def keyframes(self) -> list[Keyframe]:
        opacity = 0 if self.fade else 1
        dip = _POP_PEAK - (_POP_PEAK - self.start_scale) * _POP_DIP_FRACTION
        return [
            Keyframe(0, Pose(opacity=opacity, scale=self.start_scale),
                     EaseOutQuint()),
            Keyframe(0.55, Pose(scale=_POP_PEAK), EaseInOut()),
            Keyframe(0.78, Pose(scale=dip), EaseInOut()),
            Keyframe(1, REST),
        ]


@dataclass(frozen=True, kw_only=True)
class Pulse(RepeatableAnimation):
    amount: float = 0.06
    duration: float = 2.0
    easing: Easing = EaseInOut()

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.amount <= 0:
            raise ValueError(
                f"amount must be greater than 0, got {self.amount!r}.")

    def keyframes(self) -> list[Keyframe]:
        return [
            Keyframe(0, REST),
            Keyframe(0.5, Pose(scale=1 + self.amount)),
            Keyframe(1, REST),
        ]
