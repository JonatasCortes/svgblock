import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ._easing import EaseOut, Easing

MAX_LOOP_LIMIT = 1000

MAX_SEGMENTS = 10_000


@dataclass(frozen=True)
class Pose:
    opacity: float = 1.0
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0


REST = Pose()
HIDDEN = Pose(opacity=0)


@dataclass(frozen=True)
class Keyframe:
    at: float
    pose: Pose
    easing: Easing | None = None


@dataclass(frozen=True)
class Segment:
    duration: float
    keyframes: tuple[Keyframe, ...]
    easing: Easing


@dataclass(frozen=True)
class Expansion:
    head: tuple[Segment, ...] = ()
    cycle: tuple[Segment, ...] | None = None

    @property
    def playing_time(self) -> float:
        cycle = self.cycle or ()
        return (sum(segment.duration for segment in self.head)
                + sum(segment.duration for segment in cycle))


@dataclass(frozen=True)
class Layer:
    name: str
    keyframes: tuple[Keyframe, ...]
    duration: float
    easing: Easing
    iterations: int | None
    delay: float = 0.0
    fill: str = "both"


def check_loop_limit(loop_limit: int | None) -> None:
    if loop_limit is None:
        return
    if loop_limit < 0:
        raise ValueError(
            "loop_limit must be 0 or more, or None for no limit, "
            f"got {loop_limit!r}."
        )
    if loop_limit > MAX_LOOP_LIMIT:
        raise ValueError(
            f"loop_limit must be at most {MAX_LOOP_LIMIT}, got {loop_limit!r}. "
            "Use None for no limit."
        )


@dataclass(frozen=True, kw_only=True)
class BaseAnimation(ABC):
    duration: float = 0.8
    easing: Easing = EaseOut()

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError(
                f"duration must be greater than 0, got {self.duration!r}.")

    @abstractmethod
    def keyframes(self) -> list[Keyframe]:
        pass

    def extent(self, attribute: str) -> tuple[float, float]:
        frames = self.keyframes()
        reached = [getattr(frame.pose, attribute) for frame in frames]
        for current, following in zip(frames, frames[1:]):
            easing = current.easing or self.easing
            start = getattr(current.pose, attribute)
            end = getattr(following.pose, attribute)
            for fraction in easing.bounds:
                reached.append(start + (end - start) * fraction)
        return min(reached), max(reached)

    @property
    def max_scale(self) -> float:
        return max(1.0, self.extent("scale")[1])

    @property
    def overflow(self) -> tuple[float, float, float, float]:
        x_low, x_high = self.extent("x")
        y_low, y_high = self.extent("y")
        return (
            max(0.0, -x_low),
            max(0.0, -y_low),
            max(0.0, x_high),
            max(0.0, y_high),
        )

    @property
    def iterations(self) -> int | None:
        return 1

    @property
    def is_infinite(self) -> bool:
        return self.iterations is None

    @property
    def css_name(self) -> str:
        digest = hashlib.sha1(repr(self).encode()).hexdigest()[:8]
        return f"{type(self).__name__.lower()}-{digest}"

    def segment(self) -> Segment:
        return Segment(self.duration, tuple(self.keyframes()), self.easing)

    def expand(self) -> Expansion:
        segment = self.segment()
        if self.iterations is None:
            return Expansion(cycle=(segment,))
        return Expansion(head=(segment,) * self.iterations)

    def layers(self) -> list[Layer]:
        return [Layer(
            name=self.css_name,
            keyframes=tuple(self.keyframes()),
            duration=self.duration,
            easing=self.easing,
            iterations=self.iterations,
        )]


@dataclass(frozen=True, kw_only=True)
class RepeatableAnimation(BaseAnimation, ABC):
    loop_limit: int | None = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        check_loop_limit(self.loop_limit)

    @property
    def iterations(self) -> int | None:
        if self.loop_limit is None:
            return None
        return self.loop_limit + 1
