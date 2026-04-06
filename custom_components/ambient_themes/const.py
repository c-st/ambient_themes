"""Constants for the Ambient Themes integration."""

from __future__ import annotations

from enum import StrEnum

DOMAIN = "ambient_themes"
PLATFORMS = ["switch", "select", "number", "sensor"]

# Configuration keys
CONF_AREA_ID = "area_id"
CONF_EXCLUDED_ENTITIES = "excluded_entities"
CONF_THEME_ID = "theme_id"
CONF_DYNAMIC = "dynamic"
CONF_CYCLE_INTERVAL = "cycle_interval"
CONF_TRANSITION = "transition"
CONF_SMART_SHUFFLE = "smart_shuffle"
CONF_BRIGHTNESS_CURVE = "brightness_curve"
CONF_CONTRAST = "contrast"
CONF_SURVIVE_RESTART = "survive_restart"
CONF_STAGGER_MS = "stagger_ms"
CONF_HUE_DRIFT = "hue_drift"

# Defaults
DEFAULT_THEME_ID = "warm_glow"
DEFAULT_EXCLUDED_ENTITIES: list[str] = []
DEFAULT_DYNAMIC = False
DEFAULT_CYCLE_INTERVAL = 60
DEFAULT_TRANSITION = 20
DEFAULT_SMART_SHUFFLE = True
DEFAULT_BRIGHTNESS_CURVE = False
DEFAULT_CONTRAST = 35
DEFAULT_SURVIVE_RESTART = True
DEFAULT_STAGGER_MS = 150
DEFAULT_HUE_DRIFT = 12

# Brightness curve: list of (minutes_after_sunset, brightness_percent) tuples
DEFAULT_BRIGHTNESS_CURVE_POINTS: list[tuple[int, int]] = [
    (0, 90),
    (60, 70),
    (180, 45),
    (360, 25),
]


class LightRole(StrEnum):
    """Role assigned to a light based on its color capabilities."""

    COLOR_CARRIER = "color_carrier"
    TEMPERATURE_CARRIER = "temperature_carrier"
    ATMOSPHERE_CARRIER = "atmosphere_carrier"
    PARTICIPANT = "participant"
