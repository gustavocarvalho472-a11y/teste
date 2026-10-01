"""Tempo de Tela — teste de 35 s (gancho + início do Ato I), estilo ilustração chapada.

    VIDEO_LANG=pt python3 narracao.py tela
    export VIDEO_LANG=pt VIDEO_NARRATION=tela
    TRILHA_OUT=trilha_tela.wav python3 tela_audio.py
    python3 narracao.py tela --mix trilha_tela.wav trilha_tela_narrada.wav
    python3 engine.py wide tela tempo_de_tela_teste.mp4 trilha_tela_narrada.wav
"""
import math
import os
import random

import cairo

from prodigo import CREAM, INK, TEAL, bands, blob, cloud, fill, paint, person, sitting, sun, tree
from render import (EN, GOLD, SANS, TAU, TITLE, H, W, clamp, eback, eio, eout, glow, hexc, lerp, mix, overlay,
                    particles, seg, subscribe, text_center, title_text, town)

TEXTURE = True
VIGNETTE = 0.45
RED = "#e63946"
CARD_COLS = ["#ff5d8f", "#5fe0cf", "#ffd25a", "#f28c1e", "#8a7cff", "#4cc9f0"]


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def heart(c, x, y, s, col, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(0, 0.35)
    c.curve_to(-0.6, -0.05, -0.45, -0.6, 0, -0.25)
    c.curve_to(0.45, -0.6, 0.6, -0.05, 0, 0.35)
    c.restore()
    fill(c, col, a)


def star(c, x, y, s, col, a=1.0):
    c.move_to(x, y - s)
    for k in range(1, 10):
        r = s if k % 2 == 0 else s * 0.45
        ang = -math.pi / 2 + k * math.pi / 5
        c.line_to(x + math.cos(ang) * r, y + math.sin(ang) * r)
    c.close_path()
    fill(c, col, a)


def flame(c, x, y, s, col, a=1.0):
    c.move_to(x, y - s)
    c.curve_to(x + s * 0.9, y - s * 0.1, x + s * 0.6, y + s * 0.8, x, y + s * 0.8)
    c.curve_to(x - s * 0.6, y + s * 0.8, x - s * 0.9, y - s * 0.1, x, y - s)
    fill(c, col, a)
    c.arc(x, y + s * 0.35, s * 0.32, 0, TAU)
    fill(c, "#ffd25a", a)


def empty(c, x, y, s, a=1.0):
    c.set_line_width(s * 0.12)
    c.set_dash([s * 0.25, s * 0.18])
    c.arc(x, y, s * 0.7, 0, TAU)
    c.set_source_rgba(0.55, 0.55, 0.62, a)
    c.stroke()
    c.set_dash([])


ICONS = ["heart", "star", "flame", "empty", "heart", "star", "empty", "flame"]


def icon(c, name, x, y, s, a=1.0):
    if name == "heart":
        heart(c, x, y + s * 0.1, s * 1.6, RED, a)
    elif name == "star":
        star(c, x, y, s * 0.9, "#ffd25a", a)
    elif name == "flame":
        flame(c, x, y, s * 0.8, "#f28c1e", a)
    else:
        empty(c, x, y, s, a)


def feed_card(c, x, y, w, k):
    rnd = random.Random(k)
    h = w * 1.15
    rrect(c, x, y, w, h, w * 0.06)
    fill(c, "#262b52")
    c.arc(x + w * 0.12, y + w * 0.11, w * 0.06, 0, TAU)
    fill(c, rnd.choice(CARD_COLS))
    rrect(c, x + w * 0.22, y + w * 0.08, w * rnd.uniform(0.3, 0.5), w * 0.05, w * 0.025)
    fill(c, "#4a5080")
    rrect(c, x + w * 0.05, y + w * 0.22, w * 0.9, w * 0.62, w * 0.03)
    fill(c, rnd.choice(CARD_COLS), 0.85)
    c.arc(x + w * 0.5 + rnd.uniform(-0.2, 0.2) * w, y + w * 0.5, w * 0.12, 0, TAU)
    fill(c, CREAM, 0.5)
    heart(c, x + w * 0.1, y + w * 0.97, w * 0.09, RED)
    rrect(c, x + w * 0.2, y + w * 0.94, w * 0.25, w * 0.05, w * 0.025)
    fill(c, "#4a5080")
    return h + w * 0.05


def phone(c, cx, cy, h, scroll, banners=(), rot=0.0, spinner=0.0):
    w = h * 0.5
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    rrect(c, -w / 2, -h / 2, w, h, w * 0.14)
    fill(c, "#0a0812")
    sx, sy, sw, sh = -w / 2 + w * 0.05, -h / 2 + w * 0.05, w * 0.9, h - w * 0.1
    rrect(c, sx, sy, sw, sh, w * 0.1)
    path = c.copy_path()
    fill(c, "#141832")
    c.save()
    c.append_path(path)
    c.clip()
    cw = sw * 0.88
    step = cw * 1.2
    k0 = int(scroll // step) - 1
    for k in range(k0, k0 + int(sh / step) + 3):
        feed_card(c, sx + (sw - cw) / 2, sy + k * step - scroll + sw * 0.15, cw, k)
    if spinner > 0:
        rrect(c, sx, sy, sw, sh, 0)
        fill(c, "#141832", spinner)
        c.set_line_width(sw * 0.04)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        a0 = spinner * 40
        c.arc(0, 0, sw * 0.12, a0, a0 + 4.2)
        c.set_source_rgba(*hexc(CREAM), spinner)
        c.stroke()
    for bt, txt_w in banners:
        e = eout(seg(bt, 0, 0.35)) * (1 - eout(seg(bt, 1.6, 2.0)))
        if e > 0:
            by = sy + sw * 0.06 - (1 - e) * sw * 0.4
            rrect(c, sx + sw * 0.05, by, sw * 0.9, sw * 0.24, sw * 0.06)
            fill(c, "#f4f1ea")
            rrect(c, sx + sw * 0.1, by + sw * 0.05, sw * 0.14, sw * 0.14, sw * 0.03)
            fill(c, CARD_COLS[int(txt_w * 10) % len(CARD_COLS)])
            rrect(c, sx + sw * 0.3, by + sw * 0.06, sw * txt_w, sw * 0.04, sw * 0.02)
            fill(c, "#2a2a3a")
            rrect(c, sx + sw * 0.3, by + sw * 0.14, sw * 0.4, sw * 0.035, sw * 0.02)
            fill(c, "#8a8a9a")
    c.restore()
    rrect(c, -w * 0.14, -h / 2 + w * 0.08, w * 0.28, w * 0.06, w * 0.03)
    fill(c, "#0a0812")
    c.restore()


# ───────────────────────── cenas ─────────────────────────
PH = (W * 0.56 + 0.3 * 300, H * 0.74 - 0.5 * 300)   # posição do celular na mão


def _room(c, t, clock="03:12", day=0.0):
    """Quarto. day=0 noite (luz do celular), day=1 manhã (sol entrando pela janela)."""
    bands(c, [mix("#0b0e28", "#e9d6b8", day), mix("#10143a", "#f1e2c6", day), mix("#141a44", "#f6ead3", day)],
          0, H * 0.7)
    wx, wy, ww, wh = W * 0.1, H * 0.16, W * 0.24, H * 0.4
    c.save()
    rrect(c, wx, wy, ww, wh, 8)
    c.clip()
    paint(c, mix("#1a2250", "#8fd3f4", day))
    if day > 0.5:
        sun(c, wx + ww * 0.7, wy + wh * 0.35, 60)
    else:
        c.arc(wx + ww * 0.75, wy + wh * 0.25, 34, 0, TAU)
        fill(c, CREAM, 0.9)
    c.translate(wx, wy + wh * 0.15)
    c.scale(ww / W, wh / H)
    town(c, H * 0.95, mix("#0c1030", "#7a9cc0", day), seed=12, scale=1.6, lit=0.8 * (1 - day), t=t)
    c.restore()
    c.set_line_width(12)
    c.rectangle(wx, wy, ww, wh)
    c.move_to(wx + ww / 2, wy)
    c.line_to(wx + ww / 2, wy + wh)
    c.set_source_rgb(*mix("#0a0c24", "#8a6a4a", day))
    c.stroke()
    if day > 0:
        c.move_to(wx, wy + wh)
        c.line_to(wx + ww, wy + wh)
        c.line_to(wx + ww + W * 0.3, H)
        c.line_to(wx + W * 0.12, H)
        c.close_path()
        fill(c, "#fff4c8", 0.25 * day)
    c.rectangle(0, H * 0.7, W, H)
    fill(c, mix("#0a0c22", "#c9a27a", day))
    rrect(c, W * 0.3, H * 0.66, W * 0.56, H * 0.16, 18)
    fill(c, mix("#2a2a5a", "#5fa8b8", day))
    rrect(c, W * 0.3, H * 0.74, W * 0.56, H * 0.12, 10)
    fill(c, mix("#22224a", "#4a8a9a", day))
    rrect(c, W * 0.74, H * 0.6, W * 0.1, H * 0.08, 20)
    fill(c, mix("#3a3a6a", "#f4f1ea", day))
    c.rectangle(W * 0.88, H * 0.62, W * 0.1, H * 0.3)
    fill(c, mix("#1a1a3a", "#8a5a3a", day))
    rrect(c, W * 0.895, H * 0.56, W * 0.085, H * 0.065, 8)
    fill(c, "#070710")
    text_center(c, clock, W * 0.937, H * 0.607, 40, face=SANS, col=RED)
    if day < 0.5:
        glow(c, W * 0.937, H * 0.59, 90, RED, 0.25)


def s_gancho(c, t, d):
    move = eio(seg(t, 4.6, 6.4))
    z = lerp(7.0, 1.0, move) * lerp(1.0, 1.1, eio(seg(t, 6.4, d)))
    cx, cy = PH
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-lerp(cx, W * 0.55, move), -lerp(cy + 6, H * 0.5, move))
    _room(c, t)
    glow(c, cx, cy, 420, "#6f9cff", 0.32 + 0.05 * math.sin(t * 7))
    sitting(c, W * 0.56, H * 0.74, 300, 1, INK, look_up=0.0, ragged=False, sash="#3a4a8a")
    tt = min(t, 5.6)
    scroll = 60 * tt + 70 * tt * tt
    banners = [(t - 0.8, 0.5), (t - 2.2, 0.38), (t - 3.4, 0.55)]
    phone(c, cx, cy, 110, scroll * 0.2, banners, rot=-0.12 * move, spinner=eout(seg(t, 5.6, 6.2)))
    # marionete: o "controle" é um celular deitado, e os fios descem até a cabeça e as mãos
    e = eout(seg(t, 7.2, 8.6))
    if e > 0:
        sway = 0.05 * math.sin(t * 1.6)
        bx, by = W * 0.58, lerp(-120, H * 0.2, e)
        head = (W * 0.56 + 30, H * 0.74 - 300 * 0.62)
        anchors = [(-150, head), (0, (cx, cy - 40)), (150, (cx + 30, cy + 20))]
        c.set_line_width(2.5)
        for dx, (px, py) in anchors:
            ax = bx + dx * math.cos(sway)
            ay = by + dx * math.sin(sway)
            c.move_to(ax, ay)
            c.line_to(lerp(ax, px, e), lerp(ay, py, e))
        c.set_source_rgba(*hexc(CREAM), 0.8)
        c.stroke()
        c.save()
        c.translate(bx, by)
        c.rotate(sway)
        phone(c, 0, 0, 360, 0, rot=math.pi / 2)
        c.restore()
    overlay(c, "#000000", 1 - eout(seg(t, 0.0, 0.5)))


SPINS = [(1.0, (3.6, 4.1, 4.6), ("heart", "heart", "empty")),
         (6.2, (8.0, 8.4, 8.8), ("heart", "heart", "heart")),
         (10.0, (11.2, 11.5, 11.8), ("empty", "empty", "empty"))]


def _reel(t, r):
    """Posição (em ícones) do rolo r no tempo t."""
    pos = 0.0
    for start, stops, targets in SPINS:
        target = ICONS.index(targets[r]) + 8 * (SPINS.index((start, stops, targets)) + 1) * 3
        if t < start:
            return pos
        u = seg(t, start, stops[r])
        pos = target - (1 - eout(u)) * (22 + r * 4)
    return pos


def s_aposta(c, t, d):
    if t < 12.8:
        _slot(c, t)
    if t > 12.4:
        _infinito(c, t - 12.4, d - 12.4)
        overlay(c, "#000000", 1 - eout(seg(t, 12.4, 13.2)))


def _slot(c, t):
    paint(c, "#2a1245")
    blob(c, W * 0.5, H * 0.5, 640, 31, t, 0.02)
    fill(c, "#3d1a60")
    for k in range(5):
        a = 0.08 + 0.04 * math.sin(t * 3 + k)
        c.move_to(W * (0.1 + k * 0.2), 0)
        c.line_to(W * (0.05 + k * 0.2), H)
        c.line_to(W * (0.15 + k * 0.2), H)
        fill(c, CREAM, a)
    mx, my, mw, mh = W * 0.32, H * 0.14, W * 0.36, H * 0.72
    c.arc(mx + mw / 2, my + 30, mw * 0.45, math.pi, TAU)
    fill(c, GOLD)
    rrect(c, mx, my, mw, mh, 40)
    fill(c, "#c0182a")
    for k in range(18):
        lx = mx + 30 + k * (mw - 60) / 17
        on = (int(t * 8) + k) % 2
        c.arc(lx, my + 26, 9, 0, TAU)
        fill(c, "#ffd25a" if on else "#7a0f1a")
    text_center(c, "FEED", mx + mw / 2, my + 120, 70, face=SANS, col="#ffd25a")
    rx, ry, rw, rh = mx + 50, my + 170, mw - 100, mh * 0.42
    rrect(c, rx - 14, ry - 14, rw + 28, rh + 28, 24)
    fill(c, "#7a0f1a")
    cw = rw / 3
    for r in range(3):
        c.save()
        rrect(c, rx + r * cw + 8, ry, cw - 16, rh, 16)
        path = c.copy_path()
        fill(c, CREAM)
        c.append_path(path)
        c.clip()
        p = _reel(t, r)
        base = math.floor(p)
        for j in range(-2, 3):
            idx = (base + j) % len(ICONS)
            yy = ry + rh / 2 + (j - (p - base)) * rh * 0.55
            icon(c, ICONS[idx], rx + r * cw + cw / 2, yy, cw * 0.22)
        c.restore()
    # alavanca
    pull = max(eout(seg(t, s, s + 0.2)) * (1 - eout(seg(t, s + 0.2, s + 0.7))) for s, _, _ in SPINS)
    lx, ly = mx + mw + 40, my + mh * 0.45
    ex, ey = lx + 20 * pull, ly - 260 + 480 * pull
    c.set_line_width(22)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(lx, ly)
    c.line_to(ex, ey)
    c.set_source_rgb(*hexc("#9a9ab0"))
    c.stroke()
    c.arc(ex, ey, 38, 0, TAU)
    fill(c, RED)
    rrect(c, mx + mw - 6, ly - 50, 60, 100, 12)
    fill(c, "#7a0f1a")
    # resultado
    win = seg(t, 8.8, 10.0)
    if 0 < win < 1:
        rnd = random.Random(3)
        for _ in range(26):
            ang = rnd.uniform(0, TAU)
            dist = eout(win) * rnd.uniform(200, 620)
            heart(c, W / 2 + math.cos(ang) * dist, H * 0.42 + math.sin(ang) * dist - 200 * win, 50, RED, 1 - win)
    miss = seg(t, 11.8, 12.6)
    if 0 < miss < 1:
        overlay(c, "#000000", 0.35 * math.sin(miss * math.pi))
    # você, pequeno, olhando a máquina
    glow(c, W * 0.17, H * 0.72, 260, "#ff5d8f", 0.18)
    sitting(c, W * 0.15, H * 0.94, 260, 1, INK, look_up=1.0, ragged=False, sash="#3a4a8a")


def _infinito(c, t, d):
    paint(c, "#07081a")
    hz = H * 0.1
    off = t * 1.5
    for i in range(40, -1, -1):
        dd = i - (off % 1.0)
        if dd < -0.5:
            continue
        s0 = 1 / (1 + max(dd, 0) * 0.42)
        s1 = 1 / (1 + max(dd + 0.92, 0) * 0.42)
        y0 = hz + (H * 1.05 - hz) * s0
        y1 = hz + (H * 1.05 - hz) * s1
        w0, w1 = W * 0.36 * s0, W * 0.36 * s1
        k = i + int(off)
        rnd = random.Random(k)
        col = rnd.choice(CARD_COLS)
        a = clamp(1.2 - dd / 30)
        c.move_to(W / 2 - w0, y0)
        c.line_to(W / 2 + w0, y0)
        c.line_to(W / 2 + w1, y1)
        c.line_to(W / 2 - w1, y1)
        c.close_path()
        fill(c, "#262b52", a)
        c.move_to(W / 2 - w0 * 0.85, y0 - (y0 - y1) * 0.12)
        c.line_to(W / 2 + w0 * 0.85, y0 - (y0 - y1) * 0.12)
        c.line_to(W / 2 + w1 * 0.85, y1 + (y0 - y1) * 0.3)
        c.line_to(W / 2 - w1 * 0.85, y1 + (y0 - y1) * 0.3)
        c.close_path()
        fill(c, col, 0.8 * a)
    g = cairo.LinearGradient(0, 0, 0, H * 0.45)
    g.add_color_stop_rgba(0, 0.03, 0.03, 0.1, 1)
    g.add_color_stop_rgba(1, 0.03, 0.03, 0.1, 0)
    c.set_source(g)
    c.rectangle(0, 0, W, H * 0.45)
    c.fill()
    person(c, W * 0.5, H * 0.8, 150, "stand", col="#05050f", head=(0.0, -0.02))


def lying(c, x, y, h, col=INK):
    """Pessoa deitada de barriga pra cima, cabeça à esquerda."""
    c.save()
    c.translate(x, y)
    c.scale(h, h)
    rrect(c, -0.05, -0.16, 0.95, 0.16, 0.08)
    fill(c, col)
    c.arc(-0.14, -0.1, 0.09, 0, TAU)
    fill(c, col)
    c.restore()


def _part(t, edges):
    """Índice da parte e tempo local, dadas as bordas [0, a, b, ...]."""
    k = max(i for i, e in enumerate(edges) if t >= e)
    k = min(k, len(edges) - 2)
    return k, t - edges[k], edges[k + 1] - edges[k]


def _cut(c, lt, ld):
    overlay(c, "#000000", 1 - eout(lt / 0.3))
    overlay(c, "#000000", seg(lt, ld - 0.2, ld))


DORES = [0, 8.5, 17, 25.5, 34]


def s_dores(c, t, d):
    k, lt, ld = _part(t, DORES)
    if k == 0:  # palco × bastidores
        paint(c, "#2a1f4a")
        c.save()
        c.rectangle(0, 0, W / 2, H)
        c.clip()
        bands(c, ["#4cc9f0", "#7fdcf5", "#bdeefa"], 0, H * 0.6)
        sun(c, W * 0.36, H * 0.24, 90, ("#ffd25a", "#ffe28a", "#fff4c8"))
        c.rectangle(0, H * 0.6, W / 2, H * 0.12)
        fill(c, "#1f9fd0")
        c.rectangle(0, H * 0.72, W / 2, H)
        fill(c, "#f4d58d")
        person(c, W * 0.25, H * 0.86, 330, "raised", sash="#ff5d8f", col="#2a1a3a")
        for i in range(10):
            e = (lt * 0.6 + i * 0.1) % 1
            heart(c, W * (0.08 + 0.04 * i), H * 0.8 - e * 500, 40, RED, 1 - e)
        rrect(c, W * 0.03, H * 0.06, 300, 70, 35)
        fill(c, "#ffffff", 0.9)
        heart(c, W * 0.03 + 50, H * 0.06 + 38, 34, RED)
        text_center(c, f"{12.4 + lt * 0.3:.1f} mil", W * 0.03 + 175, H * 0.06 + 50, 36, face=SANS, col="#2a2a3a")
        c.restore()
        c.save()
        c.rectangle(W / 2, 0, W / 2, H)
        c.clip()
        paint(c, "#1a1a3a")
        rrect(c, W * 0.6, H * 0.14, W * 0.16, H * 0.3, 8)
        fill(c, "#2a3050")
        c.set_line_width(3)
        rnd = random.Random(2)
        for _ in range(30):
            x = W * 0.6 + rnd.uniform(0, W * 0.16)
            y = H * 0.14 + (rnd.uniform(0, H * 0.3) + lt * 300) % (H * 0.3)
            c.move_to(x, y)
            c.line_to(x - 6, y + 24)
        c.set_source_rgba(0.7, 0.8, 0.95, 0.5)
        c.stroke()
        c.rectangle(W / 2, H * 0.72, W / 2, H)
        fill(c, "#121228")
        for bx, by, r, col in ((W * 0.6, H * 0.8, 70, "#3a2a5a"), (W * 0.66, H * 0.78, 50, "#4a3a2a"),
                               (W * 0.9, H * 0.82, 80, "#2a3a5a")):
            c.save()
            c.translate(bx, by)
            c.scale(1, 0.55)
            c.arc(0, 0, r, 0, TAU)
            c.restore()
            fill(c, col)
        sitting(c, W * 0.78, H * 0.9, 300, -1, INK, look_up=0.0, ragged=False, sash="#3a4a8a")
        glow(c, W * 0.72, H * 0.7, 160, "#6f9cff", 0.3)
        c.restore()
        c.rectangle(W / 2 - 4, 0, 8, H)
        fill(c, "#ffffff")
        for txt, x in (("PALCO", W * 0.25), ("BASTIDORES", W * 0.75)):
            text_center(c, txt, x, H * 0.12 + 160, 44, face=SANS, col="#ffffff", spacing=6)
    elif k == 1:  # ansiedade
        paint(c, mix("#1a1a3a", "#4a0f1f", eio(lt / ld)))
        cx, cy = W / 2, H * 0.5
        person(c, cx, H * 0.86, 360, "sad", head=(0.04, 0.05), sash="#3a4a8a")
        n = int(4 + lt * 3.2)
        rnd = random.Random(7)
        for i in range(n):
            ang = rnd.uniform(0, TAU)
            r = lerp(560, 230, clamp((lt - i * 0.3) / 6)) + rnd.uniform(-40, 40)
            bx, by = cx + math.cos(ang) * r * 1.4, H * 0.42 + math.sin(ang) * r * 0.6
            a = eout(clamp((lt - i * 0.3) / 0.3))
            rrect(c, bx - 120, by - 32, 240, 64, 22)
            fill(c, "#f4f1ea", 0.92 * a)
            rrect(c, bx - 100, by - 18, 36, 36, 9)
            fill(c, CARD_COLS[i % len(CARD_COLS)], a)
            rrect(c, bx - 50, by - 14, 130, 10, 5)
            fill(c, "#2a2a3a", a)
            rrect(c, bx - 50, by + 4, 90, 8, 4)
            fill(c, "#8a8a9a", a)
        c.set_line_width(5)
        c.set_source_rgba(1, 0.35, 0.4, 0.9)
        rate = lerp(1.2, 3.2, lt / ld)
        c.move_to(0, H * 0.95)
        for x in range(0, W + 1, 8):
            ph = (x / W * 6 - lt * rate) % 1
            y = H * 0.95 - (90 if 0.45 < ph < 0.5 else (-30 if 0.5 < ph < 0.53 else 0))
            c.line_to(x, y)
        c.stroke()
    elif k == 2:  # solidão no meio da multidão
        bands(c, ["#2a1f4a", "#4a2f5c", "#6b3a6b"], 0, H * 0.7)
        town(c, H * 0.7, "#1a1030", seed=5, scale=1.2, lit=0.6, t=lt)
        c.rectangle(0, H * 0.7, W, H)
        fill(c, "#140d22")
        rnd = random.Random(11)
        for row, (yy, hh) in enumerate(((H * 0.78, 200), (H * 0.9, 260), (H * 1.02, 330))):
            x = -60 + row * 70
            while x < W + 80:
                if abs(x - W / 2) > 90 or row != 1:
                    fac = 1 if rnd.random() < 0.5 else -1
                    glow(c, x + fac * 0.25 * hh, yy - 0.75 * hh, hh * 0.35, "#6f9cff", 0.35)
                    person(c, x, yy, hh, "give", facing=fac, col="#0d0818", head=(0.05, 0.05))
                    c.save()
                    c.translate(x + fac * 0.5 * hh, yy - 0.55 * hh)
                    rrect(c, -8, -14, 16, 28, 3)
                    fill(c, "#9ec5ff")
                    c.restore()
                x += hh * rnd.uniform(0.55, 0.8)
        glow(c, W / 2, H * 0.6, 260, CREAM, 0.15)
        person(c, W / 2, H * 0.9, 260, "stand", col="#05050f", sash="#3a4a8a", head=(0.0, -0.03))
    else:  # insônia
        _room(c, lt, clock="04:47")
        lying(c, W * 0.38, H * 0.68, 420)
        glow(c, W * 0.38, H * 0.6, 200, "#6f9cff", 0.3 * (1 - seg(lt, 3.5, 4.5)))
        c.save()
        c.translate(W * 0.36 + seg(lt, 3.5, 4.5) * 120, H * 0.6 + seg(lt, 3.5, 4.5) * 40)
        rrect(c, -24, -40, 48, 80, 8)
        fill(c, "#0a0812")
        c.restore()
        for ex in (W * 0.322, W * 0.33):
            c.arc(ex, H * 0.635, 3.5, 0, TAU)
            fill(c, CREAM)
        overlay(c, "#000000", 0.25 * seg(lt, 4.0, 6.0))
    _cut(c, lt, ld)


SEDE = [0, 9, 45]


def well(c, x, y, s, glow_a=0.0, t=0.0):
    if glow_a > 0:
        c.move_to(x - 0.5 * s, y - 0.7 * s)
        c.line_to(x + 0.5 * s, y - 0.7 * s)
        c.line_to(x + 1.6 * s, -50)
        c.line_to(x - 1.6 * s, -50)
        c.close_path()
        fill(c, "#bff4ff", 0.25 * glow_a)
        particles(c, t, 40, 17, "#e8fbff", glow_a, rise=120, area=(x - 300, 0, x + 300, y))
    c.rectangle(x - 0.6 * s, y - 0.7 * s, 1.2 * s, 0.7 * s)
    fill(c, "#b07a4a")
    c.set_line_width(3)
    c.set_source_rgb(*hexc("#8a5a34"))
    for row in range(4):
        yy = y - 0.7 * s + row * 0.175 * s
        c.move_to(x - 0.6 * s, yy)
        c.line_to(x + 0.6 * s, yy)
        for col in range(5):
            xx = x - 0.6 * s + (col + (row % 2) * 0.5) * 0.24 * s
            c.move_to(xx, yy)
            c.line_to(xx, yy + 0.175 * s)
    c.stroke()
    c.save()
    c.translate(x, y - 0.7 * s)
    c.scale(1, 0.25)
    c.arc(0, 0, 0.62 * s, 0, TAU)
    c.restore()
    fill(c, "#2a6a8a" if glow_a <= 0 else mix("#2a6a8a", "#bff4ff", glow_a))
    c.set_line_width(14)
    c.move_to(x - 0.55 * s, y - 0.7 * s)
    c.line_to(x - 0.55 * s, y - 1.5 * s)
    c.line_to(x + 0.55 * s, y - 1.5 * s)
    c.line_to(x + 0.55 * s, y - 0.7 * s)
    c.set_source_rgb(*hexc("#6b3a1e"))
    c.stroke()


def s_sede(c, t, d):
    k, lt, ld = _part(t, SEDE)
    if k == 0:  # o celular é um copo que sempre esvazia
        paint(c, "#141a3a")
        blob(c, W / 2, H * 0.5, 520, 3, lt, 0.02)
        fill(c, "#1a2250")
        cx, cy, ph = W / 2, H * 0.48, 620
        pw = ph * 0.5
        rrect(c, cx - pw / 2, cy - ph / 2, pw, ph, pw * 0.14)
        fill(c, "#0a0812")
        sx, sy, sw, sh = cx - pw / 2 + pw * 0.05, cy - ph / 2 + pw * 0.05, pw * 0.9, ph - pw * 0.1
        c.save()
        rrect(c, sx, sy, sw, sh, pw * 0.1)
        c.clip()
        paint(c, "#141832")
        cyc = (lt * 0.55) % 1
        level = math.sin(cyc * math.pi) ** 0.7
        wy = sy + sh * (1 - 0.85 * level)
        c.move_to(sx, sy + sh)
        for x in range(int(sx), int(sx + sw) + 1, 6):
            c.line_to(x, wy + 8 * math.sin(x / 30 + lt * 6))
        c.line_to(sx + sw, sy + sh)
        c.close_path()
        fill(c, "#4cc9f0", 0.85)
        c.restore()
        for i in range(6):
            e = (lt * 0.8 + i / 6) % 1
            c.arc(cx + (i - 2.5) * 40, cy + ph / 2 + e * 200, 7, 0, TAU)
            fill(c, "#4cc9f0", 0.7 * (1 - e))
        person(c, W * 0.22, H * 0.92, 300, "reach", sash="#3a4a8a", head=(0.04, 0.03))
    else:
        bands(c, ["#f4a261", "#f7c46a", "#fbe3a0"], 0, H * 0.62)
        sun(c, W * 0.5, H * 0.1, 110, ("#fff1b8", "#fff8d8", "#ffffff"))
        c.rectangle(0, H * 0.62, W, H)
        fill(c, "#e3b26a")
        from render import ridge
        ridge(c, H * 0.64, 18, 0.5, 0, "#d39a52", seed=4)
        ridge(c, H * 0.82, 14, 0.4, 1, "#c98a46", seed=5)
        glow_a = eout(seg(lt, 13.8, 16.0)) * (1 - seg(lt, 26.0, 27.0))
        well(c, W * 0.46, H * 0.86, 260, glow_a, lt)
        sitting(c, W * 0.3, H * 0.88, 290, 1, INK, look_up=0.4, sash=GOLD, ragged=False)
        from jesus_flat import halo as jhalo
        c.set_line_width(4)
        c.arc(W * 0.3 + 0.04 * 290, H * 0.88 - 0.66 * 290, 0.13 * 290, 0, TAU)
        c.set_source_rgb(*hexc(GOLD))
        c.stroke()
        walk = eout(seg(lt, 0.0, 5.0))
        wx = lerp(W + 150, W * 0.66, walk)
        ph_ = lt * 4 if walk < 1 else None
        person(c, wx, H * 0.88, 330, "carry", facing=-1, scarf="#ff5d8f", sash="#ff5d8f", phase=ph_)
        c.save()
        c.translate(wx - 0.18 * 330, H * 0.88 - 1.0 * 330)
        c.scale(1, 1.15)
        c.arc(0, 0, 40, 0, TAU)
        c.restore()
        fill(c, "#b5552a")
        # "Ele estava falando de você": o brilho do poço chega ao quarto
        if lt > 26.0:
            e = eout(seg(lt, 26.0, 27.2))
            c.save()
            c.push_group()
            _room(c, lt, clock="04:52", day=0.0)
            sitting(c, W * 0.56, H * 0.74, 300, 1, INK, look_up=eout(seg(lt, 29, 31)), ragged=False,
                    sash="#3a4a8a")
            c.move_to(W * 0.15, 0)
            c.line_to(W * 0.35, 0)
            c.line_to(W * 0.7, H)
            c.line_to(W * 0.42, H)
            c.close_path()
            fill(c, "#bff4ff", 0.22 * eout(seg(lt, 28, 31)))
            c.pop_group_to_source()
            c.paint_with_alpha(e)
            c.restore()
    _cut(c, lt, ld)


def s_preco(c, t, d):
    from jesus_flat import s_cruz
    s_cruz(c, min(t * 10 / d, 10.0), 10.0)
    overlay(c, "#000000", 1 - eout(t / 0.4))


MUDA = [0, 12.5, 25, 37.5, 50]


def s_muda(c, t, d):
    k, lt, ld = _part(t, MUDA)
    if k == 0:  # paz: manhã, celular virado, oração
        _room(c, lt, clock="06:30", day=eout(seg(lt, 0, 1.5)))
        c.save()
        c.translate(W * 0.93, H * 0.555)
        rrect(c, -40, -12, 80, 18, 5)
        fill(c, "#0a0812")
        c.restore()
        from jesus_flat import kneel
        kneel(c, W * 0.42, H * 0.86, 320, sash=GOLD)
        particles(c, lt, 40, 21, "#fff4c8", 0.6, rise=20, area=(W * 0.1, H * 0.3, W * 0.6, H))
    elif k == 1:  # descanso: debaixo da árvore, Bíblia aberta
        bands(c, ["#8fd3f4", "#a9def6", "#c7eaf9"], 0, H * 0.66)
        sun(c, W * 0.8, H * 0.2, 110)
        for i, (x, y, s_) in enumerate(((W * 0.2, 150, 100), (W * 0.55, 110, 80))):
            cloud(c, (x + lt * 15 * (i + 1)) % (W + 300) - 150, y, s_)
        from render import ridge
        ridge(c, H * 0.66, 30, 0.5, 0, "#7cc37a", seed=8)
        c.rectangle(0, H * 0.74, W, H)
        fill(c, "#4fae5f")
        tree(c, W * 0.42, H * 0.86, 520, col="#2f8a4a", col2="#3fa05a")
        sitting(c, W * 0.5, H * 0.88, 300, 1, INK, look_up=0.0, sash=GOLD, ragged=False)
        c.save()
        c.translate(W * 0.5 + 0.22 * 300, H * 0.88 - 0.42 * 300)
        c.rotate(-0.3)
        rrect(c, -46, -8, 92, 16, 3)
        fill(c, CREAM)
        c.restore()
        for i in range(3):
            bx = (W * 0.1 + i * 220 + lt * 60) % (W + 200) - 100
            by = 230 + 30 * math.sin(i + lt)
            w = math.sin(lt * 8 + i) * 12
            c.set_line_width(5)
            c.move_to(bx - 22, by - w)
            c.line_to(bx, by)
            c.line_to(bx + 22, by - w)
            c.set_source_rgb(*hexc(INK))
            c.stroke()
    elif k == 2:  # identidade: os likes vão embora, a faixa dourada fica
        paint(c, "#2a1a3a")
        from jesus_flat import geo_rays
        geo_rays(c, W / 2, H * 0.62, 16, lt * 0.05, "#3a2249", 1.0)
        sun(c, W / 2, H * 0.62, 300 * eout(seg(lt, 0, 2)))
        sash = eout(seg(lt, 3.0, 5.0))
        person(c, W / 2, H * 0.92, 420, "open" if lt > 5 else "stand", sash=mix("#3a4a8a", GOLD, sash))
        rnd = random.Random(4)
        for i in range(12):
            e = seg(lt, 0.5 + i * 0.15, 4.5 + i * 0.15)
            if 0 < e < 1:
                x = W / 2 + rnd.uniform(-500, 500)
                y = H * 0.7 - e * 700
                rrect(c, x - 70, y - 26, 140, 52, 26)
                fill(c, "#ffffff", 0.85 * (1 - e))
                heart(c, x - 38, y + 4, 28, RED, 1 - e)
                text_center(c, f"{rnd.randint(1, 999)}", x + 20, y + 13, 32, face=SANS, col="#2a2a3a",
                            a=1 - e)
    else:  # presença: mesa, celulares no cesto, rostos de verdade
        paint(c, "#7a2e4a")
        blob(c, W * 0.5, H * 0.45, 640, 71, lt, 0.02)
        fill(c, "#9c3d5c")
        glow(c, W / 2, H * 0.5, 700, "#ffd25a", 0.35)
        from prodigo import lanterns
        lanterns(c, 40, 120, lt, ["#ffd25a", "#f7a531", CREAM], seed=5)
        from jesus_flat import bust
        cols = [TEAL, GOLD, "#ff5d8f", "#f28c1e", CREAM]
        for i in range(7):
            x = W * 0.5 + (i - 3) * 190
            bob = 6 * math.sin(lt * 3 + i)
            bust(c, x, H * 0.66 + bob, 80, INK, cols[i % 5] if i != 3 else "#3a4a8a")
        c.rectangle(W * 0.08, H * 0.7, W * 0.84, 36)
        fill(c, "#5a2a1a")
        c.rectangle(W * 0.1, H * 0.7 + 36, W * 0.8, H)
        fill(c, "#43200f")
        c.move_to(W * 0.72, H * 0.7)
        c.line_to(W * 0.84, H * 0.7)
        c.line_to(W * 0.82, H * 0.64)
        c.line_to(W * 0.74, H * 0.64)
        c.close_path()
        fill(c, "#c9803a")
        for i in range(4):
            c.save()
            c.translate(W * 0.75 + i * 26, H * 0.645)
            c.rotate(0.2 * (i - 1.5))
            rrect(c, -10, -34, 20, 36, 4)
            fill(c, "#0a0812")
            c.restore()
        for i in range(6):
            c.save()
            c.translate(W * (0.22 + i * 0.1), H * 0.695)
            c.scale(1, 0.4)
            c.arc(0, 0, 34, math.pi, TAU)
            c.restore()
            fill(c, ["#e0a458", "#7b2d8e", "#c9803a"][i % 3])
    _cut(c, lt, ld)


def s_desafio(c, t, d):
    paint(c, "#2a1a3a")
    blob(c, W * 0.5, H * 0.5, 600, 12, t, 0.02)
    fill(c, "#3a2249")
    if t < 22.8:
        # relógio de 10 minutos + 7 dias
        cx, cy, r = W * 0.5, H * 0.33, 190
        a = eout(seg(t, 0.2, 1.0))
        c.arc(cx, cy, r * a, 0, TAU)
        fill(c, CREAM)
        prog = eio(seg(t, 5.8, 15.0))
        c.move_to(cx, cy)
        c.arc(cx, cy, r * 0.9 * a, -math.pi / 2, -math.pi / 2 + TAU * prog)
        c.close_path()
        fill(c, GOLD)
        for k in range(12):
            ang = k / 12 * TAU
            c.set_line_width(6)
            c.move_to(cx + math.cos(ang) * r * 0.82 * a, cy + math.sin(ang) * r * 0.82 * a)
            c.line_to(cx + math.cos(ang) * r * 0.92 * a, cy + math.sin(ang) * r * 0.92 * a)
            c.set_source_rgb(*hexc("#2a1a3a"))
            c.stroke()
        text_center(c, "10 min", cx, cy + 26, 84, face=SANS, col="#2a1a3a", a=a)
        for k in range(7):
            bx = W * 0.5 + (k - 3) * 150
            by = H * 0.64
            on = seg(t, 6.0 + k * 1.3, 6.4 + k * 1.3)
            rrect(c, bx - 55, by - 55, 110, 110, 18)
            fill(c, mix("#4a2f5c", "#5fe0cf", on))
            text_center(c, f"DIA {k + 1}", bx, by - 18, 22, face=SANS, col="#ffffff")
            if on > 0:
                c.set_line_width(12)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.move_to(bx - 28, by + 10)
                c.line_to(bx - 6, by + 30)
                c.line_to(bx + 30 * eback(on), by - 8)
                c.set_source_rgb(*hexc("#1a1024"))
                c.stroke()
        if 15.6 < t < 22.8:
            e = eout(seg(t, 15.6, 16.4))
            c.save()
            c.translate(W * 0.18, H * 0.4)
            c.scale(e, e)
            for sg in (-1, 1):
                c.move_to(0, -70)
                c.line_to(sg * 130, -86)
                c.line_to(sg * 130, 70)
                c.line_to(0, 86)
                c.close_path()
                fill(c, CREAM)
                for li in range(5):
                    c.rectangle(sg * 22 if sg > 0 else -110, -50 + li * 24, 88, 6)
                    fill(c, "#b0a090")
            c.rectangle(-5, -80, 10, 166)
            fill(c, "#8a2a2a")
            c.restore()
    else:
        e = eout(seg(t, 22.8, 23.8))
        title_text(c, "ACEITO?", W / 2, H * 0.5, 230, spacing=lerp(60, 20, e), a=e * (1 - seg(t, 27.3, 27.8)),
                   shine=seg(t, 24, 25.5), face=SANS)
        if t > 27.8:
            subscribe(c, t - 27.8, d - 27.8)
    overlay(c, "#000000", 1 - eout(t / 0.4))
    overlay(c, "#000000", seg(t, d - 0.8, d))


SCENES = [
    ("", 11.0, s_gancho, [
        (0.6, 5.2, "O aplicativo que você mais usa *não foi feito* pra te fazer feliz."),
        (5.8, 10.9, "Foi feito pra te *manter aqui*.")]),
    ("I · POR QUE A GENTE NÃO CONSEGUE PARAR", 19.5, s_aposta, [
        (0.6, 6.6, "Toda vez que você desliza o dedo, seu cérebro faz uma *aposta*: e se o próximo for melhor?"),
        (6.8, 12.4, "Às vezes vem um *like*. Às vezes, nada. E é isso que te *prende*."),
        (12.8, 19.4, "O feed *não tem fim*. Por isso você nunca se sente *satisfeito*.")]),
    ("", 34.0, s_dores, [
        (0.4, 8.2, "Você compara os seus *bastidores* com o *palco* dos outros. E perde. Todo dia."),
        (8.7, 16.8, "Notícia ruim. Conta atrasada. Mais uma notificação. E o coração *dispara* antes do café."),
        (17.2, 25.2, "Você está cercado de gente… e *ninguém* está realmente ali."),
        (25.7, 33.8, "E quando você finalmente larga o celular… o *silêncio grita*.")]),
    ("II · A SEDE", 45.0, s_sede, [
        (0.4, 8.6, "O problema não é o celular. É a *sede*."),
        (9.2, 16.6, "Há dois mil anos, uma mulher foi buscar água ao meio-dia, *sozinha*, pra não cruzar com ninguém."),
        (17.0, 22.4, "No poço, estava Jesus. E Ele disse:"),
        (22.8, 34.6, "“Qualquer que beber desta água tornará a ter sede; mas aquele que beber da água que eu lhe "
                     "der *nunca terá sede*.”"),
        (35.2, 44.6, "Ele não estava falando de poço. Estava falando de *você*.")]),
    ("III · O PREÇO", 35.0, s_preco, [
        (0.4, 8.4, "Você dá horas pro feed. Ele deu a *vida* por você."),
        (8.8, 21.4, "“Deus prova o seu amor para conosco em que Cristo morreu por nós, sendo nós ainda "
                    "*pecadores*.”"),
        (22.0, 34.6, "Não quando você estava bem. Quando você estava rolando a tela às *três da manhã*.")]),
    ("IV · O QUE MUDA", 50.0, s_muda, [
        (0.4, 12.0, "No lugar da ansiedade: *paz*. “A paz de Deus, que excede todo o entendimento.”"),
        (12.9, 24.6, "No lugar do cansaço: *descanso*. “Vinde a mim… e eu vos aliviarei.”"),
        (25.4, 37.0, "No lugar da comparação: *identidade*. Você é filho. Você é filha de Deus."),
        (37.9, 49.6, "No lugar da solidão: *presença*. “Nunca te deixarei, nem te desampararei.”")]),
    ("", 34.0, s_desafio, [
        (0.4, 5.6, "Então eu te faço um *desafio*."),
        (6.0, 15.4, "Por sete dias, os primeiros *dez minutos* da sua manhã, antes do celular, são para Ele."),
        (15.8, 22.6, "Abra a Bíblia. Ore. Ou só fique em silêncio com Ele."),
        (23.0, 33.6, "Comenta *ACEITO* se você topa. E manda pra alguém que precisa largar o celular hoje.")]),
]
VERSES = {
    "II": ("Qualquer que beber desta água tornará a ter sede; mas aquele que beber da água que eu lhe der nunca "
           "terá sede.", "João 4:13-14"),
    "III": ("Deus prova o seu amor para conosco em que Cristo morreu por nós, sendo nós ainda pecadores.",
            "Romanos 5:8"),
    "IV": ("E a paz de Deus, que excede todo o entendimento, guardará os vossos corações.", "Filipenses 4:7"),
}
FADES = {i: (None, None) for i in range(7)}
STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)
SCENES0, STARTS0 = SCENES, STARTS
NARRATION_EXTRA = {}

EN.update({})


def verses():
    return VERSES


if os.environ.get("VIDEO_NARRATION") == "tela":
    import narracao
    narracao.apply(globals(), "tela")
