#!/usr/bin/env python3
"""Timeline for 'Zlatan Explained Brazil's Problem' (Becir format: narration beats interleaved with real soundbites)."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"
SHOTS = json.load(open(f"{ROOT}/build/shots.json"))
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
def sh(src, *idx): return [("shot", src, i) for i in idx]
def win(src, a, b): return [("win", src, a, b)]
A, J26, J25, F02, CRO, S71, NOR = "ancelotti_afp", "japan_2026_hl", "japan_2025_hl", "final_2002_fifa", "croatia_2022_fifa", "seven_one_fifa", "norway_cbs"
A25, A23, F70, F94, NC, R24, RU, VB, VF = "arg_bra_2025", "bra_arg_2023", "final_1970_fifa", "final_1994_fifa", "norway_crying", "raphinha_24s", "raphinha_uol", "vini_booed_as", "vini_fails"
REF, R9G, R10G, ROM, ZG, NED, BEL, FRA, N26, VB2, RZ = "ref_vini", "r9_goals", "r10_goals", "romario_goals", "zico_goals", "ned_2010", "bel_2018", "fra_2006", "nor_2026", "vini_best2", "raph_zico"
CROP = {RZ: "crop=iw*0.66:ih*0.66:iw*0.03:ih*0.2,", F70: "crop=iw*0.78:ih:iw*0.11:0,", VF: "crop=iw*0.84:ih*0.84:iw*0.16:ih*0.14,", FRA: "crop=iw*0.8:ih*0.8:0:ih*0.2,"}
PILLAR = {VB2: "crop=iw*0.34:ih*0.84:iw*0.33:0"}
POOLS = {
 "s71": sh(S71, 2, 4, 5, 7, 8, 3), "s71sad": win(S71, 108.4, 118.5),
 "vbest": win(VB2, 2, 30), "vinibest": sh(VF, 5, 4, 3),
 "viniboo": sh(VB, 1, 2) + sh(VF, 14) + sh(REF, 43, 142) + sh(VF, 1, 2, 11, 12) + sh(REF, 147),
 "vinireal": sh(REF, 142, 152) + sh(VF, 12, 7, 13, 11, 2), "diomande": sh(REF, 143, 123, 141),
 "india": sh(REF, 6, 5, 117, 115, 116), "proc": sh(REF, 33, 11) + win(REF, SHOTS[REF][41][0] + 0.1, SHOTS[REF][41][0] + 2.8), "clone": sh(REF, 51, 47) + win(REF, SHOTS[REF][41][0] + 0.1, SHOTS[REF][41][0] + 2.8),
 "virginia": sh(REF, 34, 75, 72, 11),
 "viniyellow": sh(REF, 9, 27, 28) + sh(A25, 16) + sh(J25, 2, 70, 62) + sh(J26, 8),
 "vinisad": sh(REF, 9, 28) + sh(J25, 2) + sh(A25, 16) + sh(J25, 70) + sh(REF, 87, 81) + sh(NC, 0),
 "stumble": win(VF, 139.6, 143.3), "misses": sh(VF, 7, 13, 18, 21) + sh(REF, 9, 87),
 "r9": sh(R9G, 7, 8, 11, 15, 17, 1, 0, 2, 5, 6, 14, 18), "r10": sh(R10G, 17, 16, 18, 13, 7, 12, 15, 14), "romario": sh(ROM, 1, 3, 4, 6, 5, 2), "zico": win(RZ, 168, 190),
 "cafu": sh(R10G, 14) + win(R9G, SHOTS[R9G][14][0] + 2.0, SHOTS[R9G][14][1] - 0.2) + sh(R9G, 18, 20),
 "arg25": sh(A25, 3, 4, 5, 13, 30, 32, 36, 39, 40, 15, 6), "raph25": sh(A25, 46, 7, 26, 34),
 "rpress": win(R24, 4, 100), "ruol": win(RU, 16, 55),
 "a23": sh(A23, 2, 3, 9, 8, 28, 41, 38, 25, 1, 4), "cro": sh(A25, 4, 6, 13, 15),
 "f94": sh(F94, 0, 43, 45, 30, 37, 20, 46), "f70": sh(F70, 3, 6, 7, 4),
 "today": sh(A, 10, 14, 15) + win(J26, 2, 50),
 "norwaycry": sh(NC, 0, 1), "norway": win(NOR, SHOTS[NOR][16][0] + 2, SHOTS[NOR][16][0] + 12) + win(NOR, SHOTS[NOR][26][0] + 2, SHOTS[NOR][26][0] + 12),
 "brunoface": sh(N26, 2), "nor26": sh(N26, 8, 10, 15, 5, 6, 14, 20, 18),
 "wc06": sh(FRA, 5, 13, 19, 4), "wc10": win(NED, 255, 268) + win(NED, 283, 290) + sh(NED, 21), "wc18": sh(BEL, 9, 17, 15, 7, 6),
 "neymar": sh(BEL, 15) + sh(NC, 1) + sh(N26, 18),
 "fall": sh(FRA, 5) + win(NED, 283, 290) + sh(BEL, 9) + sh(N26, 15) + sh(FRA, 19) + sh(BEL, 17) + sh(NC, 1) + sh(A25, 34) + sh(BEL, 15) + sh(N26, 10) + sh(A23, 38) + sh(J25, 2) + sh(A25, 37) + sh(NED, 21) + sh(J25, 70) + sh(J26, 17),
 "anc": sh(A, 8, 2, 3, 9, 11), "train": sh(A, 10, 14, 15, 11, 9), "wc": sh(A, 16, 17),
 "j26vini": win(J26, 207, 268) + sh(J26, 8, 6, 9, 10, 11, 7), "j26winner": win(J26, 362, 398),
 "j26end": win(J26, 401, 438) + win(J26, 441, 490) + sh(J26, 17, 15, 16), "j26score": sh(J26, 15, 16, 17),
}
APR, APS, APT, AP2, R9B, R10B = "ap_rio_71", "ap_sp_71", "ap_stadium_71", "ap_2002_fans", "r9_barca", "r10_barca"
_AP = "crop=iw*0.82:ih*0.82:0:ih*0.18,"
CROP.update({APR: _AP, APS: _AP, APT: _AP, AP2: "crop=iw*0.6:ih*0.6:iw*0.15:ih*0.32,", R9B: "crop=iw*0.8:ih*0.8:0:0,", R10B: "crop=iw*0.9:ih*0.9:0:ih*0.1,"})
PILLAR.clear()
_ap71 = sh(APR, 2, 9, 0, 8, 4, 11) + sh(APS, 3, 6) + sh(APT, 0, 2) + sh(APR, 1, 3, 7, 10) + sh(APS, 4, 2, 5) + sh(APT, 1)
_ap02 = sh(AP2, 1, 4, 3)
_r9b = sh(R9B, 11, 16, 10, 21, 14, 23, 31, 1, 3, 2); _r10b = sh(R10B, 0, 4, 5, 8, 15, 16, 17, 3, 13, 11)
POOLS.update({
 "s71": _ap71, "s71sad": sh(APR, 9, 8, 11), "vbest": sh(VF, 5, 4, 3),
 "r9": _r9b, "r10": _r10b, "romario": _r9b[5:] + _r10b[5:], "cafu": _ap02, "f94": _ap02, "f70": _ap02,
 "norwaycry": sh(APS, 3, 6) + sh(APR, 9, 4), "brunoface": sh(A, 16, 17), "nor26": sh(A, 16, 17, 8, 3),
 "wc06": _ap71, "wc10": _ap71, "wc18": _ap71, "neymar": sh(APR, 9, 4) + sh(APS, 6, 3),
 "fall": sh(APS, 3) + sh(A25, 34) + sh(APR, 8) + sh(A23, 38) + sh(J25, 2) + sh(APS, 6) + sh(A25, 37) + sh(J25, 70) + sh(APT, 2) + sh(A23, 25) + sh(APR, 4) + sh(A25, 7) + sh(J26, 17) + sh(APR, 11) + sh(APT, 0) + sh(APR, 1),
})
FIFA = [S71, F70, F94, F02, CRO, R9G, R10G, ROM, ZG, NED, BEL, FRA, N26, NC, VB2]
_items = {}; _cur = {}
def pool_items(name):
    if name not in _items:
        out = []
        for it in POOLS[name]:
            p = R(it[1])
            a, b = (it[2], it[3]) if it[0] == "win" else (SHOTS[it[1]][it[2]][0] + 0.12, SHOTS[it[1]][it[2]][1] - 0.12)
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
        slow = max(1.0, d / L); ss = a + (min(1.2, (L - d) / 2) if L > d else 0)
        takes.append({"src": p, "ss": round(ss, 2), "slow": round(slow, 3), "frames": frames, "crop": next((c for k, c in CROP.items() if p == R(k)), ""), "pillar": next((c for k, c in PILLAR.items() if p == R(k)), "")})
    return takes

E = R("espn_fc")
def C(src, ss, d, name, role, phrases, **k):
    return {"clip": True, "src": src, "ss": ss, "d": d, "extra": {a: b for a, b in k.items() if a != "crop"}, "crop": k.get("crop", ""), "gfx": {"type": "caps", "name": name, "role": role, "small": True, "phrases": [{"t0": a, "t1": b, "text": t, "q": 0} for a, b, t in phrases]}}
def P(w, pools, type_="none", cut=4.0, **p): return (w, pools, cut, {"type": type_, **p})
def L(i, *parts, music=None): return {"line": i, "parts": parts, "music": music}
def M(d, pools, cut): return {"montage": True, "d": d, "pools": pools, "cut": cut}
D_ = lambda term, full, body: dict(term=term, full=full, body=body, small=True)
SEQ = [
 {"cold": True, "src": R(APR), "ss": SHOTS[APR][2][0] + 0.2, "d": 3.2},
 L(0, P(1, "s71", "chips", 0.9, title="29 MINUTES", items=["11' · Müller", "23' · Klose", "24' · Kroos", "26' · Kroos", "29' · Khedira"], t0=.3)),
 L(1, P(1, "s71sad+" + "+".join(["fall"] * 15), "chips", 1.1, title="ROCK BOTTOM?", items=["2018 · Out to Belgium", "2022 · Out to Croatia", "2026 · Out to Norway"], t0=.45)),
 L(2, P(1, "j26end+viniboo+rpress+j26score+arg25", "word", 1.15, text="IT GOT WORSE", late=.05)),
 L(3, P(.3, "vbest", "lower", 7.0, name="VINÍCIUS JÚNIOR", role="The Best FIFA Men's Player · December 2024", late=.1),
      P(.25, "vinibest", "list", 2.6, tag="THE BEST FIFA 2024", title="THE VOTE", items=["1 · Vinícius Júnior · 48 pts", "2 · Rodri · 43 pts", "3 · Bellingham · 37 pts"], t0=.1),
      P(.45, "r9+r10+r9+r10+r9+r10", "chips", 1.7, title="THE HEIR OF", items=["Romário", "Ronaldo", "Ronaldinho"], t0=.3)),
 L(4, P(1, "viniboo", "word", 2.4, text="WHISTLED", sub="AT THE BERNABÉU", late=.3)),
 L("N0", P(.3, "vinireal", "stat", 2.6, big="1 GOAL", label="FIRST 8 MATCHES · HIS WORST START AS A STARTER", late=.3),
         P(.3, "diomande", "stat", 2.6, big="€100M+", label="SPENT ON A 19-YEAR-OLD IN HIS POSITION", late=.1),
         P(.4, "vinireal+diomande", "counter", 2.8, value=86, suffix="%", label="CHOSE THE TEENAGER OVER VINÍCIUS", sub="MARCA READERS' POLL · 50,000+ VOTES", t0=.45, sublate=.7)),
 L("N1", P(1, "india", "lower", 2.4, name="BRAZIL v INDIA", role="Vinícius is taken off at half-time", late=.55)),
 L(5, P(.3, "proc", "lower", 2.4, name="SUMMER 2026", role="A cosmetic procedure on his chin", late=.35),
      P(.4, "clone", "define", 2.6, **D_("BODY DOUBLE", "THE JOKE ONLINE · SUMMER 2026", "“The real Vini died in surgery. That one is a double.”")),
      P(.3, "clone+viniyellow", "list", 2.6, tag="REAL HEADLINES", title="KILLED AND REPLACED?", items=["“Was Vinícius killed and replaced?” · Daily Sports", "“It's a double!” · OneFootball"], t0=.12, lasthot=True)),
 L("N2", P(.55, "virginia", "lower", 2.2, name="OFF THE PITCH", role="A new face. A famous girlfriend. Millions of followers.", late=.1), P(.45, "vinisad", "none", 1.8)),
 L(6, P(1, "viniyellow", "none", 2.1)),
 M(3.6, "stumble", 3.6), M(4.4, "misses", 1.1),
 L(7, P(.45, "norwaycry+viniyellow", "word", 2.2, text="BAD FORM?", late=.08), P(.55, "r9+r10", "none", 2.0)),
 L(8, P(1, "j26score+s71sad", "word", text="WHAT HAPPENED?", late=.45)),
 {"sting": True},
 L("N3", P(1, "r10+r9+romario", "chips", 1.9, title="HELP THE CHANNEL GROW", items=["Like", "Subscribe", "Send it to a friend"], t0=.25), music="beat"),
 L(9, P(1, "raph25+rpress", "define", **D_("“BEAT THEM UP”", "RAPHINHA · MARCH 2025 · BEFORE ARGENTINA", "“On the pitch and off it, if necessary.”"))),
 L(10, P(1, "arg25", "stat", 2.4, big="4 – 1", label="ARGENTINA v BRAZIL · MARCH 25, 2025", late=.1)),
 L("N4a", P(1, "ruol+rpress", "lower", 3.4, name="JUNE 2025", role="Raphinha, on holiday, talks about the Club World Cup", late=.1)),
 C(R(RZ), 81.6, 7.6, "RAPHINHA", "June 2025", [(0.3, 7.4, "From my point of view, it's very bad to *give up my holidays* to play something you're forced to play.")], crop="crop=iw*0.66:ih*0.66:iw*0.15:ih*0.17,"),
 L("N4b", P(1, "zico", "lower", 2.9, name="ZICO", role="One of the greatest players in Brazil's history", late=.3)),
 C(R(RZ), 194.6, 11.0, "ZICO", "June 2025", [(0.3, 6.9, "If he had played the World Cups like everyone else, during his holidays,"), (7.1, 10.8, "*he wouldn't have made that statement.*")], crop="crop=iw*0.66:ih*0.66:iw*0.03:ih*0.2,"),
 L(12, P(.4, "rpress", "define", **D_("MINUTES", "RAPHINHA · NOVEMBER 2026", "“If he really counts on me, he knows he has to manage my minutes.”")),
       P(.6, "rpress+train", "stat", big="3", label="INJURIES IN EIGHT MONTHS", late=.05)),
 C(R(R24), 107.3, 11.0, "RAPHINHA", "Press conference · Singapore · November 2026", [(3.6, 10.8, "*24 SECONDS OF SILENCE*")], mute_music=True),
 L(13, P(1, "j26end", "word", text="SENT OFF", sub="THE CAPTAIN · BRAZIL v JAPAN", stamp=True, late=.5), music="drone"),
 L(14, P(.6, "nor26", "lower", 3.4, name="NORWAY 2–1 BRAZIL", role="World Cup 2026 · Round of 16 · Bruno Guimarães misses a penalty", late=.08), P(.4, "anc+train", "word", text="“IT HURTS A LOT”", late=.3)),
 L(15, P(.5, "j26vini", "stat", 3.2, big="2 GOALS", label="VINÍCIUS JÚNIOR · BRAZIL v JAPAN", late=.2), P(.5, "j26winner+j26end", "stat", big="3 – 2", label="JAPAN BEAT BRAZIL · TWICE IN 13 MONTHS", late=.1)),
 C(E, 80.6, 12.3, "", "ESPN FC · November 14, 2026", [(0.3, 6.9, "It used to be *smiles and samba.* It was the team to watch."), (7.7, 12.0, "Now that Brazil shirt is clearly *so heavy* for whoever wears it.")]),
 L(16, P(.3, "arg25", "none", 2.6), P(.25, "cro", "lower", name="QATAR 2022", role="Brazil go out. Argentina's fans celebrate.", late=.05),
       P(.45, "a23", "list", 3.4, tag="NOVEMBER 21, 2023 · MARACANÃ", title="BRAZIL 0–1 ARGENTINA", items=["Brazil's first home defeat in qualifying. Ever."], t0=.3, lasthot=True), music="beat"),
 L(17, P(1, "cafu", "chips", 3.2, title="THE CAPTAINS", items=["1994 · Dunga", "2002 · Cafu"], t0=.2), music="drone"),
 L(18, P(1, "today", "chips", title="BRAZIL TODAY", items=["Tattoos", "Hairdressers", "Followers"], t0=.1)),
 L(19, P(.5, "r9", "stat", 2.6, big="8 GOALS", label="RONALDO · WORLD CUP 2002", late=.45), P(.5, "r9+cafu", "define", 3.0, **D_("FAME", "THEN AND NOW", "Back then, fame came after the trophy. Today it comes first."))),
 L(20, P(.76, "cafu+cafu+cafu+cafu+r9+r9+r10", "chips", 3.5, title="FIVE STARS", items=["1958 · Pelé", "1962 · Garrincha", "1970 · The beautiful team", "1994 · Romário", "2002 · Ronaldo"], t0=.14), P(.24, "cafu", "stat", big="5 STARS", label="NO OTHER COUNTRY HAS FIVE", late=.1)),
 L(21, P(.3, "train+anc", "counter", value=1455, label="BRAZILIAN PLAYERS ABROAD · MOST IN THE WORLD", sub="CIES FOOTBALL OBSERVATORY · MAY 2026", t0=.25, sublate=.6),
       P(.4, "vinibest+train", "stat", big="16", label="AGE VINÍCIUS AND ENDRICK SIGNED FOR REAL MADRID", late=.1), P(.3, "ruol"), music="beat"),
 C(R(RU), 6.2, 9.0, "RAPHINHA", "Brazil captain · UOL Esporte · 2026", [(0.3, 8.8, "The affection from Brazilian fans is *different* from the people abroad who follow me.")]),
 C(R(RU), 56.2, 8.2, "RAPHINHA", "Brazil captain · UOL Esporte · 2026", [(0.3, 8.0, "It's natural. *Leaving Brazil very young,* not having a connection with any club.")]),
 L(22, P(.5, "r10", "define", 2.6, **D_("NO LOVE", "RONALDINHO · JUNE 2024", "“No love for the shirt. No fight. And above all, no football.”")), P(.5, "r10+today", "word", 2.6, text="IT WAS AN AD", sub="ALMOST NOBODY DISAGREED", late=.15)),
 L(23, P(1, "neymar+s71+cro+nor26+wc18+wc10", "chips", 2.6, title="ONE PLAYER", items=["2014 · Neymar injured · 7–1", "2022 · Neymar scores · out", "2026 · Worst World Cup since 1990"], t0=.28), music="drone"),
 C(E, 278.0, 10.7, "", "ESPN FC · November 14, 2026", [(0.2, 3.4, "When they win, they haven't played well enough."), (4.6, 6.6, "If they don't win, then everybody jumps on them."), (7.3, 10.5, "*There's nowhere for them to go.*")]),
 L(24, P(.35, "cafu", "lower", 2.2, name="ROMÁRIO", role="World champion · 1994", late=.2), P(.65, "j26end", "define", **D_("ROMÁRIO", "NOVEMBER 14, 2026", "“Ancelotti, that's enough. Pack your things and get out.”"))),
 L(25, P(.6, "anc+cafu", "counter", value=28, suffix=" YEARS", label="WITHOUT A WORLD CUP · IF BRAZIL DO NOT WIN IN 2030", sub="ANCELOTTI'S CONTRACT RUNS UNTIL 2030", t0=.3, sublate=.6),
       P(.4, "anc", "word", text="“WE HAVE A FUTURE”", late=.45), music="finale"),
 L(26, P(1, "train+today", "chips", title="WORLD CUP 2030", items=["Endrick · 23", "Estêvão · 23", "Vinícius · 30"], t0=.12)),
 L(27, P(.4, "s71+viniboo+rpress+j26score", "none", 2.0), P(.6, "s71sad+cafu+j26end", "word", text="2030?", late=.75)),
]
_T = [l.strip() for l in open(f"{ROOT}/v3/lines.txt") if l.strip()]
TEXT = {f"L{i:02d}": t for i, t in enumerate(_T[:28])}
TEXT.update({k: v for k, v in (l.strip().split("|", 1) for l in open(f"{ROOT}/v3/lines_new.txt") if l.strip())})
def key(i): return i if isinstance(i, str) else f"L{i:02d}"

def main():
    scenes = []; vo = []; music = [{"track": "drone", "start": 0}]; t = 0.0; n = 0
    def add(d, sid, **k):
        nonlocal t
        scenes.append({"id": sid, "start": t, "dur": d, "label": "", **k}); t += d
    def clip(src, ss, d, gfx, crop="", **k):
        nonlocal n
        add(d, f"c{n:02d}", gfx=gfx, takes=[{"src": src, "ss": ss, "slow": 1.0, "frames": round(d * FPS), "crop": crop, "pillar": ""}], nat={"src": src, "ss": ss}, **k); n += 1
    for it in SEQ:
        if it.get("cold"):
            clip(it["src"], it["ss"], it["d"], {"type": "none"}); scenes[-1]["takes"] = allocate("s71", round(it["d"] * FPS), 0.64); continue
        if it.get("sting"):
            add(4.6, "sting", gfx={"type": "sting", "title": "7–1 WASN'T THE BOTTOM", "sub": "WHAT HAPPENED TO THE BRAZILIAN NATIONAL TEAM"}); continue
        if it.get("clip"): clip(it["src"], it["ss"], it["d"], it["gfx"], it["crop"], **it["extra"]); continue
        if it.get("montage"):
            add(it["d"], f"m{n:02d}", gfx={"type": "none"}, pools=it["pools"], cut=it["cut"], label="BRAZIL · THE FALL"); n += 1; continue
        if it.get("music"): music.append({"track": it["music"], "start": t})
        f = key(it["line"]) + ".mp3"; d = dur(f"{ROOT}/assets/vo/{f}") + 0.3; W = sum(p[0] for p in it["parts"])
        vo.append({"file": f, "start": t + 0.12, "dur": d - 0.3})
        for k, (w, pools, cut, gfx) in enumerate(it["parts"]):
            add(d * w / W, f"n{n:02d}", gfx=gfx, pools=pools, cut=cut, label="BRAZIL · THE FALL", **({"text": TEXT[key(it["line"])], "vo0": t + 0.12, "vod": d - 0.3} if k == 0 else {})); n += 1
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
               "brand": "BRAZIL · <b>THE FALL</b>", "tagline": "7–1 WASN'T THE BOTTOM", "stingbg": "7–1", "endtitle": "BRAZIL · <span style=\"color:var(--amber)\">THE FALL</span>", "sources": "AP · AFP · CONMEBOL · ESPN FC · UOL Esporte · AS"},
              open(f"{ROOT}/build/timeline.json", "w"), indent=1, ensure_ascii=False)
    tk = [x for s in scenes for x in s.get("takes", [])]
    bad = sorted({x['src'].split('/')[-1] for x in tk if any(x['src'] == R(k) for k in FIFA)}); assert not bad, bad
    print(f"{len(scenes)} scenes, {total/60:.2f} min, {len(tk)} takes, avg {sum(x['frames'] for x in tk)/25/len(tk):.2f}s")
    for s in scenes: print(f'{s["id"]} {s["start"]:7.2f} {s["dur"]:6.2f} {s["gfx"]["type"]:8s} {len(s.get("takes",[]))}')
if __name__ == "__main__": main()
