# Snake: Modern GUI Edition

A polished take on the classic Snake experience, rebuilt with a smooth 60 FPS
pygame interface. Glide through a vibrant playfield, chase glowing apples, and
switch between rich visual themes while competing for the high score.

## Features

- **Fluid animation** with interpolation so the snake glides between cells at
  roughly 60 frames per second.
- **Theme system** featuring Classic Green, Ocean Blue, and Cyberpunk palettes
  with matching gradients, accents, and overlays.
- **Animated visuals** including a pulsing apple glow, gentle menu gradients, and
  soft lighting on the snake.
- **Professional launch screen** with title, theme selection controls, Start and
  Quit buttons, and a dynamic background.
- **In-game HUD** showing the current score, persistent high score, and active
  theme.
- **Pause overlay** with dimmed playfield and prominent "Paused" status.
- **Game-over modal** summarising your run with options to restart or return to
  the main menu.
- **High score persistence** stored locally in `highscore.dat`.

## Requirements

- Python 3.9 or newer.
- A system capable of running [pygame](https://www.pygame.org/) (Windows, macOS,
  and Linux are supported).

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/DarrenOsborne/CLISnakeCodexDemo.git
   cd CLISnakeCodexDemo
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

Launch the GUI with Python:

```bash
python main.py
```

The game opens with a themed launch screen where you can pick a colour palette
before starting a run.

## Controls

| Key(s)            | Action                                      |
|-------------------|---------------------------------------------|
| Arrow keys / WASD | Move the snake.                             |
| `P`               | Pause or resume gameplay.                   |
| `Esc`             | Return to the main menu from any game state.|
| Mouse             | Interact with menu buttons and theme arrows.|

## Gameplay Overview

1. Choose a theme from the launch screen using the on-screen arrows, then click
   **Start Game**.
2. Guide the snake to the glowing apple. Each apple increases your score and the
   snake's length.
3. Avoid colliding with the snake's body or the edge of the arena. Fill the
   entire board to trigger a celebratory win.
4. Pause at any time with `P`, or return to the menu with `Esc`.

## High Scores

The highest score achieved is stored in `highscore.dat` in the project root. The
file is created automatically the first time you beat the current record.

## Customisation

- **Themes:** Adjust or add palettes in [`theme.py`](theme.py). Each theme
  controls gradients, snake colours, overlays, and highlight accents.
- **Board and speed:** Modify grid dimensions, cell size, or movement interval in
  [`game.py`](game.py) to tailor difficulty or presentation.
- **Snake behaviour:** The movement and collision logic is encapsulated in
  [`snake.py`](snake.py) if you want to experiment with new mechanics.

After making changes, rerun `python main.py` to see them in action.

Enjoy the neon glow and happy hacking!
