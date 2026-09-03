"""Tests for the session layer: scoring, undo and the best-score file."""

from __future__ import annotations

import random

import pytest

from game2048.board import Direction, empty_grid
from game2048.game import Game, load_best_score, save_best_score


@pytest.fixture
def game(tmp_path):
    """A game with a seeded RNG and its best score kept out of the real home."""
    return Game(rng=random.Random(1), best_file=tmp_path / "best.json")


def test_a_new_game_starts_with_two_tiles(game):
    filled = [value for row in game.grid for value in row if value]
    assert len(filled) == 2
    assert game.score == 0


def test_play_scores_and_adds_a_tile(game):
    game.grid = empty_grid()
    game.grid[0] = [2, 2, 0, 0]
    assert game.play(Direction.LEFT) is True
    assert game.score == 4
    filled = [value for row in game.grid for value in row if value]
    assert len(filled) == 2  # the merged 4 plus the freshly spawned tile


def test_play_rejects_a_move_that_changes_nothing(game):
    game.grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert game.play(Direction.LEFT) is False
    assert game.score == 0
    assert game.is_over is True


def test_undo_restores_the_previous_grid_and_score(game):
    game.grid = empty_grid()
    game.grid[0] = [2, 2, 0, 0]
    before = [row[:] for row in game.grid]

    assert game.can_undo is False
    game.play(Direction.LEFT)
    assert game.can_undo is True
    assert game.undo() is True
    assert game.grid == before
    assert game.score == 0
    assert game.undo() is False  # only one level of undo is kept


def test_restart_clears_the_score(game):
    game.score = 500
    game.restart()
    assert game.score == 0
    assert game.can_undo is False


def test_the_best_score_follows_the_score(game):
    game.grid = empty_grid()
    game.grid[0] = [2, 2, 0, 0]
    game.play(Direction.LEFT)
    assert game.best == 4
    assert load_best_score(game.best_file) == 4


def test_best_score_round_trips(tmp_path):
    path = tmp_path / "best.json"
    assert load_best_score(path) == 0  # a missing file simply means no record
    save_best_score(1234, path)
    assert load_best_score(path) == 1234

    path.write_text("not json", encoding="utf-8")
    assert load_best_score(path) == 0  # a corrupt file is not fatal


def test_winning_flag_is_set_once_the_target_is_reached(tmp_path):
    game = Game(target=8, rng=random.Random(3), best_file=tmp_path / "best.json")
    game.grid = empty_grid()
    game.grid[0] = [4, 4, 0, 0]
    game.play(Direction.LEFT)
    assert game.won is True
