# -*- coding: utf-8 -*-
"""
main.py - Entry point SaveQuest (Minimalist Pastel Edition + Badges of Achievement)
Jalankan dengan: python main.py
"""

import json
import math
import os
import time
import tkinter as tk
from datetime import datetime

import kit
import art
import sfx
from dialog import Dialog, Popup
import screens_title as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "savedata.json")

ACTIVE_MS = 60   # ~16 FPS saat ada animasi singkat
IDLE_MS = 220    # ~4.5 FPS saat diam -> CPU sangat ringan, klik instan

BADGE_DEFS = [
    ("first_save", "First Coin", "Menabung pertama kali untuk masa depan.", "star"),
    ("half_fund", "Safe Haven 50%", "Dana darurat mencapai 50% dari target.", "shield"),
    ("full_fund", "Fortress 100%", "Dana darurat penuh 100% tercapai!", "heart"),
    ("wish_slayer", "Wishlist Slayer", "Berhasil mengalahkan 1 Boss Wishlist.", "crown"),
    ("dragon_tamer", "Dragon Tamer", "Mengalahkan 3 Boss Wishlist!", "crown"),
    ("lv5_hero", "Rising Legend", "Mencapai Level 5 sebagai penabung handal.", "star"),
]


class CanvasPainter:
    def __init__(self, cv, pw=1280, ph=720):
        self.cv = cv
        self.pw = pw
        self.ph = ph
        self._font_cache = {}

    def _font(self, size, weight="bold"):
        key = (max(8, int(size * 0.64)), weight)
        f = self._font_cache.get(key)
        if f is None:
            f = ("Segoe UI", key[0], weight)
            self._font_cache[key] = f
        return f

    def bgfill(self, color, tags="static", *_args, **_kwargs):
        self.cv.create_rectangle(0, 0, self.pw, self.ph, fill=color, outline="", tags=tags)

    def vgrad(self, x, y, w, h, c1, c2, steps=6, tags="static", *_args, **_kwargs):
        steps = max(2, min(6, int(steps)))
        sh = h / steps
        for i in range(steps):
            col = kit.mix(c1, c2, i / (steps - 1))
            self.cv.create_rectangle(x, y + i * sh, x + w, y + (i + 1) * sh + 1, fill=col, outline="", tags=tags)

    def hgrad(self, x, y, w, h, c1, c2, steps=6, tags="static", *_args, **_kwargs):
        steps = max(2, min(6, int(steps)))
        sw = w / steps
        for i in range(steps):
            col = kit.mix(c1, c2, i / (steps - 1))
            self.cv.create_rectangle(x + i * sw, y, x + (i + 1) * sw + 1, y + h, fill=col, outline="", tags=tags)

    def rect(self, x, y, w, h, fill="", outline="", width=1.5, tags="dyn", r=0, sh=0, *_args, **_kwargs):
        self.cv.create_rectangle(
            x, y, x + w, y + h,
            fill=fill or "",
            outline=outline or "",
            width=width if outline else 0,
            tags=tags
        )

    def oval(self, x, y, rx, ry, fill="", outline="", width=1.5, tags="dyn", stipple=None, *_args, **_kwargs):
        if stipple:
            self.cv.create_oval(x - rx, y - ry, x + rx, y + ry, fill="#dfe3ee", outline="", width=0, tags=tags)
            return
        self.cv.create_oval(
            x - rx, y - ry, x + rx, y + ry,
            fill=fill or "",
            outline=outline or "",
            width=width if outline else 0,
            tags=tags
        )

    def poly(self, pts, fill="", outline="", width=1.5, tags="dyn", smooth=False, *_args, **_kwargs):
        if not pts:
            return
        if len(pts) > 14:
            pts = pts[::2]
        flat = [coord for pt in pts for coord in pt]
        self.cv.create_polygon(
            flat,
            fill=fill or "",
            outline=outline or "",
            width=width if outline else 0,
            smooth=False,
            tags=tags
        )

    def union(self, shapes, fill="", width=1.5, tags="dyn", outline=kit.INK, *_args, **_kwargs):
        for item in shapes or []:
            pts = item[0] if (isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (bool, int))) else item
            self.poly(pts, fill=fill, outline=outline if width else "", width=width, tags=tags)

    def line(self, pts, fill="#ffffff", width=2, tags="dyn", smooth=False, dash=None, cap="round", *_args, **_kwargs):
        if len(pts) >= 2:
            flat = [coord for pt in pts for coord in pt]
            kw = {
                "fill": fill or "#ffffff",
                "width": width,
                "smooth": False,
                "capstyle": cap if cap in ("round", "butt", "projecting") else "round",
                "tags": tags,
            }
            if dash:
                kw["dash"] = dash
            self.cv.create_line(flat, **kw)

    def limb(self, pts, color, w, ow=1.5, tags="dyn", smooth=False, *_args, **_kwargs):
        if len(pts) < 2:
            return
        self.line(pts, fill=kit.INK, width=w + ow * 2, tags=tags, cap="round")
        self.line(pts, fill=color, width=w, tags=tags, cap="round")

    def text(self, x, y, txt, size=16, fill="#2b2d42", anchor="center", width=None, justify="left", tags="dyn", *_args, **_kwargs):
        kw = {
            "text": str(txt),
            "font": self._font(size),
            "fill": fill,
            "anchor": anchor,
            "justify": justify,
            "tags": tags,
        }
        if width is not None:
            kw["width"] = int(width)
        self.cv.create_text(x, y, **kw)

    def stext(self, x, y, txt, size=22, fill="#2b2d42", outline="#2b2d42", off=2, tags="dyn", *_args, **_kwargs):
        self.text(x, y, txt, size, fill, "center", tags=tags)

    def bar(self, x, y, w, h, ratio, color="#5ec492", tags="dyn", *_args, **_kwargs):
        ratio = max(0.0, min(1.0, float(ratio)))
        self.rect(x, y, w, h, fill="#eef0f6", outline=kit.INK, width=1.5, tags=tags)
        if ratio > 0:
            iw = max(3, (w - 4) * ratio)
            self.rect(x + 2, y + 2, min(w - 4, iw), max(3, h - 4), fill=color, outline="", tags=tags)

    def star(self, cx, cy, r, fill="#e9be56", outline="#2b2d42", width=1.5, tags="dyn", *_args, **_kwargs):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags)

    def sparkle(self, cx, cy, r, fill="#e9be56", outline="#2b2d42", width=1.5, tags="dyn", *_args, **_kwargs):
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags)

    def heart(self, cx, cy, r, fill="#e06d9f", outline="#2b2d42", width=1.5, tags="dyn", *_args, **_kwargs):
        pts = [
            (cx, cy + r * 0.9),
            (cx - r, cy - r * 0.1),
            (cx - r * 0.5, cy - r * 0.8),
            (cx, cy - r * 0.3),
            (cx + r * 0.5, cy - r * 0.8),
            (cx + r, cy - r * 0.1),
        ]
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags)

    def hearts_row(self, x, y, count, total=6, size=14, gap=6, tags="dyn", *_args, **_kwargs):
        for i in range(total):
            col = kit.HOT if i < count else kit.GRAY
            self.heart(x + i * (size + gap) + size * 0.5, y + size * 0.5, size * 0.5, col, kit.INK, 1.5, tags=tags)

    def window(self, x, y, w, h, title="PANEL", header_col=kit.PINK, body_col=kit.WHITE, sub="", tags="dyn", *_args, **_kwargs):
        bar_h = 30
        self.rect(x, y, w, h, fill=body_col, outline=kit.INK, width=2, tags=tags)
        self.rect(x, y, w, bar_h, fill=header_col, outline=kit.INK, width=2, tags=tags)
        label = sub or title
        if label:
            self.text(x + 12, y + bar_h / 2, label, 14, kit.INK, "w", tags=tags)
        self.rect(x + w - 24, y + 6, 18, 18, fill=kit.RED, outline=kit.INK, width=1.5, tags=tags)
        return x, y + bar_h, w, h - bar_h


# ----------------------------------------------------------------------
# MODAL GALERI BADGE OF ACHIEVEMENT (DENGAN TOMBOL KELUAR [X] & AUTO-CLOSE)
# ----------------------------------------------------------------------
class BadgesModal:
    def __init__(self, app, auto_close=0.0):
        self.app = app
        self.P = app.P
        self.hits = []
        self.t = 0.0
        self.auto_close = float(auto_close or 0.0)

    def close(self):
        if self.app.dialog is self:
            self.app.dialog = None
        self.app.mark_dirty()

    def on_key(self, key, _ch):
        if key in ("Escape", "Return", "KP_Enter", "space"):
            self.close()

    def click(self, x, y):
        for hx, hy, w, h, cb in reversed(self.hits):
            if hx <= x <= hx + w and hy <= y <= hy + h:
                sfx.play("click")
                cb()
                return True
        # Klik di luar kotak modal langsung menutup pop up
        W, H = 760, 490
        px, py = (1280 - W) / 2, (720 - H) / 2
        if not (px <= x <= px + W and py <= y <= py + H):
            self.close()
        return True

    def draw(self, dt):
        P = self.P
        self.t += dt
        if self.auto_close > 0 and self.t >= self.auto_close:
            self.close()
            return

        self.hits = []
        unlocked = set(self.app.game.data.get("badges", []))
        P.cv.create_rectangle(10, 10, P.pw - 10, P.ph - 10, fill="", outline="#8d92a8", width=10, tags="dyn")
        W, H = 760, 490
        x, y = (1280 - W) / 2, (720 - H) / 2
        title_txt = f"BADGES OF ACHIEVEMENT ({len(unlocked)}/{len(BADGE_DEFS)})  ·  Klik X / Esc untuk keluar"
        bx, by, bw, _bh = P.window(x, y, W, H, title_txt, kit.YELLOW, kit.WHITE)

        # Tombol keluar [X] yang besar & jelas di pojok kanan atas
        close_x, close_y, close_s = x + W - 28, y + 3, 24
        P.rect(close_x, close_y, close_s, close_s, kit.RED, kit.INK, 1.5, "dyn")
        P.text(close_x + close_s / 2, close_y + close_s / 2, "X", 14, kit.WHITE, "center")
        self.hits.append((close_x - 4, close_y - 4, close_s + 8, close_s + 8, self.close))

        for idx, (bid, title, desc, icon_kind) in enumerate(BADGE_DEFS):
            col = idx % 2
            row = idx // 2
            cx = bx + 20 + col * 365
            cy = by + 18 + row * 116
            is_on = bid in unlocked
            P.rect(cx, cy, 350, 102, "#fffdf5" if is_on else "#f4f5f9", kit.INK, 1.5, "dyn")
            art.draw_badge_icon(P, cx + 46, cy + 51, 30, icon_kind, is_on)
            status_lbl = "TERBUKA" if is_on else "TERKUNCI"
            P.text(cx + 90, cy + 24, f"{title} [{status_lbl}]", 15, kit.INK if is_on else "#7c8098", "w")
            P.text(cx + 90, cy + 58, desc, 13, "#4a4e69" if is_on else "#9ba0b4", "w", width=245)

        # Tombol keluar di bagian bawah
        tx, ty, tw, th = x + W / 2 - 95, y + H - 56, 190, 40
        mx, my = self.app.mouse
        hov = tx <= mx <= tx + tw and ty <= my <= ty + th
        P.rect(tx, ty, tw, th, kit.darken(kit.MINT, 0.07) if hov else kit.MINT, kit.INK, 2, "dyn")
        P.text(tx + tw / 2, ty + th / 2, "KELUAR [X]", 16, kit.INK, "center")
        self.hits.append((tx, ty, tw, th, self.close))


# ----------------------------------------------------------------------
# LOGIKA GAME (DANA DARURAT + XP/LEVEL + BOSS WISHLIST + BADGES)
# ----------------------------------------------------------------------
TITLES = [
    "Rookie Saver",
    "Coin Collector",
    "Budget Knight",
    "Wealth Mage",
    "Gold Paladin",
    "Dragon Hoarder",
    "Legendary Tycoon",
]


class GameState:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.data = self.default()
        self.load()

    @staticmethod
    def default():
        return {
            "nama": "Hero",
            "target": 5_000_000,
            "saldo": 0,
            "level": 1,
            "xp": 0,
            "bosses": [],
            "badges": [],
            "log": [],
            "setup_done": False,
            "char": {},
        }

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                saved = json.load(fh)
            merged = self.default()
            merged.update(saved)
            self.data = merged
            return True
        except (OSError, ValueError):
            return False

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def reset(self):
        self.data = self.default()
        self.save()

    def hp_ratio(self):
        t = self.data["target"]
        return max(0.0, min(1.0, self.data["saldo"] / t)) if t > 0 else 0.0

    def hp_percent(self):
        return int(self.hp_ratio() * 100)

    def status(self):
        r = self.hp_ratio()
        if self.data["saldo"] <= 0:
            return "GAME OVER", "#c93b5b"
        if r >= 0.6:
            return "SEHAT", "#2d8a5e"
        if r >= 0.3:
            return "WASPADA", "#b07d19"
        return "KRITIS", "#c93b5b"

    def xp_needed(self):
        return 100 * self.data["level"]

    def title(self):
        return TITLES[min(self.data["level"] - 1, len(TITLES) - 1)]

    def _log(self, tipe, teks):
        self.data["log"].append({
            "waktu": datetime.now().strftime("%d/%m %H:%M"),
            "tipe": tipe,
            "teks": teks,
        })
        self.data["log"] = self.data["log"][-100:]

    def _check_badges(self):
        events = []
        unlocked = self.data.setdefault("badges", [])
        defeated_count = sum(1 for b in self.data["bosses"] if b.get("defeated"))
        ratio = self.hp_ratio()

        rules = [
            ("first_save", True),
            ("half_fund", ratio >= 0.5),
            ("full_fund", ratio >= 1.0),
            ("wish_slayer", defeated_count >= 1),
            ("dragon_tamer", defeated_count >= 3),
            ("lv5_hero", self.data["level"] >= 5),
        ]
        title_map = {b[0]: (b[1], b[2]) for b in BADGE_DEFS}
        for bid, cond in rules:
            if cond and bid not in unlocked:
                unlocked.append(bid)
                bname, bdesc = title_map[bid]
                self._log("badge", f"BADGE UNLOCKED: {bname}!")
                events.append(("badge_unlocked", {"id": bid, "nama": bname, "desc": bdesc}))
        return events

    def _gain_xp(self, amount):
        events = []
        d = self.data
        d["xp"] += amount
        while d["xp"] >= 100 * d["level"]:
            d["xp"] -= 100 * d["level"]
            d["level"] += 1
            self._log("levelup", f"LEVEL UP! Lv.{d['level']} - {self.title()}")
            events.append(("level_up", d["level"]))
        return events

    def unlock_hero(self):
        self._log("info", f"Hero {self.data['nama']} siap bertualang!")
        self.save()
        return []

    def add_saving(self, jumlah, ket="", boss_id=None):
        d = self.data
        events = []
        xp = 5 + jumlah // 5000
        if boss_id is None:
            d["saldo"] += jumlah
            self._log("heal", f"+{kit.rupiah(jumlah)} Dana Darurat ({ket or 'menabung'}) | +{xp} XP")
        else:
            boss = self.find_boss(boss_id)
            boss["terkumpul"] += jumlah
            self._log("boss", f"Serang {boss['nama']}: {kit.rupiah(jumlah)} ({ket or 'menabung'}) | +{xp} XP")
            if boss["terkumpul"] >= boss["harga"] and not boss["defeated"]:
                boss["defeated"] = True
                xp += 150
                self._log("boss", f"BOSS DEFEATED: {boss['nama']}! +150 XP")
                events.append(("boss_defeated", boss))
        events += self._gain_xp(xp)
        events += self._check_badges()
        self.save()
        return events

    def add_spending(self, jumlah, ket=""):
        d = self.data
        events = []
        before = d["saldo"]
        d["saldo"] = max(0, d["saldo"] - jumlah)
        loss = 3 + jumlah // 5000
        d["xp"] = max(0, d["xp"] - loss)
        self._log("damage", f"-{kit.rupiah(jumlah)} jajan ({ket or 'impulsif'}) | -{loss} XP")
        if before > 0 and d["saldo"] == 0:
            self._log("damage", "HP habis! GAME OVER")
            events.append(("game_over", None))
        self.save()
        return events

    def find_boss(self, boss_id):
        for b in self.data["bosses"]:
            if b["id"] == boss_id:
                return b
        raise KeyError(boss_id)

    def add_boss(self, nama, harga):
        self.data["bosses"].append({
            "id": str(int(time.time() * 1000)),
            "nama": nama,
            "harga": harga,
            "terkumpul": 0,
            "defeated": False,
        })
        self._log("info", f"Boss baru: {nama} ({kit.rupiah(harga)})")
        self.save()

    def remove_boss(self, boss_id):
        boss = self.find_boss(boss_id)
        self.data["bosses"].remove(boss)
        self._log("info", f"Boss {boss['nama']} dihapus")
        self.save()


# ----------------------------------------------------------------------
# HUB MINIMALIS (TABUNG, JAJAN, BOSS WISHLIST, BADGES, CUSTOM HERO)
# ----------------------------------------------------------------------
class HubY2K(kit.Screen):
    name = "hub"

    def enter(self, **_kw):
        super().enter()
        self.selected_boss_id = None
        self.hero_pose = "idle"
        self.boss_pose = "idle"
        self.pose_timer = 0.0
        self.speech_text = ""
        self.speech_timer = 0.0
        self.boss_say = ""
        self.parts = kit.Particles()

    def leave(self):
        super().leave()
        self.pose_timer = 0.0
        self.speech_timer = 0.0
        self.hero_pose = "idle"
        self.boss_pose = "idle"

    def update(self, dt):
        super().update(dt)
        self.parts.update(dt)
        if self.pose_timer > 0:
            self.pose_timer = max(0.0, self.pose_timer - dt)
            if self.pose_timer == 0:
                self.hero_pose = "idle"
                self.boss_pose = "idle"
                self.app.mark_dirty()
        if self.speech_timer > 0:
            self.speech_timer = max(0.0, self.speech_timer - dt)
            if self.speech_timer == 0:
                self.app.mark_dirty()

    def trigger_reaction(self, hero_pose, boss_pose, hero_say, boss_say, cols, fx_x=155):
        self.hero_pose = hero_pose
        self.boss_pose = boss_pose
        self.pose_timer = 0.9
        self.speech_text = hero_say
        self.boss_say = boss_say
        self.speech_timer = 1.6
        self.parts.spawn(fx_x, 280, "spark", cols, 6, 160, 110, 400, 0.55, 7)
        self.app.mark_dirty()

    def draw_static(self):
        self.P.bgfill("#f6f7fb", tags="static")
        self.P.rect(0, 686, 1280, 34, "#eceef6", kit.INK, 1, tags="static")
        self.P.text(1264, 703, "SaveQuest · Minimalist Edition", 14, "#6c7086", "e", tags="static")

    def on_key(self, key, _ch):
        if key == "Escape":
            self.app.go_back(fallback="title")
            return True
        return False

    def draw(self):
        P = self.P
        g, d = self.app.game, self.app.game.data
        self.hits = []

        # Top Bar Minimalis (termasuk tombol BADGES)
        P.window(24, 18, 1232, 82, "MENU UTAMA", kit.PINK, kit.WHITE, tags="dyn")
        badge_cnt = len(d.get("badges", []))
        self.button(40, 56, 138, 34, "+ TABUNG", kit.MINT, self.open_save, 14)
        self.button(188, 56, 132, 34, "- JAJAN", kit.RED, self.open_spend, 14)
        self.button(330, 56, 130, 34, "+ BOSS", kit.SKY, self.open_add_boss, 14)
        self.button(470, 56, 162, 34, f"BADGES ({badge_cnt}/{len(BADGE_DEFS)})", kit.YELLOW, self.open_badges, 14)
        self.button(642, 56, 162, 34, "CUSTOM HERO", kit.LILAC, lambda: self.app.goto("creator"), 14)
        self.button(814, 56, 154, 34, "PENGATURAN", kit.CREAM, self.open_settings, 14)
        self.button(978, 56, 112, 34, "RESET", kit.GRAY, self.open_reset, 14)
        self.button(1100, 56, 140, 34, "KEMBALI", kit.ORANGE, lambda: self.app.go_back(fallback="title"), 14)

        # Panel Kiri: Arena & Status dengan Background Pemandangan Pastel
        P.window(24, 114, 580, 556, "STATUS & ARENA", kit.SKY, kit.WHITE, tags="dyn")
        ax, ay, aw, ah = 44, 158, 540, 224
        P.rect(ax, ay, aw, ah, "#e8f4fc", kit.INK, 1.5, "dyn")
        P.oval(ax + 470, ay + 42, 22, 22, "#fde68a", "", 0, "dyn")
        P.oval(ax + 115, ay + 44, 34, 12, kit.WHITE, "", 0, "dyn")
        P.oval(ax + 135, ay + 40, 26, 14, kit.WHITE, "", 0, "dyn")
        P.oval(ax + 340, ay + 54, 38, 12, kit.WHITE, "", 0, "dyn")
        P.poly([
            (ax, ay + 170),
            (ax + 150, ay + 122),
            (ax + 320, ay + 168),
            (ax + 460, ay + 126),
            (ax + aw, ay + 162),
            (ax + aw, ay + ah),
            (ax, ay + ah),
        ], fill="#cdebd8", outline="", width=0, tags="dyn")
        P.rect(ax + 1, ay + 196, aw - 2, 27, "#b7e4c7", "", 0, "dyn")
        P.line([(ax, ay + 196), (ax + aw, ay + 196)], kit.INK, 1.5, "dyn")
        P.oval(ax + 245, ay + 206, 14, 6, "#cbd5e1", kit.INK, 1, "dyn")
        P.oval(ax + 365, ay + 210, 10, 5, "#cbd5e1", kit.INK, 1, "dyn")

        char_cfg = dict(d.get("char") or {})
        for k in art.OPT:
            char_cfg.setdefault(k, art.DEFAULT_IDX[k])
        art.draw_chibi(P, 155, 366, 172, char_cfg, self.t, self.hero_pose, 1)
        if self.speech_timer > 0 and self.speech_text:
            P.rect(86, 172, 160, 28, kit.WHITE, kit.INK, 1.5, "dyn")
            P.text(166, 186, self.speech_text, 13, kit.INK, "center")

        bosses_active = [b for b in d["bosses"] if not b["defeated"]]
        if bosses_active:
            target_b = next((b for b in bosses_active if b["id"] == self.selected_boss_id), bosses_active[0])
            flash = self.boss_pose == "hurt" and int(self.t * 10) % 2 == 0
            tier = art.draw_boss_chibi(P, 455, 366, 156, target_b["harga"], self.t, self.boss_pose, flash)
            P.rect(368, 170, 198, 42, kit.LILAC, kit.INK, 1.5, "dyn")
            P.text(467, 184, target_b["nama"][:17], 13, kit.INK)
            P.text(467, 201, f"{tier['label']} · {kit.rupiah(target_b['harga'])}", 11, "#4a4e69")
            if self.speech_timer > 0 and self.boss_say:
                P.rect(386, 218, 136, 26, kit.YELLOW, kit.INK, 1.5, "dyn")
                P.text(454, 231, self.boss_say, 13, kit.INK, "center")
            P.text(308, 286, "VS", 18, "#6c7086")
        else:
            art.draw_potion(P, 445, 362, 118, g.hp_ratio(), kit.HOT, self.t)
            P.text(445, 224, "DANA DARURAT", 12, "#5c6075")

        status, scol = g.status()
        P.text(44, 404, f"{d['nama'].upper()} · Lv.{d['level']} ({g.title()})", 18, kit.INK, "w")
        P.text(44, 432, f"HP DANA DARURAT: {g.hp_percent()}% · {status}", 14, scol, "w")
        P.bar(44, 448, 540, 22, g.hp_ratio(), kit.GREEN if g.hp_ratio() >= 0.6 else (kit.GOLD if g.hp_ratio() >= 0.3 else kit.HOT))
        P.text(44, 484, f"Saldo: {kit.rupiah(d['saldo'])} / {kit.rupiah(d['target'])}", 14, kit.INK, "w")

        P.text(44, 514, f"XP: {d['xp']} / {g.xp_needed()}", 14, kit.INK, "w")
        P.bar(44, 530, 540, 18, d["xp"] / max(1, g.xp_needed()), kit.BLUE)

        P.text(44, 566, "AKTIVITAS TERBARU", 13, "#5c6075", "w")
        recent = list(reversed(d["log"][-3:]))
        if not recent:
            P.text(44, 592, "Belum ada transaksi. Klik + TABUNG atau - JAJAN.", 13, "#7c8098", "w")
        else:
            for idx, item in enumerate(recent):
                P.text(44, 592 + idx * 22, f"[{item['waktu']}] {item['teks'][:58]}", 13, kit.INK, "w")

        # Panel Kanan: Boss Wishlist Minimalis
        P.window(620, 114, 636, 556, "WISHLIST TARGET", kit.LILAC, kit.WHITE, tags="dyn")
        if not d["bosses"]:
            P.text(938, 355, "Belum ada target wishlist.\nKlik '+ BOSS' untuk menambahkan.", 16, "#7c8098", "center", justify="center")
        else:
            ordered = bosses_active + [b for b in d["bosses"] if b["defeated"]]
            for i, b in enumerate(ordered[:5]):
                by = 160 + i * 96
                prog = min(1.0, b["terkumpul"] / b["harga"]) if b["harga"] else 1.0
                P.rect(640, by, 596, 84, "#fafbfe", kit.INK, 1.5, "dyn")
                art.draw_boss_chibi(P, 678, by + 76, 62, b["harga"], self.t + i, "hurt" if b["defeated"] else "idle")
                tag_txt = " [SELESAI · BADGE!]" if b["defeated"] else ""
                P.text(718, by + 18, f"{b['nama']}{tag_txt}", 15, kit.INK, "w")
                P.text(718, by + 38, f"{kit.rupiah(b['terkumpul'])} / {kit.rupiah(b['harga'])} ({int(prog * 100)}%)", 13, "#5c6075", "w")
                P.bar(718, by + 54, 316, 16, prog, kit.GOLD if b["defeated"] else kit.HOT)
                if not b["defeated"]:
                    self.button(1048, by + 16, 84, 28, "TABUNG", kit.MINT, lambda bid=b["id"]: self.open_save(bid), 13)
                self.button(1140, by + 16, 82, 28, "HAPUS", kit.GRAY, lambda bid=b["id"]: self.remove_boss(bid), 13)

        self.parts.draw(P)

    def open_badges(self):
        self.app.dialog = BadgesModal(self.app)
        self.app.mark_dirty()

    def open_save(self, boss_id=None):
        bosses = [b for b in self.app.game.data["bosses"] if not b["defeated"]]
        labels = ["Dana Darurat (HP)"] + [f"Wishlist: {b['nama']}" for b in bosses]
        ids = [None] + [b["id"] for b in bosses]
        fields = [
            {"key": "jumlah", "label": "Nominal tabungan", "kind": "money", "value": "50000", "hint": "mis. 50000"},
            {"key": "ket", "label": "Catatan", "kind": "text", "value": "Menabung"},
        ]
        if boss_id is None:
            fields.append({"key": "tujuan", "label": "Tujuan tabungan", "kind": "choice", "choices": labels})

        def on_ok(r):
            target_id = boss_id if boss_id is not None else ids[r["tujuan"]]
            if target_id is not None:
                self.selected_boss_id = target_id
                self.trigger_reaction("attack", "hurt", "zhammm! Serang!", "aduh!", [kit.HOT, kit.SKY], fx_x=455)
            else:
                self.trigger_reaction("cheer", "idle", "yaayy^^ +HP", "...", [kit.GREEN, kit.BLUE], fx_x=155)
            ev = self.app.game.add_saving(r["jumlah"], r["ket"], target_id)
            self.app.show_events(ev)

        self.app.dialog = Dialog(
            self.app, "TABUNG (HEAL)", fields, "SIMPAN", kit.MINT, on_ok,
            "Menambah HP Dana Darurat, XP, atau progres wishlist."
        )

    def open_spend(self):
        def on_ok(r):
            sfx.play("hit")
            self.trigger_reaction("hurt", "cheer", "bhoom!! -HP", "hehe", [kit.HOT, kit.ORANGE], fx_x=155)
            ev = self.app.game.add_spending(r["jumlah"], r["ket"])
            self.app.show_events(ev)

        self.app.dialog = Dialog(
            self.app, "JAJAN IMPULSIF (DAMAGE)",
            [
                {"key": "jumlah", "label": "Nominal jajan", "kind": "money", "value": "25000", "hint": "mis. 25000"},
                {"key": "ket", "label": "Keterangan jajan", "kind": "text", "value": "Jajan impulsif"},
            ],
            "TERIMA DAMAGE", kit.RED, on_ok,
            "Mengurangi HP Dana Darurat dan XP."
        )

    def open_add_boss(self):
        def on_ok(r):
            self.app.game.add_boss(r["nama"][:24], r["harga"])
            self.selected_boss_id = self.app.game.data["bosses"][-1]["id"]
            self.app.toast("Target wishlist ditambahkan!", kit.SKY)

        self.app.dialog = Dialog(
            self.app, "TAMBAH TARGET WISHLIST",
            [
                {"key": "nama", "label": "Nama barang", "kind": "text", "required": True, "hint": "Mechanical Keyboard"},
                {"key": "harga", "label": "Harga target", "kind": "money", "value": "1000000", "hint": "mis. 1000000"},
            ],
            "TAMBAH", kit.SKY, on_ok
        )

    def remove_boss(self, boss_id):
        self.app.game.remove_boss(boss_id)
        if self.selected_boss_id == boss_id:
            self.selected_boss_id = None
        self.app.toast("Target dihapus.", kit.GRAY)

    def open_settings(self):
        d = self.app.game.data

        def on_ok(r):
            d["nama"] = r["nama"][:16]
            d["target"] = r["target"]
            d["saldo"] = r["saldo"]
            d["setup_done"] = True
            self.app.game.save()
            self.app.toast("Pengaturan tersimpan!", kit.YELLOW)

        self.app.dialog = Dialog(
            self.app, "PENGATURAN",
            [
                {"key": "nama", "label": "Nama pahlawan", "kind": "text", "required": True, "value": d["nama"]},
                {"key": "target", "label": "Target dana darurat", "kind": "money", "value": str(d["target"])},
                {"key": "saldo", "label": "Saldo dana darurat", "kind": "money", "allow_zero": True, "value": str(d["saldo"])},
            ],
            "SIMPAN", kit.YELLOW, on_ok
        )

    def open_reset(self):
        def on_ok(r):
            if r["yakin"] == 1:
                self.app.game.reset()
                self.selected_boss_id = None
                self.app.toast("Progres direset.", kit.PINK)

        self.app.dialog = Dialog(
            self.app, "RESET PROGRES",
            [{"key": "yakin", "label": "Hapus semua data?", "kind": "choice", "choices": ["Batal", "Ya, reset"]}],
            "OK", kit.RED, on_ok
        )


# ----------------------------------------------------------------------
# APLIKASI UTAMA
# ----------------------------------------------------------------------
class SaveQuestApp(tk.Tk):
    WIDTH, HEIGHT = 1280, 720

    def __init__(self):
        super().__init__()
        self.title("SaveQuest - Minimalist Savings RPG")
        self.configure(bg="#f6f7fb")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)

        self.cv = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT,
                            bg="#f6f7fb", highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        self.P = CanvasPainter(self.cv, self.WIDTH, self.HEIGHT)
        self.game = GameState()
        self.dialog = None
        self._popup_queue = []
        self.mouse = (0, 0)
        self.mouse_down = False
        self._toast_text = ""
        self._toast_timer = 0.0
        self._toast_color = kit.YELLOW
        self._dirty = True
        self._last_hover_idx = -1
        self._last_click_ts = 0.0
        self._after_id = None
        self._closing = False
        self._nav_stack = []

        self.screens = {
            "title": st.TitleScreen(self),
            "creator": st.CreatorScreen(self),
            "hub": HubY2K(self),
        }
        self.current_screen = self.screens["title"]
        self.current_screen.enter()
        self.current_screen.draw_static()
        self._redraw()

        self.cv.bind("<Motion>", self._on_motion)
        self.cv.bind("<ButtonPress-1>", self._on_press)
        self.cv.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<KeyPress>", self._on_key)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self._last_time = time.perf_counter()
        self._loop()

    def mark_dirty(self):
        self._dirty = True

    def _next_popup(self):
        if self.dialog is None and self._popup_queue:
            title, msg, color, btn, auto_sec = self._popup_queue.pop(0)
            self.dialog = Popup(
                self, title, msg, art=None, color=color, btn=btn,
                on_close=self._next_popup, sound="lvl", auto_close=auto_sec
            )
            self._dirty = True

    def _redraw(self, dt=0.016):
        if self._closing:
            return
        self.cv.delete("dyn")
        self.current_screen.hits = []
        self.current_screen.draw()

        if self.dialog is not None:
            self.dialog.draw(dt)

        if self._toast_timer > 0 and self._toast_text:
            self.P.rect(390, 24, 500, 36, self._toast_color, kit.INK, 1.5, "dyn")
            self.P.text(640, 42, self._toast_text, 14, kit.INK, tags="dyn")
        self._dirty = False

    def goto(self, name, push_history=True, **kw):
        if name not in self.screens:
            return
        prev_name = self.current_screen.name
        if push_history and prev_name != name:
            if not self._nav_stack or self._nav_stack[-1] != prev_name:
                self._nav_stack.append(prev_name)
                if len(self._nav_stack) > 10:
                    self._nav_stack.pop(0)

        self.dialog = None
        self._popup_queue.clear()
        self.mouse_down = False
        if hasattr(sfx, "clear"):
            sfx.clear()
        if hasattr(self.current_screen, "leave"):
            self.current_screen.leave()

        self.cv.delete("all")
        self._last_hover_idx = -1
        self.current_screen = self.screens[name]
        self.current_screen.enter(**kw)
        self.current_screen.draw_static()
        self._redraw()

    def go_back(self, fallback="title"):
        while self._nav_stack:
            target = self._nav_stack.pop()
            if target != self.current_screen.name and target in self.screens:
                self.goto(target, push_history=False)
                return
        self.goto(fallback, push_history=False)

    def start_game(self):
        if not self.game.data.get("setup_done"):
            self.goto("creator", first=True)
        else:
            self.goto("hub")

    def quit_app(self):
        if self._closing:
            return
        self._closing = True
        if hasattr(sfx, "clear"):
            sfx.clear()
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        self.destroy()

    def toast(self, msg, color=kit.YELLOW, duration=2.0):
        self._toast_text = msg
        self._toast_color = color
        self._toast_timer = duration
        self._dirty = True

    def show_events(self, events):
        for kind, payload in events:
            if kind == "boss_defeated":
                self._popup_queue.append((
                    "MONSTER DIKALAHKAN!",
                    f"Wishlist '{payload['nama']}' berhasil terkumpul! Bonus +150 XP.",
                    kit.GOLD,
                    "LANJUT",
                    2.5,
                ))
            elif kind == "badge_unlocked":
                self._popup_queue.append((
                    "BADGE OF ACHIEVEMENT!",
                    f"Trofi baru terbuka: {payload['nama']}\n{payload['desc']}",
                    kit.MINT,
                    "MANTAP!",
                    2.8,
                ))
            elif kind == "level_up":
                self._popup_queue.append((
                    "LEVEL UP!",
                    f"Naik ke Lv.{payload} · {self.game.title()}.",
                    kit.YELLOW,
                    "TUTUP",
                    2.2,
                ))
            elif kind == "game_over":
                self._popup_queue.append((
                    "GAME OVER",
                    "Dana Darurat habis. Klik + TABUNG untuk memulihkan HP.",
                    kit.RED,
                    "BANGKIT",
                    0.0,
                ))
        self._next_popup()
        self._dirty = True

    def _on_motion(self, e):
        self.mouse = (e.x, e.y)
        hits = self.dialog.hits if self.dialog is not None else self.current_screen.hits
        hov_idx = -1
        for i, (hx, hy, w, h, _cb) in enumerate(hits):
            if hx <= e.x <= hx + w and hy <= e.y <= hy + h:
                hov_idx = i
                break
        if hov_idx != self._last_hover_idx:
            self._last_hover_idx = hov_idx
            self._dirty = True

    def _on_press(self, e):
        now = time.perf_counter()
        if now - self._last_click_ts < 0.06:
            return
        self._last_click_ts = now
        self.mouse = (e.x, e.y)
        self.mouse_down = True
        if self.dialog is not None:
            self.dialog.click(e.x, e.y)
            self.mouse_down = False
            self._dirty = True
            self._redraw()
            return
        self.current_screen.click(e.x, e.y)
        self.mouse_down = False
        self._dirty = True
        self._redraw()

    def _on_release(self, e):
        self.mouse = (e.x, e.y)
        if self.mouse_down:
            self.mouse_down = False
            self._dirty = True

    def _on_key(self, e):
        if self.dialog is not None:
            self.dialog.on_key(e.keysym, e.char)
            self._dirty = True
            self._redraw()
            return
        self.current_screen.on_key(e.keysym, e.char)
        self._dirty = True
        self._redraw()

    def _loop(self):
        if self._closing:
            return
        now = time.perf_counter()
        dt = min(0.1, max(0.001, now - self._last_time))
        self._last_time = now

        if self._toast_timer > 0:
            self._toast_timer = max(0.0, self._toast_timer - dt)
            if self._toast_timer == 0:
                self._dirty = True

        self.current_screen.update(dt)

        has_parts = bool(getattr(self.current_screen, "parts", None) and self.current_screen.parts.items)
        has_anim = (
            getattr(self.current_screen, "pose_timer", 0.0) > 0
            or getattr(self.current_screen, "speech_timer", 0.0) > 0
            or getattr(self.current_screen, "cheer", 0.0) > 0
            or getattr(self.current_screen, "hop", 0.0) > 0
        )
        active = bool(self._dirty or has_parts or has_anim or self._toast_timer > 0 or self.dialog is not None)
        if active:
            self._redraw(dt)

        try:
            self._after_id = self.after(ACTIVE_MS if active else IDLE_MS, self._loop)
        except tk.TclError:
            self._after_id = None


if __name__ == "__main__":
    SaveQuestApp().mainloop()