# -*- coding: utf-8 -*-
"""dialog.py - Form input & popup bergaya jendela Y2K (digambar di canvas, tanpa widget bawaan)."""
import sfx
from kit import (INK, CREAM, PINK, HOT, LILAC, SKY, MINT, YELLOW, WHITE, GRAY, RED, lighten)


def grp(digits):
    return f"{int(digits):,}".replace(",", ".") if digits else ""


def _overlay(P):
    P.cv.create_rectangle(14, 14, P.pw - 14, P.ph - 14, fill="", outline=INK, width=14, tags="dyn")


def _btn(owner, x, y, w, h, label, color, cb, size=22):
    mx, my = owner.app.mouse
    hov = x <= mx <= x + w and y <= my <= y + h
    pressed = hov and owner.app.mouse_down
    P = owner.P
    yy = y + (3 if pressed else (-3 if hov else 0))
    P.rect(x, yy, w, h, lighten(color, 0.22) if hov else color, INK, 3.5, "dyn", r=h / 2, sh=5)
    P.rect(x + 9, yy + 5, w - 18, max(4, h * 0.2), lighten(color, 0.6), "", 0, "dyn", r=6)
    P.text(x + w / 2, yy + h / 2 + 1, label, size, INK)
    owner.hits.append((x, y, w, h, cb))


class Dialog:
    """Form modal. fields: [{key,label,kind('money'|'text'|'choice'),value,choices,hint,required,allow_zero}]"""

    def __init__(self, app, title, fields, ok_text="OK", color=PINK, on_ok=None, subtitle="", on_cancel=None):
        self.app, self.P = app, app.P
        self.title, self.fields, self.ok_text, self.color = title, fields, ok_text, color
        self.on_ok, self.on_cancel, self.subtitle = on_ok, on_cancel, subtitle
        for f in fields:
            f.setdefault("value", "")
            f.setdefault("maxlen", 22)
            f.setdefault("hint", "")
            f.setdefault("idx", 0)
        self.focus = 0
        for i, f in enumerate(fields):
            if f["kind"] != "choice":
                self.focus = i
                break
        self.hits, self.err, self.t = [], "", 0.0
        self._submitted = False

    def close(self):
        if self.app.dialog is self:
            self.app.dialog = None
        self.app.mark_dirty()

    def cancel(self):
        self.close()
        if self.on_cancel:
            self.on_cancel()

    def submit(self):
        if self._submitted:
            return
        out = {}
        for f in self.fields:
            k, v = f["kind"], f["value"]
            if k == "money":
                if not v or (int(v) <= 0 and not f.get("allow_zero")):
                    self.err = "'%s' harus berupa angka lebih dari 0." % f["label"]
                    self.app.mark_dirty()
                    return
                out[f["key"]] = int(v)
            elif k == "text":
                v = v.strip()
                if f.get("required") and not v:
                    self.err = "'%s' tidak boleh kosong." % f["label"]
                    self.app.mark_dirty()
                    return
                out[f["key"]] = v
            else:
                out[f["key"]] = f["idx"]
        self._submitted = True
        self.close()
        sfx.play("coin")
        if self.on_ok:
            self.on_ok(out)

    def _choice(self, f, d):
        f["idx"] = (f["idx"] + d) % len(f["choices"])
        sfx.play("click")
        self.app.mark_dirty()

    def on_key(self, key, ch):
        f = self.fields[self.focus]
        if key == "Escape":
            self.cancel()
        elif key in ("Return", "KP_Enter"):
            self.submit()
        elif key in ("Tab", "Down"):
            self.focus = (self.focus + 1) % len(self.fields)
        elif key in ("Up", "ISO_Left_Tab"):
            self.focus = (self.focus - 1) % len(self.fields)
        elif f["kind"] == "choice":
            if key == "Left":
                self._choice(f, -1)
            elif key == "Right":
                self._choice(f, 1)
        elif key == "BackSpace":
            f["value"] = f["value"][:-1]
        elif ch and ch.isprintable() and len(f["value"]) < (12 if f["kind"] == "money" else f["maxlen"]):
            if f["kind"] == "money":
                if ch.isdigit():
                    f["value"] += ch
            else:
                f["value"] += ch
        self.err = "" if key not in ("Return", "KP_Enter") else self.err
        self.app.mark_dirty()

    def click(self, x, y):
        for hx, hy, w, h, cb in reversed(self.hits):
            if hx <= x <= hx + w and hy <= y <= hy + h:
                sfx.play("click")
                cb()
                return True
        return True

    def draw(self, dt):
        P = self.P
        self.t += dt
        self.hits = []
        _overlay(P)
        W = 640
        H = 190 + len(self.fields) * 92 + (26 if self.subtitle else 0)
        x = (1280 - W) / 2
        y = (720 - H) / 2 + (1 - min(1.0, self.t * 6)) ** 2 * 50
        bx, by, bw, _bh = P.window(x, y, W, H, self.title, self.color)
        # Daftarkan tombol [X] pojok kanan atas jendela agar bisa menutup dialog
        self.hits.append((x + W - 30, y + 4, 26, 26, self.cancel))

        ty = by + 16
        if self.subtitle:
            P.text(bx + 22, ty + 8, self.subtitle, 17, "#6f6580", "w", width=bw - 44)
            ty += 30
        for i, f in enumerate(self.fields):
            fy = ty + i * 92
            foc = i == self.focus
            P.text(bx + 22, fy + 10, f["label"].upper(), 18, INK, "w")
            rx, ry, rw, rh = bx + 22, fy + 26, bw - 44, 52
            if f["kind"] == "choice":
                P.rect(rx, ry, rw, rh, WHITE, HOT if foc else INK, 4 if foc else 3, "dyn", r=14)
                P.poly([(rx + 18, ry + rh / 2), (rx + 36, ry + 10), (rx + 36, ry + rh - 10)], YELLOW, INK, 2.5)
                P.poly([(rx + rw - 18, ry + rh / 2), (rx + rw - 36, ry + 10), (rx + rw - 36, ry + rh - 10)], YELLOW, INK, 2.5)
                P.text(rx + rw / 2, ry + rh / 2 + 1, f["choices"][f["idx"]], 22, INK)
                self.hits.append((rx, ry, 56, rh, lambda f=f, i=i: (setattr(self, "focus", i), self._choice(f, -1))))
                self.hits.append((rx + rw - 56, ry, 56, rh, lambda f=f, i=i: (setattr(self, "focus", i), self._choice(f, 1))))
            else:
                P.rect(rx, ry, rw, rh, WHITE, HOT if foc else INK, 4 if foc else 3, "dyn", r=14)
                if f["kind"] == "money":
                    txt = ("Rp " + grp(f["value"])) if f["value"] else ""
                else:
                    txt = f["value"]
                if txt:
                    P.text(rx + 18, ry + rh / 2 + 1, txt, 26, INK, "w")
                else:
                    P.text(rx + 18, ry + rh / 2 + 1, f["hint"], 22, "#b5aabf", "w")
                if foc and int(self.t * 2.2) % 2 == 0:
                    cx = rx + 20 + len(txt) * 26 * 0.56
                    P.rect(cx, ry + 10, 3, rh - 20, HOT, "", 0)
                self.hits.append((rx, ry, rw, rh, lambda i=i: setattr(self, "focus", i)))
        by2 = y + H - 98
        if self.err:
            P.text(bx + bw / 2, by2 - 12, self.err, 17, RED, "center", width=bw - 40)
        _btn(self, bx + 28, by2 + 6, 170, 52, "BATAL", GRAY, self.cancel, 20)
        _btn(self, bx + bw - 28 - 260, by2 + 6, 260, 52, self.ok_text, MINT, self.submit, 22)


class Popup:
    """Popup info/perayaan: judul besar, gambar di tengah, satu tombol."""

    def __init__(self, app, title, msg, art=None, color=YELLOW, btn="OK", on_close=None, sound="lvl"):
        self.app, self.P = app, app.P
        self.title, self.msg, self.art, self.color, self.btn, self.on_close = title, msg, art, color, btn, on_close
        self.t, self.hits = 0.0, []
        self._closed = False
        if sound:
            sfx.play(sound)

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self.app.dialog is self:
            self.app.dialog = None
        self.app.mark_dirty()
        if self.on_close:
            self.on_close()

    def on_key(self, key, _ch):
        if key in ("Return", "KP_Enter", "space", "Escape"):
            self.close()

    def click(self, x, y):
        for hx, hy, w, h, cb in reversed(self.hits):
            if hx <= x <= hx + w and hy <= y <= hy + h:
                cb()
                return True
        return True

    def draw(self, dt):
        P = self.P
        self.t += dt
        self.hits = []
        _overlay(P)
        W, H = 680, 470
        x = (1280 - W) / 2
        k = min(1.0, self.t * 5)
        y = (720 - H) / 2 + (1 - k) ** 2 * 60
        bx, by, bw, bh = P.window(x, y, W, H, "NOTIFICATION.exe", self.color)
        # Daftarkan tombol [X] pojok kanan atas popup
        self.hits.append((x + W - 30, y + 4, 26, 26, self.close))
        P.stext(x + W / 2, by + 46, self.title, 44, self.color, INK, 4)
        if callable(self.art):
            self.art(P, x + W / 2, by + 250, self.t)
        P.text(x + W / 2, by + bh - 86, self.msg, 20, INK, "center", width=bw - 60, justify="center")
        _btn(self, x + W / 2 - 110, y + H - 76, 220, 52, self.btn, MINT, self.close, 22)