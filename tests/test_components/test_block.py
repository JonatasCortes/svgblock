import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from svgblock import Block, Column, Theme
from .shared import make_column_with_dividers, render_column, write_minimal_png

SVG_TAG = "{http://www.w3.org/2000/svg}svg"
DEFAULT_WIDTH = 800
DEFAULT_PADDING = 24


def parse(svg: str) -> ET.Element:
    """Parse a complete SVG document into its root element."""
    return ET.fromstring(svg)


def read_dimension(svg: str, attribute: str) -> float:
    """Return a numeric attribute of the root svg element."""
    return float(parse(svg).attrib[attribute])


def make_block_with_dividers(count: int, **options: float | bool) -> Block:
    """Build a Block holding the given number of dividers."""
    block = Block(**options)  # type: ignore[arg-type]
    for _ in range(count):
        block.divider()
    return block


class TestRenderedDocument:
    def test_root_element_is_an_svg(self) -> None:
        assert parse(Block().divider().render()).tag == SVG_TAG

    def test_default_width_is_applied(self) -> None:
        assert read_dimension(Block().divider().render(),
                              "width") == DEFAULT_WIDTH

    @pytest.mark.parametrize("width", [320, 800, 1024.5])
    def test_width_attribute_equals_the_configured_width(self, width: float) -> None:
        svg = Block(width=width).divider().render()

        assert read_dimension(svg, "width") == pytest.approx(width)

    def test_view_box_matches_width_and_height_attributes(self) -> None:
        svg = Block(width=640).title("Heading").divider().render()

        view_box = parse(svg).attrib["viewBox"].split()

        assert [float(value) for value in view_box] == pytest.approx(
            [0, 0, read_dimension(svg, "width"), read_dimension(svg, "height")]
        )

    def test_document_with_every_component_type_is_well_formed_xml(
        self, tmp_path: Path
    ) -> None:
        block = (
            Block()
            .title("Heading")
            .subsection("Subheading")
            .text("Paragraph")
            .divider()
            .table(["a", "b"], [["x", 1]])
            .image(write_minimal_png(tmp_path))
            .columns(Column().text("left"), Column().text("right"))
        )

        assert parse(block.render()).tag == SVG_TAG

    def test_rendering_twice_yields_identical_documents(self) -> None:
        block = Block().title("Heading").divider().text("Body")

        assert block.render() == block.render()

    def test_special_characters_survive_in_the_complete_document(self) -> None:
        content = "Tom & Jerry <3"

        svg = Block().text(content).render()

        assert content in "".join(parse(svg).itertext())

    def test_components_appear_in_insertion_order(self) -> None:
        svg = Block().title("FIRST").text("SECOND").render()

        text = "".join(parse(svg).itertext())

        assert text.index("FIRST") < text.index("SECOND")

    def test_width_is_not_written_in_scientific_notation(self) -> None:
        svg = Block(width=1_000_000).divider().render()

        assert "e+" not in parse(svg).attrib["width"]


class TestHeight:
    @pytest.mark.parametrize("padding", [2, 10, DEFAULT_PADDING, 50])
    def test_empty_block_height_is_twice_the_padding(self, padding: int) -> None:
        svg = Block(padding=padding).render()

        assert read_dimension(svg, "height") == pytest.approx(2 * padding)

    def test_empty_block_without_padding_raises_value_error_from_the_frame(
        self,
    ) -> None:
        with pytest.raises(ValueError, match="border width"):
            Block(padding=0).render()

    def test_empty_block_without_padding_renders_when_the_frame_is_hidden(
        self,
    ) -> None:
        svg = Block(padding=0, hide_frame=True).render()

        assert read_dimension(svg, "height") == 0

    def test_default_padding_is_applied(self) -> None:
        assert read_dimension(Block().render(), "height") == pytest.approx(
            2 * DEFAULT_PADDING
        )

    @pytest.mark.parametrize("padding", [0, 10, DEFAULT_PADDING, 50])
    def test_height_is_content_height_plus_padding_on_both_sides(
        self, padding: int
    ) -> None:
        content_height = render_column(make_column_with_dividers(3)).height

        svg = make_block_with_dividers(3, padding=padding).render()

        assert read_dimension(svg, "height") == pytest.approx(
            content_height + 2 * padding
        )

    @pytest.mark.parametrize("padding", [0, 10, DEFAULT_PADDING, 50])
    def test_hidden_frame_removes_the_padding_from_the_height(
        self, padding: int
    ) -> None:
        content_height = render_column(make_column_with_dividers(3)).height

        svg = make_block_with_dividers(
            3, padding=padding, hide_frame=True).render()

        assert read_dimension(svg, "height") == pytest.approx(content_height)

    def test_height_grows_when_components_are_added(self) -> None:
        block = Block().divider()
        before = read_dimension(block.render(), "height")

        block.divider()

        assert read_dimension(block.render(), "height") > before


class TestTheme:
    def test_default_theme_is_neon(self) -> None:
        default = Block().title("Heading").divider().render()
        neon = Block(theme=Theme.NEON).title("Heading").divider().render()

        assert default == neon

    def test_theme_member_and_its_theme_data_render_identically(self) -> None:
        from_member = Block(theme=Theme.NEON).title("Heading").render()
        from_data = Block(theme=Theme.NEON.value).title("Heading").render()

        assert from_member == from_data


class TestSave:
    def test_save_writes_the_rendered_document(self, tmp_path: Path) -> None:
        block = Block().title("Heading").divider()
        target = tmp_path / "block.svg"

        block.save(target)

        assert target.read_text(encoding="utf-8") == block.render()

    def test_save_accepts_the_path_as_a_string(self, tmp_path: Path) -> None:
        block = Block().divider()
        target = tmp_path / "block.svg"

        block.save(str(target))

        assert target.read_text(encoding="utf-8") == block.render()

    def test_save_creates_missing_parent_directories(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "deeper" / "block.svg"

        Block().divider().save(target)

        assert target.is_file()

    def test_save_overwrites_an_existing_file(self, tmp_path: Path) -> None:
        target = tmp_path / "block.svg"
        target.write_text("stale content", encoding="utf-8")
        block = Block().divider()

        block.save(target)

        assert target.read_text(encoding="utf-8") == block.render()

    def test_save_encodes_non_ascii_text_as_utf8(self, tmp_path: Path) -> None:
        block = Block().text("Ação — título ✓")
        target = tmp_path / "block.svg"

        block.save(target)

        assert target.read_bytes().decode("utf-8") == block.render()

    def test_saved_file_is_well_formed_xml(self, tmp_path: Path) -> None:
        target = tmp_path / "block.svg"

        Block().title("Heading").divider().save(target)

        assert ET.parse(target).getroot().tag == SVG_TAG


class TestInvalidGeometry:
    @pytest.mark.parametrize("invalid_width", [0, -100, float("nan")])
    def test_render_raises_value_error_when_width_is_not_a_positive_number(
        self, invalid_width: float
    ) -> None:
        with pytest.raises(ValueError):
            Block(width=invalid_width).divider().render()

    def test_render_raises_value_error_when_padding_is_negative(self) -> None:
        with pytest.raises(ValueError):
            Block(padding=-1).divider().render()

    @pytest.mark.parametrize(
        "invalid_width", [0, -100, float("nan"), float("inf"), float("-inf")]
    )
    def test_render_raises_value_error_when_width_is_infinite(self, invalid_width: float) -> None:
        with pytest.raises(ValueError):
            Block(width=invalid_width).divider().render()


class TestContentWidth:
    @pytest.mark.parametrize("padding", [50, 80])
    def test_render_raises_value_error_when_padding_leaves_no_content_width(
        self, padding: int
    ) -> None:
        with pytest.raises(ValueError, match="leaves no room for content"):
            Block(width=100, padding=padding).divider().render()

    def test_render_succeeds_when_padding_leaves_a_little_content_width(self) -> None:
        svg = Block(width=100, padding=49).divider().render()

        assert read_dimension(svg, "width") == 100

    def test_hidden_frame_ignores_a_padding_that_would_leave_no_content_width(
        self,
    ) -> None:
        svg = Block(width=100, padding=80, hide_frame=True).divider().render()

        assert read_dimension(svg, "width") == 100
