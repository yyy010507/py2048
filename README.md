# py2048

The game 2048, playable in your terminal. Pure Python, no dependencies.

```
  2048

  score 4880   best 12744

  ┌────────────────────────────┐
  │   2      8      4      2   │
  │   ·      32     16     4   │
  │   ·      ·     128     64  │
  │   ·      ·      ·     1024 │
  └────────────────────────────┘

  arrows/wasd move · u undo · r restart · q quit
```

## Install

Requires Python 3.9 or newer.

```bash
git clone https://github.com/YOUR_NAME/py2048.git
cd py2048
python -m game2048
```

Or install it so the `py2048` command is available everywhere:

```bash
pip install .
py2048
```

## Controls

| Key | Action |
| --- | --- |
| arrows, `wasd`, `hjkl` | move the tiles |
| `u` | undo the last move |
| `r` | restart |
| `q` | quit |

## Options

```
python -m game2048 --size 5        # play on a 5x5 board
python -m game2048 --target 4096   # decide what counts as a win
python -m game2048 --seed 42       # reproducible tile spawns
python -m game2048 --no-color      # plain output, no ANSI colours
```

Your best score is kept in `~/.py2048.json` between sessions.

## How it works

The code is split so that the rules can be tested without a terminal:

| File | Responsibility |
| --- | --- |
| `game2048/board.py` | the rules: sliding, merging, spawning, game over |
| `game2048/game.py` | one session: score, undo, the stored best score |
| `game2048/ui.py` | drawing the board and reading keys on Windows and POSIX |
| `game2048/__main__.py` | arguments and the main loop |

Every move is expressed as a left-collapse of a rotated grid, so the merging
rules live in exactly one function (`collapse`) instead of four near-copies.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
