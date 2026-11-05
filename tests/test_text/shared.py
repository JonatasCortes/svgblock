from dataclasses import dataclass
from itertools import permutations
from svgblock import Style, TextSegment

ESCAPE_CHARACTER = "\\"


@dataclass(frozen=True)
class MarkupSyntax:
    """A public ``Style`` together with the marker that toggles it in markup text."""
    style: Style
    marker: str


ALL_MARKUP_SYNTAXES: tuple[MarkupSyntax, ...] = (
    MarkupSyntax(Style.HIGHLIGHT, "**"),
    MarkupSyntax(Style.UNDERLINE, "__"),
    MarkupSyntax(Style.STRIKETHROUGH, "--"),
    MarkupSyntax(Style.ITALIC, "##"),
)

ORDERED_MARKUP_SYNTAX_PAIRS: tuple[tuple[MarkupSyntax, MarkupSyntax], ...] = tuple(
    permutations(ALL_MARKUP_SYNTAXES, 2)
)

MARKER_CHARACTERS: tuple[str, ...] = tuple(
    sorted({character for syntax in ALL_MARKUP_SYNTAXES for character in syntax.marker})
)

ESCAPABLE_CHARACTERS: tuple[str, ...] = (*MARKER_CHARACTERS, ESCAPE_CHARACTER)


def markup_syntax_id(syntax: MarkupSyntax) -> str:
    """Return a readable pytest id for a registered markup."""
    return syntax.style.name.lower()


def wrap_in(syntax: MarkupSyntax, text: str) -> str:
    """Surround ``text`` with the marker of ``syntax`` on both sides."""
    return f"{syntax.marker}{text}{syntax.marker}"


def escape_every_character(text: str) -> str:
    """Prefix each character of ``text`` with the escape character."""
    return "".join(f"{ESCAPE_CHARACTER}{character}" for character in text)


def plain(text: str) -> TextSegment:
    """Build a segment without styles."""
    return TextSegment(text=text)


def styled(text: str, *styles: Style) -> TextSegment:
    """Build a segment carrying the given styles, in order."""
    return TextSegment(text=text, styles=styles)
