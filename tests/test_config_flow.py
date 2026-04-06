"""Tests for the config and options flow."""

from __future__ import annotations

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ambient_themes.const import (
    CONF_AREA_IDS,
    CONF_CONTRAST,
    CONF_DYNAMIC,
    CONF_THEME_ID,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests in this module."""
    return


async def test_user_step_shows_form(hass: HomeAssistant) -> None:
    """The user step should show a form with step_id 'user'."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_step_creates_entry_single_area(hass: HomeAssistant) -> None:
    """Submitting a single area should create a config entry."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    area = area_registry.async_create("Living Room")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], user_input={CONF_AREA_IDS: [area.id]})
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Ambient: Living Room"
    assert result2["data"][CONF_AREA_IDS] == [area.id]


async def test_user_step_creates_entry_multiple_areas(hass: HomeAssistant) -> None:
    """Submitting multiple areas should create a combined entry."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    garden = area_registry.async_create("Garden")
    terrace = area_registry.async_create("Terrace")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_AREA_IDS: [garden.id, terrace.id]}
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert "Garden" in result2["title"]
    assert "Terrace" in result2["title"]
    assert set(result2["data"][CONF_AREA_IDS]) == {garden.id, terrace.id}


async def test_user_step_aborts_duplicate(hass: HomeAssistant) -> None:
    """Configuring the same area set twice should abort."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    area = area_registry.async_create("Kitchen")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    await hass.config_entries.flow.async_configure(result["flow_id"], user_input={CONF_AREA_IDS: [area.id]})

    result2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result3 = await hass.config_entries.flow.async_configure(result2["flow_id"], user_input={CONF_AREA_IDS: [area.id]})
    assert result3["type"] == FlowResultType.ABORT
    assert result3["reason"] == "already_configured"


async def test_options_flow_shows_form(hass: HomeAssistant) -> None:
    """The options flow init step should show a form."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    area = area_registry.async_create("Bedroom")

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_AREA_IDS: [area.id]}, options={})
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_saves_all_fields(hass: HomeAssistant) -> None:
    """Submitting the options form should save all provided fields."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    area = area_registry.async_create("Office")

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_AREA_IDS: [area.id]}, options={})
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    user_input = {
        CONF_THEME_ID: "party",
        "excluded_entities": [],
        CONF_DYNAMIC: True,
        "smart_shuffle": True,
        "cycle_interval": 120,
        "transition": 5,
        CONF_CONTRAST: 50,
        "brightness_curve": False,
        "survive_restart": True,
    }
    result2 = await hass.config_entries.options.async_configure(result["flow_id"], user_input=user_input)
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_THEME_ID] == "party"
    assert entry.options[CONF_DYNAMIC] is True
    assert entry.options[CONF_CONTRAST] == 50


async def test_options_flow_defaults_from_existing_options(hass: HomeAssistant) -> None:
    """The options form should pre-populate with existing option values."""
    from homeassistant.helpers import area_registry as ar

    area_registry = ar.async_get(hass)
    area = area_registry.async_create("Hallway")

    existing_options = {CONF_THEME_ID: "candlelight", CONF_DYNAMIC: True, CONF_CONTRAST: 75}
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_AREA_IDS: [area.id]}, options=existing_options)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    schema = result["data_schema"].schema
    for key in schema:
        if hasattr(key, "default") and str(key) == CONF_THEME_ID:
            assert key.default() == "candlelight"
