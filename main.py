# -*- coding: utf-8 -*-
"""
main.py - Entry point SaveQuest (Y2K + Tabungan Dana Darurat & Boss Wishlist)
Jalankan dengan: python -u main.py
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


# ----------------------------------------------------------------------
# PAINTER (P) UNTUK CANVAS 1280x720 (100% KOMPATIBEL DENGAN art.py)
# ----------------------------------------------------------------------
class CanvasPainter:
    def __init__(self, cv, pw=1280, ph=720):
        self.cv = cv
        self.pw = pw
        self.ph = ph

    def _font(self, size, weight="bold"):
        return ("Courier New", max(8, int(size * 0.62)), weight)

    def _round_pts(self, x, y, w, h, r):
        r = max(0.0, min(float(r), w / 2.0, h / 2.0))
        if r <= 0.5:
            return None
        pts = []
        corners = [
            (x + w - r, y + r, -math.pi / 2, 0.0),
            (x + w - r, y + h - r, 0.0, math.pi / 2),
            (x + r, y + h - r, math.pi / 2, math.pi),
            (x + r, y + r, math.pi, 1.5 * math.pi),
        ]
        for cx, cy, a0, a1 in corners:
            for i in range(6):
                a = a0 + (a1 - a0) * (i / 5.0)
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        return pts

    def bgfill(self, color, tags="static", *_args, **_kwargs):
        self.cv.create_rectangle(0, 0, self.pw, self.ph, fill=color, outline="", tags=tags)

    def vgrad(self, x, y, w, h, c1, c2, steps=24, tags="static", *_args, **_kwargs):
        steps = max(2, int(steps))
        sh = h / steps
        for i in range(steps):
            col = kit.mix(c1, c2, i / (steps - 1))
            self.cv.create_rectangle(
                x, y + i * sh, x + w, y + (i + 1) * sh + 1,
                fill=col, outline="", tags=tags
            )

    def hgrad(self, x, y, w, h, c1, c2, steps=24, tags="static", *_args, **_kwargs):
        steps = max(2, int(steps))
        sw = w / steps
        for i in range(steps):
            col = kit.mix(c1, c2, i / (steps - 1))
            self.cv.create_rectangle(
                x + i * sw, y, x + (i + 1) * sw + 1, y + h,
                fill=col, outline="", tags=tags
            )

    def rect(self, x, y, w, h, fill="", outline="", width=2, tags="dyn", r=0, sh=0, *_args, **_kwargs):
        rpts = self._round_pts(x, y, w, h, r)
        if sh:
            if rpts:
                spts = [(px + sh, py + sh) for px, py in rpts]
                self.poly(spts, fill=kit.INK, outline="", width=0, tags=tags, smooth=True)
            else:
                self.cv.create_rectangle(
                    x + sh, y + sh, x + w + sh, y + h + sh,
                    fill=kit.INK, outline="", tags=tags
                )
        if rpts:
            self.poly(rpts, fill=fill or "", outline=outline or "", width=width if outline else 0, tags=tags, smooth=True)
        else:
            self.cv.create_rectangle(
                x, y, x + w, y + h,
                fill=fill or "", outline=outline or "",
                width=width if outline else 0, tags=tags
            )

    def oval(self, x, y, rx, ry, fill="", outline="", width=2, tags="dyn", stipple=None, *_args, **_kwargs):
        kw = {
            "fill": fill or "",
            "outline": outline or "",
            "width": width if outline else 0,
            "tags": tags,
        }
        if stipple:
            kw["stipple"] = stipple
        self.cv.create_oval(x - rx, y - ry, x + rx, y + ry, **kw)

    def poly(self, pts, fill="", outline="", width=2, tags="dyn", smooth=False, *_args, **_kwargs):
        if not pts:
            return
        flat = [coord for pt in pts for coord in pt]
        self.cv.create_polygon(
            flat,
            fill=fill or "",
            outline=outline or "",
            width=width if outline else 0,
            smooth=bool(smooth),
            tags=tags
        )

    def union(self, shapes, fill="", width=2, tags="dyn", outline=kit.INK, *_args, **_kwargs):
        """Signature art.py: P.union([(pts, smooth), ...], fill, ow, tags)."""
        parsed = []
        for item in shapes or []:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (bool, int)):
                parsed.append((item[0], bool(item[1])))
            else:
                parsed.append((item, False))
        if outline and width:
            for pts, sm in parsed:
                self.poly(pts, fill=outline, outline=outline, width=width, tags=tags, smooth=sm)
        if fill:
            for pts, sm in parsed:
                self.poly(pts, fill=fill, outline="", width=0, tags=tags, smooth=sm)

    def line(self, pts, fill="#ffffff", width=2, tags="dyn", smooth=False, dash=None, cap="round", *_args, **_kwargs):
        if len(pts) >= 2:
            flat = [coord for pt in pts for coord in pt]
            kw = {
                "fill": fill or "#ffffff",
                "width": width,
                "smooth": bool(smooth),
                "capstyle": cap if cap in ("round", "butt", "projecting") else "round",
                "joinstyle": "round",
                "tags": tags,
            }
            if dash:
                kw["dash"] = dash
            self.cv.create_line(flat, **kw)

    def limb(self, pts, color, w, ow=2, tags="dyn", smooth=False, *_args, **_kwargs):
        """Menggambar kaki/lengan/ekor tebal dengan garis tepi tinta di luar."""
        if len(pts) < 2:
            return
        self.line(pts, fill=kit.INK, width=w + ow * 2, tags=tags, smooth=smooth, cap="round")
        self.line(pts, fill=color, width=w, tags=tags, smooth=smooth, cap="round")

    def text(self, x, y, txt, size=18, fill="#1b1429", anchor="center", width=None, justify="left", tags="dyn", *_args, **_kwargs):
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

    def stext(self, x, y, txt, size=24, fill="#ffe066", outline="#1b1429", off=3, tags="dyn", *_args, **_kwargs):
        self.text(x + off, y + off, txt, size, outline, "center", tags=tags)
        self.text(x, y, txt, size, fill, "center", tags=tags)

    def bar(self, x, y, w, h, ratio, color="#6ef2c2", tags="dyn", *_args, **_kwargs):
        ratio = max(0.0, min(1.0, float(ratio)))
        self.rect(x, y, w, h, fill=kit.CREAM, outline=kit.INK, width=3, tags=tags, r=h / 2)
        if ratio > 0:
            iw = max(h - 6, (w - 6) * ratio)
            self.rect(x + 3, y + 3, min(w - 6, iw), max(4, h - 6), fill=color, outline="", tags=tags, r=(h - 6) / 2)

    def star(self, cx, cy, r, fill="#ffe066", outline="#1b1429", width=2, tags="dyn", *_args, **_kwargs):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags)

    def sparkle(self, cx, cy, r, fill="#ffe066", outline="#1b1429", width=2, tags="dyn", *_args, **_kwargs):
        pts = [
            (cx, cy - r), (cx + r * 0.28, cy - r * 0.28),
            (cx + r, cy), (cx + r * 0.28, cy + r * 0.28),
            (cx, cy + r), (cx - r * 0.28, cy + r * 0.28),
            (cx - r, cy), (cx - r * 0.28, cy - r * 0.28),
        ]
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags)

    def heart(self, cx, cy, r, fill="#ff4fa3", outline="#1b1429", width=2, tags="dyn", *_args, **_kwargs):
        pts = []
        for i in range(24):
            a = (i / 24.0) * math.tau
            hx = 16 * (math.sin(a) ** 3)
            hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            pts.append((cx + (hx / 16.0) * r, cy + (hy / 16.0) * r))
        self.poly(pts, fill=fill, outline=outline, width=width, tags=tags, smooth=True)

    def hearts_row(self, x, y, count, total=6, size=14, gap=6, tags="dyn", *_args, **_kwargs):
        for i in range(total):
            col = kit.HOT if i < count else kit.GRAY
            self.heart(x + i * (size + gap) + size * 0.5, y + size * 0.5, size * 0.5, col, kit.INK, 2, tags=tags)

    def window(self, x, y, w, h, title="WINDOW.exe", header_col=kit.PINK, body_col=kit.CREAM, sub="", tags="dyn", *_args, **_kwargs):
        bar_h = 34
        self.rect(x, y, w, h, fill=body_col, outline=kit.INK, width=4, tags=tags, sh=6)
        self.rect(x, y, w, bar_h, fill=header_col, outline=kit.INK, width=4, tags=tags)
        label = sub or title
        if label:
            self.text(x + 14, y + bar_h / 2, label, 16, kit.INK, "w", tags=tags)
        self.rect(x + w - 26, y + 8, 18, 18, fill=kit.HOT, outline=kit.INK, width=2, tags=tags)
        return x, y + bar_h, w, h - bar_h


# ----------------------------------------------------------------------
# LOGIKA GAME (DANA DARURAT + XP/LEVEL + BOSS WISHLIST)
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
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

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
            return "GAME OVER", kit.RED
        if r >= 0.6:
            return "SEHAT", kit.GREEN
        if r >= 0.3:
            return "WASPADA", kit.YELLOW
        return "KRITIS", kit.RED

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
        self.data["log"] = self.data["log"][-200:]

    def _gain_xp(self, amount):
        events = []
        d = self.data
        d["xp"] += amount
        while d["xp"] >= 100 * d["level"]:
            d["xp"] -= 100 * d["level"]
            d["level"] += 1
            self._log("levelup", f"LEVEL UP! Sekarang Lv.{d['level']} - {self.title()}")
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
            self._log("heal", f"+{kit.rupiah(jumlah)} ke Dana Darurat ({ket or 'menabung'}) | +{xp} XP")
        else:
            boss = self.find_boss(boss_id)
            boss["terkumpul"] += jumlah
            self._log("boss", f"Serang {boss['nama']}: {kit.rupiah(jumlah)} ({ket or 'menabung'}) | +{xp} XP")
            if boss["terkumpul"] >= boss["harga"] and not boss["defeated"]:
                boss["defeated"] = True
                xp += 150
                self._log("boss", f"BOSS DEFEATED: {boss['nama']}! Bonus +150 XP")
                events.append(("boss_defeated", boss))
        events += self._gain_xp(xp)
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
        self._log("info", f"Boss baru muncul: {nama} ({kit.rupiah(harga)})")
        self.save()

    def remove_boss(self, boss_id):
        boss = self.find_boss(boss_id)
        self.data["bosses"].remove(boss)
        self._log("info", f"Boss {boss['nama']} dihapus dari wishlist")
        self.save()


# ----------------------------------------------------------------------
# HUB Y2K INTERAKTIF (TABUNG, JAJAN, BOSS WISHLIST, CUSTOM HERO)
# ----------------------------------------------------------------------
class HubY2K(kit.Screen):
    name = "hub"

    def enter(self, **_kw):
        super().enter()
        self.selected_boss_id = None
        self.hero_pose = "idle"
        self.pose_timer = 0.0
        self.speech_text = ""
        self.speech_timer = 0.0
        self.parts = kit.Particles()

    def update(self, dt):
        super().update(dt)
        self.parts.update(dt)
        if self.pose_timer > 0:
            self.pose_timer = max(0.0, self.pose_timer - dt)
            if self.pose_timer == 0:
                self.hero_pose = "idle"
        if self.speech_timer > 0:
            self.speech_timer = max(0.0, self.speech_timer - dt)

    def trigger_reaction(self, pose, say, cols):
        self.hero_pose = pose
        self.pose_timer = 1.4
        self.speech_text = say
        self.speech_timer = 2.2
        self.parts.spawn(175, 290, "star", cols, 14, 240, 150, 480, 1.0, 10)

    def draw_static(self):
        art.y2k_bg(self.P, "#ffb3da", "#b9a2ff", seed=4)
        art.taskbar(self.P)

    def on_key(self, key, _ch):
        if key == "Escape":
            self.app.goto("title")
            return True
        return False

    def draw(self):
        P = self.P
        g, d = self.app.game, self.app.game.data
        self.hits = []

        # Top bar aksi utama
        P.window(24, 18, 1232, 86, "SAVEQUEST_HUB.exe", kit.PINK, kit.CREAM, tags="dyn")
        self.button(40, 56, 175, 38, "+ TABUNG", kit.MINT, self.open_save, 16)
        self.button(227, 56, 175, 38, "- JAJAN", kit.RED, self.open_spend, 16)
        self.button(414, 56, 175, 38, "+ BOSS", kit.SKY, self.open_add_boss, 16)
        self.button(601, 56, 195, 38, "CUSTOM HERO", kit.LILAC, lambda: self.app.goto("creator"), 15)
        self.button(808, 56, 185, 38, "PENGATURAN", kit.YELLOW, self.open_settings, 15)
        self.button(1005, 56, 115, 38, "RESET", kit.GRAY, self.open_reset, 15)
        self.button(1132, 56, 108, 38, "TITLE", kit.ORANGE, lambda: self.app.goto("title"), 15)

        # Panel Kiri: Hero, Potion Dana Darurat & Status
        P.window(24, 118, 580, 550, "HERO_STATUS.exe", kit.SKY, kit.CREAM, tags="dyn")
        P.rect(44, 164, 540, 224, "#bfeaff", kit.INK, 3, "dyn", r=14)
        art.draw_clouds(P, self.t)

        char_cfg = dict(d.get("char") or {})
        for k in art.OPT:
            char_cfg.setdefault(k, art.DEFAULT_IDX[k])
        art.draw_chibi(P, 175, 372, 168, char_cfg, self.t, self.hero_pose, 1)
        if self.speech_timer > 0 and self.speech_text:
            art.draw_speech(P, 205, 196, self.speech_text, 19, kit.WHITE)

        # Botol Potion Dana Darurat di kanan panggung
        art.draw_potion(P, 335, 368, 125, g.hp_ratio(), kit.HOT, self.t)
        P.text(335, 226, "POTION HP", 13, kit.INK)

        # Kartu Target Boss
        bosses_active = [b for b in d["bosses"] if not b["defeated"]]
        if bosses_active:
            target_b = next((b for b in bosses_active if b["id"] == self.selected_boss_id), bosses_active[0])
            P.rect(404, 240, 164, 96, kit.LILAC, kit.INK, 3, "dyn", r=12, sh=4)
            P.text(486, 262, "TARGET BOSS", 13, kit.INK)
            P.text(486, 288, target_b["nama"][:15], 15, kit.INK)
            P.text(486, 314, kit.rupiah(target_b["harga"]), 13, kit.INK)

        status, scol = g.status()
        P.text(44, 408, f"{d['nama'].upper()} · Lv.{d['level']} [{g.title()}]", 19, kit.INK, "w")
        P.text(44, 436, f"HP DANA DARURAT ({g.hp_percent()}% · {status})", 15, scol, "w")
        P.bar(44, 454, 540, 26, g.hp_ratio(), kit.GREEN if g.hp_ratio() >= 0.6 else (kit.YELLOW if g.hp_ratio() >= 0.3 else kit.RED))
        P.text(44, 492, f"Saldo: {kit.rupiah(d['saldo'])} / {kit.rupiah(d['target'])}", 15, kit.INK, "w")

        P.text(44, 520, f"XP: {d['xp']} / {g.xp_needed()}", 15, kit.INK, "w")
        P.bar(44, 538, 540, 20, d["xp"] / max(1, g.xp_needed()), kit.BLUE)

        P.text(44, 574, "BATTLE LOG TERBARU:", 14, kit.INK, "w")
        recent = list(reversed(d["log"][-3:]))
        if not recent:
            P.text(44, 598, "Belum ada transaksi. Klik + TABUNG atau - JAJAN!", 13, "#6f6580", "w")
        else:
            for idx, item in enumerate(recent):
                P.text(44, 598 + idx * 22, f"[{item['waktu']}] {item['teks'][:58]}", 13, kit.INK, "w")

        # Panel Kanan: Boss Wishlist Gadget
        P.window(620, 118, 636, 550, "BOSS_WISHLIST.exe", kit.LILAC, kit.CREAM, tags="dyn")
        if not d["bosses"]:
            P.text(938, 355, "Belum ada Boss Wishlist.\nKlik '+ BOSS' di atas untuk menambah gadget!", 18, "#6f6580", "center", justify="center")
        else:
            for i, b in enumerate(d["bosses"][:5]):
                by = 166 + i * 96
                prog = min(1.0, b["terkumpul"] / b["harga"]) if b["harga"] else 1.0
                P.rect(640, by, 596, 86, kit.WHITE, kit.INK, 3, "dyn", r=12, sh=3)
                tag_txt = " [DEFEATED]" if b["defeated"] else ""
                P.text(654, by + 18, f"{b['nama']}{tag_txt}", 16, kit.INK, "w")
                P.text(654, by + 38, f"{kit.rupiah(b['terkumpul'])} / {kit.rupiah(b['harga'])} ({int(prog * 100)}%)", 13, "#5a4f6e", "w")
                P.bar(654, by + 54, 380, 20, prog, kit.GOLD if b["defeated"] else kit.HOT)
                if not b["defeated"]:
                    self.button(1048, by + 16, 84, 28, "SERANG", kit.MINT, lambda bid=b["id"]: self.open_save(bid), 13)
                self.button(1140, by + 16, 82, 28, "HAPUS", kit.GRAY, lambda bid=b["id"]: self.remove_boss(bid), 12)

        self.parts.draw(P)

    def open_save(self, boss_id=None):
        bosses = [b for b in self.app.game.data["bosses"] if not b["defeated"]]
        labels = ["Dana Darurat (HP)"] + [f"Boss: {b['nama']}" for b in bosses]
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
                self.trigger_reaction("attack", "zhammm! SERANG!", [kit.YELLOW, kit.SKY, kit.WHITE])
            else:
                self.trigger_reaction("cheer", "yaayy^^ +HP!", [kit.MINT, kit.YELLOW, kit.PINK])
            ev = self.app.game.add_saving(r["jumlah"], r["ket"], target_id)
            self.app.show_events(ev)

        self.app.dialog = Dialog(
            self.app, "TABUNG (HEAL)", fields, "HEAL!", kit.MINT, on_ok,
            "Menabung menambah HP Dana Darurat, XP, atau menyerang Boss."
        )

    def open_spend(self):
        def on_ok(r):
            sfx.play("hit")
            self.trigger_reaction("hurt", "bhoom!! -HP!", [kit.RED, kit.ORANGE, kit.YELLOW])
            ev = self.app.game.add_spending(r["jumlah"], r["ket"])
            self.app.show_events(ev)

        self.app.dialog = Dialog(
            self.app, "JAJAN IMPULSIF (DAMAGE)",
            [
                {"key": "jumlah", "label": "Nominal jajan", "kind": "money", "value": "25000", "hint": "mis. 25000"},
                {"key": "ket", "label": "Keterangan jajan", "kind": "text", "value": "Jajan impulsif"},
            ],
            "TERIMA DAMAGE", kit.RED, on_ok,
            "Jajan impulsif menurunkan HP Dana Darurat dan XP."
        )

    def open_add_boss(self):
        def on_ok(r):
            self.app.game.add_boss(r["nama"][:24], r["harga"])
            self.app.toast("Boss wishlist ditambahkan!", kit.SKY)

        self.app.dialog = Dialog(
            self.app, "TAMBAH BOSS WISHLIST",
            [
                {"key": "nama", "label": "Nama gadget / barang", "kind": "text", "required": True, "hint": "Mechanical Keyboard"},
                {"key": "harga", "label": "Harga target", "kind": "money", "value": "1000000", "hint": "mis. 1000000"},
            ],
            "MUNCULKAN", kit.SKY, on_ok,
            "Kumpulkan tabungan untuk mengalahkan Boss wishlist."
        )

    def remove_boss(self, boss_id):
        self.app.game.remove_boss(boss_id)
        if self.selected_boss_id == boss_id:
            self.selected_boss_id = None
        self.app.toast("Boss dihapus.", kit.GRAY)

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
            self.app, "PENGATURAN HERO & DANA DARURAT",
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
# APLIKASI UTAMA (tk.Tk + LOOP + ROUTER SCREEN + DIALOG/POPUP)
# ----------------------------------------------------------------------
class SaveQuestApp(tk.Tk):
    WIDTH, HEIGHT = 1280, 720

    def __init__(self):
        super().__init__()
        self.title("SaveQuest - Y2K Savings RPG")
        self.configure(bg=kit.INK)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)

        self.cv = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT,
                            bg=kit.CREAM, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        self.P = CanvasPainter(self.cv, self.WIDTH, self.HEIGHT)
        self.game = GameState()
        self.dialog = None
        self.mouse = (0, 0)
        self.mouse_down = False
        self._toast_text = ""
        self._toast_timer = 0.0
        self._toast_color = kit.YELLOW

        self.screens = {
            "title": st.TitleScreen(self),
            "creator": st.CreatorScreen(self),
            "hub": HubY2K(self),
        }
        self.current_screen = self.screens["title"]
        self.current_screen.enter(boot=True)
        self.current_screen.draw_static()

        self.cv.bind("<Motion>", self._on_motion)
        self.cv.bind("<ButtonPress-1>", self._on_press)
        self.cv.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<KeyPress>", self._on_key)

        self._last_time = time.perf_counter()
        self._loop()

    def goto(self, name, **kw):
        self.cv.delete("all")
        self.current_screen = self.screens[name]
        self.current_screen.enter(**kw)
        self.current_screen.draw_static()

    def start_game(self):
        if not self.game.data.get("setup_done"):
            self.goto("creator", first=True)
        else:
            self.goto("hub")

    def quit_app(self):
        self.destroy()

    def toast(self, msg, color=kit.YELLOW, duration=2.4):
        self._toast_text = msg
        self._toast_color = color
        self._toast_timer = duration

    def show_events(self, events):
        for kind, payload in events:
            if kind == "boss_defeated":
                self.dialog = Popup(
                    self, "BOSS DEFEATED!",
                    f"Target {payload['nama']} tercapai! Bonus +150 XP.",
                    art=None, color=kit.GOLD, btn="MANTAP!", sound="lvl"
                )
            elif kind == "level_up":
                self.dialog = Popup(
                    self, "LEVEL UP!",
                    f"Naik ke Lv.{payload}! Gelar: {self.game.title()}.",
                    art=None, color=kit.YELLOW, btn="LANJUT", sound="lvl"
                )
            elif kind == "game_over":
                self.dialog = Popup(
                    self, "GAME OVER",
                    "Dana Darurat habis! Ayo mulai menabung lagi.",
                    art=None, color=kit.RED, btn="BANGKIT", sound="lvl"
                )

    def _on_motion(self, e):
        self.mouse = (e.x, e.y)

    def _on_press(self, e):
        self.mouse = (e.x, e.y)
        self.mouse_down = True
        if self.dialog is not None:
            self.dialog.click(e.x, e.y)
            return
        self.current_screen.click(e.x, e.y)

    def _on_release(self, e):
        self.mouse = (e.x, e.y)
        self.mouse_down = False

    def _on_key(self, e):
        if self.dialog is not None:
            self.dialog.on_key(e.keysym, e.char)
            return
        self.current_screen.on_key(e.keysym, e.char)

    def _loop(self):
        now = time.perf_counter()
        dt = min(0.05, max(0.001, now - self._last_time))
        self._last_time = now

        if self._toast_timer > 0:
            self._toast_timer = max(0.0, self._toast_timer - dt)

        self.current_screen.update(dt)
        self.cv.delete("dyn")
        self.current_screen.hits = []
        self.current_screen.draw()

        if self.dialog is not None:
            self.dialog.draw(dt)

        if self._toast_timer > 0 and self._toast_text:
            self.P.rect(340, 26, 600, 42, self._toast_color, kit.INK, 3, "dyn", r=16, sh=4)
            self.P.text(640, 47, self._toast_text, 16, kit.INK, tags="dyn")

        self.after(16, self._loop)


if __name__ == "__main__":
    SaveQuestApp().mainloop()