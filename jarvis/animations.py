"""Animations: the parts that make JARVIS feel alive.

Everything here degrades to nothing when stdout is not a terminal, when
NO_COLOR is set, or when `animations` is off in config. Nothing blocks the main
thread: every animation runs in a daemon thread and is stopped by an Event.

    with Listening("listening", haptics=True):
        text = capture_speech()

    boot_sequence(ui.banner_style)     # Iron-Man-ish startup
    wake_flash()                       # one-off "I heard you" pulse
"""

from __future__ import annotations

import math
import random
import sys
import threading
import time

from . import ui

BARS = "▁▂▃▄▅▆▇█"
GLYPHS_THINK = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
GLYPHS_WAKE = "◜◝◞◟"


def enabled(force: bool | None = None) -> bool:
    """Animations only run on a real terminal, and only if config allows."""
    if force is not None:
        return force
    if sys.stdout.isatty() is False:
        return False
    return ui.ENABLED


def _write(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


def waveform_frame(tick: int, width: int = 36, level: float = 1.0) -> str:
    """One frame of the listening waveform (pure, so it can be tested)."""
    cells = []
    for i in range(width):
        phase = tick * 0.55 + i * 0.42
        envelope = 0.55 + 0.45 * math.sin(tick * 0.18 + i * 0.07)
        value = abs(math.sin(phase)) * envelope * level
        value = min(0.999, max(0.0, value + random.uniform(-0.05, 0.05)))
        cells.append(BARS[int(value * (len(BARS) - 1))])
    return "".join(cells)


class Listening:
    """Scrolling waveform shown while the microphone is open."""

    def __init__(self, label: str = "listening", force: bool | None = None, haptics: bool = False):
        self.label = label
        self.force = force
        self.haptics = haptics
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "Listening":
        if self.haptics:
            from . import shims

            shims.run(["termux-vibrate", "-d", "45", "-f"], timeout=3)
        if not enabled(self.force):
            return self
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        width = max(12, min(38, ui.width() - len(self.label) - 10))
        tick = 0
        icon = "◉"
        while not self._stop.is_set():
            frame = waveform_frame(tick, width)
            spinner = GLYPHS_WAKE[tick % len(GLYPHS_WAKE)]
            _write(
                f"\r  {ui.cyan(spinner)} {ui.dim(self.label)} "
                f"{ui.cyan(icon)} {ui.dim(frame)}  "
            )
            tick += 1
            time.sleep(0.07)
        _write("\r" + " " * (width + len(self.label) + 12) + "\r")

    def __exit__(self, *exc) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.4)
        if self.haptics:
            from . import shims

            shims.run(["termux-vibrate", "-d", "25", "-f"], timeout=3)


class Thinking:
    """HUD spinner with elapsed time — used while the model reasons."""

    FRAMES = GLYPHS_THINK

    def __init__(self, label: str = "thinking", force: bool | None = None):
        self.label = label
        self.force = force
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "Thinking":
        if not enabled(self.force):
            return self
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        started = time.monotonic()
        tick = 0
        while not self._stop.is_set():
            elapsed = time.monotonic() - started
            frame = self.FRAMES[tick % len(self.FRAMES)]
            dots = "." * (1 + tick // 4 % 3)
            _write(
                f"\r  {ui.gold(frame)} {ui.dim(self.label + dots)}"
                f"{ui.dim(f'  {elapsed:4.1f}s')}   "
            )
            tick += 1
            time.sleep(0.08)
        _write("\r" + " " * (len(self.label) + 22) + "\r")

    def __exit__(self, *exc) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.4)

    # allow `with Thinking(...) as t:` style use in the agent
    def __bool__(self) -> bool:
        return True


def wake_flash(word: str = "jarvis", force: bool | None = None) -> None:
    """A short gold pulse confirming the wake word was heard."""
    if not enabled(force):
        return
    for tick in range(6):
        frame = GLYPHS_WAKE[tick % len(GLYPHS_WAKE)]
        _write(f"\r  {ui.gold(frame)} {ui.gold(word.upper())} {ui.dim('heard')}   ")
        time.sleep(0.05)
    _write("\r" + " " * (len(word) + 18) + "\r")


BOOT_LINES = (
    "loading personality matrix",
    "waking device bridge (termux-api)",
    "indexing installed applications",
    "reticulating splines",
    "arming wake protocol",
)


def boot_sequence(force: bool | None = None, delay: float = 0.055) -> None:
    """Short startup sequence, skipped entirely when not on a terminal."""
    if not enabled(force):
        return
    for line in BOOT_LINES:
        _write(f"  {ui.gold('▸')} {ui.dim(line)}")
        for dots in range(3):
            time.sleep(delay)
            _write(ui.dim("."))
        time.sleep(delay)
        _write(ui.green("  ok") + "\n")
    time.sleep(0.12)


def demo(seconds: float = 3.0) -> None:
    """Preview every animation: python jarvis.py --demo"""
    if not sys.stdout.isatty():
        print("animations need a real terminal (run this in Termux, not a pipe)")
        return
    ui.banner("preview", "animations", False)
    boot_sequence(force=True)
    wake_flash("jarvis", force=True)
    with Listening("listening", force=True, haptics=False):
        time.sleep(seconds)
    with Thinking("thinking", force=True):
        time.sleep(seconds)
    ui.jarvis("Animations nominal, sir.")
    print(ui.dim("  (haptics and toasts also fire on device: --demo on the phone)"))
