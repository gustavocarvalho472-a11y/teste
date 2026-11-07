"""Vídeo completo: Cristiano Ronaldo Became Homelander (Beyond Success)."""
"""Amostra v2 — estilo documentário de futebol (Beyond Success), narração fiel ao roteiro.
Gancho com memes → título → quem é o Homelander (telas divididas) → Ato I (túnel de Old Trafford)."""
import json
import math
import os
import random

import cairo

import doc
from doc import (DISPLAY, GREY, LIME, UI, WHITE, act_card, bars, clip, dim, logo_bug, lower_third, meme, paint_img,
                 phone_frame, photo, quote, score_bug, split, year_tag)
from fx import FPS, H, W, clamp, eio, eout, ein, font, lerp, pulse, rgb, seg, surf, text, text_width
from fx import SERIF
from doc import DARK

HERE = os.path.dirname(os.path.abspath(__file__))
TM = json.load(open(os.path.join(HERE, "narr", "fiel", "timing.json")))
LN = {l["id"]: l for l in TM["lines"]}


def S(i):
    return LN[i]["start"]


def E(i):
    return LN[i]["end"]


def wd(lid, word, occ=0):
    k = 0
    for w, a, b in LN[lid]["words"]:
        ww = "".join(ch for ch in w.lower() if ch.isalnum())
        if ww.startswith(word.lower()):
            if k == occ:
                return a
            k += 1
    raise KeyError((lid, word))


TOTAL = 999.0   # recalculado no fim do Ato I
CUES = []      # (t, som, ganho, pan)
CLIPA = []     # (t, trecho_audio, ganho, fade_in, fade_out, dur, src_offset)
MUSIC = []     # (t0, t1, faixa, src0, ganho, fade_in, fade_out)
SILENCE = []
FLASH = []


def cue(t, n, g=1.0, p=0.0):
    CUES.append((round(t, 3), n, g, p))


def clipa(t, name, g=1.0, fi=0.15, fo=0.4, dur=None, off=0.0):
    CLIPA.append((t, name, g, fi, fo, dur, off))


SHOTS = []


def shot(t0, t1, logo=True):
    def deco(fn):
        SHOTS.append((t0, t1, fn, logo))
        return fn
    return deco


# ═══════════════ GANCHO: o meme dos olhares ═══════════════
T_BELOW = wd("H01", "below")
T_SAME1 = wd("H01", "same")
T_SAME2 = wd("H01", "same", 1)
T_OF = wd("H01", "of")
H02a = S("H02")
T_MOST = wd("H02", "most")
T_NO = wd("H02", "no")
MEMES = ["m3", "m2", "m6", "m8", "m10", "m5", "m4"]
M_T0, M_T1 = H02a - 0.08, T_NO - 0.85
M_TIMES = [M_T0 + i * 0.6 for i in range(6)] + [M_T0 + 3.6]
SLOTS = [(330, 290, -5), (1590, 270, 4), (300, 805, 3), (1615, 810, -4), (720, 610, -2), (1215, 600, 3)]
for _t in M_TIMES:
    cue(_t, "whoosh_soft", 0.18)
cue(0.0, "boom_soft", 0.8)
cue(T_SAME1 - 0.15, "whoosh_soft", 0.5)
cue(T_OF - 0.2, "whoosh_soft", 0.4)
cue(T_NO + 0.05, "hit_low", 1.0)
SILENCE.append((T_NO + 0.1, S("H03") - 0.05))


def meme_cam(c, t):
    """Meme HD dos olhares com 'câmera': topo → base → inteiro."""
    bg = surf("doc/m1hd_blur")
    paint_img(c, bg, 0, 0, W, H, zoom=1.1)
    dim(c, 0.5)
    s = surf("doc/m1hd")
    iw, ih = s.get_width(), s.get_height()
    # z = zoom relativo à altura; fy = foco vertical (0 topo, 1 base)
    k0 = eio(seg(t, 2.05, 2.8))                              # meme inteiro → topo ("next to Jorge Jesus")
    k1 = eio(seg(t, T_BELOW - 0.25, T_BELOW + 0.75))       # topo → base
    k2 = eio(seg(t, T_OF - 0.35, T_OF + 0.9))               # base → inteiro
    z0 = 0.93 + 0.03 * seg(t, 0, 2.05)
    z = lerp(lerp(z0, 1.62, k0), 0.93, k2) * (1 + 0.025 * seg(t, T_OF, H02a))
    fy = lerp(lerp(lerp(0.5, 0.265, k0), 0.735, k1), 0.5, k2)
    k = H / ih * z
    w, h = iw * k, ih * k
    x = (W - w) / 2
    y = H / 2 - fy * h
    y = clamp(y, H - h, 0) if h > H else (H - h) / 2
    sc = 1 + 0.05 * (1 - eout(seg(t, 0, 0.35)))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(sc, sc)
    c.translate(-W / 2, -H / 2)
    if h <= H:
        doc.soft_shadow(c, x, y, w, h, 6, 40, 0.6)
    c.rectangle(x, y, w, h)
    c.clip()
    c.translate(x, y)
    c.scale(k, k)
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint()
    c.restore()


def eye_strips(c, t, t0, mouth):
    """Faixas espelhadas: olhar (e depois o meio sorriso) do CR7 em cima e do Homelander embaixo."""
    gap = 6
    hh = (H - gap) / 2
    u = eio(seg(t, T_SAME2 - 0.3, T_SAME2 + 0.5)) if mouth else 0
    fa = (0.318, lerp(0.60, 0.76, u))
    fb = (0.366, lerp(0.265, 0.40, u))
    zz = 1.18 + 0.05 * seg(t, t0, t0 + 4)
    paint_img(c, surf("doc/cr7jj"), 0, 0, W, hh, focus=fa, zoom=zz)
    paint_img(c, surf("doc/hl_glance"), 0, hh + gap, W, hh, focus=fb, zoom=zz)
    hw = W * eout(seg(t, t0, t0 + 0.4))
    c.rectangle(W / 2 - hw / 2, hh, hw, gap)
    rgb(c, LIME)
    c.fill()


@shot(0.0, T_SAME1 - 0.08)
def s_meme_a(c, t, fx):
    meme_cam(c, t)


@shot(T_SAME1 - 0.08, T_OF - 0.35)
def s_strips(c, t, fx):
    eye_strips(c, t, T_SAME1 - 0.08, mouth=True)


@shot(T_OF - 0.35, M_T0)
def s_meme_b(c, t, fx):
    meme_cam(c, t)


@shot(M_T0, M_T1)
def s_memes(c, t, fx):
    k = max(i for i, ti in enumerate(M_TIMES) if ti <= t + 1e-6)
    paint_img(c, surf("doc/" + MEMES[k] + "_blur"), 0, 0, W, H, zoom=1.15)
    dim(c, 0.58)
    for i in range(k + 1):
        ti = M_TIMES[i]
        s = surf("doc/" + MEMES[i])
        iw, ih = s.get_width(), s.get_height()
        big_h, small_h = (860, 400) if iw <= ih else (560, 300)
        if i < k and i < len(SLOTS):
            u = eout(seg(t, M_TIMES[i + 1], M_TIMES[i + 1] + 0.32))
            sx, sy, sr = SLOTS[i]
            cx, cy, hh, rot, dk = lerp(W / 2, sx, u), lerp(H / 2, sy, u), lerp(big_h, small_h, u), lerp(0, sr, u), 0.38 * u
        else:
            kick = 1 + 0.07 * (1 - eout(seg(t, ti, ti + 0.25)))
            cx, cy, hh, rot, dk = W / 2, H / 2, big_h * kick, 0.0, 0.0
        kk = hh / ih
        w, h = iw * kk, ih * kk
        c.save()
        c.translate(cx, cy)
        c.rotate(math.radians(rot))
        doc.soft_shadow(c, -w / 2, -h / 2, w, h, 4, spread=26, a=0.6)
        c.rectangle(-w / 2, -h / 2, w, h)
        c.clip()
        c.save()
        c.translate(-w / 2, -h / 2)
        c.scale(kk, kk)
        c.set_source_surface(s, 0, 0)
        c.get_source().set_filter(cairo.FILTER_GOOD)
        c.paint_with_alpha(seg(t, ti, ti + 0.06))
        c.restore()
        if dk > 0:
            c.set_source_rgba(0, 0, 0, dk)
            c.paint()
        c.restore()


@shot(M_T1, S("H03") - 0.1)
def s_no(c, t, fx):
    clip(c, "v10_eyes", t, M_T1, "show", zoom=(1.0, 1.06), dur=2.5)
    if t > T_NO + 0.08:
        fx["fade"] = 1.0


# ═══════════════ GANCHO: poderes, troféus e brigas ═══════════════
H3 = S("H03")
T_PLANES = wd("H03", "brings")
T_LASERS = wd("H03", "shoots")
T_BUT = wd("H03", "but")
T_AND_CR = wd("H03", "and", 0) if False else wd("H03", "cristiano") - 0.12
T_WON = wd("H03", "won")
T_SPENT = wd("H03", "spent")
T_COACH = wd("H03", "coach")
T_CLUB = wd("H03", "club")
T_EXEC = wd("H03", "executive")
T_WHO = wd("H03", "who", 1)
H3_END = S("H04") - 0.45
cue(T_LASERS, "zap_soft", 0.5)
cue(T_SPENT - 0.1, "whoosh_soft", 0.5)
cue(H3_END, "hit_low", 0.9)
SILENCE.append((H3_END + 0.05, S("H04") + 0.3))


@shot(H3 - 0.1, T_PLANES - 0.1)
def s_fly(c, t, fx):
    photo(c, "doc/ph_hero_sky", t, H3 - 0.1, zoom=(1.05, 1.22), dur=1.8, focus=(0.5, 0.75), focus1=(0.5, 0.35))
    bars(c, 1)


@shot(T_PLANES - 0.1, T_LASERS - 0.1)
def s_planes(c, t, fx):
    clip(c, "v10_room", t, T_PLANES - 0.1, "show", zoom=(1.0, 1.08), dur=1.6)


@shot(T_LASERS - 0.1, T_BUT - 0.1)
def s_lasers(c, t, fx):
    clip(c, "v10_eyes", t, T_LASERS - 0.1, "show", zoom=(1.05, 1.15), dur=2.0)


@shot(T_BUT - 0.1, T_AND_CR)
def s_control(c, t, fx):
    photo(c, "doc/ph_control", t, T_BUT - 0.1, zoom=(1.0, 1.14), dur=4.2, focus=(0.62, 0.48), focus1=(0.72, 0.45))
    bars(c, 1)


@shot(T_AND_CR, T_WON + 0.6)
def s_euro16(c, t, fx):
    clip(c, "v02_euro16", t, T_AND_CR, "warm", zoom=(1.0, 1.08), dur=2.5)


@shot(T_WON + 0.6, T_SPENT - 0.12)
def s_trophies(c, t, fx):
    photo(c, "doc/ph_trophies", t, T_WON + 0.6, zoom=(1.0, 1.1), dur=2.6, focus=(0.5, 0.45))


@shot(T_SPENT - 0.12, T_COACH - 0.15)
def s_tunnel_q(c, t, fx):
    clip(c, "v04_tunnel", t, T_SPENT - 0.12, "doc", start=4.0, zoom=(1.12, 1.16), dur=2.0, focus=(0.5, 0.45))


@shot(T_COACH - 0.15, T_CLUB - 0.1)
def s_jj(c, t, fx):
    clip(c, "v20_jesus", t, T_COACH - 0.15, "doc", zoom=(1.0, 1.05), dur=1.2)


@shot(T_CLUB - 0.1, T_WHO - 0.05)
def s_strike(c, t, fx):
    clip(c, "v09_strike", t, T_CLUB - 0.1, "doc", start=1.0, zoom=(1.15, 1.22), dur=0.9, focus=(0.4, 0.3))


@shot(T_WHO - 0.05, H3_END)
def s_wait(c, t, fx):
    clip(c, "v19_bench", t, T_WHO - 0.05, "doc", start=2.05, rate=0.6, zoom=(1.0, 1.1), dur=2.6, focus=(0.6, 0.4))
    if t > H3_END - 0.12:
        fx["fade"] = seg(t, H3_END - 0.12, H3_END)


# ═══════════════ GANCHO: a despedida de hoje ═══════════════
H4 = S("H04")
T_NOV = wd("H04", "november")
T_ANN = wd("H04", "cristiano")
T_FIVE = wd("H04", "five")
T_HAVING = wd("H04", "having")
H4_END = E("H04") + 0.15
H5 = S("H05")
T_SAID = wd("H05", "said")
T_READ = wd("H05", "reading")
T_AND5 = wd("H05", "and")
T_FOUR = wd("H05", "four")
T_TITLE = E("H05") + 0.25
cue(T_NOV - 0.1, "swell", 0.6)
cue(T_FIVE - 0.2, "whoosh_soft", 0.35)
clipa(H4_END + 0.05, "v02_captain_a", 1.0, fi=0.2, fo=0.5, dur=H5 - H4_END - 0.05)
cue(T_AND5 + 0.3, "rewind_soft", 0.7)
cue(T_TITLE - 0.05, "boom_soft", 1.0)


@shot(H3_END, T_ANN - 0.1)
def s_today(c, t, fx):
    clip(c, "v02_sad", t, H3_END + 0.2, "cold", rate=0.8, zoom=(1.05, 1.12), dur=3.5)
    dim(c, 0.45)
    a = eout(seg(t, T_NOV - 0.35, T_NOV + 0.25))
    sp = lerp(30, 6, eout(seg(t, T_NOV - 0.35, T_NOV + 1.2)))
    text(c, "NOVEMBER 5, 2026", W / 2, H / 2 + 50, 150, DISPLAY, WHITE, a, "center", sp, shadow=0.4)
    fx["fade"] = 1 - seg(t, H3_END, H3_END + 0.5)


@shot(T_ANN - 0.1, T_FIVE - 0.15)
def s_letter(c, t, fx):
    clip(c, "v02_letter", t, T_ANN - 0.1, "warm", rate=0.33, zoom=(1.0, 1.12), dur=5.5, focus=(0.5, 0.45))
    lower_third(c, t, T_ANN + 0.4, "CRISTIANO RONALDO", "FAREWELL LETTER · 05.11.2026", dur=4.2)


@shot(T_FIVE - 0.15, T_HAVING - 0.1)
def s_walkout(c, t, fx):
    clip(c, "v21_car", t, T_FIVE - 0.15, "cold", rate=0.85, zoom=(1.0, 1.06), dur=4.5)
    lower_third(c, t, T_FIVE + 0.3, "COPENHAGEN", "LEAVES THE NATIONAL TEAM CAMP · 30.09.2026", dur=3.8)


@shot(T_HAVING - 0.1, H4_END)
def s_friends(c, t, fx):
    photo(c, "doc/ph_jj_kiss", t, T_HAVING - 0.1, zoom=(1.0, 1.12), dur=4.3, focus=(0.45, 0.4), focus1=(0.42, 0.32))


@shot(H4_END, H5 - 0.08)
def s_captain(c, t, fx):
    clip(c, "v02_captain", t, H4_END, "none", zoom=(1.0, 1.0), dur=3)


@shot(H5 - 0.08, T_SAID - 0.1)
def s_goal(c, t, fx):
    clip(c, "v16_pen", t, H5 - 0.08, "doc", start=2.4, zoom=(1.0, 1.08), dur=3.4)


@shot(T_SAID - 0.1, T_READ - 0.12)
def s_goodbye(c, t, fx):
    clip(c, "v02_sad", t, T_SAID - 0.1, "cold", zoom=(1.0, 1.06), dur=3)
    bars(c, eout(seg(t, T_SAID - 0.1, T_SAID + 0.6)))


@shot(T_READ - 0.12, T_AND5 - 0.05)
def s_phone(c, t, fx):
    dim(c, 1.0, (0.03, 0.035, 0.04))
    paint_img(c, surf("doc/ph_bench_face"), 0, 0, W, H, zoom=1.2)
    dim(c, 0.82)

    def scr(c2, r):
        x, y, w, h = r
        clip(c2, "v02_letter", t, T_READ - 0.12, "warm", rate=0.4, rect=r, zoom=(1.0, 1.0), dur=2, focus=(0.42, 0.5))
    u = eout(seg(t, T_READ - 0.12, T_READ + 0.45))
    phone_frame(c, W / 2, H / 2 + 60 * (1 - u), 860, scr, a=u)


@shot(T_AND5 - 0.05, T_TITLE)
def s_rewind(c, t, fx):
    order = ["v21_car", "v20_jesus", "v09_strike", "v19_bench", "v04_tunnel"]
    seg_len = (T_FOUR - (T_AND5 - 0.05)) / len(order)
    k = int(clamp((t - (T_AND5 - 0.05)) / seg_len, 0, len(order) - 1))
    nm = order[k]
    n = doc.seg_n(nm)
    i = int((1 - ((t - (T_AND5 - 0.05)) % seg_len) / seg_len) * (n - 1))  # tocando ao contrário
    s = doc.np_surface(doc.grade(doc.seg_frame(nm, i), "cold"))
    paint_img(c, s, 0, 0, W, H, zoom=1.04)
    dim(c, 0.35)
    # linhas de "rebobinar"
    rnd = random.Random(int(t * 30))
    for _ in range(6):
        y = rnd.uniform(0, H)
        c.rectangle(0, y, W, rnd.uniform(2, 6))
        c.set_source_rgba(1, 1, 1, rnd.uniform(0.04, 0.12))
        c.fill()
    u = eio(seg(t, T_AND5, T_FOUR + 0.2))
    yr = 2026 - 4 * u
    a = seg(t, T_AND5 - 0.05, T_AND5 + 0.3)
    c.save()
    c.translate(W / 2, H / 2 + 60)
    font(c, DISPLAY, 220)
    dw = c.text_extents("0").x_advance
    x0 = -dw * 2
    for i, ch in enumerate("202"):
        text(c, ch, x0 + i * dw + dw / 2, 0, 220, DISPLAY, WHITE, a, "center", shadow=0.4)
    doc_wheel(c, x0 + 3 * dw, 0, 220, 2 + (yr - 2022), a)
    c.restore()


def doc_wheel(c, x, y, size, value, a):
    v0 = int(math.floor(value)) % 10
    fr = value - math.floor(value)
    font(c, DISPLAY, size)
    dw = c.text_extents("0").x_advance
    c.save()
    c.rectangle(x - dw * 0.1, y - size * 0.95, dw * 1.2, size * 1.15)
    c.clip()
    for d, off in ((v0, -fr), ((v0 + 1) % 10, 1 - fr)):
        text(c, str(d), x + dw / 2, y + off * size * 1.05, size, DISPLAY, LIME, a, "center", shadow=0.4)
    c.restore()


# ═══════════════ TÍTULO ═══════════════
C1 = S("C01")


@shot(T_TITLE, C1 - 0.1, logo=False)
def s_title(c, t, fx):
    clip(c, "v03_costume", t, T_TITLE, "show", rate=0.9, zoom=(1.05, 1.15), dur=4, focus=(0.6, 0.4))
    dim(c, 0.42)
    a1 = seg(t, T_TITLE, T_TITLE + 0.3)
    sp = lerp(24, 4, eout(seg(t, T_TITLE, T_TITLE + 1.1)))
    text(c, "CRISTIANO RONALDO", W / 2, H / 2 - 30, 150, DISPLAY, WHITE, a1, "center", sp, shadow=0.4)
    a2 = seg(t, T_TITLE + 0.35, T_TITLE + 0.65)
    sp2 = lerp(24, 4, eout(seg(t, T_TITLE + 0.35, T_TITLE + 1.4)))
    text(c, "BECAME HOMELANDER", W / 2, H / 2 + 130, 150, DISPLAY, LIME, a2, "center", sp2, shadow=0.4)
    s = surf("doc/logo")
    la = seg(t, T_TITLE + 1.0, T_TITLE + 1.5)
    k = 120 / s.get_width()
    c.save()
    c.translate(W / 2 - 60, H / 2 + 210)
    c.scale(k, k)
    c.set_source_surface(s, 0, 0)
    c.paint_with_alpha(la)
    c.restore()
    fx["fade"] = 1 - seg(t, T_TITLE, T_TITLE + 0.15)


# ═══════════════ QUEM É O HOMELANDER ═══════════════
T_HL = wd("C01", "homelander")
T_FLIES = wd("C01", "flies")
T_SHOOTS = wd("C01", "shoots")
T_INDES = wd("C01", "is", 1)
T_FACE = wd("C01", "and")
C2 = S("C02")
T_OFF = wd("C02", "turn")
T_ADORED = wd("C02", "and")
T_STAGE = wd("C02", "who", 1)
T_SPOT = wd("C02", "and", 1)
T_DIFF = wd("C02", "with", 1)
T_PLANE = wd("C02", "airplane")
C3 = S("C03")
T_WHICH = wd("C03", "which")
C4 = S("C04")
T_WILL = wd("C04", "will")
T_AG1 = wd("C04", "again")
T_AG2 = wd("C04", "again", 1)
T_HARD = wd("C04", "harder")
ACT1 = E("C04") + 0.35
cue(T_OFF + 0.1, "tv_off_soft", 0.8)
cue(T_PLANE + 0.05, "boom_soft", 0.9)
cue(T_WHICH - 0.1, "hit_low", 0.7)
SILENCE.append((T_WHICH - 0.05, C4 - 0.1))
cue(ACT1, "hit_low", 0.9)
cue(ACT1 + 0.05, "whoosh_soft", 0.4)
clipa(T_ADORED - 0.1, "v07_unveil_a", 0.4, dur=T_STAGE - T_ADORED, fo=0.3)
clipa(T_WILL - 0.3, "v11_cry_a", 0.3, dur=2.5, off=1.0)
clipa(T_AG2 + 0.4, "v19_bench_a", 0.35, dur=ACT1 - T_AG2 - 0.4, off=2.0)


@shot(C1 - 0.1, T_HL - 0.1)
def s_series(c, t, fx):
    clip(c, "v22_speech", t, C1 - 0.1, "show", zoom=(1.0, 1.06), dur=2.4)


@shot(T_HL - 0.1, T_FLIES - 0.1)
def s_strongest(c, t, fx):
    clip(c, "v13_walk", t, T_HL - 0.1, "show", zoom=(1.0, 1.06), dur=3.5)


@shot(T_FLIES - 0.1, T_SHOOTS - 0.1)
def s_flies2(c, t, fx):
    photo(c, "doc/ph_hero_sky", t, T_FLIES - 0.1, zoom=(1.2, 1.32), dur=1.0, focus=(0.5, 0.7), focus1=(0.5, 0.4))
    bars(c, 1)


@shot(T_SHOOTS - 0.1, T_INDES - 0.1)
def s_lasers2(c, t, fx):
    clip(c, "v10_eyes", t, T_SHOOTS - 0.1, "show", start=0.5, zoom=(1.1, 1.18), dur=2.0)


@shot(T_INDES - 0.1, T_FACE - 0.1)
def s_indes(c, t, fx):
    photo(c, "doc/ph_poster", t, T_INDES - 0.1, zoom=(1.0, 1.1), dur=2.0, focus=(0.5, 0.35))
    bars(c, 1)


@shot(T_FACE - 0.1, C2 - 0.1)
def s_billboards(c, t, fx):
    dim(c, 1.0, (0.02, 0.022, 0.03))
    z = math.exp(lerp(math.log(1.0), math.log(0.1), eio(seg(t, T_FACE + 0.3, C2 - 0.2))))
    tw, th, gap = 1920, 1080, 120
    big = surf("s_billboard")
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    n = 8
    for gx in range(-n, n + 1):
        for gy in range(-n, n + 1):
            x, y = gx * (tw + gap), gy * (th + gap)
            if abs(x) * z > W / 2 + tw * z or abs(y) * z > H / 2 + th * z:
                continue
            c.save()
            c.translate(x - tw / 2, y - th / 2)
            c.scale(tw / big.get_width(), th / big.get_height())
            c.set_source_surface(big, 0, 0)
            c.get_source().set_filter(cairo.FILTER_FAST if z < 0.3 else cairo.FILTER_GOOD)
            c.paint()
            c.restore()
    c.restore()


@shot(C2 - 0.1, T_ADORED - 0.1)
def s_cameras(c, t, fx):
    if t < T_OFF + 0.1:
        clip(c, "v22_speech", t, C2 - 0.1, "show", start=2.4, zoom=(1.0, 1.04), dur=2.5)
        return
    u = seg(t, T_OFF + 0.1, T_OFF + 0.55)
    if u >= 1:
        dim(c, 1.0)
        return
    c.push_group()
    clip(c, "v22_speech", t, C2 - 0.1, "show", start=2.4, zoom=(1.0, 1.04), dur=2.5)
    pat = c.pop_group()
    sy = lerp(1, 0.004, ein(seg(u, 0, 0.55)))
    sx = 1 - ein(seg(u, 0.55, 1.0))
    dim(c, 1.0)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(max(0.002, sx), max(0.002, sy))
    c.translate(-W / 2, -H / 2)
    c.set_source(pat)
    c.paint()
    c.restore()


def L(name, start=0.0, kind="doc", z=(1.0, 1.06), focus=(0.5, 0.45), t0=None, rate=1.0):
    return lambda c, r, t: clip(c, name, t, t0, kind, rect=r, start=start, zoom=z, dur=3.5, focus=focus, rate=rate)


@shot(T_ADORED - 0.1, T_STAGE - 0.1)
def s_adored(c, t, fx):
    t0 = T_ADORED - 0.1
    split(c, t, t0,
          lambda c2, r: clip(c2, "v16_roar", t, t0, "warm", rect=r, zoom=(1.04, 1.12), dur=3.6, focus=(0.62, 0.38)),
          lambda c2, r: clip(c2, "v13_crowd_c", t, t0, "show", rect=r, zoom=(1.0, 1.06), dur=3.6, focus=(0.5, 0.5)))


@shot(T_STAGE - 0.1, T_SPOT - 0.1)
def s_stage(c, t, fx):
    t0 = T_STAGE - 0.1
    split(c, t, t0,
          lambda c2, r: photo(c2, "doc/ph_cr7_bruno", t, t0, rect=r, zoom=(1.0, 1.08), dur=3, focus=(0.42, 0.45)),
          lambda c2, r: clip(c2, "v06_stage_c", t, t0, "show", rect=r, zoom=(1.0, 1.06), dur=3, focus=(0.40, 0.42)))


@shot(T_SPOT - 0.1, T_DIFF - 0.1)
def s_toy(c, t, fx):
    t0 = T_SPOT - 0.1
    split(c, t, t0,
          lambda c2, r: photo(c2, "doc/ph_cry_clap", t, t0, rect=r, zoom=(1.0, 1.1), dur=6, focus=(0.55, 0.4)),
          lambda c2, r: photo(c2, "doc/ph_lost_face", t, t0, rect=r, zoom=(1.15, 1.22), dur=6, focus=(0.8, 0.30)))


@shot(T_DIFF - 0.1, C3 - 0.1)
def s_plane(c, t, fx):
    clip(c, "v10_eyes_c", t, T_DIFF - 0.1, "show", rate=0.7, zoom=(1.02, 1.2), dur=4.0, focus=(0.5, 0.38))
    if t > T_PLANE:
        FL = 0.25 * math.exp(-(t - T_PLANE) * 6)
        fx["flash"] = FL
    fx["fade"] = seg(t, C3 - 0.35, C3 - 0.1) * 0.8


@shot(C3 - 0.1, T_WHICH - 0.15)
def s_fright(c, t, fx):
    photo(c, "doc/ph_forced_smile", t, C3 - 0.1, zoom=(1.0, 1.18), dur=7.2, focus=(0.5, 0.42), focus1=(0.5, 0.38))
    bars(c, 1)


@shot(T_WHICH - 0.15, C4 - 0.05)
def s_center(c, t, fx):
    dim(c, 1.0, (0.015, 0.017, 0.02))
    a = eout(seg(t, T_WHICH - 0.15, T_WHICH + 0.3))
    text(c, "NO LONGER BEING", W / 2, H / 2 - 120, 56, DISPLAY, GREY, a, "center", 10)
    tc = wd("C03", "center")
    su = ein(seg(t, tc + 0.4, C4 - 0.05))
    c.save()
    c.translate(W / 2 + 900 * su, H / 2 + 90 + 180 * su)
    c.rotate(math.radians(10 * su))
    text(c, "THE CENTER", 0, 0, 190, DISPLAY, WHITE, a * seg(t, tc - 0.25, tc + 0.1), "center", 4)
    c.restore()
    font(c, DISPLAY, 190)
    tw = text_width(c, "THE CENTER", 4)
    c.rectangle(W / 2 - tw / 2, H / 2 + 120, tw * eout(seg(t, tc - 0.1, tc + 0.4)), 8)
    rgb(c, LIME, a)
    c.fill()


@shot(C4 - 0.05, T_WILL - 0.1)
def s_calm(c, t, fx):
    photo(c, "doc/ph_bench_face", t, C4 - 0.05, zoom=(1.0, 1.12), dur=4.5, focus=(0.5, 0.4))


@shot(T_WILL - 0.1, T_AG1 - 0.08)
def s_m2022(c, t, fx):
    clip(c, "v04_tunnel_slow", t, T_WILL - 0.1, "doc", start=1.0, zoom=(1.1, 1.14), dur=2.5, focus=(0.52, 0.45))
    year_tag(c, t, T_WILL, T_AG1 - 0.08, "2022", "OLD TRAFFORD")


@shot(T_AG1 - 0.08, T_AG2 - 0.08)
def s_m2025(c, t, fx):
    clip(c, "v11_cry", t, T_AG1 - 0.08, "doc", start=2.0, zoom=(1.25, 1.3), dur=0.6, focus=(0.47, 0.42))
    year_tag(c, t, T_AG1 - 0.05, T_AG2 - 0.08, "2025", "DUBLIN")


@shot(T_AG2 - 0.08, ACT1)
def s_m2026(c, t, fx):
    clip(c, "v19_bench", t, T_AG2 - 0.08, "fall", start=2.0, rate=0.5, zoom=(1.05, 1.22), dur=3.2, focus=(0.62, 0.36))
    year_tag(c, t, T_AG2 - 0.05, T_HARD + 0.3, "2026", "OSLO")
    bars(c, eio(seg(t, T_HARD - 0.2, T_HARD + 0.8)))


# ═══════════════ ATO I ═══════════════
A1 = S("A101")
T_OLD = wd("A101", "old")
A2 = S("A102")
T_CR_A2 = wd("A102", "and")
A3 = S("A103")
T_REF = wd("A103", "ronaldo")
T_GOT = wd("A103", "got")
A3_END = E("A103")
cue(T_GOT - 0.6, "riser_soft", 0.6)
T_SKY = A3_END + 0.25
clipa(A1 - 1.5, "v19_bench_a", 0.16, fi=1.2, fo=1.0, dur=T_SKY - A1 + 1.6)
clipa(T_SKY, "v04_tunnel_a", 1.0, fi=0.05, fo=0.5, dur=3.55)
SILENCE.append((T_GOT - 0.1, S("A104") - 0.3))


@shot(ACT1, A1 - 0.1, logo=False)
def s_act1(c, t, fx):
    clip(c, "v04_tunnel", t, ACT1, "fall", start=8.0, zoom=(1.2, 1.25), dur=2.0)
    act_card(c, t, ACT1, A1 + 0.3, 0, "THE BENCH", "OLD TRAFFORD · MANCHESTER · OCTOBER 2022")


@shot(A1 - 0.1, A2 - 0.1)
def s_a101(c, t, fx):
    photo(c, "doc/ph_utd_jacket", t, A1 - 0.1, zoom=(1.0, 1.1), dur=6.5, focus=(0.5, 0.36), focus1=(0.5, 0.3))
    lower_third(c, t, T_OLD - 0.2, "OLD TRAFFORD", "MANCHESTER UNITED vs TOTTENHAM · 19.10.2022", dur=4.0)


@shot(A2 - 0.1, T_CR_A2 - 0.1)
def s_a102(c, t, fx):
    photo(c, "doc/ph_tenhag_side", t, A2 - 0.1, zoom=(1.0, 1.1), dur=6.5, focus=(0.45, 0.4))
    score_bug(c, t, A2 + 1.0, A3 + 0.5, "MUN", 2, "TOT", 0, "2H")


T_WATCH = wd("A102", "was")


@shot(T_CR_A2 - 0.1, T_WATCH - 0.1)
def s_prodigal(c, t, fx):
    photo(c, "doc/ph_utd_arms", t, T_CR_A2 - 0.1, zoom=(1.0, 1.1), dur=5.0, focus=(0.5, 0.4))


@shot(T_WATCH - 0.1, A3 - 0.1)
def s_bench2(c, t, fx):
    photo(c, "doc/ph_utd_hips", t, T_WATCH - 0.1, zoom=(1.0, 1.12), dur=3.5, focus=(0.6, 0.35))


@shot(A3 - 0.1, T_GOT - 0.15)
def s_refused(c, t, fx):
    photo(c, "doc/ph_tunnel_photo", t, A3 - 0.1, zoom=(1.0, 1.1), dur=6, focus=(0.55, 0.5))


@shot(T_GOT - 0.15, T_SKY + 3.55)
def s_tunnel(c, t, fx):
    clip(c, "v04_tunnel_slow", t, T_GOT - 0.15, "fall", rate=0.85, zoom=(1.0, 1.18), dur=8, focus=(0.5, 0.45),
         focus1=(0.52, 0.42))
    bars(c, eio(seg(t, T_GOT, T_GOT + 1.0)))
    score_bug(c, t, T_GOT + 0.3, T_SKY + 3.4, "MUN", 2, "TOT", 0, "89'")


# ═════════════════════════════════════════════════════════════════════════════════════════════
#  VÍDEO COMPLETO — do Piers Morgan até a tela final (anexado à timeline da amostra por make_video.py)
# ═════════════════════════════════════════════════════════════════════════════════════════════
OVER = []   # (t0, t1, fn(c, t)) — grafismos por cima dos planos


def _ph(name):
    for cand in ("ph_" + name, name):
        if os.path.exists(os.path.join(HERE, "cache", "doc", cand + ".png")):
            return "doc/" + cand
    raise FileNotFoundError(name)


def over(t0, t1):
    def deco(fn):
        OVER.append((t0, t1, fn))
        return fn
    return deco


def cut(t0, t1, fn, logo=True):
    SHOTS.append((t0, t1, fn, logo))


def fr(lid, f):
    return S(lid) + f * (E(lid) - S(lid))


def CL(name, kind="doc", start=0.0, rate=1.0, z=(1.0, 1.08), focus=(0.5, 0.45), focus1=None, b=0.0, dv=0.0):
    def mk(t0, t1):
        d = max(1.0, t1 - t0)

        def fn(c, t, fx):
            clip(c, name, t, t0, kind, rate=rate, start=start, zoom=z, dur=d, focus=focus, focus1=focus1)
            if dv:
                dim(c, dv)
            if b:
                bars(c, b)
        return fn
    return mk


def PH(name, z=(1.0, 1.1), focus=(0.5, 0.45), focus1=None, b=0.0, dv=0.0):
    def mk(t0, t1):
        d = max(1.0, t1 - t0)

        def fn(c, t, fx):
            photo(c, _ph(name), t, t0, zoom=z, dur=d, focus=focus, focus1=focus1)
            if dv:
                dim(c, dv)
            if b:
                bars(c, b)
        return fn
    return mk


def POST(name, h=900):
    """foto pequena/baixa resolução: enquadrada no centro sobre a própria versão desfocada"""
    def mk(t0, t1):
        def fn(c, t, fx):
            s = surf(_ph(name))
            paint_img(c, s, 0, 0, W, H, zoom=1.25)
            dim(c, 0.72)
            iw, ih = s.get_width(), s.get_height()
            k = min(h / ih, W * 0.8 / iw) * (1 + 0.05 * seg(t, t0, t1))
            w, hh = iw * k, ih * k
            doc.soft_shadow(c, (W - w) / 2, (H - hh) / 2, w, hh, 6, 40, 0.7)
            paint_img(c, s, (W - w) / 2, (H - hh) / 2, w, hh)
        return fn
    return mk


def SP(left, right, labels=("CRISTIANO RONALDO", "HOMELANDER")):
    """left/right: ('clip', nome, grade, kwargs) ou ('photo', nome, kwargs)"""
    def mk(t0, t1):
        d = max(1.0, t1 - t0)

        def side(spec):
            if spec[0] == "clip":
                _, nm, kind, kw = spec
                return lambda c2, r, t: clip(c2, nm, t, t0, kind, rect=r, dur=d, **kw)
            _, nm, kw = spec
            return lambda c2, r, t: photo(c2, _ph(nm), t, t0, rect=r, dur=d, **kw)
        Lf, Rf = side(left), side(right)

        def fn(c, t, fx):
            split(c, t, t0, lambda c2, r: Lf(c2, r, t), lambda c2, r: Rf(c2, r, t), labels=labels)
        return fn
    return mk


def ACT(idx, title, sub, bg):
    def mk(t0, t1):
        inner = bg(t0, t1)

        def fn(c, t, fx):
            inner(c, t, fx)
            act_card(c, t, t0, t1 + 0.35, idx, title, sub)
        return fn
    return mk


def SEQ(points, makers, logo=True):
    for (a, b), mk in zip(zip(points, points[1:]), makers):
        cut(a, b, mk(a, b), logo)


# ── grafismos ──────────────────────────────────────────────────────────────────────────────────
def subtitle(c, t, t0, t1, s, y=H - 120):
    if not (t0 <= t <= t1):
        return
    a = seg(t, t0, t0 + 0.12) * (1 - seg(t, t1 - 0.12, t1))
    font(c, UI, 40, True)
    tw = text_width(c, s)
    doc.rrect(c, W / 2 - tw / 2 - 22, y - 44, tw + 44, 62, 8)
    c.set_source_rgba(0, 0, 0, 0.72 * a)
    c.fill()
    text(c, s, W / 2, y, 40, UI, WHITE, a, "center", 0, bold=True)


def big_number(c, t, t0, t1, value, label, x=W / 2, y=H / 2 + 60, size=260, prefix="", suffix="", col=WHITE,
               lab_col=LIME, count=0.9):
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.3)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    v = int(round(value * eout(seg(t, t0, t0 + count)))) if count else value
    text(c, f"{prefix}{v:,}{suffix}", x, y, size, DISPLAY, col, a, "center", 2, shadow=0.45)
    text(c, label, x, y + 70, 34, UI, lab_col, a, "center", 6, bold=True, shadow=0.5)


def red_card(c, t, t0, t1, x, y, h=300):
    if not (t0 <= t <= t1):
        return
    a = 1 - eio(seg(t, t1 - 0.3, t1))
    u = eout(seg(t, t0, t0 + 0.35))
    w = h * 0.68
    c.save()
    c.translate(x, y)
    c.rotate(math.radians(lerp(-25, 8, u)))
    c.scale(lerp(1.6, 1.0, u), lerp(1.6, 1.0, u))
    doc.soft_shadow(c, -w / 2, -h / 2, w, h, 12, 30, 0.6 * a)
    doc.rrect(c, -w / 2, -h / 2, w, h, 12)
    c.set_source_rgba(0.86, 0.1, 0.12, a * u)
    c.fill()
    c.restore()


def plan_card(c, t, t0, t1, crossed_at=None):
    """O plano de setembro: jogo 1 (Gales) e jogo 2 (Noruega); o segundo vira X quando ele não entra."""
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.35)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    dim(c, 0.55 * a)
    text(c, "THE PLAN", W / 2, 330, 46, DISPLAY, LIME, a, "center", 14)
    rows = [("GAME 1", "PORTUGAL vs WALES", "PLAYS"), ("GAME 2", "NORWAY vs PORTUGAL", "PLAYS")]
    for i, (g, m, s) in enumerate(rows):
        y = 470 + i * 150
        ra = a * seg(t, t0 + 0.25 + i * 0.35, t0 + 0.55 + i * 0.35)
        doc.rrect(c, W / 2 - 520, y - 62, 1040, 110, 10)
        c.set_source_rgba(0.06, 0.07, 0.08, 0.85 * ra)
        c.fill()
        text(c, g, W / 2 - 480, y + 12, 34, UI, GREY, ra, "left", 3, bold=True)
        text(c, m, W / 2 - 300, y + 14, 46, DISPLAY, WHITE, ra, "left", 2)
        x_ok = crossed_at is not None and i == 1 and t >= crossed_at
        cx, cy = W / 2 + 430, y - 6
        if x_ok:
            u = eout(seg(t, crossed_at, crossed_at + 0.3))
            c.set_line_width(12)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            for s1, s2 in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
                c.move_to(cx + 34 * s1[0], cy + 34 * s1[1])
                c.line_to(cx + 34 * lerp(s1[0], s2[0], u), cy + 34 * lerp(s1[1], s2[1], u))
            c.set_source_rgba(0.95, 0.2, 0.2, ra)
            c.stroke()
        else:
            c.set_line_width(12)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(cx - 32, cy)
            c.line_to(cx - 8, cy + 26)
            c.line_to(cx + 36, cy - 30)
            rgb(c, LIME, ra)
            c.stroke()


def statement(c, t, t0, t1, hl_at):
    """Comunicado do jogador (texto reconstituído a partir do roteiro), com o trecho Pelé/Maradona marcado."""
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.4)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    dim(c, 0.7 * a)
    pw, ph = 1100, 760
    x0, y0 = (W - pw) / 2, (H - ph) / 2 + 30 * (1 - eout(seg(t, t0, t0 + 0.5)))
    doc.soft_shadow(c, x0, y0, pw, ph, 6, 40, 0.6 * a)
    pat = cairo.SurfacePattern(surf("paper"))
    pat.set_extend(cairo.EXTEND_REPEAT)
    c.save()
    c.rectangle(x0, y0, pw, ph)
    c.clip()
    c.set_source(pat)
    c.paint_with_alpha(a)
    c.restore()
    ink = (0.1, 0.1, 0.1)
    text(c, "STATEMENT", x0 + 70, y0 + 100, 54, DISPLAY, ink, a, "left", 6)
    text(c, "CRISTIANO RONALDO · 06.10.2026", x0 + 72, y0 + 145, 24, UI, (0.35, 0.35, 0.35), a, "left", 2, bold=True)
    lines = ["It was agreed that the coach would open",
             "the press conference by reading points",
             "approved by me. One of them said he had",
             "been wrong to have someone of the stature",
             "of Pelé or Maradona warm up",
             "and not come on."]
    for i, ln in enumerate(lines):
        y = y0 + 250 + i * 66
        la = a * seg(t, t0 + 0.3 + i * 0.12, t0 + 0.6 + i * 0.12)
        if i in (3, 4) and t >= hl_at:
            font(c, SERIF, 44)
            tw = text_width(c, ln if i == 4 else "someone of the stature")
            xs = x0 + 70 if i == 4 else x0 + 70 + text_width(c, "been wrong to have ")
            u = eout(seg(t, hl_at + i * 0.25 - 0.75, hl_at + i * 0.25 - 0.35))
            c.rectangle(xs - 6, y - 38, (tw + 12) * u, 52)
            c.set_source_rgba(LIME[0], LIME[1], LIME[2], 0.85 * la)
            c.fill()
        text(c, ln, x0 + 70, y, 44, SERIF, ink, la, "left")


def insta_post(c, t, t0, t1):
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.35)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    dim(c, 0.6 * a)

    def scr(c2, r):
        x, y, w, h = r
        c2.set_source_rgb(0, 0, 0)
        c2.paint()
        c2.arc(x + w * 0.12, y + h * 0.08, w * 0.06, 0, 2 * math.pi)
        c2.set_source_rgb(0.3, 0.3, 0.32)
        c2.fill()
        text(c2, "cristiano", x + w * 0.22, y + h * 0.09, w * 0.06, UI, WHITE, 1, "left", bold=True)
        msg = ["In due course, I will tell", "all the Portuguese people", "the truth about the reasons",
               "that led me to leave", "the national team."]
        for i, ln in enumerate(msg):
            text(c2, ln, x + w / 2, y + h * 0.36 + i * w * 0.095, w * 0.064, UI, WHITE,
                 seg(t, t0 + 0.4 + i * 0.15, t0 + 0.7 + i * 0.15), "center", bold=True)
        text(c2, "♥  12.3M", x + w * 0.08, y + h * 0.9, w * 0.055, UI, WHITE, 1, "left", bold=True)
    doc.phone_frame(c, W / 2, H / 2 + 40 * (1 - eout(seg(t, t0, t0 + 0.4))), 880, scr, a=a)


def homelando(c, t, t0, t1):
    """RONALDO + HOMELANDER → HOMELANDO."""
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.3)) * (1 - eio(seg(t, t1 - 0.3, t1)))
    dim(c, 0.55 * a)
    m = eio(seg(t, t0 + 0.9, t0 + 1.6))
    text(c, "RONALDO", W / 2, lerp(H / 2 - 120, H / 2 + 60, m), 120, DISPLAY, WHITE, a * (1 - m), "center", 8)
    text(c, "HOMELANDER", W / 2, lerp(H / 2 + 60, H / 2 + 60, m), 120, DISPLAY, WHITE, a * (1 - m), "center", 8)
    if m > 0:
        sp = lerp(30, 8, eout(seg(t, t0 + 1.2, t0 + 2.2)))
        text(c, "HOMELANDO", W / 2, H / 2 + 60, 190, DISPLAY, LIME, a * m, "center", sp, shadow=0.5)


def subscribe_card(c, t, t0, t1, line2=""):
    if not (t0 <= t <= t1):
        return
    a = eout(seg(t, t0, t0 + 0.4)) * (1 - eio(seg(t, t1 - 0.35, t1)))
    dim(c, 0.6 * a)
    s = surf("doc/logo")
    k = 210 / s.get_width()
    sc = 1 + 0.06 * (1 - eout(seg(t, t0, t0 + 0.5)))
    c.save()
    c.translate(W / 2, H / 2 - 120)
    c.scale(k * sc, k * sc)
    c.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    c.paint_with_alpha(a)
    c.restore()
    done = t > t0 + 1.6
    bw, bh = 420, 92
    doc.rrect(c, W / 2 - bw / 2, H / 2 + 50, bw, bh, 12)
    if done:
        c.set_source_rgba(0.13, 0.14, 0.15, a)
    else:
        rgb(c, LIME, a)
    c.fill()
    text(c, "SUBSCRIBED" if done else "SUBSCRIBE", W / 2, H / 2 + 111, 50, DISPLAY, WHITE if done else DARK, a,
         "center", 4)
    if line2:
        text(c, line2, W / 2, H / 2 + 230, 34, UI, WHITE, a * seg(t, t0 + 0.6, t0 + 1.0), "center", 1, bold=True)


# ═══════════════ ATO I (continuação): Piers Morgan, Starlight, Ten Hag ═══════════════
T_PIERS = S("A104")
T_WITHIN = wd("A104", "within")
T_BETR = E("A104") + 0.45
SEQ([T_SKY + 3.55, T_WITHIN - 0.1, T_BETR - 0.05, S("A105") - 0.1],
    [CL("v05_talk", "doc", start=5.0, z=(1.28, 1.34), focus=(0.42, 0.28)),
     PH("utd_hips", z=(1.0, 1.08), focus=(0.6, 0.35), dv=0.25),
     CL("v05_talk", "doc", start=1.85, z=(1.3, 1.34), focus=(0.42, 0.28))])
clipa(T_BETR, "v05_q_a", 1.0, fi=0.03, fo=0.1, dur=1.6)
CUE_SUB = []


@over(T_PIERS + 0.3, T_PIERS + 4.3)
def _o1(c, t):
    lower_third(c, t, T_PIERS + 0.3, "PIERS MORGAN UNCENSORED", "TALKTV · NOVEMBER 2022", dur=4.0)


@over(T_WITHIN, T_BETR - 0.1)
def _o2(c, t):
    a = eout(seg(t, T_WITHIN, T_WITHIN + 0.3)) * (1 - eio(seg(t, T_BETR - 0.4, T_BETR - 0.1)))
    text(c, "CONTRACT TERMINATED", 640, H / 2, 110, DISPLAY, WHITE, a, "center", 4, shadow=0.5)
    text(c, "BY MUTUAL AGREEMENT · 22.11.2022", 640, H / 2 + 60, 30, UI, LIME, a, "center", 4, bold=True)


@over(T_BETR, T_BETR + 1.65)
def _o3(c, t):
    subtitle(c, t, T_BETR, T_BETR + 1.65, "“Yes, I feel betrayed.”")


# Starlight
T_DECIDES = wd("A105", "decides")
T_HEROINE = wd("A105", "heroine")
T_LOVE = E("A105") + 0.3
T_ACCEPTS = wd("A106", "accepts")
T_BECAUSE = wd("A106", "because")
SEQ([S("A105") - 0.1, T_DECIDES - 0.1, T_HEROINE - 0.1, T_LOVE - 0.05, T_ACCEPTS - 0.1, T_BECAUSE - 0.1,
     S("A107") - 0.1],
    [PH("seven", z=(1.0, 1.1), focus=(0.5, 0.4)),
     PH("hl_star_couch", z=(1.05, 1.15), focus=(0.5, 0.45)),
     CL("v06_full", "show", start=7.0, z=(1.0, 1.06), focus=(0.42, 0.45)),
     CL("v06_full", "show", start=0.0, z=(1.0, 1.04), focus=(0.42, 0.45)),
     PH("forced_smile", z=(1.0, 1.12), focus=(0.5, 0.4), b=1.0),
     PH("bench_face", z=(1.0, 1.14), focus=(0.5, 0.38))])
clipa(T_LOVE, "v06_q_a", 1.0, fi=0.03, fo=0.2, dur=4.1)


@over(T_LOVE, T_LOVE + 4.0)
def _o4(c, t):
    subtitle(c, t, T_LOVE, T_LOVE + 4.0, "“Starlight and I are in love.”")


# Ten Hag
T_TH = S("A107")
T_USED = wd("A107", "used")
T_SAID = wd("A107", "said")
ACT2 = E("A107") + 0.25
SEQ([S("A107") - 0.1, T_USED - 0.1, ACT2],
    [PH("tenhag_side", z=(1.0, 1.1), focus=(0.62, 0.4)),
     PH("tenhag_side", z=(1.12, 1.2), focus=(0.7, 0.38), dv=0.2)])


@over(T_TH + 0.5, T_TH + 4.6)
def _o5(c, t):
    lower_third(c, t, T_TH + 0.5, "ERIK TEN HAG", "INTERVIEW WITH THE ATHLETIC · 20.10.2026", dur=4.1)


@over(T_SAID - 0.1, ACT2)
def _o6(c, t):
    quote(c, t, T_SAID - 0.1, ACT2, ["He let the team down,", "and he let me down,", "because we planned with him."],
          "ERIK TEN HAG · THE ATHLETIC", size=64)


# ═══════════════ ATO II: a greve ═══════════════
A2S = S("A201")
T_WHERE = wd("A201", "where")
T_AND21 = wd("A201", "and")
T_SIGNED = wd("A202", "signed")
T_CONCL = wd("A202", "cristiano")
T_STOP = S("A203")
T_SKY2 = E("A203") + 0.3
T_WHILE = wd("A204", "while")
T_SAUDI = wd("A204", "saudi")
SEQ([ACT2, A2S - 0.1, T_WHERE - 0.1, T_AND21 - 0.1, S("A202") - 0.1, T_SIGNED - 0.1, T_CONCL - 0.1, T_STOP - 0.1,
     T_SKY2 - 0.05, S("A204") - 0.1, T_WHILE - 0.1, T_SAUDI - 0.1, S("A205") - 0.1, S("A206") - 0.1],
    [ACT(1, "THE STRIKE", "RIYADH · 2023 – 2026", CL("v07_arch", "doc", start=0.5, z=(1.05, 1.1))),
     CL("v07_unveil", "punch", start=0.0, z=(1.2, 1.3), focus=(0.45, 0.42)),
     CL("v07_arch", "warm", start=0.0, z=(1.0, 1.08)),
     PH("alnassr_pen", z=(1.0, 1.1), focus=(0.45, 0.4)),
     PH("alnassr_frus", z=(1.0, 1.1), focus=(0.55, 0.35), dv=0.15),
     CL("v08_benz", "doc", start=0.0, z=(1.0, 1.05)),
     PH("alnassr_frus", z=(1.15, 1.25), focus=(0.55, 0.32), dv=0.62),
     PH("alnassr_gesture", z=(1.0, 1.12), focus=(0.5, 0.35), b=1.0),
     CL("v09_quote", "doc", start=0.05, z=(1.0, 1.04)),
     CL("v09_strike", "doc", start=0.0, z=(1.1, 1.18), focus=(0.4, 0.3), dv=0.65),
     PH("alnassr_frus", z=(1.0, 1.08), focus=(0.55, 0.35)),
     CL("v09_strike", "doc", start=2.0, z=(1.0, 1.06)),
     PH("alnassr_pen", z=(1.05, 1.15), focus=(0.45, 0.38))])
clipa(T_SKY2, "v09_q_a", 1.0, fi=0.03, fo=0.2, dur=5.5)
SILENCE.append((T_STOP - 0.15, T_SKY2 - 0.05))
cue(ACT2, "hit_low", 0.9)
cue(T_STOP - 0.1, "hit_low", 0.6)


@over(T_SIGNED, T_CONCL - 0.1)
def _o7(c, t):
    lower_third(c, t, T_SIGNED, "KARIM BENZEMA", "SIGNS FOR AL HILAL · FEBRUARY 2026", dur=T_CONCL - T_SIGNED - 0.1)


@over(T_CONCL - 0.1, T_STOP - 0.1)
def _o8(c, t):
    a = eout(seg(t, T_CONCL - 0.1, T_CONCL + 0.3)) * (1 - eio(seg(t, T_STOP - 0.4, T_STOP - 0.1)))
    text(c, "PIF", W / 2, H / 2 + 30, 170, DISPLAY, WHITE, a, "center", 10, shadow=0.5)
    text(c, "PUBLIC INVESTMENT FUND", W / 2, H / 2 + 80, 26, UI, GREY, a, "center", 5, bold=True)
    clubs = [("AL HILAL", -560, -260), ("AL NASSR", 560, -260), ("AL ITTIHAD", -560, 300), ("AL AHLI", 560, 300)]
    for i, (nm, dx, dy) in enumerate(clubs):
        ca = a * seg(t, T_CONCL + 0.2 + i * 0.2, T_CONCL + 0.5 + i * 0.2)
        hot = nm == "AL HILAL" and t > T_CONCL + 1.8
        c.move_to(W / 2 + dx * 0.25, H / 2 + dy * 0.25)
        c.line_to(W / 2 + dx * 0.78, H / 2 + dy * 0.78)
        rgb(c, LIME if hot else GREY, ca * (1 if hot else 0.5))
        c.set_line_width(6 if hot else 3)
        c.stroke()
        text(c, nm, W / 2 + dx, H / 2 + dy + 20, 62, DISPLAY, LIME if hot else WHITE, ca, "center", 3, shadow=0.5)


@over(T_SKY2, T_SKY2 + 5.5)
def _o9(c, t):
    subtitle(c, t, T_SKY2, T_SKY2 + 5.5, "“...did not feature in Al-Nassr's victory against Al-Riyadh last night.”")


@over(S("A204") + 0.3, T_WHILE - 0.15)
def _o10(c, t):
    big_number(c, t, S("A204") + 0.3, T_WHILE - 0.15, 3, "GAMES MISSED · NO INJURY", y=H / 2 + 40, count=0.6)


# Stormfront
T_HEROINE2 = wd("A206", "heroine")
T_MOST2 = wd("A206", "most")
ACT3 = E("A206") + 0.25
SEQ([S("A206") - 0.1, T_HEROINE2 - 0.1, T_MOST2 - 0.1, ACT3],
    [PH("seven", z=(1.1, 1.2), focus=(0.4, 0.4), dv=0.1),
     CL("v10_storm", "show", start=0.0, rate=0.8, z=(1.0, 1.06)),
     SP(("photo", "alnassr_frus", dict(zoom=(1.0, 1.08), focus=(0.55, 0.35))),
        ("clip", "v10_room", "show", dict(zoom=(1.25, 1.3), focus=(0.5, 0.42))))])


# ═══════════════ ATO III: Dublin ═══════════════
A3S = S("A301")
T_CR31 = wd("A301", "cristiano")
T_BOO = E("A301") + 0.3
T_BOO2 = T_BOO + 2.95
T_LOOKED = wd("A302", "looked")
T_FEW = wd("A302", "few")
T_VAR = wd("A303", "var")
T_FIRST = wd("A303", "first")
T_CR34 = wd("A304", "cristiano")
T_HL35 = wd("A305", "homelander")
T_APPL = wd("A305", "applauds")
SEQ([ACT3, A3S - 0.1, T_CR31 - 0.1, T_BOO - 0.05, T_BOO2 - 0.05, S("A302") - 0.1, T_LOOKED - 0.1, T_FEW - 0.1,
     S("A303") - 0.1, T_VAR - 0.1, T_FIRST - 0.1, S("A304") - 0.1, T_CR34 - 0.1, S("A305") - 0.1, T_HL35 - 0.1,
     T_APPL - 0.6, S("A306") - 0.1, S("A307") - 0.1, S("A308") - 0.1],
    [ACT(2, "THE MASK SLIPS", "DUBLIN · NOVEMBER 2025", CL("v11_off", "fall", start=10.0, z=(1.05, 1.1))),
     CL("v11_wide", "doc", start=8.0, z=(1.0, 1.06)),
     CL("v12_talk", "doc", start=0.0, z=(1.0, 1.06), focus=(0.55, 0.4)),
     CL("v12_q1", "doc", start=0.0, z=(1.0, 1.03), focus=(0.55, 0.4)),
     CL("v12_q2", "doc", start=0.0, z=(1.06, 1.09), focus=(0.55, 0.38)),
     CL("v11_wide", "doc", start=0.0, z=(1.0, 1.06)),
     CL("v11_cry", "doc", start=1.6, rate=0.6, z=(1.2, 1.3), focus=(0.47, 0.42)),
     CL("v11_elbow", "doc", start=0.0, rate=0.9, z=(1.1, 1.2), focus=(0.45, 0.45)),
     CL("v11_var", "doc", start=2.0, z=(1.0, 1.08)),
     CL("v11_var", "doc", start=6.0, z=(1.05, 1.1), dv=0.25),
     CL("v11_cry", "fall", start=2.6, rate=0.4, z=(1.3, 1.35), focus=(0.47, 0.42), dv=0.45),
     CL("v11_off", "doc", start=0.0, z=(1.0, 1.06)),
     CL("v11_off", "doc", start=15.0, rate=0.7, z=(1.1, 1.18), b=1.0),
     CL("v13_walk", "show", start=0.0, z=(1.0, 1.06)),
     CL("v13_crowd_c", "show", start=0.0, rate=0.9, z=(1.0, 1.06)),
     CL("v13_smile", "show", start=0.0, z=(1.05, 1.12)),
     CL("v11_var", "doc", start=6.0, z=(1.0, 1.06)),
     SP(("clip", "v03_grin", "warm", dict(zoom=(1.0, 1.06), focus=(0.62, 0.42))),
        ("photo", "forced_smile", dict(zoom=(1.0, 1.06), focus=(0.5, 0.42))))])
clipa(T_BOO, "v12_q1_a", 1.0, fi=0.02, fo=0.05, dur=2.9)
clipa(T_BOO2, "v12_q2_a", 1.0, fi=0.02, fo=0.15, dur=2.8)
clipa(S("A302") - 0.2, "v11_a", 0.3, fi=0.6, fo=1.0, dur=S("A305") - S("A302"))
clipa(S("A306") - 0.2, "v11_a", 0.35, fi=0.3, fo=0.6, dur=E("A306") - S("A306") + 0.4, off=30.0)
SILENCE.append((T_FIRST - 0.35, T_FIRST + 0.6))
cue(ACT3, "hit_low", 0.9)
cue(T_FIRST - 0.3, "boom_soft", 0.9)


@over(T_CR31, T_BOO - 0.1)
def _o11(c, t):
    lower_third(c, t, T_CR31, "CRISTIANO RONALDO", "PRESS CONFERENCE · DUBLIN · 12.11.2025", dur=T_BOO - T_CR31 - 0.1)


@over(T_BOO, T_BOO2 + 2.85)
def _o12(c, t):
    subtitle(c, t, T_BOO, T_BOO + 2.9, "“I hope they don't boo too much to me tomorrow.”")
    subtitle(c, t, T_BOO2, T_BOO2 + 2.85, "“I swear that I'm gonna try to be a good boy.”")


@over(S("A302"), T_LOOKED)
def _o13(c, t):
    score_bug(c, t, S("A302") + 0.2, T_LOOKED, "IRL", 2, "POR", 0, "2H")


@over(T_FIRST - 0.3, S("A304") - 0.1)
def _o14(c, t):
    red_card(c, t, T_FIRST - 0.3, S("A304") - 0.1, W / 2 - 330, H / 2 - 20)
    big_number(c, t, T_FIRST, S("A304") - 0.1, 226, "GAMES · FIRST RED CARD", x=W / 2 + 200, y=H / 2 + 40, size=240,
               count=0.9)


# inscreva-se (meio)
ACT4 = E("A308") + 0.25
SEQ([S("A308") - 0.1, ACT4],
    [CL("v19_bench", "fall", start=2.0, rate=0.5, z=(1.05, 1.15), focus=(0.62, 0.36))])


@over(S("A308") - 0.1, ACT4)
def _o15(c, t):
    subscribe_card(c, t, S("A308") - 0.1, ACT4, "THE STRANGEST PART IS STILL TO COME")


# ═══════════════ ATO IV: o cabelo branco ═══════════════
T_GOING = wd("A401", "going")
T_BEC42 = wd("A402", "because")
T_AND43 = wd("A403", "and")
T_SPENT45 = wd("A405", "spent")
T_HEARD = wd("A405", "heard")
T_EARN = fr("A405", 0.66)
T_AG47 = wd("A407", "against")
T_SPAIN = wd("A408", "spain")
T_AND48 = wd("A408", "and")
T_DALLAS_END = S("A409")
ACT5 = E("A409") + 0.25
SEQ([ACT4, S("A401") - 0.1, T_GOING - 0.1, S("A402") - 0.1, T_BEC42 - 0.1, S("A403") - 0.1, T_AND43 - 0.1,
     S("A404") - 0.1, S("A405") - 0.1, T_SPENT45 - 0.1, T_HEARD - 0.1, T_EARN - 0.1, E("A405") + 0.3,
     S("A406") - 0.1, S("A407") - 0.1, T_AG47 - 0.1, fr("A407", 0.82), S("A408") - 0.1, T_AND48 - 0.1,
     T_DALLAS_END - 0.1, ACT5],
    [ACT(3, "GREY HAIRS", "THE BODY · WORLD CUP 2026", CL("v14_face", "show", start=0.0, z=(1.0, 1.05))),
     CL("v14_hair", "show", start=0.0, z=(1.0, 1.06)),
     CL("v14_hair", "show", start=7.4, rate=0.6, z=(1.1, 1.22), focus=(0.48, 0.42)),
     CL("v14_jar", "show", start=0.0, z=(1.0, 1.06)),
     CL("v14_face", "show", start=0.0, rate=0.7, z=(1.0, 1.1)),
     CL("v02_euro16", "warm", start=0.0, z=(1.0, 1.06)),
     PH("dallas", z=(1.05, 1.15), focus=(0.55, 0.3), dv=0.2),
     PH("alnassr_gesture", z=(1.0, 1.1), focus=(0.5, 0.35)),
     PH("yellow", z=(1.0, 1.1), focus=(0.62, 0.35)),
     CL("v15_walk", "doc", start=2.5, z=(1.0, 1.08), focus=(0.5, 0.4)),
     PH("congo_head", z=(1.0, 1.1), focus=(0.4, 0.35)),
     CL("v03_costume", "show", start=0.0, z=(1.05, 1.12), focus=(0.6, 0.4)),
     POST("m5", h=900),
     CL("v16uz_goal", "doc", start=2.0, z=(1.0, 1.06)),
     CL("v16uz_goal", "doc", start=3.5, z=(1.05, 1.1)),
     CL("v16_pen", "doc", start=1.5, z=(1.0, 1.06)),
     CL("v16_roar", "warm", start=0.0, z=(1.05, 1.12), focus=(0.62, 0.38)),
     CL("v17_header", "doc", start=0.4, rate=0.75, z=(1.0, 1.08)),
     PH("dallas", z=(1.0, 1.18), focus=(0.55, 0.3), focus1=(0.55, 0.22), b=1.0),
     POST("m10", h=900)])
clipa(T_HEARD - 0.4, "v15_a", 0.55, fi=0.5, fo=1.2, dur=E("A405") - T_HEARD + 3.6)
SILENCE.append((T_AND48 - 0.1, T_DALLAS_END - 0.05))
cue(ACT4, "hit_low", 0.9)
cue(fr("A408", 0.33), "boom_soft", 0.8)
cue(T_AND48 - 0.05, "hit_low", 0.7)


@over(T_AND43 + 0.3, S("A404") - 0.15)
def _o16(c, t):
    big_number(c, t, T_AND43 + 0.3, S("A404") - 0.15, 41, "YEARS OLD", y=H / 2 + 60, size=300, count=0.7)


@over(S("A404") + 0.2, S("A405") - 0.2)
def _o17(c, t):
    lower_third(c, t, S("A404") + 0.2, "THIGH INJURY", "FEBRUARY 2026 · THREE MONTHS BEFORE THE WORLD CUP",
                dur=S("A405") - S("A404") - 0.4)


@over(S("A405"), T_HEARD - 0.1)
def _o18(c, t):
    score_bug(c, t, S("A405") + 0.2, T_HEARD - 0.1, "POR", 1, "COD", 1, "FT")
    year_tag(c, t, S("A405") + 0.2, T_SPENT45 - 0.1, "HOUSTON", "WORLD CUP 2026 · OPENER")


@over(T_EARN - 0.1, E("A405") + 0.3)
def _o19(c, t):
    homelando(c, t, T_EARN - 0.1, E("A405") + 0.3)


@over(T_AND48, T_DALLAS_END - 0.1)
def _o23(c, t):
    year_tag(c, t, T_AND48 + 0.6, T_DALLAS_END - 0.1, "DALLAS", "ROUND OF 16 · JULY 2026")


# ═══════════════ ATO V: o roteiro ═══════════════
T_SAME51 = wd("A501", "same")
T_SEPT = wd("A502", "september")
T_BEFORE = wd("A503", "before")
T_ASKED = wd("A504", "asked")
T_W1 = wd("A505", "watched")
T_W2 = wd("A505", "watched", 1)
T_DIDNT = wd("A505", "didn")
T_ONE58 = wd("A508", "one", 0)
T_SOMEONE = wd("A508", "someone")
T_JQ = E("A509") + 0.3
T_AND510 = wd("A510", "and")
T_WROTE = wd("A510", "wrote")
T_AND511 = wd("A511", "and")
T_HLQ = E("A511") + 0.3
FALL = E("A512") + 0.25
SEQ([ACT5, S("A501") - 0.1, T_SAME51 - 0.1, S("A502") - 0.1, S("A503") - 0.1, T_BEFORE - 0.1, S("A504") - 0.1,
     T_ASKED - 0.1, S("A505") - 0.1, T_W2 - 0.1, T_DIDNT - 0.1, S("A506") - 0.1, S("A507") - 0.1, S("A508") - 0.1,
     S("A509") - 0.1, T_JQ - 0.05, S("A510") - 0.1, T_AND510 - 0.1, T_WROTE - 0.1, S("A511") - 0.1, T_AND511 - 0.1,
     T_HLQ - 0.05, S("A512") - 0.1, FALL],
    [ACT(4, "THE SCRIPT", "LISBON · OSLO · COPENHAGEN · 2026", CL("v20_talk", "fall", start=0.0, z=(1.05, 1.1))),
     PH("jesus_arms", z=(1.0, 1.1), focus=(0.5, 0.35)),
     PH("jj_kiss", z=(1.0, 1.12), focus=(0.45, 0.4)),
     PH("cr7jj", z=(1.0, 1.06), focus=(0.5, 0.5), dv=0.3),
     CL("v18_off", "doc", start=0.0, z=(1.0, 1.06), focus=(0.5, 0.4)),
     PH("cr7_bruno", z=(1.0, 1.12), focus=(0.45, 0.45)),
     PH("cr7jj", z=(1.15, 1.25), focus=(0.3, 0.45)),
     PH("jesus_serious", z=(1.0, 1.08), focus=(0.5, 0.4)),
     CL("v19_bench", "doc", start=2.0, rate=0.8, z=(1.0, 1.08), focus=(0.6, 0.38)),
     CL("v19_goal", "doc", start=4.0, z=(1.0, 1.06)),
     CL("v19_bench", "fall", start=3.0, rate=0.5, z=(1.1, 1.2), focus=(0.62, 0.36)),
     CL("v19_end", "fall", start=2.0, z=(1.0, 1.08)),
     PH("cr7jj", z=(1.2, 1.3), focus=(0.32, 0.45), b=1.0, dv=0.2),
     PH("cr7jj", z=(1.0, 1.04), focus=(0.5, 0.5), dv=0.5),
     CL("v20_talk", "doc", start=4.0, z=(1.0, 1.04)),
     CL("v20_quote", "doc", start=0.1, z=(1.0, 1.05)),
     CL("v20_talk", "doc", start=0.0, z=(1.0, 1.06)),
     CL("v21_car", "cold", start=0.0, rate=0.8, z=(1.0, 1.06)),
     PH("cr7jj", z=(1.0, 1.04), focus=(0.5, 0.5), dv=0.4),
     CL("v22_prompt", "show", start=0.0, z=(1.0, 1.06)),
     CL("v22_off", "show", start=0.0, z=(1.0, 1.08)),
     CL("v22_quote", "show", start=0.1, z=(1.0, 1.04)),
     SP(("photo", "cr7jj", dict(zoom=(1.3, 1.36), focus=(0.3, 0.45))),
        ("clip", "v20_talk", "doc", dict(start=1.0, zoom=(1.0, 1.06), focus=(0.48, 0.4))),
        labels=("THE PLAYER", "THE COACH"))])
clipa(T_JQ, "v20_q_a", 1.0, fi=0.03, fo=0.2, dur=5.25)
clipa(T_HLQ, "v22_q_a", 1.0, fi=0.03, fo=0.2, dur=4.7)
clipa(S("A505") - 0.3, "v19_amb_a", 0.3, fi=0.6, fo=1.0, dur=S("A507") - S("A505"))
SILENCE.append((S("A509") - 0.3, T_JQ + 5.3))
cue(ACT5, "hit_low", 0.9)
cue(S("A509") - 0.05, "hit_low", 0.8)


@over(S("A502") - 0.1, S("A503") - 0.1)
def _o24(c, t):
    plan_card(c, t, S("A502") - 0.1, S("A503") - 0.1)


@over(S("A503") + 0.2, T_BEFORE - 0.1)
def _o25(c, t):
    score_bug(c, t, S("A503") + 0.3, T_BEFORE - 0.1, "POR", 1, "WAL", 0, "2H")


@over(T_ASKED, S("A505") - 0.1)
def _o26(c, t):
    big_number(c, t, T_ASKED + 0.2, S("A505") - 0.1, 30, "MINUTES?", y=H / 2 + 60, size=300, suffix="'", count=0.6)


@over(S("A505"), T_DIDNT - 0.1)
def _o27(c, t):
    mins = int(lerp(46, 90, seg(t, S("A505"), T_DIDNT - 0.2)))
    score_bug(c, t, S("A505") + 0.1, T_DIDNT - 0.1, "NOR", 1 if t > T_W2 else 0, "POR", 2 if t > T_W2 + 0.8 else 0,
              f"{mins}'")


@over(T_DIDNT - 0.1, S("A506") - 0.1)
def _o28(c, t):
    plan_card(c, t, T_DIDNT - 0.1, S("A506") - 0.1, crossed_at=T_DIDNT + 0.3)


@over(S("A508") - 0.1, S("A509") - 0.1)
def _o29(c, t):
    statement(c, t, S("A508") - 0.1, S("A509") - 0.1, hl_at=T_SOMEONE)


@over(T_JQ, T_JQ + 5.25)
def _o30(c, t):
    subtitle(c, t, T_JQ, T_JQ + 2.0, "“He's a Pelé, he's a Maradona...”")
    subtitle(c, t, T_JQ + 2.05, T_JQ + 5.25, "“...that's status. But the rights are the same.”")
    lower_third(c, t, T_JQ + 0.1, "JORGE JESUS", "PRESS CONFERENCE · COPENHAGEN · 30.09.2026", dur=5.0, y=200)


@over(T_WROTE - 0.1, S("A511") - 0.1)
def _o31(c, t):
    insta_post(c, t, T_WROTE - 0.1, S("A511") - 0.1)


@over(T_HLQ, T_HLQ + 4.7)
def _o32(c, t):
    subtitle(c, t, T_HLQ, T_HLQ + 4.7, "“Those who accept my truth will be welcomed into a land of milk and honey.”")


# ═══════════════ A QUEDA ═══════════════
T_WHICH1 = wd("Q01", "which")
T_LEFT4 = wd("Q04", "left")
T_WATCH4 = wd("Q04", "watched")
ENDA = E("Q04") + 0.25
SEQ([FALL, S("Q01") - 0.1, T_WHICH1 - 0.1, S("Q02") - 0.1, S("Q03") - 0.1, S("Q04") - 0.1, T_LEFT4 - 0.1,
     T_WATCH4 - 0.1, ENDA],
    [ACT(5, "THE FALL", "OCTOBER 2026", PH("cr7jj", z=(1.0, 1.05), focus=(0.4, 0.45))),
     PH("suspended", z=(1.0, 1.08), focus=(0.5, 0.4), dv=0.45),
     PH("suspended", z=(1.08, 1.15), focus=(0.5, 0.4), dv=0.2),
     POST("ph_mourinho", h=760),
     PH("tenhag_side", z=(1.0, 1.08), focus=(0.62, 0.4), dv=0.25),
     SP(("photo", "tenhag_side", dict(zoom=(1.0, 1.06), focus=(0.72, 0.4))),
        ("photo", "jesus_arms", dict(zoom=(1.0, 1.06), focus=(0.5, 0.35))),
        labels=("ERIK TEN HAG · 2022", "JORGE JESUS · 2026")),
     SP(("clip", "v04_tunnel", "fall", dict(start=0.0, zoom=(1.1, 1.15), focus=(0.52, 0.45))),
        ("clip", "v19_bench", "fall", dict(start=2.0, rate=0.6, zoom=(1.0, 1.06), focus=(0.62, 0.36))),
        labels=("2022", "2026")),
     SP(("clip", "v04_tunnel_slow", "fall", dict(start=1.0, zoom=(1.1, 1.15), focus=(0.52, 0.45))),
        ("clip", "v21_car", "fall", dict(start=0.0, rate=0.8, zoom=(1.0, 1.06))),
        labels=("2022", "2026"))])
cue(FALL, "hit_low", 0.9)


@over(S("Q01") + 0.2, T_WHICH1 - 0.1)
def _o33(c, t):
    big_number(c, t, S("Q01") + 0.2, T_WHICH1 - 0.1, 30, "DAYS SUSPENDED", x=W / 2 - 360, y=H / 2 + 40, size=240,
               count=0.7)
    big_number(c, t, S("Q01") + 1.6, T_WHICH1 - 0.1, 255, "EURO FINE", x=W / 2 + 360, y=H / 2 + 40, size=240,
               prefix="€", count=0.8)


@over(S("Q02") + 0.2, S("Q03") - 0.2)
def _o34(c, t):
    lower_third(c, t, S("Q02") + 0.2, "JOSÉ MOURINHO", "“HE NEEDS TO ADAPT TO A NEW PHASE OF HIS CAREER”",
                dur=S("Q03") - S("Q02") - 0.4)


@over(fr("Q03", 0.45), S("Q04") - 0.1)
def _o35(c, t):
    quote(c, t, fr("Q03", 0.45), S("Q04") - 0.1, ["...because we planned with him."], "ERIK TEN HAG · THE ATHLETIC",
          size=72)


# ═══════════════ FECHAMENTO ═══════════════
T_WHILE1 = wd("F01", "while")
T_TURN = wd("F01", "turn")
T_THANKS = wd("F04", "thanks")
T_WRITES = wd("F04", "writes")
T_WHICH4 = wd("F04", "which")
T_WALK4 = wd("F04", "walking")
T_IT6 = wd("F06", "it")
T_SAME6 = wd("F06", "same")
T_END = E("F09") + 0.3
TOTAL = round(T_END + 11.5, 2)


def tv_off(src_mk, t_off):
    def mk(t0, t1):
        inner = src_mk(t0, t1)

        def fn(c, t, fx):
            if t < t_off:
                inner(c, t, fx)
                return
            u = seg(t, t_off, t_off + 0.45)
            if u >= 1:
                dim(c, 1.0)
                return
            c.push_group()
            inner(c, t, fx)
            pat = c.pop_group()
            dim(c, 1.0)
            sy = lerp(1, 0.004, ein(seg(u, 0, 0.55)))
            sx = 1 - ein(seg(u, 0.55, 1.0))
            c.save()
            c.translate(W / 2, H / 2)
            c.scale(max(0.002, sx), max(0.002, sy))
            c.translate(-W / 2, -H / 2)
            c.set_source(pat)
            c.paint()
            c.restore()
        return fn
    return mk


def walk_alone(t0, t1):
    parts = [("v04_tunnel_slow", "fall", 2.0, "2022", "OLD TRAFFORD"), ("v11_off", "fall", 14.0, "2025", "DUBLIN"),
             ("v21_car", "fall", 0.5, "2026", "COPENHAGEN"), ("v19_alone", "fall", 0.0, "2026", "OSLO")]
    n = len(parts)

    def fn(c, t, fx):
        k = min(n - 1, int((t - t0) / ((t1 - t0) / n)))
        a0 = t0 + k * (t1 - t0) / n
        nm, g, st, yr, pl = parts[k]
        clip(c, nm, t, a0, g, start=st, rate=0.7, zoom=(1.05, 1.12), dur=(t1 - t0) / n)
        year_tag(c, t, a0 + 0.1, a0 + (t1 - t0) / n - 0.05, yr, pl)
    return fn


cut(ENDA, S("F01") - 0.1, ACT(6, "THE LETTER", "NOVEMBER 5, 2026", CL("v02_letter", "warm", rate=0.3, z=(1.0, 1.06)))(
    ENDA, S("F01") - 0.1), logo=False)
SEQ([S("F01") - 0.1, T_WHILE1 - 0.1, S("F02") - 0.1, S("F03") - 0.1, S("F04") - 0.1, T_THANKS - 0.1, T_WRITES - 0.1,
     T_WHICH4 - 0.1],
    [CL("v24_fall", "show", start=1.0, z=(1.0, 1.06)),
     tv_off(CL("v22_speech", "show", start=2.4, z=(1.0, 1.04)), T_TURN + 0.15),
     PH("depowered", z=(1.0, 1.1), focus=(0.5, 0.42), b=1.0),
     CL("v02_letter", "warm", rate=0.33, z=(1.0, 1.1), focus=(0.5, 0.45)),
     CL("v02_sad", "warm", rate=0.6, z=(1.05, 1.12)),
     CL("v02_staff", "warm", start=0.0, z=(1.0, 1.06)),
     CL("v02_bus", "warm", start=0.0, rate=0.8, z=(1.0, 1.06))])
cut(T_WHICH4 - 0.1, S("F05") - 0.1, walk_alone(T_WHICH4 - 0.1, S("F05") - 0.1))
SEQ([S("F05") - 0.1, S("F06") - 0.1, T_IT6 - 0.1, T_SAME6 - 0.1, S("F07") - 0.1, S("F08") - 0.1, S("F09") - 0.1, T_END],
    [PH("alnassr_pen", z=(1.0, 1.1), focus=(0.45, 0.38)),
     PH("trophies", z=(1.0, 1.08), focus=(0.5, 0.45)),
     CL("v19_bench", "fall", start=2.0, rate=0.45, z=(1.05, 1.22), focus=(0.62, 0.36), b=1.0),
     POST("m1hd", h=1000),
     CL("v24_alone", "fall", start=0.0, z=(1.0, 1.08)),
     PH("smile26", z=(1.0, 1.1), focus=(0.5, 0.35)),
     CL("v19_alone", "fall", start=0.0, rate=0.6, z=(1.05, 1.12))])
cut(T_END, TOTAL + 1, PH("cr7jj", z=(1.0, 1.04), focus=(0.5, 0.5), dv=0.6)(T_END, TOTAL), logo=False)
clipa(S("F01") - 0.2, "v24_a", 0.35, fi=0.4, fo=0.8, dur=T_WHILE1 - S("F01") + 0.3)
SILENCE.append((T_TURN + 0.1, S("F02") + 0.2))
cue(ENDA, "hit_low", 0.8)
cue(T_TURN + 0.15, "tv_off_soft", 0.8)


@over(T_WRITES + 0.2, T_WHICH4 - 0.1)
def _o36(c, t):
    a = eout(seg(t, T_WRITES + 0.2, T_WRITES + 0.6)) * (1 - eio(seg(t, T_WHICH4 - 0.4, T_WHICH4 - 0.1)))
    dim(c, 0.45 * a)
    text(c, "“NO CAPTAIN WALKS ALONE.”", W / 2, H / 2 + 30, 110, DISPLAY, WHITE, a, "center", 4, shadow=0.5)


@over(S("F05") + 0.3, S("F06") - 0.15)
def _o37(c, t):
    big_number(c, t, S("F05") + 1.6, S("F06") - 0.15, 1000, "THE CHASE GOES ON", y=H / 2 + 60, size=280, count=1.2)


@over(T_END, TOTAL)
def _o38(c, t):
    a = eout(seg(t, T_END, T_END + 0.6))
    dim(c, 0.35 * a)
    text(c, "CAN HE STILL CHANGE HOW HE'LL BE REMEMBERED?", W / 2, 190, 54, DISPLAY, WHITE, a, "center", 3, shadow=0.5)
    text(c, "TELL US IN THE COMMENTS", W / 2, 245, 26, UI, LIME, a * seg(t, T_END + 0.4, T_END + 0.9), "center", 6,
         bold=True)
    for i, x in enumerate((130, W - 130 - 620)):   # lugares dos vídeos sugeridos (elementos do YouTube)
        u = eout(seg(t, T_END + 0.5 + i * 0.15, T_END + 1.1 + i * 0.15))
        doc.rrect(c, x, 400, 620, 349, 10)
        c.set_source_rgba(0, 0, 0, 0.45 * u)
        c.fill_preserve()
        rgb(c, LIME, 0.75 * u)
        c.set_line_width(3)
        c.stroke()
        text(c, "WATCH NEXT", x + 310, 580, 30, UI, GREY, 0.8 * u, "center", 6, bold=True)
    s = surf("doc/logo")
    k = 190 / s.get_width()
    c.save()
    c.translate(W / 2, 575)
    sc = k * (1 + 0.06 * (1 - eout(seg(t, T_END + 0.3, T_END + 0.9))))
    c.scale(sc, sc)
    c.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    c.paint_with_alpha(a)
    c.restore()
    text(c, "SUBSCRIBE", W / 2, 735, 40, DISPLAY, WHITE, a, "center", 5, shadow=0.5)
    text(c, "BEYOND SUCCESS", W / 2, H - 80, 28, UI, GREY, a, "center", 8, bold=True)

SPEECH_CLIPS = {"v02_captain_a", "v04_tunnel_a", "v05_q_a", "v06_q_a", "v09_q_a", "v12_q1_a", "v12_q2_a", "v20_q_a",
                "v22_q_a"}

_TC = T_OFF + 0.55
MUSIC = [  # (t0, t1, faixa, origem, ganho, fade_in, fade_out)
    (0.0, T_NO + 0.1, "doc_tensao", 0.0, 0.95, 0.02, 0.06),
    (S("H03") - 0.05, H3_END + 0.05, "doc_tensao", S("H03") - 0.05, 1.0, 0.25, 0.05),
    (S("H04") + 0.3, T_TITLE + 0.02, "doc_emocao", 0.0, 1.0, 0.8, 0.05),
    (T_TITLE, _TC - 0.45, "doc_tensao", 46.0, 0.95, 0.01, 0.12),
    (_TC, ACT1 + 0.05, "vilao", 0.0, 1.0, 0.6, 0.1),
    (ACT1, T_GOT, "tensao", 2.5, 0.9, 0.3, 0.5),
]


MUSIC += [
    (S("A104") - 0.3, ACT2 + 0.05, "tensao", 24.0, 0.9, 0.8, 0.3),
    (ACT2, ACT3 + 0.05, "doc_tensao", 0.0, 0.95, 0.05, 0.3),
    (ACT3, ACT3 + 76.0, "vilao", 0.0, 1.0, 0.05, 0.5),
    (ACT3 + 75.5, S("A308") - 0.1, "doc_tensao", 23.0, 0.9, 0.5, 0.3),
    (S("A308") - 0.1, ACT4 + 0.05, "doc_emocao", 28.0, 0.8, 0.5, 0.4),
    (ACT4, T_DALLAS_END + 3.4, "doc_emocao", 0.0, 1.0, 0.05, 0.6),
    (ACT5, ACT5 + 80.0, "tensao", 2.5, 0.9, 0.05, 0.5),
    (ACT5 + 79.5, S("A509") - 0.3, "doc_tensao", 46.0, 0.9, 0.5, 0.3),
    (T_JQ + 5.3, FALL + 0.05, "vilao", 38.0, 1.0, 0.3, 0.3),
    (FALL, ENDA + 0.05, "doc_tensao", 60.0, 0.9, 0.05, 0.4),
    (ENDA, S("F06") - 0.1, "piano", 3.5, 1.0, 0.3, 0.6),
    (S("F06") - 0.3, TOTAL, "doc_emocao", 62.0, 1.0, 0.8, 2.5),
]

SHOTS.sort(key=lambda s: s[0])


def frame(i):
    t = i / FPS
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    fx = {"grain": 0.8}
    fn, logo = SHOTS[-1][2], True
    for a, b, f, lg in SHOTS:
        if a <= t < b:
            fn, logo = f, lg
            break
    fn(c, t, fx)
    for a, b, f in OVER:
        if a <= t <= b:
            f(c, t)
    if logo:
        logo_bug(c, 0.8)
    return doc.post(s, i, fx)
