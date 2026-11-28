# -*- coding: utf-8 -*-
"""sfx.py - Efek suara 8-bit ringan dengan 1 worker thread."""
import queue
import threading

try:
    import winsound
except ImportError:
    winsound = None

MUTE = False

_NOTES = {
    "click": [(900, 30)],
    "coin": [(988, 50), (1319, 90)],
    "star": [(1047, 45), (1319, 75)],
    "boot": [(659, 55), (880, 95)],
    "lvl": [(587, 60), (784, 60), (1047, 120)],
    "hit": [(220, 65), (165, 85)],
}

_AUDIO_Q = queue.Queue(maxsize=3)


def _audio_worker():
    while True:
        seq = _AUDIO_Q.get()
        if MUTE or winsound is None:
            continue
        for freq, dur in seq:
            if MUTE:
                break
            try:
                winsound.Beep(int(freq), int(dur))
            except Exception:
                break


if winsound is not None:
    threading.Thread(target=_audio_worker, daemon=True).start()


def clear():
    while not _AUDIO_Q.empty():
        try:
            _AUDIO_Q.get_nowait()
        except queue.Empty:
            break


def toggle():
    global MUTE
    MUTE = not MUTE
    if MUTE:
        clear()


def play(name="click"):
    if MUTE or winsound is None:
        return
    seq = _NOTES.get(name, _NOTES["click"])
    clear()
    try:
        _AUDIO_Q.put_nowait(seq)
    except queue.Full:
        pass