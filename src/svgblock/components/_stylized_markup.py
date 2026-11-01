from .text import TextSegment, Style, calculate_line_height, calculate_baseline
from .themes import ThemeData
from xml.sax.saxutils import escape
from .themes import ThemeData


def bold_lines_markup(lines: list[str], x: float, top: float, font_size: float, fill: str) -> str:
    line_height = calculate_line_height(font_size)
    return "".join(
        svg_text_markup(
            x=x,
            baseline=calculate_baseline(top + index * line_height, font_size),
            font_size=font_size,
            fill=fill,
            content=escape(line),
            bold=True,
        )
        for index, line in enumerate(lines)
        if line
    )


def svg_text_markup(
    x: float,
    baseline: float,
    font_size: float,
    fill: str,
    content: str,
    bold: bool = False,
    bold_weight: int = 700,
    anchor: str = "start",
) -> str:
    weight = f' font-weight="{bold_weight}"' if bold else ""
    anchor_attribute = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.1f}" y="{baseline:.1f}" font-size="{font_size:g}" '
        f'fill="{fill}"{weight}{anchor_attribute}>{content}</text>'
    )


def segments_markup(segments: list[TextSegment], theme: ThemeData) -> str:
    return "".join(_segment_markup(segment, theme) for segment in segments)


def _segment_markup(segment: TextSegment, theme: ThemeData, bold_weight: int = 700) -> str:
    content = escape(segment.text)
    if not segment.styles:
        return content

    innermost_style = segment.styles[-1]
    attributes = [f'fill="{_style_color(theme, innermost_style)}"']
    if segment.is_bold:
        attributes.append(f'font-weight="{bold_weight}"')
    if Style.ITALIC in segment.styles:
        attributes.append('font-style="italic"')
    decorations = _text_decorations(segment.styles)
    if decorations:
        attributes.append(f'text-decoration="{decorations}"')
    return f'<tspan {" ".join(attributes)}>{content}</tspan>'


def _style_color(theme: ThemeData, style: Style) -> str:
    colors: dict[Style, str] = {
        Style.HIGHLIGHT: theme["highlight"],
        Style.UNDERLINE: theme["underline"],
        Style.STRIKETHROUGH: theme["strikethrough"],
        Style.ITALIC: theme["italic"],
    }
    return colors[style]


def _text_decorations(styles: tuple[Style, ...]) -> str:
    decorations: list[str] = []
    if Style.UNDERLINE in styles:
        decorations.append("underline")
    if Style.STRIKETHROUGH in styles:
        decorations.append("line-through")
    return " ".join(decorations)
