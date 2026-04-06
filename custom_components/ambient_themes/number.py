"""Brightness override number entity (slider 0-100%)."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .instance import AmbientInstance


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    instance: AmbientInstance = entry.runtime_data
    async_add_entities([AmbientBrightnessOverride(instance)])


class AmbientBrightnessOverride(NumberEntity):
    """Brightness override slider (0 = use theme default, >0 = override)."""

    _attr_has_entity_name = True
    _attr_translation_key = "ambient_brightness"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = "%"
    _attr_native_value = 0.0

    def __init__(self, instance: AmbientInstance) -> None:
        self._instance = instance
        self._attr_unique_id = f"{DOMAIN}_{instance.area_id}_brightness"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._instance.area_id)},
            name=f"Ambient: {self._instance.area_name}",
        )

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        override = int(value) if value > 0 else None
        await self._instance.set_brightness_override(override)
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:brightness-6"
