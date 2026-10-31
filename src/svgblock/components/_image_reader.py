import base64
import struct
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_PNG_HEADER_CHUNK = b"IHDR"
_PNG_MINIMUM_SIZE = 24

_GIF_SIGNATURES = (b"GIF87a", b"GIF89a")
_GIF_MINIMUM_SIZE = 10

_JPEG_SIGNATURE = b"\xff\xd8"
_JPEG_FILL_BYTE = 0xFF
_JPEG_END_OF_IMAGE = 0xD9
_JPEG_START_OF_SCAN = 0xDA
_JPEG_STANDALONE_MARKERS = frozenset({0x01, *range(0xD0, 0xD9)})
_JPEG_FRAME_MARKERS = frozenset(
    {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
)
_JPEG_FRAME_MINIMUM_SIZE = 7
_JPEG_DIMENSIONS_NOT_FOUND = "could not find the JPEG dimensions."

Size = tuple[int, int]


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
    return ImageData(f"data:{mime_type};base64,{encoded}", width, height)


def _inspect(content: bytes, path: str | Path) -> tuple[str, int, int]:
    for signature, mime_type, read_size in _FORMATS:
        if content.startswith(signature):
            return mime_type, *_read_size_or_raise(read_size, content, path)
    raise ValueError(
        f"Unsupported image format in {str(path)!r}. Supported: PNG, JPEG and GIF."
    )


def _read_size_or_raise(
    read_size: Callable[[bytes], Size], content: bytes, path: str | Path
) -> Size:
    try:
        return read_size(content)
    except ValueError as error:
        raise ValueError(f"Invalid image {str(path)!r}: {error}") from None


def _read_png_size(content: bytes) -> Size:
    if len(content) < _PNG_MINIMUM_SIZE or content[12:16] != _PNG_HEADER_CHUNK:
        raise ValueError("corrupted PNG header.")
    return struct.unpack(">II", content[16:24])


def _read_gif_size(content: bytes) -> Size:
    if len(content) < _GIF_MINIMUM_SIZE:
        raise ValueError("corrupted GIF header.")
    return struct.unpack("<HH", content[6:10])


def _read_jpeg_size(content: bytes) -> Size:
    for marker, payload_start in _jpeg_segments(content):
        if marker in _JPEG_FRAME_MARKERS:
            return _read_jpeg_frame_size(content, payload_start)
    raise ValueError(_JPEG_DIMENSIONS_NOT_FOUND)


def _jpeg_segments(content: bytes) -> Iterator[tuple[int, int]]:
    position = len(_JPEG_SIGNATURE)
    while position + 2 <= len(content) and content[position] == _JPEG_FILL_BYTE:
        marker = content[position + 1]
        if marker == _JPEG_FILL_BYTE:
            position += 1
            continue

        position += 2
        if marker in _JPEG_STANDALONE_MARKERS:
            continue
        if marker in (_JPEG_END_OF_IMAGE, _JPEG_START_OF_SCAN):
            return
        if position + 2 > len(content):
            return

        yield marker, position
        (segment_length,) = struct.unpack(
            ">H", content[position: position + 2])
        position += segment_length


def _read_jpeg_frame_size(content: bytes, payload_start: int) -> Size:
    if payload_start + _JPEG_FRAME_MINIMUM_SIZE > len(content):
        raise ValueError(_JPEG_DIMENSIONS_NOT_FOUND)
    height, width = struct.unpack(
        ">HH", content[payload_start + 3: payload_start + 7])
    return width, height


_FORMATS: tuple[tuple[bytes | tuple[bytes, ...], str, Callable[[bytes], Size]], ...] = (
    (_PNG_SIGNATURE, "image/png", _read_png_size),
    (_GIF_SIGNATURES, "image/gif", _read_gif_size),
    (_JPEG_SIGNATURE, "image/jpeg", _read_jpeg_size),
)
