import re
from dataclasses import dataclass
from markup import TextSegment
from width_guard import measure_text_width

_WORD_OR_SPACE = re.compile(r"\s+|\S+")


@dataclass(frozen=True)
class _Word:
    pieces: tuple[TextSegment, ...]
    trailing_space: TextSegment | None


def wrap_into_lines(segments: list[TextSegment], font_size: float, max_width: float) -> list[list[TextSegment]]:
    lines: list[list[TextSegment]] = []
    current_line: list[_Word] = []
    for word in _split_into_words(segments):
        line_with_word = [*current_line, word]
        if current_line and _measure_line(line_with_word, font_size) > max_width:
            lines.append(_merge_adjacent_segments(_flatten_line(current_line)))
            current_line = []
        current_line.append(word)
    if current_line:
        lines.append(_merge_adjacent_segments(_flatten_line(current_line)))
    return lines


def _split_into_words(segments: list[TextSegment]) -> list[_Word]:
    words: list[_Word] = []
    pieces: list[TextSegment] = []
    for segment in segments:
        for part in _WORD_OR_SPACE.findall(segment.text):
            piece = TextSegment(text=part, highlighted=segment.highlighted)
            if not part.isspace():
                pieces.append(piece)
            elif pieces:
                words.append(_Word(pieces=tuple(pieces), trailing_space=piece))
                pieces = []
    if pieces:
        words.append(_Word(pieces=tuple(pieces), trailing_space=None))
    return words


def _flatten_line(words: list[_Word]) -> list[TextSegment]:
    segments: list[TextSegment] = []
    for word in words[:-1]:
        segments.extend(word.pieces)
        if word.trailing_space:
            segments.append(word.trailing_space)
    segments.extend(words[-1].pieces)
    return segments


def _merge_adjacent_segments(segments: list[TextSegment]) -> list[TextSegment]:
    merged: list[TextSegment] = []
    for segment in segments:
        if merged and merged[-1].highlighted == segment.highlighted:
            merged[-1] = TextSegment(merged[-1].text +
                                     segment.text, segment.highlighted)
        else:
            merged.append(segment)
    return merged


def _measure_line(words: list[_Word], font_size: float) -> float:
    return sum(
        measure_text_width(segment.text, font_size, bold=segment.highlighted)
        for segment in _flatten_line(words)
    )
