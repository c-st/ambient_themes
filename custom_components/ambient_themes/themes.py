"""Theme definitions for the Ambient Themes integration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColor:
    """A color in hue-saturation space. Hue: 0-360, Saturation: 0-100."""

    hue: float
    saturation: float


@dataclass(frozen=True)
class ThemeMood:
    """Mood parameters describing the feel of a theme. All values: 0-1."""

    warmth: float = 0.5
    energy: float = 0.3
    contrast: float = 0.3


@dataclass(frozen=True)
class Theme:
    """A complete lighting theme."""

    id: str
    name: str
    description: str
    palette: tuple[ThemeColor, ...]
    mood: ThemeMood
    color_temp_mireds: int = 370
    color_temp_range: int = 40
    default_brightness: int = 70
    brightness_variation: int = 15

    @property
    def color_temp_warm(self) -> int:
        """Warmest color temperature (highest mireds value)."""
        return self.color_temp_mireds + self.color_temp_range // 2

    @property
    def color_temp_cool(self) -> int:
        """Coolest color temperature (lowest mireds value)."""
        return self.color_temp_mireds - self.color_temp_range // 2


BUILTIN_THEMES: dict[str, Theme] = {}


def _register(theme: Theme) -> Theme:
    BUILTIN_THEMES[theme.id] = theme
    return theme


# Calm — everyday lighting that adds depth without demanding attention
_register(
    Theme(
        id="warm_glow",
        name="Warm Glow",
        description="Golden honey with a hint of rose gold — the cozy, always-right default",
        palette=(
            ThemeColor(hue=28, saturation=65),
            ThemeColor(hue=36, saturation=58),
            ThemeColor(hue=20, saturation=72),
            ThemeColor(hue=42, saturation=52),
            ThemeColor(hue=15, saturation=68),
        ),
        mood=ThemeMood(warmth=0.90, energy=0.08, contrast=0.15),
        color_temp_mireds=405,
        color_temp_range=30,
        default_brightness=75,
        brightness_variation=12,
    )
)

# Dramatic warm — flame, ember, deep orange heat
_register(
    Theme(
        id="candlelight",
        name="Candlelight",
        description="Molten amber core, bright orange tips, deep red embers — pure flame energy",
        palette=(
            ThemeColor(hue=30, saturation=96),
            ThemeColor(hue=20, saturation=100),
            ThemeColor(hue=40, saturation=88),
            ThemeColor(hue=10, saturation=100),
            ThemeColor(hue=46, saturation=82),
            ThemeColor(hue=6, saturation=98),
        ),
        mood=ThemeMood(warmth=0.97, energy=0.50, contrast=0.80),
        color_temp_mireds=450,
        color_temp_range=60,
        default_brightness=50,
        brightness_variation=40,
    )
)

# Nordic — deep blues + aurora green, like a Scandinavian winter night
_register(
    Theme(
        id="nordic_twilight",
        name="Nordic Twilight",
        description="Midnight indigo, steel blue, and a vivid streak of aurora green",
        palette=(
            ThemeColor(hue=238, saturation=75),
            ThemeColor(hue=208, saturation=62),
            ThemeColor(hue=155, saturation=70),
            ThemeColor(hue=222, saturation=55),
            ThemeColor(hue=170, saturation=58),
            ThemeColor(hue=252, saturation=68),
        ),
        mood=ThemeMood(warmth=0.15, energy=0.22, contrast=0.50),
        color_temp_mireds=272,
        color_temp_range=75,
        default_brightness=55,
        brightness_variation=28,
    )
)

# Complementary contrast — vivid teal vs saturated coral, maximum split
_register(
    Theme(
        id="tropical_evening",
        name="Tropical Evening",
        description="Electric teal clashes with vivid coral and hot pink — high-contrast paradise",
        palette=(
            ThemeColor(hue=174, saturation=94),
            ThemeColor(hue=6, saturation=97),
            ThemeColor(hue=340, saturation=90),
            ThemeColor(hue=188, saturation=84),
            ThemeColor(hue=354, saturation=94),
            ThemeColor(hue=20, saturation=88),
        ),
        mood=ThemeMood(warmth=0.50, energy=0.60, contrast=0.72),
        color_temp_mireds=335,
        color_temp_range=70,
        default_brightness=68,
        brightness_variation=30,
    )
)

# Aurora borealis — the definitive green-violet split
_register(
    Theme(
        id="aurora",
        name="Aurora",
        description="Electric emerald and deep violet rippling like northern lights across the room",
        palette=(
            ThemeColor(hue=145, saturation=95),
            ThemeColor(hue=285, saturation=92),
            ThemeColor(hue=162, saturation=84),
            ThemeColor(hue=265, saturation=98),
            ThemeColor(hue=130, saturation=88),
            ThemeColor(hue=305, saturation=86),
        ),
        mood=ThemeMood(warmth=0.18, energy=0.70, contrast=0.78),
        color_temp_mireds=255,
        color_temp_range=70,
        default_brightness=65,
        brightness_variation=35,
    )
)

# Warm-to-cool arc — the full sunset narrative in one theme
_register(
    Theme(
        id="sunset_chase",
        name="Sunset Chase",
        description="Golden hour → deep orange → rose → magenta → violet — the whole arc of dusk",
        palette=(
            ThemeColor(hue=48, saturation=96),
            ThemeColor(hue=22, saturation=100),
            ThemeColor(hue=340, saturation=96),
            ThemeColor(hue=278, saturation=88),
            ThemeColor(hue=8, saturation=100),
            ThemeColor(hue=352, saturation=92),
        ),
        mood=ThemeMood(warmth=0.58, energy=0.75, contrast=0.75),
        color_temp_mireds=378,
        color_temp_range=90,
        default_brightness=70,
        brightness_variation=32,
    )
)

# Deep ocean — sapphire to aquamarine, cool and immersive
_register(
    Theme(
        id="ocean_pulse",
        name="Ocean Pulse",
        description="Deep sapphire, cyan surf, aquamarine shallows — the whole depth of the sea",
        palette=(
            ThemeColor(hue=195, saturation=94),
            ThemeColor(hue=222, saturation=98),
            ThemeColor(hue=172, saturation=84),
            ThemeColor(hue=205, saturation=100),
            ThemeColor(hue=238, saturation=90),
            ThemeColor(hue=158, saturation=78),
        ),
        mood=ThemeMood(warmth=0.10, energy=0.70, contrast=0.68),
        color_temp_mireds=245,
        color_temp_range=70,
        default_brightness=65,
        brightness_variation=35,
    )
)

# Maximum energy — full-spectrum primaries
_register(
    Theme(
        id="party",
        name="Party",
        description="Every hue at full saturation — maximum color energy",
        palette=(
            ThemeColor(hue=0, saturation=100),
            ThemeColor(hue=52, saturation=100),
            ThemeColor(hue=120, saturation=100),
            ThemeColor(hue=185, saturation=100),
            ThemeColor(hue=245, saturation=100),
            ThemeColor(hue=300, saturation=100),
        ),
        mood=ThemeMood(warmth=0.5, energy=1.0, contrast=0.75),
        color_temp_mireds=350,
        color_temp_range=110,
        default_brightness=90,
        brightness_variation=22,
    )
)
