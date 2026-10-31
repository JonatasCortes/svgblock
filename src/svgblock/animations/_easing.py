from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

BEZIER_SAMPLES = 400


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


@dataclass(frozen=True)
class EaseIn(_Fixed):
    _css: ClassVar[str] = "ease-in"


@dataclass(frozen=True)
class EaseOut(_Fixed):
    _css: ClassVar[str] = "ease-out"


@dataclass(frozen=True)
class EaseInOut(_Fixed):
    _css: ClassVar[str] = "ease-in-out"


@dataclass(frozen=True)
class EaseOutQuint(_Fixed):
    _css: ClassVar[str] = "cubic-bezier(0.22, 1, 0.36, 1)"


@dataclass(frozen=True)
class EaseOutBack(_Fixed):
    _css: ClassVar[str] = "cubic-bezier(0.34, 1.56, 0.64, 1)"

    @property
    def bounds(self) -> tuple[float, float]:
        return bezier_bounds(1.56, 1.0)


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


@dataclass(frozen=True)
class Steps(Easing):
    count: int

    def __post_init__(self) -> None:
        if (isinstance(self.count, bool) or self.count < 1):
            raise ValueError(
                f"count must be a whole number of 1 or more, got {self.count!r}.")

    def css(self) -> str:
        return f"steps({self.count})"
