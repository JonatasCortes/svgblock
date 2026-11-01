from ._markup import Style, TextSegment, parse_markup
from ._parser import wrap_into_lines, wrap_bold_text
from ._width import measure_text_width


def calculate_line_height(font_size: float) -> float:
    LINE_HEIGHT_RATIO = 1.5
    return font_size * LINE_HEIGHT_RATIO


def calculate_baseline(top: float, font_size: float) -> float:
    BASELINE_RATIO = 1.1
    return top + font_size * BASELINE_RATIO


__all__: list[str] = ["Style", "TextSegment", "parse_markup",
                      "wrap_into_lines", "wrap_bold_text",
                      "measure_text_width", "calculate_line_height",
                      "calculate_baseline"]
