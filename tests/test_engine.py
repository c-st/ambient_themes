"""Tests for the ThemeEngine."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_TRANSITION,
)
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_OFF, STATE_ON

from custom_components.ambient_themes.engine import ThemeEngine
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
        target = call_args[1]["target"]
        assert ATTR_HS_COLOR in data
        assert ATTR_BRIGHTNESS in data
        assert data[ATTR_TRANSITION] == 10
        assert ATTR_COLOR_TEMP_KELVIN not in data
        assert target == {"entity_id": rgb_light.entity_id}

    async def test_cct_light_gets_color_temp_not_hs(self, mock_hass, warm_glow_theme, cct_light):
        engine = ThemeEngine(mock_hass, [cct_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert ATTR_COLOR_TEMP_KELVIN in data
        assert ATTR_HS_COLOR not in data
        # kelvin range: 1_000_000/153 ≈ 6536K (cool) down to 1_000_000/500 = 2000K (warm)
        assert 2000 <= data[ATTR_COLOR_TEMP_KELVIN] <= 6536

    async def test_dimmable_light_gets_brightness_only(self, mock_hass, warm_glow_theme, dimmable_light):
        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        assert ATTR_BRIGHTNESS in data
        assert ATTR_HS_COLOR not in data
        assert ATTR_COLOR_TEMP_KELVIN not in data

    async def test_participant_gets_empty_data_with_target(self, mock_hass, warm_glow_theme, onoff_light):
        engine = ThemeEngine(mock_hass, [onoff_light], warm_glow_theme)
        await engine.apply()
        call_args = mock_hass.services.async_call.call_args_list[0]
        data = call_args[0][2]
        target = call_args[1]["target"]
        assert data == {}
        assert target == {"entity_id": onoff_light.entity_id}

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
    async def test_color_and_temp_carriers_are_turned_off(self, mock_hass, warm_glow_theme, mixed_lights):
        """COLOR_CARRIER and TEMPERATURE_CARRIER lights are always turned off on deactivate."""
        engine = ThemeEngine(mock_hass, mixed_lights, warm_glow_theme, transition=5)
        await engine.turn_off_lights()
        calls = mock_hass.services.async_call.call_args_list
        turned_off = {c[1]["target"]["entity_id"] for c in calls if c[0][1] == SERVICE_TURN_OFF}
        assert "light.garden_spot_1" in turned_off  # COLOR_CARRIER
        assert "light.terrace_wall" in turned_off   # TEMPERATURE_CARRIER
        assert "light.porch" in turned_off           # PARTICIPANT

    async def test_atmosphere_carrier_restored_when_previously_on(self, mock_hass, warm_glow_theme, dimmable_light):
        """ATMOSPHERE_CARRIER light is restored to its pre-ambient brightness if it was on."""
        prior_brightness = 180
        mock_state = MagicMock()
        mock_state.state = STATE_ON
        mock_state.attributes = {ATTR_BRIGHTNESS: prior_brightness}
        mock_hass.states.get = MagicMock(return_value=mock_state)

        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme, transition=5)
        engine._snapshot_brightness()  # simulate snapshot taken at activation
        mock_hass.services.async_call.reset_mock()

        await engine.turn_off_lights()
        calls = mock_hass.services.async_call.call_args_list
        assert len(calls) == 1
        assert calls[0][0][1] == SERVICE_TURN_ON
        data = calls[0][0][2]
        assert data[ATTR_BRIGHTNESS] == prior_brightness
        assert data[ATTR_TRANSITION] == 5

    async def test_atmosphere_carrier_turned_off_when_previously_off(self, mock_hass, warm_glow_theme, dimmable_light):
        """ATMOSPHERE_CARRIER light is turned off on deactivate if it was off before ambient started."""
        mock_state = MagicMock()
        mock_state.state = STATE_OFF
        mock_state.attributes = {}
        mock_hass.states.get = MagicMock(return_value=mock_state)

        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme, transition=5)
        engine._snapshot_brightness()  # was off, so snapshot stores None
        mock_hass.services.async_call.reset_mock()

        await engine.turn_off_lights()
        calls = mock_hass.services.async_call.call_args_list
        assert len(calls) == 1
        assert calls[0][0][1] == SERVICE_TURN_OFF

    async def test_snapshot_taken_on_start_dynamic(self, mock_hass, warm_glow_theme, dimmable_light):
        """Brightness snapshot is populated when start_dynamic is called."""
        prior_brightness = 200
        mock_state = MagicMock()
        mock_state.state = STATE_ON
        mock_state.attributes = {ATTR_BRIGHTNESS: prior_brightness}
        mock_hass.states.get = MagicMock(return_value=mock_state)

        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme)
        assert engine._brightness_snapshot == {}
        await engine.start_dynamic()
        assert engine._brightness_snapshot.get(dimmable_light.entity_id) == prior_brightness

    async def test_snapshot_taken_on_apply_initial(self, mock_hass, warm_glow_theme, dimmable_light):
        """Brightness snapshot is populated on apply_initial if not already set."""
        prior_brightness = 150
        mock_state = MagicMock()
        mock_state.state = STATE_ON
        mock_state.attributes = {ATTR_BRIGHTNESS: prior_brightness}
        mock_hass.states.get = MagicMock(return_value=mock_state)

        engine = ThemeEngine(mock_hass, [dimmable_light], warm_glow_theme)
        assert engine._brightness_snapshot == {}
        await engine.apply_initial()
        assert engine._brightness_snapshot.get(dimmable_light.entity_id) == prior_brightness


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
        engine.stop()
        assert engine._cycle_task is None


class TestBrightnessCurve:
    async def test_disabled_uses_theme_default(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, brightness_curve=False)
        assert engine._get_current_brightness() == warm_glow_theme.default_brightness

    async def test_override_takes_precedence_over_curve(self, mock_hass, warm_glow_theme, rgb_light):
        engine = ThemeEngine(mock_hass, [rgb_light], warm_glow_theme, brightness_curve=True, brightness_override=42)
        assert engine._get_current_brightness() == 42
