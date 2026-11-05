import struct
import zlib
from pathlib import Path
from svgblock import Column
from svgblock import ThemeData, Theme
import xml.etree.ElementTree as ET


LEFT = 12.0
TOP = 30.0
WIDTH = 480.0

DEFAULT_COLUMN_WEIGHT = 1

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG_WRAPPER = f'<svg xmlns="{SVG_NAMESPACE}">{{content}}</svg>'


def make_column_with_dividers(count: int) -> Column:
    """Build a Column holding the given number of dividers."""
    column = Column()
    for _ in range(count):
        column.divider()
    return column


def render_column(
    column: Column,
    theme: ThemeData | None = None,
    left: float = LEFT,
    top: float = TOP,
    width: float = WIDTH,
):
    """Render a Column using the default test geometry."""
    if theme is None:
        theme = Theme.NEON.value
    return column.render(theme, left, top, width)


def measure_component_gap() -> float:
    """Derive the vertical gap between components from rendered heights."""
    single = render_column(make_column_with_dividers(1)).height
    double = render_column(make_column_with_dividers(2)).height
    return double - 2 * single


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    body = tag + data
    return (
        struct.pack(">I", len(data))
        + body
        + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    )


def build_png_bytes(width: int, height: int) -> bytes:
    """Build a PNG file of the given size filled with a single color."""
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    rows = (b"\x00" + b"\xff\x00\x00" * width) * height
    return (
        PNG_SIGNATURE
        + _png_chunk(b"IHDR", header)
        + _png_chunk(b"IDAT", zlib.compress(rows))
        + _png_chunk(b"IEND", b"")
    )


def build_gif_bytes(width: int, height: int, signature: bytes = b"GIF89a") -> bytes:
    """Build a GIF header followed by a trailer, with the given logical size."""
    return signature + struct.pack("<HH", width, height) + b"\x00\x00\x00;"


def build_jpeg_segment(marker: int, payload: bytes) -> bytes:
    """Build a JPEG segment with a length field, as used by APPn and DHT."""
    return bytes([0xFF, marker]) + struct.pack(">H", len(payload) + 2) + payload


def build_jpeg_bytes(
    width: int, height: int, marker: int = 0xC0, leading: bytes = b""
) -> bytes:
    """Build a JPEG whose frame header uses the given start-of-frame marker."""
    frame = struct.pack(">HBHHBBBB", 11, 8, height, width, 1, 1, 0x11, 0)
    return b"\xff\xd8" + leading + bytes([0xFF, marker]) + frame + b"\xff\xd9"


def write_image(directory: Path, name: str, content: bytes) -> Path:
    """Write raw bytes to a file and return its path."""
    path = directory / name
    path.write_bytes(content)
    return path


def write_minimal_png(directory: Path, name: str = "pixel.png") -> Path:
    """Write a valid 1x1 PNG file and return its path."""
    return write_image(directory, name, build_png_bytes(1, 1))


def parse_svg_fragment(svg: str) -> ET.Element:
    """Parse an SVG fragment by wrapping it in a namespaced svg element."""
    return ET.fromstring(SVG_WRAPPER.format(content=svg))


def find_images(svg: str) -> list[ET.Element]:
    """Return every image element found in an SVG fragment."""
    return parse_svg_fragment(svg).findall(f".//{{{SVG_NAMESPACE}}}image")
