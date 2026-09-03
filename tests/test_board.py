"""Tests for the game rules. The board is pure, so no terminal is involved."""

from __future__ import annotations

import random

import pytest

from game2048.board import (
    Direction,
    can_move,
    collapse,
    empty_cells,
    empty_grid,
    has_won,
    max_tile,
    move,
    spawn_tile,
)


@pytest.mark.parametrize(
    "row, expected, gained",
    [
        ([0, 0, 0, 0], [0, 0, 0, 0], 0),
        ([2, 0, 0, 0], [2, 0, 0, 0], 0),
        ([0, 0, 0, 2], [2, 0, 0, 0], 0),
        ([2, 2, 0, 0], [4, 0, 0, 0], 4),
        ([2, 0, 2, 0], [4, 0, 0, 0], 4),
        ([2, 2, 2, 0], [4, 2, 0, 0], 4),
        ([2, 2, 2, 2], [4, 4, 0, 0], 8),
        ([4, 4, 8, 8], [8, 16, 0, 0], 24),
        ([2, 4, 2, 4], [2, 4, 2, 4], 0),
    ],
)
def test_collapse(row, expected, gained):
    assert collapse(row) == (expected, gained)


def test_a_tile_merges_only_once_per_move():
    # [4, 4, 8] would become [16] if merges chained; the rules forbid that.
    assert collapse([4, 4, 8, 0]) == ([8, 8, 0, 0], 8)


def test_move_left():
    grid = [
        [2, 2, 0, 0],
        [0, 4, 4, 0],
        [0, 0, 0, 8],
        [2, 0, 2, 2],
    ]
    result, gained, moved = move(grid, Direction.LEFT)
    assert result == [
        [4, 0, 0, 0],
        [8, 0, 0, 0],
        [8, 0, 0, 0],
        [4, 2, 0, 0],
    ]
    assert gained == 16
    assert moved is True


def test_move_right_is_a_mirrored_left():
    grid = empty_grid()
    grid[0] = [2, 2, 0, 0]
    result, gained, moved = move(grid, Direction.RIGHT)
    assert result[0] == [0, 0, 0, 4]
    assert (gained, moved) == (4, True)


def test_move_up_and_down():
    grid = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [4, 0, 0, 0],
        [4, 0, 0, 0],
    ]
    up, up_score, _ = move(grid, Direction.UP)
    assert [row[0] for row in up] == [4, 8, 0, 0]
    assert up_score == 12

    down, down_score, _ = move(grid, Direction.DOWN)
    assert [row[0] for row in down] == [0, 0, 4, 8]
    assert down_score == 12


def test_move_reports_when_nothing_changes():
    grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    result, gained, moved = move(grid, Direction.LEFT)
    assert result == grid
    assert (gained, moved) == (0, False)


def test_move_does_not_mutate_the_original_grid():
    grid = empty_grid()
    grid[0] = [2, 2, 0, 0]
    snapshot = [row[:] for row in grid]
    move(grid, Direction.LEFT)
    assert grid == snapshot


def test_spawn_tile_fills_one_empty_cell():
    grid = empty_grid()
    assert spawn_tile(grid, random.Random(0)) is True
    assert len(empty_cells(grid)) == 15
    assert max_tile(grid) in (2, 4)


def test_spawn_tile_on_a_full_board():
    grid = [[2] * 4 for _ in range(4)]
    assert spawn_tile(grid, random.Random(0)) is False


def test_can_move():
    full_but_mergeable = [
        [2, 2, 4, 8],
        [4, 8, 16, 32],
        [2, 4, 8, 16],
        [4, 8, 16, 32],
    ]
    assert can_move(full_but_mergeable) is True

    dead = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert can_move(dead) is False
    assert can_move(empty_grid()) is True


def test_has_won():
    grid = empty_grid()
    grid[0][0] = 1024
    assert has_won(grid) is False
    grid[0][0] = 2048
    assert has_won(grid) is True
    assert has_won(grid, target=4096) is False


def test_other_board_sizes_are_supported():
    grid = empty_grid(size=5)
    assert len(grid) == 5 and len(grid[0]) == 5
    grid[0] = [2, 2, 2, 2, 2]
    result, gained, _ = move(grid, Direction.LEFT)
    assert result[0] == [4, 4, 2, 0, 0]
    assert gained == 8
