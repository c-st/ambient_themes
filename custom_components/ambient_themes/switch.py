"""Ambient on/off switch entity."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_SURVIVE_RESTART, DEFAULT_SURVIVE_RESTART, DOMAIN
from .instance import AmbientInstance


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    instance: AmbientInstance = entry.runtime_data
    async_add_entities([AmbientThemeSwitch(instance, entry)])


class AmbientThemeSwitch(SwitchEntity, RestoreEntity):
    """Switch to activate/deactivate ambient lighting for an area."""

    _attr_translation_key = "ambient_switch"

    def __init__(self, instance: AmbientInstance, entry: ConfigEntry) -> None:
        self._instance = instance
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{instance.area_id}_switch"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._instance.area_id)},
            name=f"Ambient: {self._instance.area_name}",
        )

    @property
    def is_on(self) -> bool:
        return self._instance.is_active

    async def async_turn_on(self, **kwargs) -> None:
        await self._instance.activate()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self._instance.deactivate()
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:lamps"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        survive = self._entry.options.get(CONF_SURVIVE_RESTART, DEFAULT_SURVIVE_RESTART)
        if not survive:
            return
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state == "on":
            await self._instance.activate()
