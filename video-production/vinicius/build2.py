#!/usr/bin/env python3
"""v2 timeline ('Cinema + Revista' style) for 'Arteta Tried To Save Vinicius'.
Pictures lead: real takes and animated photos framed on faces; graphics are few, small and editorial.
Writes build/v2/timeline.json (scenes: shots + overlays + sfx) and build/v2/gfx.json (what gfx2.js must render)."""
import json, os, sys
import camera, faces
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25; B2 = f"{ROOT}/build/v2"; os.makedirs(B2, exist_ok=True)
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"; PHD = f"{ROOT}/assets/photos"
DUR = json.load(open(f"{ROOT}/assets/vo/durations.json"))
TEXT = {i: t for i, t in (l.strip().split("|", 1) for l in open(f"{ROOT}/lines.txt") if "|" in l)}

AG, AR, MS, MA = "arteta_girona", "arteta_respect", "mou_presser_sevilla", "mou_presser_aug25"
XS, XP, VB, PF = "xabi_supercopa_pre", "xabi_presentation", "vini_booed_betis", "ars_parade_fans"
DS, DW, RF = "diomande_signing", "diomande_words", "racism_fans"
# clean area of each source (w, h, x, y as fractions): removes channel logos, tickers and burned captions
SAFE = {MS: (0.52, 0.52, 0.24, 0.06), MA: (0.5, 0.62, 0.22, 0), XP: (0.56, 0.80, 0.08, 0), VB: (0.76, 0.70, 0.12, 0.13),
        PF: (0.84, 0.84, 0, 0.16), DS: (0.82, 0.78, 0.09, 0.09), DW: (0.5, 0.55, 0.25, 0.10), RF: (0.80, 0.70, 0.02, 0.02)}
FAN = (0.9, 0.9, 0.05, 0.05)   # VB 57.5-66: fans hugging Vini, no captions burned in

def V(src, a, b, **k): return {"kind": "video", "src": R(src), "a": a, "b": b, "safe": k.pop("safe", SAFE.get(src)), **k}
def Ph(n, **k): return {"kind": "photo", "src": f"{PHD}/{n}.jpg", "a": 0, "b": 60, "name": n, **k}
def span(src, a, b, step=5.0, **k):
    n = max(1, round((b - a) / step)); return [V(src, a + i * (b - a) / n, a + (i + 1) * (b - a) / n, **k) for i in range(n)]

POOLS = {
 "arteta":    span(AG, 222.0, 236.0, 4.6) + [Ph("arteta_face"), Ph("arteta_mz")],
 "arteta_ph": [Ph("arteta_smile"), Ph("arteta_face"), Ph("arteta_mz")],
 "vini":      [V(VB, 47.0, 51.8), Ph("vini_walk"), V(VB, 57.6, 61.8, safe=FAN), V(VB, 24.0, 29.0), Ph("vini_stand"), V(VB, 14.0, 17.6),
               V(VB, 51.8, 55.6), V(VB, 62.0, 65.4, safe=FAN), Ph("vini_bench"), V(VB, 38.0, 43.0), Ph("vini_pitch"), V(VB, 29.0, 34.0)],
 "vini_sub":  [V(VB, 14.0, 17.6), V(VB, 17.6, 21.4), Ph("vini_sub"), Ph("vini_bench"), Ph("vini_walk")],
 "vini_pitch": [V(VB, 47.0, 51.8), V(VB, 38.0, 43.0), V(VB, 24.0, 29.0), Ph("vini_stand"), V(VB, 51.8, 55.6), V(VB, 29.0, 34.0), Ph("vini_pitch")],
 "vini_fans": [V(VB, 57.6, 61.8, safe=FAN), V(VB, 62.0, 65.4, safe=FAN)],
 "vini_ph":   [Ph("vini_walk"), Ph("vini_stand"), Ph("vini_bench"), Ph("vini_sub"), Ph("vini_hoarding"), Ph("vini_pitch")],
 "vini_wall": [V(RF, 18.0, 22.4), V(RF, 22.4, 26.4), Ph("vini_hoarding")],
 "xabi":      span(XP, 21.0, 61.0) + span(XP, 300.0, 330.0) + span(XP, 520.0, 545.0),
 "xabi_ph":   [Ph("xabi_a"), Ph("xabi_b"), Ph("xabi_c"), Ph("xabi_d")],
 "mou":       span(MS, 700.0, 740.0) + span(MS, 835.0, 865.0),
 "mou_ph":    [Ph("mou_a"), Ph("mou_b"), Ph("mou_c")],
 "diom":      span(DS, 0.6, 31.5) + span(DW, 18.5, 35.5) + span(DW, 54.5, 71.5),
 "diom_ph":   [Ph("diom_shirt"), Ph("diom_face"), Ph("diom_flo"), Ph("diom_face2")],
 "parade":    span(PF, 1.0, 21.0) + span(PF, 24.0, 59.0) + span(PF, 64.0, 91.0) + span(PF, 300.0, 380.0, 6.0),
 "ars_ph":    [Ph("ars_trophy"), Ph("ars_champ"), Ph("emirates_bus"), Ph("ars_flares")],
 "madrid":    [V(RF, 0.6, 2.9), Ph("kiosk"), V(RF, 12.6, 15.0), Ph("bernabeu"), V(RF, 108.6, 110.4), Ph("papers"), Ph("bernabeu2")],
 "racism":    [V(RF, 28.6, 33.2), V(RF, 88.0, 93.0), V(RF, 40.5, 45.0), V(RF, 76.6, 81.0), V(RF, 60.5, 65.0), Ph("vini_hoarding")],
}
# framing fixes where the detector is wrong or the subject is not a face (checked on build/v2/camera.jpg)
FIX = {
 "vini_walk": {"face0": [0.32, 0.14, 0.24]}, "vini_sub": {"face0": [0.28, 0.13, 0.2]}, "vini_bench": {"face0": [0.42, 0.17, 0.14]},
 "vini_stand": {"face0": [0.74, 0.20, 0.09]}, "vini_pitch": {"face0": None, "focus": (0.84, 0.42)}, "vini_hoarding": {"face0": [0.79, 0.42, 0.14]},
 "diom_face": {"face0": [0.69, 0.42, 0.42]}, "diom_face2": {"face0": [0.66, 0.42, 0.5]}, "papers": {"focus": (0.45, 0.4), "face0": None},
 "emirates_bus": {"face0": None, "focus": (0.5, 0.55), "move": "pan"}, "bernabeu": {"move": "pan"}, "bernabeu2": {"move": "pan"},
 "ars_champ": {"face0": None, "move": "pan"}, "kiosk": {"face0": None}, "diom_shirt": {"face0": [0.507, 0.184, 0.1]},
}

# ------------------------------------------------------------------ framing data
def detect(sh):
    if sh["kind"] == "photo":
        f = faces.face_box(sh["src"]); fix = FIX.get(sh["name"], {})
        sh.update({"face0": f, "face1": f}); sh.update(fix)
        if "face0" in fix: sh["face1"] = fix["face0"]
        return sh
    crop = camera.safe_crop(sh); d = sh["frames"] / FPS / sh.get("slow", 1)
    pts = [sh["ss"] + 0.15, sh["ss"] + d / 2, sh["ss"] + max(0.2, d - 0.2)]
    got = [faces.face_box(sh["src"], round(t, 1), crop) for t in pts]
    ok = [g for g in got if g]
    # discard tiny background faces (fans/photographers) unless they are all we have in a close shot
    ok = [g for g in ok if g[2] >= 0.09]
    sh["face0"] = ok[0] if ok else None; sh["face1"] = ok[-1] if ok else None
    key = (os.path.basename(sh["src"])[:-4], round(sh["a"], 1))
    if key in VFIX:
        sh.update(VFIX[key])
        if "face0" in VFIX[key] and "face1" not in VFIX[key]: sh["face1"] = VFIX[key]["face0"]
    return sh
VFIX = {   # (source, window start) -> manual framing (fan footage: the detector locks on supporters, not on Vini)
 (DS, 0.6): {"face0": None, "focus": (0.22, 0.58), "move": "in"},
 (VB, 14.0): {"face0": None, "focus": (0.56, 0.35), "move": "in"}, (VB, 17.6): {"face0": None, "focus": (0.36, 0.32), "move": "in"},
 (VB, 24.0): {"face0": [0.63, 0.42, 0.1], "face1": [0.43, 0.40, 0.1]}, (VB, 29.0): {"face0": [0.5, 0.38, 0.1], "face1": [0.2, 0.3, 0.12], "move": "out"},
 (VB, 38.0): {"face0": [0.53, 0.38, 0.1], "face1": [0.38, 0.33, 0.1]}, (VB, 47.0): {"face0": [0.45, 0.14, 0.09], "face1": [0.85, 0.12, 0.09]},
 (VB, 51.8): {"face0": [0.8, 0.2, 0.09], "face1": [0.8, 0.26, 0.09]},
 (VB, 57.6): {"face0": [0.39, 0.21, 0.26], "face1": [0.55, 0.27, 0.26]}, (VB, 62.0): {"face0": [0.57, 0.24, 0.27], "face1": [0.56, 0.30, 0.27]},
}

_cur = {}; SHOTS = []
def allocate(pools, nf, cut, opts):
    names = pools.split("+"); D = nf / FPS; n = max(1, round(D / cut)); base = nf // n; out = []
    for i in range(n):
        frames = base if i < n - 1 else nf - base * (n - 1); d = frames / FPS; name = names[i % len(names)]; items = POOLS[name]
        for _ in range(len(items)):
            it = items[_cur.get(name, 0) % len(items)]; _cur[name] = _cur.get(name, 0) + 1; L = it["b"] - it["a"]
            if it["kind"] == "photo" or L >= d / 1.3: break
        sh = {k: v for k, v in it.items() if k not in ("a", "b")}; sh["a"] = it["a"]; sh["frames"] = frames
        if sh["kind"] == "video":
            sh["slow"] = round(min(1.6, max(1.0, d / L)), 3); sh["ss"] = round(it["a"] + max(0, (L - d * 1.0 / sh["slow"]) / 2) if L > d else it["a"], 2)
        sh["grade"] = opts.get("grade", "color"); sh["i"] = len(SHOTS)
        out.append(sh); SHOTS.append(sh)
    return out

# ------------------------------------------------------------------ DSL
GFX = []; _gid = [0]
def gfx(kind, comp, **p):
    _gid[0] += 1; gid = f"{kind[0]}{_gid[0]:03d}_{comp}"; GFX.append({"id": gid, "kind": kind, "comp": comp, "p": p})
    return f"{B2}/gfx/{gid}" + (".png" if kind == "ov" else ".jpg")
def SL(text, a=0.4, b=-0.3): return ("slate", dict(text=text), a, b)
def L3(name, role, a=0.6, b=6.0): return ("l3", dict(name=name, role=role), a, b)
def SC(home, score, away, info, note="", a=0.4, b=-0.3): return ("score", dict(home=home, score=score, away=away, info=info, note=note), a, b)
def CTA(main, small="", icon="bell", a=0.8, b=-0.5): return ("cta", dict(main=main, small=small, icon=icon), a, b)
def F(w, pools, *ovs, cut=4.8, **o): return {"w": w, "pools": pools, "ovs": ovs, "cut": cut, "o": o}
def PLT(w, comp, states=None, focus=(0.5, 0.5), amp=0.05, sfx="whoosh", **p): return {"w": w, "plate": comp, "p": p, "states": states, "focus": focus, "amp": amp, "sfx": sfx}
def L(i, *parts, music=None): return {"line": i, "parts": parts, "music": music}
def SB(src, ss, d, phrases, l3=None, slate=None, visual=None, cut=4.2, punch=True): return {"sb": True, "src": src, "ss": ss, "d": d, "phrases": phrases, "l3": l3, "slate": slate, "visual": visual, "cut": cut, "punch": punch}
def CARD(comp, d, sfx="boom", focus=(0.5, 0.5), amp=0.05, music=None, **p): return {"card": True, "comp": comp, "d": d, "p": p, "sfx": sfx, "focus": focus, "amp": amp, "music": music}

# how far the camera travels over each kind of plate (paper on a table moves more than a title)
AMP = {"clipping": 0.12, "print": 0.08, "quote": 0.06, "impact": 0.07, "title": 0.06, "chapter": 0.04, "callout": 0.08, "end": 0.03}
FOCUS = {"clipping": (0.5, 0.46), "print": (0.5, 0.45)}
def panel_pos(photo, w=920):
    f = faces.face_box(f"{PHD}/{photo}.jpg"); f = FIX.get(photo, {}).get("face0", f)
    if not f: return "50% center"
    return f"{max(0, min(100, (f[0] * 1920 - w / 2) / (1920 - w) * 100)):.0f}% center"
def callout(photo, name, meta, side="right"):
    f = FIX.get(photo, {}).get("face0") or faces.face_box(f"{PHD}/{photo}.jpg")
    return dict(photo=photo, cx=round(f[0] * 1920), cy=round(f[1] * 1080), r=round(f[2] * 1080 * 0.85), name=name, meta=meta, side=side), (f[0], f[1])

ARTETA = ("Mikel Arteta", "Arsenal manager · Champions of England")
XABI_Q = [(0.1, 3.4, "Everyone's pressing *is essential,*"), (3.5, 8.0, "and I demand, in training and in matches, that everyone is *committed*"), (8.1, 12.3, "to the moment *when we don't have the ball.*")]
CO, CO_XY = callout("diom_shirt", "Yan Diomande", "19 · RB Leipzig · €125M")

SEQ = [
 SB(AG, 236.3, 5.6, [(0.4, 2.3, "“And I must ask you: when is *Vini* joining?”", "Reporter"), (3.7, 5.5, "“*Thank you so much.*”", "Mikel Arteta")],
    slate="01 · 08 · 2026 — Girona"),
 L("B00", F(.6, "arteta", L3(*ARTETA, a=0.5, b=6.5), cut=3.4), F(.4, "vini", cut=3.2)),
 L("B01", PLT(.55, "clipping", source="Report · AS", date="August 2026", bg="arteta_smile",
              text="Arteta has taken charge of the talks himself: *Vinicius would be the focal point* of the English champions."), F(.45, "vini", cut=3.2)),
 L("B02", F(1, "vini_fans+vini", SL("06 · 08 · 2026 — Renews until 2032", a=0.6, b=-0.4), cut=3.2)),
 L("B03", F(.4, "vini_sub", cut=3.0), F(.3, "madrid", SC("BAR", "1 – 2", "RMA", "FT · Camp Nou · 25.10.2026", "Vinicius · suspended", a=0.3), cut=3.4), F(.3, "diom", cut=3.4)),
 SB(XS, 485.6, 12.4, [(a, b, t, None) for a, b, t in XABI_Q], l3=("Xabi Alonso", "Real Madrid manager · January 2026"), visual="xabi_ph"),
 L("B04", F(.34, "xabi", cut=3.0), F(.33, "arteta", cut=3.0), F(.33, "vini", cut=3.0)),
 L("B05", F(.6, "vini_pitch", cut=3.5), F(.4, "madrid", cut=2.6)),
 CARD("title", 5.2, sfx="title", kicker="A football story", l1="Arteta Tried", l2="<i>to Save</i> Vinicius", sub="Two chances to change · One choice", photo="vini_walk", pos="50% 30%"),
 L("B06", F(1, "vini_fans+vini", CTA("Subscribe", "New story every week", a=1.0, b=-0.6), cut=4.4), music="beat"),
 CARD("chapter", 4.4, num="01", date="May 2025 — Madrid", title="The<br>Request", synopsis="Xabi Alonso arrives with one condition: all eleven defend.", photo="xabi_a", pos=panel_pos("xabi_a")),
 L("B07", F(.55, "xabi", L3("Xabi Alonso", "Unveiled as Real Madrid manager · 26 May 2025", a=0.6, b=6.4)), F(.45, "madrid+xabi")),
 SB(XP, 165.0, 9.0, [(0.2, 4.8, "Right now, it's not that I'm arriving *with demands,*", None), (4.9, 8.8, "but wanting to *work as a team,* always with the idea of improving.", None)]),
 L("B08", PLT(.45, "quote", text="We all have to defend. The eleven players on the pitch have to be involved.", who="Xabi Alonso · Club World Cup · June 2025", photo="xabi_c", size=78),
      F(.55, "vini")),
 L("B09", F(1, "vini_pitch", cut=3.6)),
 L("B10", F(.45, "vini_sub", SL("26 · 10 · 2025 — Santiago Bernabéu", a=0.4)),
      PLT(.48, "clipping", source="Vinicius · Instagram", date="29 October 2025", bg="vini_sub", note="Summary of the post · not a quote",
          text="An apology to the fans, to his teammates and to the president. *The coach is not mentioned.*")),
 L("B11", PLT(1, "impact", big="72'", label="Remember this minute", photo="vini_bench", size=360, sfx="hit", focus=(0.3, 0.35))),
 L("B12", F(.62, "vini_sub", SL("04 · 01 · 2026 — Real Madrid 5–1 Betis", a=0.4)),
      PLT(.38, "print", photo="vini_walk", caption="Booed by his own stadium.", meta="Bernabéu · 04.01.2026", pos="50% 25%")),
 SB(XS, 485.6, 17.6, [(a, b, t, None) for a, b, t in XABI_Q[:2]] + [(8.1, 12.3, "to the moment *when we don't have the ball,*", None), (12.4, 17.5, "the ones up front and the ones at the back: *active, lines together.*", None)],
    l3=("Xabi Alonso", "Before the Super Cup · January 2026"), visual="xabi_ph"),
 L("B13", F(1, "xabi_ph", SL("12 · 01 · 2026 — Xabi Alonso leaves Real Madrid", a=0.5), cut=3.6, grade="bw")),
 L("B14", PLT(.5, "clipping", source="Report · The Athletic", date="January 2026", bg="xabi_d",
              text="Vinicius had held back on renewing his contract *to see whether Xabi Alonso would stay.*"), F(.5, "vini")),
 L("B15", F(1, "parade", cut=3.2)),
 CARD("chapter", 4.4, num="02", date="May 2026 — London", title="The<br>Offer", synopsis="Arsenal win the league, and Arteta goes looking for Vinicius.", photo="arteta_smile", pos=panel_pos("arteta_smile")),
 L("B16", F(.62, "parade+ars_ph", SL("May 2026 — Arsenal, champions of England", a=0.5)), F(.38, "arteta")),
 SB(AR, 32.9, 5.4, [(0.1, 2.8, "I just ask for one thing:", None), (2.9, 5.3, "*respect and commitment.* That's all.", None)], l3=("Mikel Arteta", "Arsenal press conference"), punch=False),
 L("B17", F(.5, "mou", L3("José Mourinho", "Real Madrid manager · from June 2026", a=0.5, b=-0.3)), F(.5, "vini", SL("Vinicius · contract until 2027", a=0.4))),
 L("B18", F(.5, "arteta+parade", SL("AS · summer 2026 — Real Madrid's price: €150M", a=1.0)), F(.5, "vini_pitch")),
 L("B19", F(.5, "vini"), PLT(.28, "print", photo="vini_stand", caption="Renewed until 2032.", meta="Real Madrid · 06.08.2026", pos="70% 25%", rot=1.1),
      F(.22, "arteta_ph", cut=4.0)),
 L("B20", F(.35, "madrid"), PLT(.35, "callout", focus=CO_XY, amp=0.08, **CO), F(.3, "diom")),
 CARD("quote", 5.0, sfx="whoosh", text="I didn't ask for him, but I wanted him.", who="José Mourinho on Diomande · August 2026", photo="mou_a", size=92),
 L("B21", F(1, "diom", CTA("Subscribe", "This is where it starts to resolve", a=0.4, b=-0.3), cut=3.2)),
 CARD("chapter", 4.4, num="03", date="August 2026 — Madrid", title="The<br>Ban", synopsis="Mourinho defends him, then asks for the same thing.", photo="mou_b", pos=panel_pos("mou_b"), music="drone"),
 L("B22", F(1, "mou", L3("José Mourinho", "Real Madrid press conference · 25 August 2026", a=0.6, b=6.0))),
 SB(MA, 545.0, 17.0, [(0.2, 4.8, "In this case, I've been *trying*", None), (4.9, 9.8, "to get Vini to have *more emotional control,*", None), (9.9, 16.8, "but minutes into the game *he gets kicked. That's an assault.*", None)]),
 L("B23", F(.45, "madrid", SL("10 · 10 · 2026 — Real Madrid v Villarreal", a=0.4)), F(.55, "vini_sub")),
 L("B24", F(.5, "vini_ph", SC("RMA", "1 – 0", "VIL", "FT · Bernabéu · 10.10.2026", "Vinicius · red card · 72'", a=0.4)),
      F(.5, "diom", SL("Diomande — first goal for Real Madrid", a=0.4))),
 L("B25", F(1, "vini_ph", SL("14 · 10 · 2026 — Four-game ban", a=0.4), cut=3.4, grade="bw")),
 L("B26", F(1, "mou", cut=4.2)),
 SB(MS, 781.0, 30.0, [(0.2, 9.0, "If I were in his place, *I probably wouldn't be here.*", None), (9.1, 18.4, "This past summer, I would probably have *forced an exit*", None),
                      (18.5, 29.8, "to a league, a country, clubs, stadiums… *opponents who respect him.*", None)], l3=("José Mourinho", "Before Real Madrid v Sevilla · 17 October 2026")),
 L("B27", F(.55, "racism+vini_wall"), F(.45, "parade+arteta_ph")),
 L("B28", F(.5, "vini+madrid"), PLT(.5, "quote", text="Only the badge is untouchable.", who="José Mourinho · 20 October 2026", photo="mou_b", size=100)),
 L("B29", F(.42, "madrid", SC("BAR", "1 – 2", "RMA", "FT · Camp Nou · 25.10.2026", "Vinicius · suspended", a=0.4)),
      F(.38, "parade", SC("LIV", "0 – 1", "ARS", "FT · Anfield · 01.11.2026", "Arsenal · top of the league", a=0.4)), F(.2, "vini_ph")),
 CARD("chapter", 4.4, num="04", date="Oct – Nov 2026", title="The Kid<br>in His Place", size=150, synopsis="Four games without Vinicius, and a nineteen-year-old on the left.", photo="diom_face", pos=panel_pos("diom_face")),
 L("B30", PLT(.6, "results", tag="Without Vinicius · Oct – Nov 2026", photo="diom_shirt", foot="12 scored · 2 conceded",
              rows=[["Real Madrid", "4–1", "Sevilla"], ["Barcelona", "1–2", "Real Madrid"], ["Racing", "0–3", "Real Madrid"], ["Valencia", "0–3", "Real Madrid"]],
              states=[(0.0, {"n": 0, "f": False}), (2.6, {"n": 1, "f": False}), (4.3, {"n": 2, "f": False}), (6.0, {"n": 3, "f": False}), (7.6, {"n": 4, "f": False}), (9.6, {"n": 4, "f": True})],
              focus=(0.35, 0.5)), F(.4, "diom")),
 L("B31", F(.45, "mou"), F(.55, "xabi_ph+diom")),
 CARD("quote", 5.6, sfx="whoosh", text="I'm ready to die for him.", who="Yan Diomande on José Mourinho · August 2026", photo="diom_face2", size=100),
 L("B32", F(1, "mou_ph+diom_ph", cut=3.3)),
 CARD("quote", 7.4, sfx="whoosh", text="I remember when Vini arrived at Madrid. Two or three years later, he was a top-level player.", who="José Mourinho on Diomande · August 2026", photo="mou_c", size=72),
 CARD("chapter", 4.0, num="", date="Before the verdict", title="To Be<br>Fair", synopsis="What four games can't tell us about Vinicius.", photo="vini_bench", pos=panel_pos("vini_bench"), music="finale"),
 L("B33", F(1, "racism+vini_fans+vini_wall")),
 L("B34", PLT(.4, "impact", big="4 games.<br>4 wins.", label="Real Madrid without Vinicius", photo="diom_face", sfx="hit", focus=(0.3, 0.35)),
      F(.6, "vini", SL("Now — the ban is over", a=0.5))),
 L("B35", F(1, "vini_fans+vini", CTA("Right to stay?", "Tell me in the comments", icon="bubble", a=0.6))),
 L("B36", PLT(1, "timeline", title="Two chances to change", items=[["xabi_a", "MAY 2025", "Xabi asks for more", "80% 30%"], ["xabi_d", "JAN 2026", "Xabi is sacked", "80% 30%"],
              ["arteta_smile", "AUG 2026", "Arteta calls. He stays", "45% 30%"], ["diom_shirt", "OCT 2026", "A month without him", "58% 20%"]],
              states=[(0.0, {"hi": 0}), (3.6, {"hi": 1}), (6.0, {"hi": 2}), (10.6, {"hi": 3})], focus=(0.5, 0.45), amp=0.04)),
 L("B37", F(.5, "arteta"), F(.5, "vini_pitch+vini_ph", cut=4.6, grade="bw")),
 SB(AG, 239.5, 2.4, [(0.4, 2.3, "“*Thank you so much.*”", "Mikel Arteta")], punch=False),
 CARD("end", 10.0, sfx=None, title="Arteta Tried <i>to Save</i> Vinicius",
      credits="Footage: press conferences · news reports · fan footage — full credits in the description<br>Narration: AI voice · Music: AI-generated"),
]

# ------------------------------------------------------------------ build
def main():
    scenes = []; vo = []; music = [{"track": "drone", "start": 0}]; t = 0.0; n = 0
    def add(d, sid, **k):
        nonlocal t; scenes.append({"id": sid, "start": t, "dur": d, **k}); t += d
    for it in SEQ:
        if it.get("card"):
            if it.get("music"): music.append({"track": it["music"], "start": t})
            add(it["d"], f"k{n:02d}", plate={"comp": it["comp"], "p": it["p"], "focus": it["focus"], "amp": it["amp"]}, sfx=it["sfx"], card=it["comp"]); n += 1; continue
        if it.get("sb"):
            add(it["d"], f"c{n:02d}", sb=it, nat={"src": R(it["src"]), "ss": it["ss"]}); n += 1; continue
        if it.get("music"): music.append({"track": it["music"], "start": t})
        d = DUR[it["line"]] + 0.3; Wt = sum(p["w"] for p in it["parts"])
        vo.append({"file": it["line"] + ".mp3", "start": t + 0.12, "dur": d - 0.3})
        for k, p in enumerate(it["parts"]):
            add(d * p["w"] / Wt, f"n{n:02d}", part=p, **({"text": TEXT[it["line"]], "vo0": t + 0.12, "vod": d - 0.3} if k == 0 else {})); n += 1
    for s in scenes: s["f0"] = round(s["start"] * FPS)
    for a, b in zip(scenes, scenes[1:]): a["nf"] = b["f0"] - a["f0"]
    scenes[-1]["nf"] = round(scenes[-1]["dur"] * FPS)
    out = []
    for idx, s in enumerate(scenes):
        s["start"] = s["f0"] / FPS; s["dur"] = s["nf"] / FPS; D = s["dur"]; nf = s["nf"]
        sc = {k: s[k] for k in ("id", "f0", "nf", "start", "dur") }; sc.update({k: s[k] for k in ("text", "vo0", "vod", "nat") if k in s})
        ovs = []; sfx = []; shots = []
        def ov(kind, comp, a, b, **p):
            a = a if a >= 0 else D + a; b = D if b is None else (b if b > 0 else D + b)
            ovs.append({"file": gfx("ov", comp, **p), "t0": round(a, 2), "t1": round(min(D, b), 2)})
        nxt = scenes[idx + 1] if idx + 1 < len(scenes) else None
        if "plate" in s or ("part" in s and "plate" in s["part"]):
            pl = s.get("plate") or {"comp": s["part"]["plate"], "p": s["part"]["p"], "focus": s["part"]["focus"], "amp": s["part"]["amp"]}
            states = (s.get("part") or {}).get("states") or [(0.0, {})]
            files = [(round(st, 2), gfx("plate", pl["comp"], **{**pl["p"], **ex})) for st, ex in states]
            if pl["amp"] == 0.05: pl["amp"] = AMP.get(pl["comp"], 0.05)
            if tuple(pl["focus"]) == (0.5, 0.5): pl["focus"] = FOCUS.get(pl["comp"], (0.5, 0.5))
            shots.append(camera.plan({"kind": "plate", "states": files, "frames": nf, "focus": tuple(pl["focus"]), "amp": pl["amp"], "move": "in", "grade": "none", "src": files[0][1]}))
            snd = s.get("sfx") if "plate" in s else s["part"].get("sfx")
            if snd: sfx.append([snd, 0.0])
        elif "sb" in s:
            sb = s["sb"]
            if sb.get("visual"):
                shots = [camera.plan(detect(x), x["i"]) for x in allocate(sb["visual"], nf, sb["cut"], {})]
            elif sb["src"] == AR:
                shots = [{"kind": "video", "src": R(AR), "ss": sb["ss"], "frames": nf, "slow": 1.0, "pillar": "crop=iw:ih*0.80:0:0", "grade": "color"}]
            else:   # real sync soundbite: medium close-up, then a punch-in on the next phrase (jump zoom), alternating
                cuts = [0] + ([round(p[0] * FPS) - 1 for p in sb["phrases"][1:]] if sb["punch"] else []) + [nf]
                for j in range(len(cuts) - 1):
                    a, b = cuts[j], cuts[j + 1]
                    sh = {"kind": "video", "src": R(sb["src"]), "ss": round(sb["ss"] + a / FPS, 2), "a": sb["ss"], "frames": b - a, "slow": 1.0,
                          "safe": SAFE.get(sb["src"]), "grade": "color", "shot": "tight" if j % 2 else "talk", "move": "in"}
                    shots.append(camera.plan(detect(sh)))
            ov("ov", "shade", 0, None)
            for (a, b, txt, who) in sb["phrases"]:
                ov("ov", "sub", a, b, text=txt, **({"who": who} if who else {}))
            if sb.get("slate"): ov("ov", "slate", 0.2, 3.4, text=sb["slate"])
            if sb.get("l3"): ov("ov", "l3", 0.3, min(D - 0.2, 5.0), name=sb["l3"][0], role=sb["l3"][1], bottom=250, shade=False)
        else:
            p = s["part"]
            for x in allocate(p["pools"], nf, p["cut"], p["o"]):
                shots.append(camera.plan(detect(x), x["i"]))
            for (comp, pp, a, b) in p["ovs"]:
                ov("ov", comp, a, b, **pp)
                if comp in ("l3", "score"): sfx.append(["tick", max(0.0, a if a >= 0 else D + a)])
        # left-side text (lower third, slate) -> put faces on the right third
        if any(o["file"].endswith(("_l3.png",)) for o in ovs):
            for x in shots:
                if x["kind"] != "plate" and x.get("face0"): x["frx"] = 0.6; x.update(camera.plan({k: v for k, v in x.items() if k not in ("z0", "z1", "fx0", "fx1", "fy0", "fy1")}, x.get("i", 0)))
        sc.update(shots=shots, ovs=ovs, sfx=sfx)
        if s.get("card") in ("chapter", "title", "end"): sc["fin"] = 0.45
        if nxt and nxt.get("card") in ("chapter", "end"): sc["fout"] = 0.35
        out.append(sc)
    total = (scenes[-1]["f0"] + scenes[-1]["nf"]) / FPS
    json.dump({"fps": FPS, "total": total, "scenes": out, "vo": vo, "music": music, "name": "vinicius-arteta-EN-v2"}, open(f"{B2}/timeline.json", "w"), indent=1, ensure_ascii=False)
    json.dump(GFX, open(f"{B2}/gfx.json", "w"), indent=1, ensure_ascii=False); faces.save()
    sh = [x for s in out for x in s["shots"]]; real = sum(x["frames"] for x in sh if x["kind"] == "video") / sum(x["frames"] for x in sh)
    print(f"{len(out)} scenes · {total / 60:.2f} min · {len(sh)} shots · avg {sum(x['frames'] for x in sh) / FPS / len(sh):.2f}s · "
          f"video {real:.0%} · plates {sum(x['frames'] for x in sh if x['kind'] == 'plate') / FPS:.0f}s · overlays {sum(len(s['ovs']) for s in out)} · gfx {len(GFX)}")
if __name__ == "__main__": main()
