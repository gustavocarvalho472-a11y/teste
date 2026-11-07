"""Motor 'documentário de futebol' — identidade Beyond Success.
Clipes reais em tela cheia (gradação, câmera lenta), memes, tela dividida CR7 × Homelander, lower thirds,
cartões de ato com linha do tempo, citações, placar, logo. Funções puras do tempo (render em paralelo)."""
import math
import os
import subprocess

import cairo
import cv2
import numpy as np

from fx import (FPS, H, W, clamp, eexp, ein, eio, eout, font, lerp, pulse, rgb, rrect, seg, soft_shadow, surf,
                text, text_width)

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips")
SEGDIR = os.path.join(HERE, "cache", "seg")
DOCDIR = os.path.join(HERE, "cache", "doc")
LIME = (0.788, 0.961, 0.133)     # #C9F521 (Beyond Success)
WHITE = (0.97, 0.97, 0.96)
GREY = (0.66, 0.68, 0.70)
DARK = (0.035, 0.04, 0.045)
DISPLAY, UI = "Anton", "Inter"


# ───────────────────────── extração de trechos ─────────────────────────
def extract(name, clip, t0, t1, crop=None, slow=1.0, reverse=False, fit="cover", anchor="center"):
    """Trecho [t0,t1] do clipe → cache/seg/<name>/00001.jpg… (1920x1080, 30 fps). slow=2 → metade da velocidade."""
    out = os.path.join(SEGDIR, name)
    if os.path.exists(os.path.join(out, "done")):
        return
    os.makedirs(out, exist_ok=True)
    vf = []
    if crop:
        x0, y0, x1, y1 = crop
        vf.append(f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0}")
    if fit == "letterbox":
        vf.append("scale=1920:-2:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black")
    else:
        yc = "0" if anchor == "top" else "(ih-1080)/2"
        vf.append(f"scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080:(iw-1920)/2:{yc}")
    if slow != 1.0:
        vf.append(f"setpts={slow}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        vf.append("fps=30")
    if reverse:
        vf.append("reverse")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0}", "-to", f"{t1}", "-i", os.path.join(CLIPS, clip + ".mp4"),
                    "-vf", ",".join(vf), "-q:v", "2", os.path.join(out, "%05d.jpg")], check=True)
    open(os.path.join(out, "done"), "w").write("ok")


def extract_audio(name, clip, t0, t1, slow=1.0):
    out = os.path.join(SEGDIR, name + ".wav")
    if os.path.exists(out):
        return out
    os.makedirs(SEGDIR, exist_ok=True)
    af = ["aresample=48000"]
    if slow != 1.0:
        af.append(f"atempo={1 / slow:.4f}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0}", "-to", f"{t1}", "-i", os.path.join(CLIPS, clip + ".mp4"),
                    "-vn", "-ac", "2", "-af", ",".join(af), out], check=True)
    return out


_N = {}


def seg_n(name):
    if name not in _N:
        _N[name] = len([f for f in os.listdir(os.path.join(SEGDIR, name)) if f.endswith(".jpg")])
    return _N[name]


_LAST = {}


def seg_frame(name, i):
    n = seg_n(name)
    i = int(clamp(i, 0, n - 1))
    key = (name, i)
    if key in _LAST:
        return _LAST[key]
    img = cv2.imread(os.path.join(SEGDIR, name, f"{i + 1:05d}.jpg"))
    if len(_LAST) > 6:
        _LAST.clear()
    _LAST[key] = img
    return img


# ───────────────────────── cor ─────────────────────────
def _lut(contrast=1.08, lift=0.03, gamma=1.0):
    x = np.arange(256) / 255.0
    y = 0.5 + (x - 0.5) * contrast
    y = np.clip(y, 0, 1) ** gamma
    y = lift + y * (1 - lift)
    return np.clip(y * 255, 0, 255).astype(np.uint8)


GRADES = {  # contraste, levantar pretos, gama, saturação, deslocamento B,G,R nas sombras / nas luzes
    "doc": (1.10, 0.025, 1.0, 0.88, (6, 2, -3), (-6, 0, 8)),
    "warm": (1.08, 0.02, 0.98, 0.98, (2, 0, 0), (-10, 2, 12)),
    "cold": (1.08, 0.03, 1.02, 0.70, (10, 4, -4), (2, 0, -2)),
    "fall": (1.12, 0.035, 1.04, 0.45, (10, 5, 0), (0, 0, 0)),
    "show": (1.04, 0.015, 1.0, 0.95, (3, 1, -1), (-3, 0, 4)),
    "punch": (1.34, -0.07, 1.12, 1.12, (4, 1, -2), (-6, 0, 8)),
    "none": (1.0, 0.0, 1.0, 1.0, (0, 0, 0), (0, 0, 0)),
}
_LUTS = {}


def grade(img, kind="doc"):
    if kind == "none":
        return img
    con, lift, gam, sat, sh, hi = GRADES[kind]
    if kind not in _LUTS:
        base = _lut(con, lift, gam)
        x = np.arange(256) / 255.0
        luts = []
        for k in range(3):
            v = base.astype(np.float32) + sh[k] * (1 - x) ** 2 + hi[k] * x ** 2
            luts.append(np.clip(v, 0, 255).astype(np.uint8))
        _LUTS[kind] = np.stack(luts, 1).reshape(256, 1, 3)
    out = cv2.LUT(img, _LUTS[kind])
    if sat != 1.0:
        g = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        g3 = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        out = cv2.addWeighted(out, sat, g3, 1 - sat, 0)
    return out


def np_surface(img):
    h, w = img.shape[:2]
    a = np.empty((h, w, 4), np.uint8)
    a[..., :3] = img
    a[..., 3] = 255
    s = cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, w, h, w * 4)
    _KEEP.append(a)      # o buffer precisa viver enquanto a superfície é usada
    if len(_KEEP) > 24:
        _KEEP.pop(0)
    return s


_KEEP = []


def paint_img(c, s, x, y, w, h, focus=(0.5, 0.5), zoom=1.0, alpha=1.0, filt=cairo.FILTER_GOOD):
    """Desenha a superfície cobrindo o retângulo (x,y,w,h), com zoom e foco."""
    iw, ih = s.get_width(), s.get_height()
    k = max(w / iw, h / ih) * zoom
    cx = clamp(focus[0] * iw, w / 2 / k, iw - w / 2 / k) if iw * k > w else iw / 2
    cy = clamp(focus[1] * ih, h / 2 / k, ih - h / 2 / k) if ih * k > h else ih / 2
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x + w / 2, y + h / 2)
    c.scale(k, k)
    c.translate(-cx, -cy)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(filt)
    c.paint_with_alpha(alpha)
    c.restore()


def clip(c, name, t, t0, kind="doc", rate=1.0, start=0.0, rect=(0, 0, W, H), zoom=(1.0, 1.0), dur=4.0,
         focus=(0.5, 0.5), focus1=None, alpha=1.0):
    """Quadro do trecho `name` no instante t (o trecho começa a tocar em t0)."""
    i = int(round(((t - t0) * rate + start) * FPS))
    s = np_surface(grade(seg_frame(name, i), kind))
    u = eio(seg(t, t0, t0 + dur)) * 0.3 + seg(t, t0, t0 + dur) * 0.7
    z = lerp(zoom[0], zoom[1], u)
    f = focus if focus1 is None else (lerp(focus[0], focus1[0], u), lerp(focus[1], focus1[1], u))
    paint_img(c, s, *rect, focus=f, zoom=z, alpha=alpha)


def photo(c, name, t, t0, rect=(0, 0, W, H), zoom=(1.0, 1.08), dur=5.0, focus=(0.5, 0.5), focus1=None, alpha=1.0):
    s = surf(name)
    u = eio(seg(t, t0, t0 + dur)) * 0.3 + seg(t, t0, t0 + dur) * 0.7
    z = lerp(zoom[0], zoom[1], u)
    f = focus if focus1 is None else (lerp(focus[0], focus1[0], u), lerp(focus[1], focus1[1], u))
    paint_img(c, s, *rect, focus=f, zoom=z, alpha=alpha)


def dim(c, a, col=(0, 0, 0)):
    c.set_source_rgba(col[0], col[1], col[2], a)
    c.paint()


# ───────────────────────── memes ─────────────────────────
def meme(c, name, t, t0, h_target=960, kick=True, alpha=1.0, pan=None):
    """Meme vertical centralizado sobre a versão desfocada dele mesmo (formato de post)."""
    bg = surf(name + "_blur")
    paint_img(c, bg, 0, 0, W, H, zoom=1.15)
    dim(c, 0.45)
    s = surf(name)
    iw, ih = s.get_width(), s.get_height()
    k = h_target / ih
    if iw * k > W * 0.92:
        k = W * 0.92 / iw
    sc = 1.0 + (0.06 * (1 - eout(seg(t, t0, t0 + 0.28))) if kick else 0)
    w, h = iw * k * sc, ih * k * sc
    x, y = (W - w) / 2, (H - h) / 2
    if pan:  # pan=(y_from, y_to, t_a, t_b): desloca verticalmente (para "descer" no meme)
        y += lerp(pan[0], pan[1], eio(seg(t, pan[2], pan[3])))
    soft_shadow(c, x, y, w, h, 6, spread=36, a=0.65)
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x, y)
    c.scale(k * sc, k * sc)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(alpha)
    c.restore()


# ───────────────────────── tela dividida ─────────────────────────
def split(c, t, t0, left, right, labels=("CRISTIANO RONALDO", "HOMELANDER"), label_a=1.0):
    """left/right: funções (c, rect) que desenham cada metade. Divisória verde-limão entra do centro."""
    gap = 8
    lw = (W - gap) / 2
    u = eout(seg(t, t0, t0 + 0.45))
    c.save()
    left(c, (0, 0, lw, H))
    right(c, (lw + gap, 0, lw, H))
    c.restore()
    hh = H * u
    c.rectangle(lw, H / 2 - hh / 2, gap, hh)
    rgb(c, LIME)
    c.fill()
    if label_a > 0:
        a = label_a * seg(t, t0 + 0.25, t0 + 0.6)
        for i, lab in enumerate(labels):
            cx = lw / 2 + i * (lw + gap)
            g = cairo.LinearGradient(0, H - 230, 0, H)
            g.add_color_stop_rgba(0, 0, 0, 0, 0)
            g.add_color_stop_rgba(1, 0, 0, 0, 0.75 * a)
            c.set_source(g)
            c.rectangle(i * (lw + gap), H - 230, lw, 230)
            c.fill()
            text(c, lab, cx, H - 78, 44, DISPLAY, WHITE, a, "center", 3)
            font(c, DISPLAY, 44)
            tw = text_width(c, lab, 3)
            c.rectangle(cx - tw / 2, H - 62, tw * eout(seg(t, t0 + 0.35, t0 + 0.8)), 4)
            rgb(c, LIME, a)
            c.fill()


# ───────────────────────── grafismos ─────────────────────────
def lower_third(c, t, t0, l1, l2="", dur=4.0, x=110, y=None):
    if t < t0 or t > t0 + dur:
        return
    y = H - 175 if y is None else y
    a = eout(seg(t, t0, t0 + 0.35)) * (1 - eio(seg(t, t0 + dur - 0.35, t0 + dur)))
    bh = 92 * eout(seg(t, t0, t0 + 0.3))
    c.rectangle(x, y - 60, 8, bh)
    rgb(c, LIME, a)
    c.fill()
    font(c, DISPLAY, 50)
    tw = text_width(c, l1, 2)
    if l2:
        font(c, UI, 26, True)
        tw = max(tw, text_width(c, l2, 1.5))
    rev = eout(seg(t, t0 + 0.12, t0 + 0.6))
    c.save()
    c.rectangle(x + 24, y - 70, (tw + 20) * rev, 120)
    c.clip()
    text(c, l1, x + 28, y - 10, 50, DISPLAY, WHITE, a, "left", 2, shadow=0.5)
    if l2:
        text(c, l2, x + 30, y + 26, 26, UI, GREY, a, "left", 1.5, bold=True, shadow=0.5)
    c.restore()


def score_bug(c, t, t0, t1, home, hs, away, as_, minute, x=72, y=58):
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.3)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    w, h = 360, 54
    c.save()
    c.translate(x, y)
    rrect(c, 0, 0, w, h, 8)
    c.set_source_rgba(0.06, 0.07, 0.08, 0.88 * a)
    c.fill()
    text(c, home, 22, 37, 28, UI, WHITE, a, "left", 1, bold=True)
    text(c, f"{hs} – {as_}", 150, 37, 30, UI, WHITE, a, "center", 1, bold=True)
    text(c, away, 280, 37, 28, UI, WHITE, a, "right", 1, bold=True)
    rrect(c, w - 72, 9, 62, 36, 6)
    rgb(c, LIME, a)
    c.fill()
    text(c, minute, w - 41, 36, 24, UI, DARK, a, "center", 0, bold=True)
    c.restore()


ACTS = ["I", "II", "III", "IV", "V", "FALL", "END"]


def act_card(c, t, t0, t1, idx, title, sub=""):
    """Cartão de capítulo: 'ACT I' + título + linha de progresso (marca registrada do canal)."""
    a = eout(seg(t, t0, t0 + 0.4)) * (1 - eio(seg(t, t1 - 0.35, t1)))
    dim(c, 0.62 * a)
    lab = f"ACT {ACTS[idx]}" if idx < 5 else ACTS[idx]
    text(c, lab, W / 2, H / 2 - 120, 46, DISPLAY, LIME, a, "center", 14)
    sp = lerp(26, 4, eout(seg(t, t0 + 0.1, t0 + 1.0)))
    text(c, title, W / 2, H / 2 + 40, 132, DISPLAY, WHITE, a * seg(t, t0 + 0.1, t0 + 0.45), "center", sp, shadow=0.4)
    if sub:
        text(c, sub, W / 2, H / 2 + 112, 28, UI, GREY, a * seg(t, t0 + 0.5, t0 + 0.9), "center", 4, bold=True)
    # linha de progresso
    n = len(ACTS)
    x0, x1, y = W / 2 - 520, W / 2 + 520, H - 140
    pa = a * seg(t, t0 + 0.3, t0 + 0.7)
    c.rectangle(x0, y - 1.5, x1 - x0, 3)
    c.set_source_rgba(1, 1, 1, 0.25 * pa)
    c.fill()
    prog = (idx + eout(seg(t, t0 + 0.5, t0 + 1.3)) * 0) / (n - 1)
    c.rectangle(x0, y - 1.5, (x1 - x0) * prog, 3)
    rgb(c, LIME, pa)
    c.fill()
    for i, s in enumerate(ACTS):
        x = x0 + (x1 - x0) * i / (n - 1)
        cur = i == idx
        r = 11 if cur else 6
        if cur:
            r *= 1 + 0.25 * pulse(t, t0 + 0.6, t0 + 1.2)
        c.arc(x, y, r, 0, 2 * math.pi)
        if i <= idx:
            rgb(c, LIME if cur else WHITE, pa)
            c.fill()
        else:
            c.set_source_rgba(1, 1, 1, 0.35 * pa)
            c.set_line_width(2)
            c.stroke()
        text(c, s, x, y + 44, 20, UI, LIME if cur else GREY, pa * (1 if cur else 0.8), "center", 2, bold=True)


def quote(c, t, t0, t1, lines, who, size=68):
    a = eout(seg(t, t0, t0 + 0.4)) * (1 - eio(seg(t, t1 - 0.35, t1)))
    dim(c, 0.6 * a)
    text(c, "“", 260, H / 2 - 90 - (len(lines) - 1) * size * 0.6, 220, DISPLAY, LIME, a, "left")
    for i, ln in enumerate(lines):
        y = H / 2 - (len(lines) - 1) * size * 0.62 + i * size * 1.24
        la = a * seg(t, t0 + 0.15 + i * 0.25, t0 + 0.55 + i * 0.25)
        text(c, ln, 400, y + 16 * (1 - eout(seg(t, t0 + 0.15 + i * 0.25, t0 + 0.7 + i * 0.25))), size, UI, WHITE, la,
             "left", 0, bold=True, shadow=0.4)
    text(c, who, 404, H / 2 + (len(lines) + 0.6) * size * 0.62 + 40, 28, UI, LIME, a * seg(t, t0 + 0.6, t0 + 1.0),
         "left", 2, bold=True)


def year_tag(c, t, t0, t1, year, place="", x=None, y=None):
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.25)) * (1 - eio(seg(t, t1 - 0.25, t1)))
    x = 110 if x is None else x
    y = 170 if y is None else y
    text(c, year, x, y, 96, DISPLAY, LIME, a, "left", 2, shadow=0.5)
    if place:
        text(c, place, x + 4, y + 44, 26, UI, WHITE, a, "left", 2, bold=True, shadow=0.6)


def bars(c, k):
    """Barras de cinema (k=0 sem barras, 1 = 2.39:1)."""
    if k <= 0.001:
        return
    bh = (H - W / 2.39) / 2 * k
    c.rectangle(0, 0, W, bh)
    c.rectangle(0, H - bh, W, bh)
    c.set_source_rgb(0, 0, 0)
    c.fill()


def logo_bug(c, a=0.85, size=78):
    if a <= 0:
        return
    s = surf("doc/logo")
    k = size / s.get_width()
    c.save()
    c.translate(W - size - 34, H - size - 30)
    c.scale(k, k)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(a)
    c.restore()


def phone_frame(c, cx, cy, h, draw_screen, a=1.0):
    w = h * 0.5
    r = h * 0.07
    soft_shadow(c, cx - w / 2, cy - h / 2, w, h, r, spread=h * 0.05, a=0.6 * a)
    rrect(c, cx - w / 2, cy - h / 2, w, h, r)
    c.set_source_rgba(0.07, 0.07, 0.08, a)
    c.fill()
    b = h * 0.02
    c.save()
    rrect(c, cx - w / 2 + b, cy - h / 2 + b, w - 2 * b, h - 2 * b, r * 0.8)
    c.clip()
    draw_screen(c, (cx - w / 2 + b, cy - h / 2 + b, w - 2 * b, h - 2 * b))
    c.restore()


# ───────────────────────── pós ─────────────────────────
_GR = None
_VIG = None


def post(surface, i, fx):
    global _GR, _VIG
    if _GR is None:
        from scipy.ndimage import gaussian_filter
        r = np.random.default_rng(5)
        _GR = [gaussian_filter(r.normal(0, 4.0, (H, W)).astype(np.float32), 0.6) for _ in range(6)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _VIG = (1 - 0.38 * np.clip(d, 0, 1) ** 2.4).astype(np.float32)
    surface.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=surface.get_data())
    img = buf[:, :, :3].astype(np.float32)
    img *= _VIG[..., None]
    img += _GR[i % 6][..., None] * fx.get("grain", 0.8)
    fl = fx.get("flash", 0)
    if fl > 0:
        img = img * (1 - fl) + 255 * fl
    fd = fx.get("fade", 0)
    if fd > 0:
        img *= (1 - fd)
    np.clip(img, 0, 255, out=img)
    out = np.empty((H, W, 4), np.uint8)
    out[:, :, :3] = img.astype(np.uint8)
    out[:, :, 3] = 255
    return out.tobytes()
