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


_register(
    Theme(
        id="warm_glow",
        name="Warm Glow",
        description="Simple warm white, the cozy default",
        palette=(
            ThemeColor(hue=30, saturation=55),
            ThemeColor(hue=35, saturation=50),
            ThemeColor(hue=38, saturation=60),
        ),
        mood=ThemeMood(warmth=0.85, energy=0.05, contrast=0.1),
        color_temp_mireds=400,
        color_temp_range=20,
        default_brightness=75,
        brightness_variation=5,
    )
)

_register(
    Theme(
        id="midsummer_night",
        name="Midsummer Night",
        description="Warm golden tones fading into deep amber",
        palette=(
            ThemeColor(hue=35, saturation=90),
            ThemeColor(hue=25, saturation=95),
            ThemeColor(hue=15, saturation=85),
            ThemeColor(hue=40, saturation=80),
        ),
        mood=ThemeMood(warmth=0.9, energy=0.2, contrast=0.4),
        color_temp_mireds=400,
        color_temp_range=50,
        default_brightness=70,
        brightness_variation=15,
    )
)

_register(
    Theme(
        id="nordic_twilight",
        name="Nordic Twilight",
        description="Cool blues and soft whites",
        palette=(
            ThemeColor(hue=220, saturation=40),
            ThemeColor(hue=210, saturation=55),
            ThemeColor(hue=230, saturation=35),
            ThemeColor(hue=200, saturation=25),
        ),
        mood=ThemeMood(warmth=0.2, energy=0.1, contrast=0.3),
        color_temp_mireds=280,
        color_temp_range=60,
        default_brightness=55,
        brightness_variation=10,
    )
)

_register(
    Theme(
        id="autumn_garden",
        name="Autumn Garden",
        description="Burnt orange, deep red, warm yellow",
        palette=(
            ThemeColor(hue=20, saturation=90),
            ThemeColor(hue=5, saturation=85),
            ThemeColor(hue=45, saturation=80),
            ThemeColor(hue=10, saturation=95),
        ),
        mood=ThemeMood(warmth=0.8, energy=0.25, contrast=0.5),
        color_temp_mireds=380,
        color_temp_range=40,
        default_brightness=65,
        brightness_variation=20,
    )
)

_register(
    Theme(
        id="moonlight",
        name="Moonlight",
        description="Very cool white, low brightness",
        palette=(
            ThemeColor(hue=215, saturation=15),
            ThemeColor(hue=220, saturation=20),
            ThemeColor(hue=210, saturation=10),
        ),
        mood=ThemeMood(warmth=0.15, energy=0.05, contrast=0.15),
        color_temp_mireds=250,
        color_temp_range=30,
        default_brightness=30,
        brightness_variation=5,
    )
)

_register(
    Theme(
        id="tropical_evening",
        name="Tropical Evening",
        description="Teals, corals, warm pinks",
        palette=(
            ThemeColor(hue=175, saturation=70),
            ThemeColor(hue=10, saturation=75),
            ThemeColor(hue=340, saturation=60),
            ThemeColor(hue=180, saturation=50),
            ThemeColor(hue=15, saturation=65),
        ),
        mood=ThemeMood(warmth=0.55, energy=0.4, contrast=0.5),
        color_temp_mireds=340,
        color_temp_range=50,
        default_brightness=65,
        brightness_variation=15,
    )
)

_register(
    Theme(
        id="candlelight",
        name="Candlelight",
        description="Flickering warm tones",
        palette=(
            ThemeColor(hue=30, saturation=85),
            ThemeColor(hue=25, saturation=90),
            ThemeColor(hue=35, saturation=75),
            ThemeColor(hue=20, saturation=95),
        ),
        mood=ThemeMood(warmth=0.95, energy=0.3, contrast=0.6),
        color_temp_mireds=450,
        color_temp_range=30,
        default_brightness=50,
        brightness_variation=25,
    )
)

_register(
    Theme(
        id="winter_frost",
        name="Winter Frost",
        description="Icy blues and whites",
        palette=(
            ThemeColor(hue=200, saturation=30),
            ThemeColor(hue=190, saturation=45),
            ThemeColor(hue=210, saturation=20),
            ThemeColor(hue=195, saturation=50),
        ),
        mood=ThemeMood(warmth=0.1, energy=0.1, contrast=0.25),
        color_temp_mireds=230,
        color_temp_range=40,
        default_brightness=60,
        brightness_variation=10,
    )
)

_register(
    Theme(
        id="deep_forest",
        name="Deep Forest",
        description="Greens and earthy tones",
        palette=(
            ThemeColor(hue=120, saturation=60),
            ThemeColor(hue=90, saturation=50),
            ThemeColor(hue=140, saturation=45),
            ThemeColor(hue=70, saturation=55),
        ),
        mood=ThemeMood(warmth=0.4, energy=0.15, contrast=0.35),
        color_temp_mireds=350,
        color_temp_range=40,
        default_brightness=55,
        brightness_variation=15,
    )
)

_register(
    Theme(
        id="party",
        name="Party",
        description="Saturated colors, faster cycling",
        palette=(
            ThemeColor(hue=0, saturation=100),
            ThemeColor(hue=60, saturation=100),
            ThemeColor(hue=120, saturation=100),
            ThemeColor(hue=180, saturation=100),
            ThemeColor(hue=240, saturation=100),
            ThemeColor(hue=300, saturation=100),
        ),
        mood=ThemeMood(warmth=0.5, energy=0.95, contrast=0.7),
        color_temp_mireds=350,
        color_temp_range=100,
        default_brightness=85,
        brightness_variation=20,
    )
)
