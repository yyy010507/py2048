"""Game state: the board plus score, undo and persistence of the best score."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from .board import (
    DEFAULT_SIZE,
    DEFAULT_TARGET,
    Direction,
    Grid,
    can_move,
    empty_grid,
    has_won,
    max_tile,
    move,
    spawn_tile,
)

BEST_SCORE_FILE = Path.home() / ".py2048.json"


def load_best_score(path: Path = BEST_SCORE_FILE) -> int:
    """Read the stored best score, treating any unreadable file as "no record"."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return int(data["best"])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def save_best_score(score: int, path: Path = BEST_SCORE_FILE) -> None:
    """Store the best score, silently ignoring a read-only home directory."""
    try:
        path.write_text(json.dumps({"best": score}), encoding="utf-8")
    except OSError:
        pass


@dataclass
class Game:
    """A single session: the grid, the score and one level of undo."""

    size: int = DEFAULT_SIZE
    target: int = DEFAULT_TARGET
    rng: random.Random = field(default_factory=random.Random)
    best_file: Path = BEST_SCORE_FILE
    grid: Grid = field(init=False)
    score: int = field(init=False, default=0)
    best: int = field(init=False, default=0)
    won: bool = field(init=False, default=False)
    _previous: Optional[Tuple[Grid, int]] = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.best = load_best_score(self.best_file)
        self.restart()

    def restart(self) -> None:
        """Start over with two tiles on an empty board."""
        self.grid = empty_grid(self.size)
        self.score = 0
        self.won = False
        self._previous = None
        spawn_tile(self.grid, self.rng)
        spawn_tile(self.grid, self.rng)

    def play(self, direction: Direction) -> bool:
        """Apply a move and spawn a tile. Returns False if the move changed nothing."""
        new_grid, gained, moved = move(self.grid, direction)
        if not moved:
            return False

        self._previous = ([row[:] for row in self.grid], self.score)
        self.grid = new_grid
        self.score += gained
        if self.score > self.best:
            self.best = self.score
            save_best_score(self.best, self.best_file)
        if not self.won and has_won(self.grid, self.target):
            self.won = True
        spawn_tile(self.grid, self.rng)
        return True

    def undo(self) -> bool:
        """Step back one move. Only the most recent move is remembered."""
        if self._previous is None:
            return False
        self.grid, self.score = self._previous
        self._previous = None
        return True

    @property
    def can_undo(self) -> bool:
        return self._previous is not None

    @property
    def is_over(self) -> bool:
        return not can_move(self.grid)

    @property
    def max_tile(self) -> int:
        return max_tile(self.grid)
