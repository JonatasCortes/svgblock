import re
from dataclasses import dataclass

from .markup import TextSegment
from .width_guard import measure_text_width

_WORD_OR_SPACE = re.compile(r"\s+|\S+")


@dataclass(frozen=True)
class _Word:
    pieces: tuple[TextSegment, ...]
    trailing_space: TextSegment | None


def wrap_into_lines(
    segments: list[TextSegment],
    font_size: float,
    max_width: float,
    bold: bool = False,
) -> list[list[TextSegment]]:
    words = [
        fragment
        for word in _split_into_words(segments)
        for fragment in _break_oversized_word(word, font_size, max_width, bold)
    ]
    lines: list[list[TextSegment]] = []
    current_line: list[_Word] = []
    for word in words:
        line_with_word = [*current_line, word]
        if current_line and _measure_line(line_with_word, font_size, bold) > max_width:
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


def _break_oversized_word(
    word: _Word, font_size: float, max_width: float, bold: bool
) -> list[_Word]:
    word_width = sum(
        measure_text_width(piece.text, font_size,
                           bold=bold or piece.highlighted)
        for piece in word.pieces
    )
    if word_width <= max_width:
        return [word]

    fragments: list[list[TextSegment]] = []
    current: list[TextSegment] = []
    current_width = 0.0
    for piece in word.pieces:
        for character in piece.text:
            character_width = measure_text_width(
                character, font_size, bold=bold or piece.highlighted
            )
            if current and current_width + character_width > max_width:
                fragments.append(current)
                current = []
                current_width = 0.0
            current.append(TextSegment(
                text=character, highlighted=piece.highlighted))
            current_width += character_width
    fragments.append(current)

    merged = [tuple(_merge_adjacent_segments(fragment))
              for fragment in fragments]
    result = [_Word(pieces=pieces, trailing_space=None)
              for pieces in merged[:-1]]
    result.append(_Word(pieces=merged[-1], trailing_space=word.trailing_space))
    return result


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
            merged[-1] = TextSegment(
                merged[-1].text + segment.text, segment.highlighted
            )
        else:
            merged.append(segment)
    return merged


def _measure_line(words: list[_Word], font_size: float, bold: bool) -> float:
    return sum(
        measure_text_width(segment.text, font_size,
                           bold=bold or segment.highlighted)
        for segment in _flatten_line(words)
    )
