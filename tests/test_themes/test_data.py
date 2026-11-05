"""Tests for the shape of the theme data exposed by ``svgblock.components.themes``."""

import re

import pytest

from svgblock.components.themes import Theme, ThemeData

HEX_COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}")

every_theme = pytest.mark.parametrize(
    "theme", list(Theme), ids=[theme.name for theme in Theme]
)


class TestThemeRegistry:
    def test_at_least_one_theme_is_registered(self) -> None:
        assert len(list(Theme)) > 0

    def test_no_theme_is_an_alias_of_another_theme(self) -> None:
        """Enum members with identical values become aliases and vanish from iteration."""
        aliases = [
            name for name, member in Theme.__members__.items() if name != member.name
        ]

        assert aliases == []


class TestThemeDataDeclaration:
    def test_theme_data_declares_at_least_one_key(self) -> None:
        """Guards the shape tests below against passing vacuously."""
        assert len(ThemeData.__required_keys__) > 0


class TestEveryThemeMatchesTheThemeDataShape:
    @every_theme
    def test_theme_defines_every_key_declared_by_theme_data(self, theme: Theme) -> None:
        missing_keys = set(ThemeData.__required_keys__) - set(theme.value)

        assert missing_keys == set()

    @every_theme
    def test_theme_defines_no_key_that_theme_data_does_not_declare(
        self, theme: Theme
    ) -> None:
        unexpected_keys = set(theme.value) - set(ThemeData.__required_keys__)

        assert unexpected_keys == set()

    @every_theme
    def test_every_color_of_the_theme_is_a_six_digit_hex_string(
        self, theme: Theme
    ) -> None:
        invalid_entries = {
            key: value
            for key, value in theme.value.items()
            if not HEX_COLOR_PATTERN.fullmatch(str(value))
        }

        assert invalid_entries == {}
