"""Theme engine — applies a theme to a set of managed lights."""
from __future__ import annotations

import asyncio
import random

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_TRANSITION,
)
from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_ON
from homeassistant.core import HomeAssistant

from .const import DEFAULT_BRIGHTNESS_CURVE_POINTS, LightRole
from .light_roles import ManagedLight
from .themes import Theme, ThemeColor


class ThemeEngine:
    """Applies a theme to a set of managed lights."""

    def __init__(
        self,
        hass: HomeAssistant,
        lights: list[ManagedLight],
        theme: Theme,
        dynamic: bool = False,
        cycle_interval: int = 300,
        transition: int = 15,
        smart_shuffle: bool = True,
        brightness_curve: bool = False,
        contrast: int = 30,
        brightness_override: int | None = None,
    ) -> None:
        self._hass = hass
        self._lights = lights
        self._theme = theme
        self._dynamic = dynamic
        self._cycle_interval = cycle_interval
        self._transition = transition
        self._smart_shuffle = smart_shuffle
        self._brightness_curve = brightness_curve
        self._contrast = contrast
        self._brightness_override = brightness_override
        self._running = False
        self._cycle_task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        return self._running

    def set_brightness_override(self, brightness: int | None) -> None:
        self._brightness_override = brightness

    def _brightness_pct_to_value(self, pct: int) -> int:
        """Convert brightness percentage (0-100) to HA value (0-255)."""
        return max(0, min(255, round(pct * 255 / 100)))

    def _get_current_brightness(self) -> int:
        if self._brightness_override is not None:
            return self._brightness_override
        if self._brightness_curve:
            return self._curve_brightness()
        return self._theme.default_brightness

    def _curve_brightness(self) -> int:
        """Calculate brightness based on time since sunset using linear interpolation."""
        try:
            from homeassistant.helpers.sun import get_astral_event_date
            from homeassistant.util.dt import utcnow

            today = utcnow().date()
            sunset = get_astral_event_date(self._hass, "sunset", today)
            if sunset is None:
                return self._theme.default_brightness

            now = utcnow()
            # Make sunset timezone-aware if it isn't
            if sunset.tzinfo is None:
                import datetime as dt

                from homeassistant.util.dt import as_utc
                sunset = as_utc(dt.datetime.combine(today, sunset.time()))

            minutes_since_sunset = (now - sunset).total_seconds() / 60
            points = DEFAULT_BRIGHTNESS_CURVE_POINTS

            if minutes_since_sunset <= points[0][0]:
                return points[0][1]
            if minutes_since_sunset >= points[-1][0]:
                return points[-1][1]

            for i in range(len(points) - 1):
                t0, b0 = points[i]
                t1, b1 = points[i + 1]
                if t0 <= minutes_since_sunset <= t1:
                    ratio = (minutes_since_sunset - t0) / (t1 - t0)
                    return round(b0 + ratio * (b1 - b0))

            return self._theme.default_brightness
        except Exception:
            return self._theme.default_brightness

    def _shuffle_colors(self, colors: list[ThemeColor]) -> list[ThemeColor]:
        """Shuffle colors, optionally using smart hue-distance ordering."""
        if not colors:
            return []
        colors = list(colors)

        if not self._smart_shuffle:
            random.shuffle(colors)
            return colors

        # Smart shuffle: start random, then pick from closest-hue half of remaining
        start_idx = random.randrange(len(colors))
        result = [colors[start_idx]]
        remaining = colors[:start_idx] + colors[start_idx + 1:]

        while remaining:
            last_hue = result[-1].hue
            # Sort by hue distance considering 360-wrap
            remaining.sort(key=lambda c: min(abs(c.hue - last_hue), 360 - abs(c.hue - last_hue)))
            half = max(1, len(remaining) // 2)
            chosen = random.choice(remaining[:half])
            result.append(chosen)
            remaining.remove(chosen)

        return result

    def _distribute_brightness(self, base: int) -> list[int]:
        """Distribute brightness values across lights with spread based on contrast."""
        n = len(self._lights)
        if n == 0:
            return []
        if n == 1 or self._contrast == 0:
            return [base] * n

        spread = self._theme.brightness_variation * (self._contrast / 100)
        values = []
        for i in range(n):
            offset = -spread + (2 * spread * i / (n - 1))
            values.append(round(base + offset))

        random.shuffle(values)
        return [max(5, min(100, v)) for v in values]

    def _assign_colors(self) -> list[ThemeColor]:
        """Assign shuffled palette colors to color carrier lights."""
        color_lights = [lt for lt in self._lights if lt.role == LightRole.COLOR_CARRIER]
        if not color_lights:
            return []

        palette = list(self._theme.palette)
        while len(palette) < len(color_lights):
            palette.extend(list(self._theme.palette))
        palette = palette[: len(color_lights)]

        return self._shuffle_colors(palette)

    async def apply(self) -> None:
        """Apply the current theme to all managed lights."""
        if not self._lights:
            return

        brightness_pct = self._get_current_brightness()
        brightnesses = self._distribute_brightness(brightness_pct)
        color_assignment = self._assign_colors()
        color_idx = 0
        tasks = []

        for i, light in enumerate(self._lights):
            brightness_val = self._brightness_pct_to_value(brightnesses[i])

            if light.role == LightRole.COLOR_CARRIER:
                color = (
                    color_assignment[color_idx]
                    if color_idx < len(color_assignment)
                    else self._theme.palette[0]
                )
                color_idx += 1
                data = {
                    "entity_id": light.entity_id,
                    ATTR_HS_COLOR: (color.hue, color.saturation),
                    ATTR_BRIGHTNESS: brightness_val,
                    ATTR_TRANSITION: self._transition,
                }
            elif light.role == LightRole.TEMPERATURE_CARRIER:
                color_temp = random.randint(self._theme.color_temp_cool, self._theme.color_temp_warm)
                data = {
                    "entity_id": light.entity_id,
                    ATTR_COLOR_TEMP: color_temp,
                    ATTR_BRIGHTNESS: brightness_val,
                    ATTR_TRANSITION: self._transition,
                }
            elif light.role == LightRole.ATMOSPHERE_CARRIER:
                data = {
                    "entity_id": light.entity_id,
                    ATTR_BRIGHTNESS: brightness_val,
                    ATTR_TRANSITION: self._transition,
                }
            else:  # PARTICIPANT
                data = {"entity_id": light.entity_id}

            tasks.append(
                self._hass.services.async_call(LIGHT_DOMAIN, SERVICE_TURN_ON, data, blocking=False)
            )

        await asyncio.gather(*tasks)

    async def apply_initial(self) -> None:
        """Apply theme instantly (transition=0) then restore original transition."""
        saved = self._transition
        self._transition = 0
        await self.apply()
        self._transition = saved

    async def start_dynamic(self) -> None:
        """Start dynamic cycling: apply immediately, then loop on interval."""
        if self._running:
            return
        self._running = True
        await self.apply_initial()
        self._cycle_task = self._hass.async_create_task(self._dynamic_loop())

    async def _dynamic_loop(self) -> None:
        """Background loop that re-applies the theme on every cycle_interval."""
        while self._running:
            await asyncio.sleep(self._cycle_interval)
            if not self._running:
                break
            any_on = any(
                (state := self._hass.states.get(lt.entity_id)) is not None
                and state.state == STATE_ON
                for lt in self._lights
            )
            if not any_on:
                self._running = False
                break
            await self.apply()

    def stop(self) -> None:
        """Stop dynamic cycling without turning off lights."""
        self._running = False
        if self._cycle_task is not None:
            self._cycle_task.cancel()
            self._cycle_task = None

    async def turn_off_lights(self) -> None:
        """Stop cycling and turn off all managed lights."""
        self.stop()
        tasks = [
            self._hass.services.async_call(
                LIGHT_DOMAIN,
                SERVICE_TURN_OFF,
                {"entity_id": lt.entity_id, ATTR_TRANSITION: self._transition},
                blocking=False,
            )
            for lt in self._lights
        ]
        if tasks:
            await asyncio.gather(*tasks)
