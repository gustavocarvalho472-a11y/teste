"""Amostra (gancho + quem é o Homelander + abertura do Ato I) — timeline visual + cues de som.

Cada evento visual está preso a uma palavra da narração (timing.json). CUES alimenta a trilha/sound design.
"""
import json
import math
import os
import random

import cairo

from fx import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
TM = json.load(open(os.path.join(HERE, "narr", "amostra", "timing.json")))
LN = {l["id"]: l for l in TM["lines"]}


def S(lid):
    return LN[lid]["start"]


def E(lid):
    return LN[lid]["end"]


def wd(lid, word, occ=0):
    """início da palavra `word` (prefixo, sem pontuação) na linha lid"""
    k = 0
    for w, a, b in LN[lid]["words"]:
        ww = "".join(ch for ch in w.lower() if ch.isalnum())
        if ww.startswith(word.lower()):
            if k == occ:
                return a
            k += 1
    raise KeyError((lid, word))


TOTAL = 147.6
CUES = []      # (t, som, ganho, pan)
FLASH = []     # (t, força, decaimento)
CA = []        # (t, px)
GLITCH = []    # (t0, t1, força)
SILENCE = []   # (t0, t1) música zerada
MUSIC = []     # (t0, t1, faixa, ganho) — arranjo da trilha


def cue(t, name, g=1.0, pan=0.0):
    CUES.append((round(t, 3), name, g, pan))


def hit(t, flash=0.0, ca=0, shake=0, impacts=None):
    if flash:
        FLASH.append((t, flash, 9.0))
    if ca:
        CA.append((t, ca))
    if impacts is not None and shake:
        impacts.append((t, shake))


# ═════════════════════════════ A · o meme no quadro (0 → 22.95) ═════════════════════════════
IMP_A = []
T_A1 = -0.12
T_B1 = S("L02") - 0.10
T_GL = wd("L03", "same")
T_SMILE = wd("L04", "half")
T_NET = wd("L05", "internet")
T_ROOM = S("L06")
T_NO = wd("L07", "no")
A_END = 22.95

MEME_A = ("mA", 0, -300, 1000, -1.5)
MEME_B = ("mB", 20, 330, 1000, 1.2)
WALL = [  # (nome, x, y, w, rot)
    ("w_arg", -1320, -640, 640, -4.0),
    ("w_point", 1260, -700, 580, 3.5),
    ("w_room", 1270, 500, 840, -2.0),
    ("w_poster", -1280, 560, 660, 2.5),
    ("w_piers", -2080, -60, 540, 4.0),
    ("w_hero", 2120, -80, 560, -3.0),
    ("w_bench", -2150, 760, 560, -3.5),
    ("w_dub", 2160, 780, 560, 3.0),
]
JUNC_L, JUNC_R = (-590, 10), (610, 20)
NET_TAGS = [  # (texto, x, y, t)
    ("#HOMELANDO", -1640, -1060, T_NET + 0.05),
    ("♥ 2.4M", 1060, -1110, T_NET + 0.25),
    ("“HE IS HOMELANDER”", -1880, 1150, T_NET + 0.45),
    ("♥ 918K", 1150, 940, T_NET + 0.65),
    ("#CR7", -2360, -380, T_NET + 0.85),
    ("“SAME GUY”", 1900, 330, T_NET + 1.0),
]
CAM_A = [
    (0.00, -10, -300, 1.40, 0.0, "lin"),
    (4.85, -40, -292, 1.52, 0.0, "io"),
    (5.45, 20, 330, 1.45, 0.0, "lin"),
    (6.55, 20, 326, 1.50, 0.0, "io"),
    (7.35, 10, 15, 0.86, 0.0, "lin"),
    (8.55, 10, 18, 0.88, 0.0, "io"),
    (15.20, 14, 300, 2.05, 0.0, "io"),
    (17.30, 0, 0, 0.36, -1.0, "lin"),
    (17.95, 0, 0, 0.375, -1.0, "io"),
    (19.05, 1270, 480, 2.24, 0.0, "lin"),
    (22.95, 1268, 476, 2.42, 0.0, "lin"),
]
cue(T_A1, "drop", 1.0)
cue(T_A1 + 0.9, "type", 0.5)
cue(T_B1 - 0.35, "whoosh", 0.6)
cue(T_B1, "drop", 1.0)
cue(T_B1 + 0.6, "type", 0.45)
cue(T_GL + 0.22, "marker", 0.9, -0.2)
cue(T_GL + 0.42, "marker", 0.8, 0.2)
cue(T_GL + 1.25, "pluck", 0.9)
cue(T_SMILE + 0.3, "marker", 0.7)
cue(15.35, "whoosh_big", 1.0)
for _s, _x, _y, _t in NET_TAGS:
    cue(_t, "ping", 0.35, max(-0.8, min(0.8, _x / 2400)))
cue(17.95, "whoosh", 0.8)
cue(T_NO - 0.12, "stamp_big", 1.2)
hit(T_NO, flash=0.35, ca=10, shake=26, impacts=IMP_A)
SILENCE.append((T_NO + 0.05, S("L08") - 0.05))


def eye_A(p):
    return p.pt(-187, 56)


def eye_B(p):
    return p.pt(-15, -154)


def board_A(c, t, fxd):
    cam = cam_at(CAM_A, t)
    c.save()
    apply_cam(c, cam, t, IMP_A)
    board_bg(c)
    # mural (já estava lá; a câmera revela)
    for nm, x, y, w, r in WALL:
        draw_print(c, nm, x, y, w, r, t)
    pa = draw_print(c, *MEME_A, t=t, t_in=T_A1)
    pb = draw_print(c, *MEME_B, t=t, t_in=T_B1)
    # fios do mural (estáticos) — teia
    if pa and pb:
        for nm, x, y, w, r in WALL:
            string(c, Print(nm, x, y, w, r).top(), JUNC_L if x < 0 else JUNC_R, 1, 0.05, 3.0, 0.8)
        for j in (JUNC_L, JUNC_R):
            string(c, j, (j[0] * 0.86, -300 + 250), 1, 0.03, 3.0, 0.8)
            pushpin(c, j[0], j[1], 15)
    if pa:
        label_tag(c, "EXHIBIT A · PRESS CONFERENCE · 23.09.2026", -520, -618, 22, prog=seg(t, T_A1 + 0.8, T_A1 + 2.2),
                  t=t)
    if pb:
        label_tag(c, "EXHIBIT B · THE BOYS · SEASON 5", -500, 646, 22, prog=seg(t, T_B1 + 0.6, T_B1 + 1.7), t=t)
    if pa and pb:
        ea, eb = eye_A(pa), eye_B(pb)
        marker_ellipse(c, ea[0], ea[1], 92, 44, seg(t, T_GL + 0.2, T_GL + 0.75), seed=3, width=8, rot=-1.5)
        marker_ellipse(c, eb[0], eb[1], 108, 40, seg(t, T_GL + 0.4, T_GL + 0.95), seed=5, width=8, rot=1.2)
        string(c, (ea[0] + 96, ea[1] + 8), (eb[0] + 110, eb[1] - 6), seg(t, T_GL + 0.95, T_GL + 1.35), 0.18, 3.6)
        note(c, "SAME LOOK", 250, 40, 44, -6, HOT, 1, seg(t, T_GL + 1.2, T_GL + 1.7))
        # sorriso
        m0, m1 = pb.pt(-120, 52), pb.pt(110, 48)
        marker_line(c, m0, m1, seg(t, T_SMILE + 0.3, T_SMILE + 0.75), 6, HOT, 0.06)
        mx, my = pb.pt(150, 25)
        note(c, "half-smile", mx, my, 30, -8, HOT, 1, seg(t, T_SMILE + 0.7, T_SMILE + 1.3))
    for s, x, y, tt in NET_TAGS:
        if t >= tt:
            u = eback(seg(t, tt, tt + 0.35))
            c.save()
            c.translate(x, y)
            c.scale(u, u)
            label_tag(c, s, 0, 0, 66, col=WHITE if s.startswith("♥") else HOT, prog=1, t=t)
            c.restore()
    stamp(c, "st_no", 1270, 490, 640, -9, t, T_NO)
    c.restore()
    light_pool(c)
    dust(c, t, 30)


# ═════════════════════════════ B · poderes (22.95 → 32.02) ═════════════════════════════
B1, B2, B3, B4, B_END = A_END, wd("L08", "takes") - 0.06, wd("L08", "and") - 0.03, S("L09") - 0.08, 32.02
T_LASER = wd("L08", "lasers")
T_CONTROL = wd("L09", "control")
cue(B1 + 0.1, "whoosh_up", 0.9)
cue(B2, "paper", 0.8)
cue(wd("L08", "planes"), "jet", 0.65)
cue(wd("L08", "planes") + 0.35, "boom", 0.55)
cue(T_LASER - 0.05, "laser", 0.75)
hit(T_LASER, flash=0.25, ca=6)
cue(T_CONTROL, "glitch", 1.0)
GLITCH.append((T_CONTROL - 0.02, T_CONTROL + 0.38, 1.0))
cue(30.0, "type", 0.5)


def shot_fly(c, t, fxd):
    black(c, (0.01, 0.012, 0.016))
    u = seg(t, B1, B2)
    # linhas de velocidade
    rnd = random.Random(9)
    for i in range(46):
        x = rnd.uniform(0, W)
        L = rnd.uniform(120, 420)
        sp = rnd.uniform(1800, 3200)
        y = (rnd.uniform(0, H + L) + t * sp) % (H + L) - L
        c.move_to(x, y)
        c.line_to(x, y + L)
        c.set_source_rgba(0.75, 0.82, 0.9, rnd.uniform(0.04, 0.16))
        c.set_line_width(rnd.uniform(1, 3))
        c.stroke()
    s = surf("p_fly2")
    k = 1.25 * W / s.get_width() * (1 + 0.08 * u)
    c.save()
    c.translate(W / 2, H / 2 + lerp(380, -40, eout(u)))
    c.scale(k, k)
    c.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(seg(t, B1, B1 + 0.1))
    c.restore()
    for i in range(46):
        x = rnd.uniform(0, W)
        L = rnd.uniform(160, 520)
        sp = rnd.uniform(2600, 4200)
        y = (rnd.uniform(0, H + L) + t * sp) % (H + L) - L
        c.move_to(x, y)
        c.line_to(x, y + L)
        c.set_source_rgba(0.85, 0.9, 1.0, rnd.uniform(0.05, 0.22))
        c.set_line_width(rnd.uniform(1, 2.5))
        c.stroke()
    label_tag(c, "POWER 01 // FLIGHT", 120, H - 150, 28, prog=seg(t, B1 + 0.15, B1 + 0.6), t=t)


def newspaper(c, x, y, w, rot, t, burn=None):
    h = w * 1.18
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(rot))
    soft_shadow(c, -w / 2, -h / 2, w, h, 4, spread=40, a=0.65)
    p = cairo.SurfacePattern(surf("paper"))
    p.set_extend(cairo.EXTEND_REPEAT)
    c.rectangle(-w / 2, -h / 2, w, h)
    c.set_source(p)
    c.fill()
    ink = (0.09, 0.08, 0.075)
    text(c, "THE VOUGHT DAILY", 0, -h / 2 + w * 0.11, w * 0.085, SERIF, ink, 1)
    c.rectangle(-w * 0.44, -h / 2 + w * 0.135, w * 0.88, 3)
    rgb(c, ink)
    c.fill()
    text(c, "FLIGHT 37", 0, -h / 2 + w * 0.29, w * 0.15, STAMP, ink, 1)
    text(c, "GOES DOWN", 0, -h / 2 + w * 0.43, w * 0.15, STAMP, ink, 1)
    text(c, "Homelander “arrived too late,” says Vought.", 0, -h / 2 + w * 0.52, w * 0.034, TYPE, ink, 1)
    c.rectangle(-w * 0.44, -h / 2 + w * 0.57, w * 0.88, w * 0.36)
    c.set_source_rgb(0.2, 0.2, 0.21)
    c.fill()
    # avião (silhueta) na foto
    c.save()
    c.translate(w * 0.05, -h / 2 + w * 0.73)
    c.rotate(-0.35)
    sc = w * 0.0042
    c.scale(sc, sc)
    c.move_to(-60, 0)
    c.line_to(60, -4)
    c.line_to(70, 0)
    c.line_to(60, 4)
    c.close_path()
    c.move_to(-5, -2)
    c.line_to(-30, -45)
    c.line_to(-18, -45)
    c.line_to(20, -2)
    c.close_path()
    c.move_to(-5, 2)
    c.line_to(-30, 45)
    c.line_to(-18, 45)
    c.line_to(20, 2)
    c.close_path()
    c.move_to(-55, 0)
    c.line_to(-68, -20)
    c.line_to(-60, -20)
    c.line_to(-45, 0)
    c.close_path()
    c.set_source_rgba(0.75, 0.75, 0.75, 0.9)
    c.fill()
    c.restore()
    rnd = random.Random(4)
    for col in range(2):
        for i in range(9):
            yy = -h / 2 + w * 0.97 + i * w * 0.028
            if yy > h / 2 - w * 0.03:
                break
            ww = w * 0.42 * rnd.uniform(0.75, 1.0)
            c.rectangle(-w * 0.44 + col * w * 0.46, yy, ww, w * 0.011)
            c.set_source_rgba(0.1, 0.1, 0.1, 0.55)
            c.fill()
    if burn is not None:
        burn(c, w, h)
    c.restore()
    return w, h


def shot_planes(c, t, fxd):
    black(c, (0.03, 0.035, 0.04))
    light_pool(c, a=0.10)
    u = seg(t, B2, B3)
    c.save()
    z = lerp(1.0, 1.25, eout(u))
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    newspaper(c, W / 2 + 40, H / 2 + 120, 860, -3 + 2 * u, t)
    # marcador em "arrived too late"
    marker_ellipse(c, W / 2 + 40, H / 2 + 120 - 860 * 1.18 / 2 + 860 * 0.505, 330, 36, seg(t, B2 + 0.6, B2 + 1.05), 7,
                   7, rot=-3)
    c.restore()


def shot_laser(c, t, fxd):
    u = seg(t, B3, B4)
    k, cx, cy = photo_full(c, "p_laser", t, B3, B4, 1.0, 1.32, 0.62, 0.40, 0.74, 0.36)
    # olhos do Homelander na foto ~ (1085, 300) px da imagem
    ex, ey = W / 2 + (1085 - cx) * k, H / 2 + (300 - cy) * k
    f = pulse(t, T_LASER - 0.1, T_LASER + 1.1)
    if f > 0:
        glow(c, ex, ey, 180 * k, (1, 0.25, 0.15), 0.55 * f)
        glow_line(c, (ex, ey), (ex - 900 * k, ey + 40 * k), 9 * k, alpha=f)
    c.set_source_rgba(0.6, 0.05, 0.03, 0.18 * f)
    c.paint()


def shot_control(c, t, fxd):
    photo_full(c, "p_control", t, B4, B_END, 1.02, 1.22, 0.62, 0.48, 0.70, 0.44)
    c.set_source_rgba(0, 0, 0, 0.18)
    c.paint()
    label_tag(c, "TRIGGER  //  SOMEONE ELSE DECIDES", 120, H - 150, 28, prog=seg(t, 30.0, 31.3), t=t)


# ═════════════════════════════ C · troféus (32.02 → 36.55) ═════════════════════════════
C0, C_END = B_END, S("L11") - 0.12
T_20 = wd("L10", "20")
TICK = "5× CHAMPIONS LEAGUE  ·  5× BALLON D'OR  ·  EURO 2016  ·  2× NATIONS LEAGUE  ·  LEAGUE TITLES IN ENGLAND, SPAIN AND ITALY  ·  900+ CAREER GOALS  ·  "
cue(T_20 - 0.05, "tick_roll", 0.6)
cue(C0, "swell", 0.7)


def shot_trophy(c, t, fxd):
    photo_full(c, "p_trophy", t, C0, C_END, 1.0, 1.12, 0.52, 0.42, 0.55, 0.40)
    g = cairo.LinearGradient(0, H * 0.55, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.85)
    c.set_source(g)
    c.paint()
    # 20 ANOS
    a = seg(t, T_20 - 0.1, T_20 + 0.25)
    if a > 0:
        g2 = cairo.RadialGradient(250, H - 250, 0, 250, H - 250, 380)
        g2.add_color_stop_rgba(0, 0, 0, 0, 0.82 * a)
        g2.add_color_stop_rgba(1, 0, 0, 0, 0)
        c.set_source(g2)
        c.paint()
        v = 20 * eout(seg(t, T_20 - 0.1, T_20 + 0.6))
        number_roll(c, v, 250, H - 210, 190, SERIF, WHITE, a, "center")
        text(c, "YEARS", 250, H - 150, 30, MONO, HOT, a, "center", 8)
    # letreiro
    c.rectangle(0, H - 92, W, 60)
    c.set_source_rgba(0.04, 0.045, 0.05, 0.85)
    c.fill()
    font(c, MONO, 28, True)
    tw = text_width(c, TICK, 2)
    off = (t - C0) * 260
    for k in range(3):
        text(c, TICK, 40 - off + k * tw, H - 52, 28, MONO, WHITE, 0.92, "left", 2, True)
    c.rectangle(0, H - 92, 8, 60)
    rgb(c, HOT)
    c.fill()


# ═════════════════════════════ D · contra todos (36.55 → 43.55) ═════════════════════════════
D0, D_END = C_END, 43.55
IMP_D = []
FIGHT_C = ("f_grim", 3500, 10, 780, 0.8)
FOES = [  # nome, x, y, w, rot, t_in, etiqueta, pos etiqueta
    ("f_tenhag", 2880, -470, 560, -4.0, wd("L11", "coach") - 0.08, "COACH · MAN UTD · 2022"),
    ("f_jesus", 2880, 500, 520, 3.5, wd("L11", "coach") + 0.42, "COACH · PORTUGAL · 2026"),
    ("f_club", 4120, -470, 600, 3.0, wd("L11", "club") - 0.02, "CLUB · AL NASSR · 2026"),
    ("f_exec", 4120, 510, 520, -3.0, wd("L11", "executive") - 0.05, "FEDERATION · 2026"),
]
T_GRIM = D0 + 0.25
T_DARED = wd("L11", "dared")
T_WAIT = wd("L11", "wait")
CAM_D = [
    (D0, 3470, 0, 0.58, -1.0, "io"),
    (D0 + 1.4, 3500, 15, 0.64, 0.0, "lin"),
    (T_WAIT - 0.25, 3505, 15, 0.70, 0.0, "in"),
    (D_END, 3520, -12, 2.6, 0.0, "lin"),
]
cue(T_GRIM, "drop_heavy", 1.0)
hit(T_GRIM + 0.08, shake=8, impacts=IMP_D)
for _f in FOES:
    cue(_f[5], "drop", 0.95, 0.4 if _f[1] > 3500 else -0.4)
    hit(_f[5] + 0.08, shake=6, impacts=IMP_D)
    cue(_f[5] + 0.45, "type", 0.35)
for _k in range(4):
    cue(T_DARED + _k * 0.17, "pluck", 0.6, (-0.4, -0.4, 0.4, 0.4)[_k])
cue(T_WAIT - 0.3, "riser_short", 0.9)
cue(D_END, "slam_cut", 0.85)
SILENCE.append((D_END - 0.02, S("L12") + 0.4))


def board_D(c, t, fxd):
    cam = cam_at(CAM_D, t)
    c.save()
    apply_cam(c, cam, t, IMP_D)
    board_bg(c)
    pc = draw_print(c, *FIGHT_C, t=t, t_in=T_GRIM, drop=1.2)
    for i, (nm, x, y, w, r, ti, lab) in enumerate(FOES):
        p = draw_print(c, nm, x, y, w, r, t, t_in=ti)
        if p:
            lx = x - w / 2 if x < 3500 else x - w / 2
            ly = y + p.h / 2 + 40
            label_tag(c, lab, lx, ly, 30, prog=seg(t, ti + 0.4, ti + 1.1), t=t)
            if pc:
                sx_ = -1 if x < 3500 else 1
                sy_ = -1 if y < 0 else 1
                corner = pc.pt(sx_ * (pc.mw / 2 - 30), sy_ * (pc.mh / 2 - 30))
                near = p.pt(-sx_ * (p.mw / 2 - 40), -sy_ * (p.mh / 2 - 40))
                pr_ = seg(t, T_DARED + i * 0.17, T_DARED + i * 0.17 + 0.35)
                string(c, near, corner, pr_, 0.06, 4.0)
                if pr_ > 0:
                    pushpin(c, near[0], near[1], 12)
                if pr_ >= 1:
                    pushpin(c, corner[0], corner[1], 12)
    c.restore()
    light_pool(c)
    dust(c, t, 26)
    # escurece no fim (corte seco para o preto)
    fxd["fade"] = 0.35 * seg(t, T_WAIT + 0.2, D_END)


# ═════════════════════════════ E · hoje (43.55 → 47.55) ═════════════════════════════
E0, E_END = D_END, S("L13") - 0.15
T_TODAY = S("L12")
T_NOV = wd("L12", "november")
cue(T_TODAY - 0.05, "type", 0.6)
cue(T_NOV, "boom_deep", 0.7)
hit(T_NOV, ca=3)


def shot_today(c, t, fxd):
    black(c, (0.012, 0.014, 0.018))
    lw = 700 * eout(seg(t, T_TODAY - 0.3, T_TODAY + 0.4))
    c.rectangle(W / 2 - lw, H / 2 + 24, 2 * lw, 3)
    rgb(c, HOT, 0.9)
    c.fill()
    typed(c, "TODAY", W / 2, H / 2 - 150, 34, seg(t, T_TODAY, T_TODAY + 0.35), MONO, HOT, 1, t, False, "center", 14,
          True)
    a = seg(t, T_NOV - 0.05, T_NOV + 0.5)
    sp = lerp(60, 18, eout(seg(t, T_NOV - 0.05, T_NOV + 1.4)))
    text(c, "05 · 11 · 2026", W / 2, H / 2 - 10, 170, SERIF, WHITE, a, "center", sp)
    text(c, "LISBON  ·  RIYADH  ·  THE WORLD", W / 2, H / 2 + 110, 24, MONO, GREY, seg(t, T_NOV + 0.8, T_NOV + 1.4),
         "center", 8)


# ═════════════════════════════ F/G · o anúncio e a saída (47.55 → 60.45) ═════════════════════════════
F0, F_END = E_END, S("L15") - 0.18
IMP_F = []
PHONE = (0, 2000, 820, -7)
T_AGAIN = wd("L13", "again")
T_STORM = wd("L14", "storming")
T_WAR = wd("L14", "war")
T_COACH2 = wd("L14", "coach")
T_RECOM = wd("L14", "recommended")
BUS = ("k_bus", -2000, 1790, 700, -3.0)
JES = ("k_jesus", -1180, 1720, 620, 2.5)
MEM = ("k_memory", -1640, 2420, 600, -5.0)
CAM_F = [
    (F0, 0, 1995, 1.0, 0.0, "lin"),
    (52.45, 10, 1990, 1.12, 0.0, "io"),
    (53.55, -1600, 1880, 0.98, -1.0, "lin"),
    (57.55, -1590, 1900, 1.0, -1.0, "io"),
    (58.55, -1610, 2110, 1.04, 0.0, "lin"),
    (F_END, -1615, 2120, 1.10, 0.0, "lin"),
]
cue(F0 + 0.1, "phone_buzz", 0.7)
cue(T_AGAIN, "stamp", 0.9)
hit(T_AGAIN + 0.02, flash=0.15, shake=10, impacts=IMP_F)
cue(52.5, "whoosh", 0.7)
cue(T_STORM - 0.05, "drop", 0.9, -0.3)
cue(T_WAR - 0.55, "drop", 0.9, 0.2)
cue(T_WAR - 0.3, "pluck", 0.6)
cue(T_WAR, "snap", 1.0)
cue(T_WAR + 0.05, "stamp", 1.0)
hit(T_WAR + 0.05, flash=0.2, ca=6, shake=14, impacts=IMP_F)
cue(T_RECOM - 0.9, "memory", 0.8)


def ig_screen(mode, t, likes):
    def draw(c, sx, sy, sw, sh):
        c.set_source_rgb(0, 0, 0)
        c.paint()
        # topo
        hy = sy + sh * 0.075
        g = cairo.LinearGradient(sx + sw * 0.06, hy - 20, sx + sw * 0.16, hy + 20)
        g.add_color_stop_rgb(0, 0.98, 0.75, 0.2)
        g.add_color_stop_rgb(0.5, 0.95, 0.2, 0.45)
        g.add_color_stop_rgb(1, 0.6, 0.2, 0.9)
        c.arc(sx + sw * 0.1, hy, sw * 0.055, 0, 2 * math.pi)
        c.set_source(g)
        c.fill()
        c.arc(sx + sw * 0.1, hy, sw * 0.045, 0, 2 * math.pi)
        c.set_source_rgb(0.25, 0.25, 0.27)
        c.fill()
        text(c, "cristiano", sx + sw * 0.19, hy + sw * 0.022, sw * 0.055, SANS, WHITE, 1, "left", bold=True)
        font(c, SANS, sw * 0.055, True)
        verified(c, sx + sw * 0.19 + text_width(c, "cristiano") + sw * 0.045, hy, sw * 0.026)
        # imagem 4:5
        s = surf("ph_post")
        iy = sy + sh * 0.13
        k = sw / s.get_width()
        c.save()
        c.translate(sx, iy)
        c.scale(k, k)
        c.set_source_surface(s, 0, 0)
        c.get_source().set_filter(cairo.FILTER_GOOD)
        c.paint()
        c.restore()
        ih = s.get_height() * k
        if mode == "video":
            c.rectangle(sx, iy, sw, ih)
            c.set_source_rgba(0, 0, 0, 0.35)
            c.fill()
            cx, cy = sx + sw / 2, iy + ih / 2
            c.arc(cx, cy, sw * 0.11, 0, 2 * math.pi)
            c.set_source_rgba(0, 0, 0, 0.5)
            c.fill()
            c.move_to(cx - sw * 0.035, cy - sw * 0.06)
            c.line_to(cx + sw * 0.065, cy)
            c.line_to(cx - sw * 0.035, cy + sw * 0.06)
            c.close_path()
            c.set_source_rgb(1, 1, 1)
            c.fill()
            c.rectangle(sx, iy + ih - 6, sw, 6)
            c.set_source_rgba(1, 1, 1, 0.25)
            c.fill()
            c.rectangle(sx, iy + ih - 6, sw * 0.18, 6)
            c.set_source_rgb(1, 1, 1)
            c.fill()
        ay = iy + ih + sw * 0.09
        heart(c, sx + sw * 0.08, ay, sw * 0.075, fill=True, col=(0.96, 0.2, 0.3))
        c.arc(sx + sw * 0.22, ay, sw * 0.04, 0, 2 * math.pi)
        c.set_source_rgb(1, 1, 1)
        c.set_line_width(2)
        c.stroke()
        text(c, f"{int(likes):,} likes", sx + sw * 0.05, ay + sw * 0.11, sw * 0.05, SANS, WHITE, 1, "left", bold=True)
        text(c, "cristiano", sx + sw * 0.05, ay + sw * 0.19, sw * 0.047, SANS, WHITE, 1, "left", bold=True)
        font(c, SANS, sw * 0.047, True)
        text(c, "Portugal will always be in me.", sx + sw * 0.05 + text_width(c, "cristiano ") + 4, ay + sw * 0.19,
             sw * 0.047, SANS, (0.9, 0.9, 0.9), 1, "left")
        text(c, "View all 1,284,903 comments", sx + sw * 0.05, ay + sw * 0.26, sw * 0.042, SANS, GREY, 1, "left")
    return draw


def board_F(c, t, fxd):
    cam = cam_at(CAM_F, t)
    c.save()
    apply_cam(c, cam, t, IMP_F)
    board_bg(c)
    # memória (sépia) — aparece suave
    if t > T_RECOM - 1.1:
        a = eio(seg(t, T_RECOM - 1.1, T_RECOM - 0.2))
        draw_print(c, *MEM, t=t, alpha=a, pin=False, tapes=True, lift=0.3 * (1 - a))
        label_tag(c, "AL NASSR · 2023 — FRIENDS", MEM[1] - 300, MEM[2] + 260, 22, prog=seg(t, T_RECOM - 0.3, T_RECOM + 0.6),
                  t=t)
        note(c, "he picked him", MEM[1] + 170, MEM[2] - 230, 46, -8, HOT, 1, seg(t, T_RECOM + 0.2, T_RECOM + 0.9))
    pb = draw_print(c, *BUS, t=t, t_in=T_STORM - 0.05)
    pj = draw_print(c, *JES, t=t, t_in=T_WAR - 0.55)
    if pb:
        label_tag(c, "30.09.2026 · COPENHAGEN — WALKS OUT", BUS[1] - 350, BUS[2] + 250, 22,
                  prog=seg(t, T_STORM + 0.3, T_STORM + 1.3), t=t)
    if pb and pj:
        a0 = (pb.pt(330, -40))
        b0 = (pj.pt(-310, -40))
        if t < T_WAR:
            string(c, a0, b0, seg(t, T_WAR - 0.45, T_WAR - 0.12), 0.05, 3.6)
        else:
            string_snap(c, a0, b0, t, T_WAR, 0.05, 3.6)
    stamp(c, "st_atwar", -1590, 1700, 470, -7, t, T_WAR + 0.05)
    # celular
    ph_mode = "post" if t < 69 else "video"
    likes = 1200000 + 11000000 * eout(seg(t, F0, F0 + 6))
    phone(c, PHONE[0], PHONE[1], PHONE[2], PHONE[3], t, ig_screen(ph_mode, t, likes))
    stamp(c, "st_retired", 250, 2250, 520, -11, t, T_AGAIN)
    c.restore()
    light_pool(c)
    dust(c, t, 26)


# ═════════════════════════════ H · recordes (60.45 → 69.0) ═════════════════════════════
H0, H_END = F_END, S("L16") - 0.15
T_146 = wd("L15", "146")
T_234 = wd("L15", "234")
cue(H0 + 0.5, "type", 0.55)
cue(T_146 - 0.9, "counter", 0.8, -0.3)
cue(T_146 + 0.05, "lock", 1.0, -0.3)
cue(T_234 - 0.9, "counter", 0.8, 0.3)
cue(T_234 + 0.05, "lock", 1.0, 0.3)


def shot_records(c, t, fxd):
    photo_full(c, "r_bg", t, H0, H_END, 1.05, 1.15, 0.5, 0.45, 0.52, 0.4, alpha=0.75)
    c.set_source_rgba(0.02, 0.025, 0.03, 0.55)
    c.paint()
    typed(c, "ALL-TIME TOP SCORER IN INTERNATIONAL FOOTBALL", W / 2, 250, 30,
          seg(t, H0 + 0.5, H0 + 2.0), MONO, HOT, 1, t, False, "center", 6, True)
    for xx, tt, val, lab in ((W / 2 - 380, T_146, 146, "GOALS"), (W / 2 + 380, T_234, 234, "GAMES")):
        a = seg(t, tt - 0.95, tt - 0.75)
        if a <= 0:
            continue
        v = val * eout(seg(t, tt - 0.95, tt + 0.05))
        sc = 1 + 0.06 * pulse(t, tt + 0.02, tt + 0.3)
        c.save()
        c.translate(xx, 650)
        c.scale(sc, sc)
        number_roll(c, v, 0, 0, 300, SERIF, WHITE, a, "center")
        c.restore()
        text(c, lab, xx, 740, 34, MONO, GREY, a, "center", 14, True)
    lh = 330 * eout(seg(t, T_146 + 0.3, T_234 - 0.6))
    c.rectangle(W / 2 - 1, 640 - lh / 2 - 90, 2, lh)
    rgb(c, HOT, 0.8)
    c.fill()


# ═════════════════════════════ I · a despedida + recuo (69.0 → 79.1) ═════════════════════════════
I0, I_END = H_END, 79.1
GB = ("gb_cry", 760, 1960, 600, 4.0)
T_LETTER = wd("L16", "just")
T_BACK = S("L17")
CAM_I = [
    (I0, 760, 1950, 1.25, 0.0, "lin"),
    (T_LETTER - 0.2, 770, 1915, 1.45, 0.0, "io"),
    (T_LETTER + 0.9, 20, 1995, 1.18, -1.0, "lin"),
    (T_BACK + 0.2, 10, 1995, 1.25, -1.0, "io"),
    (I_END - 0.25, 900, 820, 0.205, 0.0, "lin"),
    (I_END, 900, 820, 0.2, 0.0, "lin"),
]
cue(I0 + 0.2, "memory", 0.6)
cue(T_LETTER - 0.1, "whoosh", 0.5)
cue(T_BACK + 0.3, "riser", 1.0)
LINKS = [((0, 330), (3500, 10)), ((0, 330), (-1590, 1720)), ((-1590, 1720), (0, 2000)), ((3500, 10), (760, 1960)),
         ((0, -300), (1270, 500))]


def board_I(c, t, fxd):
    cam = cam_at(CAM_I, t)
    c.save()
    apply_cam(c, cam, t, [])
    board_bg(c)
    far = t > T_BACK
    # tudo o que já está no quadro
    for nm, x, y, w, r in WALL:
        draw_print(c, nm, x, y, w, r, t)
    if far:
        draw_print(c, *MEME_A, t=t)
        draw_print(c, *MEME_B, t=t)
        draw_print(c, *FIGHT_C, t=t)
        for nm, x, y, w, r, ti, lab in FOES:
            draw_print(c, nm, x, y, w, r, t)
        draw_print(c, *BUS, t=t)
        draw_print(c, *JES, t=t)
        draw_print(c, *MEM, t=t, pin=False, tapes=True)
        stamp(c, "st_no", 1270, 490, 640, -9, t, 0)
        stamp(c, "st_atwar", -1590, 1700, 470, -7, t, 0)
        for k, (p0, p1) in enumerate(LINKS):
            string(c, p0, p1, seg(t, T_BACK + 0.8 + k * 0.35, T_BACK + 1.6 + k * 0.35), 0.04, 6.0)
    pg = draw_print(c, *GB, t=t, t_in=I0 + 0.2, dur_in=1.1, flash=False, drop=0.6)
    if pg:
        label_tag(c, "SAID GOODBYE · NO FAREWELL MATCH", GB[1] - 300, GB[2] + 300, 22,
                  prog=seg(t, I0 + 1.2, I0 + 2.4), t=t)
    phone(c, PHONE[0], PHONE[1], PHONE[2], PHONE[3], t, ig_screen("video", t, 12400000))
    stamp(c, "st_retired", 250, 2250, 520, -11, t, 0)
    c.restore()
    light_pool(c)
    dust(c, t, 26)


# ═════════════════════════════ J · título (79.1 → 83.55) ═════════════════════════════
J0, J_END = I_END, S("L18") - 0.12
T_STAMP_T = J0 + 1.25
cue(J0, "braam", 0.85)
hit(J0, flash=0.5, ca=8)
cue(T_STAMP_T - 0.1, "stamp_big", 1.0)
hit(T_STAMP_T, flash=0.2, ca=5)


def shot_title(c, t, fxd):
    black(c, (0.03, 0.036, 0.044))
    c.save()
    board_bg(c)
    c.restore()
    light_pool(c, a=0.12)
    u = seg(t, J0, J_END)
    z = lerp(1.0, 1.07, u)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    typed(c, "CASE FILE Nº 07", W / 2, 300, 30, seg(t, J0 + 0.1, J0 + 0.6), MONO, GREY, 1, t, False, "center", 10, True)
    a1 = seg(t, J0, J0 + 0.35)
    sp = lerp(40, 4, eout(seg(t, J0, J0 + 1.2)))
    text(c, "CRISTIANO RONALDO", W / 2, 500, 128, SERIF, WHITE, a1, "center", sp)
    a2 = seg(t, J0 + 0.35, J0 + 0.7)
    sp2 = lerp(40, 4, eout(seg(t, J0 + 0.35, J0 + 1.5)))
    text(c, "BECAME HOMELANDER", W / 2, 650, 128, SERIF, HOT, a2, "center", sp2)
    lw = 640 * eout(seg(t, J0 + 0.6, J0 + 1.4))
    c.rectangle(W / 2 - lw, 712, 2 * lw, 3)
    rgb(c, HOT, 0.85)
    c.fill()
    text(c, "THE HERO WHO COULDN'T STOP BEING THE CENTER", W / 2, 790, 26, MONO, GREY, seg(t, J0 + 1.6, J0 + 2.2),
         "center", 6)
    stamp(c, "st_classified", W / 2 + 560, 310, 430, 9, t, T_STAMP_T)
    c.restore()
    fxd["fade"] = seg(t, J_END - 0.35, J_END)


# ═════════════════════════════ K · inscreva-se + ficha (83.55 → 99.35) ═════════════════════════════
K0, K_END = J_END, S("L22") - 0.1
T_SUB = wd("L18", "subscribe")
T_FOR = S("L19")
T_HL = S("L20")
T_STRONG = wd("L20", "strongest")
T_FLIES = wd("L21", "flies")
T_LASERS2 = wd("L21", "lasers")
T_INDES = wd("L21", "practically")
cue(T_SUB + 0.15, "click", 1.0)
cue(T_SUB + 0.35, "ding", 0.8)
cue(T_FOR - 0.2, "paper", 0.9)
cue(T_FOR + 0.1, "type", 0.6)
cue(T_HL, "type", 0.5)
cue(T_STRONG, "type", 0.5)
cue(T_STRONG + 1.2, "tick_roll", 0.5)
for _tt in (T_FLIES, T_LASERS2 - 0.15, T_INDES + 0.4):
    cue(_tt + 0.15, "check", 0.9)
SHEET = (W / 2, 1080 + 560)


def shot_profile(c, t, fxd):
    black(c)
    board_bg(c)
    light_pool(c, a=0.11)
    # câmera: começa no 'inscreva-se', desce para a ficha
    cam_y = lerp(0, 1, eio(seg(t, T_FOR - 0.45, T_FOR + 0.55)))
    zz = lerp(1.0, 1.12, seg(t, T_FOR, K_END))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zz, zz)
    c.translate(-W / 2, -H / 2 - cam_y * 1080)
    # inscreva-se
    done = t > T_SUB + 0.15
    a = seg(t, K0 + 0.05, K0 + 0.4)
    c.save()
    c.translate(W / 2, H / 2)
    sc = 1 + 0.08 * pulse(t, T_SUB + 0.1, T_SUB + 0.4)
    c.scale(sc, sc)
    c.scale(1.35, 1.35)
    bw, bh = 640, 120
    soft_shadow(c, -bw / 2, -bh / 2, bw, bh, 12, 30, 0.6)
    rrect(c, -bw / 2, -bh / 2, bw, bh, 12)
    if done:
        c.set_source_rgba(0.12, 0.13, 0.15, a)
    else:
        rgb(c, HOT, a)
    c.fill()
    text(c, "SUBSCRIBED" if done else "SUBSCRIBE", -22 if done else 0, 18, 52, BEBAS, WHITE, a, "center", 6)
    if done:
        marker_line(c, (118, -2), (134, 14), seg(t, T_SUB + 0.2, T_SUB + 0.3), 7, WHITE, 0)
        marker_line(c, (134, 14), (166, -24), seg(t, T_SUB + 0.3, T_SUB + 0.45), 7, WHITE, 0)
    c.restore()
    typed(c, "NEW EVIDENCE EVERY WEEK", W / 2, H / 2 + 150, 30, seg(t, K0 + 0.6, K0 + 1.6), MONO, GREY, a, t, False,
          "center", 6)
    # cursor
    if t > T_SUB - 0.6 and t < T_FOR:
        u = eout(seg(t, T_SUB - 0.6, T_SUB + 0.1))
        cx, cy = lerp(W / 2 + 520, W / 2 + 140, u), lerp(H / 2 + 300, H / 2 + 20, u)
        c.move_to(cx, cy)
        c.line_to(cx, cy + 46)
        c.line_to(cx + 12, cy + 35)
        c.line_to(cx + 22, cy + 56)
        c.line_to(cx + 30, cy + 52)
        c.line_to(cx + 20, cy + 32)
        c.line_to(cx + 36, cy + 32)
        c.close_path()
        c.set_source_rgb(1, 1, 1)
        c.fill_preserve()
        c.set_source_rgb(0, 0, 0)
        c.set_line_width(2)
        c.stroke()
    # ficha
    if t > T_FOR - 0.45:
        sx, sy = SHEET
        sw, sh = 1240, 900
        c.save()
        c.translate(sx, sy + 120 * (1 - eout(seg(t, T_FOR - 0.45, T_FOR + 0.3))))
        c.rotate(math.radians(-1.2))
        soft_shadow(c, -sw / 2, -sh / 2, sw, sh, 4, 40, 0.7)
        p = cairo.SurfacePattern(surf("paper"))
        p.set_extend(cairo.EXTEND_REPEAT)
        c.rectangle(-sw / 2, -sh / 2, sw, sh)
        c.set_source(p)
        c.fill()
        ink = (0.1, 0.1, 0.1)
        c.rectangle(-sw / 2, -sh / 2, sw, 80)
        c.set_source_rgb(0.12, 0.12, 0.13)
        c.fill()
        typed(c, "VOUGHT INTERNATIONAL · PERSONNEL FILE", -sw / 2 + 40, -sh / 2 + 52, 30,
              seg(t, T_FOR, T_FOR + 0.9), TYPE, (0.9, 0.9, 0.88), 1, t, False)
        typed(c, "SUBJECT B: HOMELANDER", -sw / 2 + 40, -sh / 2 + 170, 64, seg(t, T_HL - 0.1, T_HL + 0.8), TYPE, ink,
              1, t, False)
        # foto
        draw_print(c, "w_hero", -sw / 2 + 300, 90, 470, -3, t, t_in=T_FOR + 0.25, pin=False, tapes=True)
        # campos
        fx0 = -sw / 2 + 600
        typed(c, "REAL NAME:", fx0, -sh / 2 + 280, 32, seg(t, T_HL + 0.3, T_HL + 0.8), TYPE, ink, 1, t, False)
        rb = 260 * eout(seg(t, T_HL + 0.8, T_HL + 1.1))
        c.rectangle(fx0 + 230, -sh / 2 + 252, rb, 36)
        c.set_source_rgb(0.05, 0.05, 0.05)
        c.fill()
        typed(c, "CLASS: STRONGEST SUPE ON EARTH", fx0, -sh / 2 + 345, 32, seg(t, T_STRONG, T_STRONG + 1.0), TYPE, ink, 1,
              t, False)
        typed(c, "THREAT LEVEL:", fx0, -sh / 2 + 410, 32, seg(t, T_STRONG + 1.0, T_STRONG + 1.3), TYPE, ink, 1, t, False)
        bl = 300
        c.rectangle(fx0 + 290, -sh / 2 + 384, bl, 30)
        c.set_source_rgb(0.15, 0.15, 0.15)
        c.set_line_width(2)
        c.stroke()
        fill = bl * eout(seg(t, T_STRONG + 1.2, T_STRONG + 1.9))
        c.rectangle(fx0 + 292, -sh / 2 + 386, max(0, fill - 4), 26)
        rgb(c, RED)
        c.fill()
        for k, (lab, tt) in enumerate((("FLIGHT", T_FLIES), ("HEAT VISION", T_LASERS2 - 0.15),
                                       ("INVULNERABLE", T_INDES + 0.4))):
            yy = -sh / 2 + 500 + k * 70
            a = seg(t, tt - 0.2, tt)
            c.rectangle(fx0, yy - 30, 38, 38)
            c.set_source_rgba(0.1, 0.1, 0.1, a)
            c.set_line_width(3)
            c.stroke()
            typed(c, lab, fx0 + 60, yy, 34, seg(t, tt - 0.2, tt + 0.25), TYPE, ink, a, t, False)
            ck = seg(t, tt + 0.1, tt + 0.3)
            if ck > 0:
                marker_line(c, (fx0 + 4, yy - 12), (fx0 + 16, yy + 4), seg(ck, 0, 0.4), 7, RED, 0)
                marker_line(c, (fx0 + 16, yy + 4), (fx0 + 46, yy - 40), seg(ck, 0.4, 1), 7, RED, 0)
        c.restore()
    c.restore()
    dust(c, t, 20)


# ═════════════════════════════ L · outdoors (99.35 → 102.7) ═════════════════════════════
L0, L_END = K_END, S("L23") - 0.09
T_BILL = wd("L22", "billboard")
cue(L0, "whoosh", 0.6)
cue(T_BILL - 0.4, "whoosh_big", 0.9)
cue(T_BILL - 0.2, "crowd", 0.7)
_SMALL = {}


def _small_bill():
    if "s" not in _SMALL:
        s = surf("s_billboard")
        sm = cairo.ImageSurface(cairo.FORMAT_RGB24, 320, 180)
        cc = cairo.Context(sm)
        cc.scale(320 / s.get_width(), 180 / s.get_height())
        cc.set_source_surface(s, 0, 0)
        cc.get_source().set_filter(cairo.FILTER_BEST)
        cc.paint()
        _SMALL["s"] = sm
    return _SMALL["s"]


def shot_billboards(c, t, fxd):
    black(c, (0.02, 0.022, 0.03))
    z = math.exp(lerp(math.log(1.0), math.log(0.085), eio(seg(t, T_BILL - 0.45, L_END + 0.3))))
    tw, th, gap = 1920, 1080, 120
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    big = surf("s_billboard")
    sm = _small_bill()
    n = 9
    for gx in range(-n, n + 1):
        for gy in range(-n, n + 1):
            x, y = gx * (tw + gap), gy * (th + gap)
            if abs(x) * z > W / 2 + tw * z or abs(y) * z > H / 2 + th * z:
                continue
            c.save()
            c.translate(x - tw / 2, y - th / 2)
            if gx == 0 and gy == 0 or z > 0.45:
                c.scale(tw / big.get_width(), th / big.get_height())
                c.set_source_surface(big, 0, 0)
            else:
                c.scale(tw / 320, th / 180)
                c.set_source_surface(sm, 0, 0)
            c.get_source().set_filter(cairo.FILTER_GOOD)
            c.paint_with_alpha(1 if (gx == 0 and gy == 0) else 0.92)
            c.restore()
            c.rectangle(x - tw / 2 - 18, y - th / 2 - 18, tw + 36, th + 36)
            c.set_source_rgba(0.1, 0.11, 0.12, 1)
            c.set_line_width(18)
            c.stroke()
    c.restore()
    light_pool(c, a=0.06)


# ═════════════════════════════ M · as câmeras desligam (102.7 → 106.6) ═════════════════════════════
M0, M_END = L_END, S("L24") - 0.26
T_OFF = wd("L23", "switch")
cue(M0, "tv_on", 0.6)
cue(T_OFF + 0.05, "crt_off", 1.0)
SILENCE.append((T_OFF + 0.25, S("L24") + 0.2))


def _broadcast(c, t):
    photo_full(c, "s_billboard", t, M0, M_END, 1.0, 1.06, 0.5, 0.45)
    # linhas de TV
    for y in range(0, H, 4):
        c.rectangle(0, y, W, 1.4)
    c.set_source_rgba(0, 0, 0, 0.18)
    c.fill()
    if int(t * 2) % 2 == 0:
        c.arc(110, 92, 13, 0, 2 * math.pi)
        rgb(c, HOT)
        c.fill()
    text(c, "LIVE", 135, 104, 34, BEBAS, WHITE, 1, "left", 4)
    c.rectangle(90, H - 210, 980, 110)
    c.set_source_rgba(0.06, 0.1, 0.35, 0.85)
    c.fill()
    c.rectangle(90, H - 210, 14, 110)
    rgb(c, HOT)
    c.fill()
    text(c, "HOMELANDER", 130, H - 160, 50, BEBAS, WHITE, 1, "left", 4)
    text(c, "AMERICA'S GREATEST HERO · VOUGHT NEWS NETWORK", 130, H - 118, 24, MONO, (0.85, 0.88, 0.95), 1, "left", 2)


def shot_crt(c, t, fxd):
    black(c, (0, 0, 0))
    if t < T_OFF + 0.05:
        _broadcast(c, t)
        return
    u = seg(t, T_OFF + 0.05, T_OFF + 0.5)
    if u >= 1:
        dot = 1 - seg(t, T_OFF + 0.5, T_OFF + 0.9)
        glow(c, W / 2, H / 2, 40, (0.9, 0.95, 1.0), 0.8 * dot)
        return
    c.push_group()
    _broadcast(c, t)
    pat = c.pop_group()
    sy = lerp(1, 0.004, ein(seg(u, 0, 0.55)))
    sx = 1 - ein(seg(u, 0.55, 1.0))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(max(0.002, sx), max(0.002, sy))
    c.translate(-W / 2, -H / 2)
    c.set_source(pat)
    c.paint()
    c.restore()
    c.rectangle(W / 2 - W / 2 * sx, H / 2 - 3, W * sx, 6)
    c.set_source_rgba(0.95, 0.97, 1, 0.9 * seg(u, 0.3, 0.6))
    c.fill()


# ═════════════════════════════ N · adorado (106.6 → 110.95) ═════════════════════════════
N0, N_END = M_END, S("L25") - 0.11
T_ADORED = wd("L24", "adored")
cue(N0 + 0.3, "crowd", 0.5)
cue(T_ADORED + 0.4, "type", 0.5)


def shot_adored(c, t, fxd):
    black(c, (0.01, 0.012, 0.016))
    s = surf("s_adored")
    u = seg(t, N0, N_END)
    k = (H / s.get_height()) * lerp(1.0, 1.1, u)
    a = eio(seg(t, N0 + 0.1, N0 + 1.0))
    c.save()
    c.translate(W / 2, H / 2 + 20)
    c.scale(k, k)
    c.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    c.paint_with_alpha(a)
    c.restore()
    for side in (-1, 1):
        g = cairo.LinearGradient(W / 2 + side * 330, 0, W / 2 + side * 560, 0)
        g.add_color_stop_rgba(0, 0.01, 0.012, 0.016, 0)
        g.add_color_stop_rgba(1, 0.01, 0.012, 0.016, 1)
        c.set_source(g)
        c.rectangle(0 if side < 0 else W / 2, 0, W / 2, H)
        c.fill()
    label_tag(c, "NEEDS: ADORATION · 24/7", 120, H - 140, 30, prog=seg(t, T_ADORED + 0.3, T_ADORED + 1.3), t=t)


# ═════════════════════════════ O/P · não divide o palco / perde o holofote (110.95 → 119.95) ═════════════════════════════
O0 = N_END
T_ANYONE = wd("L25", "anyone")
T_SPOT = wd("L26", "spotlight")
T_CHILD = wd("L26", "reacts")
P_END = S("L27") - 0.12
cue(O0 + 0.05, "drop", 0.9)
cue(T_ANYONE - 0.05, "tear", 1.0)
cue(T_SPOT - 0.3, "spot_off", 0.8)
cue(T_CHILD - 0.08, "boom", 0.7)


def shot_share(c, t, fxd):
    black(c)
    board_bg(c)
    nm = "s_share"
    m = META[nm]
    w = 1240
    k = w / m["w"]
    x, y, rot = W / 2, H / 2 + 10, -1.5
    # holofote: some depois de 'spotlight'
    spot = 1 - eio(seg(t, T_SPOT - 0.3, T_SPOT + 0.5))
    if t < T_ANYONE - 0.05:
        draw_print(c, nm, x, y, w, rot, t, t_in=O0, pin=False, tapes=True)
    else:
        u = seg(t, T_ANYONE - 0.05, T_ANYONE + 1.3)
        cut = [(0.47 + 0.02 * math.sin(i * 1.7) + random.Random(i).uniform(-0.012, 0.012), i / 14) for i in range(15)]

        def half(left, tx, ty, rr, a):
            c.save()
            c.translate(x + tx, y + ty)
            c.rotate(math.radians(rot + rr))
            c.scale(k, k)
            mw, mh = m["w"], m["h"]
            c.new_path()
            if left:
                c.move_to(-mw / 2, -mh / 2)
                for fx_, fy_ in cut:
                    c.line_to(-mw / 2 + fx_ * mw, -mh / 2 + fy_ * mh)
                c.line_to(-mw / 2, mh / 2)
            else:
                c.move_to(mw / 2, -mh / 2)
                for fx_, fy_ in cut:
                    c.line_to(-mw / 2 + fx_ * mw, -mh / 2 + fy_ * mh)
                c.line_to(mw / 2, mh / 2)
            c.close_path()
            c.save()
            c.translate(14, 22)
            c.set_source_rgba(0, 0, 0, 0.5 * a)
            c.fill_preserve()
            c.restore()
            c.clip()
            c.set_source_surface(surf(nm), -mw / 2, -mh / 2)
            c.paint_with_alpha(a)
            c.restore()

        e = ein(u)
        half(True, -60 * e - 30 * u, 900 * e, -14 * e, 1 - seg(u, 0.6, 1.0))
        half(False, 25 * u, 0, 1.5 * u, 1)
    # holofote / escuridão
    if t > T_SPOT - 1.2:
        lx = lerp(W / 2 + 280, W + 500, ein(seg(t, T_SPOT - 0.3, T_SPOT + 0.6)))
        c.set_source_rgba(0, 0, 0, 0.62 * (1 - spot) + 0.25)
        c.paint()
        glow(c, lx, H / 2, 520, (1, 0.95, 0.85), 0.22 * (0.4 + 0.6 * spot))
    light_pool(c, a=0.08 * spot)


def shot_lost(c, t, fxd):
    photo_full(c, "s_lost", t, T_CHILD - 0.12, P_END + 3.5, 1.0, 1.18, 0.40, 0.42, 0.42, 0.40)
    c.set_source_rgba(0, 0, 0, 0.12)
    c.paint()
    label_tag(c, "TRIGGER  //  LOSING THE SPOTLIGHT", 120, H - 150, 28, prog=seg(t, T_CHILD + 0.9, T_CHILD + 2.0), t=t)


# ═════════════════════════════ Q · pode derrubar um avião (119.95 → 123.4) ═════════════════════════════
Q0, Q_END = P_END, S("L28") - 0.14
T_PLANE = wd("L27", "airplane")
T_BEAM0 = T_PLANE - 0.75
cue(Q0, "paper", 0.7)
cue(T_BEAM0, "laser", 1.0)
cue(T_PLANE + 0.12, "boom_deep", 1.1)
hit(T_PLANE + 0.12, flash=0.7, ca=12)
SILENCE.append((Q0 - 0.05, T_BEAM0 - 0.02))


def shot_burn(c, t, fxd):
    black(c, (0.02, 0.022, 0.026))
    light_pool(c, a=0.1)
    u = seg(t, T_BEAM0, T_PLANE + 0.1)
    z = lerp(1.08, 1.0, eout(seg(t, Q0, Q0 + 1.2)))

    def burn(c2, w, h):
        if t < T_BEAM0:
            return
        p0 = (-w * 0.62, -h * 0.30)
        p1 = (w * 0.62, h * 0.34)
        hx, hy = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
        c2.set_line_cap(cairo.LINE_CAP_ROUND)
        c2.move_to(*p0)
        c2.line_to(hx, hy)
        c2.set_source_rgba(0.06, 0.03, 0.02, 0.95)
        c2.set_line_width(26)
        c2.stroke()
        c2.move_to(*p0)
        c2.line_to(hx, hy)
        c2.set_source_rgba(1, 0.45, 0.1, 0.55 * (1 - seg(t, T_PLANE, T_PLANE + 1.5)))
        c2.set_line_width(6)
        c2.stroke()
        rnd = random.Random(int(t * 30))
        if u < 1:
            for i in range(14):
                ex = hx + rnd.uniform(-30, 30)
                ey = hy + rnd.uniform(-30, 30)
                glow(c2, ex, ey, rnd.uniform(4, 12), (1, 0.6, 0.2), 0.9)

    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    newspaper(c, W / 2, H / 2 + 60, 760, 3, t, burn)
    c.restore()
    if T_BEAM0 <= t < T_PLANE + 0.1:
        hx = lerp(-200, W + 200, u)
        hy = lerp(150, H - 120, u)
        glow_line(c, (hx - 2600 * 0.9, hy - 2600 * 0.33), (hx, hy), 10)
        glow(c, hx, hy, 160, (1, 0.35, 0.2), 0.7)


# ═════════════════════════════ R · tipografia: o centro (123.4 → 132.6) ═════════════════════════════
R0, R_END = Q_END, S("L30") - 0.2
T_NOPOW = wd("L28", "no")
T_FIX = wd("L28", "can")
T_SURV = wd("L28", "he")
T_CENTER0 = S("L29")
T_CENTER = wd("L29", "center")
cue(R0 + 0.2, "heartbeat", 0.9)
cue(R0 + 1.3, "heartbeat", 0.8)
cue(R0 + 2.4, "heartbeat", 0.8)
cue(T_NOPOW, "boom", 0.5)
cue(T_SURV, "heartbeat", 1.0)
cue(T_CENTER - 0.05, "boom_deep", 0.9)
cue(T_CENTER + 0.25, "marker", 1.0)
cue(T_CENTER + 1.05, "slide", 0.9)
SILENCE.append((R0, T_CENTER - 0.05))


def shot_center(c, t, fxd):
    black(c, (0.012, 0.014, 0.018))
    lines = [("No power in the world", T_NOPOW, H / 2 - 120), ("can fix the one thing", T_FIX, H / 2),
             ("he can’t survive.", T_SURV, H / 2 + 120)]
    fade_all = 1 - seg(t, T_CENTER0 - 0.35, T_CENTER0 + 0.05)
    for s, tt, y in lines:
        a = eio(seg(t, tt - 0.05, tt + 0.5)) * fade_all
        dy = 18 * (1 - eout(seg(t, tt - 0.05, tt + 0.7)))
        text(c, s, W / 2, y + dy, 84, SERIF, WHITE, a, "center", 1)
    if t > T_CENTER0 - 0.1:
        a = eio(seg(t, T_CENTER0 - 0.1, T_CENTER0 + 0.4))
        text(c, "NO LONGER BEING", W / 2, H / 2 - 150, 40, MONO, GREY, a, "center", 14)
        # "THE CENTER." escorrega para fora do centro; o círculo fica vazio no meio
        su = ein(seg(t, T_CENTER + 1.05, T_CENTER + 2.3))
        ox, oy, rr = 1200 * su, 260 * su, 14 * su
        c.save()
        c.translate(W / 2 + ox, H / 2 + 60 + oy)
        c.rotate(math.radians(rr))
        text(c, "THE CENTER.", 0, 0, 170, SERIF, WHITE, a, "center", 2)
        c.restore()
        marker_ellipse(c, W / 2 + 120, H / 2 + 5, 330, 120, seg(t, T_CENTER + 0.25, T_CENTER + 0.85), 11, 10, HOT,
                       -3)


# ═════════════════════════════ S · olhe de perto (132.6 → 142.3) ═════════════════════════════
S0, S_END = R_END, 142.3
IMP_S = []
T_LOOK = wd("L30", "look")
T_AG1 = wd("L31", "again")
T_AG2 = wd("L31", "again", 1)
T_HIDE = S("L32")
BENCH = ("s_bench", 0, 120, 1000, 0.6)
TUN = ("s_tunnel", -880, -250, 620, -5.0)
DUB = ("s_dublin", 880, -240, 640, 4.0)
CAM_S = [
    (S0, 0, 110, 1.18, 0.0, "lin"),
    (T_AG1 - 0.6, 10, 60, 1.26, 0.0, "io"),
    (T_AG1 - 0.15, 0, -40, 0.74, 0.0, "lin"),
    (T_HIDE - 0.1, 0, -30, 0.77, 0.0, "io"),
    (S_END, 5, 45, 1.85, 0.0, "lin"),
]
cue(S0 + 0.1, "drop", 0.9)
cue(T_LOOK, "lens", 0.8)
cue(T_AG1 - 0.6, "whoosh", 0.6)
cue(T_AG1, "drop_heavy", 1.0, -0.5)
hit(T_AG1 + 0.05, flash=0.12, shake=12, impacts=IMP_S)
cue(T_AG2, "drop_heavy", 1.0, 0.5)
hit(T_AG2 + 0.05, flash=0.12, shake=12, impacts=IMP_S)
cue(T_AG1 + 0.2, "pluck", 0.6, -0.4)
cue(T_AG2 + 0.2, "pluck", 0.6, 0.4)
cue(T_HIDE, "riser", 0.8)


def shot_look(c, t, fxd):
    cam = cam_at(CAM_S, t)
    c.save()
    apply_cam(c, cam, t, IMP_S)
    board_bg(c)
    pb = draw_print(c, *BENCH, t=t, t_in=S0 + 0.1)
    pt = draw_print(c, *TUN, t=t, t_in=T_AG1)
    pd = draw_print(c, *DUB, t=t, t_in=T_AG2)
    if pt:
        label_tag(c, "19.10.2022 · OLD TRAFFORD", TUN[1] - 320, TUN[2] + 260, 24, prog=seg(t, T_AG1 + 0.2, T_AG1 + 0.9),
                  t=t)
        string(c, pt.top(), pb.top(), seg(t, T_AG1 + 0.15, T_AG1 + 0.45), 0.06, 4)
    if pd:
        label_tag(c, "13.11.2025 · DUBLIN", DUB[1] - 320, DUB[2] + 270, 24, prog=seg(t, T_AG2 + 0.2, T_AG2 + 0.9), t=t)
        string(c, pd.top(), pb.top(), seg(t, T_AG2 + 0.15, T_AG2 + 0.45), 0.06, 4)
    if pb:
        label_tag(c, "27.09.2026 · OSLO", BENCH[1] - 500, BENCH[2] + 330, 24, prog=seg(t, S0 + 0.8, S0 + 1.6), t=t)
    # lupa
    la = seg(t, T_LOOK - 0.3, T_LOOK + 0.1) * (1 - seg(t, T_AG1 - 0.7, T_AG1 - 0.3))
    if pb and la > 0:
        u = eio(seg(t, T_LOOK - 0.3, T_LOOK + 1.4))
        lx, ly = lerp(380, 0, u), lerp(400, 30, u)
        R, mag = 190, 1.9
        c.save()
        c.arc(lx, ly, R, 0, 2 * math.pi)
        c.clip()
        c.translate(lx, ly)
        c.scale(mag, mag)
        c.translate(-lx, -ly)
        draw_print(c, *BENCH, t=t, pin=False, shadow=0, alpha=la)
        c.restore()
        c.arc(lx, ly, R, 0, 2 * math.pi)
        c.set_source_rgba(0.05, 0.05, 0.06, la)
        c.set_line_width(22)
        c.stroke()
        c.arc(lx, ly, R - 8, math.radians(200), math.radians(260))
        c.set_source_rgba(1, 1, 1, 0.35 * la)
        c.set_line_width(5)
        c.stroke()
        ang = math.radians(42)
        c.move_to(lx + (R + 8) * math.cos(ang), ly + (R + 8) * math.sin(ang))
        c.line_to(lx + (R + 230) * math.cos(ang), ly + (R + 230) * math.sin(ang))
        c.set_source_rgba(0.05, 0.05, 0.06, la)
        c.set_line_width(40)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.stroke()
    c.restore()
    light_pool(c, a=0.08)
    dust(c, t, 24)
    fxd["fade"] = 0.25 * seg(t, T_HIDE + 0.3, S_END)


# ═════════════════════════════ T · ATO I (142.3 → 147.6) ═════════════════════════════
T0, T_END = S_END, TOTAL
T_REW = T0 + 0.55
T_BENCHW = T0 + 2.1
cue(T0 + 0.05, "type", 0.5)
cue(T_REW, "rewind", 1.0)
cue(T_BENCHW, "braam", 1.0)
hit(T_BENCHW, flash=0.25, ca=6)
cue(T_BENCHW + 0.8, "type", 0.6)


def shot_act(c, t, fxd):
    black(c, (0.012, 0.014, 0.018))
    typed(c, "ACT I", W / 2, lerp(300, 215, eio(seg(t, T_BENCHW - 0.3, T_BENCHW + 0.2))), 34, seg(t, T0 + 0.05, T0 + 0.4), MONO, HOT, 1, t, False, "center", 16, True)
    # ano rolando 2026 -> 2022
    u = eio(seg(t, T_REW, T_REW + 1.3))
    yv = 2026 - 4 * u
    a = seg(t, T0, T0 + 0.3)
    sc = 1 - 0.35 * eio(seg(t, T_BENCHW - 0.3, T_BENCHW + 0.2))
    yy = lerp(560, 440, eio(seg(t, T_BENCHW - 0.3, T_BENCHW + 0.2)))
    c.save()
    c.translate(W / 2, yy)
    c.scale(sc, sc)
    font(c, SERIF, 260)
    dw = c.text_extents("0").x_advance
    x0 = -dw * 2
    for i, ch in enumerate("202"):
        text(c, ch, x0 + i * dw + dw / 2, 0, 260, SERIF, WHITE, a, "center")
    wheel(c, x0 + 3 * dw, 0, 260, 2 + (yv - 2022), SERIF, WHITE, a)
    c.restore()
    a2 = seg(t, T_BENCHW - 0.05, T_BENCHW + 0.35)
    sp = lerp(36, 6, eout(seg(t, T_BENCHW - 0.05, T_BENCHW + 1.1)))
    text(c, "THE BENCH", W / 2, 640, 150, SERIF, WHITE, a2, "center", sp)
    lw = 420 * eout(seg(t, T_BENCHW + 0.3, T_BENCHW + 1.0))
    c.rectangle(W / 2 - lw, 690, 2 * lw, 3)
    rgb(c, HOT, 0.9)
    c.fill()
    typed(c, "OLD TRAFFORD  ·  MANCHESTER  ·  19.10.2022", W / 2, 770, 28, seg(t, T_BENCHW + 0.8, T_BENCHW + 1.9),
          MONO, GREY, 1, t, False, "center", 6)
    fxd["fade"] = seg(t, T_END - 0.6, T_END)


# ═════════════════════════════ montagem ═════════════════════════════
SHOTS = [
    (0.0, A_END, board_A),
    (B1, B2, shot_fly),
    (B2, B3, shot_planes),
    (B3, B4, shot_laser),
    (B4, B_END, shot_control),
    (C0, C_END, shot_trophy),
    (D0, D_END, board_D),
    (E0, E_END, shot_today),
    (F0, F_END, board_F),
    (H0, H_END, shot_records),
    (I0, I_END, board_I),
    (J0, J_END, shot_title),
    (K0, K_END, shot_profile),
    (L0, L_END, shot_billboards),
    (M0, M_END, shot_crt),
    (N0, N_END, shot_adored),
    (O0, T_CHILD - 0.12, shot_share),
    (T_CHILD - 0.12, P_END, shot_lost),
    (Q0, Q_END, shot_burn),
    (R0, R_END, shot_center),
    (S0, S_END, shot_look),
    (T0, T_END, shot_act),
]
CUTS = [s[0] for s in SHOTS[1:]]


def fx_at(t):
    fl = sum(a * math.exp(-(t - ti) * d) for ti, a, d in FLASH if 0 <= t - ti < 0.8)
    ca = sum(px * math.exp(-(t - ti) * 7) for ti, px in CA if 0 <= t - ti < 0.6)
    gl = max([g for a, b, g in GLITCH if a <= t < b] or [0])
    return {"flash": min(0.85, fl), "ca": ca, "glitch": gl}


def frame(i):
    t = i / FPS
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    fxd = fx_at(t)
    fn = SHOTS[-1][2]
    for a, b, f in SHOTS:
        if a <= t < b:
            fn = f
            break
    fn(c, t, fxd)
    # corte: 2 quadros de "respiro" escuro em cortes secos fortes
    return post(s, i, fxd)
