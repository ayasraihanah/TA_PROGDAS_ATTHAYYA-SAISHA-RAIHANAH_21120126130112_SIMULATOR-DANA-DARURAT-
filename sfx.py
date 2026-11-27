# -*- coding: utf-8 -*-
"""sfx.py - Efek suara retro 8-bit ringan (Windows winsound non-blocking)."""
import threading

try:
    import winsound
except ImportError:
    winsound = None

MUTE = False

_NOTES = {
    "click": [(980, 35)],
    "coin": [(988, 55), (1319, 110)],
    "star": [(1047, 50), (1319, 50), (1568, 90)],
    "boot": [(523, 60), (659, 60), (784, 60), (1047, 130)],
    "lvl": [(587, 70), (784, 70), (988, 70), (1175, 160)],
    "hit": [(220, 70), (155, 95)],
}


def toggle():
    global MUTE
    MUTE = not MUTE


def play(name="click"):
    if MUTE or winsound is None:
        return
    seq = _NOTES.get(name, _NOTES["click"])

    def _run():
        for freq, dur in seq:
            try:
                winsound.Beep(int(freq), int(dur))
            except Exception:
                break

    threading.Thread(target=_run, daemon=True).start()