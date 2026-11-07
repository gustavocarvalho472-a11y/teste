"""Motor visual do dossiê (pycairo 1920x1080): câmera 2.5D, provas impressas, fio vermelho, marcador,
carimbos, máquina de escrever, celular, efeitos. Tudo é função pura do tempo (quadros em paralelo)."""
import json
import math
import os
import random

import cairo
import numpy as np

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
META = json.load(open(os.path.join(CACHE, "meta.json")))

RED = (0.80, 0.11, 0.09)        # tinta / fio
HOT = (1.0, 0.23, 0.19)         # #FF3B30
WHITE = (0.95, 0.95, 0.94)
GREY = (0.56, 0.59, 0.62)
DIM = (0.36, 0.39, 0.42)
INK = (0.067, 0.086, 0.106)     # #11161B
PAPER = (0.925, 0.905, 0.862)
SERIF, MONO, TYPE, MARK, STAMP, BEBAS, SANS = ("DM Serif Display", "JetBrains Mono", "Special Elite",
                                              "Permanent Marker", "Anton", "Bebas Neue", "Inter")


# ───────────────────────── tempo / easing ─────────────────────────
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def seg(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def lerp(a, b, u):
    return a + (b - a) * u


def eio(u):
    u = clamp(u)
    return u * u * u * (u * (u * 6 - 15) + 10)


def eout(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ein(u):
    u = clamp(u)
    return u ** 3


def eexp(u):
    u = clamp(u)
    return 1.0 if u >= 1 else 1 - 2 ** (-10 * u)


def eback(u, s=1.7):
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def pulse(t, a, b):
    """0→1→0 entre a e b."""
    return math.sin(math.pi * seg(t, a, b))


# ───────────────────────── superfícies ─────────────────────────
_S = {}


def surf(name):
    if name not in _S:
        _S[name] = cairo.ImageSurface.create_from_png(os.path.join(CACHE, name + ".png"))
    return _S[name]


def rgb(c, col, a=1.0):
    c.set_source_rgba(col[0], col[1], col[2], a)


# ───────────────────────── câmera ─────────────────────────
_EASE = {"io": eio, "out": eout, "in": ein, "lin": lambda u: clamp(u), "exp": eexp, "hold": lambda u: 0.0}


def cam_at(keys, t):
    """keys: [(t, x, y, zoom, rot_graus, ease_do_trecho_seguinte), ...]"""
    if t <= keys[0][0]:
        k = keys[0]
        return k[1], k[2], k[3], k[4]
    for a, b in zip(keys, keys[1:]):
        if t < b[0]:
            u = _EASE[a[5] if len(a) > 5 else "io"](seg(t, a[0], b[0]))
            z = math.exp(lerp(math.log(a[3]), math.log(b[3]), u))
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), z, lerp(a[4], b[4], u)
    k = keys[-1]
    return k[1], k[2], k[3], k[4]


def drift(t, amp=1.0):
    return (amp * (3.2 * math.sin(t * 0.53 + 1.3) + 1.7 * math.sin(t * 1.31 + 0.4)),
            amp * (2.6 * math.sin(t * 0.71 + 2.1) + 1.3 * math.sin(t * 1.77)),
            amp * 0.0018 * math.sin(t * 0.43 + 0.7))


def shake(t, impacts):
    dx = dy = 0.0
    for ti, amp in impacts:
        d = t - ti
        if 0 <= d < 0.7:
            e = math.exp(-d * 8.5) * amp
            dx += e * math.sin(d * 83 + ti * 7)
            dy += e * math.cos(d * 71 + ti * 3)
    return dx, dy


def apply_cam(c, cam, t, impacts=(), amp=1.0):
    x, y, z, r = cam
    dx, dy, dr = drift(t, amp)
    sx, sy = shake(t, impacts)
    c.translate(W / 2 + dx + sx, H / 2 + dy + sy)
    c.rotate(math.radians(r) + dr)
    c.scale(z, z)
    c.translate(-x, -y)


def board_bg(c, tint=1.0):
    p = cairo.SurfacePattern(surf("board"))
    p.set_extend(cairo.EXTEND_REPEAT)
    p.set_filter(cairo.FILTER_GOOD)
    c.set_source(p)
    c.paint()


def light_pool(c, cx=W / 2, cy=H * 0.46, r=W * 0.72, a=0.085, col=(1.0, 0.95, 0.88)):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g)
    c.paint()


def black(c, col=(0.02, 0.025, 0.03)):
    c.set_source_rgb(*col)
    c.paint()


# ───────────────────────── provas impressas ─────────────────────────
class Print:
    """Estado de uma prova num instante (posição, rotação, escala) para desenhar overlays nela."""

    def __init__(self, name, x, y, w, rot):
        self.name, self.x, self.y, self.w, self.rot = name, x, y, w, rot
        m = META[name]
        self.k = w / m["w"]
        self.h = m["h"] * self.k
        self.mw, self.mh = m["w"], m["h"]

    def pt(self, px, py):
        """pixel do PNG salvo (relativo ao centro) → mundo"""
        r = math.radians(self.rot)
        X, Y = px * self.k, py * self.k
        return self.x + X * math.cos(r) - Y * math.sin(r), self.y + X * math.sin(r) + Y * math.cos(r)

    def top(self, inset=26):
        return self.pt(0, -self.mh / 2 + inset / self.k)


def pushpin(c, x, y, r=13, col=RED):
    c.save()
    c.translate(x + r * 0.45, y + r * 0.7)
    c.scale(1, 0.62)
    c.arc(0, 0, r * 1.05, 0, 2 * math.pi)
    c.set_source_rgba(0, 0, 0, 0.5)
    c.fill()
    c.restore()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.05, x, y, r)
    g.add_color_stop_rgb(0, 1.0, 0.62, 0.56)
    g.add_color_stop_rgb(0.35, col[0] * 1.15, col[1] * 1.2, col[2] * 1.2)
    g.add_color_stop_rgb(1, col[0] * 0.38, col[1] * 0.2, col[2] * 0.2)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source(g)
    c.fill()
    c.arc(x - r * 0.33, y - r * 0.38, r * 0.2, 0, 2 * math.pi)
    c.set_source_rgba(1, 1, 1, 0.6)
    c.fill()


def tape(c, x, y, w, h, rot, a=0.55, seed=0):
    rnd = random.Random(seed)
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    c.move_to(-w / 2, -h / 2)
    for i in range(7):
        c.line_to(-w / 2 + w * i / 6, -h / 2 + rnd.uniform(-2, 2))
    for i in range(6):
        c.line_to(w / 2 + rnd.uniform(-3, 3), -h / 2 + h * (i + 1) / 6)
    for i in range(7):
        c.line_to(w / 2 - w * i / 6, h / 2 + rnd.uniform(-2, 2))
    for i in range(6):
        c.line_to(-w / 2 + rnd.uniform(-3, 3), h / 2 - h * (i + 1) / 6)
    c.close_path()
    c.set_source_rgba(0.86, 0.82, 0.72, a)
    c.fill()
    c.restore()


def draw_print(c, name, x, y, w, rot=0.0, t=0.0, t_in=None, dur_in=0.55, alpha=1.0, pin=True, lift=0.0,
               flash=True, shadow=1.0, drop=1.0, pin_col=RED, tapes=False):
    """Desenha a prova; com t_in, ela 'cai' na mesa (sobe, gira, pousa, flash de câmera). Devolve Print."""
    if t_in is not None and t < t_in:
        return None
    m = META[name]
    k0 = w / m["w"]
    sx = 1.0
    r = rot
    a = alpha
    lf = lift
    if t_in is not None:
        u = seg(t, t_in, t_in + dur_in)
        e = eout(u)
        lf = lift + (1 - e) * drop
        sx = 1 + 0.13 * (1 - e) * drop
        r = rot + 8 * (1 - e) * drop
        a = alpha * seg(t, t_in, t_in + 0.06)
    k = k0 * sx
    rr = math.radians(r)
    if shadow > 0 and a > 0:
        sh = surf(name + "_sh")
        c.save()
        c.translate(x + 6 + 46 * lf, y + 10 + 70 * lf)
        c.rotate(rr)
        c.scale(k * (1 + 0.05 * lf), k * (1 + 0.05 * lf))
        c.set_source_surface(sh, -sh.get_width() / 2, -sh.get_height() / 2)
        c.paint_with_alpha(a * shadow * (0.8 - 0.35 * min(lf, 1)))
        c.restore()
    c.save()
    c.translate(x, y)
    c.rotate(rr)
    c.scale(k, k)
    c.set_source_surface(surf(name), -m["w"] / 2, -m["h"] / 2)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(a)
    if flash and t_in is not None:
        fa = (1 - seg(t, t_in + 0.05, t_in + 0.55)) * 0.55 * a
        if fa > 0.002:
            c.rectangle(-m["w"] / 2, -m["h"] / 2, m["w"], m["h"])
            c.set_source_rgba(1, 1, 1, fa)
            c.fill()
    c.restore()
    p = Print(name, x, y, w * sx, r)
    if tapes and a > 0:
        tw = min(150, w * 0.22)
        for sgn in (-1, 1):
            tx, ty = p.pt(sgn * (m["w"] / 2 - 10 / k0), -m["h"] / 2 + 6 / k0)
            tape(c, tx, ty, tw, tw * 0.32, r + sgn * 38, a=0.55 * a, seed=hash(name) % 97 + sgn)
    elif pin and a > 0:
        px, py = p.top()
        pushpin(c, px, py - 26 * lf, 13 / max(0.6, 1.0), pin_col)
    return p


def photo_full(c, name, t, t0, t1, z0=1.0, z1=1.08, fx=0.5, fy=0.5, fx1=None, fy1=None, alpha=1.0, cover=True):
    """Foto em tela cheia com Ken Burns (zoom z0→z1, foco fx,fy normalizado)."""
    s = surf(name)
    iw, ih = s.get_width(), s.get_height()
    u = eio(seg(t, t0, t1)) * 0.25 + seg(t, t0, t1) * 0.75
    z = lerp(z0, z1, u)
    fx1 = fx if fx1 is None else fx1
    fy1 = fy if fy1 is None else fy1
    cx, cy = lerp(fx, fx1, u) * iw, lerp(fy, fy1, u) * ih
    base = max(W / iw, H / ih) if cover else min(W / iw, H / ih)
    k = base * z
    # não deixa sair da imagem
    hw, hh = W / 2 / k, H / 2 / k
    cx = clamp(cx, hw, iw - hw) if iw > 2 * hw else iw / 2
    cy = clamp(cy, hh, ih - hh) if ih > 2 * hh else ih / 2
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(k, k)
    c.translate(-cx, -cy)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(alpha)
    c.restore()
    return k, cx, cy


# ───────────────────────── fio, marcador, setas ─────────────────────────
def _bez(p0, p1, sag, n, prog):
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + L * sag
    pts = []
    for i in range(n + 1):
        u = prog * i / n
        pts.append(((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1,
                    (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1))
    return pts


def _poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)


def string(c, p0, p1, prog=1.0, sag=0.06, width=3.4, alpha=1.0, col=RED):
    if prog <= 0.001:
        return
    pts = _bez(p0, p1, sag, 48, clamp(prog))
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.save()
    c.translate(5, 9)
    _poly(c, pts)
    c.set_source_rgba(0, 0, 0, 0.38 * alpha)
    c.set_line_width(width * 1.4)
    c.stroke()
    c.restore()
    _poly(c, pts)
    rgb(c, col, alpha)
    c.set_line_width(width)
    c.stroke()
    c.save()
    c.translate(-0.7, -0.9)
    _poly(c, pts)
    c.set_source_rgba(1, 0.55, 0.5, 0.35 * alpha)
    c.set_line_width(width * 0.35)
    c.stroke()
    c.restore()


def string_snap(c, p0, p1, t, t_snap, sag=0.06, width=3.4):
    """Fio inteiro até t_snap; depois arrebenta no meio e as pontas caem balançando."""
    if t < t_snap:
        string(c, p0, p1, 1, sag, width)
        return
    u = seg(t, t_snap, t_snap + 0.9)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + L * sag)
    sw = math.sin(u * 9) * (1 - u) * 0.35
    for p, sgn in ((p0, -1), (p1, 1)):
        hang = (p[0] + sgn * L * 0.05 + sgn * sw * L * 0.15, p[1] + L * 0.42)
        e = eout(u)
        q = (lerp(mid[0], hang[0], e), lerp(mid[1], hang[1], e))
        string(c, p, q, 1, 0.02 + 0.08 * (1 - e), width)


def marker_ellipse(c, cx, cy, rx, ry, prog, seed=1, width=7.0, col=HOT, rot=0.0, alpha=0.95):
    if prog <= 0.001:
        return
    rnd = random.Random(seed)
    a0 = rnd.uniform(0, 2 * math.pi)
    n = 110
    pts = []
    rr = math.radians(rot)
    for i in range(int(n * clamp(prog)) + 1):
        u = i / n
        a = a0 + u * 2 * math.pi * 1.13
        wob = 1 + 0.05 * math.sin(3 * a + seed) + 0.025 * math.sin(7 * a + seed * 2)
        sh = 1 - 0.07 * u
        x, y = rx * wob * sh * math.cos(a), ry * wob * sh * math.sin(a)
        pts.append((cx + x * math.cos(rr) - y * math.sin(rr), cy + x * math.sin(rr) + y * math.cos(rr)))
    if len(pts) < 2:
        return
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    _poly(c, pts)
    rgb(c, col, alpha)
    c.set_line_width(width)
    c.stroke()
    c.save()
    c.translate(width * 0.18, -width * 0.12)
    _poly(c, pts)
    c.set_source_rgba(1, 0.55, 0.5, alpha * 0.35)
    c.set_line_width(width * 0.35)
    c.stroke()
    c.restore()


def marker_line(c, p0, p1, prog, width=7.0, col=HOT, bend=0.04, alpha=0.95, seed=2):
    if prog <= 0.001:
        return
    pts = _bez(p0, (p1[0], p1[1]), -bend, 30, clamp(prog))
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    _poly(c, pts)
    rgb(c, col, alpha)
    c.set_line_width(width)
    c.stroke()


def marker_arrow(c, p0, p1, prog, width=7.0, col=HOT, alpha=0.95):
    marker_line(c, p0, p1, seg(prog, 0, 0.75), width, col, 0.08, alpha)
    hp = seg(prog, 0.75, 1.0)
    if hp > 0:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        L = 34 * hp
        for s in (-1, 1):
            a = ang + math.pi + s * 0.5
            marker_line(c, p1, (p1[0] + L * math.cos(a), p1[1] + L * math.sin(a)), 1, width, col, 0, alpha)


# ───────────────────────── texto ─────────────────────────
def font(c, face, size, bold=False, italic=False):
    c.select_font_face(face, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def text_width(c, s, spacing=0.0):
    if not spacing:
        return c.text_extents(s).x_advance
    return sum(c.text_extents(ch).x_advance for ch in s) + spacing * max(0, len(s) - 1)


def text(c, s, x, y, size, face=SERIF, col=WHITE, alpha=1.0, align="center", spacing=0.0, bold=False,
         italic=False, shadow=0.0):
    if alpha <= 0.002 or not s:
        return 0
    font(c, face, size, bold, italic)
    w = text_width(c, s, spacing)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    if shadow:
        c.save()
        c.translate(size * 0.04, size * 0.06)
        _draw_text(c, s, x0, y, spacing)
        c.set_source_rgba(0, 0, 0, alpha * shadow)
        c.fill()
        c.restore()
    _draw_text(c, s, x0, y, spacing)
    rgb(c, col, alpha)
    c.fill()
    return w


def _draw_text(c, s, x0, y, spacing):
    if not spacing:
        c.move_to(x0, y)
        c.text_path(s)
        return
    x = x0
    for ch in s:
        c.move_to(x, y)
        c.text_path(ch)
        x += c.text_extents(ch).x_advance + spacing


def typed(c, s, x, y, size, prog, face=MONO, col=WHITE, alpha=1.0, t=0.0, cursor=True, align="left",
          spacing=0.0, bold=False):
    n = int(round(len(s) * clamp(prog)))
    font(c, face, size, bold)
    wfull = text_width(c, s, spacing)
    x0 = x - wfull / 2 if align == "center" else (x - wfull if align == "right" else x)
    sub = s[:n]
    if sub:
        text(c, sub, x0, y, size, face, col, alpha, "left", spacing, bold)
    if cursor and alpha > 0 and (prog < 1 or (int(t * 2.4) % 2 == 0)):
        font(c, face, size, bold)
        cx = x0 + (text_width(c, sub, spacing) + (spacing if sub else 0))
        c.rectangle(cx + 2, y - size * 0.78, size * 0.5, size * 0.95)
        rgb(c, col, alpha * 0.85)
        c.fill()


def label_tag(c, s, x, y, size=26, col=HOT, bg=(0.05, 0.06, 0.07), alpha=1.0, prog=1.0, rot=0.0, t=0.0):
    """Etiqueta de prova: retângulo escuro com texto mono vermelho que se digita."""
    if alpha <= 0:
        return
    font(c, MONO, size, True)
    w = text_width(c, s, 1.5) + size * 1.1
    h = size * 1.7
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    wi = w * eout(seg(prog, 0, 0.35))
    c.rectangle(0, -h / 2, wi, h)
    c.set_source_rgba(bg[0], bg[1], bg[2], 0.92 * alpha)
    c.fill()
    c.rectangle(0, -h / 2, 5, h)
    rgb(c, col, alpha)
    c.fill()
    typed(c, s, size * 0.6, size * 0.36, size, seg(prog, 0.2, 1.0), MONO, col, alpha, t, cursor=False, spacing=1.5,
          bold=True)
    c.restore()


def note(c, s, x, y, size, rot=-4, col=HOT, alpha=1.0, prog=1.0):
    """Anotação à mão (marcador)."""
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    n = int(round(len(s) * clamp(prog)))
    text(c, s[:n], 0, 0, size, MARK, col, alpha, "left")
    c.restore()


# ───────────────────────── carimbo ─────────────────────────
def stamp(c, name, x, y, w, rot, t, t_hit, alpha=1.0):
    if t < t_hit - 0.12 or alpha <= 0:
        return
    m = META[name]
    k = w / m["w"]
    if t < t_hit:
        u = seg(t, t_hit - 0.12, t_hit)
        s = lerp(2.3, 1.0, ein(u))
        a = alpha * (0.25 + 0.75 * ein(u))
    else:
        s = 1.0 + 0.018 * eout(seg(t, t_hit, t_hit + 0.5))
        a = alpha
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    c.scale(k * s, k * s)
    c.set_source_surface(surf(name), -m["w"] / 2, -m["h"] / 2)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(a)
    c.restore()


# ───────────────────────── números ─────────────────────────
def wheel(c, x, y, size, value, face=SERIF, col=WHITE, alpha=1.0):
    """Um dígito 'rolando': value float (ex. 4.3 = entre 4 e 5)."""
    v0 = int(math.floor(value)) % 10
    fr = value - math.floor(value)
    font(c, face, size)
    dw = c.text_extents("0").x_advance
    c.save()
    c.rectangle(x - dw * 0.1, y - size * 0.92, dw * 1.2, size * 1.12)
    c.clip()
    for d, off in ((v0, -fr), ((v0 + 1) % 10, 1 - fr)):
        text(c, str(d), x + dw / 2, y + off * size * 1.05, size, face, col, alpha)
    c.restore()
    return dw


def number_roll(c, value, x, y, size, face=SERIF, col=WHITE, alpha=1.0, align="center", digits=None):
    """Número inteiro com o último dígito rolando suave."""
    iv = int(math.floor(value))
    s = str(iv) if digits is None else str(iv).rjust(digits, "0")
    font(c, face, size)
    dw = c.text_extents("0").x_advance
    total = dw * len(s)
    x0 = x - total / 2 if align == "center" else (x - total if align == "right" else x)
    for i, ch in enumerate(s[:-1]):
        text(c, ch, x0 + i * dw + dw / 2, y, size, face, col, alpha)
    wheel(c, x0 + (len(s) - 1) * dw, y, size, (iv % 10) + (value - iv), face, col, alpha)
    return total


# ───────────────────────── objetos ─────────────────────────
def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def soft_shadow(c, x, y, w, h, r, spread=40, a=0.5, steps=10):
    for i in range(steps):
        k = (i + 1) / steps
        rrect(c, x - spread * k + spread * 0.3, y - spread * k + spread * 0.5, w + 2 * spread * k, h + 2 * spread * k,
              r + spread * k)
        c.set_source_rgba(0, 0, 0, a / steps * (1 - k * 0.5))
        c.fill()


def phone(c, x, y, h, rot, t, screen_fn, glow=0.0):
    """Celular de frente, centro (x,y), altura h. screen_fn(c, sx, sy, sw, sh) desenha a tela."""
    w = h * 0.49
    r = h * 0.07
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    soft_shadow(c, -w / 2, -h / 2, w, h, r, spread=h * 0.06, a=0.6)
    rrect(c, -w / 2, -h / 2, w, h, r)
    g = cairo.LinearGradient(-w / 2, -h / 2, w / 2, h / 2)
    g.add_color_stop_rgb(0, 0.16, 0.17, 0.19)
    g.add_color_stop_rgb(0.5, 0.06, 0.065, 0.07)
    g.add_color_stop_rgb(1, 0.13, 0.14, 0.15)
    c.set_source(g)
    c.fill()
    rrect(c, -w / 2 + 2, -h / 2 + 2, w - 4, h - 4, r - 2)
    c.set_source_rgba(1, 1, 1, 0.10)
    c.set_line_width(2)
    c.stroke()
    b = h * 0.022
    sx, sy, sw, sh = -w / 2 + b, -h / 2 + b, w - 2 * b, h - 2 * b
    c.save()
    rrect(c, sx, sy, sw, sh, r * 0.8)
    c.clip()
    c.set_source_rgb(0, 0, 0)
    c.paint()
    screen_fn(c, sx, sy, sw, sh)
    # reflexo no vidro
    g = cairo.LinearGradient(sx, sy, sx + sw, sy + sh)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.07)
    g.add_color_stop_rgba(0.45, 1, 1, 1, 0.0)
    c.set_source(g)
    c.paint()
    c.restore()
    rrect(c, -h * 0.06, -h / 2 + b + h * 0.012, h * 0.12, h * 0.028, h * 0.014)  # ilha
    c.set_source_rgb(0, 0, 0)
    c.fill()
    c.restore()


def verified(c, x, y, r):
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source_rgb(0.22, 0.6, 0.98)
    c.fill()
    c.move_to(x - r * 0.45, y)
    c.line_to(x - r * 0.1, y + r * 0.38)
    c.line_to(x + r * 0.5, y - r * 0.35)
    c.set_source_rgb(1, 1, 1)
    c.set_line_width(r * 0.28)
    c.stroke()


def heart(c, x, y, s, fill=False, col=(1, 1, 1)):
    c.save()
    c.translate(x, y)
    c.scale(s / 24, s / 24)
    c.move_to(0, 8)
    c.curve_to(-14, -2, -10, -14, 0, -6)
    c.curve_to(10, -14, 14, -2, 0, 8)
    c.close_path()
    c.restore()
    rgb(c, col)
    if fill:
        c.fill()
    else:
        c.set_line_width(2)
        c.stroke()


def glow_line(c, p0, p1, width, col=(1, 0.2, 0.15), core=(1, 0.95, 0.9), alpha=1.0):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for wk, a, cc in ((7.0, 0.05, col), (4.0, 0.09, col), (2.2, 0.2, col), (1.2, 0.55, col), (0.45, 1.0, core)):
        c.move_to(*p0)
        c.line_to(*p1)
        c.set_source_rgba(cc[0], cc[1], cc[2], a * alpha)
        c.set_line_width(width * wk)
        c.stroke()


def glow(c, x, y, r, col=(1, 0.3, 0.2), a=0.6):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()


def dust(c, t, n=40, seed=3, a=0.35):
    """Poeira em suspensão na luz (primeiro plano, profundidade)."""
    rnd = random.Random(seed)
    for i in range(n):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        sp = rnd.uniform(4, 16)
        r = rnd.uniform(0.8, 3.2)
        ph = rnd.uniform(0, 6.28)
        x = (x0 + t * sp * rnd.uniform(-1, 1) + 18 * math.sin(t * 0.3 + ph)) % W
        y = (y0 - t * sp * 0.6 + 12 * math.cos(t * 0.25 + ph)) % H
        al = a * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 0.8 + ph)))
        g = cairo.RadialGradient(x, y, 0, x, y, r * 2.4)
        g.add_color_stop_rgba(0, 1, 0.96, 0.9, al)
        g.add_color_stop_rgba(1, 1, 0.96, 0.9, 0)
        c.set_source(g)
        c.arc(x, y, r * 2.4, 0, 2 * math.pi)
        c.fill()


# ───────────────────────── pós-produção (numpy) ─────────────────────────
_GR = None
_VIG = None


def _post_init():
    global _GR, _VIG
    if _GR is None:
        r = np.random.default_rng(5)
        from scipy.ndimage import gaussian_filter
        _GR = [gaussian_filter(r.normal(0, 5.0, (H, W)).astype(np.float32), 0.65) for _ in range(6)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _VIG = (1 - 0.55 * np.clip(d, 0, 1) ** 2.3).astype(np.float32)


def post(surface, i, fx):
    """fx: flash (0-1), ca (px), glitch (0-1), fade (0-1 preto), grain (mult), tint."""
    _post_init()
    surface.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=surface.get_data())
    img = buf[:, :, :3].astype(np.float32)
    img *= _VIG[..., None]
    img += _GR[i % 6][..., None] * fx.get("grain", 1.0)
    ca = fx.get("ca", 0)
    if ca >= 1:
        k = int(ca)
        img[:, k:, 2] = img[:, :-k, 2]      # R (BGRA: índice 2) desloca p/ direita
        img[:, :-k, 0] = img[:, k:, 0]      # B p/ esquerda
    g = fx.get("glitch", 0)
    if g > 0.01:
        rnd = np.random.default_rng(i * 7 + 1)
        for _ in range(int(3 + g * 10)):
            y0 = int(rnd.integers(0, H - 40))
            hh = int(rnd.integers(6, 60))
            sh = int(rnd.integers(-80, 80) * g)
            img[y0:y0 + hh] = np.roll(img[y0:y0 + hh], sh, axis=1)
        k = int(6 + 14 * g)
        img[:, k:, 2] = img[:, :-k, 2]
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
