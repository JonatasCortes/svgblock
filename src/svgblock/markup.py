from dataclasses import dataclass
from enum import Enum


class Style(Enum):
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    ITALIC = "italic"


MARKERS: dict[str, Style] = {
    "**": Style.HIGHLIGHT,
    "__": Style.UNDERLINE,
    "--": Style.STRIKETHROUGH,
    "##": Style.ITALIC,
}
ESCAPE_CHARACTER = "\\"
ESCAPABLE_CHARACTERS = frozenset("".join(MARKERS) + ESCAPE_CHARACTER)

_MARKERS_LONGEST_FIRST = sorted(
    MARKERS, key=len, reverse=True)
_MARKER_OF_STYLE = {style: marker for marker, style in MARKERS.items()}


@dataclass(frozen=True)
class TextSegment:
    text: str
    styles: tuple[Style, ...] = ()

    @property
    def is_bold(self) -> bool:
        return Style.HIGHLIGHT in self.styles


def parse_markup(text: str) -> list[TextSegment]:
    segments: list[TextSegment] = []
    active_styles: list[Style] = []
    pending_characters: list[str] = []
    index = 0

    while index < len(text):
        character = text[index]
        next_character = text[index + 1] if index + 1 < len(text) else ""

        if character == ESCAPE_CHARACTER and next_character in ESCAPABLE_CHARACTERS:
            pending_characters.append(next_character)
            index += 2
            continue

        marker = _marker_at(text, index)
        if marker is None:
            pending_characters.append(character)
            index += 1
            continue

        _close_segment(segments, pending_characters, active_styles)
        _toggle(active_styles, MARKERS[marker])
        index += len(marker)

    if active_styles:
        marker = _MARKER_OF_STYLE[active_styles[0]]
        raise ValueError(
            f"Unclosed marker '{marker}' in: {text!r} "
            f"(use {ESCAPE_CHARACTER}{marker[0]} for a literal one)")
    _close_segment(segments, pending_characters, active_styles)
    return segments


def _marker_at(text: str, index: int) -> str | None:
    for marker in _MARKERS_LONGEST_FIRST:
        if text.startswith(marker, index):
            return marker
    return None


def _close_segment(
    segments: list[TextSegment], pending_characters: list[str], active_styles: list[Style]
) -> None:
    if pending_characters:
        segments.append(TextSegment(
            "".join(pending_characters), tuple(active_styles)))
        pending_characters.clear()


def _toggle(active_styles: list[Style], style: Style) -> None:
    if style in active_styles:
        active_styles.remove(style)
    else:
        active_styles.append(style)
