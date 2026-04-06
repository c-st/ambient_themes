# Ambient Themes for Home Assistant

A theme-driven ambient lighting controller for Home Assistant areas.

## Features

- **One integration per area** — create as many instances as you have areas
- **Auto-discovers lights** in the area via entity and device registry
- **Assigns roles automatically** based on each light's color capabilities
- **10 built-in themes** — warm glow, candlelight, moonlight, party, and more
- **Dynamic cycling** — colors shift on a configurable interval
- **Sunset brightness curve** — dims automatically after sunset
- **HACS-ready** — install in one click
- **Native HA UI** — no custom panels; uses config/options flow

## Installation

### HACS (recommended)

1. In HACS, add this repository as a custom integration.
2. Install "Ambient Themes".
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for "Ambient Themes".

### Manual

Copy `custom_components/ambient_themes/` into your `config/custom_components/` directory and restart.

## Configuration

Each instance is created for one HA area. A config entry creates four entities:

| Entity | Type | Purpose |
|--------|------|---------|
| `switch.ambient` | Switch | Turn the ambient lighting on/off |
| `select.theme` | Select | Pick the active theme |
| `number.brightness_override` | Number (slider) | Override the theme brightness |
| `sensor.status` | Sensor | Shows active theme, light role counts |

## Themes

| Theme | Description |
|-------|-------------|
| Warm Glow | Simple warm white — the cozy default |
| Midsummer Night | Warm golden tones fading into deep amber |
| Nordic Twilight | Cool blues and soft whites |
| Autumn Garden | Burnt orange, deep red, warm yellow |
| Moonlight | Very cool white, low brightness |
| Tropical Evening | Teals, corals, warm pinks |
| Candlelight | Flickering warm tones |
| Winter Frost | Icy blues and whites |
| Deep Forest | Greens and earthy tones |
| Party | Saturated colors, faster cycling |

## Light Roles

Lights are assigned roles based on their capabilities:

| Role | Capability | What it receives |
|------|-----------|-----------------|
| Color Carrier | HS / XY / RGB | Full theme color (hue + saturation) |
| Temperature Carrier | Color Temp | Color temperature in theme range |
| Atmosphere Carrier | Brightness only | Brightness, no color |
| Participant | On/Off only | Just turned on |

## Automation Example

```yaml
automation:
  - alias: "Living Room Ambient at Sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ambient_living_room_ambient
```

## Development

```bash
pip install -r requirements-test.txt
pytest --cov=custom_components/ambient_themes --cov-report=term-missing -v
ruff check .
ruff format .
```
