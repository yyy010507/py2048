"""Terminal rendering and key input.

Keeps every platform quirk — ANSI support on Windows, raw mode on POSIX — in
one place so `game.py` and `board.py` stay plain Python.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from .board import Direction, Grid

CELL_WIDTH = 7

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Background/foreground pairs roughly following the colours of the original game.
TILE_COLORS = {
    0: ("\033[48;5;236m", "\033[38;5;240m"),
    2: ("\033[48;5;253m", "\033[38;5;235m"),
    4: ("\033[48;5;250m", "\033[38;5;235m"),
    8: ("\033[48;5;215m", "\033[38;5;235m"),
    16: ("\033[48;5;209m", "\033[38;5;235m"),
    32: ("\033[48;5;203m", "\033[38;5;231m"),
    64: ("\033[48;5;196m", "\033[38;5;231m"),
    128: ("\033[48;5;227m", "\033[38;5;235m"),
    256: ("\033[48;5;226m", "\033[38;5;235m"),
    512: ("\033[48;5;220m", "\033[38;5;235m"),
    1024: ("\033[48;5;214m", "\033[38;5;235m"),
    2048: ("\033[48;5;208m", "\033[38;5;231m"),
}
BIG_TILE_COLOR = ("\033[48;5;160m", "\033[38;5;231m")

KEY_BINDINGS = {
    "a": Direction.LEFT,
    "d": Direction.RIGHT,
    "w": Direction.UP,
    "s": Direction.DOWN,
    "h": Direction.LEFT,
    "l": Direction.RIGHT,
    "k": Direction.UP,
    "j": Direction.DOWN,
    "left": Direction.LEFT,
    "right": Direction.RIGHT,
    "up": Direction.UP,
    "down": Direction.DOWN,
}


def setup_terminal() -> None:
    """Prepare the console: ANSI escape codes and UTF-8 output.

    Windows consoles often default to a legacy code page that cannot encode the
    box drawing characters, which would otherwise crash the first redraw.
    """
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # 7 = ENABLE_PROCESSED_OUTPUT | WRAP_AT_EOL | VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:  # pragma: no cover - depends on the host console
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover - exotic streams
        pass


class Palette:
    """Tile colours, or no colours at all when the output is not a terminal."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def tile(self, value: int) -> str:
        text = str(value) if value else "·"
        padded = text.center(CELL_WIDTH)
        if not self.enabled:
            return padded
        background, foreground = TILE_COLORS.get(value, BIG_TILE_COLOR)
        weight = BOLD if value >= 8 else ""
        return f"{background}{foreground}{weight}{padded}{RESET}"

    def style(self, text: str, code: str) -> str:
        return f"{code}{text}{RESET}" if self.enabled else text


def render(grid: Grid, score: int, best: int, palette: Palette, message: str = "") -> str:
    """Build the whole screen as a single string, ready to be printed at once."""
    size = len(grid)
    inner = CELL_WIDTH * size
    lines = [
        palette.style("  2048  ", BOLD),
        f"  score {palette.style(str(score), BOLD)}   best {best}",
        "",
        "  ┌" + "─" * inner + "┐",
    ]
    for row in grid:
        lines.append("  │" + "".join(palette.tile(value) for value in row) + "│")
    lines.append("  └" + "─" * inner + "┘")
    lines.append("")
    lines.append(palette.style("  arrows/wasd move · u undo · r restart · q quit", DIM))
    if message:
        lines.append("  " + message)
    return "\n".join(lines)


def clear_screen() -> None:
    sys.stdout.write("\033[H\033[J")


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")


def _read_key_windows() -> Optional[str]:
    import msvcrt

    char = msvcrt.getch()
    if char in (b"\x00", b"\xe0"):  # arrow keys arrive as a two-byte sequence
        arrows = {b"H": "up", b"P": "down", b"K": "left", b"M": "right"}
        return arrows.get(msvcrt.getch())
    if char in (b"\x03", b"\x04"):  # Ctrl-C / Ctrl-D
        return "q"
    try:
        return char.decode("utf-8").lower()
    except UnicodeDecodeError:
        return None


def _read_key_posix() -> Optional[str]:
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    try:
        tty.setraw(descriptor)
        char = sys.stdin.read(1)
        if char == "\x1b":  # escape sequence: arrow keys are ESC [ A..D
            sequence = sys.stdin.read(2)
            arrows = {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}
            return arrows.get(sequence)
        if char in ("\x03", "\x04"):
            return "q"
        return char.lower()
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, saved)


def read_key() -> Optional[str]:
    """Block until a key is pressed and return it as a lowercase name."""
    if os.name == "nt":
        return _read_key_windows()
    return _read_key_posix()
