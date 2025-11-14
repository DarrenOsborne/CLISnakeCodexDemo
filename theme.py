"""Definitions for visual themes used by the Snake GUI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

Color = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]


@dataclass(frozen=True)
class Theme:
    """Container describing the palette and styling for the game."""

    name: str
    gradient_top: Color
    gradient_bottom: Color
    playfield: Color
    playfield_border: Color
    grid_color: Color
    snake_head: Color
    snake_body: Color
    food_color: Color
    text_primary: Color
    text_secondary: Color
    accent: Color
    overlay_tint: RGBAColor


def get_themes() -> Sequence[Theme]:
    """Return the available visual themes for the game."""

    classic_green = Theme(
        name="Classic Green",
        gradient_top=(16, 64, 32),
        gradient_bottom=(20, 120, 60),
        playfield=(24, 40, 24),
        playfield_border=(70, 170, 90),
        grid_color=(60, 110, 70),
        snake_head=(240, 250, 90),
        snake_body=(120, 220, 90),
        food_color=(255, 80, 90),
        text_primary=(235, 250, 230),
        text_secondary=(200, 220, 205),
        accent=(140, 235, 120),
        overlay_tint=(10, 30, 15, 180),
    )

    ocean_blue = Theme(
        name="Ocean Blue",
        gradient_top=(15, 40, 80),
        gradient_bottom=(25, 120, 180),
        playfield=(18, 55, 95),
        playfield_border=(90, 170, 220),
        grid_color=(70, 125, 170),
        snake_head=(255, 255, 255),
        snake_body=(120, 200, 255),
        food_color=(255, 150, 80),
        text_primary=(225, 240, 255),
        text_secondary=(200, 220, 245),
        accent=(140, 210, 255),
        overlay_tint=(10, 30, 55, 180),
    )

    cyberpunk = Theme(
        name="Cyberpunk",
        gradient_top=(40, 0, 60),
        gradient_bottom=(140, 10, 160),
        playfield=(45, 10, 65),
        playfield_border=(255, 0, 110),
        grid_color=(120, 45, 150),
        snake_head=(10, 255, 240),
        snake_body=(180, 50, 255),
        food_color=(255, 70, 180),
        text_primary=(240, 220, 255),
        text_secondary=(215, 200, 230),
        accent=(0, 255, 200),
        overlay_tint=(40, 5, 70, 190),
    )

    return [classic_green, ocean_blue, cyberpunk]


__all__: List[str] = ["Theme", "get_themes"]
