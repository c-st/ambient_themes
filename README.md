# Ambient Themes for Home Assistant

A theme-driven ambient lighting controller for Home Assistant areas.

## Features

- **One integration per area** — create as many instances as you have areas
- **Auto-discovers lights** in the area via entity and device registry
- **Assigns roles automatically** based on each light's color capabilities
- **8 built-in themes** — from cozy candlelight to dramatic aurora light shows
- **Dynamic cycling** — colors shift on a configurable interval with smooth crossfades
- **Wave stagger** — lights update sequentially for a ripple effect across the room
- **Hue drift** — palette hues rotate each cycle so colors never repeat exactly
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

Eight themes, each built around a distinct color identity. All are designed to look great with dynamic cycling — turn it on, pick a theme, and let the lights do the rest.

---

### Warm Glow
**Vibe:** Cozy, always-on background warmth

Golden honey spanning from rose-gold amber to deep warm orange. The everyday default — never demands attention, always looks good. Subtle brightness variation keeps it alive without becoming a light show.

`brightness: 75%` · `variation: ±12%` · `color temp: very warm`

---

### Candlelight
**Vibe:** Intimate, dramatic, flickery

Six distinct fire hues from bright amber to deep red ember. The highest brightness variation of any theme (±40%) — each light pulses at a different level, creating genuine flicker energy.

`brightness: 50%` · `variation: ±40%` · `color temp: ultra-warm`

> **Tip:** Set cycle interval to 20–30s for maximum flicker effect.

---

### Nordic Twilight
**Vibe:** Cold, mysterious, northern

Midnight indigo and steel blue with a vivid streak of aurora green cutting across — like standing outside in a Scandinavian winter looking up. The green note makes it feel alive rather than flat.

`brightness: 55%` · `variation: ±28%` · `color temp: cold`

---

### Tropical Evening
**Vibe:** Vibrant, energetic, split-complementary

Electric cyan-teal on one side, saturated coral and hot pink on the other — near-maximum complementary contrast. In a room with multiple lights the effect is like neon reflections on wet pavement.

`brightness: 68%` · `variation: ±30%` · `color temp: warm-neutral`

---

### Aurora
**Vibe:** Dramatic, otherworldly, sweeping

Electric emerald green and deep violet alternating at high saturation across a 140° hue split. With wave stagger enabled, colors sweep across the room like actual northern lights.

`brightness: 65%` · `variation: ±35%` · `color temp: cold`

> **Tip:** Enable hue drift for continuous slow evolution — the palette never repeats.

---

### Sunset Chase
**Vibe:** Cinematic, warm-to-cool arc

Six hues tracing the full arc of dusk: golden hour → deep orange → rose → magenta → violet. The only theme that spans the entire warm-to-cool spectrum in a single palette. With smart shuffle the transitions feel like a time-lapse.

`brightness: 70%` · `variation: ±32%` · `color temp: full range`

---

### Ocean Pulse
**Vibe:** Immersive, cool, deep

From deep sapphire to bright aquamarine — the full depth of the sea. The most saturated blues of any theme. Creates an enveloping cool atmosphere that fills a room.

`brightness: 65%` · `variation: ±35%` · `color temp: very cold`

---

### Party
**Vibe:** Maximum energy, full-spectrum

Six primaries at 100% saturation evenly spaced around the color wheel. Every light is a different vivid hue. With fast cycling and wave stagger it becomes a full light show.

`brightness: 90%` · `variation: ±22%` · `color temp: full range`

> **Tip:** Set cycle interval to 10–15s and stagger to 300ms for maximum effect.

---

## Light Roles

Lights are assigned roles based on their capabilities:

| Role | Capability | What it receives |
|------|-----------|-----------------|
| Color Carrier | HS / XY / RGB | Full theme color (hue + saturation) |
| Temperature Carrier | Color Temp | Color temperature in theme range |
| Atmosphere Carrier | Brightness only | Brightness variation, no color |
| Participant | On/Off only | Just turned on |

## Dynamic Mode Options

| Option | Default | Description |
|--------|---------|-------------|
| Cycle interval | 60s | How often colors reassign |
| Transition | 20s | Crossfade duration (overlap with cycle for continuous motion) |
| Wave stagger | 150ms | Delay between each light's update — creates a ripple |
| Hue drift | 12°/cycle | Rotates the palette each cycle so it never repeats |
| Smart shuffle | on | Orders colors by hue distance for smoother gradients |
| Contrast | 35% | Brightness spread across lights |

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
ruff check . && ruff format .
```
