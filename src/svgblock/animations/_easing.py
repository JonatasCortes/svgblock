import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache, cached_property
from typing import ClassVar, Literal

BEZIER_SAMPLES = 400

CURVE_SAMPLES = 96

SPRING_REST = 0.002

MAX_SPRING_BOUNCE = 0.9


@cache
def bezier_bounds(y1: float, y2: float) -> tuple[float, float]:
    values: list[float] = []
    for index in range(BEZIER_SAMPLES + 1):
        t = index / BEZIER_SAMPLES
        values.append(
            3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3
        )
    return min(values), max(values)


@dataclass(frozen=True)
class Easing(ABC):

    @abstractmethod
    def css(self) -> str:
        pass

    @abstractmethod
    def mirrored(self) -> "Easing":
        pass

    @property
    def bounds(self) -> tuple[float, float]:
        return 0.0, 1.0


@dataclass(frozen=True)
class _Fixed(Easing):
    _css: ClassVar[str]

    def css(self) -> str:
        return self._css


@dataclass(frozen=True)
class Linear(_Fixed):
    _css: ClassVar[str] = "linear"

    def mirrored(self) -> Easing:
        return self


@dataclass(frozen=True)
class EaseIn(_Fixed):
    _css: ClassVar[str] = "ease-in"

    def mirrored(self) -> Easing:
        return EaseOut()


@dataclass(frozen=True)
class EaseOut(_Fixed):
    _css: ClassVar[str] = "ease-out"

    def mirrored(self) -> Easing:
        return EaseIn()


@dataclass(frozen=True)
class EaseInOut(_Fixed):
    _css: ClassVar[str] = "ease-in-out"

    def mirrored(self) -> Easing:
        return self


@dataclass(frozen=True)
class CubicBezier(Easing):
    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        for name in ("x1", "x2"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(
                    f"{name} must be between 0 and 1, got {value!r}.")

    @property
    def bounds(self) -> tuple[float, float]:
        return bezier_bounds(self.y1, self.y2)

    def css(self) -> str:
        return (f"cubic-bezier({self.x1:g}, {self.y1:g}, "
                f"{self.x2:g}, {self.y2:g})")

    def mirrored(self) -> Easing:
        return CubicBezier(1 - self.x2, 1 - self.y2, 1 - self.x1, 1 - self.y1)


@dataclass(frozen=True)
class _Preset(Easing):
    _points: ClassVar[tuple[float, float, float, float]]

    def _bezier(self) -> CubicBezier:
        return CubicBezier(*self._points)

    @property
    def bounds(self) -> tuple[float, float]:
        return self._bezier().bounds

    def css(self) -> str:
        return self._bezier().css()

    def mirrored(self) -> Easing:
        return self._bezier().mirrored()


@dataclass(frozen=True)
class EaseInSine(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.12, 0, 0.39, 0)


@dataclass(frozen=True)
class EaseOutSine(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.61, 1, 0.88, 1)


@dataclass(frozen=True)
class EaseInOutSine(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.37, 0, 0.63, 1)


@dataclass(frozen=True)
class EaseInCubic(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.32, 0, 0.67, 0)


@dataclass(frozen=True)
class EaseOutCubic(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.33, 1, 0.68, 1)


@dataclass(frozen=True)
class EaseInOutCubic(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.65, 0, 0.35, 1)


@dataclass(frozen=True)
class EaseInQuint(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.64, 0, 0.78, 0)


@dataclass(frozen=True)
class EaseOutQuint(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.22, 1, 0.36, 1)


@dataclass(frozen=True)
class EaseInOutQuint(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.83, 0, 0.17, 1)


@dataclass(frozen=True)
class EaseInExpo(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.7, 0, 0.84, 0)


@dataclass(frozen=True)
class EaseOutExpo(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.16, 1, 0.3, 1)


@dataclass(frozen=True)
class EaseInOutExpo(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.87, 0, 0.13, 1)


@dataclass(frozen=True)
class EaseInCirc(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.55, 0, 1, 0.45)


@dataclass(frozen=True)
class EaseOutCirc(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0, 0.55, 0.45, 1)


@dataclass(frozen=True)
class EaseInOutCirc(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (0.85, 0, 0.15, 1)


@dataclass(frozen=True)
class EaseInBack(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (
        0.36, 0, 0.66, -0.56)


@dataclass(frozen=True)
class EaseOutBack(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (
        0.34, 1.56, 0.64, 1)


@dataclass(frozen=True)
class EaseInOutBack(_Preset):
    _points: ClassVar[tuple[float, float, float, float]] = (
        0.68, -0.6, 0.32, 1.6)


@dataclass(frozen=True)
class Curve(Easing):

    @abstractmethod
    def value(self, t: float) -> float:
        pass

    @cached_property
    def _samples(self) -> tuple[float, ...]:
        return tuple(
            self.value(index / CURVE_SAMPLES)
            for index in range(CURVE_SAMPLES + 1)
        )

    @property
    def bounds(self) -> tuple[float, float]:
        return min(self._samples), max(self._samples)

    def css(self) -> str:
        points = ", ".join(f"{round(value, 4) + 0.0:g}"
                           for value in self._samples)
        return f"linear({points})"

    def mirrored(self) -> Easing:
        return Mirrored(self)


@dataclass(frozen=True)
class Mirrored(Curve):
    base: Curve

    def value(self, t: float) -> float:
        return 1 - self.base.value(1 - t)

    def mirrored(self) -> Easing:
        return self.base


@dataclass(frozen=True)
class Spring(Curve):
    bounce: float = 0.5

    def __post_init__(self) -> None:
        if not 0 < self.bounce <= MAX_SPRING_BOUNCE:
            raise ValueError(
                f"bounce must be greater than 0 and at most "
                f"{MAX_SPRING_BOUNCE:g}, got {self.bounce!r}.")

    def _raw(self, t: float) -> float:
        damping = 1 - self.bounce
        rate = math.log(1 / SPRING_REST)
        swing = rate * math.sqrt(1 - damping ** 2) / damping
        return 1 - math.exp(-rate * t) * (
            math.cos(swing * t) + (rate / swing) * math.sin(swing * t))

    def value(self, t: float) -> float:
        return self._raw(t) + (1 - self._raw(1)) * t


@dataclass(frozen=True)
class Bounce(Curve):
    bounces: int = 3
    rebound: float = 0.5

    def __post_init__(self) -> None:
        if isinstance(self.bounces, bool) or self.bounces < 1:
            raise ValueError(
                f"bounces must be a whole number of 1 or more, "
                f"got {self.bounces!r}.")
        if not 0 < self.rebound < 1:
            raise ValueError(
                f"rebound must be greater than 0 and less than 1, "
                f"got {self.rebound!r}.")

    def _arc(self, number: int, progress: float) -> float:
        depth = self.rebound ** (2 * number)
        return 1 - depth * 4 * progress * (1 - progress)

    def value(self, t: float) -> float:
        extra = sum(self.rebound ** k for k in range(1, self.bounces + 1))
        first = 1 / (1 + 2 * extra)
        if t <= first:
            return (t / first) ** 2
        start = first
        for number in range(1, self.bounces):
            length = 2 * first * self.rebound ** number
            if t <= start + length:
                return self._arc(number, (t - start) / length)
            start += length
        length = 2 * first * self.rebound ** self.bounces
        return self._arc(self.bounces, min(1.0, (t - start) / length))


Jump = Literal["start", "end", "none", "both"]

_MIRRORED_JUMP: dict[str, Jump] = {
    "start": "end",
    "end": "start",
    "none": "none",
    "both": "both",
}


@dataclass(frozen=True)
class Steps(Easing):
    count: int
    jump: Jump = "end"

    def __post_init__(self) -> None:
        if (isinstance(self.count, bool) or self.count < 1):
            raise ValueError(
                f"count must be a whole number of 1 or more, got {self.count!r}.")
        if self.jump not in _MIRRORED_JUMP:
            raise ValueError(
                "jump must be 'start', 'end', 'none' or 'both', "
                f"got {self.jump!r}.")
        if self.jump == "none" and self.count < 2:
            raise ValueError("count must be 2 or more when jump is 'none'.")

    def css(self) -> str:
        if self.jump == "end":
            return f"steps({self.count})"
        return f"steps({self.count}, jump-{self.jump})"

    def mirrored(self) -> Easing:
        return Steps(self.count, _MIRRORED_JUMP[self.jump])
