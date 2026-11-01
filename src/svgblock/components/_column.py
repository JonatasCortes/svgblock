from .themes import ThemeData
from ._templates import RenderedComponent
from ._composer import DEFAULT_COLUMN_WEIGHT, Composer


class Column(Composer):
    def __init__(self, weight: float = DEFAULT_COLUMN_WEIGHT) -> None:
        super().__init__()
        if weight <= 0:
            raise ValueError(
                f"Column weight must be greater than zero, got {weight!r}.")
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    def render(self, theme: ThemeData, left: float, top: float, width: float) -> RenderedComponent:
        return self._render_components(theme, left, top, width)
