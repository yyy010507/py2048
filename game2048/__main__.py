"""Command line entry point: argument parsing and the main game loop."""

from __future__ import annotations

import argparse
import random
import sys

from . import __version__
from .board import DEFAULT_SIZE, DEFAULT_TARGET
from .game import Game
from .ui import (
    KEY_BINDINGS,
    Palette,
    clear_screen,
    hide_cursor,
    read_key,
    render,
    setup_terminal,
    show_cursor,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="py2048", description="Play 2048 in your terminal."
    )
    parser.add_argument(
        "--size", type=int, default=DEFAULT_SIZE, help="board side length (default: 4)"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=DEFAULT_TARGET,
        help="tile that counts as a win (default: 2048)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="seed the RNG for a reproducible game"
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colours")
    parser.add_argument("--version", action="version", version=f"py2048 {__version__}")
    args = parser.parse_args(argv)
    if args.size < 2:
        parser.error("--size must be at least 2")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    setup_terminal()

    palette = Palette(enabled=not args.no_color and sys.stdout.isatty())
    game = Game(size=args.size, target=args.target, rng=random.Random(args.seed))
    message = ""

    hide_cursor()
    try:
        while True:
            clear_screen()
            print(render(game.grid, game.score, game.best, palette, message))
            message = ""

            if game.is_over:
                print(f"\n  game over - final score {game.score}. r restarts, q quits.")

            key = read_key()
            if key == "q":
                break
            if key == "r":
                game.restart()
                continue
            if key == "u":
                message = "" if game.undo() else "nothing to undo"
                continue

            direction = KEY_BINDINGS.get(key or "")
            if direction is None:
                continue
            if not game.play(direction) and not game.is_over:
                message = "that move changes nothing"
            elif game.won:
                message = f"you reached {args.target}! keep going or press q"
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()

    print(f"final score {game.score} - best {game.best}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
