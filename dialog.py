# -*- coding: utf-8 -*-
"""dialog.py - Form input & popup bergaya kartu minimalis dengan fitur auto-close."""
import sfx
from kit import INK, PINK, HOT, MINT, YELLOW, WHITE, GRAY, RED, darken


def grp(digits):
    return f"{int(digits):,}".replace(",", ".") if digits else ""


def _btn(owner, x, y, w, h, label, color, cb, size=18):
    mx, my = owner.app.mouse
    hov = x <= mx <= x + w and y <= my <= y + h
    P = owner.P
    P.rect(x, y, w, h, darken(color, 0.07) if hov else color, INK, 2, "dyn")
    P.text(x + w / 2, y + h / 2, label, size, INK, tags="dyn")
    owner.hits.append((x, y, w, h, cb))


class Dialog:
    """Form modal minimalis."""

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
        if hasattr(self.app, "mark_dirty"):
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
                    self.err = "'%s' harus lebih dari 0." % f["label"]
                    return
                out[f["key"]] = int(v)
            elif k == "text":
                v = v.strip()
                if f.get("required") and not v:
                    self.err = "'%s' tidak boleh kosong." % f["label"]
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
        if key not in ("Return", "KP_Enter"):
            self.err = ""

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
        P.cv.create_rectangle(10, 10, P.pw - 10, P.ph - 10, fill="", outline="#8d92a8", width=10, tags="dyn")
        W = 580
        H = 180 + len(self.fields) * 86 + (24 if self.subtitle else 0)
        x = (1280 - W) / 2
        y = (720 - H) / 2
        bx, by, bw, _bh = P.window(x, y, W, H, self.title, self.color)
        self.hits.append((x + W - 30, y + 4, 26, 26, self.cancel))

        ty = by + 16
        if self.subtitle:
            P.text(bx + 22, ty + 6, self.subtitle, 15, "#5c6075", "w", width=bw - 44)
            ty += 26
        for i, f in enumerate(self.fields):
            fy = ty + i * 86
            foc = i == self.focus
            P.text(bx + 22, fy + 10, f["label"], 16, INK, "w")
            rx, ry, rw, rh = bx + 22, fy + 24, bw - 44, 46
            if f["kind"] == "choice":
                P.rect(rx, ry, rw, rh, WHITE, HOT if foc else INK, 2.5 if foc else 1.5, "dyn")
                P.text(rx + 28, ry + rh / 2, "<", 20, INK)
                P.text(rx + rw - 28, ry + rh / 2, ">", 20, INK)
                P.text(rx + rw / 2, ry + rh / 2, f["choices"][f["idx"]], 19, INK)
                self.hits.append((rx, ry, 56, rh, lambda f=f, i=i: (setattr(self, "focus", i), self._choice(f, -1))))
                self.hits.append((rx + rw - 56, ry, 56, rh, lambda f=f, i=i: (setattr(self, "focus", i), self._choice(f, 1))))
            else:
                P.rect(rx, ry, rw, rh, WHITE, HOT if foc else INK, 2.5 if foc else 1.5, "dyn")
                txt = ("Rp " + grp(f["value"])) if (f["kind"] == "money" and f["value"]) else f["value"]
                if txt:
                    P.text(rx + 14, ry + rh / 2, txt, 21, INK, "w")
                else:
                    P.text(rx + 14, ry + rh / 2, f["hint"], 18, "#9ba0b4", "w")
                if foc and int(self.t * 2) % 2 == 0:
                    cx = rx + 16 + len(txt) * 12
                    P.rect(cx, ry + 10, 2, rh - 20, HOT, "", 0)
                self.hits.append((rx, ry, rw, rh, lambda i=i: setattr(self, "focus", i)))

        by2 = y + H - 82
        if self.err:
            P.text(bx + bw / 2, by2 - 12, self.err, 15, "#c93b5b", "center", width=bw - 40)
        _btn(self, bx + 24, by2 + 4, 150, 44, "BATAL", GRAY, self.cancel, 16)
        _btn(self, bx + bw - 24 - 220, by2 + 4, 220, 44, self.ok_text, MINT, self.submit, 17)


class Popup:
    """Popup notifikasi minimalis dengan auto-close dan klik di mana saja untuk menutup."""

    def __init__(self, app, title, msg, art=None, color=YELLOW, btn="OK", on_close=None, sound="lvl", auto_close=0.0):
        self.app, self.P = app, app.P
        self.title, self.msg, self.art, self.color, self.btn, self.on_close = title, msg, art, color, btn, on_close
        self.auto_close = float(auto_close or 0.0)
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
        if hasattr(self.app, "mark_dirty"):
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
        # Klik di luar kotak popup juga langsung menutup popup agar tidak mengganggu
        W, H = 560, 320
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
        P.cv.create_rectangle(10, 10, P.pw - 10, P.ph - 10, fill="", outline="#8d92a8", width=10, tags="dyn")
        W, H = 560, 320
        x = (1280 - W) / 2
        y = (720 - H) / 2
        bx, by, bw, bh = P.window(x, y, W, H, "INFO (Klik X / Esc untuk tutup)", self.color)
        # Area klik tombol [X] pojok kanan atas
        self.hits.append((x + W - 30, y + 4, 26, 26, self.close))
        P.text(x + W - 15, y + 15, "X", 12, WHITE, "center")

        P.text(x + W / 2, by + 54, self.title, 30, INK, "center")
        P.text(x + W / 2, by + bh / 2 - 4, self.msg, 18, "#4a4e69", "center", width=bw - 64, justify="center")

        if self.auto_close > 0:
            rem = max(0.0, 1.0 - self.t / self.auto_close)
            P.bar(x + 90, y + H - 84, W - 180, 8, rem, self.color)

        _btn(self, x + W / 2 - 95, y + H - 64, 190, 44, self.btn, MINT, self.close, 18)