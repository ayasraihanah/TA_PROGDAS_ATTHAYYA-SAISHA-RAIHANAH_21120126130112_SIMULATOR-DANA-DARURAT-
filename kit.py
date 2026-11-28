# -*- coding: utf-8 -*-
"""kit.py - Palet warna Y2K, helper gambar/matematika ter-cache, partikel, dan base class Screen."""
import math
import random
from functools import lru_cache

# ----------------------------------------------------------------------
# PALET WARNA Y2K / PIXEL PASTEL
# ----------------------------------------------------------------------
INK = "#1b1429"
CREAM = "#fff7fb"
PINK = "#ff9ed2"
HOT = "#ff4fa3"
ROSE = "#ff7eb6"
LILAC = "#c9a8ff"
GRAPE = "#8a5cf6"
SKY = "#7ad7ff"
BLUE = "#4ea8ff"
MINT = "#6ef2c2"
GREEN = "#4cd97b"
LEAF = "#2eb872"
YELLOW = "#ffe066"
GOLD = "#ffb703"
ORANGE = "#ff9f43"
RED = "#ff5c77"
TEAL = "#2ec4b6"
WHITE = "#ffffff"
GRAY = "#b8b0c8"
DIRT = "#9c6644"
DIRT_D = "#6f452c"


# ----------------------------------------------------------------------
# FUNGSI BANTU WARNA, FORMAT & GEOMETRI (TER-CACHE)
# ----------------------------------------------------------------------
@lru_cache(maxsize=256)
def _hex_to_rgb(hex_color):
    h = (hex_color or "#ffffff").lstrip("#")
    if len(h) != 6:
        return (255, 255, 255)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_to_hex(r, g, b):
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02x}{g:02x}{b:02x}"


@lru_cache(maxsize=512)
def mix(c1, c2, t=0.5):
    t = max(0.0, min(1.0, round(float(t), 3)))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


def lighten(hex_color, amt=0.3):
    return mix(hex_color, WHITE, amt)


def darken(hex_color, amt=0.3):
    return mix(hex_color, INK, amt)


@lru_cache(maxsize=16)
def _unit_circle(steps):
    return tuple((math.cos(i * math.tau / steps), math.sin(i * math.tau / steps)) for i in range(steps))


def ell(cx, cy, rx, ry, steps=16):
    """Menghasilkan daftar titik (x, y) poligon elips menggunakan tabel sin/cos ter-cache."""
    steps = max(8, min(16, int(steps)))
    return [(cx + ux * rx, cy + uy * ry) for ux, uy in _unit_circle(steps)]


def rupiah(n):
    return "Rp " + f"{int(n):,}".replace(",", ".")


# ----------------------------------------------------------------------
# SISTEM PARTIKEL (confetti, spark, star)
# ----------------------------------------------------------------------
class Particles:
    MAX_ITEMS = 48

    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def spawn(self, x, y, kind="spark", colors=None, count=10,
              vx_range=240, vy_up=180, gravity=500, life=0.9, size=9):
        cols = colors or [YELLOW, PINK, MINT, SKY, WHITE]
        room = max(0, self.MAX_ITEMS - len(self.items))
        for _ in range(min(count, room)):
            vx = random.uniform(-vx_range, vx_range)
            vy = random.uniform(-vy_up * 1.3, -vy_up * 0.3)
            self.items.append({
                "x": float(x),
                "y": float(y),
                "vx": vx,
                "vy": vy,
                "g": float(gravity),
                "life": random.uniform(life * 0.7, life * 1.15),
                "max_life": float(life),
                "col": random.choice(cols),
                "kind": kind,
                "size": size,
            })

    def update(self, dt):
        if not self.items:
            return
        alive = []
        for p in self.items:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            p["vy"] += p["g"] * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            alive.append(p)
        self.items = alive

    def draw(self, P):
        for p in self.items:
            k = max(0.1, p["life"] / max(0.01, p["max_life"]))
            sz = max(3, p["size"] * k)
            if p["kind"] == "star":
                P.star(p["x"], p["y"], sz, p["col"], INK, 1.5)
            elif p["kind"] == "confetti":
                P.rect(p["x"] - sz * 0.6, p["y"] - sz * 0.4, sz * 1.2, sz * 0.8, p["col"], INK, 1.5)
            else:
                P.sparkle(p["x"], p["y"], sz, p["col"], INK, 1.5)


# ----------------------------------------------------------------------
# BASE CLASS SCREEN (dipakai TitleScreen, CreatorScreen, HubY2K)
# ----------------------------------------------------------------------
class Screen:
    name = "base"

    def __init__(self, app):
        self.app = app
        self.P = app.P
        self.t = 0.0
        self.hits = []

    def enter(self, **_kw):
        self.t = 0.0
        self.hits = []

    def leave(self):
        """Membersihkan area klik dan partikel saat meninggalkan halaman."""
        self.hits = []
        parts = getattr(self, "parts", None)
        if parts is not None:
            parts.clear()

    def update(self, dt):
        self.t += dt

    def draw_static(self):
        pass

    def draw(self):
        pass

    def hover(self, x, y, w, h):
        mx, my = self.app.mouse
        return x <= mx <= x + w and y <= my <= y + h

    def button(self, x, y, w, h, label, color, cb, size=22):
        hov = self.hover(x, y, w, h)
        pressed = hov and self.app.mouse_down
        yy = y + (3 if pressed else (-3 if hov else 0))
        fill = lighten(color, 0.22) if hov else color
        self.P.rect(x, yy, w, h, fill, INK, 3.5, "dyn", r=h / 2, sh=5)
        if label:
            self.P.text(x + w / 2, yy + h / 2 + 1, label, size, INK)
        self.hits.append((x, y, w, h, cb))
        return hov

    def click(self, x, y):
        for hx, hy, w, h, cb in reversed(self.hits):
            if hx <= x <= hx + w and hy <= y <= hy + h:
                cb()
                return True
        return False

    def on_key(self, _key, _ch):
        return False