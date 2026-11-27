# -*- coding: utf-8 -*-
"""
SaveQuest - Simulator Tabungan "Dana Darurat & Wishlist Gadget"
Tugas Akhir Teknologi Informasi

Konsep: gamifikasi menabung ala game RPG.
  - HP Bar      : kesehatan dompet (saldo Dana Darurat dibanding targetnya)
  - Menabung    : HEAL  -> HP naik, dapat XP
  - Jajan       : DAMAGE -> HP turun, XP dipotong (penalti)
  - Boss        : tiap barang wishlist gadget adalah boss. Tabung = serang boss.
  - Level & XP  : makin rajin menabung, makin tinggi gelar karaktermu

Dibuat dengan Python + tkinter (tanpa library tambahan).
Jalankan dengan:  python savequest.py
"""

import json
import math
import os
import random
import re
import time
import tkinter as tk
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "savedata.json")

# TEMA WARNA & FONT (gaya pixel / retro game)

C = {
    "bg": "#1b1f3b",
    "panel": "#2a2f5a",
    "panel_dark": "#14172e",
    "border": "#0b0d1f",
    "text": "#f5f0e1",
    "muted": "#9aa3d6",
    "yellow": "#ffcc33",
    "yellow_d": "#c98f00",
    "red": "#e8433f",
    "red_d": "#9c1f1f",
    "green": "#4cc95c",
    "green_d": "#2a8a38",
    "blue": "#3f8fe8",
    "blue_d": "#1f5aa6",
    "pink": "#ff6fae",
    "pink_d": "#b53a76",
    "gray": "#6b7090",
    "gray_d": "#3f4263",
}
FONT_NAME = "Courier New"


def pf(size):
    """Font tebal ala terminal/pixel."""
    return (FONT_NAME, size, "bold")


# ----------------------------------------------------------------------
# SPRITE PIXEL ART (digambar per kotak di Canvas)
# Huruf = kode warna, titik = transparan
# ----------------------------------------------------------------------
HEART = [
    "..KKK.KKK..",
    ".KRRRKRRRK.",
    "KRWWRRRRRRK",
    "KRWRRRRRRRK",
    "KRRRRRRRRRK",
    ".KRRRRRRRK.",
    "..KRRRRRK..",
    "...KRRRK...",
    "....KRK....",
    ".....K.....",
]
COIN = [
    "..KKKK..",
    ".KYYYYK.",
    "KYYWYYYK",
    "KYWYYDYK",
    "KYYYYDYK",
    "KYYYDDYK",
    ".KYYYYK.",
    "..KKKK..",
]
SKULL = [
    ".KKKKKKK.",
    "KWWWWWWWK",
    "KWWWWWWWK",
    "KWKKWKKWK",
    "KWKKWKKWK",
    "KWWWKWWWK",
    ".KWWWWWK.",
    ".KWKWKWK.",
    "..KKKKK..",
]
STAR = [
    "....K....",
    "...KYK...",
    "...KYK...",
    "KKKKYKKKK",
    "KYYYYYYYK",
    ".KYYYYYK.",
    ".KYYYYYK.",
    "KYYKKKYYK",
    "KKK...KKK",
]
MONSTER = [
    "KK.......KK",
    "KRK.....KRK",
    ".KRKKKKKRK.",
    ".KRRRRRRRK.",
    "KRWKRRRKWRK",
    "KRRRRRRRRRK",
    "KRRKWKWKRRK",
    ".KRRKKKRRK.",
    "..KKRRRKK..",
    "....KKK....",
]
HERO = [
    "...KKKK...",
    "..KBBBBK..",
    ".KBBBBBBK.",
    ".KSSSSSSK.",
    ".KSKSSKSK.",
    ".KSSSSSSK.",
    "..KSSSSK..",
    ".KKRRRRKK.",
    "KRRRRRRRRK",
    "KRKRRRRKRK",
    "KSKRRRRKSK",
    ".KKRKKRKK.",
    "..KBKKBK..",
    "..KKK.KKK.",
]

PAL = {
    "K": C["border"],
    "W": "#ffffff",
    "Y": C["yellow"],
    "D": C["yellow_d"],
    "R": C["red"],
    "B": C["blue"],
    "S": "#f2c79b",
    "G": C["green"],
}
PAL_EMPTY_HEART = {"K": C["border"], "R": "#3a3f6a", "W": "#3a3f6a"}

BOSS_COLORS = ["#9b59d0", "#3fb26b", "#e8833f", "#3f8fe8", "#d9467a"]
TITLES = [
    "Rookie Saver",
    "Coin Collector",
    "Budget Knight",
    "Wealth Mage",
    "Gold Paladin",
    "Dragon Hoarder",
    "Legendary Tycoon",
]


def draw_sprite(canvas, x, y, rows, palette, scale, tags=None):
    """Gambar sprite pixel art ke canvas."""
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            color = palette.get(ch)
            if not color:
                continue
            kw = {"tags": tags} if tags else {}
            canvas.create_rectangle(
                x + c * scale, y + r * scale,
                x + (c + 1) * scale, y + (r + 1) * scale,
                fill=color, outline="", **kw
            )


# ----------------------------------------------------------------------
# FUNGSI BANTU
# ----------------------------------------------------------------------
def rupiah(n):
    return "Rp " + f"{int(n):,}".replace(",", ".")


def parse_rupiah(text):
    """'50.000', 'Rp 50000', '50,000' -> 50000. Return None jika kosong."""
    digits = re.sub(r"\D", "", text or "")
    return int(digits) if digits else None


def lighten(hex_color, amt=0.3):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * amt)
    g = int(g + (255 - g) * amt)
    b = int(b + (255 - b) * amt)
    return f"#{r:02x}{g:02x}{b:02x}"


# ----------------------------------------------------------------------
# LOGIKA GAME (terpisah dari tampilan supaya mudah dibaca & diuji)
# ----------------------------------------------------------------------
class GameState:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.data = self.default()
        self.load()

    @staticmethod
    def default():
        return {
            "nama": "Hero",
            "target": 5_000_000,   # target dana darurat
            "saldo": 0,            # saldo dana darurat sekarang
            "level": 1,
            "xp": 0,
            "bosses": [],          # wishlist gadget
            "log": [],             # riwayat transaksi
            "setup_done": False,
        }

    # ---------- penyimpanan ----------
    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                saved = json.load(fh)
            self.data.update(saved)
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

    # ---------- info status ----------
    def hp_ratio(self):
        t = self.data["target"]
        if t <= 0:
            return 0.0
        return max(0.0, min(1.0, self.data["saldo"] / t))

    def hp_percent(self):
        return int(self.hp_ratio() * 100)

    def status(self):
        r = self.hp_ratio()
        if self.data["saldo"] <= 0:
            return "GAME OVER", C["red"]
        if r >= 0.6:
            return "SEHAT", C["green"]
        if r >= 0.3:
            return "WASPADA", C["yellow"]
        return "KRITIS", C["red"]

    def xp_needed(self):
        return 100 * self.data["level"]

    def title(self):
        return TITLES[min(self.data["level"] - 1, len(TITLES) - 1)]

    # ---------- log ----------
    def _log(self, tipe, teks):
        self.data["log"].append({
            "waktu": datetime.now().strftime("%d/%m %H:%M"),
            "tipe": tipe,
            "teks": teks,
        })
        self.data["log"] = self.data["log"][-200:]

    # ---------- XP & level ----------
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

    # ---------- aksi utama ----------
    def add_saving(self, jumlah, ket="", boss_id=None):
        """Menabung = HEAL. Bisa ke Dana Darurat (boss_id=None) atau menyerang boss."""
        d = self.data
        events = []
        crit = jumlah >= 0.1 * d["target"]
        xp = 5 + jumlah // 5000
        if crit:
            xp *= 2
        tag = " CRITICAL HEAL!" if crit else ""

        if boss_id is None:
            d["saldo"] += jumlah
            self._log("heal", f"+{rupiah(jumlah)} ke Dana Darurat ({ket or 'menabung'}) | +{xp} XP{tag}")
        else:
            boss = self.find_boss(boss_id)
            boss["terkumpul"] += jumlah
            self._log("boss", f"Serang {boss['nama']}: {rupiah(jumlah)} ({ket or 'menabung'}) | +{xp} XP{tag}")
            if boss["terkumpul"] >= boss["harga"] and not boss["defeated"]:
                boss["defeated"] = True
                xp += 150
                self._log("boss", f"BOSS DEFEATED: {boss['nama']}! Bonus +150 XP")
                events.append(("boss_defeated", boss))

        events += self._gain_xp(xp)
        self.save()
        return events

    def add_spending(self, jumlah, ket=""):
        """Jajan impulsif = DAMAGE + penalti XP."""
        d = self.data
        events = []
        before = d["saldo"]
        d["saldo"] = max(0, d["saldo"] - jumlah)
        crit = jumlah >= 0.1 * d["target"]
        loss = 3 + jumlah // 5000
        if crit:
            loss *= 2
        d["xp"] = max(0, d["xp"] - loss)
        tag = " CRITICAL HIT!" if crit else ""
        self._log("damage", f"-{rupiah(jumlah)} jajan ({ket or 'impulsif'}) | -{loss} XP{tag}")
        if before > 0 and d["saldo"] == 0:
            self._log("damage", "HP habis! GAME OVER")
            events.append(("game_over", None))
        self.save()
        return events

    # ---------- wishlist / boss ----------
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
        self._log("info", f"Boss baru muncul: {nama} ({rupiah(harga)})")
        self.save()

    def remove_boss(self, boss_id):
        boss = self.find_boss(boss_id)
        self.data["bosses"].remove(boss)
        self._log("info", f"Boss {boss['nama']} dihapus dari wishlist")
        self.save()


# ----------------------------------------------------------------------
# KOMPONEN UI PIXEL
# ----------------------------------------------------------------------
class PixelBar(tk.Canvas):
    """Bar bersegmen ala HP bar game."""
    SEGMENTS = 20

    def __init__(self, master, width=300, height=24, color=None, bg=None):
        super().__init__(master, width=width, height=height,
                         bg=bg or C["panel"], highlightthickness=0)
        self.w, self.h = width, height
        self.color = color or C["green"]
        self.ratio = 0.0
        self.draw()

    def set(self, ratio, color=None):
        self.ratio = max(0.0, min(1.0, ratio))
        if color:
            self.color = color
        self.draw()

    def draw(self, override=None):
        self.delete("all")
        w, h = self.w, self.h
        self.create_rectangle(0, 0, w, h, fill=C["border"], outline="")
        self.create_rectangle(3, 3, w - 3, h - 3, fill=C["panel_dark"], outline="")
        seg_w = (w - 10) / self.SEGMENTS
        filled = math.ceil(self.ratio * self.SEGMENTS - 1e-9) if self.ratio > 0 else 0
        col = override or self.color
        light = lighten(col, 0.4)
        for i in range(filled):
            x0 = 5 + i * seg_w
            x1 = x0 + seg_w - 2
            self.create_rectangle(x0, 5, x1, h - 5, fill=col, outline="")
            self.create_rectangle(x0, 5, x1, 5 + max(2, (h - 10) // 3), fill=light, outline="")

    def flash(self):
        self.draw(override="#ffffff")
        self.after(120, self.draw)


class PixelButton(tk.Frame):
    """Tombol kotak bergaya game (menekan = turun sedikit)."""

    def __init__(self, master, text, command, color, dark, fg="#ffffff",
                 font_size=11, width=16):
        super().__init__(master, bg=C["border"], padx=3, pady=3, cursor="hand2")
        self.base = tk.Frame(self, bg=dark)
        self.base.pack(fill="x")
        self.lbl = tk.Label(self.base, text=text, bg=color, fg=fg,
                            font=pf(font_size), width=width, pady=5)
        self.lbl.pack(fill="x", pady=(0, 4))
        self.color, self.command = color, command
        for w in (self, self.base, self.lbl):
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<ButtonPress-1>", self._press)
            w.bind("<ButtonRelease-1>", self._release)

    def _enter(self, _e):
        self.lbl.config(bg=lighten(self.color, 0.2))

    def _leave(self, _e):
        self.lbl.config(bg=self.color)
        self.lbl.pack_configure(pady=(0, 4))

    def _press(self, _e):
        self.lbl.pack_configure(pady=(4, 0))

    def _release(self, _e):
        self.lbl.pack_configure(pady=(0, 4))
        if self.command:
            self.command()


class ScrollFrame(tk.Frame):
    """Frame yang bisa di-scroll (untuk daftar boss)."""

    def __init__(self, master, height=300):
        super().__init__(master, bg=C["panel"])
        self.canvas = tk.Canvas(self, bg=C["panel"], highlightthickness=0, height=height)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=C["panel"])
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.win, width=e.width))
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _e):
        self.canvas.bind_all("<MouseWheel>", self._wheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_wheel(self, _e):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _wheel(self, e):
        self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")


def _center_on(win, parent):
    win.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - win.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{max(0, x)}+{max(0, y)}")


def _make_modal(win, parent):
    win.transient(parent)
    _center_on(win, parent)
    try:
        win.wait_visibility()
        win.grab_set()
    except tk.TclError:
        pass
    parent.wait_window(win)


class FormDialog(tk.Toplevel):
    """Form input bergaya game. Hasil ada di .result (dict) atau None jika batal."""

    def __init__(self, parent, title, fields, ok_text="OK",
                 ok_color=None, ok_dark=None, subtitle=""):
        super().__init__(parent)
        self.configure(bg=C["border"], padx=4, pady=4)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.fields = fields
        self.vars = {}

        body = tk.Frame(self, bg=C["panel"], padx=20, pady=16)
        body.pack()
        tk.Label(body, text=title, bg=C["panel"], fg=C["yellow"], font=pf(16)).pack(anchor="w")
        if subtitle:
            tk.Label(body, text=subtitle, bg=C["panel"], fg=C["muted"], font=pf(10),
                     wraplength=400, justify="left").pack(anchor="w", pady=(4, 0))

        first_entry = None
        for fl in fields:
            tk.Label(body, text=fl["label"], bg=C["panel"], fg=C["text"],
                     font=pf(11)).pack(anchor="w", pady=(10, 2))
            var = tk.StringVar(value=fl.get("default", ""))
            self.vars[fl["key"]] = var
            if fl.get("kind") == "choice":
                var.set(fl["choices"][0])
                om = tk.OptionMenu(body, var, *fl["choices"])
                om.config(bg=C["panel_dark"], fg=C["yellow"], font=pf(11), relief="flat",
                          highlightthickness=3, highlightbackground=C["border"],
                          activebackground=C["gray_d"], activeforeground=C["yellow"],
                          anchor="w", width=34)
                om["menu"].config(bg=C["panel_dark"], fg=C["text"], font=pf(11))
                om.pack(fill="x")
            else:
                e = tk.Entry(body, textvariable=var, width=36, font=pf(13),
                             bg=C["panel_dark"], fg=C["yellow"],
                             insertbackground=C["yellow"], relief="flat",
                             highlightthickness=3, highlightbackground=C["border"],
                             highlightcolor=C["yellow_d"])
                e.pack(fill="x", ipady=4)
                if first_entry is None:
                    first_entry = e

        self.err = tk.Label(body, text="", bg=C["panel"], fg=C["red"], font=pf(10),
                            wraplength=400, justify="left")
        self.err.pack(anchor="w", pady=(8, 0))

        btns = tk.Frame(body, bg=C["panel"])
        btns.pack(pady=(10, 0))
        PixelButton(btns, "BATAL", self.destroy, C["gray"], C["gray_d"], width=10).pack(side="left", padx=6)
        PixelButton(btns, ok_text, self._ok, ok_color or C["green"], ok_dark or C["green_d"],
                    width=14).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        if first_entry:
            first_entry.focus_set()
            first_entry.select_range(0, "end")
        _make_modal(self, parent)

    def _ok(self):
        out = {}
        for fl in self.fields:
            val = self.vars[fl["key"]].get().strip()
            kind = fl.get("kind", "text")
            if kind == "money":
                n = parse_rupiah(val)
                if n is None or (n == 0 and not fl.get("allow_zero")):
                    self.err.config(text=f"'{fl['label']}' harus berupa angka lebih dari 0.")
                    return
                out[fl["key"]] = n
            elif kind == "text":
                if fl.get("required") and not val:
                    self.err.config(text=f"'{fl['label']}' tidak boleh kosong.")
                    return
                out[fl["key"]] = val
            else:
                out[fl["key"]] = val
        self.result = out
        self.destroy()


def show_popup(parent, title, message, sprite, palette, color, dark, scale=6, btn="OK"):
    """Popup besar untuk Level Up / Boss Defeated / Game Over."""
    win = tk.Toplevel(parent)
    win.configure(bg=C["border"], padx=4, pady=4)
    win.title(title)
    win.resizable(False, False)
    body = tk.Frame(win, bg=C["panel"], padx=30, pady=20)
    body.pack()
    cw = len(sprite[0]) * scale + 10
    ch = len(sprite) * scale + 10
    cv = tk.Canvas(body, width=cw, height=ch, bg=C["panel"], highlightthickness=0)
    cv.pack()
    draw_sprite(cv, 5, 5, sprite, palette, scale)
    tk.Label(body, text=title, bg=C["panel"], fg=color, font=pf(22)).pack(pady=(8, 4))
    tk.Label(body, text=message, bg=C["panel"], fg=C["text"], font=pf(11),
             wraplength=380, justify="center").pack(pady=(0, 12))
    PixelButton(body, btn, win.destroy, color, dark, width=14,
                fg="#14172e" if color == C["yellow"] else "#ffffff").pack()
    win.bind("<Return>", lambda e: win.destroy())
    win.bind("<Escape>", lambda e: win.destroy())
    _make_modal(win, parent)


# ----------------------------------------------------------------------
# APLIKASI UTAMA
# ----------------------------------------------------------------------
SCENE_W, SCENE_H = 340, 150

HINTS = {
    "SEHAT": "HP dompet aman. Pertahankan, dan serang boss wishlist-mu!",
    "WASPADA": "HP mulai menipis. Tahan jajan dulu dan isi Dana Darurat.",
    "KRITIS": "HP KRITIS! Prioritaskan Dana Darurat sebelum jajan lagi.",
    "GAME OVER": "Dana Darurat habis. Mulai lagi dengan menabung (HEAL).",
}


class SaveQuestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SaveQuest - Simulator Tabungan RPG")
        self.configure(bg=C["bg"])
        self.geometry("1000x740")
        self.resizable(False, False)

        self.game = GameState()
        self._bob_up = False
        self._ft_id = 0
        self.stars = []

        self.build_header()
        self.build_actions()
        mid = tk.Frame(self, bg=C["bg"])
        mid.pack(fill="both", expand=True, padx=12)
        self.build_hero_panel(mid)
        self.build_boss_panel(mid)
        self.build_log_panel()

        self.draw_scene()
        self.refresh()
        self.after(600, self.tick)
        self.after(400, self.first_run)

    # ---------- layout ----------
    def make_panel(self, parent, title):
        outer = tk.Frame(parent, bg=C["border"], padx=4, pady=4)
        inner = tk.Frame(outer, bg=C["panel"])
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=" " + title, bg=C["blue_d"], fg="#ffffff", font=pf(11),
                 anchor="w", pady=3).pack(fill="x")
        body = tk.Frame(inner, bg=C["panel"], padx=10, pady=8)
        body.pack(fill="both", expand=True)
        return outer, body

    def build_header(self):
        h = tk.Canvas(self, width=1000, height=72, bg=C["panel_dark"], highlightthickness=0)
        h.pack(fill="x")
        draw_sprite(h, 24, 18, STAR, PAL, 4)
        draw_sprite(h, 940, 18, STAR, PAL, 4)
        draw_sprite(h, 90, 22, COIN, PAL, 4)
        draw_sprite(h, 880, 22, COIN, PAL, 4)
        h.create_text(503, 28, text="SAVEQUEST", font=pf(30), fill=C["yellow_d"])
        h.create_text(500, 25, text="SAVEQUEST", font=pf(30), fill=C["yellow"])
        h.create_text(500, 56, text="Dana Darurat & Wishlist Gadget", font=pf(11), fill=C["muted"])

    def build_actions(self):
        row = tk.Frame(self, bg=C["bg"])
        row.pack(pady=10)
        PixelButton(row, "+ TABUNG (HEAL)", self.on_save, C["green"], C["green_d"]).pack(side="left", padx=5)
        PixelButton(row, "- JAJAN (DAMAGE)", self.on_spend, C["red"], C["red_d"]).pack(side="left", padx=5)
        PixelButton(row, "+ BOSS BARU", self.on_add_boss, C["blue"], C["blue_d"]).pack(side="left", padx=5)
        PixelButton(row, "PENGATURAN", self.on_settings, C["yellow"], C["yellow_d"],
                    fg="#14172e").pack(side="left", padx=5)
        PixelButton(row, "RESET", self.on_reset, C["gray"], C["gray_d"], width=8).pack(side="left", padx=5)

    def build_hero_panel(self, parent):
        outer, body = self.make_panel(parent, "HERO STATUS")
        outer.pack(side="left", fill="y", padx=(0, 8))

        self.scene = tk.Canvas(body, width=SCENE_W, height=SCENE_H, bg="#12163a",
                               highlightthickness=4, highlightbackground=C["border"])
        self.scene.pack()

        self.lbl_name = tk.Label(body, bg=C["panel"], fg=C["yellow"], font=pf(12))
        self.lbl_name.pack(anchor="w", pady=(8, 2))

        hp_row = tk.Frame(body, bg=C["panel"])
        hp_row.pack(anchor="w", pady=2)
        tk.Label(hp_row, text="HP", bg=C["panel"], fg=C["red"], font=pf(13), width=3).pack(side="left")
        self.hp_bar = PixelBar(hp_row, width=240, height=26)
        self.hp_bar.pack(side="left", padx=4)
        self.lbl_hp = tk.Label(hp_row, bg=C["panel"], fg=C["text"], font=pf(11), width=5)
        self.lbl_hp.pack(side="left")

        self.hearts = tk.Canvas(body, width=5 * 41, height=36, bg=C["panel"], highlightthickness=0)
        self.hearts.pack(anchor="w", pady=2)

        self.lbl_saldo = tk.Label(body, bg=C["panel"], fg=C["text"], font=pf(10))
        self.lbl_saldo.pack(anchor="w")
        self.lbl_status = tk.Label(body, bg=C["panel"], font=pf(12))
        self.lbl_status.pack(anchor="w", pady=(2, 4))

        xp_row = tk.Frame(body, bg=C["panel"])
        xp_row.pack(anchor="w", pady=2)
        tk.Label(xp_row, text="XP", bg=C["panel"], fg=C["blue"], font=pf(13), width=3).pack(side="left")
        self.xp_bar = PixelBar(xp_row, width=240, height=20, color=C["blue"])
        self.xp_bar.pack(side="left", padx=4)
        self.lbl_xp = tk.Label(xp_row, bg=C["panel"], fg=C["text"], font=pf(9), width=8)
        self.lbl_xp.pack(side="left")

        self.lbl_hint = tk.Label(body, bg=C["panel"], fg=C["muted"], font=pf(9),
                                 wraplength=340, justify="left")
        self.lbl_hint.pack(anchor="w", pady=(6, 0))

    def build_boss_panel(self, parent):
        outer, body = self.make_panel(parent, "BOSS WISHLIST GADGET")
        outer.pack(side="left", fill="both", expand=True)
        self.boss_scroll = ScrollFrame(body, height=360)
        self.boss_scroll.pack(fill="both", expand=True)

    def build_log_panel(self):
        outer, body = self.make_panel(self, "BATTLE LOG")
        outer.pack(fill="x", padx=12, pady=(8, 12))
        wrap = tk.Frame(body, bg=C["panel"])
        wrap.pack(fill="x")
        self.log = tk.Text(wrap, height=6, bg=C["panel_dark"], fg=C["text"], font=pf(10),
                           relief="flat", wrap="word", state="disabled",
                           highlightthickness=3, highlightbackground=C["border"])
        sb = tk.Scrollbar(wrap, command=self.log.yview)
        self.log.config(yscrollcommand=sb.set)
        self.log.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")
        self.log.tag_config("heal", foreground=C["green"])
        self.log.tag_config("damage", foreground=C["red"])
        self.log.tag_config("boss", foreground=C["pink"])
        self.log.tag_config("levelup", foreground=C["yellow"])
        self.log.tag_config("info", foreground=C["muted"])

    # ---------- scene animasi ----------
    def draw_scene(self):
        c = self.scene
        c.delete("all")
        W, H = SCENE_W, SCENE_H
        c.create_rectangle(0, 0, W, H, fill="#12163a", outline="")
        rnd = random.Random(7)
        self.stars = []
        for _ in range(25):
            x, y, s = rnd.randint(4, W - 4), rnd.randint(4, 60), rnd.choice((2, 2, 3))
            self.stars.append(c.create_rectangle(x, y, x + s, y + s, fill="#ffffff", outline=""))
        x = 0
        while x < W:
            bw, bh = rnd.randint(28, 50), rnd.randint(40, 90)
            top = H - 30 - bh
            c.create_rectangle(x, top, x + bw, H - 30, fill="#1d2350", outline=C["border"], width=2)
            for wy in range(top + 8, H - 42, 12):
                for wx in range(x + 6, x + bw - 8, 10):
                    if rnd.random() < 0.45:
                        c.create_rectangle(wx, wy, wx + 4, wy + 5, fill="#ffd95a", outline="")
            x += bw + rnd.randint(2, 6)
        c.create_rectangle(0, H - 30, W, H, fill="#3b2f4a", outline="")
        c.create_rectangle(0, H - 30, W, H - 26, fill="#5a4a6a", outline="")
        self.draw_hero()

    def draw_hero(self):
        c = self.scene
        c.delete("hero")
        cx = SCENE_W // 2
        if self.game.data["setup_done"] and self.game.data["saldo"] <= 0:
            draw_sprite(c, cx - 27, SCENE_H - 30 - 54 + 4, SKULL, PAL, 6, tags="hero")
        else:
            pal = dict(PAL)
            if self.game.hp_ratio() < 0.3:
                pal["B"] = C["gray"]
                pal["S"] = "#c9b8a8"
            draw_sprite(c, cx - 20, SCENE_H - 30 - 56 + 4, HERO, pal, 4, tags="hero")
        self._bob_up = False

    def tick(self):
        """Animasi ringan: bintang berkedip & hero naik-turun."""
        for sid in random.sample(self.stars, min(5, len(self.stars))):
            cur = self.scene.itemcget(sid, "fill")
            self.scene.itemconfig(sid, fill="#5a6090" if cur == "#ffffff" else "#ffffff")
        self.scene.move("hero", 0, 2 if self._bob_up else -2)
        self._bob_up = not self._bob_up
        self.after(600, self.tick)

    def float_text(self, text, color):
        c = self.scene
        self._ft_id += 1
        tag = f"ft{self._ft_id}"
        c.create_text(SCENE_W // 2 + 1, 61, text=text, fill="#000000", font=pf(15), tags=(tag, "float"))
        c.create_text(SCENE_W // 2, 60, text=text, fill=color, font=pf(15), tags=(tag, "float"))

        def step(n=0):
            if n >= 30:
                c.delete(tag)
                return
            c.move(tag, 0, -2)
            self.after(35, step, n + 1)
        step()

    def flash_scene(self, color):
        r = self.scene.create_rectangle(0, 0, SCENE_W, SCENE_H, fill=color, outline="",
                                        stipple="gray50")
        self.scene.tag_raise("float")
        self.after(160, lambda: self.scene.delete(r))

    # ---------- refresh tampilan ----------
    def refresh(self):
        g, d = self.game, self.game.data
        status, scolor = g.status()
        ratio = g.hp_ratio()
        hp_color = C["green"] if ratio >= 0.6 else (C["yellow"] if ratio >= 0.3 else C["red"])

        self.lbl_name.config(text=f"{d['nama'].upper()}  Lv.{d['level']}  [{g.title()}]")
        self.hp_bar.set(ratio, hp_color)
        self.lbl_hp.config(text=f"{g.hp_percent()}%")
        self.lbl_saldo.config(text=f"Dana Darurat: {rupiah(d['saldo'])} / {rupiah(d['target'])}")
        self.lbl_status.config(text=f"STATUS: {status}", fg=scolor)
        self.xp_bar.set(d["xp"] / g.xp_needed())
        self.lbl_xp.config(text=f"{d['xp']}/{g.xp_needed()}")
        self.lbl_hint.config(text=HINTS[status])

        self.hearts.delete("all")
        full = math.ceil(ratio * 5 - 1e-9) if ratio > 0 else 0
        for i in range(5):
            pal = PAL if i < full else PAL_EMPTY_HEART
            draw_sprite(self.hearts, 2 + i * 41, 1, HEART, pal, 3)

        self.draw_hero()
        self.refresh_bosses()
        self.refresh_log()

    def refresh_bosses(self):
        inner = self.boss_scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        bosses = self.game.data["bosses"]
        if not bosses:
            cv = tk.Canvas(inner, width=60, height=60, bg=C["panel"], highlightthickness=0)
            cv.pack(pady=(30, 6))
            draw_sprite(cv, 2, 8, MONSTER, dict(PAL, R=C["gray"]), 5)
            tk.Label(inner, text="Belum ada boss.\nKlik '+ BOSS BARU' untuk menambah\nwishlist gadget impianmu!",
                     bg=C["panel"], fg=C["muted"], font=pf(11), justify="center").pack()
            return

        for i, b in enumerate(bosses):
            color = BOSS_COLORS[i % len(BOSS_COLORS)]
            card = tk.Frame(inner, bg=C["border"], padx=3, pady=3)
            card.pack(fill="x", padx=6, pady=4)
            body = tk.Frame(card, bg=C["panel_dark"])
            body.pack(fill="x")

            sp = tk.Canvas(body, width=52, height=48, bg=C["panel_dark"], highlightthickness=0)
            sp.grid(row=0, column=0, rowspan=3, padx=8, pady=6)
            draw_sprite(sp, 4, 4, MONSTER, dict(PAL, R=C["gray"] if b["defeated"] else color), 4)

            title = b["nama"] + ("  [DEFEATED]" if b["defeated"] else "")
            tk.Label(body, text=title, bg=C["panel_dark"],
                     fg=C["yellow"] if b["defeated"] else C["text"],
                     font=pf(12), anchor="w").grid(row=0, column=1, sticky="w")

            progress = min(1.0, b["terkumpul"] / b["harga"]) if b["harga"] else 1.0
            bar = PixelBar(body, width=230, height=18, color=color, bg=C["panel_dark"])
            bar.set(1.0 - progress)
            bar.grid(row=1, column=1, sticky="w")

            tk.Label(body, text=f"{rupiah(b['terkumpul'])} / {rupiah(b['harga'])}  (HP boss {int((1 - progress) * 100)}%)",
                     bg=C["panel_dark"], fg=C["muted"], font=pf(9),
                     anchor="w").grid(row=2, column=1, sticky="w", pady=(0, 4))

            btns = tk.Frame(body, bg=C["panel_dark"])
            btns.grid(row=0, column=2, rowspan=3, padx=8)
            if not b["defeated"]:
                PixelButton(btns, "SERANG", lambda bid=b["id"]: self.on_save(bid),
                            C["green"], C["green_d"], font_size=9, width=7).pack(pady=2)
            PixelButton(btns, "HAPUS", lambda bid=b["id"]: self.on_remove_boss(bid),
                        C["red"], C["red_d"], font_size=9, width=7).pack(pady=2)
            body.grid_columnconfigure(1, weight=1)

    def refresh_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        for e in reversed(self.game.data["log"][-60:]):
            self.log.insert("end", f"[{e['waktu']}] {e['teks']}\n", e["tipe"])
        self.log.config(state="disabled")
        self.log.see("1.0")

    # ---------- aksi pengguna ----------
    def first_run(self):
        if not self.game.data["setup_done"]:
            self.open_setup(first=True)

    def open_setup(self, first=False):
        d = self.game.data
        res = FormDialog(
            self, "SELAMAT DATANG!" if first else "PENGATURAN",
            [
                {"key": "nama", "label": "Nama pahlawan", "default": d["nama"], "required": True},
                {"key": "target", "label": "Target Dana Darurat (Rp)", "kind": "money",
                 "default": str(d["target"])},
                {"key": "saldo", "label": "Saldo Dana Darurat saat ini (Rp)", "kind": "money",
                 "allow_zero": True, "default": str(d["saldo"])},
            ],
            ok_text="MULAI" if first else "SIMPAN",
            ok_color=C["yellow"], ok_dark=C["yellow_d"],
            subtitle=("Atur karaktermu. Rekomendasi dana darurat: 3-6x pengeluaran bulanan."
                      if first else ""),
        ).result
        if res:
            d["nama"] = res["nama"][:16]
            d["target"] = res["target"]
            d["saldo"] = res["saldo"]
        if first:
            d["setup_done"] = True
            self.game._log("info", f"Selamat datang di SaveQuest, {d['nama']}! Petualangan dimulai.")
        self.game.save()
        self.refresh()

    def on_settings(self):
        self.open_setup(first=False)

    def on_save(self, boss_id=None):
        bosses = [b for b in self.game.data["bosses"] if not b["defeated"]]
        labels = ["Dana Darurat (HP)"] + [f"Boss {i + 1}: {b['nama']}" for i, b in enumerate(bosses)]
        ids = [None] + [b["id"] for b in bosses]
        fields = [
            {"key": "jumlah", "label": "Jumlah ditabung (Rp)", "kind": "money"},
            {"key": "ket", "label": "Keterangan (opsional)", "default": "Menabung"},
        ]
        if boss_id is None:
            fields.append({"key": "tujuan", "label": "Tabung ke mana?", "kind": "choice", "choices": labels})
        res = FormDialog(self, "MENABUNG (HEAL)", fields, ok_text="HEAL!",
                         subtitle="Tabungan baru = HP naik + XP bertambah.").result
        if not res:
            return
        if boss_id is None:
            boss_id = ids[labels.index(res["tujuan"])]
        events = self.game.add_saving(res["jumlah"], res["ket"], boss_id)
        self.refresh()
        if boss_id is None:
            self.float_text("+" + rupiah(res["jumlah"]), C["green"])
            self.flash_scene(C["green"])
            self.hp_bar.flash()
        else:
            self.float_text("BOSS HIT!", C["pink"])
            self.flash_scene(C["pink"])
        self.process_events(events)

    def on_spend(self):
        res = FormDialog(
            self, "JAJAN IMPULSIF (DAMAGE)",
            [
                {"key": "jumlah", "label": "Jumlah jajan (Rp)", "kind": "money"},
                {"key": "ket", "label": "Beli apa?", "default": "Jajan impulsif"},
            ],
            ok_text="TERIMA DAMAGE", ok_color=C["red"], ok_dark=C["red_d"],
            subtitle="Jajan impulsif memotong Dana Darurat dan XP-mu.",
        ).result
        if not res:
            return
        events = self.game.add_spending(res["jumlah"], res["ket"])
        self.refresh()
        self.float_text("-" + rupiah(res["jumlah"]), C["red"])
        self.flash_scene(C["red"])
        self.hp_bar.flash()
        self.process_events(events)

    def on_add_boss(self):
        res = FormDialog(
            self, "BOSS BARU",
            [
                {"key": "nama", "label": "Nama gadget impian", "required": True},
                {"key": "harga", "label": "Harga (Rp)", "kind": "money"},
            ],
            ok_text="MUNCULKAN", ok_color=C["blue"], ok_dark=C["blue_d"],
            subtitle="Tiap gadget wishlist menjadi boss. Kumpulkan uang untuk mengalahkannya!",
        ).result
        if res:
            self.game.add_boss(res["nama"][:24], res["harga"])
            self.refresh()

    def on_remove_boss(self, boss_id):
        from tkinter import messagebox
        if messagebox.askyesno("Hapus boss", "Hapus boss ini dari wishlist?\n"
                                             "Uang yang sudah terkumpul tidak akan dihitung lagi."):
            self.game.remove_boss(boss_id)
            self.refresh()

    def on_reset(self):
        from tkinter import messagebox
        if messagebox.askyesno("Reset game", "Semua data (saldo, level, boss, riwayat) akan dihapus.\nLanjut?"):
            self.game.reset()
            self.refresh()
            self.open_setup(first=True)

    def process_events(self, events):
        for kind, payload in events:
            if kind == "boss_defeated":
                show_popup(self, "BOSS DEFEATED!",
                           f"Dana untuk {payload['nama']} sudah terkumpul!\n"
                           "Bonus +150 XP. Beli dengan bijak dan pastikan Dana Darurat tetap aman.",
                           MONSTER, dict(PAL, R=C["gray"]), C["pink"], C["pink_d"], scale=7, btn="MANTAP!")
            elif kind == "level_up":
                show_popup(self, "LEVEL UP!",
                           f"Sekarang kamu Lv.{payload}\nGelar: {self.game.title()}",
                           STAR, PAL, C["yellow"], C["yellow_d"], scale=8, btn="LANJUT")
            elif kind == "game_over":
                show_popup(self, "GAME OVER",
                           "HP habis! Dana Darurat kosong.\nSaatnya bangkit: mulai menabung lagi.",
                           SKULL, PAL, C["red"], C["red_d"], scale=8, btn="BANGKIT")


if __name__ == "__main__":
    SaveQuestApp().mainloop()