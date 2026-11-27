# -*- coding: utf-8 -*-
"""
art.py - Semua gambar vektor SaveQuest: karakter chibi yang bisa dikustom,
5 jenis boss, karakter boss chibi Y2K, pemandangan, botol potion, balon bicara.
Gaya: tepi tinta tebal, warna flat pastel, mata besar ala ilustrasi Y2K.
Semua karakter & monster ini ORIGINAL (bukan tiruan karakter yang sudah ada).
"""
import math
import random

from kit import (INK, CREAM, PINK, HOT, ROSE, LILAC, GRAPE, SKY, BLUE, MINT, GREEN, LEAF, YELLOW, GOLD,
                 ORANGE, RED, TEAL, WHITE, GRAY, DIRT, DIRT_D, mix, lighten, darken, ell)

# ------------------------------------------------------------------ opsi karakter
OPT = {
    "kelas": ["Star Mage", "Siren Bard", "Riot Rogue", "Fire Knight"],
    "rambut": ["Lurus Panjang", "Twin Tail", "Cepol Dua", "Bob Poni", "Jabrik"],
    "warna_rambut": [("Hitam", "#2a2230"), ("Putih Perak", "#f4f0ff"), ("Oranye Api", "#f0703c"),
                     ("Biru Es", "#9fd6d9"), ("Cokelat", "#7a4a32"), ("Pirang", "#f2cf72"),
                     ("Ungu", "#8d6fd6"), ("Pink", "#ff8fc0")],
    "kulit": [("Terang", "#ffdcc0"), ("Peach", "#f5bd96"), ("Sawo", "#d99a6c"),
              ("Cokelat", "#b87449"), ("Gelap", "#8a5233")],
    "mata": [("Hijau", "#8cc63f"), ("Cokelat", "#7a4a2a"), ("Biru", "#4aa8ff"),
             ("Ungu", "#a070ff"), ("Abu", "#9aa0a6"), ("Pink", "#ff6fae")],
    "baju": ["Jubah Bintang", "Hoodie Besar", "Jaket Punk", "Gaun Mini"],
    "warna_baju": [("Biru Langit", "#7fc8e8"), ("Zaitun", "#a3a24a"), ("Hitam", "#2e2a38"),
                   ("Merah", "#d8404a"), ("Pink", "#ff8fc0"), ("Ungu", "#9b7ae0"), ("Krem", "#f3e3b8")],
    "sepatu": ["Boots Putih", "Boots Hitam", "Sneakers Merah"],
    "aksesori": ["Tidak ada", "Headphone", "Kacamata", "Jepit Bintang", "Rantai Perak"],
}
ROWS = [("kelas", "KELAS"), ("rambut", "GAYA RAMBUT"), ("warna_rambut", "WARNA RAMBUT"), ("kulit", "KULIT"),
        ("mata", "MATA"), ("baju", "BAJU"), ("warna_baju", "WARNA BAJU"), ("sepatu", "SEPATU"),
        ("aksesori", "AKSESORI")]
DEFAULT_IDX = {"kelas": 0, "rambut": 0, "warna_rambut": 1, "kulit": 1, "mata": 2, "baju": 0,
               "warna_baju": 0, "sepatu": 0, "aksesori": 3}

CLASSES = {
    "Star Mage": dict(atk="Spark Slash", spell="Comet Cascade", say=["TWINKLE", "SPARKLE", "WISH!"], col="#ffd86b"),
    "Siren Bard": dict(atk="Wave Chorus", spell="Tide Echo", say=["ECHO", "ENCORE!", "LA LA~"], col="#7fd8ff"),
    "Riot Rogue": dict(atk="Budget Stab", spell="Midnight Dash", say=["SNEAKY", "NO CAP", "SLAY?"], col="#c9a8ff"),
    "Fire Knight": dict(atk="Ember Strike", spell="Phoenix Blaze", say=["BLAZE", "HOT HOT!", "BURN!"], col="#ff8a55"),
}


def opt(char, key):
    lst = OPT[key]
    i = int(char.get(key, DEFAULT_IDX[key])) % len(lst)
    v = lst[i]
    return v if isinstance(v, tuple) else (v, v)


def cycle(char, key, d):
    char[key] = (int(char.get(key, DEFAULT_IDX[key])) + d) % len(OPT[key])


def random_char():
    return {k: random.randrange(len(OPT[k])) for k in OPT}


def cls_info(char):
    return CLASSES[opt(char, "kelas")[0]]


# ------------------------------------------------------------------ konteks gambar karakter
class Ctx:
    """Satuan u = tinggi/100. y negatif = ke atas. T() memutar ke koordinat layar."""

    def __init__(self, P, cx, gy, h, char, face=1, lean=0.0, dy=0.0, tint=None, tags="dyn"):
        self.P, self.cx, self.gy, self.u = P, cx, gy, h / 100.0
        self.face, self.lean, self.dy, self.tint, self.tags = face, lean, dy, tint, tags
        self.ow = max(2.0, self.u * 1.05)
        self.skin = opt(char, "kulit")[1]
        self.hair = opt(char, "warna_rambut")[1]
        self.eye = opt(char, "mata")[1]
        self.hs = opt(char, "rambut")[0]
        self.cloth = opt(char, "baju")[0]
        self.col = opt(char, "warna_baju")[1]
        self.boot = opt(char, "sepatu")[0]
        self.acc = opt(char, "aksesori")[0]

    def T(self, x, y):
        yy = y + self.dy
        return (self.cx + (x * self.face + self.lean * 10 * (-yy) / 100.0) * self.u, self.gy + yy * self.u)

    def K(self, c):
        if not c:
            return c
        if self.tint == "white":
            return WHITE
        return mix(c, self.tint, 0.55) if self.tint else c

    def fp(self, pts, fill, smooth=False):
        self.P.poly([self.T(x, y) for x, y in pts], self.K(fill), INK, self.ow, self.tags, smooth)

    def uni(self, shapes, fill):
        self.P.union([([self.T(x, y) for x, y in pts], sm) for pts, sm in shapes], self.K(fill), self.ow, self.tags)

    def ov(self, x, y, rx, ry, fill, line=True, lc=INK, lw=None):
        cx, cy = self.T(x, y)
        w = (self.ow * 0.8 if lw is None else lw) if line else 0
        self.P.oval(cx, cy, rx * self.u, ry * self.u, self.K(fill) if fill else "", lc if line else "", w, self.tags)

    def ln(self, pts, color, w, smooth=False, dash=None):
        self.P.line([self.T(x, y) for x, y in pts], color if color == INK else self.K(color),
                    max(1.5, w * self.u), self.tags, smooth, dash)

    def limb(self, pts, color, w, smooth=False):
        self.P.limb([self.T(x, y) for x, y in pts], self.K(color), w * self.u, self.ow, self.tags, smooth)

    def star(self, x, y, r, fill=YELLOW):
        cx, cy = self.T(x, y)
        self.P.star(cx, cy, r * self.u, self.K(fill), INK, self.ow * 0.7, self.tags)


# ------------------------------------------------------------------ lapisan karakter
def _back(c, portrait=False):
    h, hair = c.hs, c.hair
    if c.cloth == "Jubah Bintang" and not portrait:
        cape = [(-13, -55), (13, -55), (23, -32), (31, -10), (23, -13), (17, -5), (9, -12), (0, -4),
                (-9, -12), (-17, -5), (-23, -13), (-31, -10), (-23, -32)]
        c.uni([(cape, False)], c.col)
        for x, y in ((-19, -28), (19, -25), (-9, -14), (10, -16), (0, -40)):
            c.star(x, y, 3.4)
    if h == "Lurus Panjang":
        c.uni([([(-21, -82), (-25, -62), (-24, -40), (-12, -34), (12, -34), (24, -40), (25, -62), (21, -82)], True)], hair)
    elif h == "Bob Poni":
        c.uni([([(-22, -82), (-26, -68), (-22, -56), (0, -52), (22, -56), (26, -68), (22, -82)], True)], hair)
    elif h == "Cepol Dua":
        c.uni([([(-21, -80), (-24, -66), (-19, -58), (0, -55), (19, -58), (24, -66), (21, -80)], True)], hair)
    elif h == "Twin Tail":
        for s in (-1, 1):
            c.uni([([(s * 14, -92), (s * 27, -86), (s * 36, -62), (s * 31, -42), (s * 26, -60), (s * 20, -78)], True)], hair)
    elif h == "Jabrik":
        c.uni([([(-21, -80), (-26, -66), (-22, -58), (0, -56), (22, -58), (26, -66), (21, -80)], True)], hair)


def _legs(c):
    for sx in (-6.2, 6.2):
        c.limb([(sx, -42), (sx, -16)], c.skin, 5.2)
    tall = c.boot != "Sneakers Merah"
    bc = {"Boots Putih": "#fbf7ff", "Boots Hitam": "#2d2833", "Sneakers Merah": "#e8434f"}[c.boot]
    sole = {"Boots Putih": "#f5e49a", "Boots Hitam": "#7a6a8c", "Sneakers Merah": "#ffffff"}[c.boot]
    top = -28 if tall else -13
    for sx in (-6.4, 6.4):
        c.fp([(sx - 6, top), (sx + 6, top), (sx + 6.4, -5), (sx + 9.5, -3), (sx + 9.5, 1.2), (sx - 7, 1.2), (sx - 7, -5)], bc)
        c.fp([(sx - 7, -3.2), (sx + 9.5, -3.2), (sx + 9.5, 1.2), (sx - 7, 1.2)], sole)
        if tall:
            c.ln([(sx - 5, top + 3), (sx + 5, top + 3)], darken(bc, 0.15) if bc != "#2d2833" else "#6a5c7a", 0.9)


def _outfit(c):
    col, cl = c.col, c.cloth
    if cl == "Jubah Bintang":
        c.fp([(-10, -44), (10, -44), (16, -30), (12, -34), (8, -29), (4, -34), (0, -29), (-4, -34),
              (-8, -29), (-12, -34), (-16, -30)], "#ffe58a")
        c.fp([(-9, -56), (9, -56), (10, -43), (-10, -43)], col)
        c.ln([(-10, -43), (-3, -41), (3, -41), (10, -43)], "#dfe6ee", 1.1, True, (3, 2))
    elif cl == "Hoodie Besar":
        c.uni([(ell(0, -56, 13, 5, 14), True)], darken(col, 0.12))
        c.uni([([(-13, -57), (13, -57), (17, -29), (-17, -29)], True)], col)
        c.ln([(-8, -38), (8, -38)], darken(col, 0.3), 1.0)
        c.ln([(-3, -55), (-3.5, -46)], WHITE, 0.9)
        c.ln([(3, -55), (3.5, -46)], WHITE, 0.9)
    elif cl == "Jaket Punk":
        c.fp([(-11, -43), (11, -43), (16, -30), (-16, -30)], "#3a3444")
        c.ln([(-12, -37), (12, -37)], "#5b5470", 0.9)
        c.fp([(-9, -56), (9, -56), (11, -42), (-11, -42)], col)
        c.ln([(-11, -42), (11, -42)], "#d8d8e0", 1.5)
        c.ln([(0, -56), (0, -42)], "#d8d8e0", 0.8)
        c.fp([(-1.8, -43.2), (1.8, -43.2), (1.8, -40.8), (-1.8, -40.8)], "#e8e8f0")
    else:  # Gaun Mini
        c.fp([(-9, -56), (9, -56), (10, -46), (19, -29), (-19, -29), (-10, -46)], col)
        for x, y in ((-9, -34), (8, -36), (0, -40)):
            c.star(x, y, 2.6, WHITE)
        bow = lighten(col, 0.55)
        c.fp([(0, -55), (-7, -59), (-7, -51)], bow)
        c.fp([(0, -55), (7, -59), (7, -51)], bow)
        c.ov(0, -55, 2.2, 2.2, bow)


def _arms(c, p):
    sleeve = c.col if c.cloth in ("Hoodie Besar", "Jaket Punk") else None
    for sx, hand in ((-11, p["al"]), (11, p["ar"])):
        sy = -52
        c.limb([(sx, sy), hand], c.skin, 3.6)
        if sleeve:
            c.limb([(sx, sy), (sx + (hand[0] - sx) * 0.78, sy + (hand[1] - sy) * 0.78)], sleeve, 5.4)
        c.ov(hand[0], hand[1], 2.7, 2.7, c.skin)


def _head(c, expr, blink):
    sk = c.skin
    for s in (-1, 1):
        c.fp([(s * 18, -77), (s * 28, -81), (s * 20, -67)], sk)
        c.ov(s * 21.5, -68.5, 1.6, 1.6, GOLD)
    c.uni([(ell(0, -72, 19.5, 17, 24), True)], sk)
    pink = mix(sk, "#ff5f8a", 0.45)
    for s in (-1, 1):
        c.ov(s * 12.5, -63, 3.4, 2.1, pink, line=False)
    for s in (-1, 1):
        ex, ey = s * 8.4, -69.5
        if expr == "hurt":
            c.ln([(ex + s * 3.5, ey - 3.5), (ex - s * 3.5, ey), (ex + s * 3.5, ey + 3.5)], INK, 1.3)
        elif expr == "happy":
            c.ln([(ex - 4.6, ey + 1.5), (ex - 2.4, ey - 2.6), (ex + 2.4, ey - 2.6), (ex + 4.6, ey + 1.5)], INK, 1.4, True)
        elif blink:
            c.ln([(ex - 4.6, ey), (ex + 4.6, ey)], INK, 1.4)
        else:
            c.ov(ex, ey, 5.5, 6.3, WHITE)
            c.ov(ex + s * -0.2, ey + 0.4, 4.3, 5.3, c.eye, line=False)
            c.ov(ex, ey + 0.6, 2.3, 3.1, INK, line=False)
            c.ov(ex - 1.5, ey - 2.0, 1.4, 1.4, WHITE, line=False)
            c.ov(ex + 1.6, ey + 2.4, 0.8, 0.8, WHITE, line=False)
            c.ln([(ex - 6, ey - 4), (ex - 1, ey - 6.9), (ex + 6.2, ey - 5)], INK, 1.3, True)
        if expr == "angry":
            c.ln([(ex + s * 6.5, -78.5), (ex - s * 5, -74.5)], INK, 1.7)
    c.ov(0, -64.2, 0.8, 0.8, darken(sk, 0.25), line=False)
    if expr == "happy":
        c.ln([(-3.2, -61.5), (0, -58.2), (3.2, -61.5)], INK, 1.2, True)
        c.ov(0, -59.6, 1.8, 1.0, "#e0507a", line=False)
    elif expr == "angry":
        c.ln([(-2.6, -60), (2.6, -60.6)], INK, 1.2)
    elif expr == "hurt":
        c.ln([(-3, -60), (-1.5, -61.6), (0, -60), (1.5, -61.6), (3, -60)], INK, 1.1)
    else:
        c.ov(0, -60.4, 1.7, 2.1, "#7a2f4a")


def _front(c):
    h, hair = c.hs, c.hair
    cap = [(-21, -77), (-23, -86), (-15, -95), (0, -98), (15, -95), (23, -86), (21, -77)]
    blunt = [(21, -78), (20, -77), (14, -76), (7, -77.5), (0, -76.5), (-7, -77.5), (-14, -76), (-20, -77), (-21, -78)]
    jag = [(21, -78), (16, -73), (11, -79), (5, -72.5), (-1, -80), (-7, -72.5), (-13, -79), (-18, -73), (-21, -78)]
    if h == "Cepol Dua":
        for s in (-1, 1):
            c.uni([(ell(s * 14, -101, 8.5, 8.5, 16), True)], hair)
            c.ov(s * 13, -95, 2.6, 2.6, HOT)
    if h == "Jabrik":
        spikes = [(-22, -76), (-26, -92), (-17, -86), (-15, -102), (-8, -92), (-3, -105), (3, -94), (10, -104),
                  (13, -92), (21, -100), (21, -84), (24, -76)]
        c.uni([(spikes, False), (jag, False)], hair)
    else:
        c.uni([(cap, True), (blunt if h in ("Lurus Panjang", "Bob Poni") else jag, False)], hair)
    if h == "Lurus Panjang":
        for s in (-1, 1):
            c.uni([([(s * 18, -80), (s * 24, -70), (s * 24, -46), (s * 20, -48), (s * 17, -70)], True)], hair)
    elif h == "Bob Poni":
        for s in (-1, 1):
            c.uni([([(s * 18, -80), (s * 24, -70), (s * 24, -58), (s * 19, -60), (s * 17, -70)], True)], hair)
    elif h == "Twin Tail":
        for s in (-1, 1):
            c.ov(s * 18, -87, 2.8, 2.8, HOT)
    c.ln([(-13, -92), (-5, -95.5)], lighten(hair, 0.5), 1.5, True)


def _acc(c, portrait=False):
    a = c.acc
    if a == "Headphone":
        c.limb([(-22, -76), (-20, -96), (0, -102), (20, -96), (22, -76)], "#4a4458", 2.2, True)
        for s in (-1, 1):
            c.uni([(ell(s * 23, -72, 4.8, 7.5, 14), True)], "#6a6478")
            c.ov(s * 23.6, -72, 2, 4.2, "#b6aec9", line=False)
    elif a == "Kacamata":
        for s in (-1, 1):
            c.ov(s * 8.4, -69.5, 7.2, 7.8, "", True, "#d8404a", c.ow * 0.9)
        c.ln([(-1.6, -70.5), (1.6, -70.5)], "#d8404a", 1.0)
    elif a == "Jepit Bintang":
        c.star(13, -88, 5.2)
        c.star(8, -92, 2.8, HOT)
    elif a == "Rantai Perak" and not portrait:
        c.ln([(-9, -55), (-6, -51), (-2, -49), (2, -49), (6, -51), (9, -55)], "#dfe6ee", 1.2, True, (3, 2))
        c.ov(0, -47, 1.8, 1.8, "#dfe6ee")


def _pose(name, t):
    sw = math.sin(t * 3)
    p = dict(dy=0.0, lean=0.0, al=(-15, -39), ar=(15, -39), expr="idle")
    if name == "idle":
        p.update(dy=math.sin(t * 2.6) * 0.8, al=(-15, -39 + sw * 0.8), ar=(15, -39 - sw * 0.8))
    elif name == "walk":
        s = math.sin(t * 12)
        p.update(dy=-abs(s) * 1.8, lean=0.08, al=(-13, -40 + s * 4), ar=(13, -40 - s * 4))
    elif name == "attack":
        p.update(lean=0.35, ar=(35, -60), al=(-12, -46), expr="angry")
    elif name == "cheer":
        p.update(dy=-abs(math.sin(t * 8)) * 3, al=(-23, -88), ar=(23, -88), expr="happy")
    elif name == "hurt":
        p.update(lean=-0.3, al=(-21, -52), ar=(21, -46), expr="hurt")
    elif name == "jump":
        p.update(al=(-21, -72), ar=(21, -72), expr="happy")
    return p


def draw_chibi(P, cx, gy, h, char, t=0.0, pose="idle", face=1, tint=None, tags="dyn", shadow=True):
    """Gambar karakter lengkap. gy = garis tanah, h = tinggi."""
    p = _pose(pose, t)
    c = Ctx(P, cx, gy, h, char, face, p["lean"], p["dy"], tint, tags)
    if shadow:
        P.oval(cx, gy, 20 * c.u, 3.6 * c.u, "#000000", "", 0, tags, stipple="gray50")
    _back(c)
    _legs(c)
    _outfit(c)
    _arms(c, p)
    _head(c, p["expr"], (t % 4.0) < 0.13)
    _front(c)
    _acc(c)
    return c


def draw_portrait(P, cx, cy, r, char, expr="idle", tags="dyn"):
    """Hanya kepala (untuk bingkai HUD)."""
    u = r / 21.0
    c = Ctx(P, cx, cy + 72 * u, 100 * u, char, 1, 0, 0, None, tags)
    _back(c, True)
    _head(c, expr, False)
    _front(c)
    _acc(c, True)


# ------------------------------------------------------------------ boss
class B:
    def __init__(self, P, cx, gy, h, tier, t=0.0, flash=False, hurt=False, tags="dyn"):
        self.P, self.cx, self.gy, self.u = P, cx, gy, h / 100.0
        self.t, self.flash, self.hurt, self.tags = t, flash, hurt, tags
        self.col = tier["col"]
        self.ow = max(2.0, self.u * 1.1)
        self.sy = 1 + 0.035 * math.sin(t * 3)
        self.dy = -abs(math.sin(t * 1.6)) * 1.4

    def T(self, x, y):
        return (self.cx + x * self.u, self.gy + (y * self.sy + self.dy) * self.u)

    def K(self, c):
        return WHITE if self.flash and c != INK else c

    def fp(self, pts, fill, smooth=False):
        self.P.poly([self.T(x, y) for x, y in pts], self.K(fill), INK, self.ow, self.tags, smooth)

    def uni(self, shapes, fill):
        self.P.union([([self.T(x, y) for x, y in pts], sm) for pts, sm in shapes], self.K(fill), self.ow, self.tags)

    def ov(self, x, y, rx, ry, fill, line=True):
        cx, cy = self.T(x, y)
        self.P.oval(cx, cy, rx * self.u, ry * self.u, self.K(fill), INK if line else "", self.ow * 0.8 if line else 0, self.tags)

    def ln(self, pts, color, w, smooth=False):
        self.P.line([self.T(x, y) for x, y in pts], color if color == INK else self.K(color), max(1.5, w * self.u), self.tags, smooth)

    def limb(self, pts, color, w, smooth=False):
        self.P.limb([self.T(x, y) for x, y in pts], self.K(color), w * self.u, self.ow, self.tags, smooth)

    def star(self, x, y, r, fill=YELLOW):
        cx, cy = self.T(x, y)
        self.P.star(cx, cy, r * self.u, self.K(fill), INK, self.ow * 0.7, self.tags)

    def eye(self, x, y, r, col=WHITE, iris=INK):
        if self.hurt:
            self.ln([(x - r * .6, y - r * .6), (x + r * .6, y + r * .6)], INK, 1.5)
            self.ln([(x - r * .6, y + r * .6), (x + r * .6, y - r * .6)], INK, 1.5)
            return
        self.ov(x, y, r, r * 1.08, col)
        self.ov(x + r * 0.1, y + r * 0.1, r * 0.55, r * 0.64, iris, line=False)
        self.ov(x - r * 0.15, y - r * 0.28, r * 0.22, r * 0.22, WHITE, line=False)


def _slime(b):
    c = b.col
    body = [(-36, 2), (-40, -14), (-32, -40), (-16, -58), (0, -62), (16, -58), (32, -40), (40, -14), (36, 2),
            (24, 5), (12, 0), (0, 5), (-12, 0), (-24, 5)]
    b.ln([(0, -62), (3, -73)], INK, 1.3)
    b.ov(4, -75, 5.5, 4, "#9be26b")
    b.uni([(body, True)], c)
    b.ln([(-26, -40), (-19, -52)], lighten(c, 0.65), 3.2)
    for x, y, r in ((24, -42, 2.4), (30, -30, 1.6), (-30, -12, 2)):
        b.ov(x, y, r, r, lighten(c, 0.5), line=False)
    b.eye(-13, -30, 8.5)
    b.eye(13, -30, 8.5)
    b.ov(-24, -17, 4.2, 2.6, mix(c, "#ff6f9a", 0.55), line=False)
    b.ov(24, -17, 4.2, 2.6, mix(c, "#ff6f9a", 0.55), line=False)
    b.ln([(-5, -17), (0, -13), (5, -17)], INK, 1.3, True)


def _gremlin(b):
    c = b.col
    for s in (-1, 1):
        b.uni([([(s * 20, -50), (s * 46, -74), (s * 52, -48), (s * 43, -52), (s * 41, -34), (s * 33, -40), (s * 25, -26)], False)], darken(c, 0.15))
    for s in (-1, 1):
        b.fp([(s * 13, -58), (s * 31, -94), (s * 27, -54)], c)
        b.fp([(s * 17, -62), (s * 27, -84), (s * 24, -60)], "#ffb3d6")
    b.uni([(ell(0, -34, 27, 30, 22), True)], c)
    b.ov(0, -24, 15, 15, lighten(c, 0.55), line=False)
    for s in (-1, 1):
        b.ov(s * 13, -2, 9.5, 5, darken(c, 0.1))
    b.fp([(2, -34), (-5, -22), (0, -22), (-3, -12), (7, -26), (2, -26)], YELLOW)
    b.eye(-11, -46, 8, "#fff7b0")
    b.eye(11, -46, 8, "#fff7b0")
    b.fp(ell(0, -33, 9, 4.6, 14), "#5a1f46")
    b.fp([(-6, -36), (-4, -31), (-2, -36)], WHITE)
    b.fp([(2, -36), (4, -31), (6, -36)], WHITE)


def _golem(b):
    c = b.col
    for s in (-1, 1):
        b.uni([([(s * 8, -26), (s * 24, -26), (s * 24, 1), (s * 8, 1)], False)], darken(c, 0.1))
    for s in (-1, 1):
        b.uni([([(s * 32, -66), (s * 48, -62), (s * 54, -32), (s * 38, -28)], False), (ell(s * 49, -22, 12.5, 12, 14), True)], darken(c, 0.06))
    b.uni([([(-31, -66), (31, -66), (37, -24), (-37, -24)], False)], c)
    b.uni([([(-22, -98), (22, -98), (27, -62), (-27, -62)], False)], lighten(c, 0.12))
    b.ln([(-30, -60), (-22, -52), (-26, -44), (-18, -36)], darken(c, 0.35), 1.2)
    b.ln([(28, -58), (21, -48), (26, -40)], darken(c, 0.35), 1.2)
    for x, y, r in ((-14, -99, 6), (-4, -100, 5), (12, -99, 6)):
        b.ov(x, y, r, r * 0.7, "#7dd36b")
    b.ov(0, -46, 13.5, 13.5, darken(c, 0.4))
    b.star(0, -46, 10, YELLOW)
    for s in (-1, 1):
        b.fp([(s * 15, -84), (s * 6, -84), (s * 6, -77), (s * 15, -77)], "#aef3ff")
    b.ln([(-8, -69), (-3, -66), (3, -66), (8, -69)], INK, 1.3)


def _demon(b):
    c = b.col
    for s in (-1, 1):
        b.uni([([(s * 16, -56), (s * 44, -88), (s * 58, -68), (s * 50, -60), (s * 54, -42), (s * 40, -48), (s * 30, -30), (s * 22, -46)], False)], darken(c, 0.28))
    b.limb([(24, -8), (44, -4), (54, -22), (48, -34)], darken(c, 0.12), 2.6, True)
    b.fp([(48, -34), (42, -44), (54, -42)], HOT if c != HOT else YELLOW)
    b.uni([(ell(0, -38, 26, 34, 24), True)], c)
    for s in (-1, 1):
        b.uni([([(s * 12, -68), (s * 21, -98), (s * 27, -92), (s * 23, -66)], False)], "#ffe9a8")
        b.ov(s * 13, -2, 10, 5, darken(c, 0.1))
    b.eye(-11, -50, 8, "#fff3a0", "#c4204f")
    b.eye(11, -50, 8, "#fff3a0", "#c4204f")
    b.ov(0, -62, 3.2, 3.2, "#fff3a0")
    b.fp([(-15, -33), (-8, -24), (0, -22), (8, -24), (15, -33), (0, -30)], "#5a1038")
    for x in (-9, -2, 5):
        b.fp([(x, -31), (x + 3.5, -31), (x + 1.8, -26.5)], WHITE)
    b.star(0, -12, 5, YELLOW)


def _dragon(b):
    c = b.col
    wing = mix(c, "#7a4aa0", 0.45)
    for s in (-1, 1):
        b.uni([([(s * 20, -62), (s * 52, -102), (s * 72, -82), (s * 63, -66), (s * 74, -48), (s * 55, -52), (s * 47, -34), (s * 30, -44)], False)], wing)
        b.star(s * 50, -66, 5.5, YELLOW)
    b.limb([(24, -12), (48, -6), (62, -24), (57, -42)], c, 7, True)
    b.fp([(57, -42), (50, -52), (64, -50)], YELLOW)
    b.uni([(ell(0, -36, 31, 35, 26), True)], c)
    b.ov(0, -24, 19, 22, "#ffe6a0", line=False)
    for y in (-34, -26, -18):
        b.ln([(-12, y), (0, y + 3), (12, y)], "#e8b45a", 1.2, True)
    for x in (-14, 0, 14):
        b.fp([(x - 6, -68), (x, -90 if x == 0 else -84), (x + 6, -68)], YELLOW)
    for s in (-1, 1):
        b.fp([(s * 22, -62), (s * 40, -78), (s * 34, -54)], darken(c, 0.12))
        b.ov(s * 14, -2, 11, 5.5, darken(c, 0.1))
    b.ov(0, -42, 15, 11, lighten(c, 0.25))
    b.eye(-13, -54, 8.5, WHITE, "#2a8a4a")
    b.eye(13, -54, 8.5, WHITE, "#2a8a4a")
    b.ov(-5, -42, 1.6, 2.2, INK, line=False)
    b.ov(5, -42, 1.6, 2.2, INK, line=False)
    b.ln([(-9, -35), (0, -31), (9, -35)], INK, 1.3, True)
    b.fp([(-5, -33.5), (-3.5, -29), (-2, -33)], WHITE)
    b.fp([(2, -33), (3.5, -29), (5, -33.5)], WHITE)


_BOSSES = {"slime": _slime, "gremlin": _gremlin, "golem": _golem, "demon": _demon, "dragon": _dragon}


def draw_boss(P, cx, gy, h, tier, t=0.0, flash=False, hurt=False, tags="dyn", shadow=True):
    b = B(P, cx, gy, h, tier, t, flash, hurt, tags)
    if shadow:
        P.oval(cx, gy, 34 * b.u, 4.5 * b.u, "#000000", "", 0, tags, stipple="gray50")
    _BOSSES[tier["key"]](b)
    return b


# ------------------------------------------------------------------ boss karakter (art style chibi Y2K)
BOSS_TIERS = [
    dict(key="slime", label="Wishlist Imp", col="#7ad7ff", min_harga=0),
    dict(key="gremlin", label="Impulse Gremlin", col="#ff8fc0", min_harga=300_000),
    dict(key="golem", label="Budget Golem", col="#9fe3b4", min_harga=1_000_000),
    dict(key="demon", label="Splurge Demon", col="#c9a8ff", min_harga=3_000_000),
    dict(key="dragon", label="Luxury Dragon", col="#ffd86b", min_harga=8_000_000),
]

BOSS_PRESETS = {
    "slime": dict(kelas=1, rambut=1, warna_rambut=3, kulit=0, mata=2, baju=3, warna_baju=0, sepatu=0, aksesori=0),
    "gremlin": dict(kelas=2, rambut=4, warna_rambut=7, kulit=1, mata=5, baju=2, warna_baju=4, sepatu=2, aksesori=0),
    "golem": dict(kelas=3, rambut=3, warna_rambut=4, kulit=2, mata=0, baju=1, warna_baju=1, sepatu=1, aksesori=0),
    "demon": dict(kelas=2, rambut=0, warna_rambut=6, kulit=0, mata=3, baju=2, warna_baju=2, sepatu=1, aksesori=4),
    "dragon": dict(kelas=3, rambut=2, warna_rambut=2, kulit=1, mata=0, baju=0, warna_baju=3, sepatu=1, aksesori=0),
}


def boss_tier_for_price(harga):
    chosen = BOSS_TIERS[0]
    for tier in BOSS_TIERS:
        if harga >= tier["min_harga"]:
            chosen = tier
    return chosen


def draw_boss_chibi(P, cx, gy, h, harga=0, t=0.0, pose="idle", flash=False, tags="dyn"):
    """Karakter Boss bergaya chibi Y2K (tepi tinta tebal, mata besar, tanduk/sayap/mahkota)."""
    tier = boss_tier_for_price(harga)
    key = tier["key"]
    cfg = BOSS_PRESETS[key]
    p = _pose(pose, t)
    tint = "white" if flash else None
    c = Ctx(P, cx, gy, h, cfg, -1, p["lean"], p["dy"], tint, tags)

    # Sayap belakang untuk Demon & Dragon
    if key in ("demon", "dragon"):
        wcol = "#7a4aa0" if key == "demon" else "#ff8a55"
        for s in (-1, 1):
            c.uni([([(s * 10, -54), (s * 34, -76), (s * 42, -56), (s * 34, -50),
                     (s * 36, -36), (s * 24, -42), (s * 14, -36)], False)], wcol)

    _back(c)
    _legs(c)
    _outfit(c)
    _arms(c, p)

    expr = "hurt" if pose == "hurt" else "angry"
    _head(c, expr, False)
    _front(c)

    # Atribut kepala khas tiap tier Boss
    if key == "slime":
        c.ln([(0, -96), (4, -108)], INK, 1.4)
        c.ov(6, -110, 6, 4.2, "#9be26b")
    elif key == "gremlin":
        for s in (-1, 1):
            c.fp([(s * 16, -86), (s * 30, -104), (s * 24, -78)], "#ff8fc0")
    elif key == "golem":
        c.fp([(-16, -95), (-10, -106), (-4, -97), (0, -108), (4, -97), (10, -106), (16, -95)], "#9fe3b4")
    elif key == "demon":
        for s in (-1, 1):
            c.fp([(s * 10, -94), (s * 18, -112), (s * 21, -91)], "#ffe9a8")
    elif key == "dragon":
        for s in (-1, 1):
            c.fp([(s * 11, -93), (s * 20, -114), (s * 23, -90)], GOLD)
        c.star(0, -102, 5.5, YELLOW)

    return tier


# ------------------------------------------------------------------ benda & UI kecil
def draw_potion(P, cx, gy, h, ratio, col=HOT, t=0.0, tags="dyn"):
    u = h / 100.0
    X = lambda x: cx + x * u
    Y = lambda y: gy + y * u
    ratio = max(0.0, min(1.0, ratio))
    P.rect(X(-6), Y(-100), 12 * u, 12 * u, "#c98a52", INK, 3, tags, r=3)
    P.rect(X(-9), Y(-90), 18 * u, 18 * u, "#eaf7ff", INK, 3, tags, r=4)
    P.oval(X(0), Y(-34), 34 * u, 34 * u, "#eaf7ff", INK, 3.5, tags)
    ycen, ry, rx = -34, 34, 34
    lvl = ycen + ry - ratio * 2 * ry
    if ratio > 0.01:
        pts = []
        for a in range(0, 361, 10):
            x = rx * math.cos(math.radians(a)) * 0.92
            y = ycen + ry * math.sin(math.radians(a)) * 0.92
            if y >= lvl:
                pts.append((X(x), Y(y)))
        if len(pts) > 2:
            xl, xr = pts[-1][0], pts[0][0]
            for i in range(1, 12):
                f = i / 12.0
                pts.append((xl + (xr - xl) * f, Y(lvl) + math.sin(t * 3 + f * 9) * 1.6 * u))
            P.poly(pts, col, "", 0, tags)
    P.line([(X(-22), Y(-52)), (X(-26), Y(-38))], WHITE, max(2, 3 * u), tags)
    P.oval(X(0), Y(-34), 34 * u, 34 * u, "", INK, 3.5, tags)
    P.heart(X(0), Y(-30), 11 * u, lighten(col, 0.3) if ratio > 0.3 else CREAM, INK, 2, tags)


def draw_speech(P, x, y, text, size=20, fill=CREAM, tags="dyn", tail=1):
    """Balon bicara ala komik. (x, y) = ujung ekor."""
    w = max(70, len(text) * size * 0.62 + 34)
    h = size * 1.9
    P.rect(x - w / 2, y - 14 - h, w, h, fill, INK, 3.5, tags, r=h / 2, sh=4)
    P.poly([(x - 10, y - 16), (x + 10, y - 16), (x + 2 * tail, y)], fill, INK, 3.5, tags)
    P.rect(x - 8, y - 18, 16, 5, fill, "", 0, tags)
    P.text(x, y - 14 - h / 2 + 1, text, size, INK, "center", tags)


# ------------------------------------------------------------------ pemandangan
def cloud(P, cx, cy, s=1.0, tags="dyn"):
    shapes = [(ell(cx - 38 * s, cy + 4 * s, 26 * s, 18 * s, 14), True), (ell(cx, cy - 10 * s, 34 * s, 26 * s, 16), True),
              (ell(cx + 40 * s, cy + 4 * s, 28 * s, 18 * s, 14), True), ([(cx - 60 * s, cy + 14 * s), (cx + 64 * s, cy + 14 * s), (cx + 64 * s, cy + 4 * s), (cx - 60 * s, cy + 4 * s)], False)]
    P.union(shapes, WHITE, 3, tags)


def draw_clouds(P, t, tags="dyn"):
    for i, (y, s, sp, off) in enumerate(((90, 1.1, 14, 0), (170, 0.8, 9, 400), (60, 0.7, 20, 800), (230, 0.9, 11, 1100))):
        x = (off + t * sp) % 1500 - 110
        cloud(P, x, y, s, tags)


def draw_meadow(P, gy=560, sky_top="#74c8ff", sky_bot="#dff6ff", tags="static"):
    """Pemandangan padang pastel: langit, bukit, kastil, pohon, tanah berumput."""
    P.bgfill(sky_top, tags)
    P.vgrad(0, 0, 1280, gy, sky_top, sky_bot, 30, tags)
    P.oval(1130, 110, 52, 52, "#fff3a8", INK, 4, tags)
    for i in range(10):
        a = i * math.pi / 5
        P.line([(1130 + 62 * math.cos(a), 110 + 62 * math.sin(a)), (1130 + 78 * math.cos(a), 110 + 78 * math.sin(a))], INK, 4, tags)
    # bukit jauh
    P.poly([(0, gy), (0, gy - 150), (160, gy - 210), (330, gy - 130), (520, gy - 190), (720, gy - 120), (900, gy - 200),
            (1100, gy - 140), (1280, gy - 190), (1280, gy)], "#9fe3b4", INK, 4, tags, True)
    # kastil
    kx, ky = 980, gy - 118
    P.rect(kx - 70, ky - 30, 140, 100, "#ffd0e6", INK, 4, tags)
    for tx in (kx - 70, kx + 40):
        P.rect(tx - 4, ky - 80, 44, 120, "#ffc0de", INK, 4, tags)
        P.poly([(tx - 10, ky - 78), (tx + 18, ky - 128), (tx + 46, ky - 78)], LILAC, INK, 4, tags)
        P.rect(tx + 10, ky - 52, 16, 22, SKY, INK, 3, tags, r=8)
    P.poly([(kx - 20, ky - 30), (kx, ky - 78), (kx + 20, ky - 30)], LILAC, INK, 4, tags)
    P.line([(kx, ky - 78), (kx, ky - 108)], INK, 4, tags)
    P.poly([(kx, ky - 108), (kx + 26, ky - 98), (kx, ky - 90)], HOT, INK, 3, tags)
    P.rect(kx - 18, ky + 20, 36, 50, "#b5733f", INK, 4, tags, r=16)
    P.star(kx, ky - 4, 11, YELLOW, INK, 3, tags)
    # bukit depan
    P.poly([(0, gy), (0, gy - 70), (200, gy - 120), (420, gy - 60), (640, gy - 105), (860, gy - 55), (1060, gy - 90), (1280, gy - 50), (1280, gy)], "#6fd08a", INK, 4, tags, True)
    # pohon pastel
    for x, s in ((120, 1.0), (330, 0.8), (1180, 1.1)):
        P.rect(x - 8 * s, gy - 90 * s, 16 * s, 90 * s, "#b5733f", INK, 4, tags)
        P.union([(ell(x, gy - 120 * s, 46 * s, 42 * s, 16), True), (ell(x - 26 * s, gy - 98 * s, 28 * s, 24 * s, 12), True),
                 (ell(x + 28 * s, gy - 98 * s, 28 * s, 24 * s, 12), True)], "#58c96b", 4, tags)
        P.sparkle(x - 12 * s, gy - 130 * s, 7 * s, WHITE, INK, 1.5, tags)
    ground(P, gy, tags)


def ground(P, gy=560, tags="static", grass="#58c96b"):
    P.rect(-20, gy, 1320, 720 - gy + 20, DIRT, INK, 4, tags)
    for row, y in enumerate(range(int(gy) + 44, 740, 34)):
        off = 0 if row % 2 == 0 else 38
        for x in range(-40 + off, 1300, 76):
            P.rect(x, y, 70, 28, DIRT if (x // 76 + row) % 3 else mix(DIRT, DIRT_D, 0.35), DIRT_D, 2.5, tags, r=3)
    P.rect(-20, gy - 4, 1320, 34, grass, INK, 4, tags)
    for x in range(-10, 1300, 44):
        P.oval(x, gy + 30, 26, 15, grass, INK, 3.5, tags)
    P.rect(-16, gy - 1, 1312, 10, lighten(grass, 0.45), "", 0, tags)
    rnd = random.Random(5)
    for x in range(30, 1280, 150):
        fx = x + rnd.randint(-30, 30)
        P.line([(fx, gy - 2), (fx, gy - 16)], LEAF, 3, tags)
        P.oval(fx, gy - 20, 7, 7, rnd.choice([PINK, YELLOW, WHITE, LILAC]), INK, 2.5, tags)
        P.oval(fx, gy - 20, 2.6, 2.6, YELLOW, "", 0, tags)


def y2k_bg(P, c1=PINK, c2=LILAC, seed=3, tags="static"):
    """Latar desktop Y2K: gradasi, grid miring, bintang dan sparkle."""
    P.bgfill(c1, tags)
    P.vgrad(0, 0, 1280, 720, c1, c2, 30, tags)
    for i in range(-10, 30):
        x = i * 70
        P.line([(x, 0), (x - 260, 720)], mix(c2, WHITE, 0.25), 2, tags)
    for y in range(40, 720, 70):
        P.line([(0, y), (1280, y)], mix(c1, WHITE, 0.25), 2, tags)
    rnd = random.Random(seed)
    for _ in range(34):
        x, y, r = rnd.randint(10, 1270), rnd.randint(10, 700), rnd.choice((6, 8, 11, 14))
        col = rnd.choice([WHITE, YELLOW, MINT, SKY, CREAM])
        if rnd.random() < 0.6:
            P.sparkle(x, y, r, col, INK, 2, tags)
        else:
            P.star(x, y, r * 0.8, col, INK, 2, tags)


def taskbar(P, tags="static"):
    P.rect(-10, 690, 1300, 40, "#d9c4ff", INK, 4, tags)
    P.rect(8, 695, 118, 26, HOT, INK, 3, tags, r=13)
    P.star(28, 708, 8, YELLOW, INK, 2, tags)
    P.text(80, 708, "START", 17, WHITE, "center", tags)
    for i, (x, col) in enumerate(((150, MINT), (206, SKY), (262, YELLOW))):
        P.rect(x, 695, 46, 26, col, INK, 3, tags, r=8)
        P.sparkle(x + 23, 708, 8, WHITE, INK, 1.8, tags)