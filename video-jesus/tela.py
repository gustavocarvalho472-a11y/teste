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

from prodigo import CREAM, INK, TEAL, bands, blob, fill, paint, person, sitting
from render import (EN, GOLD, SANS, TAU, H, W, clamp, eio, eout, glow, hexc, lerp, overlay, seg, text_center,
                    town)

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


def _room(c, t):
    bands(c, ["#0b0e28", "#10143a", "#141a44"], 0, H * 0.7)
    # janela com a cidade à noite
    wx, wy, ww, wh = W * 0.1, H * 0.16, W * 0.24, H * 0.4
    c.save()
    rrect(c, wx, wy, ww, wh, 8)
    c.clip()
    paint(c, "#1a2250")
    c.arc(wx + ww * 0.75, wy + wh * 0.25, 34, 0, TAU)
    fill(c, CREAM, 0.9)
    c.translate(wx, wy + wh * 0.15)
    c.scale(ww / W, wh / H)
    town(c, H * 0.95, "#0c1030", seed=12, scale=1.6, lit=0.8, t=t)
    c.restore()
    c.set_line_width(12)
    c.rectangle(wx, wy, ww, wh)
    c.move_to(wx + ww / 2, wy)
    c.line_to(wx + ww / 2, wy + wh)
    c.set_source_rgb(*hexc("#0a0c24"))
    c.stroke()
    c.rectangle(0, H * 0.7, W, H)
    fill(c, "#0a0c22")
    # cama
    rrect(c, W * 0.3, H * 0.66, W * 0.56, H * 0.16, 18)
    fill(c, "#2a2a5a")
    rrect(c, W * 0.3, H * 0.74, W * 0.56, H * 0.12, 10)
    fill(c, "#22224a")
    rrect(c, W * 0.74, H * 0.6, W * 0.1, H * 0.08, 20)
    fill(c, "#3a3a6a")
    # criado-mudo + relógio 03:12
    c.rectangle(W * 0.88, H * 0.62, W * 0.1, H * 0.3)
    fill(c, "#1a1a3a")
    rrect(c, W * 0.895, H * 0.56, W * 0.085, H * 0.065, 8)
    fill(c, "#070710")
    text_center(c, "03:12", W * 0.937, H * 0.607, 40, face=SANS, col=RED)
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


def s_fim(c, t, d):
    paint(c, "#2a1a3a")
    blob(c, W * 0.5, H * 0.5, 520, 5, t, 0.02)
    fill(c, "#3a2249")
    p = eout(seg(t, 0.2, 1.0))
    text_center(c, "Em breve · vídeo completo", W / 2, H * 0.4, 44, face=SANS, col=TEAL, a=p)
    text_center(c, "TEMPO DE TELA", W / 2, H * 0.55, 150, face=SANS, col="#ffffff", a=p, spacing=6)
    c.rectangle(W / 2 - 160 * p, H * 0.6, 320 * p, 10)
    fill(c, GOLD)
    overlay(c, "#000000", seg(t, d - 0.6, d))


SCENES = [
    ("", 11.0, s_gancho, [
        (0.6, 5.2, "O aplicativo que você mais usa *não foi feito* pra te fazer feliz."),
        (5.8, 10.9, "Foi feito pra te *manter aqui*.")]),
    ("I · POR QUE A GENTE NÃO CONSEGUE PARAR", 19.5, s_aposta, [
        (0.6, 6.6, "Toda vez que você desliza o dedo, seu cérebro faz uma *aposta*: e se o próximo for melhor?"),
        (6.8, 12.4, "Às vezes vem um *like*. Às vezes, nada. E é isso que te *prende*."),
        (12.8, 19.4, "O feed *não tem fim*. Por isso você nunca se sente *satisfeito*.")]),
    ("", 3.5, s_fim, []),
]
FADES = {0: (None, None), 1: (None, None), 2: ("#000000", None)}
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
    return {}


if os.environ.get("VIDEO_NARRATION") == "tela":
    import narracao
    narracao.apply(globals(), "tela")
