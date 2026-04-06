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


# ── Cozy / Warm ──────────────────────────────────────────────────────────────

_register(
    Theme(
        id="warm_glow",
        name="Warm Glow",
        description="Golden honey tones with a hint of rose gold — the cozy everyday default",
        palette=(
            ThemeColor(hue=28, saturation=65),
            ThemeColor(hue=35, saturation=60),
            ThemeColor(hue=22, saturation=70),
            ThemeColor(hue=40, saturation=55),
            ThemeColor(hue=18, saturation=72),
        ),
        mood=ThemeMood(warmth=0.88, energy=0.08, contrast=0.15),
        color_temp_mireds=400,
        color_temp_range=30,
        default_brightness=75,
        brightness_variation=12,
    )
)

_register(
    Theme(
        id="midsummer_night",
        name="Midsummer Night",
        description="Bonfire amber, molten gold, and a blush of rose on the horizon",
        palette=(
            ThemeColor(hue=32, saturation=100),
            ThemeColor(hue=18, saturation=100),
            ThemeColor(hue=50, saturation=90),
            ThemeColor(hue=355, saturation=70),
            ThemeColor(hue=38, saturation=95),
            ThemeColor(hue=8, saturation=95),
        ),
        mood=ThemeMood(warmth=0.92, energy=0.35, contrast=0.55),
        color_temp_mireds=410,
        color_temp_range=70,
        default_brightness=72,
        brightness_variation=28,
    )
)

_register(
    Theme(
        id="candlelight",
        name="Candlelight",
        description="Amber core, orange tips, deep red embers — maximum flicker energy",
        palette=(
            ThemeColor(hue=28, saturation=95),
            ThemeColor(hue=20, saturation=100),
            ThemeColor(hue=38, saturation=88),
            ThemeColor(hue=12, saturation=100),
            ThemeColor(hue=44, saturation=85),
            ThemeColor(hue=8, saturation=98),
        ),
        mood=ThemeMood(warmth=0.97, energy=0.45, contrast=0.75),
        color_temp_mireds=450,
        color_temp_range=60,
        default_brightness=50,
        brightness_variation=38,
    )
)

_register(
    Theme(
        id="autumn_garden",
        name="Autumn Garden",
        description="Burnt sienna, rust red, deep crimson, and warm golden yellow",
        palette=(
            ThemeColor(hue=18, saturation=95),
            ThemeColor(hue=5, saturation=90),
            ThemeColor(hue=48, saturation=88),
            ThemeColor(hue=358, saturation=82),
            ThemeColor(hue=28, saturation=95),
            ThemeColor(hue=55, saturation=80),
        ),
        mood=ThemeMood(warmth=0.82, energy=0.3, contrast=0.6),
        color_temp_mireds=385,
        color_temp_range=50,
        default_brightness=65,
        brightness_variation=30,
    )
)

# ── Cool / Night ──────────────────────────────────────────────────────────────

_register(
    Theme(
        id="nordic_twilight",
        name="Nordic Twilight",
        description="Deep indigo, arctic steel blue, and a whisper of aurora green",
        palette=(
            ThemeColor(hue=232, saturation=70),
            ThemeColor(hue=207, saturation=60),
            ThemeColor(hue=168, saturation=45),
            ThemeColor(hue=218, saturation=55),
            ThemeColor(hue=192, saturation=42),
            ThemeColor(hue=248, saturation=65),
        ),
        mood=ThemeMood(warmth=0.18, energy=0.15, contrast=0.4),
        color_temp_mireds=275,
        color_temp_range=70,
        default_brightness=55,
        brightness_variation=20,
    )
)

_register(
    Theme(
        id="moonlight",
        name="Moonlight",
        description="Silver-white with a whisper of lavender — serene and ethereal",
        palette=(
            ThemeColor(hue=218, saturation=18),
            ThemeColor(hue=240, saturation=14),
            ThemeColor(hue=208, saturation=12),
            ThemeColor(hue=228, saturation=20),
            ThemeColor(hue=212, saturation=10),
        ),
        mood=ThemeMood(warmth=0.12, energy=0.05, contrast=0.18),
        color_temp_mireds=248,
        color_temp_range=35,
        default_brightness=28,
        brightness_variation=12,
    )
)

_register(
    Theme(
        id="winter_frost",
        name="Winter Frost",
        description="Crisp ice white to deep frost blue — cold clarity",
        palette=(
            ThemeColor(hue=200, saturation=48),
            ThemeColor(hue=218, saturation=68),
            ThemeColor(hue=193, saturation=32),
            ThemeColor(hue=232, saturation=72),
            ThemeColor(hue=207, saturation=50),
        ),
        mood=ThemeMood(warmth=0.08, energy=0.12, contrast=0.35),
        color_temp_mireds=228,
        color_temp_range=45,
        default_brightness=62,
        brightness_variation=22,
    )
)

# ── Nature ────────────────────────────────────────────────────────────────────

_register(
    Theme(
        id="deep_forest",
        name="Deep Forest",
        description="Emerald, chartreuse, forest green, and dappled golden moss",
        palette=(
            ThemeColor(hue=138, saturation=78),
            ThemeColor(hue=88, saturation=72),
            ThemeColor(hue=158, saturation=65),
            ThemeColor(hue=65, saturation=62),
            ThemeColor(hue=118, saturation=82),
            ThemeColor(hue=75, saturation=58),
        ),
        mood=ThemeMood(warmth=0.38, energy=0.18, contrast=0.4),
        color_temp_mireds=348,
        color_temp_range=50,
        default_brightness=58,
        brightness_variation=25,
    )
)

_register(
    Theme(
        id="tropical_evening",
        name="Tropical Evening",
        description="Vivid cyan-teal vs saturated coral and hot pink — maximum tropical contrast",
        palette=(
            ThemeColor(hue=174, saturation=92),
            ThemeColor(hue=8, saturation=96),
            ThemeColor(hue=338, saturation=88),
            ThemeColor(hue=188, saturation=82),
            ThemeColor(hue=352, saturation=92),
            ThemeColor(hue=22, saturation=88),
        ),
        mood=ThemeMood(warmth=0.52, energy=0.55, contrast=0.65),
        color_temp_mireds=338,
        color_temp_range=65,
        default_brightness=68,
        brightness_variation=28,
    )
)

# ── Light Show ────────────────────────────────────────────────────────────────

_register(
    Theme(
        id="aurora",
        name="Aurora",
        description="Northern lights — emerald green, electric violet, and arctic teal in sweeping waves",
        palette=(
            ThemeColor(hue=148, saturation=92),
            ThemeColor(hue=282, saturation=88),
            ThemeColor(hue=168, saturation=82),
            ThemeColor(hue=262, saturation=96),
            ThemeColor(hue=185, saturation=75),
            ThemeColor(hue=305, saturation=84),
        ),
        mood=ThemeMood(warmth=0.22, energy=0.65, contrast=0.7),
        color_temp_mireds=258,
        color_temp_range=65,
        default_brightness=65,
        brightness_variation=32,
    )
)

_register(
    Theme(
        id="sunset_chase",
        name="Sunset Chase",
        description="Chasing the last light: golden hour bleeding into magenta, rose, and violet",
        palette=(
            ThemeColor(hue=45, saturation=95),
            ThemeColor(hue=22, saturation=100),
            ThemeColor(hue=338, saturation=95),
            ThemeColor(hue=275, saturation=85),
            ThemeColor(hue=8, saturation=100),
            ThemeColor(hue=350, saturation=90),
        ),
        mood=ThemeMood(warmth=0.62, energy=0.72, contrast=0.72),
        color_temp_mireds=375,
        color_temp_range=85,
        default_brightness=70,
        brightness_variation=32,
    )
)

_register(
    Theme(
        id="ocean_pulse",
        name="Ocean Pulse",
        description="Sapphire deep, cyan surf, and aquamarine shallows rippling through the room",
        palette=(
            ThemeColor(hue=192, saturation=92),
            ThemeColor(hue=218, saturation=96),
            ThemeColor(hue=175, saturation=82),
            ThemeColor(hue=202, saturation=100),
            ThemeColor(hue=235, saturation=88),
            ThemeColor(hue=158, saturation=76),
        ),
        mood=ThemeMood(warmth=0.12, energy=0.68, contrast=0.65),
        color_temp_mireds=248,
        color_temp_range=65,
        default_brightness=65,
        brightness_variation=32,
    )
)

_register(
    Theme(
        id="party",
        name="Party",
        description="Full-spectrum saturated primaries — maximum energy",
        palette=(
            ThemeColor(hue=0, saturation=100),
            ThemeColor(hue=60, saturation=100),
            ThemeColor(hue=120, saturation=100),
            ThemeColor(hue=180, saturation=100),
            ThemeColor(hue=240, saturation=100),
            ThemeColor(hue=300, saturation=100),
        ),
        mood=ThemeMood(warmth=0.5, energy=0.98, contrast=0.72),
        color_temp_mireds=350,
        color_temp_range=100,
        default_brightness=88,
        brightness_variation=22,
    )
)
