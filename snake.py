"""Core snake logic for the GUI implementation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

GridPosition = Tuple[int, int]


@dataclass
class Snake:
    """Represents the snake and manages its movement on the grid."""

    body: List[GridPosition]
    direction: GridPosition
    pending_direction: GridPosition

    @classmethod
    def create_centered(cls, grid_width: int, grid_height: int, length: int) -> "Snake":
        """Create a horizontal snake centered within the grid."""

        center_x = grid_width // 2
        center_y = grid_height // 2
        body = [(center_x - i, center_y) for i in range(length)]
        direction = (1, 0)
        return cls(body=body, direction=direction, pending_direction=direction)

    @property
    def head(self) -> GridPosition:
        """Return the current head coordinate of the snake."""

        return self.body[0]

    def set_direction(self, vector: GridPosition) -> None:
        """Queue a direction change, ignoring opposite moves."""

        if not self._is_opposite(vector):
            self.pending_direction = vector

    def commit_direction(self) -> None:
        """Apply the pending direction change."""

        self.direction = self.pending_direction

    def move(self, grow: bool = False) -> None:
        """Advance the snake by one grid cell.

        Args:
            grow: When ``True`` the snake extends by one segment.
        """

        head_x, head_y = self.head
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def occupies(self, position: GridPosition) -> bool:
        """Return ``True`` if the snake occupies ``position``."""

        return position in self.body

    def reset(self, grid_width: int, grid_height: int, length: int) -> None:
        """Reset the snake to its initial centered configuration."""

        refreshed = self.create_centered(grid_width, grid_height, length)
        self.body = refreshed.body
        self.direction = refreshed.direction
        self.pending_direction = refreshed.pending_direction

    def _is_opposite(self, vector: GridPosition) -> bool:
        """Determine whether ``vector`` is opposite to the current direction."""

        dir_x, dir_y = self.direction
        vec_x, vec_y = vector
        return dir_x == -vec_x and dir_y == -vec_y


DirectionMap = Sequence[Tuple[Sequence[int], GridPosition]]

# Mapping of keys to direction vectors for convenience when processing events.
DIRECTION_VECTORS: DirectionMap = (
    ((ord("w"), ord("W")), (0, -1)),
    ((ord("s"), ord("S")), (0, 1)),
    ((ord("a"), ord("A")), (-1, 0)),
    ((ord("d"), ord("D")), (1, 0)),
)


__all__ = ["Snake", "GridPosition", "DIRECTION_VECTORS"]
