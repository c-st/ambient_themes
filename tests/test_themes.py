"""Tests for the themes module."""

import dataclasses

import pytest

from custom_components.ambient_themes.themes import (
    BUILTIN_THEMES,
    Theme,
    ThemeColor,
    ThemeMood,
)


class TestThemeColor:
    def test_creation(self):
        color = ThemeColor(hue=30.0, saturation=50.0)
        assert color.hue == 30.0
        assert color.saturation == 50.0

    def test_frozen(self):
        color = ThemeColor(hue=30.0, saturation=50.0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            color.hue = 60.0  # type: ignore[misc]


class TestThemeMood:
    def test_defaults(self):
        mood = ThemeMood()
        assert mood.warmth == 0.5
        assert mood.energy == 0.3
        assert mood.contrast == 0.3

    def test_custom_values(self):
        mood = ThemeMood(warmth=0.9, energy=0.1, contrast=0.7)
        assert mood.warmth == 0.9
        assert mood.energy == 0.1
        assert mood.contrast == 0.7

    def test_frozen(self):
        mood = ThemeMood()
        with pytest.raises(dataclasses.FrozenInstanceError):
            mood.warmth = 0.8  # type: ignore[misc]


class TestTheme:
    def test_color_temp_warm_cool(self):
        theme = Theme(
            id="test",
            name="Test",
            description="A test theme",
            palette=(ThemeColor(30, 50),),
            mood=ThemeMood(),
            color_temp_mireds=370,
            color_temp_range=40,
        )
        assert theme.color_temp_warm == 390  # 370 + 40//2
        assert theme.color_temp_cool == 350  # 370 - 40//2

    def test_color_temp_zero_range(self):
        theme = Theme(
            id="test",
            name="Test",
            description="A test theme",
            palette=(ThemeColor(30, 50),),
            mood=ThemeMood(),
            color_temp_mireds=300,
            color_temp_range=0,
        )
        assert theme.color_temp_warm == 300
        assert theme.color_temp_cool == 300

    def test_frozen(self):
        theme = Theme(
            id="test",
            name="Test",
            description="desc",
            palette=(ThemeColor(30, 50),),
            mood=ThemeMood(),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            theme.id = "other"  # type: ignore[misc]


class TestBuiltinThemes:
    def test_all_themes_registered(self):
        expected_ids = {
            "warm_glow",
            "midsummer_night",
            "nordic_twilight",
            "autumn_garden",
            "moonlight",
            "tropical_evening",
            "candlelight",
            "winter_frost",
            "deep_forest",
            "party",
            "aurora",
            "sunset_chase",
            "ocean_pulse",
        }
        assert set(BUILTIN_THEMES.keys()) == expected_ids

    def test_unique_ids(self):
        ids = list(BUILTIN_THEMES.keys())
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("theme_id,theme", list(BUILTIN_THEMES.items()))
    def test_theme_has_required_fields(self, theme_id: str, theme: Theme):
        assert theme.id == theme_id
        assert theme.name
        assert theme.description
        assert len(theme.palette) >= 2
        assert 0.0 <= theme.mood.warmth <= 1.0
        assert 0.0 <= theme.mood.energy <= 1.0
        assert 0.0 <= theme.mood.contrast <= 1.0
        assert 153 <= theme.color_temp_mireds <= 500
        assert 1 <= theme.default_brightness <= 100

    def test_warm_glow_exists(self):
        assert "warm_glow" in BUILTIN_THEMES
        theme = BUILTIN_THEMES["warm_glow"]
        assert theme.name == "Warm Glow"

    def test_party_high_energy(self):
        party = BUILTIN_THEMES["party"]
        assert party.mood.energy > 0.8

    def test_moonlight_low_brightness(self):
        moonlight = BUILTIN_THEMES["moonlight"]
        assert moonlight.default_brightness <= 35

    def test_all_palette_hues_in_range(self):
        for theme in BUILTIN_THEMES.values():
            for color in theme.palette:
                assert 0 <= color.hue <= 360, f"{theme.id}: hue {color.hue} out of range"
                assert 0 <= color.saturation <= 100, f"{theme.id}: sat {color.saturation} out of range"

    def test_all_mood_values_in_range(self):
        for theme in BUILTIN_THEMES.values():
            assert 0 <= theme.mood.warmth <= 1
            assert 0 <= theme.mood.energy <= 1
            assert 0 <= theme.mood.contrast <= 1

    def test_color_temp_warm_gt_cool(self):
        for theme in BUILTIN_THEMES.values():
            if theme.color_temp_range > 0:
                assert theme.color_temp_warm > theme.color_temp_cool
