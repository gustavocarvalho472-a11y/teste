#!/usr/bin/env python3
"""Timeline for 'Ferguson Told Them To Stand By The Manager. They Never Did.' (Becir format, narration beats + real soundbites)."""
import json, os, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__)); FPS = 25
R = lambda n: f"{ROOT}/assets/real/{n}.mp4"
SHOTS = json.load(open(f"{ROOT}/build/shots.json"))
DUR = json.load(open(f"{ROOT}/assets/vo/durations.json"))
def sh(src, *idx): return [("shot", src, i) for i in idx]
def win(src, a, b): return [("win", src, a, b)]
def ph(*names): return [("photo", f"{ROOT}/assets/photos/{n}.jpg") for n in names]

FL, FS, FG, FA, FI, ITV = "fergie_line", "fergie_speech", "fergie_final_game", "fergie_aljazeera", "fergie_first_interview", "fergie_itv_dressing"
MG, RH, AM, AR, SP, MOY = "mourinho_greatest", "rangnick_heart", "amorim_manager", "amorim_rants_sky", "same_problems_hayters", "moyes_sacked"
PA, PP, PSP, LFC, LFC4 = "poch_arrival", "poch_presser_sky", "poch_spurs_presser", "lfc_parade_hayters", "lfc_parade_4k"
# crops: remove broadcaster bugs / fan-channel logos / burned captions, or zoom into a wide shot
CROP = {FA: "crop=iw*0.88:ih*0.86:iw*0.12:0,", MOY: "crop=iw*0.86:ih*0.86:0:ih*0.14,", PA: "crop=iw*0.8:ih*0.8:iw*0.2:ih*0.2,",
        PP: "crop=iw*0.38:ih*0.38:iw*0.285:ih*0.36,", PSP: "crop=iw*0.55:ih*0.55:iw*0.03:ih*0.02,", FI: "crop=ih*4/3:ih:(iw-ih*4/3)/2:0,", RH: "crop=iw*0.8:ih*0.8:iw*0.1:0,"}
PILLAR = {}
POOLS = {
 # Ferguson's farewell, 12 May 2013 (Sky Sports Retro, one continuous camera)
 "speech_wide": win(FS, 46, 78) + win(FS, 96, 118) + win(FS, 128, 142),
 "speech_close": win(FS, 236, 268) + win(FS, 168, 190) + win(FS, 150, 158),
 "otcrowd": win(FS, 40.5, 46.5) + win(FS, 86.5, 94) + win(FS, 206, 214) + win(FS, 312, 318),
 "players13": win(FS, 80, 86) + win(FS, 120, 126) + win(FS, 158, 166) + win(FS, 190, 198) + win(FS, 222, 228) + win(FS, 272, 284),
 "fergexit": win(FS, 296, 310) + win(FS, 334, 346),
 "fg_int": win(FG, 8, 30) + win(FG, 126, 140) + win(FG, 278, 290),
 # Al Jazeera, retirement report
 "fa_banner": win(FA, 0.3, 4.4), "fa_statue": win(FA, 13.6, 19.6), "fa_portrait": win(FA, 33.2, 37.2), "fa_ot": win(FA, 44.3, 48.6),
 "fa_90s": win(FA, 64.2, 72.6), "fa_trophies": win(FA, 72.8, 75.2), "fa_fans": win(FA, 79.5, 88.0), "fa_train13": win(FA, 88.3, 92.6),
 # 1986: Ferguson's first interview at Old Trafford, and the crowd
 "fi86": win(FI, 2, 58) + win(FI, 72, 114), "fi86crowd": win(FI, 59.6, 71.5),
 # ITV archive, 1990s
 "itv_ferg": sh(ITV, 16, 26, 19, 29, 23, 30, 35, 38, 40, 14, 20, 7),
 "itv_young": sh(ITV, 43, 44, 45, 25, 57, 11, 12), "itv_cantona": sh(ITV, 63, 66, 68), "itv_ole": sh(ITV, 17),
 # managers since
 "moyes": sh(MOY, 6, 1, 2, 0, 9, 4, 8), "statue": sh(MOY, 5),
 "mou": win(MG, 10, 60) + win(SP, 0.5, 20) + win(SP, 39.5, 60) + win(SP, 65, 117) + win(MG, 120, 160),
 "ran": sh(RH, 1, 2, 3) + win(SP, 124, 195) + win(SP, 202, 241),
 "tenhag": win(SP, 247, 270) + win(SP, 273, 284),
 "amo": win(AR, 0.5, 19) + win(SP, 286, 334) + win(AR, 21, 41) + win(AR, 72, 98) + win(SP, 338, 380) + win(AR, 100, 142),
 # Pochettino
 "poch_now": sh(PA, 11, 12, 13, 10), "poch_pp": win(PP, 20, 1420), "poch_spurs": win(PSP, 1, 46),
 "lfc": sh(LFC, 1, 7, 8, 13, 2) + sh(LFC4, 0),
}
POOLS["glory"] = POOLS["fa_trophies"] + POOLS["itv_cantona"] + POOLS["fa_fans"] + POOLS["players13"][:2] + POOLS["fa_90s"] + POOLS["fa_banner"]

_items = {}; _cur = {}
def pool_items(name):
    if name not in _items:
        out = []
        for it in POOLS[name]:
            if it[0] == "photo": out.append((it[1], 0.0, 30.0)); continue
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
        slow = max(1.0, d / L); ss = 0.0 if p.endswith(".jpg") else a + (min(1.2, (L - d) / 2) if L > d else 0)
        takes.append({"src": p, "ss": round(ss, 2), "slow": round(slow, 3), "frames": frames, "crop": next((c for k, c in CROP.items() if p == R(k)), ""), "pillar": next((c for k, c in PILLAR.items() if p == R(k)), "")})
    return takes

def C(src, ss, d, name, role, phrases, **k):
    return {"clip": True, "src": src, "ss": ss, "d": d, "extra": {a: b for a, b in k.items() if a != "crop"}, "crop": k.get("crop", CROP.get(src, "")),
            "gfx": {"type": "caps", "name": name, "role": role, "small": True, "phrases": [{"t0": a, "t1": b, "text": t, "q": 0} for a, b, t in phrases]}}
def P(w, pools, type_="none", cut=4.0, **p): return (w, pools, cut, {"type": type_, **p})
def L(i, *parts, music=None): return {"line": i, "parts": parts, "music": music}
def M(d, pools, cut): return {"montage": True, "d": d, "pools": pools, "cut": cut}
D_ = lambda term, full, body: dict(term=term, full=full, body=body, small=True)
SEQ = [
 M(3.2, "glory", 0.55),
 C(FL, 4.6, 15.6, "SIR ALEX FERGUSON", "Old Trafford · May 12, 2013", [(0.3, 5.0, "When we had bad times here, the club stood by me."), (6.2, 9.9, "All my staff stood by me. The players stood by me."), (10.2, 15.4, "Your job now is to *stand by our new manager.*")]),
 L("B00", P(1, "speech_wide+otcrowd+fergexit", "lower", 1.3, name="MAY 12, 2013", role="Ferguson's last game at Old Trafford", late=.25)),
 L("B01", P(.55, "moyes+fa_ot+mou+itv_ole+tenhag+amo+otcrowd", "chips", 0.9, title="7 SACKINGS", items=["2014 · Moyes", "2016 · Van Gaal", "2018 · Mourinho", "2021 · Solskjær", "2024 · Ten Hag", "2026 · Amorim", "2026 · Carrick"], t0=.08),
      P(.45, "poch_pp+fi86", "lower", 1.2, name="MAURICIO POCHETTINO", role="Manager No. 8 since Ferguson", late=.15)),
 L("B02", P(1, "fi86+poch_spurs+itv_young+poch_now", "chips", 1.2, title="SAME START", items=["A club sinking down the table", "Kids nobody had heard of", "Years without a trophy"], t0=.12)),
 L("B03", P(.5, "fi86+fg_int", "word", 1.3, text="UNITED WAITED", sub="FOR FERGUSON", late=.12), P(.5, "poch_now+lfc", "stat", 1.3, big="ANFIELD", label="SATURDAY, NOVEMBER 22 · POCHETTINO'S FIRST GAME", late=.08)),
 {"sting": True},
 L("B04", P(1, "otcrowd+players13+fa_fans", "chips", 1.8, title="HELP THE CHANNEL GROW", items=["Like", "Subscribe", "Send it to a United fan"], t0=.2), music="beat"),
 L("B05", P(.45, "fi86", "lower", 2.6, name="ALEX FERGUSON", role="Arrives from Aberdeen · November 1986", late=.1), P(.55, "fi86crowd+fi86", "stat", 2.6, big="21ST", label="MANCHESTER UNITED · OUT OF 22 TEAMS", late=.1)),
 L("B06", P(.5, "itv_ferg", "none", 2.6), P(.5, "fi86crowd+itv_ferg", "define", 3.0, **D_("TA-RA FERGIE", "BANNER AT OLD TRAFFORD · DECEMBER 1989", "“Three years of excuses… ta-ra Fergie.”"))),
 L("B07", P(1, "fa_trophies+itv_cantona+fa_90s+fa_fans", "counter", 2.2, value=38, label="TROPHIES · FERGUSON AT MANCHESTER UNITED", sub="THE FIRST · FA CUP · MAY 1990", t0=.3, sublate=.62)),
 L("B08", P(1, "poch_pp+poch_spurs", "lower", 2.6, name="MAURICIO POCHETTINO", role="2009 · Espanyol's new coach, aged 36", late=.25)),
 L("B09", P(1, "poch_pp+poch_spurs", "list", 3.0, tag="FEBRUARY 2009 · CAMP NOU", title="BARCELONA 1–2 ESPANYOL", items=["Guardiola's Barça: the treble that season", "Espanyol: bottom of La Liga", "First win at the Camp Nou in 27 years"], t0=.25, lasthot=True)),
 L("B10", P(1, "itv_young+itv_ferg", "chips", 2.0, title="THE SAME BET", items=["Ferguson · the Class of '92", "Pochettino · a dozen academy debuts"], t0=.35)),
 L("B11", P(1, "poch_spurs+poch_pp", "chips", 2.4, title="SOUTHAMPTON", items=["Newly promoted · a pressing machine", "Luke Shaw, 17 · later sold to United"], t0=.3)),
 L("B12", P(1, "poch_spurs+poch_pp", "chips", 2.4, title="TOTTENHAM", items=["Harry Kane · No. 9 at 21", "Dele Alli · £5m from MK Dons", "2019 · Champions League final"], t0=.15)),
 L("B13", P(.42, "fi86+itv_ferg", "word", 2.2, text="TIME", sub="FERGUSON GOT IT", late=.15), P(.28, "poch_spurs", "word", text="NO TROPHY", sub="POCHETTINO · IN ENGLAND", late=.1),
      P(.3, "poch_spurs+poch_pp", "stat", big="14TH", label="TOTTENHAM WHEN HE WAS SACKED · NOV 2019", late=.1)),
 L("B14", P(1, "poch_pp", "chips", 2.4, title="AFTER SPURS", items=["PSG · trophies, but no press", "Chelsea · one season", "USA · 2024–2026"], t0=.22)),
 L("B15", P(.55, "fg_int+fa_portrait", "define", **D_("FEB 2016", "FERGUSON, AS QUOTED BY DAVID LAMMY MP", "Pochettino is the best manager in the Premier League.")),
      P(.45, "poch_spurs+poch_pp", "define", **D_("JAN 2019", "POCHETTINO ON FERGUSON", "“The best manager in the history of football.”"))),
 L("B16", P(1, "moyes", "word", 2.4, text="UNDER 10 MONTHS", sub="FERGUSON'S OWN CHOICE", late=.35)),
 L("B17", P(.5, "moyes", "lower", 2.4, name="DAVID MOYES", role="2013–2014 · “The Chosen One”", late=.1), P(.5, "moyes+statue", "stat", big="APRIL 2014", label="SACKED AFTER LOSING AT EVERTON", late=.15)),
 L("B18", P(1, "fa_ot+otcrowd+fa_fans", "define", **D_("VAN GAAL", "MANCHESTER UNITED · 2014–2016", "The opposite of Ferguson: spreadsheets, patterns, slow football."))),
 L("B19", P(1, "fa_fans+otcrowd", "stat", 2.4, big="2 DAYS", label="FROM FA CUP WIN TO SACKING · MAY 2016", late=.3)),
 L("B20", P(.6, "mou", "lower", 2.6, name="JOSÉ MOURINHO", role="2016–2018 · League Cup · Europa League", late=.1), P(.4, "mou", "stat", big="2ND", label="PREMIER LEAGUE · 2017–18", late=.1)),
 C(MG, 338.0, 12.4, "JOSÉ MOURINHO", "Press conference · August 31, 2018", [(0.1, 4.2, "Not small titles, not small countries. *Eight proper titles.*"), (4.3, 12.2, "My second position last season is *one of my greatest achievements* in football.")]),
 L("B21", P(.45, "mou", "stat", 2.4, big="DEC 2018", label="MOURINHO SACKED", late=.05), P(.55, "itv_ole+speech_close", "lower", 2.6, name="OLE GUNNAR SOLSKJÆR", role="A Ferguson player · manager 2018–2021", late=.05)),
 L("B22", P(1, "otcrowd+fa_fans", "stat", 2.6, big="4–1", label="WATFORD v MAN UNITED · NOV 2021 · SOLSKJÆR'S LAST GAME", late=.25)),
 L("B23", P(1, "ran", "lower", 2.6, name="RALF RANGNICK", role="Interim manager · 2021–2022", late=.3)),
 C(RH, 37.0, 8.9, "RALF RANGNICK", "April 2022", [(0.1, 3.9, "In medicine you would see this is *an operation at the open heart.*"), (4.0, 8.7, "This is also something that *not only one single person as a manager* can do.")]),
 L("B24", P(.35, "ran", "none", 2.4), P(.65, "speech_close+otcrowd", "word", 2.6, text="WHO DESERVED MORE TIME?", sub="TELL ME IN THE COMMENTS", late=.05)),
 L("B25", P(1, "mou+tenhag+amo", "word", 1.6, text="THEY WIN. THEN THEY'RE GONE.", late=.45), music="drone"),
 L("B26", P(1, "tenhag+fa_fans", "list", 3.0, tag="THE PATTERN", title="WIN, THEN OUT", items=["2016 · Van Gaal: FA Cup → sacked 2 days later", "2023 · Ten Hag: League Cup", "2024 · FA Cup → new deal → sacked in October"], t0=.1, lasthot=True)),
 L("B27", P(.55, "amo", "lower", 2.6, name="RÚBEN AMORIM", role="2024–2026 · Europa League final lost in Bilbao", late=.1), P(.45, "amo", "stat", big="15TH", label="WORST FINISH SINCE RELEGATION IN 1974", late=.1)),
 L("B28", P(1, "amo", "none", 2.2)),
 C(AM, 8.9, 13.8, "RÚBEN AMORIM", "After Leeds 1–1 Man United · January 4, 2026", [(0.2, 6.0, "I came here to be *the manager of Manchester United,* not to be the coach of Manchester United."), (6.2, 13.6, "My name is not Tuchel, it's not Conte, it's not Mourinho, but *I'm the manager* of Manchester United.")]),
 L("B29", P(.45, "players13+speech_close", "word", 2.6, text="THE CRUELLEST", late=.1), P(.55, "otcrowd+fa_fans", "chips", 2.4, title="CARRICK · 2026", items=["January · interim", "11 wins in 16", "Champions League", "May · two-year deal"], t0=.06)),
 L("B30", P(.4, "otcrowd+fa_fans", "stat", 2.6, big="18TH", label="NOVEMBER 12, 2026 · CARRICK SACKED", late=.2), P(.6, "moyes+mou+tenhag+amo", "word", 1.2, text="2 SACKED IN 1 YEAR", sub="A FIRST IN 148 YEARS", late=.35)),
 L("B31", P(1, "lfc", "word", 2.2, text="OFF THEIR PERCH?", late=.45)),
 L("B32", P(1, "lfc", "list", 3.0, tag="LIVERPOOL", title="THEY WAITED", items=["2015 · Klopp hired", "2019 · Champions League", "2020 · Premier League"], t0=.15), music="beat"),
 L("B33", P(1, "lfc", "counter", 2.6, value=20, label="LIVERPOOL'S ENGLISH TITLES · LEVEL WITH UNITED", sub="ARNE SLOT · CHAMPION IN HIS FIRST SEASON · 2025", t0=.3, sublate=.6)),
 L("B34", P(.6, "fa_statue+otcrowd", "none", 2.4), P(.4, "speech_close", "word", text="THEY STOOD BY THEIR MANAGER", late=.1)),
 L("B35", P(1, "poch_now+poch_pp", "list", 3.0, tag="POCHETTINO AND UNITED", title="THE NEAR MISSES", items=["2016 · United choose Mourinho", "2018 · Favourite · United keep Solskjær", "2021 · Linked again · Rangnick comes in", "2022 · Last two · United pick Ten Hag"], t0=.1), music="drone"),
 L("B36", P(.5, "poch_now+poch_pp", "stat", 2.4, big="NO. 8", label="MANAGER SINCE FERGUSON", late=.2), P(.5, "poch_pp+lfc", "stat", big="18TH", label="THE TEAM HE INHERITS · FIRST GAME AT ANFIELD", late=.15)),
 L("B37", P(.5, "fi86+itv_ferg", "stat", 2.4, big="3½ YEARS", label="FERGUSON BEFORE HIS FIRST TROPHY", late=.05), P(.5, "poch_pp", "stat", big="3 MONTHS?", label="POCHETTINO", late=.05)),
 L("B38", P(1, "ran", "define", **D_("OPEN HEART", "RALF RANGNICK · APRIL 2022", "“Not something one single person as a manager can do.”"))),
 L("B39", P(1, "poch_now+poch_pp", "word", 2.2, text="YES OR NO?", sub="DOES POCHETTINO LAST THE SEASON? · COMMENT BELOW", late=.15)),
 L("B40", P(1, "speech_wide+fergexit", "none", 2.6), music="finale"),
 L("B41", P(1, "otcrowd+fa_fans", "word", 2.0, text="THE CLUB NEVER DID.", late=.5)),
 L("B42", P(.4, "lfc+poch_now", "lower", 2.6, name="SATURDAY · ANFIELD", role="Manager No. 8 · his first game", late=.1), P(.6, "fergexit+fa_statue+speech_close", "none", 2.6)),
 C(FL, 14.7, 5.6, "", "", [(0.2, 5.4, "Your job now is to *stand by our new manager.*")]),
]
TEXT = {i: t for i, t in (l.strip().split("|", 1) for l in open(f"{ROOT}/lines.txt") if "|" in l)}

def main():
    scenes = []; vo = []; music = [{"track": "drone", "start": 0}]; t = 0.0; n = 0
    def add(d, sid, **k):
        nonlocal t
        scenes.append({"id": sid, "start": t, "dur": d, "label": "THE GHOST OF 2013", **k}); t += d
    def clip(src, ss, d, gfx, crop="", **k):
        nonlocal n
        add(d, f"c{n:02d}", gfx=gfx, takes=[{"src": src, "ss": ss, "slow": 1.0, "frames": round(d * FPS), "crop": crop, "pillar": ""}], nat={"src": src, "ss": ss}, **k); n += 1
    for it in SEQ:
        if it.get("sting"):
            add(4.6, "sting", gfx={"type": "sting", "title": "THE GHOST OF 2013", "sub": "FERGUSON TOLD THEM TO STAND BY THE MANAGER"}); continue
        if it.get("clip"): clip(R(it["src"]), it["ss"], it["d"], it["gfx"], it["crop"], **it["extra"]); continue
        if it.get("montage"):
            add(it["d"], f"m{n:02d}", gfx={"type": "none"}, pools=it["pools"], cut=it["cut"]); n += 1; continue
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
               "brand": "MAN UNITED · <b>THE GHOST</b>", "tagline": "THE GHOST OF 2013", "stingbg": "2013",
               "endtitle": "THE GHOST <span style=\"color:var(--amber)\">OF 2013</span>", "sources": "Sky Sports · Al Jazeera · AP · ITV · The Independent · HaytersTV"},
              open(f"{ROOT}/build/timeline.json", "w"), indent=1, ensure_ascii=False)
    tk = [x for s in scenes for x in s.get("takes", [])]
    print(f"{len(scenes)} scenes, {total/60:.2f} min, {len(tk)} takes, avg {sum(x['frames'] for x in tk)/25/len(tk):.2f}s, slow>1.3: {sum(1 for x in tk if x['slow'] > 1.3)}")
    for s in scenes: print(f'{s["id"]} {s["start"]:7.2f} {s["dur"]:6.2f} {s["gfx"]["type"]:8s} {len(s.get("takes",[]))}')
if __name__ == "__main__": main()
