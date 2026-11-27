#!/usr/bin/env python3
"""Timeline for 'Nobody Understood Why Mourinho Signed Carlos Espí' (v3 style: Cinema + Revista, photo-led, smooth camera).
Sources: Real Madrid official site (press conference, interviews, presentation, training, photo galleries) + Pinterest photos.
Writes build/v3/timeline.json + build/v3/gfx.json; render with node gfx2.js build/v3 and BUILD=build/v3 python3 assemble3.py."""
import json, os
import cv2
import camera, faces
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25; B3 = f"{ROOT}/build/v3"; os.makedirs(B3, exist_ok=True)
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"; PHD = f"{ROOT}/assets/photos"
DUR = json.load(open(f"{ROOT}/assets/vo/durations.json"))
TEXT = {i: t for i, t in (l.strip().split("|", 1) for l in open(f"{ROOT}/lines.txt") if "|" in l)}
camera.MAXMAG = 1.9
camera.MAXMAG_PHOTO = 1.22

MP, ENT, FIR, PRE, DEB, TRN, ELC, COU, ROM = ("mou_presser_espanyol", "espi_entrevista", "espi_firma", "espi_presentacion", "espi_debut_fiorentina",
                                             "training_nov27", "espi_post_elche", "courtois_mixta", "espi_post_roma")
RMTV = (0.86, 0.86, 0.04, 0.12)   # keeps the Realmadrid.tv bug (top-right) out of frame
SAFE = {MP: (0.56, 0.64, 0.22, 0.10), ENT: RMTV, FIR: RMTV, PRE: RMTV, DEB: RMTV, TRN: RMTV, ELC: RMTV}
assert not any(s in ("espi_post_roma", "courtois_mixta") for s in ()), "UEFA / LaLiga-split sources: audio only"

_meta = {}
def pmeta(n):
    if n not in _meta:
        f = f"{PHD}/p/{n}.jpg"; im = cv2.imread(f); h, w = im.shape[:2]
        face = FIX.get(n, {}).get("face0", "auto")
        if face == "auto": face = faces.face_box(f)
        _meta[n] = {"w": w, "h": h, "face": face, "kind": "full" if w >= 1440 else ("print" if w / h >= 1.25 else "panel")}
    return _meta[n]
FIX = {"espi_fiore": {"face0": [0.24, 0.12, 0.06]}, "espi_lev_run": {"face0": [0.514, 0.18, 0.135]}}
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
def Ph(n): return {"kind": "pic", "name": n, "key": n}
def V(src, a, b): return {"kind": "video", "src": R(src), "a": a, "b": b, "safe": SAFE.get(src), "key": f"{src}@{a}"}
P = lambda *ns: [Ph(n) for n in ns]
POOLS = {
 "espi":   P("espi_fiore", "espi_train1", "espi_train2", "espi_train3", "espi_train4",
             "espi_konate", "espi_kids", "espi_signing", "espi_medical"),
 "end":    P("end_rm", "end_rm2", "end_smile", "end_shout", "end_orange", "end_back", "end_orange2", "end_studio"),
 "hug_v":  [V(ENT, 77.4, 79.2), V(ENT, 79.2, 81.0), V(ENT, 81.0, 82.7)],
 "kid_v":  [V(PRE, 29.0, 31.4), V(PRE, 33.2, 35.6), V(PRE, 36.1, 38.0)],
 "suit_v": [V(ENT, 0.3, 2.8), V(ENT, 3.3, 5.8), V(ENT, 21.0, 23.5)],
 "firma_v": [V(FIR, 19.0, 21.0), V(FIR, 9.3, 11.8), V(FIR, 13.3, 15.8), V(FIR, 23.3, 25.8), V(FIR, 27.3, 29.8), V(FIR, 16.3, 18.3)],
 "train_v": [V(TRN, 15.5, 18.0), V(TRN, 18.5, 21.0), V(TRN, 23.0, 25.5), V(TRN, 32.0, 34.5), V(TRN, 35.0, 37.5), V(TRN, 0.5, 3.0), V(TRN, 41.0, 43.4)],
 "debut_v": [V(DEB, 6.5, 9.0), V(DEB, 12.5, 15.0), V(DEB, 24.5, 27.0)],
 "elche_v": [V(ELC, 0.5, 3.0), V(ELC, 9.5, 12.0)],
 "mou_v":  [V(MP, 461.0, 463.5), V(MP, 466.0, 468.5), V(MP, 472.0, 474.5), V(MP, 581.0, 583.5)],
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
        sh["face0"] = sh["face1"] = f if (f and f[2] >= 0.12 and not any(k in sh["src"] for k in NOFACE)) else None
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


CO_POS, CO_X, CO_Y, CO_R = cover_face("espi_lev_run", (0.62, 0.42))
NOFACE = (PRE, TRN)
MOU = ("José Mourinho", "Real Madrid manager · after Espanyol 1–2 Real Madrid")
SEQ = [
 SB(MP, 569.45, 9.25, [(0.1, 2.5, "He's a very young kid, with a *profile*", None), (2.6, 9.2, "of player that *we need for this type of game.*", None)],
    slate="22 · 08 · 2026 — Espanyol 1–2 Real Madrid"),
 L("n01", F(.42, "@gon_cele,gon_back,gon_cele2", SL("July 2026 — Gonzalo García · sold to Fulham", a=0.3)), PLT(.58, "callout", focus=(CO_X / 1920, CO_Y / 1080), amp=0.06, photo=ph("espi_lev_run"), pos=CO_POS, cx=CO_X, cy=CO_Y, r=CO_R, name="Carlos Espí", meta="21 · Levante · €25M release clause", side="left", sfx="whoosh")),
 L("n02", F(.6, "@end_bench,end_sad", cut=2.6), F(.4, "@mou_touchline", cut=2.6)),
 L("n03", F(.38, "mou_v"), F(.62, "@espi_white,espi_kids", SL("14 · 10 · 2026 — Rome · 80th minute · Roma 3–1 Real Madrid", a=0.3), cut=6.5)),
 L("n04", F(.5, "@espi_suit"), F(.5, "@mou_ear2")),
 CARD("title", 5.2, sfx="title", kicker="A football story", l1="Nobody Understood <i>Why</i>", l2="Mourinho Signed Carlos Espí", sub="A €25M kid · A striker on the bench · One bet", photo=ph("mou_walk"), pos="50% 20%"),
 CARD("chapter", 4.4, num="01", date="Valencia — Levante", title="The Kid<br>From Levante", size=150, synopsis="A small town, a survival nobody expected, and an offer from England.", photo=ph("espi_lev_cele"), pos=chap("espi_lev_cele"), music="beat"),
 L("n05", F(1, "kid_v")),
 L("n06", F(.5, "@espi_lev_knee", L3("Carlos Espí", "Levante · Best U-23 player in La Liga, 2025–26", a=0.4, b=-0.2)), PLT(.5, "print", photo=ph("espi_lev_port"), caption="Levante, the club that made him.", meta="Levante UD · 2025–26", pos=obj_pos("espi_lev_port", 1112, 690, 0.4), rot=-1.0)),
 L("n07", PLT(.58, "clipping", source="Report · DAZN", date="July 2026", bg=ph("espi_lev_run"), note="Paraphrased from the report · not a quote",
              text="Hull City were already negotiating for Carlos Espí *when Real Madrid swooped in.*"), F(.42, "@espi_head")),
 L("n08", F(.36, "firma_v", SL("23 · 08 · 2026 — Signed until 2031", a=0.3)), PLT(.30, "print", photo=ph("espi_shirt19b"), caption="Number 19.", meta="Real Madrid · 23.08.2026", pos="50% 30%", rot=1.0), F(.34, "firma_v")),
 L("n09", F(1, "mou_v")),
 SB(MP, 544.95, 14.05, [(0.0, 1.3, "He's an *excellent* player.", None), (1.4, 7.9, "When we sensed that *Gonzalo could go to Fulham,*", None), (8.0, 14.0, "Juni Calafat put *some names on the table.*", None)], l3=MOU),
 CARD("chapter", 4.4, num="02", date="August – September 2026", title="Why<br>Him?", synopsis="Mbappé, Endrick, and a €25M kid nobody asked for.", photo=ph("end_sad"), pos=chap("end_sad")),
 L("n10", F(.34, "@bell_mbappe"), F(.33, "end"), F(.33, "@espi_hand")),
 L("n11", F(.5, "end"), PLT(.5, "impact", big="4'", label="Endrick · minutes played by late September", photo=ph("end_mouth"), pos="50% 25%", size=330, sfx="hit", focus=(0.3, 0.35))),
 L("n12", PLT(1, "quote", text="I just want to play.", who="Endrick · with Brazil · November 2026", photo=ph("end_brazil"), pos="60% 20%", size=120)),
 L("n13", F(.32, "@anc_brazil", L3("Carlo Ancelotti", "Brazil head coach", a=0.4, b=-0.2)), PLT(.30, "print", photo=ph("anc_brazil2"), caption="Brazil’s coach.", meta="CBF · 2026", pos="50% 30%", rot=1.0), F(.38, "@end_brazil_b,end_brazil9,end_brazil_tr", cut=6.5)),
 CARD("chapter", 4.4, num="03", date="Valdebebas — 2026", title="Under<br>One Roof", synopsis="Mourinho didn't just sign him. He lives with him.", photo=ph("mou_presser_nov"), pos=chap("mou_presser_nov")),
 L("n14", F(.5, "@espi_train1"), F(.5, "train_v")),
 SB(MP, 492.55, 16.9, [(0.1, 5.0, "We live together, there at *Valdebebas.*", None), (5.1, 11.5, "Breakfast together, lunch together, *dinner together.*", None), (11.6, 16.8, "Me, my staff, *him and Cucurella.*", None)]),
 L("n15", F(.5, "debut_v"), F(.5, "@espi_train2")),
 SB(MP, 525.5, 8.85, [(0.0, 5.4, "The kid is *living a dream,* but he doesn't work like someone *on the moon.*", None), (5.5, 8.8, "He works hard. *Really hard,* for the team.", None)]),
 L("n16", F(1, "@courtois", L3("Thibaut Courtois", "Real Madrid goalkeeper", a=0.3, b=-0.1))),
 SB(COU, 59.95, 11.35, [(0.0, 1.6, "He's a *beast.*", "Thibaut Courtois"), (1.7, 7.4, "Watching him in training, crashing into *Konaté, Rüdiger,* guys like that…", "Thibaut Courtois"),
                        (7.5, 11.3, "it's honestly *impressive.* He has talent, he's very strong.", "Thibaut Courtois")], visual="train_v+@espi_konate,espi_train3,espi_train4"),
 L("n17", F(.5, "@espi_celta_fight"), PLT(.5, "impact", big="1.94 m", label="Carlos Espí · a number nine who lives in the box", photo=ph("espi_celta_jump"), pos="50% 30%", size=260, sfx="hit", focus=(0.3, 0.35))),
 L("n18", F(1, "espi")),
 CARD("chapter", 4.4, num="04", date="August – November 2026", title="Game<br>by Game", synopsis="Off the bench, late in the game, again and again.", photo=ph("espi_dark"), pos=chap("espi_dark")),
 L("n19", F(.5, "@espi_esp_cele", SC("ESP", "1 – 2", "RMA", "FT · RCDE Stadium · 22.08.2026", "Espí · stoppage time", a=0.3), cut=7), F(.5, "hug_v")),
 L("n20", F(.5, "@elche_mbappe,espi_elche_run"), F(.5, "@espi_elche_hug,espi_elche_knees", SC("ELC", "2 – 3", "RMA", "FT · Martínez Valero · 15.09.2026", "Espí · stoppage time", a=0.3))),
 L("n21", F(.5, "@espi_roma", SC("ROM", "3 – 4", "RMA", "FT · Rome · 14.10.2026", "Espí · Real's second goal", a=0.3)), F(.5, "@bell_mbappe2")),
 SB(ROM, 0.15, 7.1, [(0.0, 3.3, "*Absolute madness.* We had to go until the end,", "Carlos Espí"), (3.4, 7.0, "and we all went *together for the win.*", "Carlos Espí")], visual="@espi_cele19,espi_thumb,espi_dark2,espi_signing"),
 L("n22", F(.5, "@espi_celta,espi_celta2", SC("RMA", "2 – 1", "CEL", "FT · Bernabéu · 21.11.2026", "Espí · 85' · ninth win in a row", a=0.3)), F(.5, "@espi_celta_vini,espi_celta_scream")),
 CARD("chapter", 4.4, num="05", date="November 2026", title="The Other<br>Side", synopsis="Endrick, the offers, and a president who refuses to sell.", photo=ph("end_trophy"), pos=chap("end_trophy"), music="finale"),
 L("n23", F(.5, "end"), F(.5, "firma_v", L3("Florentino Pérez", "Real Madrid president", a=0.3, b=-0.2))),
 L("n24", F(.5, "@mou_ear"), F(.5, "@end_wave")),
 L("n25", F(.34, "@end_run"), F(.33, "@espi_elche_smile"), F(.33, "mou_v")),
 CARD("end", 9.0, sfx=None, title="Nobody Understood <i>Why</i><br>Mourinho Signed Carlos Espí",
      credits="Footage and photos: Real Madrid C.F. (realmadrid.com) · press photography via Pinterest — full credits in the description<br>Narration: AI voice · Music: AI-generated"),
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
            elif False:
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
    json.dump({"fps": FPS, "total": total, "scenes": out, "vo": vo, "music": music, "name": "nobody-understood-why-mourinho-signed-espi-EN"}, open(f"{B3}/timeline.json", "w"), indent=1, ensure_ascii=False)
    json.dump(GFX, open(f"{B3}/gfx.json", "w"), indent=1, ensure_ascii=False); faces.save()
    sh = [x for s in out for x in s["shots"]]; tot = sum(x["frames"] for x in sh)
    kinds = {}
    for x in sh: kinds[x["kind"]] = kinds.get(x["kind"], 0) + x["frames"] / FPS
    print(f"{len(out)} scenes · {total / 60:.2f} min · {len(sh)} shots · avg {tot / FPS / len(sh):.2f}s · " + " · ".join(f"{k} {v:.0f}s" for k, v in kinds.items()))
    rep = {k: v for k, v in USED.items() if v > 1}
    print("reused:", sorted(rep.items(), key=lambda x: -x[1])[:20])
    print("photos never used:", [x["name"] for p in POOLS.values() for x in p if x["kind"] == "pic" and x["key"] not in USED][:30])
if __name__ == "__main__": main()
