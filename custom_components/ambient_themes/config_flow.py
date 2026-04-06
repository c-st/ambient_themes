"""Config and options flow for Ambient Themes."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.selector import (
    AreaSelector,
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_AREA_ID,
    CONF_BRIGHTNESS_CURVE,
    CONF_CONTRAST,
    CONF_CYCLE_INTERVAL,
    CONF_DYNAMIC,
    CONF_EXCLUDED_ENTITIES,
    CONF_HUE_DRIFT,
    CONF_SMART_SHUFFLE,
    CONF_STAGGER_MS,
    CONF_SURVIVE_RESTART,
    CONF_THEME_ID,
    CONF_TRANSITION,
    DEFAULT_BRIGHTNESS_CURVE,
    DEFAULT_CONTRAST,
    DEFAULT_CYCLE_INTERVAL,
    DEFAULT_DYNAMIC,
    DEFAULT_EXCLUDED_ENTITIES,
    DEFAULT_HUE_DRIFT,
    DEFAULT_SMART_SHUFFLE,
    DEFAULT_STAGGER_MS,
    DEFAULT_SURVIVE_RESTART,
    DEFAULT_THEME_ID,
    DEFAULT_TRANSITION,
    DOMAIN,
)
from .themes import BUILTIN_THEMES


class AmbientThemesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial config flow (area selection)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            area_id = user_input[CONF_AREA_ID]
            await self.async_set_unique_id(f"{DOMAIN}_{area_id}")
            self._abort_if_unique_id_configured()

            area_reg = ar.async_get(self.hass)
            area = area_reg.async_get_area(area_id)
            area_name = area.name if area else area_id

            return self.async_create_entry(
                title=f"Ambient: {area_name}",
                data={CONF_AREA_ID: area_id},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_AREA_ID): AreaSelector()}),
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> AmbientThemesOptionsFlow:
        return AmbientThemesOptionsFlow()


class AmbientThemesOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow (full configuration)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        opts = self.config_entry.options
        theme_options = [
            {"value": theme_id, "label": f"{theme.name} — {theme.description}"}
            for theme_id, theme in BUILTIN_THEMES.items()
        ]

        schema = vol.Schema(
            {
                vol.Optional(CONF_THEME_ID, default=opts.get(CONF_THEME_ID, DEFAULT_THEME_ID)): SelectSelector(
                    SelectSelectorConfig(options=theme_options, mode=SelectSelectorMode.DROPDOWN)
                ),
                vol.Optional(
                    CONF_EXCLUDED_ENTITIES,
                    default=opts.get(CONF_EXCLUDED_ENTITIES, DEFAULT_EXCLUDED_ENTITIES),
                ): EntitySelector(EntitySelectorConfig(domain="light", multiple=True)),
                vol.Optional(CONF_DYNAMIC, default=opts.get(CONF_DYNAMIC, DEFAULT_DYNAMIC)): BooleanSelector(),
                vol.Optional(
                    CONF_SMART_SHUFFLE, default=opts.get(CONF_SMART_SHUFFLE, DEFAULT_SMART_SHUFFLE)
                ): BooleanSelector(),
                vol.Optional(
                    CONF_CYCLE_INTERVAL, default=opts.get(CONF_CYCLE_INTERVAL, DEFAULT_CYCLE_INTERVAL)
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=10, max=3600, step=10, unit_of_measurement="s", mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(CONF_TRANSITION, default=opts.get(CONF_TRANSITION, DEFAULT_TRANSITION)): NumberSelector(
                    NumberSelectorConfig(min=0, max=60, step=1, unit_of_measurement="s", mode=NumberSelectorMode.SLIDER)
                ),
                vol.Optional(CONF_CONTRAST, default=opts.get(CONF_CONTRAST, DEFAULT_CONTRAST)): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=100, step=5, unit_of_measurement="%", mode=NumberSelectorMode.SLIDER
                    )
                ),
                vol.Optional(
                    CONF_BRIGHTNESS_CURVE, default=opts.get(CONF_BRIGHTNESS_CURVE, DEFAULT_BRIGHTNESS_CURVE)
                ): BooleanSelector(),
                vol.Optional(
                    CONF_SURVIVE_RESTART, default=opts.get(CONF_SURVIVE_RESTART, DEFAULT_SURVIVE_RESTART)
                ): BooleanSelector(),
                vol.Optional(CONF_STAGGER_MS, default=opts.get(CONF_STAGGER_MS, DEFAULT_STAGGER_MS)): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=2000, step=100, unit_of_measurement="ms", mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(CONF_HUE_DRIFT, default=opts.get(CONF_HUE_DRIFT, DEFAULT_HUE_DRIFT)): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=120, step=5, unit_of_measurement="°", mode=NumberSelectorMode.SLIDER
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
