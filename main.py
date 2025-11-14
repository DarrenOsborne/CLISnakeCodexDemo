"""Application entry point for the modern Snake GUI."""
from __future__ import annotations

import pygame

from game import SnakeGame


def main() -> None:
    """Initialise pygame and launch the Snake game."""

    pygame.init()
    pygame.font.init()
    game = SnakeGame()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
