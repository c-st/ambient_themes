"""Tests for the ThemeEngine."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_TRANSITION,
    ColorMode,
)
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON

from custom_components.ambient_themes.const import LightRole
from custom_components.ambient_themes.engine import ThemeEngine
from custom_components.ambient_themes.light_roles import ManagedLight
from custom_components.ambient_themes.themes import BUILTIN_THEMES, ThemeColor


def make_engine(mock_hass, lights, theme_id="warm_glow", **kwargs) -> ThemeEngine:
    theme = BUILTIN_THEMES[theme_id]
    return ThemeEngine(hass=mock_hass, lights=lights, theme=theme, **kwargs)


class TestBrightnessPctToValue:
    def test_zero(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._brightness_pct_to_value(0) == 0

    def test_hundred(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._brightness_pct_to_value(100) == 255

    def test_fifty(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._brightness_pct_to_value(50) == 128

    def test_clamp_over(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._brightness_pct_to_value(200) == 255

    def test_clamp_under(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._brightness_pct_to_value(-10) == 0


class TestShuffleColors:
    def test_empty(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._shuffle_colors([]) == []

    def test_single(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        colors = [ThemeColor(30, 50)]
        result = engine._shuffle_colors(colors)
        assert result == colors

    def test_smart_shuffle_preserves_all_colors(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme, smart_shuffle=True)
        colors = list(warm_glow_theme.palette)
        result = engine._shuffle_colors(colors)
        assert len(result) == len(colors)
        assert set((c.hue, c.saturation) for c in result) == set((c.hue, c.saturation) for c in colors)

    def test_non_smart_shuffle_preserves_all_colors(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme, smart_shuffle=False)
        colors = list(warm_glow_theme.palette)
        result = engine._shuffle_colors(colors)
        assert len(result) == len(colors)
        assert set((c.hue, c.saturation) for c in result) == set((c.hue, c.saturation) for c in colors)


class TestDistributeBrightness:
    def test_single_light_uniform(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, contrast=50)
        result = engine._distribute_brightness(70)
        assert result == [70]

    def test_zero_contrast_uniform(self, mock_hass, warm_glow_theme, mixed_lights):
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme, contrast=0)
        result = engine._distribute_brightness(70)
        assert all(v == 70 for v in result)
        assert len(result) == 4

    def test_high_contrast_has_spread(self, mock_hass, warm_glow_theme, mixed_lights):
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme, contrast=100)
        result = engine._distribute_brightness(70)
        assert len(result) == 4
        assert max(result) > min(result)

    def test_values_in_valid_range(self, mock_hass, warm_glow_theme, mixed_lights):
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme, contrast=100)
        result = engine._distribute_brightness(70)
        assert all(5 <= v <= 100 for v in result)

    def test_empty_lights(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        assert engine._distribute_brightness(70) == []


class TestApply:
    async def test_no_lights_no_calls(self, mock_hass, warm_glow_theme):
        engine = ThemeEngine(mock_hass, [], warm_glow_theme)
        await engine.apply()
        mock_hass.services.async_call.assert_not_called()

    async def test_calls_turn_on_for_each_light(self, mock_hass, warm_glow_theme, mixed_lights):
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme)
        await engine.apply()
        assert mock_hass.services.async_call.call_count == 4

    async def test_rgb_light_gets_hs_color_brightness_transition(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, transition=10)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert ATTR_HS_COLOR in data
        assert ATTR_BRIGHTNESS in data
        assert data[ATTR_TRANSITION] == 10
        assert ATTR_COLOR_TEMP not in data

    async def test_cct_light_gets_color_temp_not_hs(self, mock_hass, warm_glow_theme, cct_light):
        engine = ThemeEngine(mock_hass, [cct_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert ATTR_COLOR_TEMP in data
        assert ATTR_HS_COLOR not in data
        assert 153 <= data[ATTR_COLOR_TEMP] <= 500

    async def test_dimmable_light_gets_brightness_only(self, mock_hass, warm_glow_theme, dimmable_light):
        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert ATTR_BRIGHTNESS in data
        assert ATTR_HS_COLOR not in data
        assert ATTR_COLOR_TEMP not in data

    async def test_participant_gets_entity_id_only(self, mock_hass, warm_glow_theme, onoff_light):
        engine = ThemeEngine(mock_hass, [onoff_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert data == {"entity_id": onoff_light.entity_id}

    async def test_brightness_override_used(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, brightness_override=50)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        expected = round(50 * 255 / 100)
        assert data[ATTR_BRIGHTNESS] == expected


class TestApplyInitial:
    async def test_uses_zero_transition_then_restores(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, transition=15)
        await engine.apply_initial()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert data[ATTR_TRANSITION] == 0
        assert engine._transition == 15


class TestTurnOffLights:
    async def test_calls_turn_off_for_each_light(self, mock_hass, warm_glow_theme, mixed_lights):
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme, transition=5)
        await engine.turn_off_lights()
        calls = mock_hass.services.async_call.call_args_list
        assert len(calls) == 4
        for call in calls:
            assert call[0][1] == SERVICE_TURN_OFF
            data = call[0][2]
            assert data[ATTR_TRANSITION] == 5


class TestDynamic:
    async def test_start_sets_running(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme)
        await engine.start_dynamic()
        assert engine.is_running is True

    async def test_stop_clears_running(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme)
        await engine.start_dynamic()
        engine.stop()
        assert engine.is_running is False

    async def test_double_start_is_noop(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme)
        await engine.start_dynamic()
        call_count = mock_hass.services.async_call.call_count
        await engine.start_dynamic()  # should be noop
        assert mock_hass.services.async_call.call_count == call_count

    async def test_stop_cancels_task(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme)
        await engine.start_dynamic()
        task = engine._cycle_task
        engine.stop()
        assert engine._cycle_task is None


class TestBrightnessCurve:
    async def test_disabled_uses_theme_default(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, brightness_curve=False)
        assert engine._get_current_brightness() == warm_glow_theme.default_brightness

    async def test_override_takes_precedence_over_curve(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(
            mock_hass, [rgb_light], warm_glow_theme,
            brightness_curve=True, brightness_override=42
        )
        assert engine._get_current_brightness() == 42
