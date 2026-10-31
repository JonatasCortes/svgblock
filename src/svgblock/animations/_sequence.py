from dataclasses import dataclass
from functools import cached_property

from ._base import (
    MAX_SEGMENTS,
    BaseAnimation,
    Expansion,
    Keyframe,
    Layer,
    RepeatableAnimation,
    Segment,
    check_loop_limit,
)
from ._easing import Linear

_JUMP = 1e-6


def _total(segments: tuple[Segment, ...]) -> float:
    return sum(segment.duration for segment in segments)


def _compile(segments: tuple[Segment, ...]) -> tuple[Keyframe, ...]:
    total = _total(segments)
    frames: list[Keyframe] = []
    start = 0.0
    last = len(segments) - 1
    for index, segment in enumerate(segments):
        for keyframe in segment.keyframes:
            at = (start + keyframe.at * segment.duration) / total
            ends_segment = keyframe.at >= 1
            if ends_segment and index < last:
                at -= _JUMP
            frames.append(Keyframe(
                at, keyframe.pose, None if ends_segment else segment.easing))
        start += segment.duration
    return tuple(frames)


def _layer(name: str, segments: tuple[Segment, ...], *, iterations: int | None,
           delay: float = 0.0, fill: str = "both") -> Layer:
    return Layer(
        name=name,
        keyframes=_compile(segments),
        duration=_total(segments),
        easing=Linear(),
        iterations=iterations,
        delay=delay,
        fill=fill,
    )


@dataclass(frozen=True, init=False)
class Sequence(RepeatableAnimation):
    steps: tuple[BaseAnimation, ...] = ()

    def __init__(self, *steps: BaseAnimation,
                 loop_limit: int | None = 0) -> None:
        check_loop_limit(loop_limit)
        object.__setattr__(self, "steps", steps)
        object.__setattr__(self, "loop_limit", loop_limit)
        object.__setattr__(self, "easing", Linear())
        object.__setattr__(self, "duration", self._body.playing_time)

    @cached_property
    def _body(self) -> Expansion:
        head: list[Segment] = []
        cycle: tuple[Segment, ...] | None = None
        infinite_step: int | None = None
        for number, step in enumerate(self.steps, start=1):
            expansion = step.expand()
            if infinite_step is not None:
                if expansion.playing_time > 0:
                    raise ValueError(
                        f"Step {number} of the sequence would never play, "
                        f"because step {infinite_step} is infinite. Only the "
                        "last step of a sequence can be infinite."
                    )
                continue
            head.extend(expansion.head)
            if expansion.cycle is not None:
                cycle = expansion.cycle
                infinite_step = number
            if len(head) + len(cycle or ()) > MAX_SEGMENTS:
                raise ValueError(
                    "This sequence repeats too much: once its repetitions are "
                    f"unrolled it has more than {MAX_SEGMENTS} steps. Reduce a "
                    "loop_limit or use None for no limit."
                )
        return Expansion(tuple(head), cycle)

    @property
    def is_infinite(self) -> bool:
        body = self._body
        if body.cycle is not None:
            return True
        return self.loop_limit is None and bool(body.head)

    @property
    def max_scale(self) -> float:
        return max([1.0, *(step.max_scale for step in self.steps)])

    def keyframes(self) -> list[Keyframe]:
        body = self._body
        segments = body.head + (body.cycle or ())
        return list(_compile(segments)) if segments else []

    def expand(self) -> Expansion:
        body = self._body
        if body.cycle is not None:
            return body
        if not body.head:
            return Expansion()
        if self.loop_limit is None:
            return Expansion(cycle=body.head)
        runs = self.loop_limit + 1
        if len(body.head) * runs > MAX_SEGMENTS:
            raise ValueError(
                "This sequence repeats too much: unrolled, it would have "
                f"{len(body.head) * runs} steps (the limit is {MAX_SEGMENTS}). "
                "Reduce a loop_limit or use None for no limit."
            )
        return Expansion(head=body.head * runs)

    def segment(self) -> Segment:
        raise TypeError(
            "A sequence is expanded, not played as a single segment.")

    def layers(self) -> list[Layer]:
        body = self._body
        name = self.css_name

        if body.cycle is not None:
            layers: list[Layer] = []
            if body.head:
                layers.append(_layer(name, body.head, iterations=1))
            layers.append(_layer(
                f"{name}-loop", body.cycle, iterations=None,
                delay=_total(body.head), fill="forwards"))
            return layers

        if not body.head:
            return []
        return [_layer(name, body.head, iterations=self.iterations)]
