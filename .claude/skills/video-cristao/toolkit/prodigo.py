"""O Filho Pródigo (Lucas 15:11-32) — ilustração chapada/geométrica com textura de papel.

Renderização (via engine.py):
    python3 prodigo_audio.py                                   # trilha_prodigo.wav
    python3 engine.py wide prodigo filho_prodigo.mp4 trilha_prodigo.wav
    VIDEO_LANG=en python3 engine.py wide prodigo prodigal_son_en.mp4 trilha_prodigo.wav
"""
import math
import os
import random

import cairo

from render import (EN, GOLD, LANG, SANS, TAU, TITLE, H, W, appeal_lines, clamp, eback, eio, eout, glow, hexc,
                    lerp, overlay, particles, rays, ridge, seg, subscribe, text_center, town)

TEXTURE = True
VIGNETTE = 0.35

INK = "#140d1b"
TEAL = "#5fe0cf"
GOLD2 = "#d98a1c"
CREAM = "#fff4dc"


def fill(c, col, a=1.0):
    r, g, b = hexc(col) if isinstance(col, str) else col
    c.set_source_rgba(r, g, b, a)
    c.fill()


def paint(c, col):
    c.set_source_rgb(*(hexc(col) if isinstance(col, str) else col))
    c.paint()


def blob(c, cx, cy, r, seed, t=0.0, wob=0.0, n=9):
    """Forma orgânica grande (as 'manchas' de fundo do estilo)."""
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        a = k / n * TAU
        rad = r * (rnd.uniform(0.84, 1.12) + wob * math.sin(t * 1.3 + k * 1.7))
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    c.move_to((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        c.curve_to(p[0], p[1], p[0], p[1], (p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    c.close_path()


def bands(c, cols, y0=0, y1=H):
    """Céu em faixas chapadas (sem degradê)."""
    n = len(cols)
    for k, col in enumerate(cols):
        c.rectangle(0, y0 + (y1 - y0) * k / n, W, (y1 - y0) / n + 1)
        fill(c, col)


def sun(c, x, y, r, cols=("#f28c1e", "#f7a531", "#ffd25a")):
    for k, col in enumerate(cols):
        c.arc(x, y, r * (1 - k * 0.22), 0, TAU)
        fill(c, col)


def cloud(c, x, y, s, col="#ffffff", a=0.9):
    for dx, dy, r in ((0, 0, 0.5), (-0.55, 0.12, 0.36), (0.55, 0.1, 0.4), (0.2, -0.2, 0.42)):
        c.new_sub_path()
        c.arc(x + dx * s, y + dy * s, r * s, 0, TAU)
    c.rectangle(x - 0.9 * s, y + 0.1 * s, 1.8 * s, 0.4 * s)
    fill(c, col, a)


# ───────────────────────── personagens ─────────────────────────
ARMS = {
    "stand": ([(-0.15, -0.72), (-0.21, -0.46), (-0.19, -0.27)], [(0.15, -0.72), (0.21, -0.46), (0.19, -0.27)]),
    "reach": ([(-0.15, -0.72), (-0.21, -0.46), (-0.19, -0.27)], [(0.15, -0.72), (0.36, -0.62), (0.55, -0.64)]),
    "give": ([(-0.15, -0.72), (-0.21, -0.46), (-0.19, -0.27)], [(0.15, -0.72), (0.33, -0.56), (0.5, -0.52)]),
    "open": ([(-0.15, -0.72), (-0.4, -0.72), (-0.62, -0.86)], [(0.15, -0.72), (0.4, -0.72), (0.62, -0.86)]),
    "raised": ([(-0.15, -0.72), (-0.3, -0.96), (-0.33, -1.2)], [(0.15, -0.72), (0.3, -0.96), (0.33, -1.2)]),
    "dance": ([(-0.15, -0.72), (-0.3, -0.96), (-0.33, -1.2)], [(0.15, -0.72), (0.38, -0.62), (0.56, -0.76)]),
    "hug": ([(-0.12, -0.72), (0.18, -0.64), (0.46, -0.66)], [(0.15, -0.72), (0.4, -0.74), (0.56, -0.66)]),
    "carry": ([(-0.15, -0.72), (-0.21, -0.46), (-0.19, -0.27)], [(0.15, -0.72), (0.27, -0.88), (0.17, -0.99)]),
    "shade": ([(-0.15, -0.72), (-0.21, -0.46), (-0.19, -0.27)], [(0.15, -0.72), (0.3, -0.82), (0.13, -0.93)]),
    "sad": ([(-0.13, -0.7), (-0.16, -0.46), (-0.1, -0.28)], [(0.13, -0.7), (0.17, -0.46), (0.12, -0.28)]),
}


def person(c, x, y, h, pose="stand", facing=1, col=INK, sash=None, scarf=None, ragged=False, phase=None,
           run=False, head=(0.0, 0.0), a=1.0):
    """Silhueta geométrica: manto em trapézio, ombros retos, faixa diagonal colorida."""
    c.save()
    c.translate(x, y)
    bob = 0.0
    if phase is not None:
        bob = abs(math.sin(phase)) * (0.05 if run else 0.018)
    c.scale(h * facing, h)
    c.translate(0, -bob)
    if run:
        c.rotate(0.22)
    arms = ARMS[pose]
    if phase is not None:
        s = math.sin(phase)
        if run:
            arms = ([(-0.14, -0.72), (-0.3 - 0.1 * s, -0.55), (-0.42 - 0.12 * s, -0.72 + 0.1 * s)],
                    [(0.15, -0.72), (0.34 + 0.1 * s, -0.78), (0.48 + 0.12 * s, -0.95 - 0.1 * s)])
        elif pose in ("stand", "sad"):
            arms = ([arms[0][0], (-0.2 - 0.06 * s, -0.46), (-0.17 - 0.12 * s, -0.28)],
                    [arms[1][0], (0.2 + 0.06 * s, -0.46), (0.17 + 0.12 * s, -0.28)])
        # pés
        for sg in (1, -1):
            fx = 0.1 * sg * s * (2.2 if run else 1.0) + 0.04
            c.save()
            c.translate(fx, 0.0)
            c.scale(1, 0.45)
            c.arc(0, 0, 0.06, 0, TAU)
            c.restore()
            fill(c, col, a)
    # braços (atrás do corpo o esquerdo, na frente o direito)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_width(0.075)
    r = hexc(col)

    def arm(pts):
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_source_rgba(r[0], r[1], r[2], a)
        c.stroke()
        c.arc(pts[-1][0], pts[-1][1], 0.042, 0, TAU)
        fill(c, col, a)

    arm(arms[0])
    # manto
    c.move_to(-0.15, -0.79)
    c.line_to(0.15, -0.79)
    c.curve_to(0.22, -0.76, 0.25, -0.62, 0.26, -0.45)
    c.line_to(0.31, -0.02)
    if ragged:
        for k in range(8):
            c.line_to(0.31 - (k + 0.5) * 0.0775, -0.09 if k % 2 == 0 else -0.02)
    c.line_to(-0.31, -0.02)
    c.line_to(-0.26, -0.45)
    c.curve_to(-0.25, -0.62, -0.22, -0.76, -0.15, -0.79)
    c.close_path()
    fill(c, col, a)
    if sash:
        c.move_to(0.05, -0.79)
        c.line_to(0.15, -0.79)
        c.line_to(-0.12, -0.02)
        c.line_to(-0.24, -0.02)
        c.close_path()
        fill(c, sash, a)
        c.move_to(0.15, -0.79)
        c.line_to(0.19, -0.77)
        c.line_to(-0.07, -0.02)
        c.line_to(-0.12, -0.02)
        c.close_path()
        fill(c, "#000000", 0.18 * a)
    # pescoço e cabeça
    hx, hy = 0.0 + head[0], -0.9 + head[1]
    c.rectangle(-0.035, -0.84, 0.07, 0.07)
    fill(c, col, a)
    c.arc(hx, hy, 0.085, 0, TAU)
    fill(c, col, a)
    if scarf:
        c.move_to(hx - 0.1, hy + 0.02)
        c.curve_to(hx - 0.1, hy - 0.14, hx + 0.1, hy - 0.14, hx + 0.1, hy + 0.0)
        c.line_to(hx + 0.07, hy + 0.0)
        c.line_to(hx - 0.02, hy - 0.04)
        c.line_to(hx - 0.12, hy + 0.25)
        c.line_to(hx - 0.2, hy + 0.22)
        c.close_path()
        fill(c, scarf, a)
    arm(arms[1])
    c.restore()


def sitting(c, x, y, h, facing=1, col=INK, look_up=0.0, sash=None, ragged=True):
    c.save()
    c.translate(x, y)
    c.scale(h * facing, h)
    c.move_to(-0.3, 0)
    c.line_to(0.34, 0)
    c.curve_to(0.36, -0.2, 0.34, -0.36, 0.26, -0.38)
    c.line_to(0.1, -0.4)
    c.curve_to(0.08, -0.52, 0.04, -0.6, -0.02, -0.62)
    c.curve_to(-0.16, -0.62, -0.26, -0.5, -0.28, -0.3)
    c.close_path()
    fill(c, col)
    if ragged:
        for k in range(5):
            c.move_to(-0.3 + k * 0.13, 0)
            c.line_to(-0.24 + k * 0.13, -0.06)
            c.line_to(-0.18 + k * 0.13, 0)
            fill(c, col)
    if sash:
        c.move_to(-0.04, -0.6)
        c.line_to(0.04, -0.6)
        c.line_to(-0.1, -0.08)
        c.line_to(-0.18, -0.1)
        c.close_path()
        fill(c, sash)
    hx = 0.1 - 0.06 * look_up
    hy = -0.62 - 0.1 * look_up
    c.arc(hx, hy, 0.085, 0, TAU)
    fill(c, col)
    c.set_line_width(0.075)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(0.04, -0.52)
    c.line_to(0.22, -0.38)
    c.line_to(0.3, -0.3)
    r = hexc(col)
    c.set_source_rgb(*r)
    c.stroke()
    c.restore()


def hug(c, x, y, h, glow_a=0.0):
    """Pai (faixa verde-água, lenço) abraçando o filho (maltrapilho)."""
    if glow_a:
        glow(c, x, y - h * 0.6, h * 1.6, "#fff1c2", 0.8 * glow_a)
    person(c, x + h * 0.11, y, h * 0.95, "hug", facing=-1, ragged=True, head=(0.03, 0.04))
    person(c, x - h * 0.11, y, h, "hug", facing=1, sash=TEAL, scarf="#efe6d2", head=(0.03, 0.02))


def house(c, x, y, s, lit=1.0, t=0.0, wall="#f28c1e", roof="#c9602a", door=INK):
    """Casa de pedra de teto plano (Oriente Médio), base em (x, y)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rectangle(-150, -170, 300, 170)
    fill(c, wall)
    c.rectangle(-165, -190, 330, 26)
    fill(c, roof)
    c.rectangle(60, -250, 90, 62)
    fill(c, wall)
    c.rectangle(52, -262, 106, 16)
    fill(c, roof)
    c.move_to(-30, 0)
    c.line_to(-30, -90)
    c.arc(0, -90, 30, math.pi, TAU)
    c.line_to(30, 0)
    fill(c, door)
    for wx in (-105, 78):
        c.rectangle(wx, -130, 36, 40)
        if lit:
            fill(c, "#ffd25a", 0.5 + 0.5 * lit * (0.85 + 0.15 * math.sin(t * 5 + wx)))
        else:
            fill(c, door)
    c.restore()


def tree(c, x, y, s, col="#1f7a45", col2="#2fa060", trunk="#6b3a1e"):
    c.rectangle(x - 0.06 * s, y - 0.6 * s, 0.12 * s, 0.6 * s)
    fill(c, trunk)
    c.arc(x, y - 0.85 * s, 0.38 * s, 0, TAU)
    fill(c, col)
    c.arc(x - 0.1 * s, y - 0.95 * s, 0.22 * s, 0, TAU)
    fill(c, col2)


def coin(c, x, y, r, a=1.0):
    c.arc(x, y, r, 0, TAU)
    fill(c, GOLD, a)
    c.set_line_width(r * 0.22)
    c.arc(x, y, r * 0.7, 0, TAU)
    c.set_source_rgba(*hexc(GOLD2), a)
    c.stroke()


def bag(c, x, y, s, a=1.0, empty=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s * (0.55 if empty else 1))
    c.move_to(-0.18, -0.9)
    c.line_to(0.18, -0.9)
    c.curve_to(0.6, -0.6, 0.55, 0, 0, 0)
    c.curve_to(-0.55, 0, -0.6, -0.6, -0.18, -0.9)
    fill(c, GOLD2, a)
    c.rectangle(-0.22, -0.95, 0.44, 0.1)
    fill(c, "#8a4a12", a)
    c.restore()


def pig(c, x, y, s, t, facing=1, seed=0):
    root = math.sin(t * 3 + seed) * 0.06
    c.save()
    c.translate(x, y)
    c.scale(s * facing, s)
    c.set_line_width(0.12)
    c.set_source_rgb(*hexc("#d9736a"))
    for lx in (-0.45, -0.25, 0.25, 0.45):
        c.move_to(lx, -0.3)
        c.line_to(lx, 0)
    c.stroke()
    c.save()
    c.translate(0, -0.55)
    c.scale(1, 0.62)
    c.arc(0, 0, 0.7, 0, TAU)
    c.restore()
    fill(c, "#f4978e")
    c.save()
    c.translate(0.7, -0.5 + root)
    c.rotate(0.3 + root)
    c.arc(0, 0, 0.32, 0, TAU)
    fill(c, "#f4978e")
    c.move_to(-0.1, -0.25)
    c.line_to(0.1, -0.5)
    c.line_to(0.18, -0.2)
    fill(c, "#d9736a")
    c.save()
    c.translate(0.32, 0.05)
    c.scale(0.5, 1)
    c.arc(0, 0, 0.14, 0, TAU)
    c.restore()
    fill(c, "#d9736a")
    c.arc(0.1, -0.08, 0.04, 0, TAU)
    fill(c, INK)
    c.restore()
    c.set_line_width(0.06)
    c.move_to(-0.68, -0.62)
    c.curve_to(-0.9, -0.8, -0.95, -0.5, -0.8, -0.55)
    c.set_source_rgb(*hexc("#d9736a"))
    c.stroke()
    c.restore()


def lanterns(c, y0, sag, t, cols, off_after=None, seed=0):
    rnd = random.Random(seed)
    c.set_line_width(3)
    c.set_source_rgba(0, 0, 0, 0.5)
    pts = []
    for k in range(0, 21):
        x = -40 + k * (W + 80) / 20
        u = k / 20
        y = y0 + sag * 4 * u * (1 - u)
        pts.append((x, y))
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()
    for k, (x, y) in enumerate(pts[1:-1]):
        on = 1.0
        if off_after is not None:
            on = 1 - seg(t, off_after + rnd.uniform(0, 1.2), off_after + rnd.uniform(0, 1.2) + 0.08)
        col = cols[k % len(cols)]
        fl = 0.85 + 0.15 * math.sin(t * 6 + k)
        if on > 0:
            glow(c, x, y + 18, 60, col, 0.45 * on * fl)
        c.rectangle(x - 10, y + 4, 20, 28)
        fill(c, col if on > 0.5 else "#3a2a44")


def speed_lines(c, x, y, h, facing, a):
    c.set_line_width(5)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(4):
        yy = y - h * (0.25 + k * 0.17)
        L = h * (0.35 + 0.15 * (k % 2))
        c.move_to(x - facing * h * 0.45, yy)
        c.line_to(x - facing * (h * 0.45 + L), yy)
    c.set_source_rgba(1, 1, 1, 0.55 * a)
    c.stroke()


def zoom(c, z, cx, cy):
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)


# ───────────────────────── cenas ─────────────────────────
def s_intro(c, t, d):
    paint(c, "#4a2f5c")
    blob(c, W * 0.72, H * 0.6, 540, 4, t, 0.02)
    fill(c, "#3a2249")
    sun(c, W * 0.8, H * 0.5, 140, ("#f28c1e", "#f7a531", "#ffd25a"))
    ridge(c, H * 0.78, 30, 0.5, 0, "#2c1b38", seed=3)
    # estrada saindo da casa
    c.move_to(W * 0.74, H * 0.8)
    c.curve_to(W * 0.8, H * 0.9, W * 0.95, H * 0.88, W + 20, H * 0.95)
    c.line_to(W + 20, H + 10)
    c.curve_to(W * 0.9, H, W * 0.76, H * 0.94, W * 0.7, H * 0.8)
    fill(c, "#6b4a7a")
    house(c, W * 0.66, H * 0.8, 0.9, 1.0, t, wall="#e07a3a", roof="#b5552a")
    person(c, W * 0.76, H * 0.82, 230, "shade", sash=TEAL, scarf="#efe6d2")
    # título
    for k, (txt, size, face, col, y) in enumerate((
            (tr_("Uma parábola de Jesus"), 46, SANS, TEAL, 330),
            (tr_("O Filho"), 150, SANS, "#ffffff", 480),
            (tr_("Pródigo"), 150, SANS, "#ffffff", 630))):
        p = eout(seg(t, 0.3 + k * 0.35, 1.1 + k * 0.35))
        c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(size)
        c.move_to(140, y + (1 - p) * 40)
        c.set_source_rgba(*hexc(col), p)
        c.show_text(txt)
    ln = eout(seg(t, 1.2, 2.0))
    c.rectangle(144, 680, 260 * ln, 8)
    fill(c, GOLD)


def s_heranca(c, t, d):
    zoom(c, lerp(1.0, 1.06, t / d), W * 0.52, H * 0.6)
    paint(c, "#7cc6d6")
    sun(c, W * 0.82, H * 0.22, 120, ("#ffe28a", "#ffd25a", "#fff1b8"))
    for k, (x, y, s) in enumerate(((W * 0.2, 150, 110), (W * 0.55, 110, 90), (W * 0.95, 190, 120))):
        cloud(c, (x + t * 18 * (k + 1)) % (W + 300) - 150, y, s)
    ridge(c, H * 0.6, 40, 0.5, 0, "#5fbf7a", seed=11)
    ridge(c, H * 0.72, 25, 0.7, 1, "#2fa060", seed=12)
    tree(c, W * 0.08, H * 0.74, 300)
    house(c, W * 0.27, H * 0.76, 1.3, 0.0, t)
    c.rectangle(0, H * 0.84, W, H)
    fill(c, "#1f7a45")
    fx, fy, fh = W * 0.45, H * 0.9, 380
    sx, sy, sh = W * 0.63, H * 0.9, 360
    give = t > 3.3
    person(c, fx, fy, fh, "give" if give else "stand", sash=TEAL, scarf="#efe6d2")
    person(c, sx, sy, sh, "reach" if t > 1.4 else "stand", facing=-1, sash="#f28c1e")
    # a bolsa com a herança
    hx0, hy0 = fx + 0.5 * fh, fy - 0.52 * fh
    hx1, hy1 = sx - 0.55 * sh, sy - 0.64 * sh
    if give:
        u = eio(seg(t, 4.1, 5.1))
        bx, by = lerp(hx0, hx1, u), lerp(hy0, hy1, u) - math.sin(u * math.pi) * 60
        pop = eback(seg(t, 3.3, 3.8))
        bag(c, bx, by + 70 * pop, 90 * pop)
        for k in range(4):
            e = seg(t, 5.1 + k * 0.18, 6.3 + k * 0.18)
            if 0 < e < 1:
                coin(c, hx1 + (k - 1.5) * 40 * e, hy1 - 40 - 140 * math.sin(e * math.pi), 16, 1 - e * 0.5)


def s_partida(c, t, d):
    p = t / d
    zoom(c, lerp(1.0, 1.07, p), W * 0.4, H * 0.66)
    bands(c, ["#8a3a5c", "#b5485d", "#e76f51", "#f4a261"], 0, H * 0.66)
    sun(c, W * 0.64, H * 0.64, 170, ("#f28c1e", "#f7a531", "#ffd25a"))
    ridge(c, H * 0.6, 45, 0.5, 0, "#8a3f5e", seed=21)
    ridge(c, H * 0.7, 30, 0.6, 1, "#5a2548", seed=22)
    # estrada até o horizonte
    c.move_to(W * 0.2, H + 10)
    c.curve_to(W * 0.45, H * 0.86, W * 0.6, H * 0.74, W * 0.66, H * 0.68)
    c.line_to(W * 0.675, H * 0.68)
    c.curve_to(W * 0.66, H * 0.76, W * 0.62, H * 0.88, W * 0.5, H + 10)
    fill(c, "#d98a6a")
    house(c, W * 0.12, H * 0.74, 0.75, 1.0, t, wall="#7a3a4a", roof="#5a2a3a")
    person(c, W * 0.2, H * 0.76, 190, "shade", sash=TEAL, scarf="#efe6d2")
    # filho indo embora
    u = eio(clamp(p * 1.05))
    x = lerp(W * 0.36, W * 0.664, u)
    y = lerp(H * 1.02, H * 0.69, u ** 0.8)
    h = lerp(380, 40, u ** 0.65)
    person(c, x, y, h, "carry", sash="#f28c1e", phase=t * 5.5)
    bag(c, x + 0.16 * h, y - 0.93 * h, 0.28 * h)


def s_desperdicio(c, t, d):
    off = 5.2
    dark = eio(seg(t, off, off + 1.5))
    paint(c, "#2a1245")
    blob(c, W * 0.5, H * 0.5, 620, 31, t, 0.03)
    fill(c, "#3d1a60")
    town(c, H * 0.68, "#1c0b30", seed=6, scale=1.0, lit=1 - dark, t=t)
    lanterns(c, 60, 140, t, ["#ff5d8f", "#ffd25a", TEAL, "#f28c1e"], off_after=off, seed=1)
    lanterns(c, 180, 110, t + 1, ["#ffd25a", "#ff5d8f", "#f28c1e", TEAL], off_after=off, seed=2)
    c.rectangle(0, H * 0.86, W, H)
    fill(c, "#1a0a2a")
    # amigos dançando (vão embora quando o dinheiro acaba)
    rnd = random.Random(5)
    for k, fx in enumerate((0.16, 0.28, 0.38, 0.62, 0.72, 0.84)):
        side = -1 if fx < 0.5 else 1
        leave = eio(seg(t, off + 0.2 + k * 0.1, off + 1.6 + k * 0.1))
        x = W * fx + side * leave * 700
        bob = math.sin(t * 7 + k) * 10
        person(c, x, H * 0.9 + bob, rnd.uniform(280, 330), "dance" if (int(t * 2 + k) % 2) else "raised",
               facing=-side, sash=["#ff5d8f", TEAL, GOLD, "#f28c1e"][k % 4], a=1 - leave * 0.2)
    # o filho no centro jogando moedas
    party = t < off
    person(c, W * 0.5, H * 0.92, 380, "raised" if party else "sad", sash="#ff5d8f",
           head=(0.0, 0.0) if party else (0.06, 0.05))
    hx, hy = W * 0.5, H * 0.92 - 380 * 1.2
    for k in range(20):
        tk = 0.3 + k * 0.24
        age = t - tk
        if 0 < age < 1.6 and tk < off:
            vx = (k % 5 - 2) * 170
            x = hx + vx * age
            y = hy - 520 * age + 520 * age * age
            coin(c, x, y, 15, clamp(1.6 - age))
    # confete
    rnd = random.Random(8)
    ca = 1 - seg(t, off, off + 0.8)
    if ca > 0:
        for _ in range(90):
            x = rnd.uniform(0, W)
            y = (rnd.uniform(0, H) + t * rnd.uniform(90, 200)) % H
            c.save()
            c.translate(x, y)
            c.rotate(t * rnd.uniform(-4, 4))
            c.rectangle(-6, -3, 12, 6)
            fill(c, rnd.choice(["#ff5d8f", "#ffd25a", TEAL, "#f28c1e"]), ca)
            c.restore()
    if not party:
        bag(c, W * 0.5 + 150, H * 0.92, 60, empty=True)
    overlay(c, "#05010a", 0.45 * dark)


def s_fome(c, t, d):
    zoom(c, lerp(1.0, 1.05, t / d), W * 0.35, H * 0.75)
    bands(c, ["#e76f51", "#ee8959", "#f4a261"], 0, H * 0.66)
    sun(c, W * 0.7, H * 0.26, 150 + 4 * math.sin(t * 2), ("#ffe8a3", "#fff1c4", "#fffae6"))
    ridge(c, H * 0.64, 25, 0.4, 0, "#c26a3a", seed=41)
    c.rectangle(0, H * 0.72, W, H)
    fill(c, "#a0522d")
    rnd = random.Random(4)
    c.set_line_width(4)
    c.set_source_rgb(*hexc("#6e3a1e"))
    for _ in range(26):
        x, y = rnd.uniform(0, W), rnd.uniform(H * 0.75, H)
        c.move_to(x, y)
        for _ in range(3):
            x += rnd.uniform(20, 70)
            y += rnd.uniform(-15, 15)
            c.line_to(x, y)
    c.stroke()
    # árvore seca
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgb(*hexc("#4a2a18"))
    for lw, pts in ((26, [(W * 0.1, H * 0.8), (W * 0.11, H * 0.55), (W * 0.08, H * 0.4)]),
                    (14, [(W * 0.11, H * 0.6), (W * 0.16, H * 0.5), (W * 0.2, H * 0.47)]),
                    (12, [(W * 0.1, H * 0.5), (W * 0.05, H * 0.44)]),
                    (9, [(W * 0.16, H * 0.5), (W * 0.17, H * 0.42)])):
        c.set_line_width(lw)
        c.move_to(*pts[0])
        for q in pts[1:]:
            c.line_to(*q)
        c.stroke()
    # cerca e cocho
    for k in range(12):
        c.rectangle(W * 0.42 + k * 95, H * 0.7, 14, 110)
    c.rectangle(W * 0.42, H * 0.73, W * 0.58, 12)
    c.rectangle(W * 0.42, H * 0.78, W * 0.58, 12)
    fill(c, "#5a3420")
    c.move_to(W * 0.58, H * 0.78)
    c.line_to(W * 0.72, H * 0.78)
    c.line_to(W * 0.7, H * 0.83)
    c.line_to(W * 0.6, H * 0.83)
    fill(c, "#6e3a1e")
    pig(c, W * 0.54, H * 0.83, 95, t, 1, 0)
    pig(c, W * 0.78, H * 0.84, 110, t, -1, 2)
    pig(c, W * 0.9, H * 0.79, 80, t, -1, 4)
    sitting(c, W * 0.3, H * 0.86, 330, 1, INK, look_up=0.0)
    particles(c, t, 50, 43, "#f4d58d", 0.5, rise=-25, size=(1.5, 4), area=(0, H * 0.5, W, H))


def _memoria(c, cx, cy, r, t):
    blob(c, cx, cy, r, 51, t, 0.025, n=10)
    path = c.copy_path()
    c.set_source_rgb(*hexc(CREAM))
    c.fill()
    c.save()
    c.new_path()
    c.append_path(path)
    c.clip()
    c.translate(cx, cy)
    k = r / 330
    c.scale(k, k)
    c.rectangle(-400, -400, 800, 400)
    fill(c, "#ffd9a0")
    sun(c, 150, -120, 80, ("#ffd25a", "#ffe28a", "#fff1b8"))
    c.rectangle(-400, 60, 800, 400)
    fill(c, "#e9a86a")
    house(c, -40, 90, 0.8, 1.0, t)
    person(c, 150, 120, 200, "open", facing=-1, sash=TEAL, scarf="#efe6d2")
    for k2, bx in enumerate((-250, -205, -160)):
        c.save()
        c.translate(bx, 150)
        c.scale(1, 0.55)
        c.arc(0, 0, 28, 0, TAU)
        c.restore()
        fill(c, "#c9803a")
    c.restore()
    c.new_path()
    c.append_path(path)
    c.set_line_width(10)
    c.set_source_rgb(1, 1, 1)
    c.stroke()


def s_despertar(c, t, d):
    paint(c, "#1f2a8a")
    blob(c, W * 0.62, H * 0.45, 600, 53, t, 0.02)
    fill(c, "#2a36a8")
    rnd = random.Random(2)
    for _ in range(80):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.6)
        c.arc(x, y, rnd.uniform(1.5, 3.2), 0, TAU)
        fill(c, "#fff6d8", 0.5 + 0.4 * math.sin(t * 2 + x))
    c.arc(W * 0.92, H * 0.14, 60, 0, TAU)
    fill(c, CREAM)
    c.arc(W * 0.92 + 28, H * 0.14 - 14, 54, 0, TAU)
    fill(c, "#1f2a8a")
    ridge(c, H * 0.8, 25, 0.5, 0, "#141a5a", seed=55)
    c.move_to(W * 0.16, H * 0.9)
    c.curve_to(W * 0.17, H * 0.8, W * 0.36, H * 0.78, W * 0.4, H * 0.9)
    fill(c, "#10154a")
    look = eout(seg(t, 1.0, 2.0))
    stand = eout(seg(t, 6.8, 7.3))
    if stand < 1:
        sitting(c, W * 0.28, H * 0.85, 300, 1, INK, look_up=look)
    if stand > 0:
        person(c, W * 0.29, H * 0.85 - (1 - stand) * 30, 360, "stand", ragged=True, a=stand)
    # balões de pensamento + memória da casa do pai
    for k in range(3):
        e = eback(seg(t, 1.2 + k * 0.2, 1.5 + k * 0.2))
        c.arc(W * (0.36 + k * 0.045), H * (0.5 - k * 0.05), (10 + k * 7) * e, 0, TAU)
        fill(c, CREAM)
    r = 330 * eback(seg(t, 1.8, 2.8)) * (1 + 0.03 * math.sin(t * 2.5))
    if r > 1:
        _memoria(c, W * 0.66, H * 0.42, r, t)


def s_volta(c, t, d):
    p = t / d
    zoom(c, lerp(1.0, 1.05, p), W * 0.6, H * 0.8)
    bands(c, ["#264653", "#287271", "#2a9d8f", "#8ab17d", "#e9c46a"], 0, H * 0.68)
    sun(c, W * 0.28, H * 0.68 - 40 * p, 110, ("#f4a261", "#f7c46a", "#ffe28a"))
    ridge(c, H * 0.66, 30, 0.5, 0, "#1d5e5a", seed=61)
    ridge(c, H * 0.74, 22, 0.6, 1, "#16413f", seed=62)
    c.move_to(W * 0.56, H + 10)
    c.curve_to(W * 0.5, H * 0.86, W * 0.34, H * 0.74, W * 0.27, H * 0.7)
    c.line_to(W * 0.285, H * 0.7)
    c.curve_to(W * 0.42, H * 0.76, W * 0.78, H * 0.88, W * 0.96, H + 10)
    fill(c, "#d9b27a")
    for rx, ry, rr in ((W * 0.08, H * 0.92, 60), (W * 0.9, H * 0.8, 40), (W * 0.15, H * 0.8, 30)):
        c.arc(rx, ry, rr, math.pi, TAU)
        fill(c, "#10302e")
    u = p
    x = lerp(W * 0.8, W * 0.58, u)
    y = lerp(H * 1.0, H * 0.86, u)
    h = lerp(430, 320, u)
    person(c, x, y, h, "sad", facing=-1, ragged=True, phase=t * 3.6, head=(0.06, 0.06))


def s_pai_corre(c, t, d):
    meet = 5.0
    z = lerp(1.0, 1.3, eio(seg(t, meet, d)))
    hxm, hym = W * 0.585, H * 0.86
    zoom(c, z, hxm, hym - 150)
    bands(c, ["#f28c1e", "#f7a531", "#ffc75a"], 0, H * 0.7)
    sun(c, hxm, H * 0.66, 200, ("#ffd25a", "#ffe28a", "#fff4c8"))
    burst = eout(seg(t, meet, meet + 1.2))
    if burst > 0:
        rays(c, hxm, hym - 200, 22, 1400 * burst, t * 0.1, "#fff4c8", 0.35 * burst, width=0.12)
    ridge(c, H * 0.68, 20, 0.5, 0, "#e07a4a", seed=71)
    # colina do pai (à esquerda)
    c.move_to(-10, H + 10)
    c.line_to(-10, H * 0.55)
    c.line_to(W * 0.22, H * 0.55)
    c.curve_to(W * 0.34, H * 0.57, W * 0.42, H * 0.8, W * 0.56, H * 0.86)
    c.line_to(W + 10, H * 0.86)
    c.line_to(W + 10, H + 10)
    fill(c, "#c9573a")
    c.rectangle(0, H * 0.86, W, H)
    fill(c, "#9c3d2e")
    house(c, W * 0.11, H * 0.555, 0.85, 0.0, t)
    # pai: vê, depois corre ladeira abaixo
    run = seg(t, 1.8, meet)
    if t < meet:
        if run <= 0:
            person(c, W * 0.21, H * 0.56, 200, "shade", sash=TEAL, scarf="#efe6d2")
        else:
            u = eio(run) if run < 0.15 else run
            x = lerp(W * 0.21, hxm - 0.11 * 330, u)
            if x < W * 0.22:
                y = H * 0.56
            else:
                v = (x - W * 0.22) / (hxm - 0.11 * 330 - W * 0.22)
                y = lerp(H * 0.56, hym, clamp(v) ** 1.3)
            h = lerp(200, 330, u)
            person(c, x, y, h, "stand", sash=TEAL, scarf="#efe6d2", phase=t * 13, run=True)
            speed_lines(c, x, y, h, 1, clamp(run * 4))
        # filho se aproximando devagar
        u2 = clamp(t / meet)
        sx = lerp(W * 0.92, hxm + 0.11 * 330, u2)
        sh = lerp(150, 314, u2)
        person(c, sx, lerp(H * 0.83, hym, u2), sh, "sad", facing=-1, ragged=True, phase=t * 3.6, head=(0.06, 0.06))
    else:
        hug(c, hxm, hym, 330, glow_a=burst)
        particles(c, t, 70, 77, "#fff4c8", burst, rise=50, area=(hxm - 500, hym - 700, hxm + 500, hym))


def s_festa_pai(c, t, d):
    zoom(c, lerp(1.0, 1.05, t / d), W * 0.52, H * 0.6)
    paint(c, "#7a2e4a")
    blob(c, W * 0.52, H * 0.5, 620, 81, t, 0.03)
    fill(c, "#9c3d5c")
    lanterns(c, 50, 160, t, ["#ffd25a", "#f7a531", CREAM], seed=3)
    lanterns(c, 170, 120, t + 1, ["#f7a531", "#ffd25a"], seed=4)
    # dançando nas laterais
    for k, fx in enumerate((0.1, 0.2, 0.8, 0.9)):
        bob = math.sin(t * 6 + k * 1.3) * 12
        person(c, W * fx, H * 0.82 + bob, 300, "dance" if (int(t * 2.2 + k) % 2) else "raised",
               facing=1 if fx < 0.5 else -1, sash=[TEAL, "#ff5d8f", GOLD, "#f28c1e"][k])
    # pai e filho de roupa nova
    person(c, W * 0.44, H * 0.82, 380, "open", sash=TEAL, scarf="#efe6d2")
    new = eout(seg(t, 0.4, 1.6))
    if new < 1:
        person(c, W * 0.58, H * 0.82, 360, "stand", facing=-1, ragged=True, a=1 - new)
    if new > 0:
        person(c, W * 0.58, H * 0.82, 360, "raised" if t > 4.5 else "stand", facing=-1, col="#f5ecd7",
               sash=GOLD, a=new)
    # brilho do anel
    e = seg(t, 1.8, 3.2)
    if 0 < e < 1:
        rx, ry = W * 0.58 - 0.19 * 360 * -1, H * 0.82 - 0.27 * 360
        sz = 30 * math.sin(e * math.pi)
        c.save()
        c.translate(rx, ry)
        for k in range(4):
            c.rotate(math.pi / 4)
            c.move_to(0, -sz)
            c.line_to(sz * 0.18, 0)
            c.line_to(0, sz)
            c.line_to(-sz * 0.18, 0)
            c.close_path()
            fill(c, "#fff8d8")
        c.restore()
    # mesa
    c.rectangle(W * 0.2, H * 0.84, W * 0.6, 30)
    fill(c, "#5a2a1a")
    c.rectangle(W * 0.22, H * 0.84 + 30, W * 0.56, H)
    fill(c, "#43200f")
    for k in range(9):
        bx = W * 0.24 + k * W * 0.065
        c.save()
        c.translate(bx, H * 0.835)
        c.scale(1, 0.5)
        c.arc(0, 0, 30, math.pi, TAU)
        c.restore()
        fill(c, ["#e0a458", "#7b2d8e", "#c9803a"][k % 3])
    rnd = random.Random(8)
    for _ in range(70):
        x = rnd.uniform(0, W)
        y = (rnd.uniform(0, H) + t * rnd.uniform(90, 200)) % H
        c.save()
        c.translate(x, y)
        c.rotate(t * rnd.uniform(-4, 4))
        c.rectangle(-6, -3, 12, 6)
        fill(c, rnd.choice(["#ffd25a", TEAL, "#ff5d8f", CREAM]))
        c.restore()


APPEAL = [
    (0.4, 4.4, [("Não importa o quão *longe*", 78, SANS), ("você foi…", 78, SANS)]),
    (4.4, 8.4, [("O Pai está na estrada,", 64, SANS), ("*esperando por você*.", 84, SANS)]),
    (8.4, 12.2, [("Volte para casa.", 74, SANS), ("ELE TE AMA", 170, TITLE)]),
]


def s_final(c, t, d):
    paint(c, "#2a1a3a")
    rays(c, W / 2, H * 0.86, 24, 1500, t * 0.04, "#ffd25a", 0.1)
    sun(c, W / 2, H * 0.86, 260, ("#f28c1e", "#f7a531", "#ffd25a"))
    ridge(c, H * 0.88, 12, 0.4, 0, "#1a1024", seed=91)
    hug(c, W / 2, H * 0.89, 240)
    for a0, a1, lines in APPEAL:
        if a0 <= t < a1:
            appeal_lines(c, lines, t - a0, a1 - a0, cy=H * 0.36)
    if t >= 12.2:
        subscribe(c, t - 12.2, d - 12.2)
    overlay(c, "#000000", seg(t, d - 0.8, d))


# ───────────────────────── roteiro ─────────────────────────
SCENES = [
    ("", 6.0, s_intro, [(1.8, 5.9, "Jesus contou a história de um pai… e de um filho que *foi embora*.")]),
    ("I · A HERANÇA", 8.0, s_heranca, [
        (0.3, 4.0, "Um jovem diz ao pai: “Me dá a minha *herança*.”"),
        (4.0, 7.9, "Ele quer viver longe… do seu *jeito*.")]),
    ("II · A PARTIDA", 8.0, s_partida, [
        (0.3, 3.8, "Ele parte para uma *terra distante*."),
        (3.8, 7.9, "E o pai fica olhando a *estrada*…")]),
    ("III · O DESPERDÍCIO", 8.0, s_desperdicio, [
        (0.3, 4.8, "Festas, amigos, *dinheiro* jogado fora…"),
        (5.0, 7.9, "Até que tudo… *acaba*.")]),
    ("IV · A FOME", 9.0, s_fome, [
        (0.3, 4.2, "Vem a *fome*. Os amigos desaparecem."),
        (4.2, 8.9, "Ele cuida de porcos… e deseja a *comida* deles.")]),
    ("V · O DESPERTAR", 9.0, s_despertar, [
        (0.3, 3.4, "Então ele *cai em si*…"),
        (3.4, 8.9, "“Na casa do meu pai sobra *pão*… eu vou *voltar*.”")]),
    ("VI · A VOLTA", 8.0, s_volta, [
        (0.3, 3.8, "Ele volta com vergonha, ensaiando o que dizer:"),
        (3.8, 7.9, "“Pai, não sou digno de ser chamado teu *filho*…”")]),
    ("VII · O PAI CORRE", 9.0, s_pai_corre, [
        (0.3, 4.6, "Mas, quando ele *ainda estava longe*, o pai o viu…"),
        (4.8, 8.9, "…e *correu*. Abraçou. *Beijou*.")]),
    ("VIII · A FESTA", 9.0, s_festa_pai, [
        (0.3, 4.2, "Roupa nova, anel no dedo… *festa*!"),
        (4.2, 8.9, "“Meu filho estava *perdido*… e foi *achado*!”")]),
    ("", 17.0, s_final, []),
]
FADES = {0: ("#000000", None)}

STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)  # fator de desaceleração por cena (ajustado pela narração)

# falas narradas sem legenda (o apelo final já aparece grande na tela)
NARRATION_EXTRA = {
    9: [(0.4, "Não importa o quão longe você foi…"),
        (4.4, "O Pai está na estrada, esperando por você."),
        (8.4, "Volte para casa. Ele te ama."),
        (12.4, "Inscreva-se no canal para mais histórias que transformam vidas.")],
}

VERSES_PT = {
    "I": ("Pai, dá-me a parte dos bens que me pertence.", "Lucas 15:12"),
    "II": ("O filho mais novo, ajuntando tudo, partiu para uma terra longínqua.", "Lucas 15:13"),
    "III": ("E ali desperdiçou os seus bens, vivendo dissolutamente.", "Lucas 15:13"),
    "IV": ("Desejava encher o seu estômago com as bolotas que os porcos comiam.", "Lucas 15:16"),
    "V": ("Quantos trabalhadores de meu pai têm abundância de pão, e eu aqui pereço de fome!", "Lucas 15:17"),
    "VI": ("Levantar-me-ei, e irei ter com meu pai.", "Lucas 15:18"),
    "VII": ("Quando ainda estava longe, viu-o seu pai, e se moveu de íntima compaixão, e, correndo, "
            "lançou-se-lhe ao pescoço e o beijou.", "Lucas 15:20"),
    "VIII": ("Este meu filho estava morto, e reviveu; tinha-se perdido, e foi achado.", "Lucas 15:24"),
}
VERSES_EN = {  # King James Version (domínio público)
    "I": ("Father, give me the portion of goods that falleth to me.", "Luke 15:12"),
    "II": ("The younger son gathered all together, and took his journey into a far country.", "Luke 15:13"),
    "III": ("And there wasted his substance with riotous living.", "Luke 15:13"),
    "IV": ("He would fain have filled his belly with the husks that the swine did eat.", "Luke 15:16"),
    "V": ("How many hired servants of my father's have bread enough and to spare, and I perish with hunger!",
          "Luke 15:17"),
    "VI": ("I will arise and go to my father.", "Luke 15:18"),
    "VII": ("When he was yet a great way off, his father saw him, and had compassion, and ran, and fell on his "
            "neck, and kissed him.", "Luke 15:20"),
    "VIII": ("For this my son was dead, and is alive again; he was lost, and is found.", "Luke 15:24"),
}

EN.update({
    "Uma parábola de Jesus": "A parable of Jesus", "O Filho": "The Prodigal", "Pródigo": "Son",
    "I · A HERANÇA": "I · THE INHERITANCE", "II · A PARTIDA": "II · THE DEPARTURE",
    "III · O DESPERDÍCIO": "III · RIOTOUS LIVING", "IV · A FOME": "IV · THE FAMINE",
    "V · O DESPERTAR": "V · COMING TO HIMSELF", "VI · A VOLTA": "VI · THE RETURN",
    "VII · O PAI CORRE": "VII · THE FATHER RUNS", "VIII · A FESTA": "VIII · THE CELEBRATION",
    "Jesus contou a história de um pai… e de um filho que *foi embora*.":
        "Jesus told the story of a father… and a son who *walked away*.",
    "Um jovem diz ao pai: “Me dá a minha *herança*.”": "A young man tells his father: “Give me my *inheritance*.”",
    "Ele quer viver longe… do seu *jeito*.": "He wants to live far away… *his own way*.",
    "Ele parte para uma *terra distante*.": "He leaves for a *far country*.",
    "E o pai fica olhando a *estrada*…": "And the father keeps watching the *road*…",
    "Festas, amigos, *dinheiro* jogado fora…": "Parties, friends, *money* thrown away…",
    "Até que tudo… *acaba*.": "Until it's all… *gone*.",
    "Vem a *fome*. Os amigos desaparecem.": "*Famine* comes. His friends disappear.",
    "Ele cuida de porcos… e deseja a *comida* deles.": "He feeds pigs… and longs for their *food*.",
    "Então ele *cai em si*…": "Then he *comes to himself*…",
    "“Na casa do meu pai sobra *pão*… eu vou *voltar*.”": "“My father's house has *bread* to spare… I will *go back*.”",
    "Ele volta com vergonha, ensaiando o que dizer:": "He heads home in shame, rehearsing what to say:",
    "“Pai, não sou digno de ser chamado teu *filho*…”": "“Father, I am no longer worthy to be called your *son*…”",
    "Mas, quando ele *ainda estava longe*, o pai o viu…": "But while he was *still far away*, his father saw him…",
    "…e *correu*. Abraçou. *Beijou*.": "…and *ran*. Embraced him. *Kissed* him.",
    "Roupa nova, anel no dedo… *festa*!": "A new robe, a ring on his finger… a *feast*!",
    "“Meu filho estava *perdido*… e foi *achado*!”": "“My son was *lost*… and now is *found*!”",
    "Não importa o quão *longe*": "No matter how *far*", "você foi…": "you have gone…",
    "O Pai está na estrada,": "The Father is on the road,", "*esperando por você*.": "*waiting for you*.",
    "Volte para casa.": "Come back home.",
    "Não importa o quão longe você foi…": "No matter how far you have gone…",
    "O Pai está na estrada, esperando por você.": "The Father is on the road, waiting for you.",
    "Volte para casa. Ele te ama.": "Come back home. He loves you.",
    "Inscreva-se no canal para mais histórias que transformam vidas.":
        "Subscribe for more stories that transform lives.",
})


def tr_(s):
    return EN.get(s, s) if LANG == "en" else s


def verses():
    return VERSES_EN if LANG == "en" else VERSES_PT


if os.environ.get("VIDEO_NARRATION") == "prodigo":
    import narracao
    narracao.apply(globals(), "prodigo")
