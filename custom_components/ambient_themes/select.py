"""Theme picker select entity."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_THEME_ID, DEFAULT_THEME_ID, DOMAIN
from .instance import AmbientInstance
from .themes import BUILTIN_THEMES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    instance: AmbientInstance = entry.runtime_data
    async_add_entities([AmbientThemeSelect(instance, entry)])


class AmbientThemeSelect(SelectEntity):
    """Selects the active ambient theme."""

    _attr_has_entity_name = True
    _attr_translation_key = "ambient_theme"

    def __init__(self, instance: AmbientInstance, entry: ConfigEntry) -> None:
        self._instance = instance
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{instance.area_id}_theme"
        self._attr_options = list(BUILTIN_THEMES.keys())

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._instance.area_id)},
            name=f"Ambient: {self._instance.area_name}",
        )

    @property
    def current_option(self) -> str:
        return self._entry.options.get(CONF_THEME_ID, DEFAULT_THEME_ID)

    async def async_select_option(self, option: str) -> None:
        new_options = {**self._entry.options, CONF_THEME_ID: option}
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)

    @property
    def icon(self) -> str:
        return "mdi:palette"
