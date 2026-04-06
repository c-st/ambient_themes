"""Shared pytest fixtures for ambient_themes tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.light import ColorMode
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant

from custom_components.ambient_themes.const import LightRole
from custom_components.ambient_themes.light_roles import ManagedLight
from custom_components.ambient_themes.themes import BUILTIN_THEMES


@pytest.fixture
def mock_hass():
    """A minimal HomeAssistant mock suitable for engine/instance unit tests."""
    hass = MagicMock(spec=HomeAssistant)
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()

    mock_state = MagicMock()
    mock_state.state = STATE_ON
    hass.states = MagicMock()
    hass.states.get = MagicMock(return_value=mock_state)

    hass.async_create_task = MagicMock(return_value=MagicMock())
    return hass


@pytest.fixture
def rgb_light():
    return ManagedLight("light.garden_spot_1", LightRole.COLOR_CARRIER, {ColorMode.HS, ColorMode.COLOR_TEMP})


@pytest.fixture
def cct_light():
    return ManagedLight("light.terrace_wall", LightRole.TEMPERATURE_CARRIER, {ColorMode.COLOR_TEMP})


@pytest.fixture
def dimmable_light():
    return ManagedLight("light.path_lamp", LightRole.ATMOSPHERE_CARRIER, {ColorMode.BRIGHTNESS})


@pytest.fixture
def onoff_light():
    return ManagedLight("light.porch", LightRole.PARTICIPANT, {ColorMode.ONOFF})


@pytest.fixture
def mixed_lights(rgb_light, cct_light, dimmable_light, onoff_light):
    return [rgb_light, cct_light, dimmable_light, onoff_light]


@pytest.fixture
def warm_glow_theme():
    return BUILTIN_THEMES["warm_glow"]


@pytest.fixture
def party_theme():
    return BUILTIN_THEMES["party"]


@pytest.fixture
def midsummer_theme():
    return BUILTIN_THEMES["midsummer_night"]
