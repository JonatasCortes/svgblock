import base64
import struct
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_HEADER_CHUNK = b"IHDR"
PNG_MINIMUM_SIZE = 24

GIF_SIGNATURES = (b"GIF87a", b"GIF89a")
GIF_MINIMUM_SIZE = 10

JPEG_SIGNATURE = b"\xff\xd8"

_JPEG_FRAME_MARKERS = frozenset(
    {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
)
_JPEG_STANDALONE_MARKERS = frozenset({0x01, *range(0xD0, 0xD9)})
_JPEG_END_OF_IMAGE = 0xD9
_JPEG_START_OF_SCAN = 0xDA
_JPEG_FILL_BYTE = 0xFF


@dataclass(frozen=True)
class ImageData:
    data_uri: str
    width: int
    height: int


def read_image(path: str | Path) -> ImageData:
    content = Path(path).read_bytes()
    mime_type, width, height = _inspect(content, path)
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Image {str(path)!r} has invalid dimensions {width}x{height}.")
    encoded = base64.b64encode(content).decode("ascii")
    return ImageData(
        data_uri=f"data:{mime_type};base64,{encoded}",
        width=width,
        height=height,
    )


def _inspect(content: bytes, path: str | Path) -> tuple[str, int, int]:
    try:
        if content.startswith(PNG_SIGNATURE):
            return ("image/png", *_read_png_size(content))
        if content.startswith(GIF_SIGNATURES):
            return ("image/gif", *_read_gif_size(content))
        if content.startswith(JPEG_SIGNATURE):
            return ("image/jpeg", *_read_jpeg_size(content))
    except ValueError as error:
        raise ValueError(f"Invalid image {str(path)!r}: {error}") from None
    raise ValueError(
        f"Unsupported image format in {str(path)!r}. Supported: PNG, JPEG and GIF."
    )


def _read_png_size(content: bytes) -> tuple[int, int]:
    if len(content) < PNG_MINIMUM_SIZE or content[12:16] != PNG_HEADER_CHUNK:
        raise ValueError("corrupted PNG header.")
    width, height = struct.unpack(">II", content[16:24])
    return width, height


def _read_gif_size(content: bytes) -> tuple[int, int]:
    if len(content) < GIF_MINIMUM_SIZE:
        raise ValueError("corrupted GIF header.")
    width, height = struct.unpack("<HH", content[6:10])
    return width, height


def _read_jpeg_size(content: bytes) -> tuple[int, int]:
    position = len(JPEG_SIGNATURE)
    while position + 2 <= len(content):
        if content[position] != _JPEG_FILL_BYTE:
            break
        marker = content[position + 1]
        if marker == _JPEG_FILL_BYTE:
            position += 1
            continue
        position += 2
        if marker in _JPEG_STANDALONE_MARKERS:
            continue
        if marker in (_JPEG_END_OF_IMAGE, _JPEG_START_OF_SCAN):
            break
        if position + 2 > len(content):
            break
        (segment_length,) = struct.unpack(
            ">H", content[position: position + 2])
        if marker in _JPEG_FRAME_MARKERS:
            if position + 7 > len(content):
                break
            height, width = struct.unpack(
                ">HH", content[position + 3: position + 7])
            return width, height
        position += segment_length
    raise ValueError("could not find the JPEG dimensions.")
