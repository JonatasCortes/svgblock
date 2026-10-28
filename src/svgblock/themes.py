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
    # ==========================================
    # 1. DARK COLORS
    # ==========================================
    "red": {
        "background_center": "#1A0A0A", "background_edge": "#0D0505",
        "border_start": "#E60012", "border_end": "#660008",
        "title_text": "#FF3344", "title_bar": "#E60012",
        "subsection_text": "#FF8A98", "subsection_marker": "#FF3344",
        "text": "#FFB3B3", "highlight": "#FF6677",
    },
    "orange": {
        "background_center": "#24140B", "background_edge": "#140C07",
        "border_start": "#FB923C", "border_end": "#C2410C",
        "title_text": "#FDBA74", "title_bar": "#EA580C",
        "subsection_text": "#D6AE91", "subsection_marker": "#F97316",
        "text": "#FFEDD5", "highlight": "#FF8C42",
    },
    "yellow": {
        "background_center": "#211B0D", "background_edge": "#121008",
        "border_start": "#FDE047", "border_end": "#A16207",
        "title_text": "#FDE68A", "title_bar": "#D4A20A",
        "subsection_text": "#D6C99A", "subsection_marker": "#EAB308",
        "text": "#FEF3C7", "highlight": "#FFE44D",
    },
    "green": {
        "background_center": "#081F10", "background_edge": "#051209",
        "border_start": "#059669", "border_end": "#064E3B",
        "title_text": "#6EE7B7", "title_bar": "#10B981",
        "subsection_text": "#65A384", "subsection_marker": "#10B981",
        "text": "#A7F3D0", "highlight": "#34D399",
    },
    "blue": {
        "background_center": "#0F1B30", "background_edge": "#080F1F",
        "border_start": "#60A5FA", "border_end": "#1D4ED8",
        "title_text": "#7DD3FC", "title_bar": "#2563EB",
        "subsection_text": "#93B4D6", "subsection_marker": "#3B82F6",
        "text": "#BAE6FD", "highlight": "#38BDF8",
    },
    "purple": {
        "background_center": "#19112B", "background_edge": "#0D0918",
        "border_start": "#A78BFA", "border_end": "#5B21B6",
        "title_text": "#C4B5FD", "title_bar": "#8B5CF6",
        "subsection_text": "#B0A1D0", "subsection_marker": "#6D28D9",
        "text": "#DDD6FE", "highlight": "#C084FC",
    },
    "pink": {
        "background_center": "#1D101D", "background_edge": "#0D080F",
        "border_start": "#F472B6", "border_end": "#9D174D",
        "title_text": "#F9A8D4", "title_bar": "#BE185D",
        "subsection_text": "#D6A0C4", "subsection_marker": "#EC4899",
        "text": "#FBCFE8", "highlight": "#FF4FA3",
    },
    "obsidian": {
        "background_center": "#0F0F0F", "background_edge": "#050505",
        "border_start": "#525252", "border_end": "#171717",
        "title_text": "#FAFAFA", "title_bar": "#808080",
        "subsection_text": "#A3A3A3", "subsection_marker": "#5E5E5E",
        "text": "#D4D4D4", "highlight": "#E5E5E5",
    },

    # ==========================================
    # 2. LIGHT COLORS (PASTELS)
    # ==========================================
    "mint": {
        "background_center": "#DCFCE7", "background_edge": "#F0FDF4",
        "border_start": "#059669", "border_end": "#A7F3D0",
        "title_text": "#047857", "title_bar": "#10B981",
        "subsection_text": "#065F46", "subsection_marker": "#34D399",
        "text": "#064E3B", "highlight": "#0D9488",
    },
    "chocomint": {
        "background_center": "#D6F5E0", "background_edge": "#EAF8EF",
        "border_start": "#6B4226", "border_end": "#34D399",
        "title_text": "#6B4226", "title_bar": "#10B981",
        "subsection_text": "#5C4033", "subsection_marker": "#34D399",
        "text": "#4A2A18", "highlight": "#8C5A3C",
    },
    "lavender": {
        "background_center": "#E7E1F6", "background_edge": "#F3F0FA",
        "border_start": "#8B5CF6", "border_end": "#DDD6F3",
        "title_text": "#7C3AED", "title_bar": "#9B7BE0",
        "subsection_text": "#7E68C8", "subsection_marker": "#8B5CF6",
        "text": "#4C3A8A", "highlight": "#9333EA",
    },
    "peach": {
        "background_center": "#FFE6D5", "background_edge": "#FFF4EC",
        "border_start": "#F28B5B", "border_end": "#FFD3B8",
        "title_text": "#C2410C", "title_bar": "#F28B5B",
        "subsection_text": "#9A3412", "subsection_marker": "#E2531B",
        "text": "#7C2D12", "highlight": "#D9622B",
    },
    "sky": {
        "background_center": "#E0F2FE", "background_edge": "#F0F9FF",
        "border_start": "#0284C7", "border_end": "#BAE6FD",
        "title_text": "#0369A1", "title_bar": "#0EA5E9",
        "subsection_text": "#075985", "subsection_marker": "#0284C7",
        "text": "#0C4A6E", "highlight": "#38BDF8",
    },

    # ==========================================
    # 3. NATURE & SEASONS
    # ==========================================
    "spring": {
        "background_center": "#E8F5D6", "background_edge": "#F7FBEF",
        "border_start": "#8BC34A", "border_end": "#F8BBD0",
        "title_text": "#4C8A1F", "title_bar": "#7CB342",
        "subsection_text": "#33691E", "subsection_marker": "#8BC34A",
        "text": "#274E13", "highlight": "#E8467F",
    },
    "summer": {
        "background_center": "#FFEFC2", "background_edge": "#FFF8E1",
        "border_start": "#FF6B35", "border_end": "#00B4D8",
        "title_text": "#EA580C", "title_bar": "#FF9F1C",
        "subsection_text": "#B45309", "subsection_marker": "#00B4D8",
        "text": "#9A3412", "highlight": "#F97316",
    },
    "autumn": {
        "background_center": "#292D22", "background_edge": "#191A16",
        "border_start": "#D5A15E", "border_end": "#8D4937",
        "title_text": "#E0B66F", "title_bar": "#C18C52",
        "subsection_text": "#B5AD99", "subsection_marker": "#B96345",
        "text": "#E2D5B9", "highlight": "#D5A15E",
    },
    "winter": {
        "background_center": "#172033", "background_edge": "#0D1321",
        "border_start": "#7DD3FC", "border_end": "#1E293B",
        "title_text": "#7DD3FC", "title_bar": "#38A3E0",
        "subsection_text": "#CBD5E1", "subsection_marker": "#366480",
        "text": "#F1F5F9", "highlight": "#E0F2FE",
    },

    # ==========================================
    # 4. DRINKS
    # ==========================================
    "wine": {
        "background_center": "#2A0D17", "background_edge": "#16060C",
        "border_start": "#D4A94B", "border_end": "#6E0F2F",
        "title_text": "#D4A94B", "title_bar": "#B0123F",
        "subsection_text": "#E0B56F", "subsection_marker": "#B3194A",
        "text": "#F3E4C8", "highlight": "#FFD27A",
    },
    "beer": {
        "background_center": "#291E12", "background_edge": "#17110A",
        "border_start": "#D97706", "border_end": "#78350F",
        "title_text": "#F59E0B", "title_bar": "#D97706",
        "subsection_text": "#FDE68A", "subsection_marker": "#82560E",
        "text": "#FEF3C7", "highlight": "#FFF3C4",
    },
    "coffee": {
        "background_center": "#2C201C", "background_edge": "#1C1411",
        "border_start": "#8C6046", "border_end": "#4A3326",
        "title_text": "#B98F6C", "title_bar": "#A67B5B",
        "subsection_text": "#D9B38C", "subsection_marker": "#A0663A",
        "text": "#EADDD7", "highlight": "#E8D5C4",
    },
    "matcha": {
        "background_center": "#E5E9DD", "background_edge": "#F4F6F0",
        "border_start": "#5B704C", "border_end": "#D2DAC7",
        "title_text": "#5F7E4A", "title_bar": "#748C61",
        "subsection_text": "#4E6A3C", "subsection_marker": "#A3C48A",
        "text": "#3D4C35", "highlight": "#3D5A2B",
    },
    "berrymatcha": {
        "background_center": "#E5E9DD", "background_edge": "#F4F6F0",
        "border_start": "#5B704C", "border_end": "#E63946",
        "title_text": "#D62839", "title_bar": "#5F8B3C",
        "subsection_text": "#3D4C35", "subsection_marker": "#E63946",
        "text": "#2A3524", "highlight": "#FF4D6D",
    },
    "latte": {
        "background_center": "#F4EBDD", "background_edge": "#FDFBF7",
        "border_start": "#D4A373", "border_end": "#A9743B",
        "title_text": "#A8692B", "title_bar": "#C19A6B",
        "subsection_text": "#9A6B3E", "subsection_marker": "#D9A566",
        "text": "#5A3D21", "highlight": "#C97B2E",
    },

    # ==========================================
    # 5. COUNTRIES AND CULTURE
    # ==========================================
    "brazil": {
        "background_center": "#0B2B1E", "background_edge": "#071A12",
        "border_start": "#FACC15", "border_end": "#166534",
        "title_text": "#22C55E", "title_bar": "#17CF5B",
        "subsection_text": "#86EFAC", "subsection_marker": "#22C55E",
        "text": "#F0FDF4", "highlight": "#FEF08A",
    },
    "usa": {
        "background_center": "#152238", "background_edge": "#0A1128",
        "border_start": "#E61C38", "border_end": "#2563EB",
        "title_text": "#FF334B", "title_bar": "#E61C38",
        "subsection_text": "#C7D2E3", "subsection_marker": "#2563EB",
        "text": "#FFFFFF", "highlight": "#60A5FA",
    },
    "miami": {
        "background_center": "#002A4D", "background_edge": "#00152B",
        "border_start": "#00B4D8", "border_end": "#FF2E7E",
        "title_text": "#FF3D8B", "title_bar": "#FF2E7E",
        "subsection_text": "#FF6FA8", "subsection_marker": "#FF1F6B",
        "text": "#FFD60A", "highlight": "#00F5C4",
    },
    "france": {
        "background_center": "#151C2E", "background_edge": "#0A0E1A",
        "border_start": "#ED2939", "border_end": "#0055A5",
        "title_text": "#60A5FA", "title_bar": "#ED2939",
        "subsection_text": "#8E9BB0", "subsection_marker": "#3B82F6",
        "text": "#FFFFFF", "highlight": "#FF4D5E",
    },
    "india": {
        "background_center": "#182232", "background_edge": "#0D111A",
        "border_start": "#FF7A00", "border_end": "#059669",
        "title_text": "#FF8C00", "title_bar": "#FF7A00",
        "subsection_text": "#8C9BB0", "subsection_marker": "#10B981",
        "text": "#FFFFFF", "highlight": "#FFC266",
    },
    "china": {
        "background_center": "#240C12", "background_edge": "#120608",
        "border_start": "#DE2910", "border_end": "#8B0000",
        "title_text": "#FFD700", "title_bar": "#DE2910",
        "subsection_text": "#A68A80", "subsection_marker": "#FF3B30",
        "text": "#FFF5E6", "highlight": "#FFE766",
    },
    "mexico": {
        "background_center": "#11231A", "background_edge": "#0A140E",
        "border_start": "#00A859", "border_end": "#E4002B",
        "title_text": "#00D67E", "title_bar": "#00C26E",
        "subsection_text": "#7DF0B3", "subsection_marker": "#E4002B",
        "text": "#FFFFFF", "highlight": "#FF2D3F",
    },
    "fiesta": {
        "background_center": "#2A1020", "background_edge": "#170A14",
        "border_start": "#FF1493", "border_end": "#FFB800",
        "title_text": "#FF3FA4", "title_bar": "#FF1493",
        "subsection_text": "#FF7DD1", "subsection_marker": "#FFB800",
        "text": "#FFE600", "highlight": "#00E5A8",
    },
    "greece": {
        "background_center": "#EDF3FA", "background_edge": "#FAFAFA",
        "border_start": "#0D5EAF", "border_end": "#9CC3E8",
        "title_text": "#0D5EAF", "title_bar": "#0077B6",
        "subsection_text": "#1B4F8A", "subsection_marker": "#7FB8F0",
        "text": "#003A75", "highlight": "#0096C7",
    },
    "egypt": {
        "background_center": "#EADCA6", "background_edge": "#F7EED2",
        "border_start": "#C2A42D", "border_end": "#1B4A87",
        "title_text": "#1B4A87", "title_bar": "#C2A42D",
        "subsection_text": "#8A6A0A", "subsection_marker": "#1B4A87",
        "text": "#2B2311", "highlight": "#D4A82A",
    },
    "japandark": {
        "background_center": "#0A0A0A", "background_edge": "#000000",
        "border_start": "#BC002D", "border_end": "#333333",
        "title_text": "#E60033", "title_bar": "#BC002D",
        "subsection_text": "#FF6B87", "subsection_marker": "#6D061C",
        "text": "#FFFFFF", "highlight": "#FFB3C1",
    },
    "japanlight": {
        "background_center": "#E5E7EB", "background_edge": "#F8F9FA",
        "border_start": "#E60033", "border_end": "#990022",
        "title_text": "#BC002D", "title_bar": "#E60033",
        "subsection_text": "#374151", "subsection_marker": "#990022",
        "text": "#111827", "highlight": "#FF4D4D",
    },
    "sakura": {
        "background_center": "#1A1D2C", "background_edge": "#0F111A",
        "border_start": "#FF6B8B", "border_end": "#7C3AED",
        "title_text": "#FF9EAA", "title_bar": "#FF6B8B",
        "subsection_text": "#8A94A6", "subsection_marker": "#7C3AED",
        "text": "#F7F2EF", "highlight": "#FFD1DC",
    },

    # ==========================================
    # 6. AESTHETICS & CULTURE
    # ==========================================
    "neon": {
        "background_center": "#121324", "background_edge": "#080811",
        "border_start": "#FF0055", "border_end": "#7000FF",
        "title_text": "#FF0055", "title_bar": "#7000FF",
        "subsection_text": "#A3A7C9", "subsection_marker": "#FF0055",
        "text": "#FFFFFF", "highlight": "#00F0FF",
    },
    "cyberpunk": {
        "background_center": "#180538", "background_edge": "#0D0221",
        "border_start": "#FF007F", "border_end": "#2B00FF",
        "title_text": "#FF007F", "title_bar": "#2B00FF",
        "subsection_text": "#FF7CC9", "subsection_marker": "#FF007F",
        "text": "#0FF0FC", "highlight": "#00FF41",
    },
    "steampunk": {
        "background_center": "#29211D", "background_edge": "#1A1512",
        "border_start": "#8B4513", "border_end": "#3E2723",
        "title_text": "#C27A2E", "title_bar": "#8B4513",
        "subsection_text": "#E3B26B", "subsection_marker": "#A36329",
        "text": "#D4A373", "highlight": "#E6C287",
    },
    "synthwave": {
        "background_center": "#240046", "background_edge": "#130026",
        "border_start": "#7B2CBF", "border_end": "#FF006E",
        "title_text": "#05FFA1", "title_bar": "#7B2CBF",
        "subsection_text": "#FFB3F7", "subsection_marker": "#F425F4",
        "text": "#FF71CE", "highlight": "#F9A11B",
    },
    "lofi": {
        "background_center": "#323247", "background_edge": "#27273A",
        "border_start": "#8B5CF6", "border_end": "#4C1D95",
        "title_text": "#A78BFA", "title_bar": "#8B5CF6",
        "subsection_text": "#C4B5FD", "subsection_marker": "#8B6CE0",
        "text": "#E2D9F3", "highlight": "#5EEAD4",
    },

    # ==========================================
    # 7. CLASSICAL UI
    # ==========================================
    "dracula": {
        "background_center": "#343746", "background_edge": "#282A36",
        "border_start": "#50FA7B", "border_end": "#BD93F9",
        "title_text": "#FF79C6", "title_bar": "#BD93F9",
        "subsection_text": "#B8B9C9", "subsection_marker": "#FF79C6",
        "text": "#F8F8F2", "highlight": "#8BE9FD",
    },
    "mocha": {
        "background_center": "#242438", "background_edge": "#1E1E2E",
        "border_start": "#89DCEB", "border_end": "#CBA6F7",
        "title_text": "#F5C2E7", "title_bar": "#CBA6F7",
        "subsection_text": "#A6ADC8", "subsection_marker": "#89B4FA",
        "text": "#CDD6F4", "highlight": "#94E2D5",
    },
    "nord": {
        "background_center": "#3B4252", "background_edge": "#2E3440",
        "border_start": "#81A1C1", "border_end": "#434C5E",
        "title_text": "#88C0D0", "title_bar": "#81A1C1",
        "subsection_text": "#B7E3EA", "subsection_marker": "#5AA3BA",
        "text": "#ECEFF4", "highlight": "#A3BE8C",
    },
    "solarizeddark": {
        "background_center": "#073642", "background_edge": "#002B36",
        "border_start": "#CB4B16", "border_end": "#002B36",
        "title_text": "#B58900", "title_bar": "#CB4B16",
        "subsection_text": "#839496", "subsection_marker": "#FFD866",
        "text": "#93A1A1", "highlight": "#2AA198",
    },
    "solarizedlight": {
        "background_center": "#EEE8D5", "background_edge": "#FDF6E3",
        "border_start": "#2AA198", "border_end": "#CCC5B2",
        "title_text": "#268BD2", "title_bar": "#2AA198",
        "subsection_text": "#8FC8F2", "subsection_marker": "#1F6FB8",
        "text": "#586E75", "highlight": "#D33682",
    },
    "atlas": {
        "background_center": "#151E35", "background_edge": "#0B1020",
        "border_start": "#8299D4", "border_end": "#62528F",
        "title_text": "#E8C878", "title_bar": "#718FD8",
        "subsection_text": "#929FB9", "subsection_marker": "#6F8CCF",
        "text": "#D9E4F2", "highlight": "#F6E3B0",
    },
    "heaven": {
        "background_center": "#E6F1FC", "background_edge": "#F4F9FF",
        "border_start": "#38BDF8", "border_end": "#FFC83D",
        "title_text": "#0B6FC2", "title_bar": "#38BDF8",
        "subsection_text": "#3B5BA9", "subsection_marker": "#5BB8F5",
        "text": "#1E3A8A", "highlight": "#FFB300",
    },
    "hell": {
        "background_center": "#170505", "background_edge": "#0A0303",
        "border_start": "#FF3300", "border_end": "#4D0000",
        "title_text": "#E01010", "title_bar": "#CC0000",
        "subsection_text": "#FF7A45", "subsection_marker": "#D40000",
        "text": "#FF6600", "highlight": "#FF9900",
    },
    "abyss": {
        "background_center": "#021226", "background_edge": "#010A14",
        "border_start": "#0077B6", "border_end": "#01050A",
        "title_text": "#00B4D8", "title_bar": "#0077B6",
        "subsection_text": "#7DF0FF", "subsection_marker": "#0096C7",
        "text": "#64FFDA", "highlight": "#B5FFEE",
    },
}
