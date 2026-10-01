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
from render import (EN, GOLD, SANS, TAU, TITLE, H, W, clamp, draw_chapter, eback, eio, eout, glow, hexc, lerp,
                    mix, overlay, particles, seg, subscribe, text_center, title_text, town)

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


def phone(c, cx, cy, h, scroll, banners=(), rot=0.0, spinner=0.0, content=None):
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
    if content:
        c.save()
        c.rotate(-rot)
        land = abs(abs(rot) - math.pi / 2) < 0.3
        content(c, sh if land else sw, sw if land else sh)
        c.restore()
    else:
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


def kinetic(c, word, lt, size=190, col="#ffffff", dur=1.2, y=H * 0.46):
    """Palavra-chave grande no centro: entra com um 'soco' e some."""
    if lt < 0 or lt > dur:
        return
    p = eout(lt / 0.16)
    a = clamp((dur - lt) / 0.25)
    rnd = random.Random(int(lt * 30))
    sh = (1 - p) * 10
    c.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    tw = c.text_extents(word).x_advance + 4 * len(word)
    if tw > W * 0.86:   # cabe sempre na tela
        size *= W * 0.86 / tw
    c.save()
    c.translate(W / 2 + rnd.uniform(-sh, sh), y + rnd.uniform(-sh, sh))
    sc = lerp(1.45, 1.0, p)
    c.scale(sc, sc)
    text_center(c, word, 6, 8, size, face=SANS, col="#000000", a=0.45 * a * p, spacing=4)
    text_center(c, word, 0, 0, size, face=SANS, col=col, a=a * p, spacing=4)
    c.restore()


def strings(c, top, pts, a=0.8, sway=0.0, fall=0.0):
    """Fios de marionete do alto até os pontos (cabeça/mãos). fall>0 = fios cortados caindo."""
    if a <= 0:
        return
    c.set_line_width(2.5)
    for k, (px, py) in enumerate(pts):
        ax = px + sway * 40 * (k - 1)
        if fall > 0:
            cut_y = lerp(top, py, 0.35)
            c.move_to(ax, top)
            c.line_to(ax, cut_y - fall * 300)
            c.move_to(px, py)
            c.line_to(px + 6 * math.sin(fall * 6 + k), cut_y + fall * 500)
        else:
            c.move_to(ax, top)
            c.line_to(px, py)
    c.set_source_rgba(*hexc(CREAM), a * (1 - fall))
    c.stroke()


def _fit(c, bw, bh, draw, *args):
    """Desenha uma cena W×H dentro de uma caixa bw×bh centrada na origem (encaixe pela largura)."""
    s = bw / W
    c.save()
    c.translate(-bw / 2, -H * s / 2)
    c.scale(s, s)
    draw(c, *args)
    c.restore()


# ── linha do tempo do Ato I (contínuo) ──
T_ROT, T_DIVE, T_SLOT = 14.0, 15.0, 16.8
T_PASS, T_ROAD = 27.6, 29.2
BEATS = [(36.0, "news", "NOTÍCIA RUIM"), (37.6, "bill", "CONTA ATRASADA"),
         (39.2, "perfect", "A VIDA PERFEITA DELA"), (41.1, "like", "MAIS UM LIKE"),
         (42.6, "like2", "MAIS UM"), (43.7, "like3", "MAIS UM…"), (44.6, "palco", "")]
T_CROWD, T_WIN, T_BED, T_BLACK, T_NOTIF, T_FLASH = 49.6, 54.0, 55.4, 60.0, 62.6, 66.8
SPINS = [(17.6, (19.6, 20.0, 20.4), ("heart", "heart", "empty")),
         (22.8, (24.0, 24.3, 24.6), ("heart", "heart", "heart")),
         (25.8, (26.6, 26.9, 27.2), ("empty", "empty", "empty"))]
CROWD_PHONE = (W * 0.5 + 0.42 * 260, H * 0.9 - 0.6 * 260)
WIN_TARGET = (W * 0.79, H * 0.47)


def _reel(t, r):
    pos = 0.0
    for n, (start, stops, targets) in enumerate(SPINS):
        target = ICONS.index(targets[r]) + 8 * (n + 1) * 3
        if t < start:
            return pos
        u = seg(t, start, stops[r])
        pos = target - (1 - eout(u)) * (22 + r * 4)
    return pos


def _gancho_world(c, t):
    """Quarto + celular na mão (com marionete). Devolve nada; desenha em coordenadas do mundo."""
    cx, cy = PH
    move = eio(seg(t, 4.6, 6.4))
    _room(c, t)
    glow(c, cx, cy, 420, "#6f9cff", 0.32 + 0.05 * math.sin(t * 7))
    sitting(c, W * 0.56, H * 0.74, 300, 1, INK, look_up=0.0, ragged=False, sash="#3a4a8a")
    tt = min(t, 5.6)
    scroll = 60 * tt + 70 * tt * tt
    banners = [(t - 0.8, 0.5), (t - 2.2, 0.38), (t - 3.4, 0.55)]
    rot = lerp(-0.12 * move, -math.pi / 2, eio(seg(t, T_ROT, T_ROT + 1.0)))
    content = (lambda cc, bw, bh: _fit(cc, bw, bh, _slot, t)) if t > T_ROT - 0.2 else None
    phone(c, cx, cy, 110, scroll * 0.2, banners, rot=rot, spinner=eout(seg(t, 5.6, 6.2)) * (t < T_ROT - 0.2),
          content=content)
    e = eout(seg(t, 7.2, 8.6)) * (1 - seg(t, T_ROT - 1.0, T_ROT))
    if e > 0:
        sway = 0.05 * math.sin(t * 1.6)
        bx, by = W * 0.58, lerp(-120, H * 0.2, e)
        head = (W * 0.56 + 30, H * 0.74 - 300 * 0.62)
        strings(c, by, [head, (cx, cy - 40), (cx + 30, cy + 20)], 0.8 * e, sway)
        c.save()
        c.translate(bx, by)
        c.rotate(sway)
        phone(c, 0, 0, 360, 0, rot=math.pi / 2)
        c.restore()


def _gancho(c, t):
    cx, cy = PH
    move = eio(seg(t, 4.6, 6.4))
    z = lerp(7.0, 1.0, move) * lerp(1.0, 1.1, eio(seg(t, 6.4, 11.0)))
    ccx, ccy = lerp(cx, W * 0.55, move), lerp(cy + 6, H * 0.5, move)
    dive = seg(t, T_DIVE, T_SLOT) ** 2.4
    if dive > 0:
        z = lerp(z, W / 104.5, dive)   # no fim, a tela deitada (104,5 px) ocupa toda a largura
        ccx, ccy = lerp(ccx, cx, eout(seg(t, T_DIVE, T_DIVE + 1.2))), lerp(ccy, cy, eout(seg(t, T_DIVE, T_DIVE + 1.2)))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-ccx, -ccy)
    _gancho_world(c, t)
    c.restore()
    overlay(c, "#000000", 1 - eout(seg(t, 0.0, 0.5)))


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
    win = seg(t, SPINS[1][1][2], SPINS[1][1][2] + 1.2)
    if 0 < win < 1:
        rnd = random.Random(3)
        for _ in range(26):
            ang = rnd.uniform(0, TAU)
            dist = eout(win) * rnd.uniform(200, 620)
            heart(c, W / 2 + math.cos(ang) * dist, H * 0.42 + math.sin(ang) * dist - 200 * win, 50, RED, 1 - win)
    glow(c, W * 0.17, H * 0.72, 260, "#ff5d8f", 0.18)
    sitting(c, W * 0.15, H * 0.94, 260, 1, INK, look_up=1.0, ragged=False, sash="#3a4a8a")


SLOT_HOLE = (W * 0.32 + 50 + (W * 0.36 - 100) / 2, H * 0.14 + 170 + H * 0.72 * 0.21)


def _road(c, off, card_fn=None):
    paint(c, "#07081a")
    hz = H * 0.1
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
        col = random.Random(k).choice(CARD_COLS)
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


def _road_off(t):
    tt = t - T_ROAD
    return 1.5 * tt + 0.12 * max(0.0, t - BEATS[0][0]) ** 2


def draw_palco(c, lt, lose=0.0):
    paint(c, "#2a1f4a")
    c.save()
    c.translate(-W * 0.5 * eio(lose), 0)
    c.rectangle(0, 0, W / 2, H)
    c.clip()
    bands(c, ["#4cc9f0", "#7fdcf5", "#bdeefa"], 0, H * 0.6)
    sun(c, W * 0.36, H * 0.24, 90, ("#ffd25a", "#ffe28a", "#fff4c8"))
    c.rectangle(0, H * 0.6, W / 2, H * 0.12)
    fill(c, "#1f9fd0")
    c.rectangle(0, H * 0.72, W / 2, H)
    fill(c, "#f4d58d")
    person(c, W * 0.25, H * 0.86, 330, "raised", sash="#ff5d8f", col="#2a1a3a", scarf="#ff5d8f")
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
    if lose < 1:
        c.rectangle(W / 2 - 4 - W * 0.5 * eio(lose), 0, 8, H)
        fill(c, "#ffffff")
        text_center(c, "PALCO", W * 0.25 - W * 0.5 * eio(lose), H * 0.12 + 160, 44, face=SANS, col="#ffffff",
                    spacing=6)
    text_center(c, "BASTIDORES", W * 0.75, H * 0.12 + 160, 44, face=SANS, col="#ffffff", spacing=6)


def _card(c, kind, lt):
    """Desenho de cada dor da montagem (tela cheia W×H)."""
    if kind == "news":
        paint(c, "#16162a")
        c.rectangle(0, 0, W, H * 0.16)
        fill(c, "#d62828")
        text_center(c, "URGENTE", W * 0.18, H * 0.11, 70, face=SANS, col="#ffffff", spacing=6)
        rrect(c, W * 0.08, H * 0.24, W * 0.84, H * 0.42, 20)
        fill(c, "#3a0f1a")
        c.set_line_width(14)
        c.move_to(W * 0.12, H * 0.32)
        for i in range(1, 12):
            c.line_to(W * (0.12 + i * 0.07), H * (0.32 + i * 0.028 + (0.04 if i % 2 else -0.02)))
        c.set_source_rgb(*hexc("#ff5d5d"))
        c.stroke()
        for i in range(3):
            rrect(c, W * 0.08, H * (0.72 + i * 0.06), W * (0.8 - i * 0.2), H * 0.03, 8)
            fill(c, "#4a4a6a")
    elif kind == "bill":
        paint(c, "#2a2236")
        c.save()
        c.translate(W / 2, H / 2)
        c.rotate(-0.04)
        rrect(c, -W * 0.3, -H * 0.42, W * 0.6, H * 0.84, 14)
        fill(c, "#f1ece2")
        for i in range(7):
            rrect(c, -W * 0.25, -H * 0.3 + i * H * 0.07, W * (0.3 + 0.15 * (i % 2)), H * 0.022, 6)
            fill(c, "#b8b0a2")
        text_center(c, "R$ 1.248,90", W * 0.12, H * 0.28, 70, face=SANS, col="#2a2a3a")
        c.rotate(-0.25)
        c.set_line_width(12)
        rrect(c, -W * 0.2, -H * 0.1, W * 0.4, H * 0.18, 16)
        c.set_source_rgba(0.85, 0.15, 0.2, 0.9)
        c.stroke()
        text_center(c, "ATRASADA", 0, H * 0.035, 96, face=SANS, col="#d62839", spacing=6)
        c.restore()
    elif kind == "perfect":
        bands(c, ["#4cc9f0", "#7fdcf5", "#bdeefa"], 0, H * 0.6)
        sun(c, W * 0.72, H * 0.24, 110, ("#ffd25a", "#ffe28a", "#fff4c8"))
        c.rectangle(0, H * 0.6, W, H * 0.12)
        fill(c, "#1f9fd0")
        c.rectangle(0, H * 0.72, W, H)
        fill(c, "#f4d58d")
        person(c, W * 0.5, H * 0.92, 420, "raised", sash="#ff5d8f", col="#2a1a3a", scarf="#ff5d8f")
        for i in range(16):
            e = (lt * 0.8 + i / 16) % 1
            heart(c, W * (0.1 + 0.05 * i), H * 0.85 - e * 700, 50, RED, 1 - e)
    else:
        n = {"like": 1, "like2": 2, "like3": 3}[kind]
        cols = ["#ff5d8f", "#5fe0cf", "#ffd25a"]
        col = cols[(n - 1 + (int(lt * 12) if n == 3 else 0)) % 3]
        paint(c, col)
        s = 1 + 0.08 * math.sin(lt * 20) + 0.25 * eback(clamp(lt / 0.25))
        heart(c, W / 2, H * 0.48, 520 * s, "#ffffff")
        rnd = random.Random(n)
        for i in range(8 * n):
            e = (lt * (1 + n) + rnd.random()) % 1
            heart(c, rnd.uniform(0, W), H - e * H * 1.2, rnd.uniform(40, 90), "#ffffff", 0.7 * (1 - e))


def _montage(c, t):
    _road(c, _road_off(t))
    for n, (tb, kind, word) in enumerate(BEATS):
        tn = BEATS[n + 1][0] if n + 1 < len(BEATS) else 1e9
        if t < tb or t > tn + 0.3:
            continue
        grow = eout(seg(t, tb, tb + 0.3))
        past = eio(seg(t, tn, tn + 0.3))
        s = lerp(0.12, 1.0, grow) * (1 + 2.0 * past)
        a = 1 - past
        cy = lerp(H * 0.3, H / 2, grow)
        c.save()
        c.translate(W / 2, cy)
        c.scale(s, s)
        c.translate(-W / 2, -H / 2)
        c.push_group()
        if kind == "palco":
            draw_palco(c, t - tb, lose=seg(t, 48.4, 49.2))
        else:
            _card(c, kind, t - tb)
        c.pop_group_to_source()
        c.paint_with_alpha(a)
        c.restore()
        if word and grow > 0.5:
            kinetic(c, word, t - tb - 0.12, size=170, dur=tn - tb, y=H * 0.86)


def draw_crowd(c, t, inner_t):
    bands(c, ["#2a1f4a", "#4a2f5c", "#6b3a6b"], 0, H * 0.7)
    town(c, H * 0.7, "#1a1030", seed=5, scale=1.2, lit=0.6, t=t)
    # prédio com a janela acesa (para onde a câmera vai)
    wx, wy = WIN_TARGET
    c.rectangle(wx - 140, wy - 160, 280, H * 0.7 - wy + 160)
    fill(c, "#1a1030")
    rrect(c, wx - 34, wy - 26, 68, 52, 4)
    fill(c, "#6f9cff")
    c.rectangle(0, H * 0.7, W, H)
    fill(c, "#140d22")
    rnd = random.Random(11)
    for row, (yy, hh) in enumerate(((H * 0.78, 200), (H * 0.9, 260), (H * 1.02, 330))):
        x = -60 + row * 70
        while x < W + 80:
            if abs(x - W / 2) > 120 or row != 1:
                fac = 1 if rnd.random() < 0.5 else -1
                glow(c, x + fac * 0.25 * hh, yy - 0.75 * hh, hh * 0.35, "#6f9cff", 0.35)
                person(c, x, yy, hh, "give", facing=fac, col="#0d0818", head=(0.05, 0.05))
                c.save()
                c.translate(x + fac * 0.5 * hh, yy - 0.55 * hh)
                rrect(c, -8, -14, 16, 28, 3)
                fill(c, "#9ec5ff")
                c.restore()
                c.set_line_width(1.5)
                c.move_to(x + 0.05 * hh * fac, 0)
                c.line_to(x + 0.05 * hh * fac, yy - 0.95 * hh)
                c.set_source_rgba(*hexc(CREAM), 0.18)
                c.stroke()
            x += hh * rnd.uniform(0.55, 0.8)
    # quem segura o celular com o "palco" na tela
    glow(c, CROWD_PHONE[0], CROWD_PHONE[1], 200, "#6f9cff", 0.4)
    person(c, W / 2, H * 0.9, 260, "reach", col="#05050f", sash="#3a4a8a", head=(0.05, 0.05))
    c.save()
    c.translate(*CROWD_PHONE)
    rrect(c, -24, -15, 48, 30, 4)
    fill(c, "#0a0812")
    c.save()
    rrect(c, -22, -13, 44, 26, 3)
    c.clip()
    _fit(c, 44, 26, draw_palco, inner_t, 1.0)
    c.restore()
    c.restore()


def draw_insonia(c, lt, drop_at=2.0):
    _room(c, lt, clock="04:47")
    lying(c, W * 0.38, H * 0.68, 420)
    d = seg(lt, drop_at, drop_at + 0.8)
    glow(c, W * 0.38, H * 0.6, 200, "#6f9cff", 0.3 * (1 - d))
    px, py = W * 0.36 + d * 120, H * 0.6 + d * 40
    strings(c, 0, [(W * 0.33, H * 0.6), (px, py)], 0.35 * (1 - d))
    c.save()
    c.translate(px, py)
    rrect(c, -24, -40, 48, 80, 8)
    fill(c, "#0a0812")
    c.restore()
    for ex in (W * 0.322, W * 0.33):
        c.arc(ex, H * 0.635, 3.5, 0, TAU)
        fill(c, CREAM)


def _notif(c, t):
    lt = t - T_NOTIF
    draw_insonia(c, 6.0)
    overlay(c, "#000000", 0.82)
    px, py = W * 0.36 + 120, H * 0.6 + 40
    on = eout(seg(lt, 0.0, 0.3))
    glow(c, px, py, lerp(60, 520, eout(seg(lt, 0.0, 4.0))), "#ffd98a", 0.55 * on)
    c.save()
    c.translate(px, py)
    rrect(c, -24, -40, 48, 80, 8)
    fill(c, "#0a0812")
    rrect(c, -21, -36, 42, 72, 6)
    fill(c, "#ffe9b0", on)
    c.restore()
    e = eout(seg(lt, 0.5, 1.1))
    if e > 0:
        bw, bh = 1180, 300
        bx, by = W / 2 - bw / 2, lerp(-bh - 20, H * 0.14, e)
        rrect(c, bx, by, bw, bh, 40)
        fill(c, "#f7f3ea", 0.97)
        c.arc(bx + 80, by + 80, 42, 0, TAU)
        fill(c, GOLD)
        c.rectangle(bx + 76, by + 52, 8, 56)
        c.rectangle(bx + 60, by + 66, 40, 8)
        fill(c, "#ffffff")
        c.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(30)
        c.move_to(bx + 140, by + 72)
        c.set_source_rgb(0.15, 0.15, 0.2)
        c.show_text("agora")
        c.set_font_size(44)
        for i, line in enumerate(("“Vinde a mim, todos os que estais cansados", "e sobrecarregados, e eu vos aliviarei.”")):
            c.move_to(bx + 60, by + 160 + i * 58)
            c.set_source_rgb(0.1, 0.1, 0.15)
            c.show_text(line)
        c.set_font_size(32)
        c.move_to(bx + 60, by + 272)
        c.set_source_rgb(*hexc("#b8860b"))
        c.show_text("Mateus 11:28")


def s_ato1(c, t, d):
    if t < T_SLOT:
        _gancho(c, t)
    elif t < T_ROAD:
        z = 1 + 13 * seg(t, T_PASS, T_ROAD) ** 2.2
        hx, hy = SLOT_HOLE
        c.save()
        c.translate(lerp(W / 2, W / 2, 0), H / 2)
        c.scale(z, z)
        c.translate(-lerp(W / 2, hx, eout(seg(t, T_PASS, T_PASS + 0.6))), -lerp(H / 2, hy, eout(seg(t, T_PASS, T_PASS + 0.6))))
        _slot(c, t)
        c.restore()
        ra = seg(t, T_ROAD - 0.6, T_ROAD)
        if ra > 0:
            c.push_group()
            _road(c, _road_off(t))
            c.pop_group_to_source()
            c.paint_with_alpha(ra)
        kinetic(c, "APOSTA", t - 20.0)
        kinetic(c, "NADA", t - 27.25, col="#c9c9d9")
    elif t < T_CROWD:
        if t < BEATS[0][0]:
            _road(c, _road_off(t))
            kinetic(c, "SEM FIM", t - 31.6)
        else:
            _montage(c, t)
    elif t < T_BED:
        pull = eout(seg(t, T_CROWD, T_CROWD + 1.6))
        z0 = W / 44.0
        z = lerp(z0, 1.0, pull)
        cx, cy = CROWD_PHONE
        wz = seg(t, T_WIN, T_BED) ** 2.2
        wx, wy = WIN_TARGET
        c.save()
        c.translate(W / 2, H / 2)
        c.scale(z * (1 + 22 * wz), z * (1 + 22 * wz))
        c.translate(-lerp(lerp(cx, W / 2, pull), wx, eout(seg(t, T_WIN, T_WIN + 0.8))),
                    -lerp(lerp(cy, H / 2, pull), wy, eout(seg(t, T_WIN, T_WIN + 0.8))))
        draw_crowd(c, t, t - BEATS[-1][0])
        c.restore()
        if t > T_BED - 0.4:
            c.push_group()
            draw_insonia(c, 0.0)
            c.pop_group_to_source()
            c.paint_with_alpha(seg(t, T_BED - 0.4, T_BED))
    elif t < T_BLACK:
        draw_insonia(c, t - T_BED)
        overlay(c, "#000000", seg(t, T_BLACK - 0.15, T_BLACK))
    elif t < T_NOTIF:
        paint(c, "#000000")
    else:
        _notif(c, t)
        overlay(c, "#fff4dc", eio(seg(t, T_FLASH, d - 0.1)))
    if T_SLOT <= t < T_SLOT + 12:
        draw_chapter(c, "I · POR QUE A GENTE NÃO CONSEGUE PARAR", t - T_SLOT, 12.0, verses={})


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


_STROKES = None


def brush(c, a=0.07):
    """Pinceladas quentes fixas: muda o 'traço' do Ato II para algo mais pictórico."""
    global _STROKES
    if _STROKES is None:
        rnd = random.Random(77)
        _STROKES = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(60, 220), rnd.uniform(8, 22),
                     rnd.uniform(-0.5, 0.5), rnd.choice(["#ffffff", "#7a3a1a", "#f4a261", "#fff1c4"]))
                    for _ in range(420)]
    for x, y, L, w, ang, col in _STROKES:
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        c.scale(L, w)
        c.arc(0, 0, 0.5, 0, TAU)
        c.restore()
        fill(c, col, a)


def _phone_in_sand(c, t):
    cx, cy, ph = W * 0.52, H * 0.56, 560
    pw = ph * 0.5
    c.save()
    c.translate(cx, cy)
    c.rotate(0.18)
    rrect(c, -pw / 2, -ph / 2, pw, ph, pw * 0.14)
    fill(c, "#0a0812")
    sx, sy, sw, sh = -pw / 2 + pw * 0.05, -ph / 2 + pw * 0.05, pw * 0.9, ph - pw * 0.1
    c.save()
    rrect(c, sx, sy, sw, sh, pw * 0.1)
    c.clip()
    paint(c, "#141832")
    level = math.sin(((t * 0.55) % 1) * math.pi) ** 0.7
    wy = sy + sh * (1 - 0.85 * level)
    c.move_to(sx, sy + sh)
    for x in range(int(sx), int(sx + sw) + 1, 6):
        c.line_to(x, wy + 8 * math.sin(x / 30 + t * 6))
    c.line_to(sx + sw, sy + sh)
    c.close_path()
    fill(c, "#4cc9f0", 0.85)
    c.restore()
    c.restore()
    # areia cobrindo a base + mancha molhada que seca
    c.save()
    c.translate(cx, H * 0.84)
    c.scale(1, 0.3)
    c.arc(0, 0, 420, 0, TAU)
    c.restore()
    fill(c, "#d9a45a")
    c.save()
    c.translate(cx + 40, H * 0.86)
    c.scale(1, 0.25)
    c.arc(0, 0, 160 * (0.6 + 0.4 * math.sin(t * 3)), 0, TAU)
    c.restore()
    fill(c, "#b07a3a", 0.6)
    for i in range(6):
        e = (t * 0.8 + i / 6) % 1
        c.arc(cx + 40 + (i - 2.5) * 30, H * 0.72 + e * 120, 7, 0, TAU)
        fill(c, "#4cc9f0", 0.7 * (1 - e))
    sitting(c, W * 0.2, H * 0.9, 300, 1, INK, look_up=0.5, sash="#3a4a8a", ragged=False)


def _well_scene(c, lt):
    glow_a = eout(seg(lt, 13.8, 16.0)) * (1 - seg(lt, 26.0, 27.0))
    well(c, W * 0.46, H * 0.86, 260, glow_a, lt)
    sitting(c, W * 0.3, H * 0.88, 290, 1, INK, look_up=0.4, sash=GOLD, ragged=False)
    c.set_line_width(4)
    c.arc(W * 0.3 + 0.04 * 290, H * 0.88 - 0.66 * 290, 0.13 * 290, 0, TAU)
    c.set_source_rgb(*hexc(GOLD))
    c.stroke()
    walk = eout(seg(lt, 0.0, 5.0))
    wx = lerp(W + 150, W * 0.66, walk)
    person(c, wx, H * 0.88, 330, "carry", facing=-1, scarf="#ff5d8f", sash="#ff5d8f",
           phase=lt * 4 if walk < 1 else None)
    c.save()
    c.translate(wx - 0.18 * 330, H * 0.88 - 1.0 * 330)
    c.scale(1, 1.15)
    c.arc(0, 0, 40, 0, TAU)
    c.restore()
    fill(c, "#b5552a")


def s_sede(c, t, d):
    from render import ridge
    pan = eio(seg(t, 8.2, 10.6))
    bands(c, ["#f4a261", "#f7c46a", "#fbe3a0"], 0, H * 0.62)
    sun(c, W * 0.5, H * 0.1, 110, ("#fff1b8", "#fff8d8", "#ffffff"))
    c.rectangle(0, H * 0.62, W, H)
    fill(c, "#e3b26a")
    c.save()
    c.translate(-W * 0.5 * pan, 0)
    ridge(c, H * 0.64, 18, 0.5, 0, "#d39a52", seed=4)
    c.restore()
    c.save()
    c.translate(-W * pan, 0)
    ridge(c, H * 0.82, 14, 0.4, 1, "#c98a46", seed=5)
    if pan < 1:
        _phone_in_sand(c, t)
    c.translate(W, 0)
    if pan > 0:
        _well_scene(c, t - 9.0)
    c.restore()
    brush(c, 0.06)
    kinetic(c, "SEDE", t - 2.9, col="#fff4dc")
    lt = t - 9.0
    if lt > 26.0:
        e = eout(seg(lt, 26.0, 27.2))
        c.push_group()
        _room(c, lt, clock="04:52", day=0.0)
        sitting(c, W * 0.56, H * 0.74, 300, 1, INK, look_up=eout(seg(lt, 29, 31)), ragged=False, sash="#3a4a8a")
        c.move_to(W * 0.15, 0)
        c.line_to(W * 0.35, 0)
        c.line_to(W * 0.7, H)
        c.line_to(W * 0.42, H)
        c.close_path()
        fill(c, "#ffd98a", 0.25 * eout(seg(lt, 28, 31)))
        c.pop_group_to_source()
        c.paint_with_alpha(e)
    overlay(c, "#000000", seg(t, d - 0.25, d))


def s_preco(c, t, d):
    from jesus_flat import s_cruz
    s_cruz(c, min(t * 10 / d, 10.0), 10.0)
    kinetic(c, "A VIDA", t - 3.0, col=GOLD)
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
        # os fios da marionete são cortados por um traço de luz dourada
        cut = seg(lt, 1.3, 1.6)
        fall = eout(seg(lt, 1.5, 3.0))
        head = (W * 0.42 + 0.08 * 320, H * 0.86 - 0.64 * 320)
        hands = (W * 0.42 + 0.26 * 320, H * 0.86 - 0.5 * 320)
        strings(c, 0, [head, hands, (hands[0] + 30, hands[1] + 20)], 0.8 * (1 - seg(lt, 2.8, 3.4)), 0, fall)
        if 0 < cut < 1:
            yy = H * 0.22
            c.set_line_width(10)
            c.move_to(W * 0.2, yy)
            c.line_to(W * (0.2 + 0.5 * eout(cut)), yy)
            c.set_source_rgba(*hexc(GOLD), 1 - cut * 0.5)
            c.stroke()
            glow(c, W * (0.2 + 0.5 * eout(cut)), yy, 120, "#ffd98a", 0.8)
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
    for w, at in (("PAZ", 2.4), ("DESCANSO", 15.3), ("IDENTIDADE", 28.0), ("PRESENÇA", 40.3)):
        kinetic(c, w, t - at, col=GOLD, size=170)
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
    kinetic(c, "7 DIAS", t - 7.4, col=GOLD)
    overlay(c, "#000000", 1 - eout(t / 0.4))
    overlay(c, "#000000", seg(t, d - 0.8, d))


SCENES = [
    ("", 68.6, s_ato1, [
        (0.6, 5.2, "O aplicativo que você mais usa *não foi feito* pra te fazer feliz."),
        (5.8, 10.9, "Foi feito pra te *manter aqui*."),
        (11.2, 16.4, "Fica até o fim: tem um *desafio* que pode mudar os seus próximos 7 dias."),
        (16.8, 22.4, "Toda vez que você desliza o dedo, seu cérebro faz uma *aposta*: e se o próximo for melhor?"),
        (22.6, 28.4, "Às vezes vem um *like*. Às vezes, nada. E é isso que te *prende*."),
        (29.6, 35.6, "O feed *não tem fim*. Por isso você nunca se sente *satisfeito*."),
        (44.8, 48.2, "Você compara os seus *bastidores* com o *palco* dos outros."),
        (48.4, 49.8, "E *perde*."),
        (50.2, 53.8, "Cercado de gente… e *ninguém* está ali."),
        (55.6, 58.4, "E quando você finalmente larga o celular…"),
        (58.5, 60.0, "o *silêncio grita*.")]),
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
FADES = {0: (None, None), 1: ("#fff4dc", None), 2: (None, None), 3: (None, None), 4: (None, None)}
STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)
SCENES0, STARTS0 = SCENES, STARTS
NARRATION_EXTRA = {0: [(tb, w.capitalize() + ("" if w.endswith("…") else ".")) for tb, _, w in BEATS if w]}
NARR_GAP = 0.12      # montagem rápida: falas curtas encostadas
CAPTION_SCALE = 0.78  # legendas mais discretas

EN.update({})


def verses():
    return VERSES


if os.environ.get("VIDEO_NARRATION") == "tela":
    import narracao
    narracao.apply(globals(), "tela")
