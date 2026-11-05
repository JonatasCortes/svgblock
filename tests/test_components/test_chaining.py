from collections.abc import Callable
from pathlib import Path
import pytest
from svgblock import Column, Composer
from .shared import render_column, write_minimal_png

Builder = Callable[[Composer, Path], Composer]

BUILDERS: dict[str, Builder] = {
    "title": lambda target, _: target.title("Heading"),
    "subsection": lambda target, _: target.subsection("Subheading"),
    "text": lambda target, _: target.text("Paragraph"),
    "image": lambda target, image: target.image(image),
    "columns": lambda target, _: target.columns(Column().divider()),
    "table": lambda target, _: target.table(["a", "b"], [["x", "y"]]),
    "divider": lambda target, _: target.divider(),
}
BUILDER_PARAMS = [pytest.param(builder, id=name)
                  for name, builder in BUILDERS.items()]


class TestBuilderReturnValue:
    @pytest.mark.parametrize("composer_type", [Composer, Column])
    @pytest.mark.parametrize("builder", BUILDER_PARAMS)
    def test_builder_returns_the_instance_it_was_called_on(
        self, tmp_path: Path, composer_type: type[Composer], builder: Builder
    ) -> None:
        target = composer_type()
        image = write_minimal_png(tmp_path)

        assert builder(target, image) is target

    @pytest.mark.parametrize("builder", BUILDER_PARAMS)
    def test_builder_called_on_column_returns_a_column(
        self, tmp_path: Path, builder: Builder
    ) -> None:
        image = write_minimal_png(tmp_path)

        assert isinstance(builder(Column(), image), Column)


class TestChainedCalls:
    def test_chained_calls_render_the_same_as_separate_calls(self) -> None:
        chained = Column().title("Heading").divider().text("Body")

        separate = Column()
        separate.title("Heading")
        separate.divider()
        separate.text("Body")

        assert render_column(chained).svg == render_column(separate).svg

    def test_composers_created_separately_do_not_share_components(self) -> None:
        populated = Column().divider()
        untouched = Column()

        assert render_column(populated).height > 0
        assert render_column(untouched).height == 0
        assert render_column(untouched).svg == ""
