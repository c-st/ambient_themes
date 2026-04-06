"""Ambient Themes — theme-driven ambient lighting controller for HA areas."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .instance import AmbientInstance


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an Ambient Themes instance from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    instance = AmbientInstance(hass, entry)
    await instance.refresh_lights()

    hass.data[DOMAIN][entry.entry_id] = instance
    entry.runtime_data = instance

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """React to options changes: stop then re-activate if previously active."""
    instance: AmbientInstance = hass.data[DOMAIN][entry.entry_id]
    was_active = instance.is_active
    instance.stop()
    await instance.refresh_lights()
    if was_active:
        await instance.activate()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Ambient Themes config entry."""
    instance: AmbientInstance = hass.data[DOMAIN].pop(entry.entry_id)
    instance.stop()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
