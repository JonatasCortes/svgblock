import hashlib
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from ._easing import EaseOut, Easing

MAX_LOOP_LIMIT = 1000

MAX_SEGMENTS = 10_000

BLUR_REACH = 3.0

Origin = tuple[float, float]
Margins = tuple[float, float, float, float]

ORIGIN_CENTER: Origin = (0.5, 0.5)
ORIGIN_TOP: Origin = (0.5, 0.0)
ORIGIN_BOTTOM: Origin = (0.5, 1.0)
ORIGIN_LEFT: Origin = (0.0, 0.5)
ORIGIN_RIGHT: Origin = (1.0, 0.5)

NO_MARGINS: Margins = (0.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class Pose:
    opacity: float = 1.0
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotate: float = 0.0
    blur: float = 0.0
    origin: Origin = ORIGIN_CENTER

    def __post_init__(self) -> None:
        if self.blur < 0:
            raise ValueError(f"blur must be 0 or more, got {self.blur!r}.")


REST = Pose()
HIDDEN = Pose(opacity=0)


def at_rest(origin: Origin = ORIGIN_CENTER) -> Pose:
    return replace(REST, origin=origin)


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


def combine_margins(*parts: Margins) -> Margins:
    return (
        sum(part[0] for part in parts),
        sum(part[1] for part in parts),
        sum(part[2] for part in parts),
        sum(part[3] for part in parts),
    )


def rotation_margins(
    width: float,
    height: float,
    low: float,
    high: float,
    origins: set[Origin] | frozenset[Origin],
) -> Margins:
    if low == 0 and high == 0:
        return NO_MARGINS
    end = min(high, low + 360.0)
    angles = [float(degree)
              for degree in range(math.floor(low), math.ceil(end) + 1)]
    angles.extend((low, end))
    corners = ((0.0, 0.0), (width, 0.0), (width, height), (0.0, height))
    min_x = min_y = 0.0
    max_x, max_y = width, height
    for origin_x, origin_y in origins:
        pivot_x, pivot_y = origin_x * width, origin_y * height
        for degrees in angles:
            radians = math.radians(degrees)
            cosine, sine = math.cos(radians), math.sin(radians)
            for corner_x, corner_y in corners:
                dx, dy = corner_x - pivot_x, corner_y - pivot_y
                x = pivot_x + dx * cosine - dy * sine
                y = pivot_y + dx * sine + dy * cosine
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
    return (-min_x, -min_y, max_x - width, max_y - height)


@dataclass(frozen=True, kw_only=True)
class BaseAnimation(ABC):
    duration: float = 0.8
    easing: Easing = EaseOut()

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError(
                f"duration must be greater than 0, got {self.duration!r}.")
        if self.extent("blur")[0] < 0:
            raise ValueError(
                "This animation would make the blur go below 0 because of its "
                "easing. Use an easing that does not overshoot.")

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
        uniform = self.extent("scale")[1]
        stretch = max(self.extent("scale_x")[1], self.extent("scale_y")[1])
        return max(1.0, uniform * stretch)

    @property
    def max_blur(self) -> float:
        return max(0.0, self.extent("blur")[1])

    @property
    def origins(self) -> frozenset[Origin]:
        return frozenset(frame.pose.origin for frame in self.keyframes())

    @property
    def overflow(self) -> tuple[float, float, float, float]:
        frames = self.keyframes()
        result = {"x": (0.0, 0.0), "y": (0.0, 0.0)}
        for attribute in ("x", "y"):
            values = [getattr(frame.pose, attribute) for frame in frames]
            floor, ceiling = min(values), max(values)
            low, high = self.extent(attribute)
            result[attribute] = (max(0.0, floor - low),
                                 max(0.0, high - ceiling))
        (x_before, x_after), (y_before, y_after) = result["x"], result["y"]
        return x_before, y_before, x_after, y_after

    @property
    def travel(self) -> Margins:
        x_low, x_high = self.extent("x")
        y_low, y_high = self.extent("y")
        return (max(0.0, -x_low), max(0.0, -y_low),
                max(0.0, x_high), max(0.0, y_high))

    def sweep(self, width: float, height: float) -> Margins:
        low, high = self.extent("rotate")
        return rotation_margins(width, height, low, high, self.origins)

    @property
    def blur_margin(self) -> Margins:
        reach = BLUR_REACH * self.max_blur
        return (reach, reach, reach, reach)

    def margins(self, width: float, height: float) -> Margins:
        return self.overflow

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

    def margins(self, width: float, height: float) -> Margins:
        return combine_margins(
            self.travel, self.sweep(width, height), self.blur_margin)
