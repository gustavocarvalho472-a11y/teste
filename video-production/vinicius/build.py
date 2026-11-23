#!/usr/bin/env python3
"""Timeline for 'Arteta Tried To Save Vinicius' (Becir format: narration beats + real soundbites, rights-safe pools)."""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"
DUR = json.load(open(f"{ROOT}/assets/vo/durations.json"))
def win(src, a, b): return [("win", src, a, b)]
def ph(*names): return [("photo", f"{ROOT}/assets/photos/{n}.jpg") for n in names]

AG, AR, MS, MA, MC = "arteta_girona", "arteta_respect", "mou_presser_sevilla", "mou_presser_aug25", "mou_chiringuito"
XS, XP, VB, PF = "xabi_supercopa_pre", "xabi_presentation", "vini_booed_betis", "ars_parade_fans"
DS, DW, RF = "diomande_signing", "diomande_words", "racism_fans"
# crops: remove TV/channel logos, tickers and burned captions; zoom on the speaker in wide press-room shots
CROP = {MS: "crop=iw*0.52:ih*0.52:iw*0.24:ih*0.06,", MA: "crop=iw*0.5:ih*0.62:iw*0.22:0,", XP: "crop=iw*0.56:ih*0.80:iw*0.08:0,",
        VB: "crop=iw*0.76:ih*0.70:iw*0.12:ih*0.13,", PF: "crop=iw*0.84:ih*0.84:0:ih*0.16,", DS: "crop=iw*0.82:ih*0.78:iw*0.09:ih*0.09,",
        DW: "crop=iw*0.5:ih*0.55:iw*0.25:ih*0.10,", RF: "crop=iw*0.80:ih*0.70:iw*0.02:ih*0.02,", MC: "crop=iw*0.8:ih*0.8:iw*0.1:ih*0.05,"}
PILLAR = {AR: "crop=iw:ih*0.80:0:0"}   # square Arsenal clip with burned subtitles -> blurred 16:9 background
# Rights: NO LaLiga / Champions League / Premier League / FIFA match feeds. Pools = press rooms (club backdrops),
# a vlogger's mixed-zone phone video, fan footage from the stands and the street, a news report, freeze-frames of those.
POOLS = {
 "arteta": win(AG, 224.5, 236.0) + ph("arteta_face", "arteta_mz", "arteta_smile"),
 "arteta_ph": ph("arteta_smile", "arteta_face", "arteta_mz"),
 "parade": win(PF, 1.0, 22.0) + win(PF, 24.0, 60.0) + win(PF, 64.0, 92.0) + ph("ars_trophy", "ars_champ") + win(PF, 300.0, 380.0),
 "ars_ph": ph("emirates_bus", "ars_trophy", "ars_champ", "ars_flares"),
 "vini": win(VB, 44.6, 56.4) + ph("vini_stand", "vini_walk", "vini_pitch") + win(RF, 20.6, 26.4) + ph("vini_hoarding"),
 "vini_sub": win(VB, 2.6, 21.6) + ph("vini_sub", "vini_bench", "vini_walk"),
 "vini_ph": ph("vini_stand", "vini_walk", "vini_pitch", "vini_sub", "vini_hoarding"),
 "xabi": win(XP, 21.0, 120.0) + ph("xabi_a", "xabi_c") + win(XP, 300.0, 400.0) + ph("xabi_b", "xabi_d") + win(XP, 520.0, 600.0),
 "xabi_ph": ph("xabi_a", "xabi_b", "xabi_c", "xabi_d"),
 "mou": win(MS, 700.0, 780.0) + ph("mou_a", "mou_c") + win(MS, 830.0, 900.0) + ph("mou_b"),
 "mou_ph": ph("mou_a", "mou_b", "mou_c"),
 "diom": win(DS, 0.6, 31.5) + ph("diom_face", "diom_shirt") + win(DW, 18.5, 35.5) + ph("diom_face2", "diom_flo") + win(DW, 54.5, 71.5),
 "diom_ph": ph("diom_shirt", "diom_face", "diom_flo", "diom_face2"),
 "madrid": win(RF, 0.6, 3.8) + ph("bernabeu", "kiosk") + win(RF, 12.6, 19.8) + ph("bernabeu2"),
 "racism": win(RF, 28.6, 58.0) + ph("vini_hoarding") + win(RF, 76.6, 104.0) + ph("papers"),
 "bernabeu": ph("bernabeu", "bernabeu2") + win(RF, 12.6, 16.4) + win(RF, 108.6, 111.6),
}

_items = {}; _cur = {}
def pool_items(name):
    if name not in _items:
        out = []
        for it in POOLS[name]:
            if it[0] == "photo": out.append((it[1], 0.0, 30.0)); continue
            p = R(it[1]); a, b = it[2], it[3]
            if b - a > 9.5:
                k = int((b - a) // 4.7); out += [(p, a + i * (b - a) / k, a + (i + 1) * (b - a) / k) for i in range(k)]
            else: out.append((p, a, b))
        _items[name] = out; _cur[name] = 0
    return _items[name]
def allocate(pools, nf, cut=4.0):
    D = nf / FPS; n = max(1, round(D / cut)); names = pools.split("+"); takes = []; base = nf // n
    for i in range(n):
        frames = base if i < n - 1 else nf - base * (n - 1); d = frames / FPS; name = names[i % len(names)]; items = pool_items(name)
        for _ in range(len(items)):
            p, a, b = items[_cur[name] % len(items)]; _cur[name] += 1; L = b - a
            if L >= d or d / L <= 1.75: break
        slow = max(1.0, d / L); ss = 0.0 if p.endswith(".jpg") else a + (min(1.2, (L - d) / 2) if L > d else 0)
        takes.append({"src": p, "ss": round(ss, 2), "slow": round(slow, 3), "frames": frames,
                      "crop": next((c for k, c in CROP.items() if p == R(k)), ""), "pillar": next((c for k, c in PILLAR.items() if p == R(k)), "")})
    return takes

def C(src, ss, d, name, role, phrases, **k):
    return {"clip": True, "src": src, "ss": ss, "d": d, "extra": {a: b for a, b in k.items() if a != "crop"}, "crop": k.get("crop", CROP.get(src, "")),
            "gfx": {"type": "caps", "name": name, "role": role, "small": True, "phrases": [{"t0": a, "t1": b, "text": t, "q": 0} for a, b, t in phrases]}}
def P(w, pools, type_="none", cut=4.0, **p): return (w, pools, cut, {"type": type_, **p})
def L(i, *parts, music=None): return {"line": i, "parts": parts, "music": music}
def M(d, pools, cut): return {"montage": True, "d": d, "pools": pools, "cut": cut}
def G(d, pools, type_, cut=3.0, **p): return {"gfxscene": True, "d": d, "pools": pools, "cut": cut, "gfx": {"type": type_, **p}}
def CARD(text, sub="", pools="bernabeu"): return {"card": True, "text": text, "sub": sub, "pools": pools}
D_ = lambda term, full, body: dict(term=term, full=full, body=body, small=True)

ARTETA_Q = C(AG, 236.3, 5.6, "MIKEL ARTETA", "Girona 1–4 Arsenal · pre-season · August 1, 2026",
             [(0.4, 2.3, "“And I must ask you: when is *Vini* joining?”"), (3.7, 5.5, "“*Thank you so much.*”")])
XABI_SHORT = C(XS, 485.6, 12.4, "XABI ALONSO", "Real Madrid press conference · January 2026",
               [(0.1, 3.4, "Everyone's pressing *is essential,*"), (3.5, 8.0, "and I demand, in training and in matches, that everyone is *committed*"), (8.1, 12.3, "to the moment *when we don't have the ball.*")],
               pools="xabi_ph", cut=1.8)
XABI_LONG = C(XS, 485.6, 17.6, "XABI ALONSO", "Before the Super Cup · January 2026",
              [(0.1, 3.4, "Everyone's pressing *is essential,*"), (3.5, 8.0, "and I demand, in training and in matches, that everyone is *committed*"),
               (8.1, 12.3, "to the moment *when we don't have the ball,*"), (12.4, 17.5, "the ones up front and the ones at the back: *active, lines together.*")],
              pools="xabi+xabi_ph", cut=2.6)
MOU_SHORT = C(MS, 781.0, 9.4, "JOSÉ MOURINHO", "Real Madrid press conference · October 17, 2026",
              [(0.2, 9.3, "If I were in his place, *I probably wouldn't be here.*")])
MOU_LONG = C(MS, 781.0, 30.0, "JOSÉ MOURINHO", "Before Real Madrid v Sevilla · October 17, 2026",
             [(0.2, 9.0, "If I were in his place, *I probably wouldn't be here.*"), (9.1, 18.4, "This past summer, I would probably have *forced an exit*"),
              (18.5, 29.8, "to a league, a country, clubs, stadiums… *opponents who respect him.*")])
ARTETA_RESPECT = C(AR, 32.9, 5.4, "MIKEL ARTETA", "Arsenal press conference",
                   [(0.1, 2.8, "I just ask for one thing:"), (2.9, 5.3, "*respect and commitment.* That's all.")])

SEQ = [
 ARTETA_Q,
 L("B00", P(.55, "arteta", "lower", 1.6, name="MIKEL ARTETA", role="Arsenal · champions of England 2025-26", late=.08), P(.45, "arteta_ph+vini_ph", "none", 1.3)),
 L("B01", P(1, "arteta_ph+vini+ars_ph", "define", 1.6, **D_("AS", "SPANISH NEWSPAPER · AUGUST 2026", "Arteta personally leads the talks: Vinicius would be the centre of the champions' project."))),
 L("B02", P(1, "vini+bernabeu", "stat", 1.5, big="2032", label="AUGUST 6, 2026 · VINICIUS RENEWS WITH REAL MADRID", late=.1)),
 L("B03", P(.55, "vini_sub+vini_ph", "list", 1.2, tag="OCTOBER 2026", title="BANNED · 4 GAMES", items=["Red card v Villarreal: hair pull", "Real Madrid win all four", "Including the Clásico at the Camp Nou"], t0=.06, lasthot=True),
      P(.45, "diom_ph+diom", "none", 1.2)),
 XABI_SHORT,
 L("B04", P(1, "xabi_ph+arteta_ph+vini_ph", "chips", 1.5, title="TWO CHANCES TO CHANGE", items=["Xabi Alonso · inside Real Madrid", "Mikel Arteta · a new club", "Both times, he stayed"], t0=.12)),
 L("B05", P(.6, "vini+bernabeu", "word", 1.8, text="HE'S BACK", sub="TO A TEAM THAT JUST WON A MONTH WITHOUT HIM", late=.08), P(.4, "xabi_ph", "none", 1.6)),
 {"sting": True},
 L("B06", P(1, "vini+madrid+bernabeu", "chips", 2.0, title="HELP THE CHANNEL GROW", items=["Like", "Subscribe", "Send it to a Madrid fan"], t0=.2), music="beat"),
 CARD("MAY 2025", "THE REQUEST", "xabi_ph"),
 L("B07", P(.6, "xabi", "lower", 2.6, name="XABI ALONSO", role="Unveiled as Real Madrid coach · May 26, 2025", late=.08), P(.4, "xabi+bernabeu", "none", 2.4)),
 "XABI_PRES",
 L("B08", P(.55, "xabi", "define", 2.6, **D_("ALL ELEVEN", "XABI ALONSO · CLUB WORLD CUP · JUNE 2025", "“We all have to defend. The eleven players on the pitch have to be involved.”")),
      P(.45, "vini_ph+vini", "chips", 2.2, title="VINICIUS IN 2025", items=["2× Champions League", "FIFA The Best · 2024", "Freedom on the left"], t0=.08)),
 L("B09", P(1, "vini+bernabeu", "none", 2.2)),
 L("B10", P(.45, "bernabeu+vini_sub", "stat", 2.0, big="72'", label="OCTOBER 26, 2025 · CLÁSICO · REAL MADRID 2–1 BARCELONA", late=.15),
      P(.55, "vini_sub+vini_ph", "list", 2.0, tag="OCTOBER 29, 2025", title="THE APOLOGY", items=["The fans ✔", "His teammates ✔", "The president ✔", "The coach —"], t0=.12, lasthot=True)),
 L("B11", P(1, "vini_ph", "word", 2.0, text="72'", sub="REMEMBER THIS MINUTE", late=.08)),
 L("B12", P(.6, "vini_sub+madrid", "chips", 1.8, title="JANUARY 4, 2026 · REAL MADRID 5–1 BETIS", items=["Xabi: keep pressing", "Vini: pass me the ball", "The Bernabéu whistles"], t0=.12),
      P(.4, "xabi+xabi_ph", "lower", 2.0, name="XABI ALONSO", role="Days later · before the Super Cup", late=.15)),
 XABI_LONG,
 L("B13", P(1, "xabi_ph+xabi", "stat", 2.2, big="12 JAN", label="XABI ALONSO LEAVES REAL MADRID · AFTER 7½ MONTHS", late=.35)),
 L("B14", P(.55, "vini+madrid", "define", 2.4, **D_("RENEWAL", "THE ATHLETIC · JANUARY 2026", "Vinicius held back on his new contract to see whether Xabi would stay.")),
      P(.45, "xabi_ph+vini_ph", "word", 2.0, text="ATTEMPT #1", sub="THE COACH LEFT · THE PLAYER STAYED", late=.1)),
 L("B15", P(1, "ars_ph+parade", "word", 2.0, text="ATTEMPT #2", sub="FROM LONDON", late=.25)),
 CARD("MAY 2026 · LONDON", "THE OFFER", "ars_ph"),
 L("B16", P(.6, "parade", "chips", 2.2, title="ARSENAL · 2025-26", items=["Champions of England", "First title in 22 years", "Best defence: 26 conceded"], t0=.1), P(.4, "arteta+ars_ph", "none", 2.0)),
 ARTETA_RESPECT,
 L("B17", P(.5, "mou", "lower", 2.4, name="JOSÉ MOURINHO", role="Real Madrid coach · from June 2026", late=.1), P(.5, "vini+vini_ph", "stat", 2.2, big="2027", label="WHEN VINICIUS'S CONTRACT WAS DUE TO RUN OUT", late=.1)),
 L("B18", P(1, "arteta+vini_ph+ars_ph", "list", 2.2, tag="AS · SUMMER 2026", title="ARTETA'S PITCH", items=["Arteta leads the talks himself", "Vinicius: the reference on the left", "In Martinelli's place", "Real Madrid's price: €150M"], t0=.1, lasthot=True)),
 L("B19", P(.55, "vini+bernabeu", "stat", 2.0, big="2032", label="AUGUST 6 · FIVE DAYS AFTER GIRONA", late=.35), P(.45, "arteta_ph", "word", 2.0, text="ATTEMPT #2", sub="HE STAYED", late=.08)),
 L("B20", P(1, "diom", "chips", 2.2, title="YAN DIOMANDE", items=["19 years old", "From RB Leipzig", "Around €125M"], t0=.18)),
 "MOU_CHIRINGUITO",
 L("B21", P(1, "diom_ph+diom", "word", 2.0, text="SUBSCRIBE", sub="THIS IS WHERE IT STARTS TO RESOLVE", late=.1)),
 CARD("AUGUST 2026", "THE CONSEQUENCES", "mou_ph"),
 L("B22", P(1, "mou", "lower", 2.4, name="JOSÉ MOURINHO", role="Real Madrid press conference · August 2026", late=.25), music="drone"),
 "MOU_EMOTIONS",
 L("B23", P(1, "vini_sub+vini_ph+bernabeu", "list", 1.6, tag="OCTOBER 10, 2026 · REAL MADRID 1–0 VILLARREAL", title="20 MINUTES", items=["Comes off the bench", "Scores · ruled out by VAR", "Hair pull on Nathan Saliba", "Straight red card"], t0=.08, lasthot=True)),
 L("B24", P(.5, "vini_ph", "stat", 1.8, big="72'", label="ALMOST THE SAME MINUTE AS THE 2025 CLÁSICO", late=.1), P(.5, "diom+diom_ph", "stat", 1.8, big="62'", label="DIOMANDE · HIS FIRST GOAL FOR REAL MADRID", late=.1)),
 L("B25", P(1, "vini_ph+madrid", "list", 1.6, tag="OCTOBER 14, 2026", title="THE BAN", items=["2 games · the hair pull", "2 games · protests at the referee", "Out: Sevilla · Barcelona · Racing · Valencia"], t0=.08, lasthot=True)),
 L("B26", P(1, "mou", "none", 2.0)),
 MOU_LONG,
 L("B27", P(.55, "racism", "none", 2.4), P(.45, "ars_ph+vini_ph", "word", 2.0, text="HE STAYED", sub="TWO MONTHS EARLIER", late=.1)),
 L("B28", P(.5, "vini_ph+madrid", "none", 2.0), P(.5, "mou+mou_ph", "define", 2.4, **D_("THE BADGE", "MOURINHO · OCTOBER 20, 2026", "“Only the badge is untouchable.”"))),
 L("B29", P(.4, "bernabeu+madrid", "stat", 2.0, big="BAR 1–2 RMA", label="OCTOBER 25 · CAMP NOU · VINICIUS SUSPENDED", late=.1),
      P(.35, "parade+ars_ph", "stat", 2.0, big="LIV 0–1 ARS", label="NOVEMBER 1 · FIRST WIN AT ANFIELD SINCE 2012 · TOP OF THE TABLE", late=.1),
      P(.25, "vini_ph", "word", 2.0, text="WINNING WITHOUT HIM", late=.08)),
 CARD("THE KID IN HIS POSITION", "", "diom_ph"),
 L("B30", P(.55, "diom+madrid", "list", 2.0, tag="DURING THE BAN", title="4 GAMES · 4 WINS", items=["Real Madrid 4–1 Sevilla", "Barcelona 1–2 Real Madrid", "Racing 0–3 Real Madrid", "Valencia 0–3 Real Madrid"], t0=.06, lasthot=True),
      P(.45, "diom+diom_ph", "chips", 2.0, title="12 SCORED · 2 CONCEDED", items=["Diomande on the left", "Goals v Villarreal, Sevilla, Racing"], t0=.1)),
 L("B31", P(.55, "diom+diom_ph", "chips", 2.0, title="WHAT MOURINHO SAW IN HIM", items=["Pace", "Above all: defensive work"], t0=.15), P(.45, "xabi_ph", "word", 2.0, text="WHAT XABI ASKED FOR", late=.05)),
 G(5.6, "diom_ph", "define", 2.8, **D_("DIOMANDE", "ON MOURINHO · AUGUST 2026", "“I'm ready to die for him.”")),
 L("B32", P(1, "mou_ph+diom_ph", "none", 2.0)),
 G(7.4, "mou_ph+vini_ph", "define", 2.4, **D_("MOURINHO", "ON DIOMANDE · AUGUST 2026", "“I remember when Vini arrived at Madrid. Two or three years later, he was a top-level player.”")),
 CARD("TO BE FAIR", "", "racism"),
 L("B33", P(1, "racism+vini_ph", "chips", 2.2, title="TO BE FAIR", items=["Racially abused in stadium after stadium", "Scored in two Champions League finals", "Four games are a small sample"], t0=.1), music="finale"),
 L("B34", P(.6, "vini+vini_ph", "none", 2.2), P(.4, "bernabeu+vini", "word", 2.0, text="HE'S BACK", sub="NOW THE BAN IS OVER", late=.1)),
 L("B35", P(1, "vini_ph+bernabeu", "word", 2.4, text="RIGHT TO STAY?", sub="TELL ME IN THE COMMENTS · SUBSCRIBE", late=.08)),
 L("B36", P(1, "xabi_ph+arteta_ph+diom_ph", "list", 2.0, tag="THE STORY", title="ONE CHOICE", items=["Xabi asked · sacked a week later", "Arteta offered · turned down", "A month without him · every game won"], t0=.08, lasthot=True)),
 L("B37", P(.5, "arteta", "none", 2.2), P(.5, "vini_ph", "none", 2.6)),
 C(AG, 239.5, 2.4, "", "", [(0.4, 2.3, "“*Thank you so much.*”")]),
]
TEXT = {i: t for i, t in (l.strip().split("|", 1) for l in open(f"{ROOT}/lines.txt") if "|" in l)}
EXTRA = json.load(open(f"{ROOT}/clips_extra.json")) if os.path.exists(f"{ROOT}/clips_extra.json") else {}

def main():
    scenes = []; vo = []; music = [{"track": "drone", "start": 0}]; t = 0.0; n = 0
    def add(d, sid, **k):
        nonlocal t
        scenes.append({"id": sid, "start": t, "dur": d, "label": "ARTETA TRIED TO SAVE VINICIUS", **k}); t += d
    seq = []
    for it in SEQ:
        if isinstance(it, str):   # optional soundbites found later (clips_extra.json) or a quote card instead
            e = EXTRA.get(it)
            if e: seq.append(C(e["src"], e["ss"], e["d"], e["name"], e["role"], [tuple(p) for p in e["phrases"]], **({"pools": e["pools"], "cut": 2.0} if e.get("pools") else {})))
            elif it == "MOU_CHIRINGUITO": seq.append(G(5.0, "mou_ph+diom_ph", "define", 2.5, **D_("MOURINHO", "EL CHIRINGUITO · AUGUST 2026", "“I didn't ask for him, but I wanted him.”")))
            elif it == "XABI_PRES": seq.append(G(5.6, "xabi_ph", "define", 2.8, **D_("XABI ALONSO", "PRESENTATION · MAY 26, 2025", "“I'm not coming with demands. I come wanting to work as a team and improve.”")))
            elif it == "MOU_EMOTIONS": seq.append(G(5.2, "mou_ph+vini_ph", "define", 2.6, **D_("EMOTIONS", "MOURINHO · AUGUST 2026", "Unfairly targeted, but he needs to manage his emotions better.")))
            continue
        seq.append(it)
    for it in seq:
        if it.get("sting"):
            add(4.6, "sting", gfx={"type": "sting", "title": "ARTETA TRIED TO SAVE VINICIUS", "sub": "TWO CHANCES TO CHANGE · ONE CHOICE"}); continue
        if it.get("card"):
            add(2.4, f"k{n:02d}", gfx={"type": "bigtext", "lines": [it["text"]], "sub": it["sub"], "bare": True}, pools=it["pools"], cut=1.2); n += 1; continue
        if it.get("gfxscene"):
            add(it["d"], f"g{n:02d}", gfx=it["gfx"], pools=it["pools"], cut=it["cut"]); n += 1; continue
        if it.get("clip"):
            if it["extra"].get("pools"):
                ex = dict(it["extra"]); pools = ex.pop("pools"); cut = ex.pop("cut", 1.6)
                add(it["d"], f"c{n:02d}", gfx=it["gfx"], pools=pools, cut=cut, nat={"src": R(it["src"]), "ss": it["ss"]}, **ex); n += 1; continue
            add(it["d"], f"c{n:02d}", gfx=it["gfx"], takes=[{"src": R(it["src"]), "ss": it["ss"], "slow": 1.0, "frames": round(it["d"] * FPS),
                "crop": it["crop"], "pillar": PILLAR.get(it["src"], "")}], nat={"src": R(it["src"]), "ss": it["ss"]}); n += 1; continue
        if it.get("music"): music.append({"track": it["music"], "start": t})
        f = it["line"] + ".mp3"; d = DUR[it["line"]] + 0.3; W = sum(p[0] for p in it["parts"])
        vo.append({"file": f, "start": t + 0.12, "dur": d - 0.3})
        for k, (w, pools, cut, gfx) in enumerate(it["parts"]):
            add(d * w / W, f"n{n:02d}", gfx=gfx, pools=pools, cut=cut, **({"text": TEXT[it["line"]], "vo0": t + 0.12, "vod": d - 0.3} if k == 0 else {})); n += 1
    add(12.0, "end", gfx={"type": "end"})
    for s in scenes: s["f0"] = round(s["start"] * FPS)
    for a, b in zip(scenes, scenes[1:]): a["nf"] = b["f0"] - a["f0"]
    scenes[-1]["nf"] = round(scenes[-1]["dur"] * FPS)
    for s in scenes:
        s["start"] = s["f0"] / FPS; s["dur"] = s["nf"] / FPS
        if s.get("pools"): s["takes"] = allocate(s["pools"], s["nf"], s.get("cut", 4.0))
        s["framed"] = "takes" in s and s["gfx"]["type"] in ("none", "stat", "word", "lower", "chips", "caps")
    total = (scenes[-1]["f0"] + scenes[-1]["nf"]) / FPS
    json.dump({"fps": FPS, "total": total, "scenes": scenes, "vo": vo, "music": music,
               "brand": "REAL MADRID · <b>VINICIUS</b>", "tagline": "ARTETA TRIED TO SAVE VINICIUS", "stingbg": "VINI",
               "endtitle": "VINI'S <span style=\"color:var(--amber)\">CHOICE</span>",
               "sources": "AS TV · NBC News NOW · Arsenal · fan footage"},
              open(f"{ROOT}/build/timeline.json", "w"), indent=1, ensure_ascii=False)
    tk = [x for s in scenes for x in s.get("takes", [])]
    print(f"{len(scenes)} scenes, {total/60:.2f} min, {len(tk)} takes, avg {sum(x['frames'] for x in tk)/25/len(tk):.2f}s, slow>1.3: {sum(1 for x in tk if x['slow'] > 1.3)}")
    real = sum(x["frames"] for x in tk if "/real/" in x["src"]) / max(1, sum(x["frames"] for x in tk))
    print(f"real footage share of takes: {real:.0%}")
    for s in scenes: print(f'{s["id"]} {s["start"]:7.2f} {s["dur"]:6.2f} {s["gfx"]["type"]:8s} {len(s.get("takes",[]))}')
if __name__ == "__main__": main()
