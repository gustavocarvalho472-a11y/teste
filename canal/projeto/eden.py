"""O Éden não era o jardim — ilustração chapada estilo BibleProject (~7 min).

    bash <skill>/scripts/produzir.sh eden pt eden_pt "0:60"

Cada cena é uma função (c, t, d). Desenhe TUDO em função de t (sem estado entre quadros).
"""
import math
import os
import random

import cairo

from prodigo import CREAM, blob, fill, paint
from render import (EN, GOLD, LANG, SANS, SERIF, TAU, H, W, eio, eout, glow, lerp, mix, overlay,
                    particles, seg, text_center, title_text, tr)

TEXTURE = True
VIGNETTE = 0.35
CAPTION_SCALE = 0.78
NARR_GAP = 0.12
SHORT = False

# paleta BibleProject: papel, tinta marrom, petróleo, ocre, oliva, dourado
PAPER = "#f1e2c2"
PAPER2 = "#e6d1a6"
LINE = "#5a4330"
SEA = "#cfdccb"
TEALD = "#2f6f73"
OCHRE = "#c98a3a"
OLIVE = "#6f8a3c"
NAVY = "#18263a"


def stroke(c, col, w, a=1.0):
    r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    c.set_source_rgba(r, g, b, a)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()


# ───────────────────────── objetos ─────────────────────────
LANDS = [(W * 0.24, H * 0.30, 300, 3), (W * 0.62, H * 0.40, 380, 7), (W * 0.40, H * 0.78, 260, 11),
         (W * 0.88, H * 0.80, 230, 5), (W * 0.06, H * 0.82, 200, 9)]
RIVERS = [[(W * 0.55, H * 0.18), (W * 0.58, H * 0.30), (W * 0.63, H * 0.42), (W * 0.67, H * 0.58)],
          [(W * 0.70, H * 0.17), (W * 0.69, H * 0.30), (W * 0.70, H * 0.44), (W * 0.67, H * 0.58)],
          [(W * 0.18, H * 0.16), (W * 0.22, H * 0.28), (W * 0.30, H * 0.38)]]
# onde o alfinete cai (as "teorias")
PINS = [(W * 0.66, H * 0.50), (W * 0.24, H * 0.36), (W * 0.82, H * 0.70), (W * 0.40, H * 0.66),
        (W * 0.58, H * 0.30), (W * 0.16, H * 0.62), (W * 0.74, H * 0.34)]
PIN_T = [0.6, 2.4, 3.4, 4.2, 4.9, 5.5, 6.0]   # quando cada alfinete pousa (cena 0)


def draw_map(c):
    paint(c, PAPER)
    c.rectangle(0, 0, W, H)
    fill(c, SEA, 0.55)
    c.save()
    c.set_dash([6, 10])
    for k in range(1, 8):
        c.move_to(W * k / 8, 0)
        c.line_to(W * k / 8, H)
    for k in range(1, 5):
        c.move_to(0, H * k / 5)
        c.line_to(W, H * k / 5)
    stroke(c, LINE, 1.5, 0.25)
    c.restore()
    rw = random.Random(21)
    for _ in range(34):
        wx, wy = rw.uniform(0, W), rw.uniform(0, H)
        if any(math.hypot(wx - x, wy - y) < r * 1.15 for x, y, r, _s in LANDS):
            continue
        for j in range(2):
            c.move_to(wx - 22, wy + j * 10)
            c.curve_to(wx - 11, wy - 8 + j * 10, wx, wy + 8 + j * 10, wx + 11, wy + j * 10)
        stroke(c, TEALD, 2, 0.35)
    for x, y, r, s in LANDS:
        c.save()
        c.translate(x, y)
        c.scale(1.07, 1.07)
        c.translate(-x, -y)
        blob(c, x, y, r, s, n=11)
        c.restore()
        stroke(c, TEALD, 1.6, 0.3)
        blob(c, x, y, r, s, n=11)
        fill(c, PAPER2)
        blob(c, x, y, r, s, n=11)
        stroke(c, LINE, 3.2, 0.8)
        rnd = random.Random(s)
        for _ in range(4):
            mx, my = x + rnd.uniform(-0.45, 0.45) * r, y + rnd.uniform(-0.4, 0.4) * r
            c.move_to(mx - 18, my + 10)
            c.line_to(mx, my - 12)
            c.line_to(mx + 18, my + 10)
            stroke(c, LINE, 2.4, 0.55)
    for pts in RIVERS:
        c.move_to(*pts[0])
        for i in range(1, len(pts) - 1):
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            c.curve_to(pts[i][0], pts[i][1], pts[i][0], pts[i][1], mx, my)
        c.line_to(*pts[-1])
        stroke(c, TEALD, 4.5, 0.85)
    # rosa dos ventos
    cx, cy, r = W * 0.9, H * 0.2, 70
    for k in range(8):
        a = k * TAU / 8 - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.55
        c.move_to(cx, cy)
        c.line_to(cx + math.cos(a - 0.18) * rr * 0.3, cy + math.sin(a - 0.18) * rr * 0.3)
        c.line_to(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
        c.close_path()
        fill(c, OCHRE if k % 2 == 0 else LINE, 0.85)
    c.arc(cx, cy, r * 1.15, 0, TAU)
    stroke(c, LINE, 2, 0.6)
    text_center(c, "N", cx - 10, cy - r * 1.3, 30, face=SERIF, col=LINE, a=0.8)
    # bordas queimadas do pergaminho
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.62)
    g.add_color_stop_rgba(0, 0.35, 0.22, 0.1, 0)
    g.add_color_stop_rgba(1, 0.35, 0.22, 0.1, 0.45)
    c.set_source(g)
    c.paint()


def pin(c, x, y, s=1.0, a=1.0, col=GOLD):
    """Alfinete de mapa dourado com a ponta em (x, y)."""
    if a <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(0, 0)
    c.line_to(-14, -46)
    c.line_to(14, -46)
    c.close_path()
    fill(c, "#b7862f", a)
    c.arc(0, -62, 26, 0, TAU)
    fill(c, col, a)
    c.arc(-8, -70, 8, 0, TAU)
    fill(c, "#fff6dc", 0.8 * a)
    c.restore()


def hole(c, x, y, a=1.0, red=0.0):
    """Furo no pergaminho, com borda rasgada."""
    rnd = random.Random(int(x * 7 + y))
    c.move_to(x + 16, y)
    for k in range(1, 12):
        ang = k * TAU / 11
        r = rnd.uniform(9, 17)
        c.line_to(x + math.cos(ang) * r, y + math.sin(ang) * r * 0.7)
    c.close_path()
    fill(c, mix("#2a1c12", "#c0392b", red), a)
    if red > 0:
        c.arc(x, y, 34, 0, TAU)
        stroke(c, "#c0392b", 5, red)


def pin_drop(c, x, y, lt, x0=None, y0=None):
    """Alfinete caindo (ou pulando de (x0, y0)) e quicando ao pousar em lt = 0."""
    if lt < -0.45:
        return
    if lt < 0:
        p = 1 + lt / 0.45
        if x0 is None:
            px, py = x, lerp(-120, y, p * p)
        else:
            px = lerp(x0, x, p)
            py = lerp(y0, y, p) - math.sin(p * math.pi) * 260
        pin(c, px, py, 1.0)
        return
    b = math.exp(-lt * 6) * abs(math.sin(lt * 18)) * 40
    sq = 1 - 0.18 * math.exp(-lt * 10)
    c.save()
    c.translate(x, y)
    c.scale(1 / sq, sq)
    pin(c, 0, -b, 1.0)
    c.restore()


def bible(c, x, y, s, glow_word=0.0, page_col=CREAM, t=0.0):
    """Bíblia aberta vista de cima, centrada em (x, y), largura total ~2*s."""
    c.save()
    c.translate(x, y)
    c.rectangle(-s * 1.04, -s * 0.72, s * 2.08, s * 1.44)
    fill(c, "#6b2f22")
    for side in (-1, 1):
        c.save()
        c.scale(side, 1)
        c.move_to(0, -s * 0.66)
        c.curve_to(s * 0.3, -s * 0.72, s * 0.7, -s * 0.70, s, -s * 0.66)
        c.line_to(s, s * 0.66)
        c.curve_to(s * 0.7, s * 0.62, s * 0.3, s * 0.62, 0, s * 0.68)
        c.close_path()
        fill(c, page_col)
        c.restore()
    c.move_to(0, -s * 0.66)
    c.line_to(0, s * 0.68)
    stroke(c, LINE, 3, 0.5)
    rnd = random.Random(4)
    for side in (-1, 1):
        for k in range(14):
            yy = -s * 0.52 + k * s * 0.078
            xx = s * 0.12
            while xx < s * 0.86:
                wl = min(rnd.uniform(0.04, 0.13) * s, s * 0.88 - xx)
                if not (side > 0 and k == 3 and xx < s * 0.47 < xx + wl + s * 0.025):
                    c.rectangle(xx if side > 0 else -xx - wl, yy, wl, s * 0.022)
                    fill(c, LINE, 0.35)
                xx += wl + s * 0.025
    if glow_word > 0:
        wx, wy = s * 0.47, -s * 0.52 + 3 * s * 0.078 + s * 0.011
        glow(c, wx, wy, s * 0.22, GOLD, 0.9 * glow_word)
        glow(c, wx, wy, s * 0.07, "#fff6dc", 0.9 * glow_word)
        c.rectangle(wx - s * 0.035, wy - s * 0.016, s * 0.07, s * 0.034)
        fill(c, "#e6a92e", glow_word)
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            c.arc(wx, wy, s * (0.05 + 0.12 * ph), 0, TAU)
            stroke(c, GOLD, s * 0.006, glow_word * (1 - ph) * 0.8)
    c.restore()


def leaf_tree(c, x, y, s, a=1.0, sway=0.0):
    """Árvore chapada: copa redonda em camadas."""
    if a <= 0:
        return
    c.push_group()
    c.rectangle(x - 0.05 * s, y - 0.55 * s, 0.1 * s, 0.55 * s)
    fill(c, "#6b4a2e")
    for k, (dx, dy, r, col) in enumerate(((0, -0.8, 0.42, "#3f6b35"), (-0.22, -0.68, 0.28, "#4f7f3f"),
                                          (0.24, -0.66, 0.3, OLIVE), (0.05, -1.0, 0.26, "#86a356"))):
        c.arc(x + (dx + sway * 0.02 * (k - 1)) * s, y + dy * s, r * s, 0, TAU)
        fill(c, col)
    c.pop_group_to_source()
    c.paint_with_alpha(a)


def river(c, pts, w, a=1.0, col=TEALD):
    c.move_to(*pts[0])
    for q in pts[1:]:
        c.line_to(*q)
    stroke(c, col, w, a)


def wavy(x0, y0, x1, y1, amp=14, n=40, ph=0.0):
    pts = []
    for i in range(n + 1):
        u = i / n
        x, y = lerp(x0, x1, u), lerp(y0, y1, u)
        dx, dy = y1 - y0, -(x1 - x0)
        L = math.hypot(dx, dy) or 1
        o = math.sin(u * TAU * 1.5 + ph) * amp
        pts.append((x + dx / L * o, y + dy / L * o))
    return pts


def garden(c, x, y, s, p, t, city=False):
    """Medalhão da linha do tempo: jardim (Gênesis) ou cidade-jardim (Apocalipse)."""
    if p <= 0:
        return
    e = eout(p)
    c.save()
    c.translate(x, y)
    c.scale(e, e)
    c.arc(0, 0, s, 0, TAU)
    fill(c, "#e9dcb8")
    c.save()
    c.arc(0, 0, s - 2, 0, TAU)
    c.clip()
    c.rectangle(-s, s * 0.25, 2 * s, s)
    fill(c, "#b9c98e")
    if city:
        glow(c, 0, -s * 0.1, s * 0.9, GOLD, 0.45)
        c.rectangle(-s * 0.42, -s * 0.5, s * 0.84, s * 0.8)
        fill(c, "#f4c95d")
        c.move_to(-s * 0.42, -s * 0.5)
        c.line_to(-s * 0.2, -s * 0.66)
        c.line_to(s * 0.62, -s * 0.66)
        c.line_to(s * 0.42, -s * 0.5)
        c.close_path()
        fill(c, "#ffe39a")
        c.move_to(s * 0.42, -s * 0.5)
        c.line_to(s * 0.62, -s * 0.66)
        c.line_to(s * 0.62, s * 0.14)
        c.line_to(s * 0.42, s * 0.3)
        c.close_path()
        fill(c, "#d9a441")
    river(c, wavy(-s * 0.05, s * 0.2, s * 0.15, s * 1.05, amp=s * 0.06, ph=t * 2), s * 0.09, 0.95, "#3f8e94")
    leaf_tree(c, -s * 0.5, s * 0.5, s * 0.6, sway=math.sin(t))
    leaf_tree(c, s * 0.52, s * 0.52, s * 0.55, sway=math.sin(t + 1))
    if not city:
        leaf_tree(c, s * 0.02, s * 0.32, s * 0.8, sway=math.sin(t + 2))
    c.restore()
    c.arc(0, 0, s, 0, TAU)
    stroke(c, LINE, 5, 0.8)
    c.restore()


def tomb_garden(c, t):
    """Jardim ao amanhecer com o túmulo vazio."""
    g = cairo.LinearGradient(0, 0, 0, H * 0.8)
    for col, off in (("#1b2440", 0), ("#3a3a5e", 0.35), ("#a8607a", 0.62), ("#f0a46a", 0.85)):
        r, gg, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
        g.add_color_stop_rgb(off, r, gg, b)
    c.set_source(g)
    c.paint()
    glow(c, W * 0.5, H * 0.72, 520, "#ffd08a", 0.45)
    c.move_to(0, H)
    c.curve_to(W * 0.2, H * 0.62, W * 0.42, H * 0.42, W * 0.62, H * 0.46)
    c.curve_to(W * 0.8, H * 0.5, W * 0.92, H * 0.62, W, H * 0.7)
    c.line_to(W, H)
    c.close_path()
    fill(c, "#2a2234")
    ox, oy, r = W * 0.6, H * 0.66, 110
    glow(c, ox, oy, 300, "#fff1c8", 0.5 + 0.1 * math.sin(t * 2))
    c.arc(ox, oy, r, math.pi, TAU)
    c.line_to(ox + r, H * 0.8)
    c.line_to(ox - r, H * 0.8)
    c.close_path()
    fill(c, "#ffe6b0")
    c.arc(ox + r * 2.0, H * 0.72, r * 0.95, 0, TAU)
    fill(c, "#3a3046")
    c.arc(ox + r * 2.0, H * 0.72, r * 0.95, 0, TAU)
    stroke(c, "#1a1422", 4, 0.6)
    c.rectangle(0, H * 0.8, W, H * 0.2)
    fill(c, "#1d1a28")
    rnd = random.Random(2)
    for k in range(26):
        fx = rnd.uniform(0, W)
        fy = H * rnd.uniform(0.79, 0.86)
        h = rnd.uniform(30, 70)
        sw = math.sin(t + k) * 4
        c.move_to(fx, fy)
        c.line_to(fx + sw, fy - h)
        stroke(c, "#3b5a3a", 4)
        c.arc(fx + sw, fy - h, rnd.uniform(7, 12), 0, TAU)
        fill(c, rnd.choice(["#f2c14e", "#f7f3e3", "#e88a6a"]))
    leaf_tree(c, W * 0.13, H * 0.84, 460, sway=math.sin(t * 0.8))
    leaf_tree(c, W * 0.92, H * 0.86, 360, sway=math.sin(t * 0.8 + 1))
    particles(c, t, 26, 5, "#ffe9b0", a=0.6, rise=25)


# ───────────────────────── cenas ─────────────────────────
def s_mapa(c, t, d):
    """0 · Mapa antigo: o alfinete dourado cai e pula de teoria em teoria, furando o pergaminho."""
    z = lerp(1.08, 1.0, eout(seg(t, 0, 3.0)))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    draw_map(c)
    red = seg(t, 6.4, 6.8)
    for k, (x, y) in enumerate(PINS):
        last = k == len(PINS) - 1
        if not last and t >= PIN_T[k + 1] - 0.45:
            hole(c, x, y, red=red)
            continue
        x0, y0 = PINS[k - 1] if k else (None, None)
        if t >= PIN_T[k] - 0.45:
            pin_drop(c, x, y, t - PIN_T[k], x0, y0)
    c.restore()


def s_biblia(c, t, d):
    """1 · Recuo: o mapa furado vai para a mesa, ao lado da Bíblia; zoom até a palavra que brilha."""
    paint(c, "#3a2a20")
    for k in range(9):
        c.rectangle(0, k * H / 9, W, 3)
        fill(c, "#2c1f17", 0.6)
    p = eio(seg(t, 0, 2.0))
    zp = eio(seg(t, 2.6, d - 0.1))
    s0, by = 380, H * 0.5
    bx = lerp(W * 1.4, W * 0.66, eout(seg(t, 0.3, 2.2)))
    wx, wy = bx + s0 * 0.47, by - s0 * 0.52 + 3 * s0 * 0.078
    zz = lerp(1.0, 3.4, zp)
    c.save()
    c.translate(lerp(wx, W / 2, zp), lerp(wy, H * 0.38, zp))
    c.scale(zz, zz)
    c.translate(-wx, -wy)
    c.save()
    s = lerp(1.0, 0.42, p)
    c.translate(lerp(W / 2, W * 0.22, p), lerp(H / 2, H * 0.5, p))
    c.rotate(lerp(0, -0.08, p))
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    draw_map(c)
    for x, y in PINS:
        hole(c, x, y, red=1 - p)
    c.restore()
    c.rectangle(bx - s0 * 1.0, by - s0 * 0.66 + 18, s0 * 2.1, s0 * 1.4)
    fill(c, "#000000", 0.3)
    gw = seg(t, 2.4, 3.2) * (0.85 + 0.15 * math.sin(t * 7))
    bible(c, bx, by, s0, glow_word=gw, t=t)
    c.restore()


def s_linha(c, t, d):
    """2 · A linha do tempo: um fio dourado liga o jardim do início ao jardim do fim."""
    paint(c, PAPER)
    y = H * 0.42
    p = eio(seg(t, 0.6, 3.4))
    x0, x1 = W * 0.2, W * 0.8
    c.move_to(x0, y)
    c.line_to(lerp(x0, x1, p), y)
    stroke(c, "#d9a441", 10)
    glow(c, lerp(x0, x1, p), y, 60, GOLD, 0.6 * (1 - seg(t, 3.2, 3.8)))
    rnd = random.Random(9)
    for k in range(66):
        u = (k + 0.5) / 66
        big = rnd.random() > 0.8
        if u > p or abs(lerp(x0, x1, u) - x0) < 175 or abs(lerp(x0, x1, u) - x1) < 175:
            continue
        c.arc(lerp(x0, x1, u), y, 8 if big else 5, 0, TAU)
        fill(c, LINE, 0.55)
    garden(c, x0, y, 170, seg(t, 0.2, 1.2), t)
    garden(c, x1, y, 170, seg(t, 3.4, 4.4), t, city=True)
    text_center(c, tr("GÊNESIS"), x0, y + 235, 34, face=SANS, col=LINE, a=seg(t, 1.0, 1.6), spacing=6)
    text_center(c, tr("APOCALIPSE"), x1, y + 235, 34, face=SANS, col=LINE, a=seg(t, 4.0, 4.6), spacing=6)
    q = eio(seg(t, 5.0, 7.2))
    if q > 0:
        n = 60
        c.move_to(x0, y - 175)
        for i in range(1, int(n * q) + 1):
            u = i / n
            c.line_to(lerp(x0, x1, u), y - 175 - math.sin(u * math.pi) * 170)
        stroke(c, GOLD, 6, 0.9)
    overlay(c, "#000000", seg(t, d - 0.4, d))


def s_tumulo(c, t, d):
    """3 · O open loop: o túmulo vazio num jardim. Zoom lento."""
    z = lerp(1.0, 1.14, eio(t / d))
    c.save()
    c.translate(W * 0.6, H * 0.66)
    c.scale(z, z)
    c.translate(-W * 0.6, -H * 0.66)
    tomb_garden(c, t)
    c.restore()
    overlay(c, "#000000", 1 - eout(seg(t, 0, 0.6)))
    overlay(c, "#000000", seg(t, d - 0.4, d))


def s_titulo(c, t, d):
    """4 · Cartão de título."""
    paint(c, NAVY)
    e = eout(seg(t, 0.1, 0.7))
    glow(c, W / 2, H * 0.47, 700, "#2f6f73", 0.5 * e)
    c.move_to(W * 0.5 - W * 0.33 * e, H * 0.6)
    c.line_to(W * 0.5 + W * 0.33 * e, H * 0.6)
    stroke(c, GOLD, 4, 0.8)
    a = e * (1 - seg(t, d - 0.5, d))
    text_center(c, tr("O ÉDEN"), W / 2, H * 0.40, 64, face=SANS, col="#e9dcb8", a=a, spacing=18)
    title_text(c, tr("NÃO ERA O JARDIM"), W / 2, H * 0.54, 128, a=a, shine=seg(t, 0.5, 2.0), face=SERIF)


# ───────────────────────── roteiro ─────────────────────────
SCENES = [
    ("", 9.0, s_mapa, [
        (0.4, 5.6, "Por *dois* *mil* *anos*, gente muito inteligente tentou achar o Jardim do Éden no mapa."),
        (5.8, 8.8, "E todos erraram *no* *mesmo* *ponto*.")]),
    ("", 6.0, s_biblia, [
        (0.2, 5.9, "A resposta estava na primeira página da Bíblia. Numa palavra de *duas* *letras*.")]),
    ("", 8.2, s_linha, [
        (0.3, 8.0, "E quando você enxerga essa palavra, a Bíblia inteira muda de forma. Ela começa num *jardim*… e termina num jardim.")]),
    ("", 6.0, s_tumulo, [
        (0.5, 5.8, "E tem um detalhe no *túmulo* de *Jesus* que quase ninguém percebe. Fica até o fim.")]),
    ("", 3.4, s_titulo, []),
]
VERSES = {}
VERSES_EN = {}
FADES = {0: ("#000000", None)}

STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)
SCENES0, STARTS0 = SCENES, STARTS
NARRATION_EXTRA = {}

EN.update({
    "GÊNESIS": "GENESIS", "APOCALIPSE": "REVELATION", "O ÉDEN": "EDEN", "NÃO ERA O JARDIM": "WAS NOT THE GARDEN",
    "Por *dois* *mil* *anos*, gente muito inteligente tentou achar o Jardim do Éden no mapa.":
        "For *two* *thousand* *years*, very smart people tried to find the Garden of Eden on a map.",
    "E todos erraram *no* *mesmo* *ponto*.": "And they all got it wrong *in the same place*.",
    "A resposta estava na primeira página da Bíblia. Numa palavra de *duas* *letras*.":
        "The answer was on the first page of the Bible. In a *two-letter* word.",
    "E quando você enxerga essa palavra, a Bíblia inteira muda de forma. Ela começa num *jardim*… e termina num jardim.":
        "And once you see that word, the whole Bible changes shape. It begins in a *garden*… and ends in a garden.",
    "E tem um detalhe no *túmulo* de *Jesus* que quase ninguém percebe. Fica até o fim.":
        "And there's a detail at *Jesus'* *tomb* almost nobody notices. Stay to the end.",
})


def verses():
    return VERSES_EN if LANG == "en" else VERSES


if os.environ.get("VIDEO_NARRATION") == "eden":
    import narracao
    narracao.apply(globals(), "eden")
