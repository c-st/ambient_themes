"""Light role detection and management for the Ambient Themes integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.light import ColorMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import LightRole

# ColorMode enum members that indicate full color support
_COLOR_CARRIER_MODES: frozenset[ColorMode] = frozenset({
    ColorMode.HS, ColorMode.XY, ColorMode.RGB, ColorMode.RGBW, ColorMode.RGBWW,
})

# String equivalents (capabilities may arrive as strings from entity registry)
_COLOR_CARRIER_STRINGS: frozenset[str] = frozenset({"hs", "xy", "rgb", "rgbw", "rgbww"})
_TEMP_STRINGS: frozenset[str] = frozenset({"color_temp"})
_BRIGHTNESS_STRINGS: frozenset[str] = frozenset({"brightness"})


def detect_role(supported_color_modes: set | list | None) -> LightRole:
    """Detect the ambient role of a light based on its supported color modes.

    Handles both ColorMode enum values and raw string values.
    Priority: COLOR_CARRIER > TEMPERATURE_CARRIER > ATMOSPHERE_CARRIER > PARTICIPANT
    """
    if not supported_color_modes:
        return LightRole.PARTICIPANT

    # Normalize to lowercase strings for uniform comparison
    string_modes: set[str] = set()
    enum_modes: set[ColorMode] = set()

    for mode in supported_color_modes:
        if isinstance(mode, ColorMode):
            enum_modes.add(mode)
            string_modes.add(mode.value)
        else:
            s = str(mode).lower()
            string_modes.add(s)
            try:
                enum_modes.add(ColorMode(s))
            except ValueError:
                pass

    if enum_modes & _COLOR_CARRIER_MODES or string_modes & _COLOR_CARRIER_STRINGS:
        return LightRole.COLOR_CARRIER
    if ColorMode.COLOR_TEMP in enum_modes or string_modes & _TEMP_STRINGS:
        return LightRole.TEMPERATURE_CARRIER
    if ColorMode.BRIGHTNESS in enum_modes or string_modes & _BRIGHTNESS_STRINGS:
        return LightRole.ATMOSPHERE_CARRIER
    return LightRole.PARTICIPANT


@dataclass
class ManagedLight:
    """A light entity managed by the Ambient Themes engine."""

    entity_id: str
    role: LightRole
    supported_color_modes: set[ColorMode]

    @property
    def supports_color(self) -> bool:
        """True if this light can display HS/RGB colors."""
        return self.role == LightRole.COLOR_CARRIER

    @property
    def supports_temp(self) -> bool:
        """True if this light can display a color temperature."""
        return self.role in (LightRole.COLOR_CARRIER, LightRole.TEMPERATURE_CARRIER)

    @property
    def supports_brightness(self) -> bool:
        """True if this light can be dimmed."""
        return self.role != LightRole.PARTICIPANT


async def discover_area_lights(
    hass: HomeAssistant,
    area_id: str,
    excluded_entity_ids: list[str] | None = None,
) -> list[ManagedLight]:
    """Discover all light entities in a HA area and return them as ManagedLight objects.

    Finds lights via both direct area assignment and devices assigned to the area.
    Deduplicates results.
    """
    excluded: set[str] = set(excluded_entity_ids or [])
    entity_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)

    found_entity_ids: set[str] = set()

    # Lights directly assigned to the area
    for entry in er.async_entries_for_area(entity_reg, area_id):
        if (
            entry.domain == "light"
            and not entry.disabled_by
            and entry.entity_id not in excluded
        ):
            found_entity_ids.add(entry.entity_id)

    # Lights on devices assigned to the area
    for device in dr.async_entries_for_area(device_reg, area_id):
        for entry in er.async_entries_for_device(entity_reg, device.id):
            if (
                entry.domain == "light"
                and not entry.disabled_by
                and entry.entity_id not in excluded
            ):
                found_entity_ids.add(entry.entity_id)

    result: list[ManagedLight] = []
    for entity_id in sorted(found_entity_ids):  # sorted for determinism
        entry = entity_reg.async_get(entity_id)
        if entry is None:
            continue
        raw_modes = (entry.capabilities or {}).get("supported_color_modes", set())
        if isinstance(raw_modes, list):
            raw_modes = set(raw_modes)
        elif not isinstance(raw_modes, set):
            raw_modes = set()
        role = detect_role(raw_modes)
        result.append(ManagedLight(entity_id=entity_id, role=role, supported_color_modes=raw_modes))

    return result
