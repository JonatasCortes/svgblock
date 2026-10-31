from dataclasses import dataclass
from typing import Protocol
from .themes import ThemeData


@dataclass(frozen=True)
class RenderedComponent:
    svg: str
    height: float


class Component(Protocol):
    def render(
        self, theme: ThemeData, left: float, top: float, width: float
    ) -> RenderedComponent: ...


class WeightedComponent(Component, Protocol):
    @property
    def weight(self) -> float: ...
