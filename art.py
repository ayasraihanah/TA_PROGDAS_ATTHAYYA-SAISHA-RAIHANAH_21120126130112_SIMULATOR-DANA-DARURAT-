# -*- coding: utf-8 -*-
"""art.py - Karakter anime chibi proporsi awal, boss naga/godzilla, potion, dan badge."""
import math
import random

OPT = {
    "kelas": [
        ("Star Mage", "#e4def8"),
        ("Siren Bard", "#d8eefb"),
        ("Riot Rogue", "#d2f3e5"),
        ("Fire Knight", "#f6d6e5"),
    ],
    "rambut": [
        ("Long Wavy", "long"),
        ("Twin Tails", "twins"),
        ("Layered Bob", "bob"),
        ("High Ponytail", "pony"),
    ],
    "warna_rambut": [
        ("Sakura Pink", "#f497b6"),
        ("Sky Blue", "#7bb8e8"),
        ("Butter Gold", "#f6d365"),
        ("Lavender", "#b8a9e6"),
        ("Espresso", "#5c4742"),
    ],
    "kulit": [
        ("Porcelain", "#ffe8dc"),
        ("Warm Ivory", "#fbd5c0"),
        ("Honey Tan", "#e6b08a"),
    ],
    "mata": [
        ("Sparkle", "sparkle"),
        ("Happy Arc", "happy"),
        ("Cool", "calm"),
    ],
    "outfit": [
        ("Magical Skirt", "#f6d6e5"),
        ("Sailor Blazer", "#d8eefb"),
        ("Mint Jacket", "#d2f3e5"),
        ("Lilac Cape", "#e4def8"),
    ],
    "aksesoris": [
        ("Star Clip", "star"),
        ("Cat Ears", "cat"),
        ("Mini Crown", "crown"),
        ("None", "none"),
    ],
}

ROWS = [
    ("kelas", "Kelas"),
    ("rambut", "Gaya Rambut"),
    ("warna_rambut", "Warna Rambut"),
    ("kulit", "Warna Kulit"),
    ("mata", "Ekspresi Mata"),
    ("outfit", "Outfit"),
    ("aksesoris", "Aksesoris"),
]

DEFAULT_IDX = {
    "kelas": 0,
    "rambut": 0,
    "warna_rambut": 0,
    "kulit": 0,
    "mata": 0,
    "outfit": 0,
    "aksesoris": 0,
}

_CLASS_SKILLS = {
    "Star Mage": {"atk": "Starlight Slash", "spell": "Cosmic Saving Aura"},
    "Siren Bard": {"atk": "Melody Strike", "spell": "Coin Harmony"},
    "Riot Rogue": {"atk": "Quick Coin Cut", "spell": "Impulse Dodge"},
    "Fire Knight": {"atk": "Valor Blade", "spell": "Shield of Budget"},
}


def opt(cfg, key):
    items = OPT[key]
    idx = int(cfg.get(key, DEFAULT_IDX.get(key, 0))) % len(items)
    return items[idx]


def cycle(cfg, key, delta=1):
    items = OPT[key]
    cur = int(cfg.get(key, DEFAULT_IDX.get(key, 0)))
    cfg[key] = (cur + delta) % len(items)


def random_char():
    return {k: random.randrange(len(v)) for k, v in OPT.items()}


def cls_info(cfg):
    cname = opt(cfg, "kelas")[0]
    return _CLASS_SKILLS.get(cname, _CLASS_SKILLS["Star Mage"])


def draw_chibi(P, cx, gy, h, cfg, t=0.0, pose="idle", facing=1):
    """Menggambar karakter anime proporsi remaja/awal (kaki jenjang, torso ramping, senjata)."""
    ink = "#2b2d42"
    hair_style = opt(cfg, "rambut")[1]
    hair_col = opt(cfg, "warna_rambut")[1]
    skin_col = opt(cfg, "kulit")[1]
    eye_style = opt(cfg, "mata")[1]
    outfit_col = opt(cfg, "outfit")[1]
    acc = opt(cfg, "aksesoris")[1]

    bob = math.sin(t * 3.8) * (h * 0.015)
    if pose == "cheer":
        bob = -abs(math.sin(t * 8.5)) * (h * 0.045)
    elif pose == "hurt":
        bob = math.sin(t * 26.0) * (h * 0.018)

    lunge = (h * 0.07 * facing) if pose == "attack" else 0.0
    x = cx + lunge
    y = gy + bob

    # Bayangan kaki
    P.oval(x, gy + 2, h * 0.22, h * 0.04, fill="#d5dce8", outline="", width=0)

    # Rambut belakang panjang / ponytail / twin tails
    head_y = y - h * 0.72
    if hair_style == "long":
        P.poly([
            (x - h * 0.16, head_y),
            (x + h * 0.16, head_y),
            (x + h * 0.21, y - h * 0.24),
            (x - h * 0.21, y - h * 0.24),
        ], fill=hair_col, outline=ink, width=1.6)
    elif hair_style == "twins":
        P.poly([(x - h * 0.13, head_y - h * 0.04), (x - h * 0.25, y - h * 0.28), (x - h * 0.14, y - h * 0.26)], fill=hair_col, outline=ink, width=1.6)
        P.poly([(x + h * 0.13, head_y - h * 0.04), (x + h * 0.25, y - h * 0.28), (x + h * 0.14, y - h * 0.26)], fill=hair_col, outline=ink, width=1.6)
    elif hair_style == "pony":
        P.poly([(x + h * 0.06, head_y - h * 0.08), (x + h * 0.24, head_y + h * 0.04), (x + h * 0.18, y - h * 0.34)], fill=hair_col, outline=ink, width=1.6)

    # Kaki jenjang & sepatu boots pastel
    leg_top = y - h * 0.32
    P.rect(x - h * 0.085, leg_top, h * 0.06, h * 0.26, fill=skin_col, outline=ink, width=1.5)
    P.rect(x + h * 0.025, leg_top, h * 0.06, h * 0.26, fill=skin_col, outline=ink, width=1.5)
    # Sepatu / boots
    P.rect(x - h * 0.095, y - h * 0.08, h * 0.075, h * 0.08, fill=outfit_col, outline=ink, width=1.5)
    P.rect(x + h * 0.020, y - h * 0.08, h * 0.075, h * 0.08, fill=outfit_col, outline=ink, width=1.5)

    # Rok / Celana & Atasan ramping
    skirt_y = y - h * 0.36
    P.poly([
        (x - h * 0.09, y - h * 0.44),
        (x + h * 0.09, y - h * 0.44),
        (x + h * 0.15, y - h * 0.26),
        (x - h * 0.15, y - h * 0.26),
    ], fill=outfit_col, outline=ink, width=1.6)
    # Torso / Baju atas
    P.poly([
        (x - h * 0.08, y - h * 0.58),
        (x + h * 0.08, y - h * 0.58),
        (x + h * 0.10, skirt_y + h * 0.02),
        (x - h * 0.10, skirt_y + h * 0.02),
    ], fill="#ffffff", outline=ink, width=1.6)
    # Pita / Dasi dada
    P.poly([
        (x - h * 0.035, y - h * 0.53),
        (x + h * 0.035, y - h * 0.53),
        (x, y - h * 0.47),
    ], fill="#e06d9f", outline=ink, width=1.2)

    # Lengan ramping
    shoulder_y = y - h * 0.55
    if pose in ("cheer", "attack"):
        P.limb([(x - h * 0.08, shoulder_y), (x - h * 0.18, shoulder_y - h * 0.13)], skin_col, h * 0.042, 1.4)
        P.limb([(x + h * 0.08, shoulder_y), (x + h * 0.20, shoulder_y - h * 0.10)], skin_col, h * 0.042, 1.4)
    else:
        P.limb([(x - h * 0.08, shoulder_y), (x - h * 0.14, y - h * 0.37)], skin_col, h * 0.042, 1.4)
        P.limb([(x + h * 0.08, shoulder_y), (x + h * 0.14, y - h * 0.37)], skin_col, h * 0.042, 1.4)

    # Tongkat bintang / pedang saat attack
    if pose == "attack":
        wx = x + h * 0.22 * facing
        wy = shoulder_y - h * 0.08
        P.line([(wx, wy + h * 0.16), (wx + h * 0.14 * facing, wy - h * 0.16)], fill="#e9be56", width=3.5)
        P.star(wx + h * 0.15 * facing, wy - h * 0.18, h * 0.055, fill="#fdf0c2", outline=ink, width=1.4)

    # Leher & Kepala proporsional
    P.rect(x - h * 0.025, y - h * 0.62, h * 0.05, h * 0.05, fill=skin_col, outline=ink, width=1.2)
    P.oval(x, head_y, h * 0.145, h * 0.135, fill=skin_col, outline=ink, width=1.7)

    # Poni & rambut samping
    P.poly([
        (x - h * 0.155, head_y + h * 0.02),
        (x - h * 0.12, head_y - h * 0.14),
        (x, head_y - h * 0.16),
        (x + h * 0.12, head_y - h * 0.14),
        (x + h * 0.155, head_y + h * 0.02),
        (x + h * 0.06, head_y - h * 0.05),
        (x, head_y - h * 0.02),
        (x - h * 0.06, head_y - h * 0.05),
    ], fill=hair_col, outline=ink, width=1.7)

    # Aksesoris
    if acc == "star":
        P.star(x + h * 0.10, head_y - h * 0.09, h * 0.04, fill="#fdf0c2", outline=ink, width=1.2)
    elif acc == "cat":
        P.poly([(x - h * 0.12, head_y - h * 0.10), (x - h * 0.09, head_y - h * 0.21), (x - h * 0.03, head_y - h * 0.13)], fill=hair_col, outline=ink, width=1.4)
        P.poly([(x + h * 0.12, head_y - h * 0.10), (x + h * 0.09, head_y - h * 0.21), (x + h * 0.03, head_y - h * 0.13)], fill=hair_col, outline=ink, width=1.4)
    elif acc == "crown":
        P.poly([
            (x - h * 0.06, head_y - h * 0.14),
            (x - h * 0.06, head_y - h * 0.22),
            (x - h * 0.02, head_y - h * 0.18),
            (x, head_y - h * 0.24),
            (x + h * 0.02, head_y - h * 0.18),
            (x + h * 0.06, head_y - h * 0.22),
            (x + h * 0.06, head_y - h * 0.14),
        ], fill="#fdf0c2", outline=ink, width=1.4)

    # Mata anime & rona pipi
    ex = h * 0.055
    ey = head_y + h * 0.01
    P.oval(x - ex - 2, ey + h * 0.03, h * 0.02, h * 0.012, fill="#f6b2c6", outline="", width=0)
    P.oval(x + ex + 2, ey + h * 0.03, h * 0.02, h * 0.012, fill="#f6b2c6", outline="", width=0)

    if pose == "hurt":
        P.line([(x - ex - 3.5, ey - 2.5), (x - ex + 3.5, ey + 2.5)], fill=ink, width=2)
        P.line([(x - ex - 3.5, ey + 2.5), (x - ex + 3.5, ey - 2.5)], fill=ink, width=2)
        P.line([(x + ex - 3.5, ey - 2.5), (x + ex + 3.5, ey + 2.5)], fill=ink, width=2)
        P.line([(x + ex - 3.5, ey + 2.5), (x + ex + 3.5, ey - 2.5)], fill=ink, width=2)
    elif eye_style == "happy" or pose == "cheer":
        P.line([(x - ex - 4, ey + 2), (x - ex, ey - 3), (x - ex + 4, ey + 2)], fill=ink, width=1.8)
        P.line([(x + ex - 4, ey + 2), (x + ex, ey - 3), (x + ex + 4, ey + 2)], fill=ink, width=1.8)
    else:
        P.oval(x - ex, ey, h * 0.022, h * 0.028, fill=ink, outline="", width=0)
        P.oval(x + ex, ey, h * 0.022, h * 0.028, fill=ink, outline="", width=0)
        if eye_style == "sparkle":
            P.oval(x - ex - 1, ey - 1.5, h * 0.008, h * 0.008, fill="#ffffff", outline="", width=0)
            P.oval(x + ex - 1, ey - 1.5, h * 0.008, h * 0.008, fill="#ffffff", outline="", width=0)

    # Mulut
    my = head_y + h * 0.062
    if pose in ("cheer", "attack"):
        P.oval(x, my, h * 0.02, h * 0.016, fill="#e06d9f", outline=ink, width=1.1)
    else:
        P.line([(x - 3.5, my), (x, my + 2), (x + 3.5, my)], fill=ink, width=1.5)


def draw_boss_chibi(P, cx, gy, h, harga, t=0.0, pose="idle", flash=False):
    """Menggambar Boss Wishlist bertema monster hewan: Wyvern, Chibi Godzilla, atau Fire Dragon."""
    if harga < 1_000_000:
        tier = {
            "kind": "wyvern",
            "label": "BABY WYVERN",
            "body": "#a8e6cf",
            "belly": "#fdf6d8",
            "spike": "#ffd166",
            "eye": "#2b2d42",
        }
    elif harga < 5_000_000:
        tier = {
            "kind": "godzilla",
            "label": "CHIBI GODZILLA",
            "body": "#8ecae6",
            "belly": "#e0fbfc",
            "spike": "#7b6cf6",
            "eye": "#d62828",
        }
    else:
        tier = {
            "kind": "dragon",
            "label": "FIRE DRAGON",
            "body": "#f4978e",
            "belly": "#ffe5d9",
            "spike": "#ffb703",
            "eye": "#2b2d42",
        }

    body_col = "#ffffff" if flash else tier["body"]
    belly_col = "#ffffff" if flash else tier["belly"]
    spike_col = "#ffffff" if flash else tier["spike"]
    ink = "#2b2d42"

    bob = math.sin(t * 3.5) * (h * 0.025)
    shake = (math.sin(t * 36) * h * 0.04) if pose == "hurt" else 0.0
    x = cx + shake
    y = gy + bob

    P.oval(x, gy + 2, h * 0.34, h * 0.06, fill="#cfd6e6", outline="", width=0)

    # Ekor
    P.poly([
        (x + h * 0.16, y - h * 0.16),
        (x + h * 0.44, y - h * 0.24),
        (x + h * 0.48, y - h * 0.14),
        (x + h * 0.20, y - h * 0.06),
    ], fill=body_col, outline=ink, width=1.8)

    # Sayap atau Duri Punggung Godzilla
    if tier["kind"] in ("wyvern", "dragon"):
        flap = math.sin(t * 5.0) * h * 0.04
        P.poly([
            (x + h * 0.08, y - h * 0.44),
            (x + h * 0.38, y - h * 0.68 + flap),
            (x + h * 0.32, y - h * 0.38 + flap),
            (x + h * 0.12, y - h * 0.32),
        ], fill=spike_col, outline=ink, width=1.8)
    else:
        for idx, dy in enumerate((0.52, 0.38, 0.24)):
            sz = h * (0.09 if idx == 1 else 0.07)
            P.poly([
                (x + h * 0.16, y - h * dy - sz),
                (x + h * 0.28 + sz * 0.4, y - h * dy),
                (x + h * 0.16, y - h * dy + sz),
            ], fill=spike_col, outline=ink, width=1.5)

    # Badan & perut
    P.oval(x, y - h * 0.28, h * 0.24, h * 0.24, fill=body_col, outline=ink, width=1.8)
    P.oval(x - h * 0.04, y - h * 0.26, h * 0.14, h * 0.17, fill=belly_col, outline=ink, width=1.4)

    # Kaki
    P.oval(x - h * 0.11, y - h * 0.06, h * 0.09, h * 0.06, fill=body_col, outline=ink, width=1.8)
    P.oval(x + h * 0.10, y - h * 0.06, h * 0.09, h * 0.06, fill=body_col, outline=ink, width=1.8)

    # Kepala & moncong
    hx, hy = x - h * 0.06, y - h * 0.56
    P.oval(hx, hy, h * 0.21, h * 0.17, fill=body_col, outline=ink, width=1.8)
    P.oval(hx - h * 0.14, hy + h * 0.03, h * 0.11, h * 0.09, fill=body_col, outline=ink, width=1.8)

    # Tanduk
    P.poly([
        (hx + h * 0.02, hy - h * 0.14),
        (hx + h * 0.08, hy - h * 0.27),
        (hx + h * 0.13, hy - h * 0.12),
    ], fill=spike_col, outline=ink, width=1.5)

    # Mata
    ex, ey = hx - h * 0.06, hy - h * 0.03
    if pose == "hurt":
        P.line([(ex - 5, ey - 4), (ex + 5, ey + 4)], fill=ink, width=2.2)
        P.line([(ex - 5, ey + 4), (ex + 5, ey - 4)], fill=ink, width=2.2)
    else:
        P.oval(ex, ey, h * 0.042, h * 0.048, fill="#ffffff", outline=ink, width=1.4)
        P.oval(ex - 1, ey, h * 0.022, h * 0.028, fill=tier["eye"], outline="", width=0)

    # Tangan & semburan api
    P.oval(x - h * 0.18, y - h * 0.30, h * 0.06, h * 0.04, fill=body_col, outline=ink, width=1.4)
    if tier["kind"] == "dragon" and pose != "hurt":
        P.poly([
            (hx - h * 0.25, hy + h * 0.04),
            (hx - h * 0.38, hy + h * 0.01),
            (hx - h * 0.34, hy + h * 0.08),
        ], fill="#ffb703", outline=ink, width=1.4)

    return tier


def draw_potion(P, cx, gy, h, ratio=0.5, color="#e06d9f", t=0.0):
    """Botol potion HP Dana Darurat minimalis."""
    ink = "#2b2d42"
    ratio = max(0.0, min(1.0, float(ratio)))
    bob = math.sin(t * 3.0) * 3.0
    y = gy + bob

    P.oval(cx, gy + 2, h * 0.28, h * 0.05, fill="#cfd6e6", outline="", width=0)
    P.rect(cx - h * 0.10, y - h * 0.78, h * 0.20, h * 0.16, fill="#ffffff", outline=ink, width=1.8)
    P.rect(cx - h * 0.12, y - h * 0.88, h * 0.24, h * 0.10, fill="#e9be56", outline=ink, width=1.8)
    r = h * 0.32
    cy = y - r - h * 0.04
    P.oval(cx, cy, r, r, fill="#ffffff", outline=ink, width=2.0)
    if ratio > 0:
        fill_r = r * (0.35 + 0.58 * ratio)
        P.oval(cx, cy + (r - fill_r) * 0.45, fill_r, fill_r * 0.85, fill=color, outline="", width=0)
    P.heart(cx, cy, r * 0.28, fill="#ffffff", outline=ink, width=1.4)


def draw_badge_icon(P, cx, cy, r, kind="star", unlocked=True):
    """Menggambar medali Badge of Achievement minimalis."""
    ink = "#2b2d42"
    bg = "#fdf0c2" if unlocked else "#e6e8f0"
    rim = "#e9be56" if unlocked else "#cbd5e1"
    P.oval(cx, cy, r, r, fill=rim, outline=ink, width=1.8)
    P.oval(cx, cy, r * 0.78, r * 0.78, fill=bg, outline=ink, width=1.4)
    if not unlocked:
        P.text(cx, cy, "?", int(r * 0.9), "#7c8098", "center")
        return
    if kind == "heart":
        P.heart(cx, cy, r * 0.42, "#e06d9f", ink, 1.4)
    elif kind == "crown":
        P.poly([
            (cx - r * 0.42, cy + r * 0.24),
            (cx - r * 0.42, cy - r * 0.24),
            (cx - r * 0.16, cy - r * 0.02),
            (cx, cy - r * 0.34),
            (cx + r * 0.16, cy - r * 0.02),
            (cx + r * 0.42, cy - r * 0.24),
            (cx + r * 0.42, cy + r * 0.24),
        ], fill="#ffb703", outline=ink, width=1.4)
    elif kind == "shield":
        P.poly([
            (cx - r * 0.34, cy - r * 0.32),
            (cx + r * 0.34, cy - r * 0.32),
            (cx + r * 0.30, cy + r * 0.10),
            (cx, cy + r * 0.42),
            (cx - r * 0.30, cy + r * 0.10),
        ], fill="#7bb8e8", outline=ink, width=1.4)
    else:
        P.star(cx, cy, r * 0.46, "#ffb703", ink, 1.4)