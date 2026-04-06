"""Tests for the light_roles module."""
import pytest

from homeassistant.components.light import ColorMode

from custom_components.ambient_themes.const import LightRole
from custom_components.ambient_themes.light_roles import ManagedLight, detect_role


class TestDetectRole:
    """Tests for detect_role()."""

    def test_hs_mode_is_color_carrier(self):
        assert detect_role({ColorMode.HS}) == LightRole.COLOR_CARRIER

    def test_xy_mode_is_color_carrier(self):
        assert detect_role({ColorMode.XY}) == LightRole.COLOR_CARRIER

    def test_rgb_mode_is_color_carrier(self):
        assert detect_role({ColorMode.RGB}) == LightRole.COLOR_CARRIER

    def test_rgbw_mode_is_color_carrier(self):
        assert detect_role({ColorMode.RGBW}) == LightRole.COLOR_CARRIER

    def test_rgbww_mode_is_color_carrier(self):
        assert detect_role({ColorMode.RGBWW}) == LightRole.COLOR_CARRIER

    def test_color_temp_is_temperature_carrier(self):
        assert detect_role({ColorMode.COLOR_TEMP}) == LightRole.TEMPERATURE_CARRIER

    def test_brightness_is_atmosphere_carrier(self):
        assert detect_role({ColorMode.BRIGHTNESS}) == LightRole.ATMOSPHERE_CARRIER

    def test_onoff_is_participant(self):
        assert detect_role({ColorMode.ONOFF}) == LightRole.PARTICIPANT

    def test_unknown_is_participant(self):
        assert detect_role({ColorMode.UNKNOWN}) == LightRole.PARTICIPANT

    def test_empty_set_is_participant(self):
        assert detect_role(set()) == LightRole.PARTICIPANT

    def test_none_is_participant(self):
        assert detect_role(None) == LightRole.PARTICIPANT

    def test_color_takes_precedence_over_temp(self):
        assert detect_role({ColorMode.HS, ColorMode.COLOR_TEMP}) == LightRole.COLOR_CARRIER

    def test_string_hs_mode(self):
        assert detect_role({"hs"}) == LightRole.COLOR_CARRIER

    def test_string_xy_mode(self):
        assert detect_role({"xy"}) == LightRole.COLOR_CARRIER

    def test_string_rgb_mode(self):
        assert detect_role({"rgb"}) == LightRole.COLOR_CARRIER

    def test_string_color_temp_mode(self):
        assert detect_role({"color_temp"}) == LightRole.TEMPERATURE_CARRIER

    def test_string_brightness_mode(self):
        assert detect_role({"brightness"}) == LightRole.ATMOSPHERE_CARRIER

    def test_list_input(self):
        assert detect_role([ColorMode.HS, ColorMode.COLOR_TEMP]) == LightRole.COLOR_CARRIER

    def test_mixed_enum_and_string(self):
        assert detect_role({ColorMode.COLOR_TEMP, "hs"}) == LightRole.COLOR_CARRIER


class TestManagedLight:
    """Tests for ManagedLight properties."""

    def test_color_carrier_supports_color(self):
        light = ManagedLight("light.test", LightRole.COLOR_CARRIER, {ColorMode.HS})
        assert light.supports_color is True

    def test_color_carrier_supports_temp(self):
        light = ManagedLight("light.test", LightRole.COLOR_CARRIER, {ColorMode.HS})
        assert light.supports_temp is True

    def test_color_carrier_supports_brightness(self):
        light = ManagedLight("light.test", LightRole.COLOR_CARRIER, {ColorMode.HS})
        assert light.supports_brightness is True

    def test_temperature_carrier_no_color(self):
        light = ManagedLight("light.test", LightRole.TEMPERATURE_CARRIER, {ColorMode.COLOR_TEMP})
        assert light.supports_color is False

    def test_temperature_carrier_supports_temp(self):
        light = ManagedLight("light.test", LightRole.TEMPERATURE_CARRIER, {ColorMode.COLOR_TEMP})
        assert light.supports_temp is True

    def test_temperature_carrier_supports_brightness(self):
        light = ManagedLight("light.test", LightRole.TEMPERATURE_CARRIER, {ColorMode.COLOR_TEMP})
        assert light.supports_brightness is True

    def test_atmosphere_carrier_no_color(self):
        light = ManagedLight("light.test", LightRole.ATMOSPHERE_CARRIER, {ColorMode.BRIGHTNESS})
        assert light.supports_color is False

    def test_atmosphere_carrier_no_temp(self):
        light = ManagedLight("light.test", LightRole.ATMOSPHERE_CARRIER, {ColorMode.BRIGHTNESS})
        assert light.supports_temp is False

    def test_atmosphere_carrier_supports_brightness(self):
        light = ManagedLight("light.test", LightRole.ATMOSPHERE_CARRIER, {ColorMode.BRIGHTNESS})
        assert light.supports_brightness is True

    def test_participant_no_color(self):
        light = ManagedLight("light.test", LightRole.PARTICIPANT, {ColorMode.ONOFF})
        assert light.supports_color is False

    def test_participant_no_temp(self):
        light = ManagedLight("light.test", LightRole.PARTICIPANT, {ColorMode.ONOFF})
        assert light.supports_temp is False

    def test_participant_no_brightness(self):
        light = ManagedLight("light.test", LightRole.PARTICIPANT, {ColorMode.ONOFF})
        assert light.supports_brightness is False
