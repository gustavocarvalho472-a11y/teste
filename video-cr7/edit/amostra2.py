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
    k1 = eio(seg(t, T_BELOW - 0.25, T_BELOW + 0.75))       # topo → base
    k2 = eio(seg(t, T_OF - 0.35, T_OF + 0.9))               # base → inteiro
    z = lerp(lerp(1.62, 1.62, k1), 0.93, k2) * (1 + 0.025 * seg(t, T_OF, H02a))
    fy = lerp(lerp(0.265, 0.735, k1), 0.5, k2)
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
    text(c, "TODAY", W / 2, H / 2 - 110, 40, DISPLAY, LIME, a, "center", 16)
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
TOTAL = round(T_SKY + 3.55 + 1.0, 2)
SILENCE.append((T_GOT - 0.1, TOTAL + 1))
cue(TOTAL - 1.0, "hit_low", 0.8)


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


@shot(T_GOT - 0.15, TOTAL)
def s_tunnel(c, t, fx):
    clip(c, "v04_tunnel_slow", t, T_GOT - 0.15, "fall", rate=0.85, zoom=(1.0, 1.18), dur=8, focus=(0.5, 0.45),
         focus1=(0.52, 0.42))
    bars(c, eio(seg(t, T_GOT, T_GOT + 1.0)))
    score_bug(c, t, T_GOT + 0.3, TOTAL - 0.4, "MUN", 2, "TOT", 0, "89'")
    fx["fade"] = seg(t, TOTAL - 0.7, TOTAL)


SPEECH_CLIPS = {"v02_captain_a", "v04_tunnel_a"}
_TC = T_OFF + 0.55
MUSIC = [  # (t0, t1, faixa, origem, ganho, fade_in, fade_out)
    (0.0, T_NO + 0.1, "doc_tensao", 0.0, 0.95, 0.02, 0.06),
    (S("H03") - 0.05, H3_END + 0.05, "doc_tensao", S("H03") - 0.05, 1.0, 0.25, 0.05),
    (S("H04") + 0.3, T_TITLE + 0.02, "doc_emocao", 0.0, 1.0, 0.8, 0.05),
    (T_TITLE, _TC - 0.45, "doc_tensao", 46.0, 0.95, 0.01, 0.12),
    (_TC, ACT1 + 0.05, "vilao", 0.0, 1.0, 0.6, 0.1),
    (ACT1, T_GOT, "tensao", 2.5, 0.9, 0.3, 0.5),
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
    if logo:
        logo_bug(c, 0.8)
    return doc.post(s, i, fx)
