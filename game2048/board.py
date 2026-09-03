"""Pure game rules for 2048: the grid, the moves and tile spawning.

Nothing in this module touches the terminal, so every rule of the game can be
tested without simulating a single keypress.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import List, Sequence, Tuple

Grid = List[List[int]]

DEFAULT_SIZE = 4
DEFAULT_TARGET = 2048


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


def empty_grid(size: int = DEFAULT_SIZE) -> Grid:
    """Return a `size` x `size` grid with every cell empty (0)."""
    return [[0] * size for _ in range(size)]


def collapse(row: Sequence[int]) -> Tuple[List[int], int]:
    """Slide a single row to the left and merge equal neighbours.

    Returns the new row and the score gained. Each tile may merge only once
    per move, so [2, 2, 2, 2] becomes [4, 4, 0, 0] and not [8, 0, 0, 0].
    """
    tiles = [value for value in row if value]
    merged: List[int] = []
    gained = 0
    index = 0
    while index < len(tiles):
        if index + 1 < len(tiles) and tiles[index] == tiles[index + 1]:
            value = tiles[index] * 2
            merged.append(value)
            gained += value
            index += 2
        else:
            merged.append(tiles[index])
            index += 1
    merged.extend([0] * (len(row) - len(merged)))
    return merged, gained


def _transpose(grid: Grid) -> Grid:
    return [list(column) for column in zip(*grid)]


def _mirror(grid: Grid) -> Grid:
    return [row[::-1] for row in grid]


def move(grid: Grid, direction: Direction) -> Tuple[Grid, int, bool]:
    """Apply a move to the whole grid.

    Every direction is expressed as a left-collapse of a rotated grid, so the
    merging rules live in exactly one place. Returns the new grid, the score
    gained and whether anything actually moved.
    """
    if direction is Direction.LEFT:
        working = grid
    elif direction is Direction.RIGHT:
        working = _mirror(grid)
    elif direction is Direction.UP:
        working = _transpose(grid)
    else:  # Direction.DOWN
        working = _mirror(_transpose(grid))

    collapsed = []
    gained = 0
    for row in working:
        new_row, row_score = collapse(row)
        collapsed.append(new_row)
        gained += row_score

    if direction is Direction.LEFT:
        result = collapsed
    elif direction is Direction.RIGHT:
        result = _mirror(collapsed)
    elif direction is Direction.UP:
        result = _transpose(collapsed)
    else:  # Direction.DOWN
        result = _transpose(_mirror(collapsed))

    return result, gained, result != grid


def empty_cells(grid: Grid) -> List[Tuple[int, int]]:
    """Return the (row, column) coordinates of every empty cell."""
    return [
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value == 0
    ]


def spawn_tile(grid: Grid, rng: random.Random | None = None) -> bool:
    """Place a new tile (2 with 90% chance, otherwise 4) on a random empty cell.

    Mutates `grid` and returns False when there was no room left.
    """
    rng = rng or random
    cells = empty_cells(grid)
    if not cells:
        return False
    row, column = rng.choice(cells)
    grid[row][column] = 4 if rng.random() < 0.1 else 2
    return True


def can_move(grid: Grid) -> bool:
    """True while at least one direction would change the grid."""
    if empty_cells(grid):
        return True
    for row, values in enumerate(grid):
        for column, value in enumerate(values):
            if column + 1 < len(values) and value == values[column + 1]:
                return True
            if row + 1 < len(grid) and value == grid[row + 1][column]:
                return True
    return False


def max_tile(grid: Grid) -> int:
    """The largest value currently on the board."""
    return max(max(row) for row in grid)


def has_won(grid: Grid, target: int = DEFAULT_TARGET) -> bool:
    """True once the target tile has been built."""
    return max_tile(grid) >= target
