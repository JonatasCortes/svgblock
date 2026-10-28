from typing import Final, TypedDict


class Theme(TypedDict):
    background_center: str    # center of the radial background glow
    background_edge: str      # outer color of the radial background
    border_start: str         # block border gradient start
    border_end: str           # block border gradient end
    title_text: str           # title text
    title_bar: str            # side bar next to the title
    subsection_text: str      # subsection text
    subsection_marker: str    # dot next to the subsection
    text: str                 # regular text
    highlight: str            # highlighted words


THEMES: Final[dict[str, Theme]] = {
    "red": {
        "background_center": "#2B0A0E", "background_edge": "#0D0505",
        "border_start": "#E60012", "border_end": "#660008",
        "title_text": "#FF3344", "title_bar": "#FF3344",
        "subsection_text": "#FF6677", "subsection_marker": "#FF3344",
        "text": "#FFB3B3", "highlight": "#FFFFFF",
    },
}
