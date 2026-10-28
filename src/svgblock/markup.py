import re
from collections.abc import Sequence
from dataclasses import dataclass

HIGHLIGHT_MARKER = "**"
ESCAPE_CHARACTER = "\\"
ESCAPED_ASTERISK = ESCAPE_CHARACTER + "*"

_UNESCAPED_MARKER = re.compile(
    rf"(?<!{re.escape(ESCAPE_CHARACTER)}){re.escape(HIGHLIGHT_MARKER)}"
)


@dataclass(frozen=True)
class TextSegment:
    text: str
    highlighted: bool


def parse_highlights(text: str, highlighted_words: Sequence[str] = ()) -> list[TextSegment]:
    segments = _parse_marked_highlights(text)
    return _highlight_words(segments, highlighted_words)


def _parse_marked_highlights(text: str) -> list[TextSegment]:
    parts = _UNESCAPED_MARKER.split(text)
    if len(parts) % 2 == 0:
        raise ValueError(
            f"Unclosed highlight marker '{HIGHLIGHT_MARKER}' in: {text!r}")
    return [
        TextSegment(text=part.replace(ESCAPED_ASTERISK, "*"),
                    highlighted=index % 2 == 1)
        for index, part in enumerate(parts)
        if part
    ]


def _highlight_words(
    segments: list[TextSegment], highlighted_words: Sequence[str]
) -> list[TextSegment]:
    word_pattern = _build_word_pattern(highlighted_words)
    if word_pattern is None:
        return segments

    result: list[TextSegment] = []
    for segment in segments:
        if segment.highlighted:
            result.append(segment)
        else:
            result.extend(_split_by_words(segment.text, word_pattern))
    return result


def _build_word_pattern(highlighted_words: Sequence[str]) -> re.Pattern[str] | None:
    longest_first = sorted(
        {word for word in highlighted_words if word}, key=len, reverse=True)
    if not longest_first:
        return None
    return re.compile("(" + "|".join(re.escape(word) for word in longest_first) + ")")


def _split_by_words(text: str, word_pattern: re.Pattern[str]) -> list[TextSegment]:
    parts = word_pattern.split(text)
    return [
        TextSegment(text=part, highlighted=index % 2 == 1)
        for index, part in enumerate(parts)
        if part
    ]
