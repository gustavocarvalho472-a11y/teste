"""A História de Jesus no estilo ilustração chapada (mesmo design do Filho Pródigo).

Mesmo roteiro, legendas, versículos e tempos de render.py; só as cenas são redesenhadas.

    VIDEO_LANG=pt python3 narracao.py jesus_flat
    export VIDEO_LANG=pt VIDEO_NARRATION=jesus_flat
    TRILHA_PROJ=jesus_flat TRILHA_OUT=trilha_jesus_flat_pt.wav python3 audio_emocional.py
    python3 narracao.py jesus_flat --mix trilha_jesus_flat_pt.wav trilha_jesus_flat_pt_narrada.wav
    python3 engine.py wide jesus_flat historia_de_jesus_narrado.mp4 trilha_jesus_flat_pt_narrada.wav
"""
import math
import os
import random

import cairo

import render
from prodigo import (ARMS, CREAM, GOLD2, INK, TEAL, bands, blob, cloud, fill, lanterns, paint, person, sun, tree,
                     zoom)
from render import (EN, GOLD, SANS, TAU, H, W, appeal_lines, camel, clamp, dove, eback, eio, eout, glow, hexc, lerp,
                    lightning, mix, overlay, palm, particles, ridge, seg, starburst, subscribe, text_center,
                    title_text, town, tr, water)

TEXTURE = True
VIGNETTE = 0.35
RED = "#c0182a"

ARMS.update({
    "bless": (ARMS["stand"][0], [(0.15, -0.72), (0.3, -0.95), (0.34, -1.2)]),
    "cross": ([(-0.15, -0.72), (-0.4, -0.74), (-0.62, -0.76)], [(0.15, -0.72), (0.4, -0.74), (0.62, -0.76)]),
    "shoulder": ([(-0.15, -0.72), (-0.02, -0.8), (0.08, -0.86)], [(0.15, -0.72), (0.22, -0.86), (0.12, -0.96)]),
    "torch": (ARMS["stand"][0], [(0.15, -0.72), (0.26, -0.9), (0.3, -1.08)]),
})


def halo(c, x, y, h, a=1.0):
    """Anel dourado atrás da cabeça de uma figura de altura h com pés em (x, y)."""
    if a <= 0:
        return
    c.set_line_width(max(2.0, h * 0.012))
    c.arc(x, y - 0.9 * h, 0.13 * h, 0, TAU)
    c.set_source_rgba(*hexc(GOLD), a)
    c.stroke()


def kneel(c, x, y, h, facing=1, col=INK, veil=None, sash=None, halo_a=0.0):
    hx, hy = 0.08, -0.64
    if halo_a:
        c.set_line_width(max(2.0, h * 0.012))
        c.arc(x + hx * h * facing, y + hy * h, 0.13 * h, 0, TAU)
        c.set_source_rgba(*hexc(GOLD), halo_a)
        c.stroke()
    c.save()
    c.translate(x, y)
    c.scale(h * facing, h)
    c.move_to(-0.34, 0)
    c.line_to(0.3, 0)
    c.line_to(0.26, -0.14)
    c.line_to(0.12, -0.2)
    c.line_to(0.14, -0.5)
    c.curve_to(0.1, -0.57, 0.04, -0.58, -0.02, -0.57)
    c.curve_to(-0.16, -0.55, -0.24, -0.4, -0.28, -0.2)
    c.close_path()
    fill(c, col)
    if sash:
        c.move_to(0.0, -0.56)
        c.line_to(0.09, -0.56)
        c.line_to(-0.1, -0.02)
        c.line_to(-0.2, -0.02)
        c.close_path()
        fill(c, sash)
    c.arc(hx, hy, 0.085, 0, TAU)
    fill(c, col)
    if veil:
        c.move_to(hx - 0.1, hy + 0.02)
        c.curve_to(hx - 0.1, hy - 0.14, hx + 0.1, hy - 0.14, hx + 0.1, hy)
        c.line_to(hx + 0.07, hy)
        c.line_to(hx - 0.02, hy - 0.04)
        c.line_to(hx - 0.14, hy + 0.36)
        c.line_to(hx - 0.24, hy + 0.34)
        c.close_path()
        fill(c, veil)
    # mãos postas
    c.set_line_width(0.075)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(0.1, -0.48)
    c.line_to(0.24, -0.42)
    c.line_to(0.28, -0.56)
    c.set_source_rgb(*hexc(col))
    c.stroke()
    c.restore()


def wings(c, x, y, h, t, col=CREAM):
    flap = 0.08 * math.sin(t * 3)
    c.save()
    c.translate(x, y)
    c.scale(h, h)
    for s in (-1, 1):
        c.save()
        c.translate(s * 0.08, -0.72)
        c.rotate(-s * flap)
        c.move_to(0, 0)
        c.line_to(s * 0.5, -0.46)
        c.line_to(s * 0.6, -0.3)
        c.line_to(s * 0.46, -0.08)
        c.line_to(s * 0.5, 0.12)
        c.line_to(s * 0.22, 0.34)
        c.close_path()
        fill(c, col)
        c.move_to(s * 0.05, 0.02)
        c.line_to(s * 0.46, -0.3)
        c.line_to(s * 0.4, -0.1)
        c.close_path()
        fill(c, "#e8dcc0")
        c.restore()
    c.restore()


def bust(c, x, y, s, col=INK, sash=None, a=1.0):
    """Cabeça e ombros (pessoas atrás da mesa / na multidão)."""
    c.arc(x, y - s * 1.2, s * 0.34, 0, TAU)
    fill(c, col, a)
    c.move_to(x - s * 0.62, y + s)
    c.line_to(x - s * 0.56, y - s * 0.55)
    c.curve_to(x - s * 0.5, y - s * 0.8, x + s * 0.5, y - s * 0.8, x + s * 0.56, y - s * 0.55)
    c.line_to(x + s * 0.62, y + s)
    fill(c, col, a)
    if sash:
        c.move_to(x + s * 0.08, y - s * 0.72)
        c.line_to(x + s * 0.32, y - s * 0.66)
        c.line_to(x - s * 0.2, y + s)
        c.line_to(x - s * 0.44, y + s)
        c.close_path()
        fill(c, sash, a)


def cross(c, x, y, h, col=INK):
    w = h * 0.085
    c.rectangle(x - w / 2, y - h, w, h)
    c.rectangle(x - h * 0.34, y - h * 0.8, h * 0.68, w * 0.9)
    fill(c, col)


def geo_rays(c, x, y, n, rot, col, a=1.0, width=0.07, length=1600):
    for k in range(n):
        ang = rot + k / n * TAU
        c.move_to(x, y)
        c.line_to(x + math.cos(ang - width) * length, y + math.sin(ang - width) * length)
        c.line_to(x + math.cos(ang + width) * length, y + math.sin(ang + width) * length)
        c.close_path()
        fill(c, col, a)


def disk(c, x, y, r, col, a=1.0):
    c.arc(x, y, r, 0, TAU)
    fill(c, col, a)


# ───────────────────────── cenas ─────────────────────────
def s_intro(c, t, d):
    paint(c, "#4a2f5c")
    blob(c, W * 0.72, H * 0.6, 560, 4, t, 0.02)
    fill(c, "#3a2249")
    geo_rays(c, W * 0.74, H * 0.62, 14, t * 0.05, "#5a3a6c", 0.8)
    sun(c, W * 0.74, H * 0.62, 280)
    ridge(c, H * 0.86, 25, 0.5, 0, "#2c1b38", seed=3)
    a = eout(seg(t, 0.2, 1.2))
    person(c, W * 0.74, H * 0.9, 380 * lerp(0.9, 1.0, a), "open", sash=GOLD, a=a)
    halo(c, W * 0.74, H * 0.9, 380, a)
    for k, (txt, size, col, y) in enumerate(((tr("Do nascimento à ressurreição"), 46, TEAL, 330),
                                             (tr("A História"), 150, "#ffffff", 480),
                                             (tr("de Jesus"), 150, "#ffffff", 630))):
        p = eout(seg(t, 0.2 + k * 0.3, 1.0 + k * 0.3))
        c.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(size)
        c.move_to(140, y + (1 - p) * 40)
        c.set_source_rgba(*hexc(col), p)
        c.show_text(txt)
    ln = eout(seg(t, 1.0, 1.8))
    c.rectangle(144, 680, 260 * ln, 8)
    fill(c, GOLD)


def s_promessa(c, t, d):
    zoom(c, lerp(1.0, 1.05, t / d), W * 0.5, H * 0.6)
    bands(c, ["#1f2a8a", "#2d2f8f", "#4a2f7a", "#7a3a7a"], 0, H * 0.8)
    rnd = random.Random(2)
    for _ in range(70):
        disk(c, rnd.uniform(0, W), rnd.uniform(0, H * 0.5), rnd.uniform(1.5, 3), CREAM, 0.6)
    town(c, H * 0.82, "#1c1435", seed=8, scale=0.8, lit=0.8, t=t)
    c.rectangle(0, H * 0.82, W, H)
    fill(c, "#150f28")
    la = eout(seg(t, 0, 2.2))
    ax, ay = W * 0.36, lerp(-150, H * 0.84, eout(seg(t, 0, 2.4))) + 8 * math.sin(t * 2)
    for k, r in enumerate((420, 300, 190)):
        disk(c, ax, ay - 220, r * la, CREAM, 0.12 + k * 0.05)
    wings(c, ax, ay, 330, t)
    person(c, ax, ay, 330, "reach", col=CREAM, sash=GOLD)
    kneel(c, W * 0.64, H * 0.86, 300, facing=-1, veil=TEAL)


def s_nascimento(c, t, d):
    zoom(c, lerp(1.0, 1.1, t / d), W * 0.5, H * 0.65)
    paint(c, "#1f2a8a")
    blob(c, W * 0.5, H * 0.52, 620, 9, t, 0.02)
    fill(c, "#2a36a8")
    rnd = random.Random(1)
    for _ in range(90):
        disk(c, rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(1.5, 3.5), CREAM, 0.7)
    sx, sy = W * 0.62, H * 0.16
    sa = eout(seg(t, 0.2, 1.4))
    c.move_to(sx - 8, sy)
    c.line_to(W * 0.36, H)
    c.line_to(W * 0.64, H)
    fill(c, "#ffd25a", 0.16 * sa)
    starburst(c, sx, sy, 22, 0, sa, col="#ffd25a")
    c.move_to(0, H * 0.78)
    c.curve_to(W * 0.3, H * 0.66, W * 0.6, H * 0.72, W, H * 0.64)
    c.line_to(W, H)
    c.line_to(0, H)
    fill(c, "#2fae5a")
    c.move_to(0, H * 0.9)
    c.curve_to(W * 0.4, H * 0.82, W * 0.7, H * 0.92, W, H * 0.86)
    c.line_to(W, H)
    c.line_to(0, H)
    fill(c, "#1f8a44")
    bx, by = W * 0.5, H * 0.92
    c.move_to(bx - 340, by - 300)
    c.line_to(bx, by - 470)
    c.line_to(bx + 340, by - 300)
    c.line_to(bx + 310, by - 288)
    c.line_to(bx, by - 440)
    c.line_to(bx - 310, by - 288)
    c.close_path()
    fill(c, "#f28c1e")
    c.rectangle(bx - 310, by - 295, 26, 295)
    c.rectangle(bx + 284, by - 295, 26, 295)
    fill(c, "#c96a12")
    disk(c, bx, by - 110, 180, "#ffd25a", 0.3 + 0.05 * math.sin(t * 2))
    c.move_to(bx - 85, by - 80)
    c.line_to(bx + 85, by - 80)
    c.line_to(bx + 58, by - 18)
    c.line_to(bx - 58, by - 18)
    c.close_path()
    fill(c, "#f28c1e")
    c.save()
    c.translate(bx, by - 94)
    c.scale(1, 0.45)
    c.arc(0, 0, 55, 0, TAU)
    c.restore()
    fill(c, CREAM)
    disk(c, bx + 40, by - 104, 18, CREAM)
    c.set_line_width(3)
    c.arc(bx + 40, by - 104, 28, 0, TAU)
    c.set_source_rgb(*hexc(GOLD))
    c.stroke()
    kneel(c, bx - 190, by, 250, veil=TEAL)
    person(c, bx + 200, by, 300, "stand", facing=-1, sash=GOLD, scarf="#efe6d2")
    c.set_line_width(9)
    c.move_to(bx + 140, by - 330)
    c.line_to(bx + 140, by)
    c.set_source_rgb(*hexc("#6b3a1e"))
    c.stroke()
    for ox in (bx - 380, bx + 380):
        c.save()
        c.translate(ox, by - 30)
        c.scale(1, 0.62)
        c.arc(0, 0, 48, 0, TAU)
        c.restore()
        fill(c, CREAM)
        disk(c, ox + (42 if ox > bx else -42), by - 52, 18, INK)


def s_magos(c, t, d):
    p = t / d
    bands(c, ["#3a1f6b", "#6b2f6b", "#b5485d", "#e76f51", "#f4a261"], 0, H * 0.7)
    starburst(c, W * 0.8, H * 0.16, 20 + 2 * math.sin(t * 3), 0, 1.0, col="#ffd25a")
    c.move_to(W * 0.8, H * 0.16)
    c.line_to(W * 0.7, H)
    c.line_to(W * 0.95, H)
    fill(c, "#ffd25a", 0.12)
    ridge(c, H * 0.62, 50, 0.5, 0, "#8a3f5e", seed=21, xoff=t * 20)
    ridge(c, H * 0.72, 60, 0.4, 1, "#5a2548", seed=22, xoff=t * 45)
    for i in range(3):
        cx = lerp(-200, W * 0.62, p) + i * 230
        camel(c, cx, H * 0.82 + 10 * math.sin(cx / 300), 200, t + i * 0.7, INK, crown=True)
    ridge(c, H * 0.88, 30, 0.6, 2, "#2c1238", seed=23, xoff=t * 45)
    palm(c, W * 0.1 - t * 30, H * 1.02, 520, INK, t)


def s_batismo(c, t, d):
    zoom(c, lerp(1.0, 1.06, t / d), W * 0.5, H * 0.45)
    op = eout(seg(t, 1.4, 3.4))
    bands(c, ["#3e6fa8", "#5b8fc4", "#8ab8dc", "#bcd9e8"], 0, H * 0.64)
    geo_rays(c, W * 0.5, -80, 10, math.pi / 2 - 0.9, "#fff4c8", 0.25 * op, width=0.05, length=1300)
    c.move_to(W * 0.5 - 60, 0)
    c.line_to(W * 0.5 + 60, 0)
    c.line_to(W * 0.5 + 180, H * 0.72)
    c.line_to(W * 0.5 - 180, H * 0.72)
    fill(c, CREAM, 0.4 * op)
    for i, (cx, cy, s) in enumerate(((W * 0.2, 140, 130), (W * 0.36, 90, 110), (W * 0.64, 100, 120),
                                     (W * 0.8, 150, 140))):
        cloud(c, cx + (-1 if cx < W / 2 else 1) * op * 170, cy, s, "#f5f1e8", 0.95)
    ridge(c, H * 0.58, 35, 0.6, 0, "#5d9a6a", seed=31)
    ridge(c, H * 0.64, 25, 0.9, 1, "#3f7a52", seed=32)
    c.rectangle(0, H * 0.66, W, H)
    fill(c, "#3b82b0")
    water(c, H * 0.7, 6, t, "#4a94c4")
    person(c, W * 0.5, H * 0.92, 400, "open", sash=GOLD)
    halo(c, W * 0.5, H * 0.92, 400, op)
    person(c, W * 0.7, H * 0.92, 380, "reach", facing=-1, sash=TEAL, scarf="#efe6d2")
    water(c, H * 0.8, 8, t, "#2f6f9c", 0.95, phase=1)
    water(c, H * 0.88, 10, t, "#265f88", 1.0, phase=2)
    for k in range(16):
        x = W * 0.04 + k * 28
        c.set_line_width(7)
        c.move_to(x, H)
        c.curve_to(x, H * 0.85, x + 10 * math.sin(t + k), H * 0.78, x + 18 * math.sin(t + k), H * 0.7 - (k % 4) * 22)
        c.set_source_rgb(*hexc("#1f5a3a"))
        c.stroke()
    da = eout(seg(t, 2.0, 4.4))
    if da > 0:
        dy = lerp(-60, H * 0.26, da)
        disk(c, W * 0.5, dy, 110, "#ffffff", 0.25 * da)
        dove(c, W * 0.5, dy, 72, t, a=da)


def s_milagres(c, t, d):
    s = 1 - eio(seg(t, 5.2, 7.6))
    storm = ["#1b2230", "#232b3b", "#2c3444", "#394356"]
    calm = ["#6d4a7a", "#b5485d", "#e98c5a", "#f6c177"]
    bands(c, [mix(b, a, s) for a, b in zip(storm, calm)], 0, H * 0.7)
    if s < 0.95:
        sun(c, W * 0.5, H * 0.66, 220 * (1 - s))
    for i in range(6):
        cloud(c, (i * 380 + t * 40) % (W + 400) - 200, 120 + (i % 2) * 70, 190, "#141a26", 0.9 * s)
    fl = 0
    for lt_, lx in ((1.0, 0.25), (2.6, 0.75), (4.0, 0.4)):
        e = seg(t, lt_, lt_ + 0.35)
        if 0 < e < 1:
            fl = max(fl, (1 - e) * s)
            lightning(c, W * lx, 0, H * 0.6, int(lt_ * 10), (1 - e) * s)
    amp = lerp(8, 42, s)
    c.rectangle(0, H * 0.68, W, H)
    fill(c, mix("#b76a58", "#1f2a3a", s))
    bx, by = W * 0.26, H * 0.74 + amp * 0.6 * math.sin(t * 1.6)
    c.save()
    c.translate(bx, by)
    c.rotate(0.12 * s * math.sin(t * 2.2))
    c.move_to(-230, -30)
    c.line_to(230, -40)
    c.line_to(170, 30)
    c.line_to(-180, 30)
    c.close_path()
    fill(c, "#6b3a1e")
    c.rectangle(-6, -330, 12, 300)
    fill(c, INK)
    c.move_to(0, -320)
    c.line_to(150, -80)
    c.line_to(0, -70)
    c.close_path()
    fill(c, CREAM)
    for k in range(4):
        bust(c, -150 + k * 70, -40, 34, INK, [TEAL, GOLD, "#ff5d8f", "#f28c1e"][k])
    c.restore()
    jx = W * 0.64
    person(c, jx, H * 0.8 + 6 * math.sin(t), 420, "bless" if t > 4.4 else "stand", sash=GOLD)
    halo(c, jx, H * 0.8 + 6 * math.sin(t), 420)
    water(c, H * 0.78, amp, t * 1.6, mix("#d08a62", "#27354a", s), phase=1.3)
    water(c, H * 0.88, amp * 1.2, t * 1.9, mix("#a2604e", "#18212f", s), phase=2.1)
    if s > 0.02:
        c.set_line_width(3)
        rnd = random.Random(5)
        for _ in range(200):
            x = rnd.uniform(0, W + 300)
            y = (rnd.uniform(0, H) + t * 1400) % H
            c.move_to(x - y * 0.25, y)
            c.line_to(x - y * 0.25 - 12, y + 40)
        c.set_source_rgba(0.75, 0.85, 0.95, 0.35 * s)
        c.stroke()
    overlay(c, "#dfe6ff", fl * 0.3)


def s_mensagem(c, t, d):
    zoom(c, lerp(1.0, 1.05, t / d), W * 0.5, H * 0.4)
    bands(c, ["#3a2a6a", "#6b2f6b", "#b5485d", "#e76f51", "#f4a261"], 0, H * 0.72)
    geo_rays(c, W * 0.5, H * 0.5, 16, t * 0.05, "#ffd25a", 0.18)
    sun(c, W * 0.5, H * 0.5, 260)
    for k in range(5):
        bx = (W * 0.2 + k * 160 + t * 70) % (W + 200) - 100
        by = 200 + 40 * math.sin(k * 2 + t)
        w = math.sin(t * 8 + k) * 12
        c.set_line_width(5)
        c.move_to(bx - 22, by - w)
        c.line_to(bx, by)
        c.line_to(bx + 22, by - w)
        c.set_source_rgb(*hexc(INK))
        c.stroke()
    c.move_to(-10, H)
    c.curve_to(W * 0.3, H * 0.6, W * 0.42, H * 0.62, W * 0.5, H * 0.62)
    c.curve_to(W * 0.58, H * 0.62, W * 0.7, H * 0.6, W + 10, H)
    fill(c, "#5a2548")
    person(c, W * 0.5, H * 0.63, 290, "open", sash=GOLD)
    halo(c, W * 0.5, H * 0.63, 290)
    cols = [TEAL, GOLD, "#ff5d8f", "#f28c1e", CREAM]
    for row, (yy, sz, col) in enumerate(((H * 0.86, 55, "#3a1530"), (H * 0.94, 72, "#2a0f22"),
                                         (H * 1.03, 92, INK))):
        rnd = random.Random(row + 60)
        x = -40 + row * 25
        while x < W + 60:
            bob = 4 * math.sin(t * 2 + x * 0.05)
            bust(c, x, yy + bob, sz, col, rnd.choice(cols))
            x += sz * rnd.uniform(1.0, 1.35)


def s_ceia(c, t, d):
    zoom(c, lerp(1.0, 1.08, t / d), W * 0.5, H * 0.5)
    cold = eio(seg(t, 3.6, 4.8))
    paint(c, mix("#7a2e4a", "#2a1f4a", cold))
    blob(c, W * 0.5, H * 0.45, 640, 71, t, 0.02)
    fill(c, mix("#9c3d5c", "#3a2d5c", cold))
    for wx in (W * 0.3, W * 0.5, W * 0.7):
        c.move_to(wx - 90, H * 0.5)
        c.line_to(wx - 90, H * 0.24)
        c.arc(wx, H * 0.24, 90, math.pi, TAU)
        c.line_to(wx + 90, H * 0.5)
        c.close_path()
        fill(c, "#1f2a8a")
        disk(c, wx + 30, H * 0.2, 5, CREAM)
    lanterns(c, 40, 90, t, ["#ffd25a", "#f7a531"], seed=5)
    cols = [TEAL, GOLD, "#ff5d8f", "#f28c1e", CREAM]
    for i in range(13):
        x = W * 0.5 + (i - 6) * 128
        y = H * 0.62 + (0 if i == 6 else 12)
        col, sash = INK, cols[i % 5]
        if i == 6:
            sash = GOLD
        if i == 11:
            sash = mix(cols[i % 5], "#6a0f1a", cold)
            x += 25 * cold
        bust(c, x, y, 62, col, sash)
        if i == 6:
            c.set_line_width(4)
            c.arc(x, y - 62 * 1.2, 34, 0, TAU)
            c.set_source_rgb(*hexc(GOLD))
            c.stroke()
    c.rectangle(W * 0.05, H * 0.66, W * 0.9, 34)
    fill(c, "#5a2a1a")
    c.rectangle(W * 0.07, H * 0.66 + 34, W * 0.86, H)
    fill(c, "#43200f")
    split = eout(seg(t, 1.0, 2.2)) * 30
    for sg in (-1, 1):
        c.save()
        c.translate(W * 0.46 + sg * split, H * 0.655)
        c.scale(1, 0.5)
        c.arc(0, 0, 42, math.pi, TAU)
        c.restore()
        fill(c, "#e0a458")
    cx, cy = W * 0.555, H * 0.66
    c.move_to(cx - 30, cy - 70)
    c.line_to(cx + 30, cy - 70)
    c.line_to(cx + 8, cy - 22)
    c.line_to(cx + 8, cy - 6)
    c.line_to(cx + 24, cy)
    c.line_to(cx - 24, cy)
    c.line_to(cx - 8, cy - 6)
    c.line_to(cx - 8, cy - 22)
    c.close_path()
    fill(c, GOLD)
    for vx in (W * 0.2, W * 0.36, W * 0.64, W * 0.8):
        fl = 0.85 + 0.15 * math.sin(t * 13 + vx)
        c.rectangle(vx - 8, H * 0.6, 16, 42)
        fill(c, CREAM)
        disk(c, vx, H * 0.59, 8 * fl, "#ffd25a")


def s_getsemani(c, t, d):
    zoom(c, lerp(1.05, 1.0, t / d), W * 0.5, H * 0.5)
    paint(c, "#141a5a")
    blob(c, W * 0.5, H * 0.42, 620, 81, t, 0.02)
    fill(c, "#1f2a8a")
    rnd = random.Random(3)
    for _ in range(70):
        disk(c, rnd.uniform(0, W), rnd.uniform(0, H * 0.55), rnd.uniform(1.5, 3), CREAM, 0.6)
    disk(c, W * 0.8, H * 0.18, 70, CREAM)
    ridge(c, H * 0.66, 30, 0.6, 0, "#10154a", seed=71)
    for i, (x, s) in enumerate(((W * 0.1, 360), (W * 0.28, 280), (W * 0.64, 300), (W * 0.9, 380))):
        tree(c, x, H * 0.82, s, col="#0c2a3a", col2="#12384a", trunk="#0a1a24")
    c.move_to(W * 0.5, H * 0.88)
    c.curve_to(W * 0.5, H * 0.72, W * 0.57, H * 0.68, W * 0.63, H * 0.74)
    c.line_to(W * 0.68, H * 0.88)
    fill(c, "#0b1030")
    c.move_to(W * 0.43, 0)
    c.line_to(W * 0.49, 0)
    c.line_to(W * 0.56, H * 0.88)
    c.line_to(W * 0.4, H * 0.88)
    fill(c, CREAM, 0.12)
    kneel(c, W * 0.47, H * 0.88, 300, sash=GOLD, halo_a=0.9)
    for k in range(3):
        e = (t * 0.7 + k * 0.33) % 1
        disk(c, W * 0.47 + 30, H * 0.66 + e * 110, 5, RED, 0.9 * (1 - e))
    c.rectangle(0, H * 0.88, W, H)
    fill(c, "#070a24")
    ta = eout(seg(t, 3.4, 7.2))
    for k in range(5):
        tx = lerp(W + 150, W * 0.72, ta) + k * 95
        ty = H * 0.88 - (k % 2) * 8
        fl = 0.85 + 0.15 * math.sin(t * 14 + k)
        disk(c, tx + 0.3 * 230, ty - 1.08 * 230, 70, "#f28c1e", 0.3 * fl)
        person(c, tx, ty, 230, "torch", facing=-1, sash="#6a0f1a" if k == 0 else None)
        disk(c, tx - 0.3 * 230, ty - 1.08 * 230, 12 * fl, "#ffd25a")


def s_paixao(c, t, d):
    split = 3.8
    if t < split + 0.4:
        a = 1 - seg(t, split, split + 0.4)
        paint(c, "#3d0710")
        blob(c, W * 0.5, H * 0.45, 560, 91, t, 0.02)
        fill(c, "#5a0f1c")
        c.save()
        c.translate(W / 2, H * 0.45)
        zz = lerp(0.9, 1.12, t / split)
        c.scale(zz, zz)
        c.rotate(t * 0.12)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_source_rgba(*hexc(INK), a)
        for k in range(3):
            c.save()
            c.scale(1, 0.42)
            c.set_line_width(16)
            c.arc(0, 0, 300 + k * 18, k, k + TAU)
            c.restore()
            c.stroke()
        rnd = random.Random(9)
        c.set_line_width(6)
        for _ in range(60):
            ang = rnd.uniform(0, TAU)
            r = 300 + rnd.uniform(-10, 40)
            x, y = math.cos(ang) * r, math.sin(ang) * r * 0.42
            L = rnd.uniform(25, 55)
            c.move_to(x, y)
            c.line_to(x + math.cos(ang + rnd.uniform(-1, 1)) * L, y + math.sin(ang + rnd.uniform(-1, 1)) * L)
        c.stroke()
        c.restore()
        for k in range(8):
            e = (t * 0.6 + k * 0.125) % 1
            disk(c, W / 2 + (k - 4) * 70, H * 0.62 + e * 300, 6, RED, 0.9 * a * (1 - e))
        if t < split:
            return
    lt = t - split
    b = eout(seg(lt, 0, 0.5))
    bands(c, ["#1c0a0a", "#6a2115", "#c2562a", "#f28c1e"], 0, H * 0.66)
    sun(c, W * 0.8, H * 0.62, 150)
    ridge(c, H * 0.64, 25, 0.6, 0, "#6a2115", seed=91)
    c.move_to(-10, H)
    c.line_to(-10, H * 0.84)
    c.curve_to(W * 0.4, H * 0.8, W * 0.7, H * 0.64, W + 10, H * 0.58)
    c.line_to(W + 10, H)
    fill(c, "#3a120c")
    cx = lerp(W * 0.32, W * 0.44, lt / (d - split))
    step = abs(math.sin(lt * 3)) * 6
    cy = H * 0.82 - (cx - W * 0.3) * 0.08
    c.save()
    c.translate(cx, cy + step)
    c.rotate(0.18)
    person(c, 0, 0, 330, "shoulder", sash=GOLD, ragged=True)
    c.restore()
    tx, ty = cx + 140, cy - 290 + step
    bx, by = cx - 360, cy + 10
    ang = math.atan2(by - ty, bx - tx)
    c.set_line_width(30)
    c.move_to(tx, ty)
    c.line_to(bx, by)
    mx, my = lerp(tx, bx, 0.22), lerp(ty, by, 0.22)
    px, py = -math.sin(ang), math.cos(ang)
    c.move_to(mx - px * 150, my - py * 150)
    c.line_to(mx + px * 130, my + py * 130)
    c.set_source_rgb(*hexc("#6b3a1e"))
    c.stroke()
    for k in range(3):
        person(c, W * 0.1 + k * 110, H * 0.86, 250, "sad", facing=1, scarf=[TEAL, CREAM, "#ff5d8f"][k],
               head=(0.05, 0.04))
    overlay(c, "#000000", 1 - b)


def s_cruz(c, t, d):
    zoom(c, lerp(1.0, 1.12, t / d), W * 0.5, H * 0.45)
    dark = eio(seg(t, 5.0, 8.0))
    light = ["#6a1a1a", "#a33a1a", "#e76f51", "#f4a261"]
    night = ["#040306", "#0c0508", "#150808", "#2a0d0a"]
    bands(c, [mix(a, b, dark) for a, b in zip(light, night)], 0, H * 0.72)
    if dark < 0.98:
        sun(c, W * 0.5, H * 0.7, 300, (mix("#f28c1e", "#2a0d0a", dark), mix("#f7a531", "#2a0d0a", dark),
                                       mix("#ffd25a", "#3a1010", dark)))
    for i in range(7):
        cloud(c, (i * 320 + t * (30 + i * 5)) % (W + 400) - 200, 90 + (i % 3) * 60, 150, "#1a0808", 0.5 + 0.4 * dark)
    fl = 0
    e = seg(t, 6.3, 6.8)
    if 0 < e < 1:
        fl = 1 - e
        lightning(c, W * 0.3, 0, H * 0.55, 77, fl)
        lightning(c, W * 0.72, 0, H * 0.5, 78, fl * 0.8)
    c.move_to(-10, H)
    c.curve_to(W * 0.25, H * 0.76, W * 0.4, H * 0.69, W * 0.5, H * 0.69)
    c.curve_to(W * 0.6, H * 0.69, W * 0.75, H * 0.76, W + 10, H)
    fill(c, INK)
    for x in (W * 0.32, W * 0.68):
        cross(c, x, H * 0.74, 330)
        person(c, x, H * 0.74 - 0.341 * 330, 330 * 0.62, "cross")
    cross(c, W * 0.5, H * 0.71, 470)
    fy = H * 0.71 - 0.297 * 470
    person(c, W * 0.5, fy, 470 * 0.68, "cross", sash=GOLD)
    halo(c, W * 0.5, fy, 470 * 0.68, 1 - 0.6 * dark)
    overlay(c, "#ffe8e0", fl * 0.4)


def _tomb(c, stone_off=0.0, stone_rot=0.0, inner=0.0, rock="#3a3a5a", rock2="#2c2c48"):
    c.move_to(W * 0.2, H)
    c.curve_to(W * 0.22, H * 0.55, W * 0.35, H * 0.35, W * 0.55, H * 0.38)
    c.curve_to(W * 0.75, H * 0.4, W * 0.85, H * 0.6, W * 0.9, H)
    fill(c, rock)
    c.move_to(W * 0.3, H)
    c.curve_to(W * 0.32, H * 0.6, W * 0.42, H * 0.46, W * 0.55, H * 0.48)
    c.curve_to(W * 0.68, H * 0.5, W * 0.78, H * 0.65, W * 0.8, H)
    fill(c, rock2)
    ox, oy, r = W * 0.53, H * 0.78, 150
    c.arc(ox, oy, r, math.pi, TAU)
    c.line_to(ox + r, H * 0.9)
    c.line_to(ox - r, H * 0.9)
    fill(c, "#0a0a14")
    if inner > 0:
        c.save()
        c.arc(ox, oy, r * 0.95, math.pi, TAU)
        c.line_to(ox + r * 0.95, H * 0.9)
        c.line_to(ox - r * 0.95, H * 0.9)
        c.clip()
        sun(c, ox, H * 0.86, 260 * inner, ("#ffd25a", "#ffe28a", "#fff4c8"))
        c.restore()
    c.save()
    c.translate(ox + 30 + stone_off, oy + 20)
    c.rotate(stone_rot)
    disk(c, 0, 0, 175, "#5a5a7a")
    disk(c, 0, 0, 125, "#4a4a68")
    c.set_line_width(8)
    c.move_to(-60, -40)
    c.line_to(20, -90)
    c.set_source_rgb(*hexc("#6a6a8a"))
    c.stroke()
    c.restore()
    c.rectangle(0, H * 0.9, W, H)
    fill(c, "#141428")


def s_silencio(c, t, d):
    zoom(c, lerp(1.0, 1.04, t / d), W * 0.53, H * 0.6)
    paint(c, "#141a3a")
    rnd = random.Random(4)
    for k in range(90):
        disk(c, rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(1.5, 3), CREAM, 0.5 + 0.3 * math.sin(t + k))
    tree(c, W * 0.1, H * 0.92, 380, col="#0c2a3a", col2="#12384a", trunk="#0a1a24")
    _tomb(c)
    for a0, lbl in ((2.9, tr("DIA 1")), (4.7, tr("DIA 2"))):
        e = seg(t, a0, a0 + 2.0)
        if 0 < e < 1:
            al = eout(e / 0.25) * clamp((1 - e) / 0.3)
            text_center(c, lbl, W / 2, H * 0.3, lerp(130, 150, e), face=SANS, col=CREAM, a=al, spacing=12)


def s_ressurreicao(c, t, d):
    dawn = eio(seg(t, 0.5, 5.5))
    burst = eout(seg(t, 5.2, 6.6))
    c.save()
    if 3.4 < t < 5.4:
        c.translate(random.Random(int(t * 30)).uniform(-9, 9), random.Random(int(t * 30) + 1).uniform(-6, 6))
    zoom(c, lerp(1.04, 1.0, eout(seg(t, 0, 5))) + 0.06 * eout(seg(t, 6.5, 12)), W * 0.53, H * 0.6)
    night = ["#141a3a", "#1a2250", "#23306a", "#2c3a7a"]
    morn = ["#4a78c8", "#8ab8dc", "#f4a261", "#ffd25a"]
    bands(c, [mix(a, b, dawn) for a, b in zip(night, morn)], 0, H * 0.7)
    tree(c, W * 0.1, H * 0.92, 380, col=mix("#0c2a3a", "#1f7a45", dawn), col2=mix("#12384a", "#2fa060", dawn),
         trunk=mix("#0a1a24", "#6b3a1e", dawn))
    if burst > 0:
        geo_rays(c, W * 0.53, H * 0.78, 18, t * 0.08, "#fff4c8", 0.35 * burst, width=0.06, length=2200)
    roll = eio(seg(t, 4.0, 6.0))
    _tomb(c, stone_off=roll * 420, stone_rot=roll * 2.4, inner=burst,
          rock=mix("#3a3a5a", "#9c6a5a", dawn), rock2=mix("#2c2c48", "#7a4a4a", dawn))
    fig = eout(seg(t, 6.6, 8.2))
    if fig > 0:
        fy = H * 0.92 - 20 * fig
        disk(c, W * 0.53, fy - 280, 330, "#fff4c8", 0.35 * fig)
        person(c, W * 0.53, fy, 460, "raised", col=CREAM, sash=GOLD, a=fig)
        halo(c, W * 0.53, fy, 460, fig)
        particles(c, t, 100, 131, "#fff4c8", fig, rise=90)
    c.restore()
    e = seg(t, 0, 2.6)
    if e < 1:
        al = eout(e / 0.2) * clamp((1 - e) / 0.3)
        text_center(c, tr("DIA 3"), W / 2, H * 0.3, lerp(140, 170, e), face=SANS, col="#ffd25a", a=al, spacing=14)
    overlay(c, "#ffffff", seg(t, 6.2, 6.4) - seg(t, 6.4, 7.4))


def s_final(c, t, d):
    paint(c, "#2a1a3a")
    geo_rays(c, W / 2, H * 0.86, 20, t * 0.03, "#ffd25a", 0.1)
    sun(c, W / 2, H * 0.86, 280)
    ridge(c, H * 0.9, 10, 0.4, 0, "#1a1024", seed=91)
    ca = eout(seg(t, 0.2, 1.4))
    cross(c, W / 2, H * 0.9, 340 * ca, INK)
    ta = eout(seg(t, 0.8, 2.0)) * (1 - seg(t, 4.0, 4.6))
    title_text(c, tr("ELE VIVE"), W / 2, H * 0.42, 200, spacing=lerp(70, 30, eout(seg(t, 0.8, 3.0))), a=ta,
               shine=seg(t, 2.0, 3.4))
    for a0, a1, lines in render.APPEAL:
        if a0 <= t < a1:
            appeal_lines(c, lines, t - a0, a1 - a0, cy=H * 0.36)
    if t >= 14.9:
        subscribe(c, t - 14.9, d - 14.9)
    overlay(c, "#000000", seg(t, d - 0.8, d))


FNS = [s_intro, s_promessa, s_nascimento, s_magos, s_batismo, s_milagres, s_mensagem, s_ceia, s_getsemani,
       s_paixao, s_cruz, s_silencio, s_ressurreicao, s_final]
SCENES = [(lbl, dur, fn, caps) for (lbl, dur, _, caps), fn in zip(render.SCENES0, FNS)]
FADES = render.FADES
STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)
SCENES0, STARTS0 = SCENES, STARTS
NARRATION_EXTRA = render.NARRATION_EXTRA

EN.update({"Do nascimento à ressurreição": "From birth to resurrection", "A História": "The Story",
           "de Jesus": "of Jesus"})


def verses():
    return render.verses()


if os.environ.get("VIDEO_NARRATION") == "jesus_flat":
    import narracao
    narracao.apply(globals(), "jesus_flat")
