# -*- coding: utf-8 -*-
"""screens_title.py - Halaman 1: Opening/Title, Halaman 2: Pembuat Karakter."""
import math
import random

import art
import sfx
from dialog import Dialog, Popup
from kit import (INK, CREAM, PINK, HOT, LILAC, SKY, MINT, YELLOW, GOLD, WHITE, GRAY, GREEN, ORANGE, BLUE,
                 Screen, Particles, lighten, mix)

BOOT = 3.0

CAST = [  # empat tokoh pembuka (original)
    dict(kelas=0, rambut=0, warna_rambut=1, kulit=1, mata=3, baju=0, warna_baju=0, sepatu=0, aksesori=3),
    dict(kelas=3, rambut=2, warna_rambut=2, kulit=0, mata=0, baju=2, warna_baju=2, sepatu=1, aksesori=1),
    dict(kelas=2, rambut=4, warna_rambut=3, kulit=3, mata=4, baju=1, warna_baju=5, sepatu=0, aksesori=0),
    dict(kelas=1, rambut=1, warna_rambut=0, kulit=2, mata=5, baju=3, warna_baju=4, sepatu=2, aksesori=2),
]
CAST_POS = [(130, 300, 1), (305, 250, 1), (975, 250, -1), (1150, 300, -1)]
CAST_SAY = ["Hi!", "Nabung yuk!", "Ayo!", "Semangat!"]
GY = 640

HOWTO = ("TABUNG = HEAL: HP dompet naik + XP.\nJAJAN impulsif = DAMAGE: HP dan XP turun.\n"
         "Wishlist gadget jadi BOSS. Makin mahal, makin sulit.\nJalan-jalan di Arena, kumpulkan bintang, lalu SERANG!")


def bounce(k):
    if k >= 1:
        return 1.0
    if k < 1 / 2.75:
        return 7.5625 * k * k
    if k < 2 / 2.75:
        k -= 1.5 / 2.75
        return 7.5625 * k * k + 0.75
    if k < 2.5 / 2.75:
        k -= 2.25 / 2.75
        return 7.5625 * k * k + 0.9375
    k -= 2.625 / 2.75
    return 7.5625 * k * k + 0.984375


class TitleScreen(Screen):
    name = "title"

    def enter(self, **kw):
        super().enter()
        self.t = 0.0 if kw.get("boot", True) else BOOT + 2
        self.parts = Particles()
        self.hop = [0.0] * 4
        self.say = [0.0] * 4
        self.started = self.t >= BOOT

    def draw_static(self):
        art.draw_meadow(self.P, GY)

    def update(self, dt):
        self.t += dt
        self.parts.update(dt)
        self.hop = [max(0.0, h - dt) for h in self.hop]
        self.say = [max(0.0, s - dt) for s in self.say]
        if self.t >= BOOT and not self.started:
            self.started = True
            sfx.play("boot")
            for _ in range(5):
                self.parts.spawn(640, 200, "confetti", [HOT, YELLOW, MINT, SKY, LILAC], 14, 520, 380, 600, 1.6, 10)

    def has_save(self):
        return self.app.game.data["setup_done"]

    def start(self):
        self.app.start_game()

    def on_key(self, key, ch):
        if self.t >= BOOT and key in ("Return", "space", "KP_Enter"):
            self.start()
            return True
        return False

    def on_click_extra(self, x, y):
        for i, (cx, h, f) in enumerate(CAST_POS):
            if abs(x - cx) < h * 0.28 and GY - h * 1.05 < y < GY:
                self.hop[i], self.say[i] = 0.7, 1.8
                sfx.play("star")
                self.parts.spawn(cx, GY - h * 0.6, "spark", [YELLOW, WHITE, PINK], 8, 220, 80, 500, 0.8, 9)

    def click(self, x, y):
        if self.t < BOOT:
            return False
        if super().click(x, y):
            return True
        self.on_click_extra(x, y)
        return True

    # ---------------------------------------------------------- gambar
    def draw(self):
        if self.t < BOOT:
            self.draw_boot()
            return
        P, t = self.P, self.t - BOOT
        art.draw_clouds(P, self.t)
        for i, (cx, h, f) in enumerate(CAST_POS):
            hop = abs(math.sin(self.hop[i] / 0.7 * math.pi)) * 60 if self.hop[i] > 0 else 0
            pose = "cheer" if self.hop[i] > 0 else "idle"
            art.draw_chibi(P, cx, GY - hop, h, CAST[i], self.t + i * 1.3, pose, f)
            if self.say[i] > 0:
                art.draw_speech(P, cx, GY - h * 1.14, CAST_SAY[i], 22)
        word = "SAVEQUEST"
        cols = [HOT, YELLOW, MINT, SKY, LILAC, HOT, YELLOW, MINT, SKY]
        for i, ch in enumerate(word):
            k = max(0.0, min(1.0, (t - i * 0.07) / 0.55))
            drop = -(1 - bounce(k)) * 420
            P.stext(640 + (i - 4) * 76, 128 + drop + math.sin(self.t * 3 + i * 0.7) * 5, ch, 104, cols[i], INK, 5)
        if t > 0.9:
            P.rect(420, 206, 440, 46, HOT, INK, 4, r=23, sh=5)
            P.text(640, 230, "Dana Darurat & Wishlist Quest", 21, WHITE)
            P.star(448, 229, 11, YELLOW, INK, 2)
            P.star(832, 229, 11, YELLOW, INK, 2)
        if t > 1.2:
            slide = (1 - min(1.0, (t - 1.2) * 3)) * 300
            lab = "LANJUTKAN" if self.has_save() else "MULAI PETUALANGAN"
            if self.button(450 + slide, 288, 380, 78, lab, MINT, self.start, 27):
                pass
            P.poly([(450 + slide + 34, 313), (450 + slide + 34, 341), (450 + slide + 58, 327)], WHITE, INK, 3)
            self.button(450 + slide, 380, 380, 58, "CARA MAIN", YELLOW, self.howto, 23)
            self.button(450 + slide, 450, 182, 52, "SUARA " + ("OFF" if sfx.MUTE else "ON"), SKY, self.toggle_snd, 18)
            if self.has_save():
                self.button(648 + slide, 450, 182, 52, "GAME BARU", PINK, self.newgame, 18)
            else:
                self.button(648 + slide, 450, 182, 52, "KELUAR", PINK, self.app.quit_app, 18)
            if self.has_save():
                self.button(450 + slide, 514, 380, 52, "KELUAR", GRAY, self.app.quit_app, 20)
            if int(self.t * 2) % 2 == 0:
                P.stext(640, 674, "tekan ENTER atau SPASI untuk mulai", 19, WHITE, INK, 2)
        self.parts.draw(P)

    def draw_boot(self):
        P, t = self.P, self.t
        P.cv.create_rectangle(0, 0, P.pw, P.ph, fill=PINK, outline="", tags="dyn")
        for i in range(-4, 22):
            x = (i * 100 + t * 70) % 1600 - 150
            P.line([(x, 0), (x - 320, 720)], lighten(PINK, 0.28), 4)
        bx, by, bw, bh = P.window(270, 130, 740, 440, "", LILAC, CREAM, "savequest.exe/loading")
        P.stext(640, by + 62, "SAVEQUEST", 78, YELLOW, INK, 4)
        prog = min(1.0, t / (BOOT - 0.4))
        P.bar(bx + 60, by + 160, bw - 120, 40, prog, HOT)
        P.text(640, by + 230, "LOADING... %d%%" % int(prog * 100), 24)
        msgs = ["Memuat dompet...", "Memanggil boss wishlist...", "Mengasah pedang tabungan...", "Siap bertualang!"]
        P.text(640, by + 272, msgs[min(3, int(prog * 4))], 20, "#7a6a8a")
        for i in range(8):
            a = t * 1.5 + i * 0.8
            P.sparkle(640 + math.cos(a) * 430, 350 + math.sin(a * 1.3) * 250, 10 + 4 * math.sin(a * 3), [YELLOW, WHITE, MINT, SKY][i % 4], INK, 2)

    # ---------------------------------------------------------- aksi
    def toggle_snd(self):
        sfx.toggle()

    def howto(self):
        self.app.dialog = Popup(self.app, "CARA MAIN", HOWTO, None, SKY, "SIAP!", sound="coin")

    def newgame(self):
        def ok(r):
            if r["yakin"] == 1:
                self.app.game.reset()
                self.app.toast("Data dihapus. Mulai dari awal!", HOT)
        self.app.dialog = Dialog(self.app, "GAME BARU?", [dict(key="yakin", label="Hapus semua progres?", kind="choice",
                                 choices=["Tidak, batal", "Ya, hapus semua"])], "OK", PINK, ok)


# ====================================================================== CREATOR
CLASS_STATS = {"Star Mage": (0.3, 0.5, 0.95), "Siren Bard": (0.4, 0.75, 0.7),
               "Riot Rogue": (0.55, 0.95, 0.4), "Fire Knight": (0.95, 0.4, 0.5)}


class CreatorScreen(Screen):
    name = "creator"

    def enter(self, **kw):
        super().enter()
        g = self.app.game
        self.first = kw.get("first", False)
        self.char = dict(g.data["char"] or {})
        for k in art.OPT:
            self.char.setdefault(k, art.DEFAULT_IDX[k])
        self.nama = g.data["nama"]
        self.parts = Particles()
        self.cheer = 0.0
        self.shown = [0.3, 0.3, 0.3]

    def draw_static(self):
        art.y2k_bg(self.P, "#ffb3da", "#b9a2ff", seed=8)
        art.taskbar(self.P)

    def update(self, dt):
        self.t += dt
        self.cheer = max(0.0, self.cheer - dt)
        self.parts.update(dt)
        tgt = CLASS_STATS[art.opt(self.char, "kelas")[0]]
        self.shown = [s + (g - s) * min(1.0, dt * 8) for s, g in zip(self.shown, tgt)]

    # ---------------------------------------------------------- aksi
    def change(self, key, d):
        art.cycle(self.char, key, d)
        self.cheer = 0.9
        self.parts.spawn(728, 380, "spark", [YELLOW, WHITE, PINK, MINT], 10, 260, 120, 500, 0.8, 9)

    def randomize(self):
        self.char = art.random_char()
        self.cheer = 1.0
        sfx.play("coin")
        self.parts.spawn(728, 380, "star", [YELLOW, PINK, MINT, SKY], 14, 320, 160, 500, 1.0, 10)

    def rename(self):
        def ok(r):
            self.nama = r["nama"][:14]
        self.app.dialog = Dialog(self.app, "NAMA PAHLAWAN", [dict(key="nama", label="Nama karakter", kind="text",
                                 value=self.nama, required=True, maxlen=14)], "SIMPAN", YELLOW, ok)

    def back(self):
        self.app.goto("hub" if self.app.game.data["setup_done"] else "title")

    def finish(self):
        g = self.app.game
        g.data["char"] = dict(self.char)
        g.data["nama"] = self.nama or "Hero"
        g.save()
        if g.data["setup_done"]:
            self.app.toast("Karakter tersimpan!", MINT)
            self.app.goto("hub")
            return

        def ok(r):
            g.data["target"] = r["target"]
            g.data["saldo"] = r["saldo"]
            g.data["setup_done"] = True
            ev = g.unlock_hero()
            self.app.goto("hub")
            self.app.show_events(ev)
        self.app.dialog = Dialog(self.app, "PENGATURAN AWAL", [
            dict(key="target", label="Target dana darurat", kind="money", value="5000000", hint="mis. 5000000"),
            dict(key="saldo", label="Saldo dana darurat saat ini", kind="money", value="0", allow_zero=True)],
            "MULAI!", MINT, ok, "Tips: dana darurat ideal 3-6x pengeluaran bulanan.")

    def on_key(self, key, ch):
        if key in ("Return", "KP_Enter"):
            self.finish()
            return True
        return False

    # ---------------------------------------------------------- gambar
    def arrow(self, x, y, d, cb):
        P = self.P
        self.button(x, y, 40, 44, "", YELLOW, cb)
        hov = self.hover(x, y, 40, 44)
        yy = y - (3 if hov and not self.app.mouse_down else 0) + (4 if hov and self.app.mouse_down else 0)
        cx = x + 20
        P.poly([(cx + 7 * d, yy + 12), (cx - 7 * d, yy + 22), (cx + 7 * d, yy + 32)], INK, INK, 2)

    def draw(self):
        P, ch = self.P, self.char
        cls = art.cls_info(ch)
        cname = art.opt(ch, "kelas")[0]
        # ---- kiri: lemari
        bx, by, bw, bh = P.window(24, 24, 500, 650, "WARDROBE.exe", PINK)
        for i, (key, label) in enumerate(art.ROWS):
            y = by + 12 + i * 62
            P.text(bx + 16, y + 22, label, 17, INK, "w")
            self.arrow(bx + 178, y, -1, lambda k=key: self.change(k, -1))
            self.arrow(bx + 434, y, 1, lambda k=key: self.change(k, 1))
            P.rect(bx + 224, y, 206, 44, WHITE, INK, 3, r=12)
            lab, val = art.opt(ch, key)
            if val.startswith("#"):
                P.oval(bx + 246, y + 22, 12, 12, val, INK, 2.5)
                P.text(bx + 266, y + 23, lab, 18, INK, "w")
            else:
                P.text(bx + 327, y + 23, lab, 18, INK)
        # ---- tengah: panggung
        sx, sy, sw, sh = 548, 24, 360, 650
        P.rect(sx, sy, sw, sh, lighten(cls["col"], 0.35), INK, 4, r=20, sh=7)
        cx, cy = sx + sw / 2, 300
        for i in range(14):
            a = self.t * 0.25 + i * math.tau / 14
            a2 = a + math.tau / 28
            P.poly([(cx, cy), (cx + 560 * math.cos(a), cy + 560 * math.sin(a)), (cx + 560 * math.cos(a2), cy + 560 * math.sin(a2))],
                   lighten(cls["col"], 0.55), "", 0)
        P.rect(sx - 2, sy - 2, 4, 4, "", "", 0)
        P.rect(sx, sy + 560, sw, 90, INK, INK, 4, r=20)
        P.rect(sx, sy + 560, sw, 40, INK, "", 0)
        P.rect(sx, sy, sw, sh, "", INK, 4, r=20)
        for i in range(5):
            a = self.t * 0.8 + i * 1.3
            P.sparkle(sx + 60 + (i * 67) % 250, sy + 70 + 40 * math.sin(a) + i * 60, 10 + 3 * math.sin(a * 2), [YELLOW, WHITE, PINK][i % 3], INK, 2)
        art.draw_chibi(P, cx, sy + 540, 440, ch, self.t, "cheer" if self.cheer > 0 else "idle")
        word = cls["say"][int(self.t / 2.5) % len(cls["say"])]
        art.draw_speech(P, cx + 90, sy + 150, word, 24, WHITE)
        P.text(sx + 22, sy + 580, "ATTACK:", 17, YELLOW, "w")
        P.text(sx + 110, sy + 580, cls["atk"], 19, CREAM, "w")
        P.text(sx + 22, sy + 618, "SPELL:", 17, YELLOW, "w")
        P.text(sx + 110, sy + 618, cls["spell"], 19, CREAM, "w")
        # ---- kanan: kartu karakter
        rx, ry, rw, rh = P.window(924, 24, 332, 650, "CHARACTER.exe", LILAC)
        self.button(rx + 12, ry + 12, rw - 24, 56, self.nama + "  (ubah)", YELLOW, self.rename, 24)
        P.text(rx + 16, ry + 100, "KELAS", 16, "#6f6580", "w")
        P.stext(rx + rw / 2, ry + 132, cname.upper(), 30, cls["col"], INK, 3)
        P.text(rx + 16, ry + 176, "HP", 22, INK, "w")
        P.hearts_row(rx + 56, ry + 177, 6, 6, 15, 4)
        for i, (lab, v) in enumerate(zip(("STRENGTH", "AGILITY", "MAGIC"), self.shown)):
            y = ry + 214 + i * 58
            P.text(rx + 16, y, lab, 17, INK, "w")
            P.bar(rx + 16, y + 14, rw - 32, 22, v, [HOT, MINT, SKY][i])
        yy = ry + 400
        self.button(rx + 12, yy, rw - 24, 54, "ACAK KARAKTER", SKY, self.randomize, 21)
        self.button(rx + 12, yy + 68, rw - 24, 76, "SELESAI!", MINT, self.finish, 32)
        if not self.first or self.app.game.data["setup_done"]:
            self.button(rx + 12, yy + 156, rw - 24, 44, "KEMBALI", GRAY, self.back, 18)
        self.parts.draw(P)