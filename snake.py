"""Command-line Snake game implemented with curses."""
from __future__ import annotations

import curses
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Constants controlling the board dimensions and gameplay speed.
BOARD_WIDTH = 40  # Interior width of the play area (in characters).
BOARD_HEIGHT = 20  # Interior height of the play area (in characters).
TICK_RATE = 0.1  # Seconds between frames.
INITIAL_SNAKE_LENGTH = 5

# Characters used for rendering elements on the board.
WALL_CHAR = "#"
SNAKE_HEAD_CHAR = "@"
SNAKE_BODY_CHAR = "o"
FOOD_CHAR = "*"
EMPTY_CHAR = " "

# Key mappings for controlling the snake.
KEY_BINDINGS: Dict[int, Tuple[int, int]] = {}
PAUSE_KEYS = {ord("p"), ord("P")}
QUIT_KEYS = {ord("q"), ord("Q")}
RESTART_KEYS = {ord("r"), ord("R")}

# High score storage location (adjacent to this script).
HIGH_SCORE_FILE = Path(__file__).resolve().parent / "highscore.dat"


@dataclass
class Direction:
    """Simple data class representing a movement direction."""

    dx: int
    dy: int

    def is_opposite(self, other: "Direction") -> bool:
        """Return ``True`` if ``other`` points in the exact opposite direction."""

        return self.dx == -other.dx and self.dy == -other.dy


def _build_key_bindings() -> None:
    """Populate the global key binding dictionary."""

    global KEY_BINDINGS
    KEY_BINDINGS = {
        curses.KEY_UP: (0, -1),
        curses.KEY_DOWN: (0, 1),
        curses.KEY_LEFT: (-1, 0),
        curses.KEY_RIGHT: (1, 0),
        ord("w"): (0, -1),
        ord("W"): (0, -1),
        ord("s"): (0, 1),
        ord("S"): (0, 1),
        ord("a"): (-1, 0),
        ord("A"): (-1, 0),
        ord("d"): (1, 0),
        ord("D"): (1, 0),
    }


@dataclass
class Snake:
    """Represents the snake, including its body segments and direction."""

    body: List[Tuple[int, int]]
    direction: Direction

    @property
    def head(self) -> Tuple[int, int]:
        """Return the current position of the snake's head."""

        return self.body[0]

    def move(self, grow: bool = False) -> None:
        """Move the snake in its current direction.

        Args:
            grow: If ``True`` the snake grows (the tail is not removed).
        """

        new_head = (self.head[0] + self.direction.dx, self.head[1] + self.direction.dy)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def set_direction(self, new_direction: Direction) -> None:
        """Update the snake's direction if it is not opposite the current one."""

        if not self.direction.is_opposite(new_direction):
            self.direction = new_direction

    def occupies(self, position: Tuple[int, int]) -> bool:
        """Return ``True`` if the snake occupies ``position``."""

        return position in self.body


class SnakeGame:
    """Main class coordinating the Snake game."""

    def __init__(self, screen: "curses._CursesWindow") -> None:
        self.screen = screen
        self.board_width = BOARD_WIDTH
        self.board_height = BOARD_HEIGHT
        self.window = curses.newwin(
            self.board_height + 2, self.board_width + 2, 1, 2
        )
        self.window.nodelay(True)
        self.window.keypad(True)
        self.window.timeout(0)
        self.score = 0
        self.high_score = self.load_high_score()
        self.snake = self._create_initial_snake()
        self.food: Optional[Tuple[int, int]] = None
        self.paused = False
        self.game_over = False
        self._place_food()

    def _create_initial_snake(self) -> Snake:
        """Create the initial snake positioned horizontally at the center."""

        center_x = self.board_width // 2
        center_y = self.board_height // 2
        body = [
            (center_x - i, center_y)
            for i in range(INITIAL_SNAKE_LENGTH)
        ]
        direction = Direction(dx=1, dy=0)
        return Snake(body=body, direction=direction)

    def run(self) -> None:
        """Primary game loop."""

        last_tick = time.monotonic()
        while True:
            now = time.monotonic()
            delta = now - last_tick
            if delta < TICK_RATE:
                time.sleep(max(TICK_RATE - delta, 0))
                now = time.monotonic()
                delta = now - last_tick
            last_tick = now

            if not self.game_over:
                self._handle_input()

            if self.paused:
                self._draw()
                continue

            if not self.game_over:
                self._update()
                self._draw()

            if self.game_over:
                self._draw()
                self._display_game_over()
                if not self._handle_game_over_input():
                    break
                self._reset()
                last_tick = time.monotonic()

    def _reset(self) -> None:
        """Reset game state for a new round."""

        self.snake = self._create_initial_snake()
        self.score = 0
        self.food = None
        self.paused = False
        self.game_over = False
        self._place_food()

    def _handle_input(self) -> None:
        """Process user input from the window."""

        while True:
            try:
                key = self.window.getch()
            except curses.error:
                break

            if key == -1:
                break

            if key in QUIT_KEYS:
                raise SystemExit

            if key in PAUSE_KEYS:
                self.paused = not self.paused
                continue

            if key in KEY_BINDINGS:
                dx, dy = KEY_BINDINGS[key]
                self.snake.set_direction(Direction(dx=dx, dy=dy))

    def _handle_game_over_input(self) -> bool:
        """Handle input on the game over screen.

        Returns ``True`` if the user chooses to restart, ``False`` to exit.
        """

        self.window.nodelay(False)
        self.window.timeout(-1)

        while True:
            key = self.window.getch()
            if key in QUIT_KEYS:
                return False
            if key in RESTART_KEYS:
                self.window.nodelay(True)
                self.window.timeout(0)
                return True

    def _update(self) -> None:
        """Advance the game state by one tick."""

        next_head = (
            self.snake.head[0] + self.snake.direction.dx,
            self.snake.head[1] + self.snake.direction.dy,
        )

        if self._hit_wall(*next_head):
            self.game_over = True
            return

        will_grow = self.food is not None and next_head == self.food
        body_to_check = self.snake.body if will_grow else self.snake.body[:-1]
        if next_head in body_to_check:
            self.game_over = True
            return

        self.snake.move(grow=will_grow)

        if will_grow:
            self.score += 1
            self._place_food()

        if self.food is None and len(self.snake.body) == self.board_width * self.board_height:
            # The player filled the board; treat as victory.
            self.game_over = True

    def _hit_wall(self, x: int, y: int) -> bool:
        """Return ``True`` if the coordinate intersects a wall."""

        return (
            x <= 0
            or x >= self.board_width + 1
            or y <= 0
            or y >= self.board_height + 1
        )

    def _available_cells(self) -> List[Tuple[int, int]]:
        """Compute a list of empty cells where food can spawn."""

        all_cells = [
            (x, y)
            for x in range(1, self.board_width + 1)
            for y in range(1, self.board_height + 1)
        ]
        return [cell for cell in all_cells if not self.snake.occupies(cell)]

    def _place_food(self) -> None:
        """Place food at a random available location."""

        empty_cells = self._available_cells()
        if not empty_cells:
            self.food = None
            return
        self.food = random.choice(empty_cells)

    def _draw(self) -> None:
        """Render the current game state."""

        self.window.erase()
        self.window.border(*[ord(WALL_CHAR)] * 8)

        # Draw food.
        if self.food:
            fx, fy = self.food
            self.window.addch(fy, fx, FOOD_CHAR)

        # Draw snake.
        for idx, (x, y) in enumerate(self.snake.body):
            char = SNAKE_HEAD_CHAR if idx == 0 else SNAKE_BODY_CHAR
            try:
                self.window.addch(y, x, char)
            except curses.error:
                # Ignore drawing errors when the snake hits the border while game over.
                pass

        self.window.refresh()
        self._draw_status_bar()

    def _draw_status_bar(self) -> None:
        """Display the score, high score, and instructions."""

        status = (
            f" Score: {self.score} "
            f"High Score: {self.high_score} "
            "(Arrows/WASD to move, P to pause, Q to quit)"
        )
        try:
            self.screen.move(0, 0)
            self.screen.clrtoeol()
            max_x = self.screen.getmaxyx()[1]
            self.screen.addstr(0, 0, status[: max_x - 1])
            if self.paused:
                pause_msg = " PAUSED "
                self.screen.addstr(
                    0,
                    max(0, max_x - len(pause_msg) - 1),
                    pause_msg,
                )
            self.screen.refresh()
        except curses.error:
            pass

    def _display_game_over(self) -> None:
        """Show the game over dialog and update high score."""

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score(self.high_score)

        if self.food is None and len(self.snake.body) == self.board_width * self.board_height:
            title = " YOU WIN! "
        else:
            title = " GAME OVER "

        msg_lines = [
            title,
            f" Score: {self.score}  High Score: {self.high_score} ",
            " Press R to restart or Q to quit ",
        ]

        height, width = self.window.getmaxyx()
        start_y = height // 2 - len(msg_lines) // 2

        for idx, line in enumerate(msg_lines):
            x = (width - len(line)) // 2
            try:
                self.window.addstr(start_y + idx, x, line)
            except curses.error:
                pass
        self.window.refresh()

    @staticmethod
    def load_high_score() -> int:
        """Load the high score from disk."""

        try:
            text = HIGH_SCORE_FILE.read_text(encoding="utf-8")
            return int(text.strip())
        except (FileNotFoundError, ValueError, OSError):
            return 0

    @staticmethod
    def save_high_score(score: int) -> None:
        """Persist the high score to disk."""

        try:
            HIGH_SCORE_FILE.write_text(str(score), encoding="utf-8")
        except OSError:
            pass


def main(stdscr: "curses._CursesWindow") -> None:
    """Entry point invoked by ``curses.wrapper``."""

    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(True)
    stdscr.keypad(True)
    _build_key_bindings()

    game = SnakeGame(stdscr)

    try:
        game.run()
    except SystemExit:
        pass


def start() -> None:
    """Launch the game using ``curses.wrapper`` to manage terminal state."""

    curses.wrapper(main)


if __name__ == "__main__":
    start()
