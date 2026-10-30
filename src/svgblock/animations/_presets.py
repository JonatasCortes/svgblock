from dataclasses import dataclass

from ._base import REST, BaseAnimation, Keyframe, Pose, RepeatableAnimation


def _enter_from(start: Pose) -> list[Keyframe]:
    return [Keyframe(0, start), Keyframe(1, REST)]


@dataclass(frozen=True, kw_only=True)
class Fade(BaseAnimation):
    def keyframes(self) -> list[Keyframe]:
        return _enter_from(Pose(opacity=0))


@dataclass(frozen=True, kw_only=True)
class Rise(BaseAnimation):
    distance: float = 40
    fade: bool = True
    easing: str = "cubic-bezier(0.22, 1, 0.36, 1)"

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
    easing: str = "cubic-bezier(0.22, 1, 0.36, 1)"

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
    easing: str = "cubic-bezier(0.34, 1.56, 0.64, 1)"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.start_scale <= 0:
            raise ValueError(
                f"start_scale must be greater than 0, got {self.start_scale!r}.")

    def keyframes(self) -> list[Keyframe]:
        opacity = 0 if self.fade else 1
        return _enter_from(Pose(opacity=opacity, scale=self.start_scale))


@dataclass(frozen=True, kw_only=True)
class Pulse(RepeatableAnimation):
    amount: float = 0.06  # quanto cresce (0.06 = 6%)
    duration: float = 2.0
    easing: str = "ease-in-out"

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
