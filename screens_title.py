# -*- coding: utf-8 -*-
"""screens_title.py - Halaman Title & Kustomisasi Karakter Minimalis."""
import art
import sfx
from dialog import Dialog, Popup
from kit import INK, CREAM, PINK, HOT, LILAC, SKY, MINT, YELLOW, WHITE, GRAY, Screen

BOOT = 0.0  # Langsung tampil tanpa animasi loading berat

HOWTO = (
    "1. TABUNG (HEAL): Menambah HP Dana Darurat & XP.\n"
    "2. JAJAN (DAMAGE): Mengurangi HP Dana Darurat & XP.\n"
    "3. BOSS WISHLIST: Target gadget yang bisa diserang dengan tabungan."
)


class TitleScreen(Screen):
    name = "title"

    def enter(self, **_kw):
        super().enter()
        self.hop = 0.0
        self.say = ""

    def draw_static(self):
        # Latar polos pastel minimalis sangat ringan
        self.P.bgfill("#f6f7fb", tags="static")
        self.P.rect(0, 686, 1280, 34, "#eceef6", INK, 1, tags="static")
        self.P.text(1264, 703, "SaveQuest · Minimalist Edition", 14, "#6c7086", "e", tags="static")

    def update(self, dt):
        super().update(dt)
        if self.hop > 0:
            self.hop = max(0.0, self.hop - dt)
            if self.hop == 0:
                self.say = ""
                self.app.mark_dirty()

    def has_save(self):
        return self.app.game.data["setup_done"]

    def start(self):
        self.app.start_game()

    def on_key(self, key, _ch):
        if key in ("Return", "space", "KP_Enter"):
            self.start()
            return True
        return False

    def draw(self):
        P = self.P
        self.hits = []

        # Kartu utama terpusat
        P.window(350, 96, 580, 520, "SAVEQUEST.exe", PINK, WHITE, tags="dyn")
        P.text(640, 184, "SAVEQUEST", 46, INK, "center")
        P.text(640, 224, "Simulator Dana Darurat & Wishlist RPG", 17, "#5c6075", "center")

        # Preview mini karakter pengguna di tengah atas tombol
        char_cfg = dict(self.app.game.data.get("char") or {})
        for k in art.OPT:
            char_cfg.setdefault(k, art.DEFAULT_IDX[k])
        art.draw_chibi(P, 640, 346 - (10 if self.hop > 0 else 0), 106, char_cfg, self.t, "cheer" if self.hop > 0 else "idle", 1)
        if self.say:
            P.text(640, 252, self.say, 14, HOT, "center")
        self.hits.append((595, 250, 90, 100, self._poke_hero))

        lab = "LANJUTKAN" if self.has_save() else "MULAI PETUALANGAN"
        self.button(450, 372, 380, 50, lab, MINT, self.start, 20)
        self.button(450, 434, 380, 44, "CARA MAIN", YELLOW, self.howto, 18)
        self.button(450, 490, 184, 42, "SUARA: " + ("OFF" if sfx.MUTE else "ON"), SKY, self.toggle_snd, 16)

        if self.has_save():
            self.button(646, 490, 184, 42, "GAME BARU", PINK, self.newgame, 16)
            self.button(450, 544, 380, 40, "KELUAR", GRAY, self.app.quit_app, 16)
        else:
            self.button(646, 490, 184, 42, "KELUAR", GRAY, self.app.quit_app, 16)

    def _poke_hero(self):
        self.hop = 0.6
        self.say = "Ayo menabung!"
        sfx.play("star")
        self.app.mark_dirty()

    def toggle_snd(self):
        sfx.toggle()
        self.app.mark_dirty()

    def howto(self):
        self.app.dialog = Popup(self.app, "CARA MAIN", HOWTO, None, SKY, "MENGERTI", sound="coin")

    def newgame(self):
        def ok(r):
            if r["yakin"] == 1:
                self.app.game.reset()
                self.app.toast("Data direset.", PINK)

        self.app.dialog = Dialog(
            self.app, "GAME BARU?",
            [dict(key="yakin", label="Hapus semua progres?", kind="choice", choices=["Batal", "Ya, hapus semua"])],
            "OK", PINK, ok
        )


CLASS_STATS = {
    "Star Mage": (0.3, 0.5, 0.95),
    "Siren Bard": (0.4, 0.75, 0.7),
    "Riot Rogue": (0.55, 0.95, 0.4),
    "Fire Knight": (0.95, 0.4, 0.5),
}


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
        self.cheer = 0.0
        self.shown = list(CLASS_STATS[art.opt(self.char, "kelas")[0]])

    def draw_static(self):
        self.P.bgfill("#f6f7fb", tags="static")
        self.P.rect(0, 686, 1280, 34, "#eceef6", INK, 1, tags="static")
        self.P.text(1264, 703, "Kustomisasi Hero · Esc untuk Kembali", 14, "#6c7086", "e", tags="static")

    def update(self, dt):
        super().update(dt)
        if self.cheer > 0:
            self.cheer = max(0.0, self.cheer - dt)
            if self.cheer == 0:
                self.app.mark_dirty()
        tgt = CLASS_STATS[art.opt(self.char, "kelas")[0]]
        if any(abs(s - g) > 0.01 for s, g in zip(self.shown, tgt)):
            self.shown = [s + (g - s) * min(1.0, dt * 12) for s, g in zip(self.shown, tgt)]
            self.app.mark_dirty()

    def change(self, key, d):
        art.cycle(self.char, key, d)
        self.cheer = 0.5
        sfx.play("click")
        self.app.mark_dirty()

    def randomize(self):
        self.char = art.random_char()
        self.cheer = 0.6
        sfx.play("coin")
        self.app.mark_dirty()

    def rename(self):
        def ok(r):
            self.nama = r["nama"][:14]

        self.app.dialog = Dialog(
            self.app, "NAMA PAHLAWAN",
            [dict(key="nama", label="Nama karakter", kind="text", value=self.nama, required=True, maxlen=14)],
            "SIMPAN", YELLOW, ok
        )

    def back(self):
        self.app.go_back(fallback="hub" if self.app.game.data["setup_done"] else "title")

    def finish(self):
        g = self.app.game
        g.data["char"] = dict(self.char)
        g.data["nama"] = self.nama or "Hero"
        g.save()
        if g.data["setup_done"]:
            self.app.toast("Karakter tersimpan!", MINT)
            self.app.go_back(fallback="hub")
            return

        def ok(r):
            g.data["target"] = r["target"]
            g.data["saldo"] = r["saldo"]
            g.data["setup_done"] = True
            ev = g.unlock_hero()
            self.app.goto("hub")
            self.app.show_events(ev)

        self.app.dialog = Dialog(
            self.app, "PENGATURAN AWAL",
            [
                dict(key="target", label="Target dana darurat", kind="money", value="5000000", hint="mis. 5000000"),
                dict(key="saldo", label="Saldo dana darurat saat ini", kind="money", value="0", allow_zero=True),
            ],
            "MULAI!", MINT, ok, "Dana darurat ideal 3-6x pengeluaran bulanan."
        )

    def on_key(self, key, _ch):
        if key == "Escape":
            self.back()
            return True
        if key in ("Return", "KP_Enter"):
            self.finish()
            return True
        return False

    def draw(self):
        P, ch = self.P, self.char
        self.hits = []
        cls = art.cls_info(ch)
        cname = art.opt(ch, "kelas")[0]

        # Kiri: Wardrobe
        bx, by, _bw, _bh = P.window(24, 24, 500, 646, "WARDROBE", PINK, WHITE)
        for i, (key, label) in enumerate(art.ROWS):
            y = by + 14 + i * 62
            P.text(bx + 18, y + 20, label, 15, INK, "w")
            self.button(bx + 178, y, 40, 40, "<", YELLOW, lambda k=key: self.change(k, -1), 18)
            self.button(bx + 434, y, 40, 40, ">", YELLOW, lambda k=key: self.change(k, 1), 18)
            P.rect(bx + 224, y, 204, 40, "#fafbfe", INK, 1.5)
            lab, val = art.opt(ch, key)
            if val.startswith("#"):
                P.oval(bx + 244, y + 20, 10, 10, val, INK, 1.5)
                P.text(bx + 262, y + 20, lab, 16, INK, "w")
            else:
                P.text(bx + 326, y + 20, lab, 16, INK)

        # Tengah: Preview Hero
        sx, sy, sw, sh = 544, 24, 368, 646
        P.window(sx, sy, sw, sh, "PREVIEW HERO", SKY, WHITE)
        cx = sx + sw / 2
        P.oval(cx, 300, 128, 128, "#f3f6fc", "", 0)
        art.draw_chibi(P, cx, sy + 520, 380, ch, self.t, "cheer" if self.cheer > 0 else "idle")
        P.rect(sx + 18, sy + 544, sw - 36, 82, "#f6f7fb", INK, 1.5)
        P.text(sx + 32, sy + 568, f"ATTACK : {cls['atk']}", 15, INK, "w")
        P.text(sx + 32, sy + 602, f"SPELL  : {cls['spell']}", 15, INK, "w")

        # Kanan: Info & Navigasi
        rx, ry, rw, _rh = P.window(932, 24, 324, 646, "CHARACTER", LILAC, WHITE)
        self.button(rx + 16, ry + 16, rw - 32, 46, f"{self.nama} (Ubah Nama)", YELLOW, self.rename, 17)
        P.text(rx + 18, ry + 86, "KELAS", 14, "#6c7086", "w")
        P.text(rx + 18, ry + 114, cname.upper(), 24, INK, "w")
        P.text(rx + 18, ry + 154, "HP", 16, INK, "w")
        P.hearts_row(rx + 56, ry + 148, 6, 6, 13, 4)

        for i, (lab, v) in enumerate(zip(("STRENGTH", "AGILITY", "MAGIC"), self.shown)):
            y = ry + 190 + i * 56
            P.text(rx + 18, y, lab, 14, INK, "w")
            P.bar(rx + 18, y + 12, rw - 36, 18, v, [PINK, MINT, SKY][i])

        yy = ry + 382
        self.button(rx + 16, yy, rw - 32, 46, "ACAK KARAKTER", SKY, self.randomize, 17)
        self.button(rx + 16, yy + 60, rw - 32, 62, "SELESAI!", MINT, self.finish, 24)
        self.button(rx + 16, yy + 136, rw - 32, 42, "KEMBALI", GRAY, self.back, 16)