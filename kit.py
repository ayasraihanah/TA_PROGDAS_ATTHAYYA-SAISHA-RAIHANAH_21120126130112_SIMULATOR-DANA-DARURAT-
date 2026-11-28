# -*- coding: utf-8 -*-
"""kit.py - Palet minimalis pastel, helper ter-cache, partikel ringan, dan base Screen."""
import math
import random
from functools import lru_cache

# Palet Minimalis Pastel (bersih, kontras nyaman, rendah beban render)
INK = "#2b2d42"
CREAM = "#ffffff"
PINK = "#f6d6e5"
HOT = "#e06d9f"
ROSE = "#eba8c5"
LILAC = "#e4def8"
GRAPE = "#8b7ec8"
SKY = "#d8eefb"
BLUE = "#7bb8e8"
MINT = "#d2f3e5"
GREEN = "#5ec492"
LEAF = "#46a878"
YELLOW = "#fdf0c2"
GOLD = "#e9be56"
ORANGE = "#f5cfa8"
RED = "#f3a6b2"
TEAL = "#7ac7c4"
WHITE = "#ffffff"
GRAY = "#e6e8f0"
DIRT = "#c8b6a6"
DIRT_D = "#9f8c7a"


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


def lighten(hex_color, amt=0.25):
    return mix(hex_color, WHITE, amt)


def darken(hex_color, amt=0.25):
    return mix(hex_color, INK, amt)


@lru_cache(maxsize=16)
def _unit_circle(steps):
    return tuple((math.cos(i * math.tau / steps), math.sin(i * math.tau / steps)) for i in range(steps))


def ell(cx, cy, rx, ry, steps=12):
    steps = max(8, min(14, int(steps)))
    return [(cx + ux * rx, cy + uy * ry) for ux, uy in _unit_circle(steps)]


def rupiah(n):
    return "Rp " + f"{int(n):,}".replace(",", ".")


class Particles:
    """Efek partikel minimalis (maksimal 16 titik agar selalu ringan)."""
    MAX_ITEMS = 16

    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def spawn(self, x, y, kind="spark", colors=None, count=6,
              vx_range=180, vy_up=140, gravity=420, life=0.6, size=7):
        cols = colors or [HOT, BLUE, GREEN]
        room = max(0, self.MAX_ITEMS - len(self.items))
        for _ in range(min(count, room)):
            self.items.append({
                "x": float(x),
                "y": float(y),
                "vx": random.uniform(-vx_range, vx_range),
                "vy": random.uniform(-vy_up * 1.2, -vy_up * 0.3),
                "g": float(gravity),
                "life": random.uniform(life * 0.75, life),
                "max_life": float(life),
                "col": random.choice(cols),
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
            k = max(0.2, p["life"] / max(0.01, p["max_life"]))
            sz = max(2.5, p["size"] * k)
            P.oval(p["x"], p["y"], sz, sz, fill=p["col"], outline="", width=0, tags="dyn")


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

    def button(self, x, y, w, h, label, color, cb, size=18):
        hov = self.hover(x, y, w, h)
        fill = darken(color, 0.07) if hov else color
        self.P.rect(x, y, w, h, fill=fill, outline=INK, width=2, tags="dyn")
        if label:
            self.P.text(x + w / 2, y + h / 2, label, size, INK, tags="dyn")
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