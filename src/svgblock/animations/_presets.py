from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

from ._base import (
    HIDDEN,
    REST,
    BaseAnimation,
    Keyframe,
    Pose,
    RepeatableAnimation,
    at_rest,
)
from ._easing import (
    EaseIn,
    EaseInOut,
    EaseInQuint,
    EaseOutQuint,
    Easing,
    Linear,
)

FOCUS_BLUR = 8.0

_POP_PEAK = 1.0
_POP_DIP_FRACTION = 0.25


def reverse_keyframes(frames: list[Keyframe],
                      default: Easing) -> list[Keyframe]:
    reversed_frames: list[Keyframe] = []
    for index in range(len(frames) - 1, -1, -1):
        easing = None
        if index > 0:
            easing = (frames[index - 1].easing or default).mirrored()
        reversed_frames.append(
            Keyframe(1 - frames[index].at, frames[index].pose, easing))
    return reversed_frames


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
class Effect(BaseAnimation, ABC):

    @abstractmethod
    def enter_from(self) -> Pose:
        pass

    def exit_to(self) -> Pose:
        return self.enter_from()

    def frames_in(self) -> list[Keyframe]:
        away = self.enter_from()
        return [Keyframe(0, away), Keyframe(1, at_rest(away.origin))]

    def frames_out(self) -> list[Keyframe]:
        away = self.exit_to()
        return [Keyframe(0, at_rest(away.origin)), Keyframe(1, away)]


@dataclass(frozen=True, kw_only=True)
class EnterAnimation(Effect, ABC):

    def keyframes(self) -> list[Keyframe]:
        return self.frames_in()


@dataclass(frozen=True, kw_only=True)
class ExitAnimation(Effect, ABC):

    def keyframes(self) -> list[Keyframe]:
        return self.frames_out()


@dataclass(frozen=True, kw_only=True)
class Fading(Effect, ABC):
    fade: bool = True
    focus: bool = False

    def _hidden(self, *, x: float = 0.0, y: float = 0.0,
                scale: float = 1.0) -> Pose:
        return Pose(
            opacity=0.0 if self.fade else 1.0,
            x=x,
            y=y,
            scale=scale,
            blur=FOCUS_BLUR if self.focus else 0.0,
        )


@dataclass(frozen=True, kw_only=True)
class _Fade(Effect, ABC):

    def enter_from(self) -> Pose:
        return Pose(opacity=0)


@dataclass(frozen=True, kw_only=True)
class FadeIn(_Fade, EnterAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class FadeOut(_Fade, ExitAnimation):
    easing: Easing = EaseIn()


@dataclass(frozen=True, kw_only=True)
class _Focus(Effect, ABC):
    blur: float = FOCUS_BLUR
    fade: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.blur <= 0:
            raise ValueError(
                f"blur must be greater than 0, got {self.blur!r}.")

    def enter_from(self) -> Pose:
        return Pose(opacity=0.0 if self.fade else 1.0, blur=self.blur)


@dataclass(frozen=True, kw_only=True)
class FocusIn(_Focus, EnterAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class FocusOut(_Focus, ExitAnimation):
    easing: Easing = EaseIn()


@dataclass(frozen=True, kw_only=True)
class _Travel(Fading, ABC):
    distance: float = 40

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.distance < 0:
            raise ValueError(
                f"distance must be 0 or more, got {self.distance!r}.")

    @abstractmethod
    def heading(self) -> tuple[float, float]:
        pass

    def enter_from(self) -> Pose:
        dx, dy = self.heading()
        return self._hidden(
            x=0.0 - dx * self.distance, y=0.0 - dy * self.distance)

    def exit_to(self) -> Pose:
        dx, dy = self.heading()
        return self._hidden(x=dx * self.distance, y=dy * self.distance)


@dataclass(frozen=True, kw_only=True)
class _Rise(_Travel, ABC):

    def heading(self) -> tuple[float, float]:
        return 0.0, -1.0


@dataclass(frozen=True, kw_only=True)
class RiseIn(_Rise, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class RiseOut(_Rise, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Drop(_Travel, ABC):

    def heading(self) -> tuple[float, float]:
        return 0.0, 1.0


@dataclass(frozen=True, kw_only=True)
class DropIn(_Drop, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class DropOut(_Drop, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Slide(_Travel, ABC):
    direction: Literal["left", "right"] = "right"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.direction not in ("left", "right"):
            raise ValueError(
                f"direction must be 'left' or 'right', got {self.direction!r}.")

    def heading(self) -> tuple[float, float]:
        return (1.0 if self.direction == "right" else -1.0), 0.0


@dataclass(frozen=True, kw_only=True)
class SlideIn(_Slide, EnterAnimation):
    easing: Easing = EaseOutQuint()


@dataclass(frozen=True, kw_only=True)
class SlideOut(_Slide, ExitAnimation):
    easing: Easing = EaseInQuint()


@dataclass(frozen=True, kw_only=True)
class _Pop(Fading, ABC):
    start_scale: float = 0.8
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

    def enter_from(self) -> Pose:
        return self._hidden(scale=self.start_scale)

    def frames_in(self) -> list[Keyframe]:
        dip = _POP_PEAK - (_POP_PEAK - self.start_scale) * _POP_DIP_FRACTION
        return [
            Keyframe(0, self.enter_from(), EaseOutQuint()),
            Keyframe(0.55, Pose(scale=_POP_PEAK), EaseInOut()),
            Keyframe(0.78, Pose(scale=dip), EaseInOut()),
            Keyframe(1, REST),
        ]

    def frames_out(self) -> list[Keyframe]:
        return reverse_keyframes(self.frames_in(), self.easing)


@dataclass(frozen=True, kw_only=True)
class PopIn(_Pop, EnterAnimation):
    pass


@dataclass(frozen=True, kw_only=True)
class PopOut(_Pop, ExitAnimation):
    pass


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
