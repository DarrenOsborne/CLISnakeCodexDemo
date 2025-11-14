"""Main gameplay loop and rendering for the Snake GUI."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable, List, Optional, Sequence

import pygame

from snake import DIRECTION_VECTORS, GridPosition, Snake
from theme import Theme, get_themes

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
GRID_WIDTH = 28
GRID_HEIGHT = 20
CELL_SIZE = 24
PLAYFIELD_TOP = 140
INITIAL_SNAKE_LENGTH = 5
MOVE_INTERVAL = 0.12
FPS = 60
HIGH_SCORE_FILE = Path(__file__).resolve().parent / "highscore.dat"


class GameState(Enum):
    """Enumeration describing the different screens of the game."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


@dataclass
class Button:
    """Simple clickable button used across the interface."""

    rect: pygame.Rect
    text: str
    callback: Callable[[], None]
    font: Optional[pygame.font.Font] = None

    def draw(self, surface: pygame.Surface, theme: Theme, mouse_pos: GridPosition) -> None:
        """Draw the button with hover feedback."""

        hovered = self.rect.collidepoint(mouse_pos)
        accent = theme.accent
        highlight = _lerp_color(accent, (255, 255, 255), 0.35 if hovered else 0.2)
        button_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        button_surface.fill((*highlight, 210 if hovered else 180))
        pygame.draw.rect(
            button_surface,
            (*theme.text_secondary, 230),
            button_surface.get_rect(),
            width=2,
            border_radius=14,
        )
        surface.blit(button_surface, self.rect.topleft)
        font = self.font or pygame.font.Font(None, 32)
        label = font.render(self.text, True, theme.text_primary)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class SnakeGame:
    """Encapsulates the Snake gameplay, UI, and rendering."""

    def __init__(self) -> None:
        pygame.display.set_caption("Snake: Modern GUI Edition")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.themes: Sequence[Theme] = list(get_themes())
        self.selected_theme_index = 0
        self.active_theme: Theme = self.themes[0]

        self.title_font = pygame.font.Font(None, 96)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.ui_font = pygame.font.Font(None, 36)
        self.hud_font = pygame.font.Font(None, 32)

        self.playfield_rect = pygame.Rect(
            (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2,
            PLAYFIELD_TOP,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE,
        )

        self.state = GameState.MENU
        self.score = 0
        self.high_score = self._load_high_score()
        self.victory = False

        self.snake = Snake.create_centered(GRID_WIDTH, GRID_HEIGHT, INITIAL_SNAKE_LENGTH)
        self.previous_body: List[GridPosition] = list(self.snake.body)
        self.move_progress = 0.0

        self.food_position: Optional[GridPosition] = None
        self.food_pulse_time = 0.0

        self.gradient_phase = 0.0

        self.menu_buttons: List[Button] = []
        self.theme_cycle_buttons: List[Button] = []
        self.game_over_buttons: List[Button] = []

        self._build_menu_buttons()
        self._build_game_over_buttons()
        self._reset_game_state()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------
    def _build_menu_buttons(self) -> None:
        center_x = WINDOW_WIDTH // 2
        start_rect = pygame.Rect(0, 0, 260, 60)
        start_rect.center = (center_x, 360)
        quit_rect = pygame.Rect(0, 0, 260, 60)
        quit_rect.center = (center_x, 440)

        theme_left = pygame.Rect(0, 0, 60, 60)
        theme_left.center = (center_x - 150, 260)
        theme_right = pygame.Rect(0, 0, 60, 60)
        theme_right.center = (center_x + 150, 260)

        self.start_button = Button(start_rect, "Start Game", self.start_game, self.ui_font)
        self.quit_button = Button(quit_rect, "Quit", self.quit, self.ui_font)
        self.theme_prev_button = Button(theme_left, "<", lambda: self.change_theme(-1), self.ui_font)
        self.theme_next_button = Button(theme_right, ">", lambda: self.change_theme(1), self.ui_font)

        self.menu_buttons = [self.start_button, self.quit_button]
        self.theme_cycle_buttons = [self.theme_prev_button, self.theme_next_button]

    def _build_game_over_buttons(self) -> None:
        modal_width = 420
        modal_height = 320
        modal_rect = pygame.Rect(0, 0, modal_width, modal_height)
        modal_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.game_over_modal_rect = modal_rect

        button_width = modal_width - 120
        restart_rect = pygame.Rect(0, 0, button_width, 56)
        restart_rect.center = (modal_rect.centerx, modal_rect.bottom - 110)
        menu_rect = pygame.Rect(0, 0, button_width, 56)
        menu_rect.center = (modal_rect.centerx, modal_rect.bottom - 40)

        self.restart_button = Button(restart_rect, "Restart", self.start_game, self.ui_font)
        self.menu_button = Button(menu_rect, "Main Menu", self.return_to_menu, self.ui_font)
        self.game_over_buttons = [self.restart_button, self.menu_button]

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Run the main loop until the window is closed."""

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.return_to_menu()
            return

        if self.state == GameState.MENU:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif key == pygame.K_LEFT:
                self.change_theme(-1)
            elif key == pygame.K_RIGHT:
                self.change_theme(1)
            return

        if self.state == GameState.GAME_OVER:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            return

        if key in (pygame.K_p, pygame.K_PAUSE):
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
            return

        if self.state not in (GameState.PLAYING, GameState.PAUSED):
            return

        direction_keys = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
        }
        if key in direction_keys:
            self.snake.set_direction(direction_keys[key])
            return

        for key_group, vector in DIRECTION_VECTORS:
            if key in key_group:
                self.snake.set_direction(vector)
                break

    def _handle_click(self, position: GridPosition) -> None:
        if self.state == GameState.MENU:
            for button in (*self.theme_cycle_buttons, *self.menu_buttons):
                if button.rect.collidepoint(position):
                    button.callback()
                    return
        elif self.state == GameState.GAME_OVER:
            for button in self.game_over_buttons:
                if button.rect.collidepoint(position):
                    button.callback()
                    return

    # ------------------------------------------------------------------
    # Update and rendering logic
    # ------------------------------------------------------------------
    def _update(self, dt: float) -> None:
        self.gradient_phase = (self.gradient_phase + dt * 35) % WINDOW_HEIGHT

        if self.state == GameState.MENU:
            return

        if self.state == GameState.PAUSED:
            return

        if self.state == GameState.GAME_OVER:
            return

        self.food_pulse_time += dt
        self.move_progress += dt

        while self.move_progress >= MOVE_INTERVAL:
            self.move_progress -= MOVE_INTERVAL
            self._advance_snake()
            if self.state == GameState.GAME_OVER:
                break

    def _draw(self) -> None:
        theme = self.current_theme
        self._draw_gradient_background(theme)

        if self.state == GameState.MENU:
            self._draw_menu(theme)
            return

        self._draw_playfield(theme)
        self._draw_hud(theme)

        if self.state == GameState.PAUSED:
            self._draw_pause_overlay(theme)
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over(theme)

    # ------------------------------------------------------------------
    # Gameplay helpers
    # ------------------------------------------------------------------
    def _advance_snake(self) -> None:
        self.snake.commit_direction()
        head_x, head_y = self.snake.head
        dir_x, dir_y = self.snake.direction
        next_head = (head_x + dir_x, head_y + dir_y)

        if not self._within_bounds(next_head):
            self._enter_game_over(False)
            return

        body_to_check = self.snake.body[:-1]
        if next_head in body_to_check:
            self._enter_game_over(False)
            return

        old_body = list(self.snake.body)
        will_grow = self.food_position is not None and next_head == self.food_position
        self.snake.move(grow=will_grow)
        self.previous_body = list(old_body)
        if will_grow:
            self.previous_body.append(old_body[-1])
            self.score += 1
            self._spawn_food()
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()

        if self.food_position is None:
            total_cells = GRID_WIDTH * GRID_HEIGHT
            if len(self.snake.body) >= total_cells:
                self._enter_game_over(True)

    def _within_bounds(self, position: GridPosition) -> bool:
        x, y = position
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def _spawn_food(self) -> None:
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake.body
        ]
        self.food_position = random.choice(available) if available else None
        self.food_pulse_time = 0.0

    def _enter_game_over(self, victory: bool) -> None:
        self.victory = victory
        self.state = GameState.GAME_OVER
        self.move_progress = 0.0
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw_gradient_background(self, theme: Theme) -> None:
        gradient_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        offset = (math.sin(self.gradient_phase * 0.02) + 1) / 2
        for y in range(WINDOW_HEIGHT):
            ratio = (y / WINDOW_HEIGHT + offset) % 1.0
            color = _lerp_color(theme.gradient_top, theme.gradient_bottom, ratio)
            pygame.draw.line(gradient_surface, color, (0, y), (WINDOW_WIDTH, y))
        self.screen.blit(gradient_surface, (0, 0))

    def _draw_menu(self, theme: Theme) -> None:
        mouse_pos = pygame.mouse.get_pos()
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("SNAKE", True, theme.text_primary)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.subtitle_font.render("Modern Arcade Edition", True, theme.text_secondary)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 210))
        self.screen.blit(subtitle, subtitle_rect)

        theme_label = self.ui_font.render("Theme", True, theme.text_primary)
        theme_label_rect = theme_label.get_rect(center=(WINDOW_WIDTH // 2, 260))
        self.screen.blit(theme_label, theme_label_rect)

        theme_name = self.ui_font.render(self.current_theme.name, True, theme.text_primary)
        name_rect = theme_name.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(theme_name, name_rect)

        for button in self.theme_cycle_buttons + self.menu_buttons:
            button.draw(self.screen, theme, mouse_pos)

    def _draw_playfield(self, theme: Theme) -> None:
        board_surface = pygame.Surface(self.playfield_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            board_surface,
            (*theme.playfield_border, 220),
            board_surface.get_rect(),
            border_radius=26,
        )
        inner_rect = board_surface.get_rect().inflate(-16, -16)
        pygame.draw.rect(
            board_surface,
            (*theme.playfield, 235),
            inner_rect,
            border_radius=22,
        )
        self.screen.blit(board_surface, self.playfield_rect.topleft)

        self._draw_grid(theme)
        self._draw_food(theme)
        self._draw_snake(theme)

    def _draw_grid(self, theme: Theme) -> None:
        color = (*theme.grid_color, 80)
        grid_surface = pygame.Surface(self.playfield_rect.size, pygame.SRCALPHA)
        for x in range(1, GRID_WIDTH):
            px = x * CELL_SIZE
            pygame.draw.line(grid_surface, color, (px, 0), (px, self.playfield_rect.height))
        for y in range(1, GRID_HEIGHT):
            py = y * CELL_SIZE
            pygame.draw.line(grid_surface, color, (0, py), (self.playfield_rect.width, py))
        self.screen.blit(grid_surface, self.playfield_rect.topleft)

    def _draw_food(self, theme: Theme) -> None:
        if not self.food_position:
            return
        fx, fy = self.food_position
        center_x = self.playfield_rect.left + int((fx + 0.5) * CELL_SIZE)
        center_y = self.playfield_rect.top + int((fy + 0.5) * CELL_SIZE)
        pulse = (math.sin(self.food_pulse_time * 4) + 1) / 2
        glow_radius = int(CELL_SIZE * (0.7 + 0.3 * pulse))
        core_radius = int(CELL_SIZE * 0.35)

        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*theme.food_color, 70),
            (glow_radius, glow_radius),
            glow_radius,
        )
        self.screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius), special_flags=pygame.BLEND_ADD)

        pygame.draw.circle(self.screen, theme.food_color, (center_x, center_y), core_radius)

    def _draw_snake(self, theme: Theme) -> None:
        alpha = 0.0
        if MOVE_INTERVAL > 0:
            alpha = min(1.0, max(0.0, self.move_progress / MOVE_INTERVAL))

        for index, position in enumerate(self.snake.body):
            prev_index = index if index < len(self.previous_body) else -1
            prev_position = self.previous_body[prev_index]
            interp_x = _lerp(prev_position[0], position[0], alpha)
            interp_y = _lerp(prev_position[1], position[1], alpha)
            pixel_x = int(round(self.playfield_rect.left + interp_x * CELL_SIZE))
            pixel_y = int(round(self.playfield_rect.top + interp_y * CELL_SIZE))
            rect = pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)
            color = theme.snake_head if index == 0 else theme.snake_body
            segment_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(
                segment_surface,
                (*color, 255),
                segment_surface.get_rect(),
                border_radius=16 if index == 0 else 12,
            )
            if index == 0:
                highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(
                    highlight,
                    (255, 255, 255, 90),
                    (CELL_SIZE // 2, CELL_SIZE // 2),
                    CELL_SIZE // 3,
                )
                segment_surface.blit(highlight, (0, 0), special_flags=pygame.BLEND_ADD)
            self.screen.blit(segment_surface, rect.topleft)

    def _draw_hud(self, theme: Theme) -> None:
        hud_height = 90
        hud_surface = pygame.Surface((WINDOW_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill((*theme.playfield_border, 60))
        self.screen.blit(hud_surface, (0, 0))

        score_text = self.hud_font.render(f"Score: {self.score}", True, theme.text_primary)
        high_score_text = self.hud_font.render(f"High Score: {self.high_score}", True, theme.text_primary)
        theme_text = self.hud_font.render(f"Theme: {self.active_theme.name}", True, theme.text_primary)

        self.screen.blit(score_text, (60, 30))
        high_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, 35))
        self.screen.blit(high_score_text, high_rect)
        theme_rect = theme_text.get_rect(topright=(WINDOW_WIDTH - 60, 30))
        self.screen.blit(theme_text, theme_rect)

    def _draw_pause_overlay(self, theme: Theme) -> None:
        overlay = pygame.Surface(self.playfield_rect.size, pygame.SRCALPHA)
        r, g, b, a = theme.overlay_tint
        overlay.fill((r, g, b, a))
        self.screen.blit(overlay, self.playfield_rect.topleft)
        text = self.subtitle_font.render("Paused", True, theme.text_primary)
        text_rect = text.get_rect(center=self.playfield_rect.center)
        self.screen.blit(text, text_rect)

    def _draw_game_over(self, theme: Theme) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        r, g, b, a = theme.overlay_tint
        overlay.fill((r, g, b, min(220, a + 40)))
        self.screen.blit(overlay, (0, 0))

        modal_surface = pygame.Surface(self.game_over_modal_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            modal_surface,
            (*theme.playfield_border, 240),
            modal_surface.get_rect(),
            border_radius=24,
        )
        inner = modal_surface.get_rect().inflate(-18, -18)
        pygame.draw.rect(
            modal_surface,
            (*theme.playfield, 245),
            inner,
            border_radius=20,
        )
        self.screen.blit(modal_surface, self.game_over_modal_rect.topleft)

        title_text = "You Win!" if self.victory else "Game Over"
        title_surface = self.subtitle_font.render(title_text, True, theme.text_primary)
        title_rect = title_surface.get_rect(center=(self.game_over_modal_rect.centerx, self.game_over_modal_rect.top + 70))
        self.screen.blit(title_surface, title_rect)

        score_text = self.ui_font.render(f"Score: {self.score}", True, theme.text_secondary)
        high_text = self.ui_font.render(f"High Score: {self.high_score}", True, theme.text_secondary)
        score_rect = score_text.get_rect(center=(self.game_over_modal_rect.centerx, self.game_over_modal_rect.top + 140))
        high_rect = high_text.get_rect(center=(self.game_over_modal_rect.centerx, self.game_over_modal_rect.top + 180))
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_text, high_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons:
            button.draw(self.screen, theme, mouse_pos)

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def start_game(self) -> None:
        self.active_theme = self.themes[self.selected_theme_index]
        self._reset_game_state()
        self.state = GameState.PLAYING

    def return_to_menu(self) -> None:
        self._reset_game_state()
        self.state = GameState.MENU

    def change_theme(self, offset: int) -> None:
        self.selected_theme_index = (self.selected_theme_index + offset) % len(self.themes)

    def quit(self) -> None:
        self.running = False

    @property
    def current_theme(self) -> Theme:
        if self.state == GameState.MENU:
            return self.themes[self.selected_theme_index]
        return self.active_theme

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _load_high_score(self) -> int:
        try:
            return int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip())
        except (FileNotFoundError, ValueError, OSError):
            return 0

    def _save_high_score(self) -> None:
        try:
            HIGH_SCORE_FILE.write_text(str(self.high_score), encoding="utf-8")
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def _reset_game_state(self) -> None:
        self.snake.reset(GRID_WIDTH, GRID_HEIGHT, INITIAL_SNAKE_LENGTH)
        self.previous_body = list(self.snake.body)
        self.move_progress = 0.0
        self.score = 0
        self.food_position = None
        self.food_pulse_time = 0.0
        self.victory = False
        self._spawn_food()


def _lerp_color(a: GridPosition, b: GridPosition, t: float) -> GridPosition:
    t = max(0.0, min(1.0, t))
    return tuple(int(ai + (bi - ai) * t) for ai, bi in zip(a, b))  # type: ignore[return-value]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


__all__ = ["SnakeGame", "GameState"]
