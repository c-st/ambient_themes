"""Tests for the AmbientInstance lifecycle manager."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.ambient_themes.const import (
    CONF_AREA_ID,
    CONF_DYNAMIC,
    CONF_THEME_ID,
    DEFAULT_DYNAMIC,
    DEFAULT_THEME_ID,
)
from custom_components.ambient_themes.instance import AmbientInstance
from custom_components.ambient_themes.themes import BUILTIN_THEMES


def make_entry(area_id: str = "area_living_room", options: dict | None = None):
    """Create a mock config entry."""
    entry = MagicMock()
    entry.data = {CONF_AREA_ID: area_id}
    entry.options = options or {}
    return entry


def make_instance(mock_hass, area_id="area_living_room", options=None):
    """Create an AmbientInstance with a mock hass and entry."""
    entry = make_entry(area_id, options)
    return AmbientInstance(mock_hass, entry)


class TestProperties:
    def test_area_id(self, mock_hass):
        instance = make_instance(mock_hass, area_id="area_kitchen")
        assert instance.area_id == "area_kitchen"

    def test_theme_id_default(self, mock_hass):
        instance = make_instance(mock_hass)
        assert instance.theme_id == DEFAULT_THEME_ID

    def test_theme_id_from_options(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_THEME_ID: "party"})
        assert instance.theme_id == "party"

    def test_theme_returns_builtin(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_THEME_ID: "party"})
        assert instance.theme is BUILTIN_THEMES["party"]

    def test_theme_returns_none_for_invalid_id(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_THEME_ID: "nonexistent_theme"})
        assert instance.theme is None

    def test_is_active_initially_false(self, mock_hass):
        instance = make_instance(mock_hass)
        assert instance.is_active is False

    def test_dynamic_default(self, mock_hass):
        instance = make_instance(mock_hass)
        assert instance.dynamic == DEFAULT_DYNAMIC

    def test_dynamic_from_options(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_DYNAMIC: True})
        assert instance.dynamic is True

    def test_area_name_from_registry(self, mock_hass):
        mock_area = MagicMock()
        mock_area.name = "Living Room"
        with patch("custom_components.ambient_themes.instance.ar") as mock_ar:
            mock_ar.async_get.return_value.async_get_area.return_value = mock_area
            instance = make_instance(mock_hass, area_id="area_living_room")
            assert instance.area_name == "Living Room"

    def test_area_name_fallback_to_id(self, mock_hass):
        with patch("custom_components.ambient_themes.instance.ar") as mock_ar:
            mock_ar.async_get.return_value.async_get_area.return_value = None
            instance = make_instance(mock_hass, area_id="area_fallback")
            assert instance.area_name == "area_fallback"


class TestActivate:
    async def test_activate_creates_engine(self, mock_hass):
        instance = make_instance(mock_hass)
        with patch.object(instance, "refresh_lights", new_callable=AsyncMock):
            instance._lights = []
            with patch("custom_components.ambient_themes.instance.ThemeEngine") as MockEngine:
                mock_engine = MagicMock()
                mock_engine.apply_initial = AsyncMock()
                MockEngine.return_value = mock_engine
                await instance.activate()
                assert instance.is_active is True

    async def test_activate_with_dynamic_starts_cycling(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_DYNAMIC: True})
        with patch.object(instance, "refresh_lights", new_callable=AsyncMock):
            instance._lights = []
            with patch("custom_components.ambient_themes.instance.ThemeEngine") as MockEngine:
                mock_engine = MagicMock()
                mock_engine.start_dynamic = AsyncMock()
                MockEngine.return_value = mock_engine
                await instance.activate()
                mock_engine.start_dynamic.assert_called_once()

    async def test_activate_without_dynamic_applies_initial(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_DYNAMIC: False})
        with patch.object(instance, "refresh_lights", new_callable=AsyncMock):
            instance._lights = []
            with patch("custom_components.ambient_themes.instance.ThemeEngine") as MockEngine:
                mock_engine = MagicMock()
                mock_engine.apply_initial = AsyncMock()
                MockEngine.return_value = mock_engine
                await instance.activate()
                mock_engine.apply_initial.assert_called_once()

    async def test_invalid_theme_engine_stays_none(self, mock_hass):
        instance = make_instance(mock_hass, options={CONF_THEME_ID: "nonexistent"})
        with patch.object(instance, "refresh_lights", new_callable=AsyncMock):
            await instance.activate()
            assert instance._engine is None

    async def test_reactivate_stops_previous_engine(self, mock_hass):
        instance = make_instance(mock_hass)
        with patch.object(instance, "refresh_lights", new_callable=AsyncMock):
            instance._lights = []
            with patch("custom_components.ambient_themes.instance.ThemeEngine") as MockEngine:
                first_engine = MagicMock()
                first_engine.apply_initial = AsyncMock()
                second_engine = MagicMock()
                second_engine.apply_initial = AsyncMock()
                MockEngine.side_effect = [first_engine, second_engine]

                await instance.activate()
                await instance.activate()
                first_engine.stop.assert_called_once()


class TestDeactivate:
    async def test_deactivate_calls_turn_off_and_clears_engine(self, mock_hass):
        instance = make_instance(mock_hass)
        mock_engine = MagicMock()
        mock_engine.turn_off_lights = AsyncMock()
        instance._engine = mock_engine

        await instance.deactivate()

        mock_engine.turn_off_lights.assert_called_once()
        assert instance._engine is None
        assert instance.is_active is False

    async def test_deactivate_when_inactive_is_noop(self, mock_hass):
        instance = make_instance(mock_hass)
        await instance.deactivate()  # should not raise


class TestStop:
    def test_stop_clears_engine_without_turn_off(self, mock_hass):
        instance = make_instance(mock_hass)
        mock_engine = MagicMock()
        instance._engine = mock_engine

        instance.stop()

        mock_engine.stop.assert_called_once()
        mock_engine.turn_off_lights.assert_not_called()
        assert instance._engine is None

    def test_stop_when_inactive_is_noop(self, mock_hass):
        instance = make_instance(mock_hass)
        instance.stop()  # should not raise


class TestSetBrightnessOverride:
    async def test_propagates_to_engine_and_reapplies(self, mock_hass):
        instance = make_instance(mock_hass)
        mock_engine = MagicMock()
        mock_engine.apply = AsyncMock()
        instance._engine = mock_engine

        await instance.set_brightness_override(75)

        mock_engine.set_brightness_override.assert_called_once_with(75)
        mock_engine.apply.assert_called_once()

    async def test_none_override_propagates(self, mock_hass):
        instance = make_instance(mock_hass)
        mock_engine = MagicMock()
        mock_engine.apply = AsyncMock()
        instance._engine = mock_engine

        await instance.set_brightness_override(None)
        mock_engine.set_brightness_override.assert_called_once_with(None)

    async def test_no_engine_is_noop(self, mock_hass):
        instance = make_instance(mock_hass)
        await instance.set_brightness_override(50)  # should not raise
