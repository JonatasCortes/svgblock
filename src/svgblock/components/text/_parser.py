import re
from dataclasses import dataclass
from ._markup import TextSegment
from ._width import measure_text_width


@dataclass(frozen=True)
class _Word:
    pieces: tuple[TextSegment, ...]
    trailing_spaces: tuple[TextSegment, ...]


def wrap_bold_text(text: str, font_size: float, max_width: float) -> list[str]:
    segments = [TextSegment(text=text)]
    lines = wrap_into_lines(segments, font_size, max_width, bold=True)
    return ["".join(segment.text for segment in line) for line in lines] or [""]


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
    spaces: list[TextSegment] = []
    for segment in segments:
        for part in re.compile(r"\s+|\S+").findall(segment.text):
            piece = TextSegment(text=part, styles=segment.styles)
            if part.isspace():
                spaces.append(piece)
                continue
            if not pieces:
                pieces, spaces = spaces, []
            elif spaces:
                words.append(_Word(tuple(pieces), tuple(spaces)))
                pieces, spaces = [], []
            pieces.append(piece)
    if pieces:
        words.append(_Word(tuple(pieces), tuple(spaces)))
    return words


def _break_oversized_word(
    word: _Word, font_size: float, max_width: float, bold: bool
) -> list[_Word]:
    word_width = sum(
        measure_text_width(piece.text, font_size,
                           bold=bold or piece.is_bold)
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
                character, font_size, bold=bold or piece.is_bold
            )
            if current and current_width + character_width > max_width:
                fragments.append(current)
                current = []
                current_width = 0.0
            current.append(TextSegment(text=character, styles=piece.styles))
            current_width += character_width
    fragments.append(current)

    merged = [tuple(_merge_adjacent_segments(fragment))
              for fragment in fragments]
    result = [_Word(pieces=pieces, trailing_spaces=())
              for pieces in merged[:-1]]
    result.append(
        _Word(pieces=merged[-1], trailing_spaces=word.trailing_spaces))
    return result


def _flatten_line(words: list[_Word]) -> list[TextSegment]:
    segments: list[TextSegment] = []
    for word in words[:-1]:
        segments.extend(word.pieces)
        segments.extend(word.trailing_spaces)
    segments.extend(words[-1].pieces)
    return segments


def _merge_adjacent_segments(segments: list[TextSegment]) -> list[TextSegment]:
    merged: list[TextSegment] = []
    for segment in segments:
        if merged and merged[-1].styles == segment.styles:
            merged[-1] = TextSegment(
                merged[-1].text + segment.text, segment.styles
            )
        else:
            merged.append(segment)
    return merged


def _measure_line(words: list[_Word], font_size: float, bold: bool) -> float:
    return sum(
        measure_text_width(segment.text, font_size,
                           bold=bold or segment.is_bold)
        for segment in _flatten_line(words)
    )
