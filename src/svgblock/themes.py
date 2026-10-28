from typing import Final, TypedDict


class Theme(TypedDict):
    background_center: str
    background_edge: str
    border_start: str
    border_end: str
    title_text: str
    title_bar: str
    subsection_text: str
    subsection_marker: str
    text: str
    highlight: str
    table_background: str
    table_header_background: str
    table_header_text: str
    table_text: str
    table_divider: str
    table_stripe_background: str
    table_border: str
    divider: str


THEMES: Final[dict[str, Theme]] = {
    # ==========================================
    # 1. DARK COLORS
    # ==========================================
    "red": {
        "background_center": "#1A0A0A", "background_edge": "#0D0505",
        "border_start": "#E60012", "border_end": "#660008",
        "title_text": "#FF3344", "title_bar": "#E60012",
        "subsection_text": "#FF8A98", "subsection_marker": "#FF3344",
        "text": "#FFB3B3", "highlight": "#FF6677", "table_background": "#140808", "table_header_background": "#2A0D10",
        "table_header_text": "#FF3344", "table_text": "#FFB3B3",
        "table_divider": "#4D1A1F", "table_stripe_background": "#1F0B0D",
        "table_border": "#660008", "divider": "#B3202E",
    }
}
