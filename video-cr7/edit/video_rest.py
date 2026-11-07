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
