"""Status sensor entity."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LightRole
from .instance import AmbientInstance


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    instance: AmbientInstance = entry.runtime_data
    async_add_entities([AmbientStatusSensor(instance)])


class AmbientStatusSensor(SensorEntity):
    """Shows the current status and light role summary for an ambient instance."""

    _attr_translation_key = "ambient_status"

    def __init__(self, instance: AmbientInstance) -> None:
        self._instance = instance
        self._attr_unique_id = f"{DOMAIN}_{instance.area_id}_status"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._instance.area_id)},
            name=f"Ambient: {self._instance.area_name}",
        )

    @property
    def native_value(self) -> str:
        if not self._instance.is_active:
            return "inactive"
        theme = self._instance.theme
        theme_name = theme.name if theme else self._instance.theme_id
        mode = "dynamic" if self._instance.dynamic else "static"
        return f"{theme_name} ({mode})"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        lights = self._instance.lights
        return {
            "is_active": self._instance.is_active,
            "theme_id": self._instance.theme_id,
            "total_lights": len(lights),
            "color_carriers": sum(1 for lt in lights if lt.role == LightRole.COLOR_CARRIER),
            "temperature_carriers": sum(1 for lt in lights if lt.role == LightRole.TEMPERATURE_CARRIER),
            "atmosphere_carriers": sum(1 for lt in lights if lt.role == LightRole.ATMOSPHERE_CARRIER),
            "participants": sum(1 for lt in lights if lt.role == LightRole.PARTICIPANT),
        }

    @property
    def icon(self) -> str:
        return "mdi:information-outline"
