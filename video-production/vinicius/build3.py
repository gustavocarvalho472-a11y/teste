#!/usr/bin/env python3
"""v3 timeline for 'Arteta Tried To Save Vinicius' — owner's feedback on v2 (nov/2026):
 * the bad-quality takes (Vini from behind in fan footage, Xabi's press conference) are gone;
 * no take is repeated: every item is used once before anything comes back (global usage count);
 * pictures lead: high-quality photos, held almost still; video only in short clips from clean sources.
Photo treatment is chosen from the file itself:
 full  (width >= 1700)              -> full frame, gentle move on the face
 print (landscape, width < 1700)    -> printed photo on a dark table (keeps it sharp)
 panel (vertical, width < 1700)     -> two or three side by side (duo/trio), revealed one after the other
Writes build/v3/timeline.json + build/v3/gfx.json; render with gfx2.js build/v3 and BUILD=build/v3 assemble2.py."""
import json, os
import cv2
import camera, faces
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25; B3 = f"{ROOT}/build/v3"; os.makedirs(B3, exist_ok=True)
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"; PHD = f"{ROOT}/assets/photos"
DUR = json.load(open(f"{ROOT}/assets/vo/durations.json"))
TEXT = {i: t for i, t in (l.strip().split("|", 1) for l in open(f"{ROOT}/lines.txt") if "|" in l)}
camera.MAXMAG = 1.9          # video: never blow a source up more than this
camera.MAXMAG_PHOTO = 1.22   # photos: almost still, never soft

AG, AR, MS, MA = "arteta_girona", "arteta_respect", "mou_presser_sevilla", "mou_presser_aug25"
XS, PF, DS, DW, RF = "xabi_supercopa_pre", "ars_parade_fans", "diomande_signing", "diomande_words", "racism_fans"
SAFE = {MS: (0.52, 0.52, 0.24, 0.06), MA: (0.5, 0.62, 0.22, 0), PF: (0.84, 0.84, 0, 0.16), DS: (0.82, 0.78, 0.09, 0.09),
        DW: (0.5, 0.55, 0.25, 0.10), RF: (0.80, 0.70, 0.02, 0.02)}

# ------------------------------------------------------------------ photo library (assets/photos/p, high quality)
_meta = {}
def pmeta(n):
    if n not in _meta:
        f = f"{PHD}/p/{n}.jpg"; im = cv2.imread(f); h, w = im.shape[:2]
        face = FIX.get(n, {}).get("face0", "auto")
        if face == "auto": face = faces.face_box(f)
        _meta[n] = {"w": w, "h": h, "face": face, "kind": "full" if w >= 1700 else ("print" if w / h >= 1.25 else "panel")}
    return _meta[n]
FIX = {  # detector misses / wrong person
 "vini_back_bw": {"face0": [0.55, 0.12, 0.12]}, "vini_back_dark": {"face0": [0.5, 0.45, 0.1]}, "vini_walk7": {"face0": [0.42, 0.18, 0.08]},
 "vini_walk7b": {"face0": [0.5, 0.2, 0.08]}, "diom_25": {"face0": [0.55, 0.2, 0.15]}, "diom_walk": {"face0": [0.5, 0.55, 0.05]},
 "bern_street": {"face0": None}, "bern_in": {"face0": None}, "bern_in2": {"face0": None}, "bern_aerial": {"face0": None},
 "bern_night": {"face0": None}, "bern_night2": {"face0": None},
 "art_stands": {"face0": [0.42, 0.32, 0.15]}, "vini_barca": {"face0": [0.6, 0.3, 0.05]}, "vini_atleti": {"face0": [0.45, 0.3, 0.08]},
 "vini_drib": {"face0": [0.55, 0.38, 0.07]}, "vini_gala": {"face0": [0.42, 0.22, 0.07]}, "vini_best2": {"face0": [0.5, 0.3, 0.08]},
 "vini_orange": {"face0": [0.45, 0.24, 0.08]}, "vini_shirtless": {"face0": [0.48, 0.22, 0.08]}, "vini_stand2": {"face0": [0.45, 0.2, 0.05]},
 "vini_dance2": {"face0": [0.42, 0.17, 0.1]}, "vini_clap": {"face0": [0.5, 0.28, 0.06]}, "vini_cover": {"face0": [0.5, 0.28, 0.06]},
 "vini_corner": {"face0": [0.48, 0.27, 0.07]}, "vini_arms": {"face0": [0.48, 0.3, 0.06]}, "vini_night": {"face0": [0.55, 0.55, 0.04]},
 "vini_liv": {"face0": [0.62, 0.27, 0.07]}, "vini_land": {"face0": [0.45, 0.25, 0.12]}, "vini_flag": {"face0": [0.5, 0.32, 0.06]},
 "vini_walkdark": {"face0": [0.52, 0.45, 0.05]}, "vini_ucl": {"face0": [0.38, 0.1, 0.06]}, "vini_triangle": {"face0": [0.42, 0.32, 0.2]},
 "vini_point": {"face0": [0.45, 0.22, 0.1]}, "vini_eyes": {"face0": [0.45, 0.25, 0.25]}, "vini_slide": {"face0": [0.55, 0.45, 0.07]},
 "diom_civ2": {"face0": [0.32, 0.18, 0.06]}, "mou_rmpoint": {"face0": [0.45, 0.15, 0.12]}, "xabi_jacket": {"face0": [0.55, 0.3, 0.1]},
}
def obj_pos(n, pw, ph, ycen=0.36):
    """CSS background-position that puts the face at the centre of a pw x ph panel (eyes on the upper third)."""
    m = pmeta(n); f = m["face"]
    if not f: return "50% 50%"
    s = max(pw / m["w"], ph / m["h"]); sw, sh = m["w"] * s, m["h"] * s
    px = 50 if sw - pw < 1 else max(0, min(100, (f[0] * sw - pw / 2) / (sw - pw) * 100))
    py = 50 if sh - ph < 1 else max(0, min(100, (f[1] * sh - ph * ycen) / (sh - ph) * 100))
    return f"{px:.0f}% {py:.0f}%"
def cover_face(n, want=(0.62, 0.4)):
    """background-position for a full-bleed 16:9 plate + where the face lands (px) — for callouts."""
    m = pmeta(n); f = m["face"]; s = max(1920 / m["w"], 1080 / m["h"]); sw, sh = m["w"] * s, m["h"] * s
    x0 = max(0, min(sw - 1920, f[0] * sw - want[0] * 1920)); y0 = max(0, min(sh - 1080, f[1] * sh - want[1] * 1080))
    pos = f"{(x0 / (sw - 1920) * 100) if sw > 1921 else 50:.0f}% {(y0 / (sh - 1080) * 100) if sh > 1081 else 50:.0f}%"
    return pos, round(f[0] * sw - x0), round(f[1] * sh - y0), round(f[2] * sh * 0.85)

def Ph(n): return {"kind": "pic", "name": n, "key": n}
def V(src, a, b): return {"kind": "video", "src": R(src), "a": a, "b": b, "safe": SAFE.get(src), "key": f"{src}@{a}"}
def wins(src, *starts, L=2.5): return [V(src, a, a + L) for a in starts]
P = lambda *ns: [Ph(n) for n in ns]
POOLS = {
 "vini_glory": P("vini_studio", "vini_barca", "vini_drib", "vini_cele3", "vini_kiss", "vini_ballcup", "vini_goal", "vini_atleti", "vini_dance",
                 "vini_shirt", "vini_point", "vini_stand2", "vini_slide", "vini_high5", "vini_orange", "vini_cele", "vini_land", "vini_corner",
                 "vini_cele4", "vini_arms", "vini_dance2", "vini_liv", "vini_shirtless", "vini_corner2"),
 "vini_dark":  P("vini_track", "vini_walk7", "vini_flag", "vini_back_dark", "vini_angry", "vini_eyes", "vini_walkdark", "vini_night", "vini_cover",
                 "vini_bw", "vini_black", "vini_triangle", "vini_clap", "vini_walk7b", "vini_smile2", "vini_back_bw"),
 "xabi_ph":    P("xabi_crest", "xabi_port", "xabi_unveil", "xabi_clap", "xabi_touch", "xabi_hips", "xabi_dark", "xabi_wave", "xabi_wink", "xabi_arms",
                 "xabi_walk", "xabi_clap2", "xabi_jacket", "xabi_stand", "xabi_seat"),
 "art_ph":     P("art_think", "art_look", "art_pray", "art_orange", "art_trophy2", "art_jacket", "art_stands", "art_bag", "art_presser", "art_walk",
                 "art_port", "art_land", "art_smile2", "art_trophy"),
 "mou_ph":     P("mou_rmgreen", "mou_studio", "mou_rmpoint", "mou_desk", "mou_rmwhite", "mou_suit", "mou_rmtrack", "mou_rmjacket", "mou_old", "mou_arms"),
 "diom_ph":    P("diom_potm", "diom_25", "diom_civ", "diom_fist", "diom_walk", "diom_civ2", "diom_smile", "diom_rm"),
 "bern_ph":    P("bern_street", "bern_in", "bern_night", "bern_aerial", "bern_in2", "bern_night2"),
 "fair":       [V(RF, 88.0, 90.6)] + P("vini_brazil", "vini_ucl") + [V(RF, 28.6, 31.2)] + P("vini_trophy"),
 # short clips from clean sources only
 "arteta_v":   wins(AG, 222.4, 227.0, 230.0, L=2.4),
 "mou_v":      wins(MS, 700.0, 712.0, 724.0, 736.0, 840.0, 852.0, 864.0),
 "diom_v":     wins(DS, 0.6, 6.0, 11.0, 16.0, 21.0, 26.0) + wins(DW, 19.0, 25.0, 31.0, 55.0, 61.0, 67.0),
 "parade_v":   wins(PF, 2.0, 8.0, 26.0, 34.0, 44.0, 66.0, 76.0, 302.0, 320.0, 340.0),
 "madrid_v":   [V(RF, 0.6, 2.9), V(RF, 12.6, 15.0), V(RF, 108.6, 110.4)],
 "racism_v":   [V(RF, 18.0, 20.6), V(RF, 28.6, 31.2), V(RF, 88.0, 90.6), V(RF, 40.5, 43.0), V(RF, 76.6, 79.2), V(RF, 60.5, 63.0)],
}
USED = {}
def take(pool, kind=None):
    """least-used item of the pool (pool order breaks ties); kind='panel' asks for a vertical photo."""
    items = POOLS[pool] if not pool.startswith("@") else P(*pool[1:].split(","))
    if kind: items = [x for x in items if x["kind"] == "pic" and pmeta(x["name"])["kind"] == kind]
    if not items: return None
    best = min(items, key=lambda x: (USED.get(x["key"], 0), 0))
    USED[best["key"]] = USED.get(best["key"], 0) + 1
    return best

GFX = []; _gid = [0]
def gfx(kind, comp, **p):
    _gid[0] += 1; gid = f"{kind[0]}{_gid[0]:03d}_{comp}"; GFX.append({"id": gid, "kind": kind, "comp": comp, "p": p})
    return f"{B3}/gfx/{gid}" + (".png" if kind == "ov" else ".jpg")
def plate_shot(comp, frames, states=None, focus=(0.5, 0.5), amp=0.04, **p):
    files = [(round(t, 2), gfx("plate", comp, **{**p, **ex})) for t, ex in (states or [(0.0, {})])]
    return camera.plan({"kind": "plate", "states": files, "frames": frames, "focus": focus, "amp": amp, "move": "in", "grade": "none", "src": files[0][1]})

_rot = [0]
def make_shot(it, frames, pool):
    """turn a pool item into a shot of `frames` frames (pictures choose their own treatment)."""
    d = frames / FPS
    if it["kind"] == "video":
        L = it["b"] - it["a"]; sh = {"kind": "video", "src": it["src"], "ss": it["a"], "a": it["a"], "frames": frames, "safe": it["safe"],
                                     "slow": round(min(1.25, max(1.0, d / L)), 3), "grade": "color"}
        f = faces.face_box(sh["src"], round(sh["ss"] + min(L, d) / 2, 1), camera.safe_crop(sh))
        sh["face0"] = sh["face1"] = f if (f and f[2] >= 0.12) else None
        return camera.plan(sh, len(USED))
    n = it["name"]; m = pmeta(n); _rot[0] += 1
    if m["kind"] == "full":
        sh = {"kind": "photo", "src": f"{PHD}/p/{n}.jpg", "frames": frames, "face0": m["face"], "face1": m["face"], "grade": "color", "shot": "photo", "amp": 0.08}
        return camera.plan(sh, _rot[0])
    if m["kind"] == "print":
        return plate_shot("print", frames, photo=f"p/{n}", caption="", pos=obj_pos(n, 1112, 690, 0.4), rot=[-1.2, 1.0, -0.6][_rot[0] % 3], amp=0.06)
    # vertical photo: pair it with one or two more verticals from the same pool
    k = 3 if d >= 4.4 else 2
    more = []
    for _ in range(k - 1):
        x = take(pool, "panel")
        if x and x["name"] != n and x["name"] not in [y["name"] for y in more]: more.append(x)
    names = [n] + [x["name"] for x in more]; k = len(names)
    if k == 1:   # nothing to pair with: centre panel on a dark frame
        return plate_shot("duo", frames, photos=[{"photo": f"p/{n}", "pos": obj_pos(n, 955, 1080)}, {"photo": f"p/{n}", "pos": obj_pos(n, 955, 1080), "bw": True}], amp=0.03)
    w = (1920 - 10 * (k - 1)) / k
    photos = [{"photo": f"p/{x}", "pos": obj_pos(x, w, 1080)} for x in names]
    return plate_shot("duo" if k == 2 else "trio", frames, photos=photos, amp=0.04)   # all panels at once: a half-black frame reads as an error

CUT = {"video": 2.4, "full": 3.8, "print": 3.8, "panel": 4.2}
def allocate(pools, nf, cut=None):
    names = pools.split("+"); out = []; left = nf; i = 0
    while left > 0:
        pool = names[i % len(names)]; it = take(pool); i += 1
        kind = "video" if it["kind"] == "video" else pmeta(it["name"])["kind"]
        tgt = round((cut if (cut and kind != "video") else CUT[kind]) * FPS)
        if kind == "video": tgt = min(tgt, round((it["b"] - it["a"]) * 1.2 * FPS))
        fr = left if left < tgt * 1.5 else tgt
        out.append(make_shot(it, fr, pool)); left -= fr
    return out

# ------------------------------------------------------------------ DSL (same as v2)
def SL(text, a=0.4, b=-0.3): return ("slate", dict(text=text), a, b)
def L3(name, role, a=0.6, b=6.0): return ("l3", dict(name=name, role=role), a, b)
def SC(home, score, away, info, note="", a=0.4, b=-0.3): return ("score", dict(home=home, score=score, away=away, info=info, note=note), a, b)
def CTA(main, small="", icon="bell", a=0.8, b=-0.5): return ("cta", dict(main=main, small=small, icon=icon), a, b)
def F(w, pools, *ovs, cut=None, **o): return {"w": w, "pools": pools, "ovs": ovs, "cut": cut, "o": o}
def PLT(w, comp, states=None, focus=(0.5, 0.5), amp=0.05, sfx="whoosh", **p): return {"w": w, "plate": comp, "p": p, "states": states, "focus": focus, "amp": amp, "sfx": sfx}
def L(i, *parts, music=None): return {"line": i, "parts": parts, "music": music}
def SB(src, ss, d, phrases, l3=None, slate=None, visual=None, punch=True): return {"sb": True, "src": src, "ss": ss, "d": d, "phrases": phrases, "l3": l3, "slate": slate, "visual": visual, "punch": punch}
def CARD(comp, d, sfx="boom", focus=(0.5, 0.5), amp=0.05, music=None, **p): return {"card": True, "comp": comp, "d": d, "p": p, "sfx": sfx, "focus": focus, "amp": amp, "music": music}
AMP = {"clipping": 0.12, "print": 0.08, "quote": 0.05, "impact": 0.06, "title": 0.05, "chapter": 0.04, "callout": 0.06, "end": 0.03}
FOCUS = {"clipping": (0.5, 0.46), "print": (0.5, 0.45)}
def ph(n): return f"p/{n}"
def chap(n, w=920): return obj_pos(n, w, 1080)

ARTETA = ("Mikel Arteta", "Arsenal manager · Champions of England")
XABI_Q = [(0.1, 3.4, "Everyone's pressing *is essential,*"), (3.5, 8.0, "and I demand, in training and in matches, that everyone is *committed*"), (8.1, 12.3, "to the moment *when we don't have the ball.*")]
CO_POS, CO_X, CO_Y, CO_R = cover_face("diom_potm", (0.42, 0.42))

SEQ = [
 SB(AG, 236.3, 5.6, [(0.4, 2.3, "“And I must ask you: when is *Vini* joining?”", "Reporter"), (3.7, 5.5, "“*Thank you so much.*”", "Mikel Arteta")], slate="01 · 08 · 2026 — Girona"),
 L("B00", F(.55, "art_ph", L3(*ARTETA, a=0.5, b=6.5), cut=3.2), F(.45, "vini_glory", cut=3.2)),
 L("B01", PLT(.5, "clipping", source="Report · AS", date="August 2026", bg=ph("art_smile2"),
              text="Arteta has taken charge of the talks himself: *Vinicius would be the focal point* of the English champions."), F(.5, "vini_glory", cut=3.2)),
 L("B02", F(1, "vini_glory", SL("06 · 08 · 2026 — Renews until 2032", a=0.6, b=-0.4), cut=3.2)),
 L("B03", F(.4, "vini_dark", cut=3.2), F(.3, "bern_ph", SC("BAR", "1 – 2", "RMA", "FT · Camp Nou · 25.10.2026", "Vinicius · suspended", a=0.3)), F(.3, "diom_v+diom_ph")),
 SB(XS, 485.6, 12.4, [(a, b, t, None) for a, b, t in XABI_Q], l3=("Xabi Alonso", "Real Madrid manager · January 2026"), visual="xabi_ph+vini_dark"),
 L("B04", F(.34, "xabi_ph", cut=3.0), F(.33, "art_ph", cut=3.0), F(.33, "vini_dark", cut=3.0)),
 L("B05", F(.6, "vini_glory", cut=3.4), F(.4, "bern_ph+madrid_v")),
 CARD("title", 5.2, sfx="title", kicker="A football story", l1="Arteta Was Right", l2="<i>About</i> Vinicius Jr", sub="Two chances to change · One choice", photo=ph("vini_back_bw"), pos="50% 20%"),
 L("B06", F(1, "vini_glory", CTA("Subscribe", "New story every week", a=1.0, b=-0.6)), music="beat"),
 CARD("chapter", 4.4, num="01", date="May 2025 — Madrid", title="The<br>Request", synopsis="Xabi Alonso arrives with one condition: all eleven defend.", photo=ph("xabi_port"), pos=chap("xabi_port")),
 L("B07", F(.55, "@xabi_unveil,xabi_crest", L3("Xabi Alonso", "Unveiled as Real Madrid manager · 26 May 2025", a=0.6, b=6.4)), F(.45, "bern_ph+xabi_ph")),
 SB("xabi_presentation", 165.0, 9.0, [(0.2, 4.8, "Right now, it's not that I'm arriving *with demands,*", None), (4.9, 8.8, "but wanting to *work as a team,* always with the idea of improving.", None)], visual="xabi_ph"),
 L("B08", PLT(.45, "quote", text="We all have to defend. The eleven players on the pitch have to be involved.", who="Xabi Alonso · Club World Cup · June 2025", photo=ph("xabi_hips"), pos="70% 20%", size=78),
      F(.55, "@vini_trophy,vini_ucl,vini_best2,vini_gala")),
 L("B09", F(1, "vini_dark")),
 L("B10", F(.45, "vini_dark", SL("26 · 10 · 2025 — Santiago Bernabéu", a=0.4)),
      PLT(.48, "clipping", source="Vinicius · Instagram", date="29 October 2025", bg=ph("vini_eyes"), note="Summary of the post · not a quote",
          text="An apology to the fans, to his teammates and to the president. *The coach is not mentioned.*")),
 L("B11", PLT(1, "impact", big="72'", label="Remember this minute", photo=ph("vini_walk7"), pos="30% 20%", size=360, sfx="hit", focus=(0.3, 0.35))),
 L("B12", F(.62, "@xabi_touch,vini_angry,xabi_jacket,vini_walkdark", SL("04 · 01 · 2026 — Real Madrid 5–1 Betis", a=0.4)),
      PLT(.38, "print", photo=ph("vini_walk7b"), caption="Booed by his own stadium.", meta="Bernabéu · 04.01.2026", pos="50% 22%")),
 SB(XS, 485.6, 17.6, [(a, b, t, None) for a, b, t in XABI_Q[:2]] + [(8.1, 12.3, "to the moment *when we don't have the ball,*", None), (12.4, 17.5, "the ones up front and the ones at the back: *active, lines together.*", None)],
    l3=("Xabi Alonso", "Before the Super Cup · January 2026"), visual="xabi_ph+vini_dark"),
 L("B13", F(1, "xabi_ph+bern_ph", SL("12 · 01 · 2026 — Xabi Alonso leaves Real Madrid", a=0.5))),
 L("B14", PLT(.5, "clipping", source="Report · The Athletic", date="January 2026", bg=ph("xabi_dark"),
              text="Vinicius had held back on renewing his contract *to see whether Xabi Alonso would stay.*"), F(.5, "vini_dark")),
 L("B15", F(1, "parade_v+art_ph")),
 CARD("chapter", 4.4, num="02", date="May 2026 — London", title="The<br>Offer", synopsis="Arsenal win the league, and Arteta goes looking for Vinicius.", photo=ph("art_trophy"), pos=chap("art_trophy")),
 L("B16", F(.62, "parade_v+art_ph", SL("May 2026 — Arsenal, champions of England", a=0.5)), F(.38, "art_ph")),
 SB(AR, 32.9, 5.4, [(0.1, 2.8, "I just ask for one thing:", None), (2.9, 5.3, "*respect and commitment.* That's all.", None)], l3=("Mikel Arteta", "Arsenal press conference"), punch=False),
 L("B17", F(.5, "mou_v+mou_ph", L3("José Mourinho", "Real Madrid manager · from June 2026", a=0.5, b=-0.3)), F(.5, "vini_glory", SL("Vinicius · contract until 2027", a=0.4))),
 L("B18", F(.5, "art_ph", SL("AS · summer 2026 — Real Madrid's price: €150M", a=1.0)), F(.5, "vini_glory")),
 L("B19", F(.5, "vini_glory"), PLT(.28, "print", photo=ph("vini_smile2"), caption="Renewed until 2032.", meta="Real Madrid · 06.08.2026", pos="50% 25%", rot=1.1),
      F(.22, "arteta_v")),
 L("B20", F(.35, "bern_ph"), PLT(.35, "callout", focus=(CO_X / 1920, CO_Y / 1080), amp=0.06, photo=ph("diom_potm"), pos=CO_POS, cx=CO_X, cy=CO_Y, r=CO_R,
                                 name="Yan Diomande", meta="19 · RB Leipzig · €125M", side="right"), F(.3, "diom_v")),
 CARD("quote", 5.0, sfx="whoosh", text="I didn't ask for him, but I wanted him.", who="José Mourinho on Diomande · August 2026", photo=ph("mou_desk"), pos="70% 25%", size=92),
 L("B21", F(1, "diom_v+diom_ph", CTA("Subscribe", "This is where it starts to resolve", a=0.4, b=-0.3))),
 CARD("chapter", 4.4, num="03", date="August 2026 — Madrid", title="The<br>Ban", synopsis="Mourinho defends him, then asks for the same thing.", photo=ph("mou_studio"), pos=chap("mou_studio"), music="drone"),
 L("B22", F(1, "mou_v+mou_ph", L3("José Mourinho", "Real Madrid press conference · 25 August 2026", a=0.6, b=6.0))),
 SB(MA, 545.0, 17.0, [(0.2, 4.8, "In this case, I've been *trying*", None), (4.9, 9.8, "to get Vini to have *more emotional control,*", None), (9.9, 16.8, "but minutes into the game *he gets kicked. That's an assault.*", None)]),
 L("B23", F(.45, "madrid_v+bern_ph", SL("10 · 10 · 2026 — Real Madrid v Villarreal", a=0.4)), F(.55, "vini_dark")),
 L("B24", F(.5, "vini_dark", SC("RMA", "1 – 0", "VIL", "FT · Bernabéu · 10.10.2026", "Vinicius · red card · 72'", a=0.4)), F(.5, "diom_v+diom_ph", SL("Diomande — first goal for Real Madrid", a=0.4))),
 L("B25", F(1, "vini_dark", SL("14 · 10 · 2026 — Four-game ban", a=0.4))),
 L("B26", F(1, "mou_v+mou_ph")),
 SB(MS, 781.0, 30.0, [(0.2, 9.0, "If I were in his place, *I probably wouldn't be here.*", None), (9.1, 18.4, "This past summer, I would probably have *forced an exit*", None),
                      (18.5, 29.8, "to a league, a country, clubs, stadiums… *opponents who respect him.*", None)], l3=("José Mourinho", "Before Real Madrid v Sevilla · 17 October 2026")),
 L("B27", F(.55, "racism_v+vini_dark"), F(.45, "parade_v+art_ph")),
 L("B28", F(.5, "@anc_ucl,anc_suit,vini_ucl"), PLT(.5, "quote", text="Only the badge is untouchable.", who="José Mourinho · 20 October 2026", photo=ph("mou_old"), pos="60% 20%", size=100)),
 L("B29", F(.42, "bern_ph+madrid_v", SC("BAR", "1 – 2", "RMA", "FT · Camp Nou · 25.10.2026", "Vinicius · suspended", a=0.4)),
      F(.38, "parade_v+art_ph", SC("LIV", "0 – 1", "ARS", "FT · Anfield · 01.11.2026", "Arsenal · top of the league", a=0.4)), F(.2, "vini_dark")),
 CARD("chapter", 4.4, num="04", date="Oct – Nov 2026", title="The Kid<br>in His Place", size=150, synopsis="Four games without Vinicius, and a nineteen-year-old on the left.", photo=ph("diom_25"), pos=chap("diom_25")),
 L("B30", PLT(.6, "results", tag="Without Vinicius · Oct – Nov 2026", photo=ph("diom_walk"), foot="12 scored · 2 conceded",
              rows=[["Real Madrid", "4–1", "Sevilla"], ["Barcelona", "1–2", "Real Madrid"], ["Racing", "0–3", "Real Madrid"], ["Valencia", "0–3", "Real Madrid"]],
              states=[(0.0, {"n": 0, "f": False}), (2.6, {"n": 1, "f": False}), (4.3, {"n": 2, "f": False}), (6.0, {"n": 3, "f": False}), (7.6, {"n": 4, "f": False}), (9.6, {"n": 4, "f": True})],
              focus=(0.35, 0.5)), F(.4, "diom_v+diom_ph")),
 L("B31", F(.45, "mou_v+mou_ph"), F(.55, "xabi_ph+diom_ph")),
 CARD("quote", 5.6, sfx="whoosh", text="I'm ready to die for him.", who="Yan Diomande on José Mourinho · August 2026", photo=ph("diom_civ"), pos="70% 20%", size=100),
 L("B32", F(1, "mou_ph+diom_ph")),
 CARD("quote", 7.4, sfx="whoosh", text="I remember when Vini arrived at Madrid. Two or three years later, he was a top-level player.", who="José Mourinho on Diomande · August 2026", photo=ph("mou_suit"), pos="70% 20%", size=72),
 CARD("chapter", 4.0, num="", date="Before the verdict", title="To Be<br>Fair", synopsis="What four games can't tell us about Vinicius.", photo=ph("vini_brazil"), pos=chap("vini_brazil"), music="finale"),
 L("B33", F(1, "fair")),
 L("B34", PLT(.4, "impact", big="4 games.<br>4 wins.", label="Real Madrid without Vinicius", photo=ph("diom_walk"), pos="50% 40%", sfx="hit", focus=(0.3, 0.35)),
      F(.6, "vini_glory", SL("Now — the ban is over", a=0.5))),
 L("B35", F(1, "vini_glory", CTA("Right to stay?", "Tell me in the comments", icon="bubble", a=0.6))),
 L("B36", PLT(1, "timeline", title="Two chances to change", items=[[ph("xabi_hips"), "MAY 2025", "Xabi asks for more", obj_pos("xabi_hips", 336, 250)], [ph("xabi_walk"), "JAN 2026", "Xabi is sacked", obj_pos("xabi_walk", 336, 250)],
              [ph("art_smile2"), "AUG 2026", "Arteta calls. He stays", obj_pos("art_smile2", 336, 250)], [ph("diom_25"), "OCT 2026", "A month without him", obj_pos("diom_25", 336, 250)]],
              states=[(0.0, {"hi": 0}), (3.6, {"hi": 1}), (6.0, {"hi": 2}), (10.6, {"hi": 3})], focus=(0.5, 0.45), amp=0.04)),
 L("B37", F(.5, "arteta_v+art_ph"), F(.5, "vini_dark")),
 SB(AG, 239.5, 2.4, [(0.4, 2.3, "“*Thank you so much.*”", "Mikel Arteta")], punch=False),
 CARD("end", 10.0, sfx=None, title="Arteta Was Right <i>About</i> Vinicius Jr",
      credits="Photos and footage: press conferences · news reports · fan footage · press photography — full credits in the description<br>Narration: AI voice · Music: AI-generated"),
]

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
        sc = {k: s[k] for k in ("id", "f0", "nf", "start", "dur")}; sc.update({k: s[k] for k in ("text", "vo0", "vod", "nat") if k in s})
        ovs = []; sfx = []; shots = []
        def ov(comp, a, b, **p):
            a = a if a >= 0 else D + a; b = D if b is None else (b if b > 0 else D + b)
            ovs.append({"file": gfx("ov", comp, **p), "t0": round(a, 2), "t1": round(min(D, b), 2)})
        nxt = scenes[idx + 1] if idx + 1 < len(scenes) else None
        if "plate" in s or ("part" in s and "plate" in s["part"]):
            pl = s.get("plate") or {"comp": s["part"]["plate"], "p": s["part"]["p"], "focus": s["part"]["focus"], "amp": s["part"]["amp"]}
            amp = pl["amp"] if pl["amp"] != 0.05 else AMP.get(pl["comp"], 0.05)
            focus = pl["focus"] if tuple(pl["focus"]) != (0.5, 0.5) else FOCUS.get(pl["comp"], (0.5, 0.5))
            shots.append(plate_shot(pl["comp"], nf, states=(s.get("part") or {}).get("states"), focus=tuple(focus), amp=amp, **pl["p"]))
            snd = s.get("sfx") if "plate" in s else s["part"].get("sfx")
            if snd: sfx.append([snd, 0.0])
        elif "sb" in s:
            sb = s["sb"]
            if sb.get("visual"): shots = allocate(sb["visual"], nf, 3.4)
            elif sb["src"] == AR:
                shots = [{"kind": "video", "src": R(AR), "ss": sb["ss"], "frames": nf, "slow": 1.0, "pillar": "crop=iw:ih*0.80:0:0", "grade": "color"}]
            else:   # real sync soundbite: medium close-up, then a punch-in on the next phrase
                cuts = [0] + ([round(p[0] * FPS) - 1 for p in sb["phrases"][1:]] if sb["punch"] else []) + [nf]
                for j in range(len(cuts) - 1):
                    a, b = cuts[j], cuts[j + 1]
                    sh = {"kind": "video", "src": R(sb["src"]), "ss": round(sb["ss"] + a / FPS, 2), "a": sb["ss"], "frames": b - a, "slow": 1.0,
                          "safe": SAFE.get(sb["src"]), "grade": "color", "shot": "tight" if j % 2 else "talk", "move": "in"}
                    f = faces.face_box(sh["src"], round(sh["ss"] + (b - a) / FPS / 2, 1), camera.safe_crop(sh)); sh["face0"] = sh["face1"] = f
                    shots.append(camera.plan(sh))
            ov("shade", 0, None)
            for (a, b, txt, who) in sb["phrases"]: ov("sub", a, b, text=txt, **({"who": who} if who else {}))
            if sb.get("slate"): ov("slate", 0.2, 3.4, text=sb["slate"])
            if sb.get("l3"): ov("l3", 0.3, min(D - 0.2, 5.0), name=sb["l3"][0], role=sb["l3"][1], bottom=250, shade=False)
        else:
            p = s["part"]; shots = allocate(p["pools"], nf, p["cut"])
            for (comp, pp, a, b) in p["ovs"]:
                ov(comp, a, b, **pp)
                if comp in ("l3", "score"): sfx.append(["tick", max(0.0, a if a >= 0 else D + a)])
        if any(o["file"].endswith("_l3.png") for o in ovs):
            for x in shots:
                if x["kind"] in ("video", "photo") and x.get("face0"):
                    x["frx"] = 0.6; x.update(camera.plan({k: v for k, v in x.items() if k not in ("z0", "z1", "fx0", "fx1", "fy0", "fy1")}))
        sc.update(shots=shots, ovs=ovs, sfx=sfx)
        if s.get("card") in ("chapter", "title", "end"): sc["fin"] = 0.45
        if nxt and nxt.get("card") in ("chapter", "end"): sc["fout"] = 0.35
        out.append(sc)
    total = (scenes[-1]["f0"] + scenes[-1]["nf"]) / FPS
    json.dump({"fps": FPS, "total": total, "scenes": out, "vo": vo, "music": music, "name": "arteta-was-right-about-vinicius-EN"}, open(f"{B3}/timeline.json", "w"), indent=1, ensure_ascii=False)
    json.dump(GFX, open(f"{B3}/gfx.json", "w"), indent=1, ensure_ascii=False); faces.save()
    sh = [x for s in out for x in s["shots"]]; tot = sum(x["frames"] for x in sh)
    kinds = {}
    for x in sh: kinds[x["kind"]] = kinds.get(x["kind"], 0) + x["frames"] / FPS
    print(f"{len(out)} scenes · {total / 60:.2f} min · {len(sh)} shots · avg {tot / FPS / len(sh):.2f}s · " + " · ".join(f"{k} {v:.0f}s" for k, v in kinds.items()))
    rep = {k: v for k, v in USED.items() if v > 1}
    print("reused:", sorted(rep.items(), key=lambda x: -x[1])[:20])
    print("photos never used:", [x["name"] for p in POOLS.values() for x in p if x["kind"] == "pic" and x["key"] not in USED][:30])
if __name__ == "__main__": main()
