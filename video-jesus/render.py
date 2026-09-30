"""
A História de Jesus — vídeo em motion graphics (1920x1080, 30 fps, ~2 min).

Tudo é desenhado proceduralmente com Cairo (ilustrações vetoriais) e
codificado com ffmpeg. A trilha sonora é sintetizada por audio.py.

Uso:
    pip install pycairo numpy imageio-ffmpeg
    python3 audio.py          # gera trilha.wav
    python3 render.py         # gera jesus_historia.mp4
    python3 render.py --frames 12.5 40 97   # só exporta PNGs de teste
"""
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

import cairo

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
TAU = math.tau

SERIF = "Cinzel"
TITLE = "Italiana"
SANS = "Montserrat"
GOLD = "#FFD36B"


# ───────────────────────── utilidades ─────────────────────────
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eio(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def eout(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def eback(t):
    t = clamp(t)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(c1, c2, t):
    a, b = hexc(c1) if isinstance(c1, str) else c1, hexc(c2) if isinstance(c2, str) else c2
    return tuple(lerp(a[i], b[i], clamp(t)) for i in range(3))


def rgb(c, col, a=1.0):
    col = hexc(col) if isinstance(col, str) else col
    c.set_source_rgba(col[0], col[1], col[2], a)


def sky(c, stops, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for pos, col in stops:
        col = hexc(col) if isinstance(col, str) else col
        g.add_color_stop_rgb(pos, *col)
    c.set_source(g)
    c.paint()


def glow(c, x, y, r, col, a=1.0, core=0.0):
    col = hexc(col) if isinstance(col, str) else col
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    if core:
        g.add_color_stop_rgba(core, col[0], col[1], col[2], a * 0.6)
    g.add_color_stop_rgba(0.45, col[0], col[1], col[2], a * 0.25)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g)
    c.arc(x, y, r, 0, TAU)
    c.fill()


def rays(c, x, y, n, length, rot, col, a, width=0.09, rnd_seed=1):
    col = hexc(col) if isinstance(col, str) else col
    rnd = random.Random(rnd_seed)
    for i in range(n):
        ang = rot + i * TAU / n + rnd.uniform(-0.1, 0.1)
        w = width * rnd.uniform(0.5, 1.3)
        L = length * rnd.uniform(0.6, 1.0)
        g = cairo.RadialGradient(x, y, 0, x, y, L)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
        g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        c.set_source(g)
        c.move_to(x, y)
        c.line_to(x + math.cos(ang - w / 2) * L, y + math.sin(ang - w / 2) * L)
        c.line_to(x + math.cos(ang + w / 2) * L, y + math.sin(ang + w / 2) * L)
        c.close_path()
        c.fill()


_STARS = [(random.Random(i).uniform(0, W), random.Random(i * 7 + 3).uniform(0, H),
           random.Random(i * 13 + 5).uniform(0.6, 2.4), random.Random(i * 17 + 1).uniform(0, TAU))
          for i in range(260)]


def stars(c, t, maxy=H * 0.7, a=1.0, n=260):
    for x, y, r, ph in _STARS[:n]:
        if y > maxy:
            continue
        tw = 0.55 + 0.45 * math.sin(t * (1.5 + r) + ph)
        c.set_source_rgba(1, 0.97, 0.9, a * tw * (0.4 + 0.25 * r))
        c.arc(x, y, r, 0, TAU)
        c.fill()


def ridge(c, y0, amp, freq, phase, col, a=1.0, seed=0, xoff=0.0):
    rnd = random.Random(seed)
    comps = [(rnd.uniform(0.6, 1.6) * freq, rnd.uniform(0, TAU), rnd.uniform(0.3, 1.0)) for _ in range(4)]
    tot = sum(x[2] for x in comps)
    c.move_to(-10, H + 10)
    for x in range(-10, W + 31, 30):
        xx = x + xoff
        y = y0 + amp * sum(s * math.sin(xx * f / 1000 * TAU + p + phase) for f, p, s in comps) / tot
        c.line_to(x, y)
    c.line_to(W + 30, H + 10)
    c.close_path()
    rgb(c, col, a)
    c.fill()


def particles(c, t, n, seed, col, a=1.0, rise=40, size=(1, 3.5), area=(0, 0, W, H)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = area
    hh = y1 - y0
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        sp = rnd.uniform(0.5, 1.5) * rise
        r = rnd.uniform(*size)
        ph = rnd.uniform(0, TAU)
        yy = y0 + ((y - y0 - t * sp) % hh)
        xx = x + 18 * math.sin(t * 0.8 + ph)
        tw = 0.5 + 0.5 * math.sin(t * 2 + ph)
        rgb(c, col, a * tw)
        c.arc(xx, yy, r, 0, TAU)
        c.fill()


def cloud(c, x, y, s, col, a=1.0, seed=0):
    rnd = random.Random(seed)
    rgb(c, col, a)
    for i in range(7):
        c.new_sub_path()
        c.arc(x + rnd.uniform(-1.2, 1.2) * s, y + rnd.uniform(-0.25, 0.25) * s, s * rnd.uniform(0.45, 0.8), 0, TAU)
    c.fill()


def vignette(c, a=0.6):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, a)
    c.set_source(g)
    c.paint()


def overlay(c, col, a):
    if a <= 0:
        return
    rgb(c, col, clamp(a))
    c.paint()


# ───────────────────────── personagens ─────────────────────────
def _robe(c):
    c.move_to(-0.045, -0.80)
    c.curve_to(-0.09, -0.795, -0.13, -0.785, -0.145, -0.74)
    c.curve_to(-0.17, -0.55, -0.19, -0.25, -0.235, 0)
    c.line_to(0.235, 0)
    c.curve_to(0.19, -0.25, 0.17, -0.55, 0.145, -0.74)
    c.curve_to(0.13, -0.785, 0.09, -0.795, 0.045, -0.80)
    c.close_path()


def _arm(c, sx, sy, ex, ey, w0=0.055, w1=0.032):
    ang = math.atan2(ey - sy, ex - sx)
    nx, ny = -math.sin(ang), math.cos(ang)
    c.move_to(sx + nx * w0, sy + ny * w0)
    c.line_to(ex + nx * w1, ey + ny * w1)
    c.line_to(ex - nx * w1, ey - ny * w1)
    c.line_to(sx - nx * w0, sy - ny * w0)
    c.close_path()
    c.fill()
    c.arc(ex, ey, 0.03, 0, TAU)


POSES = {
    "stand": (None, None),
    "open": ((-0.44, -0.62), (0.44, -0.62)),
    "raised": ((-0.34, -1.1), (0.34, -1.1)),
    "bless": (None, (0.3, -1.02)),
    "cross": ((-0.5, -0.74), (0.5, -0.74)),
    "reach": (None, (0.42, -0.5)),
}


def halo(c, x, y, r, a=1.0, col=GOLD):
    glow(c, x, y, r * 3.2, col, 0.55 * a)
    c.set_line_width(max(1.5, r * 0.12))
    rgb(c, col, 0.9 * a)
    c.arc(x, y, r * 1.35, 0, TAU)
    c.stroke()


def figure(c, x, y, h, col="#140c1c", pose="stand", veil=False, halo_a=0.0, a=1.0,
           staff=False, flip=False, hands=None):
    if halo_a > 0:
        halo(c, x, y - 0.89 * h, 0.075 * h, halo_a)
    c.save()
    c.translate(x, y)
    c.scale(-h if flip else h, h)
    rgb(c, col, a)
    c.save()
    if pose == "cross":
        c.scale(0.62, 1)
    _robe(c)
    c.fill()
    c.restore()
    c.arc(0, -0.89, 0.075, 0, TAU)
    c.fill()
    c.rectangle(-0.03, -0.84, 0.06, 0.06)
    c.fill()
    l, r = hands if hands else POSES[pose]
    if l:
        _arm(c, -0.12, -0.74, *l)
        c.fill()
    if r:
        _arm(c, 0.12, -0.74, *r)
        c.fill()
    if veil:
        c.move_to(0, -0.99)
        c.curve_to(-0.1, -0.99, -0.13, -0.9, -0.15, -0.8)
        c.curve_to(-0.2, -0.6, -0.24, -0.4, -0.27, -0.25)
        c.line_to(0.27, -0.25)
        c.curve_to(0.24, -0.4, 0.2, -0.6, 0.15, -0.8)
        c.curve_to(0.13, -0.9, 0.1, -0.99, 0, -0.99)
        c.close_path()
        c.fill()
    if staff:
        c.set_line_width(0.028)
        c.move_to(0.3, -1.08)
        c.curve_to(0.36, -1.14, 0.42, -1.08, 0.38, -1.0)
        c.move_to(0.3, -1.08)
        c.line_to(0.3, 0)
        c.stroke()
        c.set_line_width(0.06)
        c.move_to(0.12, -0.72)
        c.line_to(0.3, -0.5)
        c.stroke()
    c.restore()


def kneel(c, x, y, h, col="#140c1c", veil=False, halo_a=0.0, a=1.0, flip=False, praying=True):
    hx, hy = 0.07, -0.63
    if halo_a > 0:
        halo(c, x + (-hx if flip else hx) * h, y + hy * h, 0.075 * h, halo_a)
    c.save()
    c.translate(x, y)
    c.scale(-h if flip else h, h)
    rgb(c, col, a)
    c.move_to(0.02, -0.55)
    c.curve_to(-0.1, -0.55, -0.2, -0.45, -0.24, -0.25)
    c.curve_to(-0.27, -0.12, -0.3, -0.04, -0.34, 0)
    c.line_to(0.3, 0)
    c.curve_to(0.3, -0.08, 0.27, -0.14, 0.2, -0.17)
    c.curve_to(0.14, -0.22, 0.14, -0.4, 0.12, -0.5)
    c.close_path()
    c.fill()
    c.arc(hx, hy, 0.075, 0, TAU)
    c.fill()
    if praying:
        c.move_to(0.1, -0.5)
        c.line_to(0.24, -0.46)
        c.line_to(0.26, -0.58)
        c.line_to(0.21, -0.6)
        c.line_to(0.12, -0.42)
        c.close_path()
        c.fill()
    if veil:
        c.move_to(hx, hy - 0.1)
        c.curve_to(hx - 0.12, hy - 0.1, hx - 0.16, hy, hx - 0.2, hy + 0.12)
        c.curve_to(hx - 0.28, hy + 0.3, hx - 0.33, hy + 0.45, hx - 0.36, hy + 0.6)
        c.line_to(hx - 0.1, hy + 0.3)
        c.curve_to(hx + 0.05, hy + 0.1, hx + 0.1, hy, hx, hy - 0.1)
        c.close_path()
    c.fill()
    c.restore()


def wings(c, x, y, h, t, col, a):
    flap = math.sin(t * 3.2) * 0.08
    c.save()
    c.translate(x, y)
    c.scale(h, h)
    rgb(c, col, a)
    for s in (-1, 1):
        c.move_to(s * 0.06, -0.72)
        c.curve_to(s * 0.35, -1.05 - flap, s * 0.62, -1.25 - flap, s * 0.72, -1.2 - flap)
        c.curve_to(s * 0.62, -0.95, s * 0.5, -0.65, s * 0.22, -0.3)
        for k in range(4):
            yy = -0.35 - k * 0.14
            c.line_to(s * (0.26 + k * 0.08), yy + 0.05)
            c.line_to(s * (0.2 + k * 0.06), yy)
        c.close_path()
        c.fill()
    c.restore()


def dove(c, x, y, s, t, col="#ffffff", a=1.0):
    f = math.sin(t * 9) * 0.6
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rgb(c, col, a)
    c.save()
    c.scale(1, 0.55)
    c.arc(0, 0, 0.35, 0, TAU)
    c.restore()
    c.fill()
    c.arc(0.32, -0.12, 0.13, 0, TAU)
    c.fill()
    c.move_to(-0.3, 0)
    c.line_to(-0.62, -0.12)
    c.line_to(-0.6, 0.12)
    c.close_path()
    c.fill()
    for sgn in (-1, 1):
        c.move_to(-0.1, -0.05)
        c.curve_to(-0.2, -0.6 * f * sgn - 0.3, 0.1, -0.9 * f * sgn - 0.5, 0.3, -0.05)
        c.close_path()
        c.fill()
    c.restore()


def camel(c, x, y, s, t, col="#1a0f22", rider=True, crown=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rgb(c, col)
    c.move_to(-0.55, -0.62)
    c.curve_to(-0.5, -0.9, -0.3, -0.95, -0.2, -0.78)
    c.curve_to(-0.1, -1.0, 0.15, -1.0, 0.25, -0.75)
    c.curve_to(0.35, -0.7, 0.42, -0.8, 0.5, -1.05)
    c.line_to(0.66, -1.08)
    c.line_to(0.7, -1.0)
    c.line_to(0.58, -0.98)
    c.curve_to(0.5, -0.7, 0.4, -0.52, 0.28, -0.5)
    c.line_to(-0.5, -0.48)
    c.close_path()
    c.fill()
    c.set_line_width(0.07)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i, lx in enumerate((-0.45, -0.32, 0.12, 0.25)):
        sw = math.sin(t * 5 + i * math.pi) * 0.1
        c.move_to(lx, -0.52)
        c.line_to(lx + sw, 0)
        c.stroke()
    if rider:
        c.move_to(-0.15, -0.9)
        c.line_to(-0.2, -1.35)
        c.line_to(0.05, -1.35)
        c.line_to(0.02, -0.9)
        c.close_path()
        c.fill()
        c.arc(-0.08, -1.45, 0.09, 0, TAU)
        c.fill()
        if crown:
            c.move_to(-0.16, -1.53)
            for k in range(4):
                c.line_to(-0.16 + k * 0.055 + 0.027, -1.65)
                c.line_to(-0.16 + (k + 1) * 0.055, -1.53)
            c.close_path()
            c.fill()
    c.restore()


def olive_tree(c, x, y, s, col, seed=0, sway=0.0):
    rnd = random.Random(seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rgb(c, col)
    c.move_to(-0.08, 0)
    c.curve_to(-0.02, -0.25, -0.15, -0.45, -0.05, -0.7)
    c.line_to(0.05, -0.7)
    c.curve_to(0.0, -0.45, 0.12, -0.25, 0.1, 0)
    c.close_path()
    c.fill()
    for _ in range(9):
        c.new_sub_path()
        c.arc(rnd.uniform(-0.45, 0.45) + sway, rnd.uniform(-1.05, -0.65), rnd.uniform(0.16, 0.3), 0, TAU)
    c.fill()
    c.restore()


def palm(c, x, y, s, col, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rgb(c, col)
    c.set_line_width(0.05)
    c.move_to(0, 0)
    c.curve_to(0.05, -0.4, 0.02, -0.7, 0.1, -1.0)
    c.stroke()
    for k in range(7):
        ang = -math.pi + k * math.pi / 6 + 0.05 * math.sin(t + k)
        c.move_to(0.1, -1.0)
        ex, ey = 0.1 + math.cos(ang) * 0.5, -1.0 + math.sin(ang) * 0.3 + 0.2
        c.curve_to(0.1 + math.cos(ang) * 0.25, -1.1, ex, ey - 0.1, ex, ey)
        c.curve_to(ex, ey - 0.02, 0.1 + math.cos(ang) * 0.25, -1.05, 0.1, -0.98)
        c.fill()
    c.restore()


def cross_shape(c, x, y, h, w=None, col="#0d0710", a=1.0):
    w = w or h * 0.08
    rgb(c, col, a)
    c.rectangle(x - w / 2, y - h, w, h)
    c.rectangle(x - h * 0.33, y - h * 0.8, h * 0.66, w * 0.9)
    c.fill()


def town(c, y, col, seed=3, scale=1.0, lit=0.0, t=0.0):
    rnd = random.Random(seed)
    x = -40
    wins = []
    while x < W + 40:
        w = rnd.uniform(70, 150) * scale
        h = rnd.uniform(60, 170) * scale
        rgb(c, col)
        c.rectangle(x, y - h, w, h + 400)
        c.fill()
        if rnd.random() < 0.3:
            c.arc(x + w / 2, y - h, w * 0.35, math.pi, TAU)
            c.fill()
        if rnd.random() < 0.6:
            wins.append((x + rnd.uniform(0.2, 0.7) * w, y - h * rnd.uniform(0.3, 0.7), rnd.uniform(0, TAU)))
        x += w + rnd.uniform(-10, 30)
    if lit:
        for wx, wy, ph in wins:
            fl = 0.8 + 0.2 * math.sin(t * 6 + ph)
            glow(c, wx, wy, 26 * scale, "#ffb347", 0.5 * lit * fl)
            rgb(c, "#ffcf7a", lit * fl)
            c.rectangle(wx - 5 * scale, wy - 8 * scale, 10 * scale, 14 * scale)
            c.fill()


def starburst(c, x, y, r, rot, a=1.0, col="#fffbe8"):
    glow(c, x, y, r * 6, "#fff2c4", 0.45 * a)
    glow(c, x, y, r * 2, "#ffffff", 0.8 * a)
    rgb(c, col, a)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    for k, L in ((0, 1.0), (1, 0.55)):
        c.save()
        c.rotate(k * math.pi / 4)
        c.move_to(0, -r * 3 * L)
        c.line_to(r * 0.22, -r * 0.22)
        c.line_to(r * 3 * L, 0)
        c.line_to(r * 0.22, r * 0.22)
        c.line_to(0, r * 3 * L)
        c.line_to(-r * 0.22, r * 0.22)
        c.line_to(-r * 3 * L, 0)
        c.line_to(-r * 0.22, -r * 0.22)
        c.close_path()
        c.fill()
        c.restore()
    c.restore()


def lightning(c, x, y0, y1, seed, a):
    if a <= 0:
        return
    rnd = random.Random(seed)
    pts = [(x, y0)]
    yy = y0
    xx = x
    while yy < y1:
        yy += rnd.uniform(30, 70)
        xx += rnd.uniform(-45, 45)
        pts.append((xx, yy))
    for lw, al in ((22, 0.15), (9, 0.35), (3.5, 1.0)):
        c.set_line_width(lw)
        c.set_source_rgba(0.9, 0.93, 1, a * al)
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.stroke()


def water(c, y0, amp, t, col, a=1.0, freq=1.0, speed=1.0, phase=0.0):
    c.move_to(-10, H + 10)
    for x in range(-10, W + 21, 20):
        y = y0 + amp * (math.sin(x / 180 * freq + t * 1.6 * speed + phase)
                        + 0.5 * math.sin(x / 67 * freq - t * 2.3 * speed + phase * 2))
        c.line_to(x, y)
    c.line_to(W + 20, H + 10)
    c.close_path()
    rgb(c, col, a)
    c.fill()


def text_center(c, s, x, y, size, face=SERIF, col="#ffffff", a=1.0, spacing=0.0, bold=True):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    advs = [c.text_extents(ch).x_advance for ch in s]
    total = sum(advs) + spacing * (len(s) - 1)
    xx = x - total / 2
    rgb(c, col, a)
    for ch, adv in zip(s, advs):
        c.move_to(xx, y)
        c.show_text(ch)
        xx += adv + spacing
    return total


def title_text(c, s, x, y, size, spacing=0.0, a=1.0, shine=-1.0, glow_a=0.6, face=TITLE,
               top="#fff6dc", mid="#ffe3a3", bottom="#e0a84a", outline=True):
    """Título dourado com degradê, halo e reflexo de luz (shine de 0 a 1 percorre o texto)."""
    if a <= 0:
        return
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    advs = [c.text_extents(ch).x_advance for ch in s]
    total = sum(advs) + spacing * (len(s) - 1)
    c.new_path()
    xx = x - total / 2
    for ch, adv in zip(s, advs):
        c.move_to(xx, y)
        c.text_path(ch)
        xx += adv + spacing
    path = c.copy_path()
    x0, x1 = x - total / 2, x + total / 2
    for lw, al in ((size * 0.22, 0.05), (size * 0.12, 0.08), (size * 0.05, 0.14)):
        c.new_path()
        c.append_path(path)
        c.set_line_width(lw)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_source_rgba(1, 0.78, 0.4, al * glow_a * a)
        c.stroke()
    g = cairo.LinearGradient(0, y - size * 0.75, 0, y)
    for pos, col in ((0, top), (0.55, mid), (1, bottom)):
        cc = hexc(col)
        g.add_color_stop_rgba(pos, cc[0], cc[1], cc[2], a)
    c.new_path()
    c.append_path(path)
    c.set_source(g)
    if outline:
        c.fill_preserve()
        c.set_line_width(max(1.0, size * 0.008))
        c.set_source_rgba(1, 0.97, 0.88, 0.6 * a)
        c.stroke()
    else:
        c.fill()
    if 0 <= shine <= 1:
        c.save()
        c.new_path()
        c.append_path(path)
        c.clip()
        sx = lerp(x0 - size, x1 + size, shine)
        sg = cairo.LinearGradient(sx - size * 0.5, 0, sx + size * 0.5, 0)
        sg.add_color_stop_rgba(0, 1, 1, 1, 0)
        sg.add_color_stop_rgba(0.5, 1, 1, 1, 0.95 * a)
        sg.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(sg)
        c.paint()
        c.restore()
    c.new_path()
    return total

# ───────────────────────── idioma ─────────────────────────
LANG = os.environ.get("VIDEO_LANG", "pt")

EN = {
    "DO NASCIMENTO À RESSURREIÇÃO": "FROM BIRTH TO RESURRECTION",
    "DIA 1": "DAY 1", "DIA 2": "DAY 2", "DIA 3": "DAY 3",
    "ELE VIVE": "HE LIVES",
    "Siga nosso canal": "Subscribe to our channel",
    "para mais histórias que transformam vidas": "for more stories that transform lives",
    "INSCREVA-SE": "SUBSCRIBE", "INSCRITO": "SUBSCRIBED",
    # capítulos
    "I · A PROMESSA": "I · THE PROMISE", "II · O NASCIMENTO": "II · THE BIRTH",
    "III · A ESTRELA": "III · THE STAR", "IV · O BATISMO": "IV · THE BAPTISM",
    "V · OS MILAGRES": "V · THE MIRACLES", "VI · A MENSAGEM": "VI · THE MESSAGE",
    "VII · A ÚLTIMA CEIA": "VII · THE LAST SUPPER", "VIII · GETSÊMANI": "VIII · GETHSEMANE",
    "IX · A PAIXÃO": "IX · THE PASSION", "X · A CRUZ": "X · THE CROSS",
    "XI · O SILÊNCIO": "XI · THE SILENCE", "XII · A RESSURREIÇÃO": "XII · THE RESURRECTION",
    # legendas
    "Há dois mil anos, uma história mudaria o mundo *para sempre*.":
        "Two thousand years ago, a story would change the world *forever*.",
    "Em Nazaré, um anjo aparece a uma jovem chamada *Maria*.":
        "In Nazareth, an angel appears to a young woman named *Mary*.",
    "“Você terá um filho… e o chamará *Jesus*.”": "“You will bear a son… and call him *Jesus*.”",
    "Em *Belém*, sem lugar na hospedaria…": "In *Bethlehem*, with no room at the inn…",
    "…o Filho de Deus nasce numa simples *manjedoura*.": "…the Son of God is born in a simple *manger*.",
    "Uma *estrela* guia magos do Oriente até o Rei recém-nascido.":
        "A *star* guides wise men from the East to the newborn King.",
    "Aos 30 anos, no rio *Jordão*, os céus se abrem:": "At 30, in the *Jordan* River, the heavens open:",
    "“Este é o meu *Filho amado*.”": "“This is my *beloved Son*.”",
    "Ele cura *cegos*. Faz paralíticos *andarem*.": "He heals the *blind*. Makes the paralyzed *walk*.",
    "Caminha sobre as águas… e a *tempestade* se cala.": "He walks on water… and the *storm* falls silent.",
    "Multidões o seguem. Ele fala de *amor*, *perdão* e *esperança*.":
        "Crowds follow him. He speaks of *love*, *forgiveness* and *hope*.",
    "“Eu sou o caminho, a verdade e a *vida*.”": "“I am the way, the truth and the *life*.”",
    "Na última ceia, ele parte o pão com os *doze*.": "At the last supper, he breaks bread with the *twelve*.",
    "“Um de vocês vai me *trair*.”": "“One of you will *betray* me.”",
    "No jardim, ele ora em *agonia*.": "In the garden, he prays in *agony*.",
    "Judas chega com soldados… e o entrega com um *beijo*.":
        "Judas arrives with soldiers… and betrays him with a *kiss*.",
    "Condenado. Açoitado. *Coroado de espinhos*.": "Condemned. Scourged. *Crowned with thorns*.",
    "Carrega a própria cruz rumo ao *Calvário*.": "He carries his own cross to *Calvary*.",
    "Pregado na cruz, ele clama: “Pai, *perdoa-lhes*.”":
        "Nailed to the cross, he cries: “Father, *forgive them*.”",
    "“Está *consumado*.” E o céu escurece.": "“It is *finished*.” And the sky grows dark.",
    "Seu corpo é selado num *túmulo*.": "His body is sealed in a *tomb*.",
    "Silêncio. Um dia… dois dias…": "Silence. One day… two days…",
    "Mas, no *terceiro dia*…": "But on the *third day*…",
    "a pedra é removida. O túmulo está *vazio*!": "the stone is rolled away. The tomb is *empty*!",
    "*ELE* *RESSUSCITOU!*": "*HE* *IS RISEN!*",
    "A morte não teve a *última palavra*.": "Death did not have the *last word*.",
    # apelo
    "Jesus morreu por *mim*": "Jesus died for *me*", "e por *você*.": "and for *you*.",
    "Não importa a sua religião:": "No matter your religion:",
    "o que devemos olhar": "what we must look to",
    "é para *Ele*.": "is *Him*.",
    "Ele nos amou.": "He loved us.", "ELE TE AMA": "HE LOVES YOU",
}

VERSES_EN = {  # King James Version (domínio público)
    "I": ("Thou shalt conceive in thy womb, and bring forth a son, and shalt call his name Jesus.", "Luke 1:31"),
    "II": ("She brought forth her firstborn son, wrapped him in swaddling clothes, and laid him in a manger.", "Luke 2:7"),
    "III": ("Where is he that is born King of the Jews? For we have seen his star in the east.", "Matthew 2:2"),
    "IV": ("This is my beloved Son, in whom I am well pleased.", "Matthew 3:17"),
    "V": ("Peace, be still. And the wind ceased, and there was a great calm.", "Mark 4:39"),
    "VI": ("I am the way, the truth, and the life.", "John 14:6"),
    "VII": ("This is my body which is given for you: this do in remembrance of me.", "Luke 22:19"),
    "VIII": ("O my Father, if it be possible, let this cup pass from me: nevertheless not as I will, but as thou wilt.", "Matthew 26:39"),
    "IX": ("He was wounded for our transgressions… and with his stripes we are healed.", "Isaiah 53:5"),
    "X": ("Father, forgive them; for they know not what they do.", "Luke 23:34"),
    "XI": ("He rolled a great stone to the door of the sepulchre, and departed.", "Matthew 27:60"),
    "XII": ("He is not here: for he is risen, as he said.", "Matthew 28:6"),
}


def tr(s):
    return EN.get(s, s) if LANG == "en" else s


# ───────────────────────── legendas ─────────────────────────
def draw_caption(c, text, lt, dur, big=False):
    face = SERIF if big else SANS
    size = 92 if big else 56
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    words = []
    for tok in tr(text).split(" "):
        emph = "*" in tok
        words.append((tok.replace("*", ""), emph))
    space = c.text_extents(" ").x_advance
    maxw = 1600
    lines, cur, curw = [], [], 0
    for wd, em in words:
        wdt = c.text_extents(wd).x_advance
        if cur and curw + space + wdt > maxw:
            lines.append((cur, curw))
            cur, curw = [], 0
        curw += (space if cur else 0) + wdt
        cur.append((wd, em, wdt))
    lines.append((cur, curw))
    lh = size * 1.22
    base = H - 105 - (len(lines) - 1) * lh
    fade_out = clamp((dur - lt) / 0.22)
    i = 0
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        y = base + li * lh
        for wd, em, wdt in ln:
            p = eout((lt - i * 0.055) / 0.28)
            if p > 0:
                a = p * fade_out
                dy = (1 - p) * 26
                c.save()
                sc = lerp(0.85, 1.0, eback(clamp((lt - i * 0.055) / 0.3)))
                c.translate(x + wdt / 2, y + dy - size * 0.35)
                c.scale(sc, sc)
                c.translate(-wdt / 2, size * 0.35)
                if em:
                    c.move_to(0, 0)
                    c.text_path(wd)
                    c.set_line_width(10)
                    c.set_source_rgba(1, 0.7, 0.2, 0.22 * a)
                    c.stroke()
                c.move_to(2, 4)
                c.set_source_rgba(0, 0, 0, 0.75 * a)
                c.show_text(wd)
                c.move_to(0, 0)
                rgb(c, GOLD if em else "#ffffff", a)
                c.show_text(wd)
                c.restore()
            x += wdt + space
            i += 1


VERSES = {
    "I": ("Eis que conceberás e darás à luz um filho, e pôr-lhe-ás o nome de Jesus.", "Lucas 1:31"),
    "II": ("Deu à luz o seu filho primogênito, envolveu-o em panos e o deitou numa manjedoura.", "Lucas 2:7"),
    "III": ("Onde está o rei dos judeus, que é nascido? Vimos a sua estrela no Oriente.", "Mateus 2:2"),
    "IV": ("Este é o meu Filho amado, em quem me comprazo.", "Mateus 3:17"),
    "V": ("Cala-te, aquieta-te. E o vento cessou, e fez-se grande bonança.", "Marcos 4:39"),
    "VI": ("Eu sou o caminho, e a verdade, e a vida.", "João 14:6"),
    "VII": ("Isto é o meu corpo, que por vós é dado; fazei isto em memória de mim.", "Lucas 22:19"),
    "VIII": ("Meu Pai, não seja como eu quero, mas como tu queres.", "Mateus 26:39"),
    "IX": ("Foi ferido por causa das nossas transgressões; pelas suas pisaduras fomos sarados.", "Isaías 53:5"),
    "X": ("Pai, perdoa-lhes, porque não sabem o que fazem.", "Lucas 23:34"),
    "XI": ("Rolou uma grande pedra para a porta do sepulcro.", "Mateus 27:60"),
    "XII": ("Não está aqui, ressuscitou, como tinha dito.", "Mateus 28:6"),
}


def _wrap(c, text, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if cur and c.text_extents(t).x_advance > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def draw_chapter(c, label, lt, dur):
    a = eout(lt / 0.5) * clamp((dur - lt) / 0.3)
    if a <= 0:
        return
    key = label.split(" · ")[0]
    verse = (VERSES_EN if LANG == "en" else VERSES).get(key)
    label = tr(label)
    g = cairo.RadialGradient(60, 60, 0, 60, 60, 900)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.6 * a)
    g.add_color_stop_rgba(0.5, 0, 0, 0, 0.3 * a)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g)
    c.rectangle(0, 0, 960, 620)
    c.fill()
    ln = 70 * eout(lt / 0.6)
    c.set_line_width(3)
    rgb(c, GOLD, a)
    c.move_to(80, 92)
    c.line_to(80 + ln, 92)
    c.stroke()
    c.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(26)
    x = 170 - (1 - eout(lt / 0.5)) * 30
    for ch in label:
        c.move_to(x + 2, 102)
        c.set_source_rgba(0, 0, 0, 0.6 * a)
        c.show_text(ch)
        c.move_to(x, 100)
        rgb(c, "#fff4d6", a)
        c.show_text(ch)
        x += c.text_extents(ch).x_advance + 4
    if verse:
        va = eout(seg(lt, 0.5, 1.1)) * clamp((dur - lt) / 0.3)
        dy = (1 - eout(seg(lt, 0.5, 1.1))) * 12
        c.select_font_face(SANS, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        c.set_font_size(32)
        lines = _wrap(c, "“" + verse[0] + "”", 800)
        y = 152 + dy
        for l in lines:
            c.move_to(82, y + 2)
            c.set_source_rgba(0, 0, 0, 0.7 * va)
            c.show_text(l)
            c.move_to(80, y)
            rgb(c, "#ffffff", 0.95 * va)
            c.show_text(l)
            y += 44
        c.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(27)
        c.move_to(82, y + 6)
        c.set_source_rgba(0, 0, 0, 0.7 * va)
        c.show_text("— " + verse[1])
        c.move_to(80, y + 4)
        rgb(c, GOLD, va)
        c.show_text("— " + verse[1])


# ───────────────────────── cenas ─────────────────────────
def camera(c, p, z0=1.0, z1=1.08, cx=W / 2, cy=H / 2):
    z = lerp(z0, z1, p)
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)


def s_intro(c, t, d):
    sky(c, [(0, "#05030d"), (0.6, "#140a2a"), (1, "#2a1238")])
    stars(c, t, H, 0.9)
    gl = eout(t / 2.5)
    rays(c, W / 2, H * 0.45, 22, 1300 * gl, t * 0.08, "#ffd98a", 0.16 * gl)
    glow(c, W / 2, H * 0.45, 700 * gl, "#ffbf5e", 0.45 * gl)
    particles(c, t, 90, 11, "#ffd98a", 0.8, rise=50)
    ridge(c, H * 0.86, 40, 1.2, 0, "#0a0512", seed=2)
    # título
    ta = eout(seg(t, 0.3, 1.6))
    sp = lerp(110, 46, eout(seg(t, 0.3, 2.6)))
    zz = lerp(1.12, 1.0, eout(seg(t, 0.3, 2.6)))
    c.save()
    c.translate(W / 2, H * 0.47)
    c.scale(zz, zz)
    title_text(c, "JESUS", 0, 95, 270, spacing=sp, a=ta, shine=seg(t, 1.6, 3.2))
    c.restore()
    la = eout(seg(t, 1.2, 2.2))
    c.set_line_width(2)
    rgb(c, GOLD, la)
    c.move_to(W / 2 - 360 * la, H * 0.58)
    c.line_to(W / 2 + 360 * la, H * 0.58)
    c.stroke()
    text_center(c, tr("DO NASCIMENTO À RESSURREIÇÃO"), W / 2, H * 0.58 + 58, 32, face=SANS,
                col=GOLD, a=eout(seg(t, 1.5, 2.5)), spacing=8)


def s_anunciacao(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.07, W * 0.5, H * 0.55)
    sky(c, [(0, "#0d0b2e"), (0.55, "#3b2a6b"), (0.85, "#b06a8a"), (1, "#e2a37a")])
    stars(c, t, H * 0.5, 0.6)
    ridge(c, H * 0.78, 50, 0.8, 0.5, "#2a1c45", seed=5)
    town(c, H * 0.82, "#1b1230", seed=8, scale=0.8, lit=0.8, t=t)
    ridge(c, H * 0.9, 15, 0.5, 0, "#120b20", seed=6)
    # anjo desce
    ay = lerp(-150, H * 0.78, eout(seg(t, 0, 2.6))) + 8 * math.sin(t * 2)
    ax = W * 0.36
    la = eout(seg(t, 0, 2.2))
    rays(c, ax, ay - 190, 18, 900, t * 0.15, "#fff3c8", 0.22 * la)
    glow(c, ax, ay - 200, 520, "#fff1c2", 0.6 * la)
    wings(c, ax, ay, 300, t, "#fffaf0", 0.95 * la)
    figure(c, ax, ay, 300, "#ffffff", pose="reach", halo_a=la)
    particles(c, t, 60, 21, "#fff3c8", 0.9 * la, rise=-30, area=(ax - 400, ay - 500, ax + 400, ay + 50))
    # Maria
    mx = W * 0.64
    glow(c, mx, H * 0.83 - 150, 260, "#ffd9a0", 0.35 * la)
    kneel(c, mx, H * 0.86, 300, "#170d24", veil=True, flip=True)


def s_nascimento(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.12, W * 0.5, H * 0.62)
    sky(c, [(0, "#040a1f"), (0.6, "#10224a"), (1, "#2c3d6e")])
    stars(c, t, H * 0.7, 1.0)
    sx, sy = W * 0.66, H * 0.14
    sa = eout(seg(t, 0.2, 1.5))
    # feixe da estrela até o estábulo
    g = cairo.LinearGradient(sx, sy, W * 0.5, H * 0.7)
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.35 * sa)
    g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.0)
    c.set_source(g)
    c.move_to(sx - 10, sy)
    c.line_to(W * 0.36, H * 0.85)
    c.line_to(W * 0.64, H * 0.85)
    c.line_to(sx + 10, sy)
    c.close_path()
    c.fill()
    starburst(c, sx, sy, 22 + 3 * math.sin(t * 3), t * 0.2, sa)
    ridge(c, H * 0.66, 40, 0.9, 1, "#101a36", seed=9)
    town(c, H * 0.7, "#0b1229", seed=4, scale=0.6, lit=1.0, t=t)
    ridge(c, H * 0.84, 18, 0.6, 2, "#070b1a", seed=10)
    # estábulo
    bx, by = W * 0.5, H * 0.88
    glow(c, bx, by - 110, 420, "#ffb24a", 0.75)
    rgb(c, "#1a0f0a")
    c.rectangle(bx - 330, by - 300, 26, 300)
    c.rectangle(bx + 304, by - 300, 26, 300)
    c.move_to(bx - 400, by - 290)
    c.line_to(bx, by - 430)
    c.line_to(bx + 400, by - 290)
    c.line_to(bx + 400, by - 260)
    c.line_to(bx, by - 395)
    c.line_to(bx - 400, by - 260)
    c.close_path()
    c.fill()
    # manjedoura + bebê
    rgb(c, "#2a170c")
    c.move_to(bx - 90, by - 90)
    c.line_to(bx + 90, by - 90)
    c.line_to(bx + 60, by - 30)
    c.line_to(bx - 60, by - 30)
    c.close_path()
    c.fill()
    c.set_line_width(10)
    c.move_to(bx - 70, by)
    c.line_to(bx - 40, by - 40)
    c.move_to(bx + 70, by)
    c.line_to(bx + 40, by - 40)
    c.stroke()
    ba = 0.8 + 0.2 * math.sin(t * 2.5)
    glow(c, bx, by - 105, 190, "#fff3c8", ba)
    rgb(c, "#fff8e6")
    c.save()
    c.translate(bx, by - 102)
    c.scale(1, 0.45)
    c.arc(0, 0, 55, 0, TAU)
    c.restore()
    c.fill()
    c.arc(bx + 42, by - 110, 17, 0, TAU)
    c.fill()
    halo(c, bx + 42, by - 110, 16, 0.8)
    kneel(c, bx - 190, by, 230, "#120a06", veil=True)
    figure(c, bx + 200, by, 290, "#120a06", staff=True, flip=True)
    # ovelhas
    for ox in (bx - 330, bx + 330):
        rgb(c, "#140b07")
        c.save()
        c.translate(ox, by - 30)
        c.scale(1, 0.6)
        c.arc(0, 0, 45, 0, TAU)
        c.restore()
        c.fill()
        c.arc(ox + (40 if ox > bx else -40), by - 50, 16, 0, TAU)
        c.fill()
    ridge(c, H * 0.98, 6, 0.4, 0, "#050308", seed=12)


def s_magos(c, t, d):
    p = t / d
    sky(c, [(0, "#1a0b3a"), (0.5, "#6b2f6b"), (0.8, "#d9735a"), (1, "#f4b36a")])
    stars(c, t, H * 0.4, 0.5)
    starburst(c, W * 0.8, H * 0.16, 20 + 2 * math.sin(t * 3), t * 0.2, 1.0)
    c.set_source_rgba(1, 1, 1, 0.07)
    c.move_to(W * 0.8, H * 0.16)
    c.line_to(W * 0.7, H)
    c.line_to(W * 0.95, H)
    c.close_path()
    c.fill()
    glow(c, W * 0.5, H * 0.8, 900, "#ffb36a", 0.35)
    ridge(c, H * 0.62, 50, 0.5, 0, "#8a3f5e", seed=21, xoff=t * 20)
    ridge(c, H * 0.72, 60, 0.4, 1, "#5a2548", seed=22, xoff=t * 45)
    # caravana
    base = H * 0.8
    for i in range(3):
        cx = lerp(-200, W * 0.62, p) + i * 220
        cy = base + 10 * math.sin(cx / 300)
        camel(c, cx, cy, 190, t + i * 0.7, "#24102a", crown=True)
    ridge(c, H * 0.86, 30, 0.6, 2, "#24102a", seed=23, xoff=t * 45)
    ridge(c, H * 0.95, 40, 0.5, 3, "#12071a", seed=24, xoff=t * 90)
    palm(c, W * 0.1 - t * 30, H * 1.02, 520, "#0c0410", t)


def s_batismo(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.08, W * 0.5, H * 0.45)
    sky(c, [(0, "#3e6fa8"), (0.55, "#9cc3dd"), (1, "#f3dca8")])
    op = eout(seg(t, 1.5, 3.5))
    # nuvens se abrem
    for i, (cx, cy, s) in enumerate([(W * 0.2, 140, 120), (W * 0.35, 90, 100), (W * 0.65, 100, 110), (W * 0.8, 150, 130)]):
        dx = (-1 if cx < W / 2 else 1) * op * 160
        cloud(c, cx + dx, cy, s, "#f5f1e8", 0.9, seed=i)
    rays(c, W * 0.5, -60, 16, 1300, math.pi / 2 - 0.35 + 0.02 * math.sin(t), "#fff7d6", 0.35 * op, width=0.06)
    g = cairo.LinearGradient(0, 0, 0, H * 0.7)
    g.add_color_stop_rgba(0, 1, 0.98, 0.85, 0.6 * op)
    g.add_color_stop_rgba(1, 1, 0.98, 0.85, 0.0)
    c.set_source(g)
    c.move_to(W * 0.5 - 60, 0)
    c.line_to(W * 0.5 + 60, 0)
    c.line_to(W * 0.5 + 170, H * 0.7)
    c.line_to(W * 0.5 - 170, H * 0.7)
    c.close_path()
    c.fill()
    ridge(c, H * 0.55, 40, 0.6, 0, "#7f9a86", seed=31)
    ridge(c, H * 0.6, 30, 0.9, 1, "#5d7a64", seed=32)
    # rio
    water(c, H * 0.66, 6, t, "#5f9ec4")
    figure(c, W * 0.5, H * 0.86, 380, "#1c2a33", pose="open", halo_a=op)
    figure(c, W * 0.7, H * 0.86, 360, "#23231a", pose="bless", flip=True)
    water(c, H * 0.78, 8, t, "#4a86b0", 0.92, phase=1)
    water(c, H * 0.86, 10, t, "#3b739c", 1.0, phase=2)
    for k in range(18):
        x = W * 0.05 + k * 30 + (k % 3) * 8
        rgb(c, "#2d4a2e")
        c.set_line_width(6)
        c.move_to(x, H)
        c.curve_to(x, H * 0.85, x + 10 * math.sin(t + k), H * 0.78, x + 20 * math.sin(t + k), H * 0.7 - (k % 4) * 20)
        c.stroke()
    # pomba
    da = eout(seg(t, 2.0, 4.5))
    if da > 0:
        dy = lerp(-50, H * 0.26, da)
        glow(c, W * 0.5, dy, 160, "#ffffff", 0.7 * da)
        dove(c, W * 0.5, dy, 70, t, a=da)


def s_milagres(c, t, d):
    s = 1 - eio(seg(t, 5.2, 7.6))
    sk = mix("#f6c177", "#1b2230", s)
    sm = mix("#e98c5a", "#2c3444", s)
    sb = mix("#6d4a7a", "#394356", s)
    sky(c, [(0, sb), (0.55, sm), (1, sk)], 0, H * 0.7)
    rgb(c, sk)
    c.rectangle(0, H * 0.7, W, H)
    c.fill()
    if s < 1:
        glow(c, W * 0.5, H * 0.6, 700, "#ffcf7a", 0.6 * (1 - s))
    for i in range(6):
        cloud(c, (i * 380 + t * 40) % (W + 400) - 200, 110 + (i % 2) * 70, 170, "#161b26", 0.85 * s, seed=i + 40)
    fl = 0
    for lt_, lx in ((1.0, 0.25), (2.6, 0.75), (4.0, 0.4)):
        e = seg(t, lt_, lt_ + 0.35)
        if 0 < e < 1:
            fl = max(fl, (1 - e) * s)
            lightning(c, W * lx, 0, H * 0.6, int(lt_ * 10), (1 - e) * s)
    amp = lerp(8, 42, s)
    water(c, H * 0.66, amp * 0.6, t * 1.4, mix("#b76a58", "#1f2a3a", s), phase=0.3)
    # barco
    bx, by = W * 0.26, H * 0.7 + amp * 0.6 * math.sin(t * 1.6)
    c.save()
    c.translate(bx, by)
    c.rotate(0.12 * s * math.sin(t * 2.2))
    rgb(c, "#120c10")
    c.move_to(-230, -30)
    c.line_to(230, -40)
    c.curve_to(180, 40, -180, 40, -230, -30)
    c.fill()
    c.rectangle(-6, -330, 12, 300)
    c.fill()
    c.move_to(0, -320)
    c.line_to(150, -80)
    c.line_to(0, -70)
    c.close_path()
    c.fill()
    for k in range(4):
        c.arc(-150 + k * 70, -60, 16, 0, TAU)
        c.fill()
    c.restore()
    # Jesus sobre as águas
    jx = W * 0.64
    ja = eout(seg(t, 0.3, 1.5))
    calm_arm = eout(seg(t, 4.4, 5.4))
    glow(c, jx, H * 0.52, 360, "#fff1c8", 0.45 * ja + 0.3 * (1 - s))
    hand = (lerp(0.2, 0.34, calm_arm), lerp(-0.45, -1.08, calm_arm))
    figure(c, jx, H * 0.76 + 6 * math.sin(t), 420, "#101418", hands=(None, hand), halo_a=ja)
    water(c, H * 0.76, amp, t * 1.6, mix("#d08a62", "#27354a", s), phase=1.3)
    water(c, H * 0.86, amp * 1.2, t * 1.9, mix("#a2604e", "#18212f", s), phase=2.1)
    # chuva
    if s > 0.02:
        c.set_line_width(2)
        c.set_source_rgba(0.75, 0.8, 0.9, 0.35 * s)
        rnd = random.Random(5)
        for _ in range(220):
            x = rnd.uniform(0, W + 300)
            y = (rnd.uniform(0, H) + t * 1400) % H
            c.move_to(x - y * 0.25, y)
            c.line_to(x - y * 0.25 - 12, y + 40)
        c.stroke()
    overlay(c, "#dfe6ff", fl * 0.35)


def s_pregacao(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.06, W * 0.5, H * 0.4)
    sky(c, [(0, "#3a2a6a"), (0.45, "#e0784f"), (0.75, "#ffc46b"), (1, "#ffe3a3")])
    sx, sy = W * 0.5, H * 0.46
    rays(c, sx, sy, 28, 1500, t * 0.06, "#fff1c4", 0.25)
    glow(c, sx, sy, 380, "#fff3cf", 1.0, core=0.15)
    for k in range(5):
        bx = (W * 0.2 + k * 160 + t * 70) % (W + 200) - 100
        by = 200 + 40 * math.sin(k * 2 + t)
        w = math.sin(t * 8 + k) * 12
        c.set_line_width(4)
        rgb(c, "#3a1d2a")
        c.move_to(bx - 22, by - w)
        c.line_to(bx, by)
        c.line_to(bx + 22, by - w)
        c.stroke()
    ridge(c, H * 0.72, 30, 0.5, 0, "#b4524a", seed=51)
    # colina
    rgb(c, "#40182a")
    c.move_to(-10, H)
    c.curve_to(W * 0.3, H * 0.6, W * 0.42, H * 0.6, W * 0.5, H * 0.6)
    c.curve_to(W * 0.58, H * 0.6, W * 0.7, H * 0.6, W + 10, H)
    c.fill()
    figure(c, W * 0.5, H * 0.61, 300, "#2a0f1e", pose="open", halo_a=1)
    # multidão
    for row, (yy, sz, col) in enumerate(((H * 0.84, 55, "#2b0e1e"), (H * 0.92, 70, "#1e0914"), (H * 1.0, 90, "#12050c"))):
        rnd = random.Random(row + 60)
        x = -40 + row * 20
        while x < W + 60:
            bob = 4 * math.sin(t * 2 + x * 0.05)
            rgb(c, col)
            c.arc(x, yy - sz * 1.1 + bob, sz * 0.32, 0, TAU)
            c.fill()
            c.move_to(x - sz * 0.6, H + 10)
            c.curve_to(x - sz * 0.55, yy - sz * 0.8 + bob, x + sz * 0.55, yy - sz * 0.8 + bob, x + sz * 0.6, H + 10)
            c.fill()
            if rnd.random() < 0.18 and p > 0.3:
                c.set_line_width(sz * 0.14)
                c.move_to(x + sz * 0.35, yy - sz * 0.6 + bob)
                c.line_to(x + sz * 0.55, yy - sz * 1.6 + bob)
                c.stroke()
            x += sz * rnd.uniform(0.9, 1.3)


def s_ceia(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.1, W * 0.5, H * 0.5)
    cold = eio(seg(t, 3.8, 5.0))
    wall = mix("#3a1f14", "#1a1622", cold)
    rgb(c, wall)
    c.paint()
    for k, wx in enumerate((W * 0.3, W * 0.5, W * 0.7)):
        rgb(c, mix("#1d2d5a", "#0e1633", cold))
        c.move_to(wx - 90, H * 0.52)
        c.line_to(wx - 90, H * 0.25)
        c.arc(wx, H * 0.25, 90, math.pi, TAU)
        c.line_to(wx + 90, H * 0.52)
        c.close_path()
        c.fill()
        c.save()
        c.rectangle(wx - 90, H * 0.1, 180, H * 0.42)
        c.clip()
        stars(c, t, H, 0.8, 120)
        c.restore()
    glow(c, W * 0.5, H * 0.55, 900, mix("#ff9a3c", "#6a7bbf", cold), 0.55)
    # apóstolos
    xs = [W * 0.5 + (i - 6) * 128 for i in range(13)]
    for i, x in enumerate(xs):
        hy = H * 0.5 + (0 if i == 6 else 18 + (i % 2) * 10)
        col = "#150a07"
        if i == 11:
            col = mix("#150a07", "#050305", cold)
            x += cold * 25
        if i == 6:
            halo(c, x, hy - 60, 34, 1.0)
        rgb(c, col)
        c.arc(x, hy - 60, 34, 0, TAU)
        c.fill()
        c.move_to(x - 75, H * 0.7)
        c.curve_to(x - 75, hy - 125, x + 75, hy - 125, x + 75, H * 0.7)
        c.fill()
        if i == 11 and cold > 0:
            glow(c, x, hy - 30, 120, "#8a1010", 0.5 * cold)
    # mesa
    rgb(c, "#2b140a")
    c.rectangle(W * 0.06, H * 0.64, W * 0.88, 40)
    c.fill()
    rgb(c, "#1c0c05")
    c.rectangle(W * 0.08, H * 0.64 + 40, W * 0.84, H)
    c.fill()
    # velas
    for vx in (W * 0.2, W * 0.36, W * 0.64, W * 0.8):
        fl = 0.85 + 0.15 * math.sin(t * 13 + vx)
        glow(c, vx, H * 0.56, 160, "#ffb347", 0.6 * fl)
        rgb(c, "#e8d6b0")
        c.rectangle(vx - 8, H * 0.58, 16, 50)
        c.fill()
        rgb(c, "#ffd66b", fl)
        c.save()
        c.translate(vx, H * 0.565)
        c.scale(1, 1.8)
        c.arc(0, 0, 8, 0, TAU)
        c.restore()
        c.fill()
    # pão e cálice
    split = eout(seg(t, 1.0, 2.2)) * 30
    glow(c, W * 0.5, H * 0.62, 180, "#ffe2a0", 0.6)
    rgb(c, "#c9894a")
    for sgn in (-1, 1):
        c.save()
        c.translate(W * 0.47 + sgn * split, H * 0.63)
        c.scale(1, 0.5)
        c.arc(0, 0, 44, 0, TAU)
        c.restore()
        c.fill()
    rgb(c, "#d4a64a")
    cx, cy = W * 0.555, H * 0.64
    c.move_to(cx - 30, cy - 70)
    c.line_to(cx + 30, cy - 70)
    c.curve_to(cx + 30, cy - 30, cx + 8, cy - 25, cx + 5, cy - 20)
    c.line_to(cx + 5, cy - 5)
    c.line_to(cx + 22, cy)
    c.line_to(cx - 22, cy)
    c.line_to(cx - 5, cy - 5)
    c.line_to(cx - 5, cy - 20)
    c.curve_to(cx - 8, cy - 25, cx - 30, cy - 30, cx - 30, cy - 70)
    c.fill()
    rgb(c, "#6a0f1a")
    c.rectangle(cx - 27, cy - 68, 54, 10)
    c.fill()
    overlay(c, "#0a0c1c", 0.25 * cold)


def s_getsemani(c, t, d):
    p = t / d
    camera(c, p, 1.05, 1.0, W * 0.5, H * 0.5)
    sky(c, [(0, "#02030c"), (0.6, "#0c1838"), (1, "#1b2d55")])
    stars(c, t, H * 0.6, 0.8)
    mx, my = W * 0.78, H * 0.2
    glow(c, mx, my, 360, "#c9d8ff", 0.35)
    rgb(c, "#eef2ff")
    c.arc(mx, my, 70, 0, TAU)
    c.fill()
    ridge(c, H * 0.64, 40, 0.6, 0, "#0d1730", seed=71)
    for i, (x, s) in enumerate(((W * 0.1, 360), (W * 0.28, 280), (W * 0.62, 300), (W * 0.9, 380))):
        olive_tree(c, x, H * 0.8, s, "#070c1c", seed=i + 3, sway=0.02 * math.sin(t + i))
    # rocha
    rgb(c, "#0b1124")
    c.move_to(W * 0.5, H * 0.86)
    c.curve_to(W * 0.5, H * 0.7, W * 0.56, H * 0.66, W * 0.62, H * 0.72)
    c.curve_to(W * 0.66, H * 0.76, W * 0.66, H * 0.84, W * 0.68, H * 0.86)
    c.fill()
    # luz do alto
    g = cairo.LinearGradient(0, 0, 0, H * 0.8)
    g.add_color_stop_rgba(0, 0.8, 0.85, 1, 0.0)
    g.add_color_stop_rgba(1, 0.8, 0.85, 1, 0.22)
    c.set_source(g)
    c.move_to(W * 0.43, 0)
    c.line_to(W * 0.49, 0)
    c.line_to(W * 0.56, H * 0.86)
    c.line_to(W * 0.4, H * 0.86)
    c.close_path()
    c.fill()
    glow(c, W * 0.49, H * 0.72, 220, "#9fb4ff", 0.35)
    kneel(c, W * 0.47, H * 0.86, 320, "#04060e", halo_a=0.8)
    # gotas
    for k in range(3):
        e = ((t * 0.7 + k * 0.33) % 1)
        rgb(c, "#b01c1c", 0.8 * (1 - e))
        c.arc(W * 0.47 + 25, H * 0.66 + e * 110, 4, 0, TAU)
        c.fill()
    # tochas chegando
    ta = eout(seg(t, 3.5, 7.5))
    for k in range(5):
        tx = lerp(W + 150, W * 0.72, ta) + k * 95
        ty = H * 0.86 - (k % 2) * 8
        fl = 0.8 + 0.2 * math.sin(t * 14 + k)
        glow(c, tx + 30, ty - 250, 180, "#ff7a2a", 0.55 * fl)
        figure(c, tx, ty, 230, "#030409", hands=((-0.2, -0.45), (0.13, -1.0)))
        rgb(c, "#ffb04a", fl)
        c.arc(tx + 30, ty - 245, 10, 0, TAU)
        c.fill()
    ridge(c, H * 0.95, 20, 0.5, 1, "#02030a", seed=72)


def s_paixao(c, t, d):
    split = 3.8
    if t < split + 0.4:
        a = 1 - seg(t, split, split + 0.4)
        sky(c, [(0, "#1a0205"), (1, "#3d0710")])
        glow(c, W / 2, H * 0.45, 700, "#8a1020", 0.6)
        c.save()
        c.translate(W / 2, H * 0.45)
        zz = lerp(0.9, 1.15, t / split)
        c.scale(zz, zz)
        c.rotate(t * 0.12)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(3):
            c.set_line_width(14)
            rgb(c, "#0c0404", a)
            c.save()
            c.scale(1, 0.42)
            c.arc(0, 0, 300 + k * 18, k, k + TAU)
            c.restore()
            c.stroke()
        rnd = random.Random(9)
        c.set_line_width(5)
        for _ in range(70):
            ang = rnd.uniform(0, TAU)
            r = 300 + rnd.uniform(-10, 40)
            x, y = math.cos(ang) * r, math.sin(ang) * r * 0.42
            L = rnd.uniform(25, 55)
            dx, dy = math.cos(ang + rnd.uniform(-1, 1)) * L, math.sin(ang + rnd.uniform(-1, 1)) * L
            c.move_to(x, y)
            c.line_to(x + dx, y + dy)
        c.stroke()
        c.restore()
        for k in range(8):
            e = (t * 0.6 + k * 0.125) % 1
            rgb(c, "#c0182a", 0.9 * a * (1 - e))
            c.arc(W / 2 + (k - 4) * 70, H * 0.6 + e * 300, 5, 0, TAU)
            c.fill()
        overlay(c, "#000000", 1 - a if t > split else 0)
        if t < split:
            return
    lt = t - split
    b = eout(seg(lt, 0, 0.5))
    sky(c, [(0, "#1c0a0a"), (0.5, "#6a2115"), (1, "#c2562a")])
    glow(c, W * 0.8, H * 0.55, 500, "#ff8a3a", 0.5)
    ridge(c, H * 0.62, 30, 0.6, 0, "#3a120c", seed=91)
    # caminho em subida
    rgb(c, "#1e0806")
    c.move_to(-10, H)
    c.line_to(-10, H * 0.82)
    c.curve_to(W * 0.4, H * 0.78, W * 0.7, H * 0.62, W + 10, H * 0.55)
    c.line_to(W + 10, H)
    c.fill()
    cx = lerp(W * 0.3, W * 0.42, lt / (8 - split))
    step = math.sin(lt * 3) * 6
    cy = H * 0.8 - (cx - W * 0.3) * 0.05
    c.save()
    c.translate(cx, cy + abs(step))
    c.rotate(0.18)
    figure(c, 0, 0, 330, "#0c0304", hands=((-0.16, -0.8), (0.04, -0.86)))
    c.restore()
    # cruz no ombro
    tx, ty = cx + 140, cy - 290 + abs(step)
    bx, by = cx - 360, cy + 10
    ang = math.atan2(by - ty, bx - tx)
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    rgb(c, "#140605")
    c.set_line_width(30)
    c.move_to(tx, ty)
    c.line_to(bx, by)
    c.stroke()
    mx, my = lerp(tx, bx, 0.22), lerp(ty, by, 0.22)
    px, py = -math.sin(ang), math.cos(ang)
    c.move_to(mx - px * 150, my - py * 150)
    c.line_to(mx + px * 130, my + py * 130)
    c.stroke()
    particles(c, lt, 60, 93, "#d9905a", 0.4, rise=-20, area=(0, H * 0.6, W, H))
    for k in range(3):
        figure(c, W * 0.12 + k * 120, H * 0.83, 260, "#0a0203", flip=True, veil=True)
    overlay(c, "#000000", 1 - b)


def s_cruz(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.14, W * 0.5, H * 0.45)
    dark = eio(seg(t, 5.0, 8.0))
    top = mix("#3a0d0d", "#040306", dark)
    mid = mix("#a33a1a", "#150808", dark)
    bot = mix("#f09a4a", "#2a0d0a", dark)
    sky(c, [(0, top), (0.55, mid), (1, bot)])
    glow(c, W * 0.5, H * 0.62, 800, "#ffb070", 0.5 * (1 - dark))
    for i in range(8):
        cloud(c, (i * 300 + t * (30 + i * 5)) % (W + 400) - 200, 80 + (i % 3) * 60, 150,
              mix("#2a0909", "#020203", dark), 0.7, seed=i + 80)
    fl = 0
    e = seg(t, 6.3, 6.8)
    if 0 < e < 1:
        fl = 1 - e
        lightning(c, W * 0.3, 0, H * 0.55, 77, fl)
        lightning(c, W * 0.72, 0, H * 0.5, 78, fl * 0.8)
    # colina
    rgb(c, "#060203")
    c.move_to(-10, H)
    c.curve_to(W * 0.25, H * 0.75, W * 0.4, H * 0.68, W * 0.5, H * 0.68)
    c.curve_to(W * 0.6, H * 0.68, W * 0.75, H * 0.75, W + 10, H)
    c.fill()
    glow(c, W * 0.5, H * 0.33, 260, "#ffd98a", 0.55 * (1 - 0.6 * dark))
    for x in (W * 0.32, W * 0.68):
        h = 330
        cross_shape(c, x, H * 0.73, h, col="#060203")
        figure(c, x, H * 0.73 - 0.341 * h, h * 0.62, "#060203", pose="cross")
    h = 470
    cross_shape(c, W * 0.5, H * 0.7, h, col="#060203")
    figure(c, W * 0.5, H * 0.7 - 0.297 * h, h * 0.68, "#060203", pose="cross", halo_a=0.9 * (1 - dark * 0.7))
    rgb(c, "#060203")
    c.rectangle(0, H * 0.95, W, H)
    c.fill()
    overlay(c, "#ffe8e0", fl * 0.45)


def _tomb(c, t, stone_off=0.0, stone_rot=0.0, inner_light=0.0):
    rgb(c, "#1a1a24")
    c.move_to(W * 0.2, H)
    c.curve_to(W * 0.22, H * 0.55, W * 0.35, H * 0.35, W * 0.55, H * 0.38)
    c.curve_to(W * 0.75, H * 0.4, W * 0.85, H * 0.6, W * 0.9, H)
    c.fill()
    rgb(c, "#23232f")
    c.move_to(W * 0.3, H)
    c.curve_to(W * 0.32, H * 0.6, W * 0.42, H * 0.45, W * 0.55, H * 0.47)
    c.curve_to(W * 0.68, H * 0.5, W * 0.78, H * 0.65, W * 0.8, H)
    c.fill()
    ox, oy, orad = W * 0.53, H * 0.78, 150
    rgb(c, "#050508")
    c.arc(ox, oy, orad, math.pi, TAU)
    c.line_to(ox + orad, H * 0.9)
    c.line_to(ox - orad, H * 0.9)
    c.close_path()
    c.fill()
    if inner_light > 0:
        glow(c, ox, oy, 420, "#fff6d8", inner_light)
        rgb(c, "#fffaf0", inner_light)
        c.arc(ox, oy, orad * 0.95, math.pi, TAU)
        c.line_to(ox + orad * 0.95, H * 0.9)
        c.line_to(ox - orad * 0.95, H * 0.9)
        c.close_path()
        c.fill()
    # pedra
    sx = ox + 30 + stone_off
    c.save()
    c.translate(sx, oy + 20)
    c.rotate(stone_rot)
    rgb(c, "#3a3a48")
    c.arc(0, 0, 175, 0, TAU)
    c.fill()
    rgb(c, "#2c2c38")
    c.arc(0, 0, 130, 0, TAU)
    c.fill()
    c.set_line_width(5)
    rgb(c, "#474758")
    c.move_to(-60, -40)
    c.line_to(20, -90)
    c.move_to(40, 50)
    c.line_to(100, 10)
    c.stroke()
    c.restore()
    rgb(c, "#0c0c12")
    c.rectangle(0, H * 0.9, W, H)
    c.fill()


def s_tumulo(c, t, d):
    p = t / d
    camera(c, p, 1.0, 1.05, W * 0.53, H * 0.6)
    sky(c, [(0, "#020308"), (0.7, "#0b1022"), (1, "#141a30")])
    stars(c, t, H * 0.6, 0.9)
    olive_tree(c, W * 0.12, H * 0.92, 380, "#07080f", seed=5)
    _tomb(c, t)
    vignette(c, 0.4)
    for k, (a0, lbl) in enumerate(((2.9, tr("DIA 1")), (4.7, tr("DIA 2")))):
        e = seg(t, a0, a0 + 2.2)
        if 0 < e < 1:
            al = eout(e / 0.25) * clamp((1 - e) / 0.3)
            sz = lerp(120, 150, e)
            text_center(c, lbl, W / 2, H * 0.32, sz, col="#c9d0e6", a=0.9 * al, spacing=20)


def s_ressurreicao(c, t, d):
    dawn = eio(seg(t, 0.5, 5.5))
    burst = eout(seg(t, 5.2, 6.6))
    shake = (seg(t, 3.4, 5.4) > 0 and seg(t, 3.4, 5.4) < 1)
    c.save()
    if shake:
        c.translate(random.Random(int(t * 30)).uniform(-9, 9), random.Random(int(t * 30) + 1).uniform(-6, 6))
    zz = lerp(1.05, 1.0, eout(seg(t, 0, 5))) + 0.06 * eout(seg(t, 6.5, 12))
    c.translate(W * 0.53, H * 0.6)
    c.scale(zz, zz)
    c.translate(-W * 0.53, -H * 0.6)
    sky(c, [(0, mix("#020308", "#4a78c8", dawn)), (0.6, mix("#0b1022", "#ffb877", dawn)),
            (1, mix("#141a30", "#ffe6a6", dawn))])
    stars(c, t, H * 0.6, 0.9 * (1 - dawn))
    glow(c, W * 0.53, H * 0.9, 1000, "#ffcf7a", 0.6 * dawn)
    olive_tree(c, W * 0.12, H * 0.92, 380, mix("#07080f", "#3a2a2a", dawn), seed=5)
    roll = eio(seg(t, 4.0, 6.0))
    _tomb(c, t, stone_off=roll * 420, stone_rot=roll * 2.4, inner_light=burst)
    if burst > 0:
        rays(c, W * 0.53, H * 0.78, 30, 2200 * burst, t * 0.1, "#fffbe6", 0.35 * burst, width=0.08)
    fig = eout(seg(t, 6.6, 8.2))
    if fig > 0:
        fy = H * 0.9 - 20 * fig
        glow(c, W * 0.53, fy - 260, 700, "#ffffff", 0.7 * fig)
        figure(c, W * 0.53, fy, 460, "#fffdf6", pose="raised", halo_a=fig, a=fig)
        particles(c, t, 110, 131, "#fff1c0", fig, rise=90, area=(0, 0, W, H))
    c.restore()
    e = seg(t, 0, 2.6)
    if e < 1:
        al = eout(e / 0.2) * clamp((1 - e) / 0.3)
        text_center(c, tr("DIA 3"), W / 2, H * 0.32, lerp(140, 175, e), col="#ffe7b0", a=al, spacing=24)
    wf = seg(t, 6.2, 6.4) - seg(t, 6.4, 7.4)
    overlay(c, "#ffffff", wf)


APPEAL = [
    # (início, fim, linhas [(texto, tamanho, fonte, cor)])
    (4.8, 8.1, [("Jesus morreu por *mim*", 84, SANS), ("e por *você*.", 84, SANS)]),
    (8.1, 11.8, [("Não importa a sua religião:", 62, SANS), ("o que devemos olhar", 62, SANS),
                 ("é para *Ele*.", 84, SANS)]),
    (11.8, 14.9, [("Ele nos amou.", 74, SANS), ("ELE TE AMA", 170, TITLE)]),
]


def appeal_lines(c, lines, lt, dur):
    fade_out = clamp((dur - lt) / 0.35)
    base = [0.0]
    for k in range(1, len(lines)):
        base.append(base[-1] + lines[k - 1][1] * 0.42 + lines[k][1] * 0.95)
    top = base[0] - lines[0][1] * 0.75
    bot = base[-1] + lines[-1][1] * 0.2
    off = H * 0.47 - (top + bot) / 2
    for k, (txt, sz, face) in enumerate(lines):
        txt = tr(txt)
        y = base[k] + off
        p = eout((lt - k * 0.45) / 0.5)
        if p > 0:
            a = p * fade_out
            yy = y + (1 - p) * 30
            if face == TITLE:
                title_text(c, txt, W / 2, yy + sz * 0.1, sz, spacing=lerp(40, 14, p), a=a,
                           shine=seg(lt, 1.2, 2.4))
            else:
                c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                c.set_font_size(sz)
                words = [(w.replace("*", ""), "*" in w) for w in txt.split(" ")]
                sp = c.text_extents(" ").x_advance
                ws = [c.text_extents(w).x_advance for w, _ in words]
                xx = W / 2 - (sum(ws) + sp * (len(ws) - 1)) / 2
                for (w, em), wd in zip(words, ws):
                    c.move_to(xx + 3, yy + 5)
                    c.set_source_rgba(0, 0, 0, 0.6 * a)
                    c.show_text(w)
                    c.move_to(xx, yy)
                    rgb(c, GOLD if em else "#ffffff", a)
                    c.show_text(w)
                    xx += wd + sp


def subscribe(c, lt, dur):
    a = eout(lt / 0.5) * clamp((dur - lt) / 0.6)
    if a <= 0:
        return
    text_center(c, tr("Siga nosso canal"), W / 2, H * 0.34 + (1 - eout(lt / 0.5)) * 30, 64, face=SANS,
                col="#ffffff", a=a)
    text_center(c, tr("para mais histórias que transformam vidas"), W / 2, H * 0.34 + 70, 36, face=SANS,
                col=GOLD, a=a * eout(seg(lt, 0.3, 0.8)), bold=False)
    # botão "INSCREVA-SE" com clique animado
    pop = eback(seg(lt, 0.5, 1.0))
    click = seg(lt, 1.6, 1.9)
    done = lt > 1.75
    press = 1 - 0.08 * math.sin(math.pi * click)
    bw, bh = 520, 120
    c.save()
    c.translate(W / 2 - 50, H * 0.6)
    c.scale(pop * press, pop * press)
    r = bh / 2
    c.new_sub_path()
    c.arc(-bw / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2)
    c.arc(bw / 2 - r, 0, r, -math.pi / 2, math.pi / 2)
    c.close_path()
    if done:
        c.set_source_rgba(0.3, 0.3, 0.33, a)
    else:
        c.set_source_rgba(0.86, 0.1, 0.12, a)
    c.fill()
    tw = text_center(c, tr("INSCRITO" if done else "INSCREVA-SE"), -22 if done else 0, 18, 48, face=SANS,
                     col="#ffffff", a=a, spacing=2)
    if done:
        c.set_line_width(8)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(tw / 2 - 2, 0)
        c.line_to(tw / 2 + 12, 14)
        c.line_to(tw / 2 + 38, -16)
        c.stroke()
    c.restore()
    # sino
    bell_a = a * eout(seg(lt, 0.8, 1.2))
    ring = math.sin(lt * 30) * 0.35 * clamp(1 - seg(lt, 2.1, 2.9)) if lt > 2.1 else 0
    c.save()
    c.translate(W / 2 + 290, H * 0.6 - 48)
    c.rotate(ring)
    c.scale(pop, pop)
    rgb(c, "#ffffff", bell_a)
    c.move_to(-34, 60)
    c.curve_to(-30, 40, -32, 0, -24, -12)
    c.curve_to(-14, -36, 14, -36, 24, -12)
    c.curve_to(32, 0, 30, 40, 34, 60)
    c.close_path()
    c.fill()
    c.arc(0, 70, 11, 0, TAU)
    c.fill()
    c.arc(0, -36, 6, 0, TAU)
    c.fill()
    c.restore()
    # cursor
    if lt < 2.3:
        mx = lerp(W * 0.75, W / 2 + 40, eio(seg(lt, 0.9, 1.6)))
        my = lerp(H * 0.9, H * 0.6 + 20, eio(seg(lt, 0.9, 1.6)))
        ca = a * eout(seg(lt, 0.8, 1.0)) * clamp((2.3 - lt) / 0.3)
        if 0 < click < 1:
            c.set_line_width(4)
            c.set_source_rgba(1, 1, 1, ca * (1 - click))
            c.arc(mx, my, 20 + 60 * click, 0, TAU)
            c.stroke()
        c.save()
        c.translate(mx, my)
        c.move_to(0, 0)
        for px, py in ((0, 52), (13, 40), (24, 64), (33, 60), (22, 37), (38, 36)):
            c.line_to(px, py)
        c.close_path()
        c.set_source_rgba(1, 1, 1, ca)
        c.fill_preserve()
        c.set_line_width(3)
        c.set_source_rgba(0, 0, 0, ca)
        c.stroke()
        c.restore()


def s_final(c, t, d):
    # parte 1 — "ELE VIVE" em luz dourada
    dark = eio(seg(t, 4.2, 5.2))
    sky(c, [(0, mix("#fff5dc", "#07040f", dark)), (0.5, mix("#ffd98f", "#1a0d24", dark)),
            (1, mix("#f2a55c", "#2d1430", dark))])
    rays(c, W / 2, H * 0.42, 36, 1600, t * 0.05, mix("#ffffff", "#ffd98a", dark), lerp(0.45, 0.12, dark))
    glow(c, W / 2, H * 0.42, lerp(900, 750, dark), mix("#ffffff", "#ff9f3a", dark), lerp(0.9, 0.35, dark))
    ca = eout(seg(t, 0.2, 1.6))
    rgb(c, "#ffffff", ca * lerp(0.85, 0.12, dark))
    c.rectangle(W / 2 - 14, H * 0.42 - 380 * ca, 28, 760 * ca)
    c.rectangle(W / 2 - 250 * ca, H * 0.42 - 230, 500 * ca, 28)
    c.fill()
    particles(c, t, 120, 141, mix("#ffffff", "#ffd98a", dark), 0.9, rise=60)
    ta = eout(seg(t, 0.8, 2.0)) * (1 - seg(t, 4.0, 4.6))
    sp = lerp(70, 30, eout(seg(t, 0.8, 3.0)))
    title_text(c, tr("ELE VIVE"), W / 2, H * 0.52, 210, spacing=sp, a=ta, shine=seg(t, 2.0, 3.4),
               top="#9a5a16", mid="#7a3e0a", bottom="#4a2004", glow_a=0.25, outline=False)
    # parte 2 — apelo
    for a0, a1, lines in APPEAL:
        if a0 <= t < a1:
            appeal_lines(c, lines, t - a0, a1 - a0)
    if t >= 14.9:
        subscribe(c, t - 14.9, d - 14.9)
    overlay(c, "#000000", seg(t, d - 0.8, d))


# (label, duração, função, legendas [início, fim, texto, grande?], transição)
SCENES = [
    ("", 5.0, s_intro, [(1.3, 4.95, "Há dois mil anos, uma história mudaria o mundo *para sempre*.")]),
    ("I · A PROMESSA", 7.5, s_anunciacao, [
        (0.3, 4.0, "Em Nazaré, um anjo aparece a uma jovem chamada *Maria*."),
        (3.8, 7.4, "“Você terá um filho… e o chamará *Jesus*.”")]),
    ("II · O NASCIMENTO", 7.5, s_nascimento, [
        (0.3, 3.6, "Em *Belém*, sem lugar na hospedaria…"),
        (3.5, 7.4, "…o Filho de Deus nasce numa simples *manjedoura*.")]),
    ("III · A ESTRELA", 6.0, s_magos, [
        (0.2, 5.9, "Uma *estrela* guia magos do Oriente até o Rei recém-nascido.")]),
    ("IV · O BATISMO", 7.5, s_batismo, [
        (0.2, 3.8, "Aos 30 anos, no rio *Jordão*, os céus se abrem:"),
        (3.6, 7.4, "“Este é o meu *Filho amado*.”")]),
    ("V · OS MILAGRES", 9.0, s_milagres, [
        (0.2, 4.6, "Ele cura *cegos*. Faz paralíticos *andarem*."),
        (4.4, 8.9, "Caminha sobre as águas… e a *tempestade* se cala.")]),
    ("VI · A MENSAGEM", 7.5, s_pregacao, [
        (0.2, 4.0, "Multidões o seguem. Ele fala de *amor*, *perdão* e *esperança*."),
        (3.9, 7.4, "“Eu sou o caminho, a verdade e a *vida*.”")]),
    ("VII · A ÚLTIMA CEIA", 7.5, s_ceia, [
        (0.2, 3.8, "Na última ceia, ele parte o pão com os *doze*."),
        (3.6, 7.4, "“Um de vocês vai me *trair*.”")]),
    ("VIII · GETSÊMANI", 7.5, s_getsemani, [
        (0.2, 3.8, "No jardim, ele ora em *agonia*."),
        (3.6, 7.4, "Judas chega com soldados… e o entrega com um *beijo*.")]),
    ("IX · A PAIXÃO", 8.0, s_paixao, [
        (0.2, 3.7, "Condenado. Açoitado. *Coroado de espinhos*."),
        (3.9, 7.9, "Carrega a própria cruz rumo ao *Calvário*.")]),
    ("X · A CRUZ", 10.0, s_cruz, [
        (0.3, 4.8, "Pregado na cruz, ele clama: “Pai, *perdoa-lhes*.”"),
        (4.8, 9.9, "“Está *consumado*.” E o céu escurece.")]),
    ("XI · O SILÊNCIO", 7.0, s_tumulo, [
        (0.3, 3.2, "Seu corpo é selado num *túmulo*."),
        (3.0, 6.9, "Silêncio. Um dia… dois dias…")]),
    ("XII · A RESSURREIÇÃO", 12.0, s_ressurreicao, [
        (0.4, 3.4, "Mas, no *terceiro dia*…"),
        (3.4, 7.2, "a pedra é removida. O túmulo está *vazio*!"),
        (7.4, 11.9, "*ELE* *RESSUSCITOU!*", True)]),
    ("", 17.5, s_final, [(1.6, 4.4, "A morte não teve a *última palavra*.")]),
]

# fades: (entrada, saída) — None = corte seco
FADES = {0: ("#000000", None), 11: ("#000000", None), 12: (None, None), 13: ("#ffffff", None)}

STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc


def render_frame(i):
    T = i / FPS
    idx = max(k for k, s in enumerate(STARTS) if s <= T + 1e-9)
    idx = min(idx, len(SCENES) - 1)
    label, dur, fn, caps = SCENES[idx][:4]
    t = T - STARTS[idx]
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    c.save()
    fn(c, t, dur)
    c.restore()
    vignette(c, 0.55)
    # faixa das legendas
    active = [cp for cp in caps if cp[0] <= t < cp[1]]
    if active:
        g = cairo.LinearGradient(0, H - 330, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
        c.set_source(g)
        c.rectangle(0, H - 330, W, 330)
        c.fill()
        for cp in active:
            draw_caption(c, cp[2], t - cp[0], cp[1] - cp[0], big=len(cp) > 3 and cp[3])
    if label:
        draw_chapter(c, label, t, dur)
    fin, fout = FADES.get(idx, ("#000000", "#000000"))
    if fin:
        overlay(c, fin, 1 - eout(t / 0.35))
    if fout and idx + 1 < len(SCENES) and FADES.get(idx + 1, ("#000000",))[0]:
        overlay(c, fout, seg(t, dur - 0.25, dur) * 0.9)
    surf.flush()
    return bytes(surf.get_data())


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--frames":
        for ts in sys.argv[2:]:
            i = int(float(ts) * FPS)
            data = render_frame(i)
            s = cairo.ImageSurface.create_for_data(bytearray(data), cairo.FORMAT_RGB24, W, H)
            out = os.path.join(os.environ.get("OUT", HERE), f"frame_{float(ts):06.2f}.png")
            s.write_to_png(out)
            print(out)
        return
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    n = int(round(TOTAL * FPS))
    audio = os.environ.get("VIDEO_AUDIO", os.path.join(HERE, "trilha.wav"))
    out = os.environ.get("VIDEO_OUT", os.path.join(HERE, "jesus_historia.mp4"))
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if os.path.exists(audio):
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(n), chunksize=4)):
            proc.stdin.write(fr)
            if k % 150 == 0:
                print(f"{k}/{n} quadros", flush=True)
    proc.stdin.close()
    proc.wait()
    print("OK:", out, f"{TOTAL:.1f}s")


if __name__ == "__main__":
    main()
