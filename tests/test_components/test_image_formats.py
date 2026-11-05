import base64
import re
from pathlib import Path

import pytest

from svgblock.components import Column

from .shared import (
    PNG_SIGNATURE,
    build_gif_bytes,
    build_jpeg_bytes,
    build_jpeg_segment,
    build_png_bytes,
    find_images,
    render_column,
    write_image,
)

WIDE_AVAILABLE_WIDTH = 10_000.0
JPEG_DIMENSIONS_MESSAGE = "could not find the JPEG dimensions"

FORMAT_SAMPLES = [
    pytest.param(build_png_bytes(2, 2), "image/png", id="png"),
    pytest.param(build_gif_bytes(2, 2), "image/gif", id="gif"),
    pytest.param(build_jpeg_bytes(2, 2), "image/jpeg", id="jpeg"),
]

CORRUPTED_FILES = [
    pytest.param(PNG_SIGNATURE, "corrupted PNG header", id="png-truncated"),
    pytest.param(
        build_png_bytes(1, 1).replace(b"IHDR", b"XXXX", 1),
        "corrupted PNG header",
        id="png-wrong-first-chunk",
    ),
    pytest.param(b"GIF89a\x01\x00", "corrupted GIF header",
                 id="gif-truncated"),
    pytest.param(b"\xff\xd8", JPEG_DIMENSIONS_MESSAGE,
                 id="jpeg-signature-only"),
    pytest.param(b"\xff\xd8\xff", JPEG_DIMENSIONS_MESSAGE,
                 id="jpeg-cut-marker"),
    pytest.param(b"\xff\xd8\xff\xe0", JPEG_DIMENSIONS_MESSAGE,
                 id="jpeg-cut-segment"),
    pytest.param(
        b"\xff\xd8\x00\x00\x00\x00", JPEG_DIMENSIONS_MESSAGE, id="jpeg-no-marker"
    ),
    pytest.param(
        b"\xff\xd8\xff\xd9", JPEG_DIMENSIONS_MESSAGE, id="jpeg-end-before-frame"
    ),
    pytest.param(
        b"\xff\xd8\xff\xda\x00\x02", JPEG_DIMENSIONS_MESSAGE, id="jpeg-scan-before-frame"
    ),
    pytest.param(
        b"\xff\xd8\xff\xc0\x00\x0b\x08", JPEG_DIMENSIONS_MESSAGE, id="jpeg-cut-frame"
    ),
]

ZERO_DIMENSION_FILES = [
    pytest.param(build_png_bytes(0, 5), "0x5", id="png-zero-width"),
    pytest.param(build_png_bytes(5, 0), "5x0", id="png-zero-height"),
    pytest.param(build_gif_bytes(0, 5), "0x5", id="gif-zero-width"),
    pytest.param(build_gif_bytes(5, 0), "5x0", id="gif-zero-height"),
    pytest.param(build_jpeg_bytes(0, 5), "0x5", id="jpeg-zero-width"),
    pytest.param(build_jpeg_bytes(5, 0), "5x0", id="jpeg-zero-height"),
]


def read_natural_size(path: Path) -> tuple[float, float]:
    """Return the size at which an image is drawn when nothing constrains it."""
    rendered = render_column(Column().image(path), width=WIDE_AVAILABLE_WIDTH)
    image = find_images(rendered.svg)[0]
    return float(image.attrib["width"]), float(image.attrib["height"])


class TestNaturalSize:
    @pytest.mark.parametrize("width, height", [(1, 1), (30, 20), (7, 300)])
    def test_png_size_is_read_from_the_header(
        self, tmp_path: Path, width: int, height: int
    ) -> None:
        path = write_image(tmp_path, "image.png",
                           build_png_bytes(width, height))

        assert read_natural_size(path) == (width, height)

    @pytest.mark.parametrize("signature", [b"GIF87a", b"GIF89a"])
    @pytest.mark.parametrize("width, height", [(1, 1), (30, 20), (7, 300)])
    def test_gif_size_is_read_from_the_header(
        self, tmp_path: Path, signature: bytes, width: int, height: int
    ) -> None:
        path = write_image(
            tmp_path, "image.gif", build_gif_bytes(width, height, signature)
        )

        assert read_natural_size(path) == (width, height)

    @pytest.mark.parametrize(
        "marker", [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6,
                   0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]
    )
    def test_jpeg_size_is_read_from_every_start_of_frame_marker(
        self, tmp_path: Path, marker: int
    ) -> None:
        path = write_image(tmp_path, "image.jpg",
                           build_jpeg_bytes(40, 25, marker))

        assert read_natural_size(path) == (40, 25)

    def test_jpeg_size_is_not_swapped_for_portrait_images(self, tmp_path: Path) -> None:
        path = write_image(tmp_path, "image.jpg", build_jpeg_bytes(25, 40))

        assert read_natural_size(path) == (25, 40)


class TestJpegSegmentScanning:
    def test_application_segment_before_the_frame_is_skipped(
        self, tmp_path: Path
    ) -> None:
        leading = build_jpeg_segment(0xE0, b"JFIF\x00")
        path = write_image(
            tmp_path, "image.jpg", build_jpeg_bytes(40, 25, leading=leading)
        )

        assert read_natural_size(path) == (40, 25)

    def test_huffman_table_segment_is_not_mistaken_for_a_frame(
        self, tmp_path: Path
    ) -> None:
        leading = build_jpeg_segment(0xC4, b"\x00\x00")
        path = write_image(
            tmp_path, "image.jpg", build_jpeg_bytes(40, 25, leading=leading)
        )

        assert read_natural_size(path) == (40, 25)

    def test_several_segments_before_the_frame_are_skipped(
        self, tmp_path: Path
    ) -> None:
        leading = (
            build_jpeg_segment(0xE0, b"JFIF\x00")
            + build_jpeg_segment(0xDB, b"\x00" * 65)
            + build_jpeg_segment(0xC4, b"\x00" * 17)
        )
        path = write_image(
            tmp_path, "image.jpg", build_jpeg_bytes(40, 25, leading=leading)
        )

        assert read_natural_size(path) == (40, 25)

    def test_fill_bytes_before_a_marker_are_skipped(self, tmp_path: Path) -> None:
        path = write_image(
            tmp_path, "image.jpg", build_jpeg_bytes(40, 25, leading=b"\xff")
        )

        assert read_natural_size(path) == (40, 25)

    def test_standalone_marker_before_the_frame_is_skipped(
        self, tmp_path: Path
    ) -> None:
        path = write_image(
            tmp_path, "image.jpg", build_jpeg_bytes(
                40, 25, leading=b"\xff\x01")
        )

        assert read_natural_size(path) == (40, 25)


class TestEmbeddedData:
    @pytest.mark.parametrize("content, mime_type", FORMAT_SAMPLES)
    def test_image_is_embedded_as_a_data_uri_with_its_mime_type(
        self, tmp_path: Path, content: bytes, mime_type: str
    ) -> None:
        path = write_image(tmp_path, "sample.dat", content)

        image = find_images(render_column(Column().image(path)).svg)[0]

        assert image.attrib["href"].startswith(f"data:{mime_type};base64,")

    @pytest.mark.parametrize("content, mime_type", FORMAT_SAMPLES)
    def test_embedded_data_decodes_to_the_original_file(
        self, tmp_path: Path, content: bytes, mime_type: str
    ) -> None:
        path = write_image(tmp_path, "sample.dat", content)

        image = find_images(render_column(Column().image(path)).svg)[0]
        encoded = image.attrib["href"].split(",", 1)[1]

        assert base64.b64decode(encoded) == content

    def test_format_is_detected_from_the_content_and_not_the_extension(
        self, tmp_path: Path
    ) -> None:
        path = write_image(tmp_path, "actually_a_gif.png",
                           build_gif_bytes(2, 2))

        image = find_images(render_column(Column().image(path)).svg)[0]

        assert image.attrib["href"].startswith("data:image/gif;base64,")


class TestInvalidFiles:
    def test_unrecognized_content_raises_value_error(self, tmp_path: Path) -> None:
        path = write_image(tmp_path, "notes.png", b"definitely not an image")

        with pytest.raises(ValueError, match="Unsupported image format"):
            Column().image(path)

    def test_empty_file_raises_value_error(self, tmp_path: Path) -> None:
        path = write_image(tmp_path, "empty.png", b"")

        with pytest.raises(ValueError, match="Unsupported image format"):
            Column().image(path)

    def test_error_message_names_the_offending_file(self, tmp_path: Path) -> None:
        path = write_image(tmp_path, "offending.png",
                           b"definitely not an image")

        with pytest.raises(ValueError, match=re.escape(path.name)):
            Column().image(path)

    @pytest.mark.parametrize("content, message", CORRUPTED_FILES)
    def test_corrupted_header_raises_value_error_describing_the_problem(
        self, tmp_path: Path, content: bytes, message: str
    ) -> None:
        path = write_image(tmp_path, "corrupted.bin", content)

        with pytest.raises(ValueError, match=f"Invalid image.*{message}"):
            Column().image(path)

    @pytest.mark.parametrize("content, dimensions", ZERO_DIMENSION_FILES)
    def test_zero_dimension_raises_value_error_with_the_dimensions(
        self, tmp_path: Path, content: bytes, dimensions: str
    ) -> None:
        path = write_image(tmp_path, "empty_canvas.bin", content)

        with pytest.raises(ValueError, match=f"invalid dimensions {dimensions}"):
            Column().image(path)
