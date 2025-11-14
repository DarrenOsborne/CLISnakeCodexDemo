# CLI Snake Codex Demo

A fully featured Snake game that runs entirely in a Unix-like terminal using
Python's built-in `curses` module. Move the snake, grab food, avoid walls and
your own tail, and compete for the top score recorded on disk.

## Features

- Smooth, flicker-free rendering in a bordered terminal play field.
- Keyboard controls using arrow keys or WASD.
- Pause (`p`) and quit (`q`) shortcuts plus restart prompts on game over.
- Random food placement that always appears in an empty cell.
- Full collision detection against walls and the snake's body.
- Persistent high score tracking stored in `highscore.dat` alongside the game.
- Clean, object-oriented structure with dedicated `Snake` and `SnakeGame` classes.
- Customisable board size, speed, and glyphs through module-level constants.

## Requirements

- Python 3.8 or newer.
- A Unix-like terminal (Linux, macOS, WSL) capable of running the standard
  library `curses` module. Windows users can run the game through WSL or another
  environment that supports curses.

No third-party packages are required.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/DarrenOsborne/CLISnakeCodexDemo.git
   cd CLISnakeCodexDemo
   ```

2. (Optional) Create and activate a virtual environment if you prefer to keep
   Python projects isolated. No extra dependencies need to be installed.

## Running the Game

Launch the game directly with Python:

```bash
python3 snake.py
```

The terminal will switch to a full-screen style interface managed by curses. The
terminal state is automatically restored when you quit the game.

## Controls

| Key(s)          | Action                         |
|-----------------|--------------------------------|
| Arrow keys/WASD | Move up, down, left, or right. |
| `p`             | Pause or resume the game.      |
| `q`             | Quit immediately.              |
| `r` (on game over) | Restart a new round.       |

The snake moves continuously even if no keys are pressed, so plan ahead and be
ready to change direction.

## High Scores

The highest score achieved is stored in `highscore.dat` in the repository
folder. If the file cannot be written (for example due to filesystem
permissions), the game will silently continue without saving.

## Customisation

You can tweak the game's behaviour by editing the constants at the top of
`snake.py`:

- `BOARD_WIDTH` and `BOARD_HEIGHT` – change the size of the play area.
- `TICK_RATE` – adjust the speed of the snake (lower is faster).
- `INITIAL_SNAKE_LENGTH` – start the snake longer or shorter.
- `WALL_CHAR`, `SNAKE_HEAD_CHAR`, `SNAKE_BODY_CHAR`, and `FOOD_CHAR` – adjust
  the characters used for drawing.

After modifying these values, rerun `python3 snake.py` to see the changes.

## Code Structure

- `snake.py` – Contains all game code, including:
  - `Direction`, a dataclass representing x/y deltas.
  - `Snake`, which tracks the snake's body segments and movement.
  - `SnakeGame`, responsible for game state, drawing, input, and the main loop.
  - Helper functions for key bindings, food placement, and high score storage.
  - A `start()` helper function and `main()` entry point used by
    `curses.wrapper` to safely manage the terminal state.

## Troubleshooting

- If the window looks distorted, enlarge the terminal so it can display at
  least 80×30 characters.
- On macOS you may need to install Python with `brew` to get a version linked
  against the system curses (Python 3.8+ installed via Homebrew works well).
- If the keyboard controls feel unresponsive, ensure the terminal has focus and
  that no other application is intercepting the arrow keys.

Enjoy the nostalgia and happy hacking!
