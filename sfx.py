# -*- coding: utf-8 -*-
"""sfx.py - Efek suara retro 8-bit ringan dengan 1 worker thread (tanpa thread spam)."""
import queue
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

_AUDIO_Q = queue.Queue(maxsize=4)


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


def toggle():
    global MUTE
    MUTE = not MUTE


def play(name="click"):
    if MUTE or winsound is None:
        return
    seq = _NOTES.get(name, _NOTES["click"])
    # Buang antrean lama jika klik terlalu cepat agar suara tidak menumpuk
    while not _AUDIO_Q.empty():
        try:
            _AUDIO_Q.get_nowait()
        except queue.Empty:
            break
    try:
        _AUDIO_Q.put_nowait(seq)
    except queue.Full:
        pass