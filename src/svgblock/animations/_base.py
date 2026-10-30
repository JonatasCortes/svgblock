import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose:
    opacity: float = 1.0
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0


REST = Pose()


@dataclass(frozen=True)
class Keyframe:
    at: float
    pose: Pose


@dataclass(frozen=True, kw_only=True)
class BaseAnimation(ABC):
    duration: float = 0.8
    easing: str = "ease-out"

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError(
                f"duration must be greater than 0, got {self.duration!r}.")

    @abstractmethod
    def keyframes(self) -> list[Keyframe]:
        pass

    @property
    def max_scale(self) -> float:
        """Maior tamanho que o bloco atinge (1 = nunca passa do normal)."""
        return max(1.0, *(keyframe.pose.scale for keyframe in self.keyframes()))

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


@dataclass(frozen=True, kw_only=True)
class RepeatableAnimation(BaseAnimation, ABC):
    loop_limit: int | None = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.loop_limit is not None and self.loop_limit < 0:
            raise ValueError(
                "loop_limit must be 0 or more, or None for no limit, "
                f"got {self.loop_limit!r}."
            )

    @property
    def iterations(self) -> int | None:
        if self.loop_limit is None:
            return None
        return self.loop_limit + 1
