"""Per-area ambient instance manager."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar

from .const import (
    CONF_AREA_ID,
    CONF_BRIGHTNESS_CURVE,
    CONF_CONTRAST,
    CONF_CYCLE_INTERVAL,
    CONF_DYNAMIC,
    CONF_EXCLUDED_ENTITIES,
    CONF_SMART_SHUFFLE,
    CONF_THEME_ID,
    CONF_TRANSITION,
    DEFAULT_BRIGHTNESS_CURVE,
    DEFAULT_CONTRAST,
    DEFAULT_CYCLE_INTERVAL,
    DEFAULT_DYNAMIC,
    DEFAULT_EXCLUDED_ENTITIES,
    DEFAULT_SMART_SHUFFLE,
    DEFAULT_THEME_ID,
    DEFAULT_TRANSITION,
)
from .engine import ThemeEngine
from .light_roles import ManagedLight, discover_area_lights
from .themes import BUILTIN_THEMES, Theme


class AmbientInstance:
    """Manages the ambient theme lifecycle for one Home Assistant area."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._engine: ThemeEngine | None = None
        self._lights: list[ManagedLight] = []

    @property
    def area_id(self) -> str:
        return self._entry.data[CONF_AREA_ID]

    @property
    def area_name(self) -> str:
        area_reg = ar.async_get(self._hass)
        area = area_reg.async_get_area(self.area_id)
        return area.name if area else self.area_id

    @property
    def theme_id(self) -> str:
        return self._entry.options.get(CONF_THEME_ID, DEFAULT_THEME_ID)

    @property
    def theme(self) -> Theme | None:
        return BUILTIN_THEMES.get(self.theme_id)

    @property
    def is_active(self) -> bool:
        return self._engine is not None

    @property
    def dynamic(self) -> bool:
        return self._entry.options.get(CONF_DYNAMIC, DEFAULT_DYNAMIC)

    @property
    def lights(self) -> list[ManagedLight]:
        return self._lights

    async def refresh_lights(self) -> None:
        """Re-discover lights in the area from the entity/device registry."""
        excluded = self._entry.options.get(CONF_EXCLUDED_ENTITIES, DEFAULT_EXCLUDED_ENTITIES)
        self._lights = await discover_area_lights(self._hass, self.area_id, excluded)

    async def activate(self) -> None:
        """Start the ambient engine, stopping any previous one first."""
        if self._engine is not None:
            self._engine.stop()
            self._engine = None

        await self.refresh_lights()

        theme = self.theme
        if theme is None:
            return

        opts = self._entry.options
        engine = ThemeEngine(
            hass=self._hass,
            lights=self._lights,
            theme=theme,
            dynamic=opts.get(CONF_DYNAMIC, DEFAULT_DYNAMIC),
            cycle_interval=opts.get(CONF_CYCLE_INTERVAL, DEFAULT_CYCLE_INTERVAL),
            transition=opts.get(CONF_TRANSITION, DEFAULT_TRANSITION),
            smart_shuffle=opts.get(CONF_SMART_SHUFFLE, DEFAULT_SMART_SHUFFLE),
            brightness_curve=opts.get(CONF_BRIGHTNESS_CURVE, DEFAULT_BRIGHTNESS_CURVE),
            contrast=opts.get(CONF_CONTRAST, DEFAULT_CONTRAST),
        )
        self._engine = engine

        if opts.get(CONF_DYNAMIC, DEFAULT_DYNAMIC):
            await engine.start_dynamic()
        else:
            await engine.apply_initial()

    async def deactivate(self) -> None:
        """Turn off all lights and stop the engine."""
        if self._engine is not None:
            await self._engine.turn_off_lights()
            self._engine = None

    def stop(self) -> None:
        """Stop the engine without turning off lights (e.g., on HA shutdown)."""
        if self._engine is not None:
            self._engine.stop()
            self._engine = None

    async def set_brightness_override(self, brightness: int | None) -> None:
        """Set a brightness override and immediately re-apply if active."""
        if self._engine is not None:
            self._engine.set_brightness_override(brightness)
            await self._engine.apply()
