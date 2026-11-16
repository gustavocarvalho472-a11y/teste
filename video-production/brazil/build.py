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
POOLS = {
 "anc": sh(A, 8, 2, 3, 9, 11),
 "train": sh(A, 10, 14, 15, 11, 9),
 "wc": sh(A, 16, 17),
 "j26start": win(J26, 2, 50) + sh(J26, 1, 3, 4),
 "j26goals": sh(J26, 1) + win(J26, 70, 100) + sh(J26, 3, 4),
 "j26vini": win(J26, 207, 268) + sh(J26, 8, 6, 9, 10, 11, 7),
 "j26winner": win(J26, 362, 398),
 "j26end": win(J26, 401, 438) + win(J26, 441, 490) + sh(J26, 17, 15, 16),
 "j26score": sh(J26, 15, 16, 17),
 "j25": sh(J25, 56, 58, 53, 63, 66, 54, 67, 69, 59, 62, 70, 71),
 "j25sad": sh(J25, 70, 62, 59, 2),
 "f2002": sh(F02, 47, 46, 9, 1, 3, 6, 23, 12, 17),
 "elim": sh(S71, 2, 9, 4, 8, 7) + sh(CRO, 37, 38, 43, 47),
 "neymar": sh(CRO, 31, 46, 41, 38),
 "norway": win(NOR, SHOTS[NOR][16][0] + 2, SHOTS[NOR][16][0] + 12) + win(NOR, SHOTS[NOR][26][0] + 2, SHOTS[NOR][26][0] + 12) + sh(NOR, 37),
}
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
        takes.append({"src": p, "ss": round(ss, 2), "slow": round(slow, 3), "frames": frames, "crop": ""})
    return takes

Z = R("zlatan_fox"); E = R("espn_fc"); ZC = "crop=iw:iw*0.667:0:ih*0.24"
def C(src, ss, d, name, role, phrases, pillar=""):
    return {"clip": True, "src": src, "ss": ss, "d": d, "pillar": pillar, "gfx": {"type": "caps", "name": name, "role": role, "small": True,
            "phrases": [{"t0": a, "t1": b, "text": t, "q": 0} for a, b, t in phrases]}}
def N(vtext, pools, type_="none", cut=4.0, music=None, **p): return {"text": vtext, "pools": pools, "cut": cut, "music": music, "gfx": {"type": type_, **p}}
ZL = ("ZLATAN IBRAHIMOVIĆ", "FOX Sports · June 13, 2026")
SEQ = [
 C(Z, 12.9, 11.5, *ZL, [(0.2, 2.4, "I had him as a *manager, not coach.*"), (2.6, 8.9, "The coach will tell the player how to move, where to go, and how to play."), (9.1, 11.3, "A manager will *manage the player.*")], ZC),
 ("vo", 1),
 N("June 13th, 2026. One hour before Brazil's first match at the World Cup, Zlatan Ibrahimović says this about Carlo Ancelotti on American television. He means it as a compliment.", "wc+anc", "lower", name="CARLO ANCELOTTI", role="Brazil head coach", late=0.45),
 N("Five months later, in Singapore, Japan beat Brazil three-two. In stoppage time. With Ancelotti sent off.", "j26winner+j26end", "stat", big="3 – 2", label="JAPAN BEAT BRAZIL · NOVEMBER 14, 2026", late=0.35),
 N("It is the second time Japan have beaten Brazil in thirteen months. Before that, in fourteen matches, it had never happened. And suddenly, what Zlatan said that afternoon does not sound like praise anymore.", "j26score+j25+j26end", "word", text="TWICE", sub="IN THIRTEEN MONTHS", late=0.08),
 {"sting": True},
 N("Brazil have not won the World Cup since 2002. Yokohama. Ronaldo, Rivaldo, Ronaldinho.", "f2002", "stat", big="2002", label="BRAZIL'S LAST WORLD CUP", cut=2.6, music="beat"),
 N("Since then: out to France. Out to the Netherlands. Seven-one against Germany, at home. Out to Belgium. Out to Croatia, on penalties.", "elim", "chips", title="SINCE THEN", items=["2006 · France", "2010 · Netherlands", "2014 · Germany 7–1", "2018 · Belgium", "2022 · Croatia"], t0=0.12, cut=3.0),
 N("For most of those years, Brazil had one plan. Give the ball to Neymar.", "neymar", "word", text="ONE PLAN", late=0.3),
 N("So in 2025, Brazil hire the man who has managed more stars than anyone alive. Carlo Ancelotti. Five Champions League titles. And Zlatan, who played for him in Paris, explains exactly how he does it.", "anc+train", "stat", big="5", label="CHAMPIONS LEAGUE TITLES · CARLO ANCELOTTI", late=0.42),
 C(Z, 26.2, 2.3, *ZL, [(0.15, 2.2, "We had two right backs.")], ZC),
 C(Z, 34.2, 12.8, *ZL, [(0.2, 3.7, "He goes to the first one: *he's my best right back.*"), (4.2, 7.9, "Then to the other one: *also my best right back.*"), (8.2, 9.9, "And he would play them each week."), (10.2, 12.6, "*That is what a manager does.*")], ZC),
 N("The studio laughs. That is what a manager does. He keeps everyone happy. Zlatan finishes with one more line.", "train+anc"),
 C(Z, 58.6, 3.3, *ZL, [(0.2, 3.2, "I'm pretty sure he will *do good* this time too.")], ZC),
 N("There were signs before that. October 2025, Tokyo. Brazil lead Japan two-nil at half-time. They lose three-two. Japan's first win over Brazil, ever. It is Ancelotti's first defeat. It is called an accident.", "j25", "stat", big="3 – 2", label="JAPAN v BRAZIL · TOKYO · OCTOBER 2025", late=0.42, cut=3.2, music="drone"),
 N("In May 2026, before he has coached a single World Cup match, the federation extends his contract to 2030. Nine and a half million euros a year. The best-paid national team coach in the world.", "anc+train", "counter", prefix="€", value=9500000, label="PER YEAR · CONTRACT EXTENDED TO 2030", sub="THE BEST-PAID NATIONAL TEAM COACH IN THE WORLD", t0=0.42, sublate=0.72),
 N("Seven weeks later, at MetLife Stadium, Erling Haaland scores twice. Norway two, Brazil one. Round of sixteen. Brazil's worst World Cup since 1990. Neymar comes off the bench, scores a penalty, and it is not enough.", "wc+norway+neymar", "list", tag="WORLD CUP 2026 · ROUND OF 16", title="NORWAY 2–1 BRAZIL", items=["Haaland scores twice", "Brazil's worst World Cup since 1990", "Neymar scores from the bench. Not enough."], t0=0.18, lasthot=True),
 ("vo", 2),
 N("And then, for a few weeks, it looks fine. Brazil beat Australia four-two. They beat India four-nil. The manager says he is happy with the young players. That lasts until November 14th.", "train+anc", "chips", title="AFTER THE WORLD CUP", items=["Australia 1–1", "Australia 4–2", "India 4–0"], t0=0.2, music="beat"),
 N("Singapore. Raphinha wears the number ten and the captain's armband. Kubo scores. Nakamura scores. Japan two, Brazil nil.", "j26start+j26goals", "stat", big="2 – 0", label="JAPAN v BRAZIL · SINGAPORE · 19 MINUTES", late=0.72, cut=3.0),
 N("Then Vinícius hits one from outside the box into the top corner. Then he scores again. Two-two. Endrick hits the post. Brazil are on top. This is the part of the story where Brazil used to win.", "j26vini", "stat", big="2 – 2", label="VINÍCIUS JÚNIOR · TWO GOALS", late=0.38, cut=3.2),
 N("In the ninety-first minute, João Gomes loses the ball in midfield. Brazil's players stop and appeal for a foul. Japan do not stop.", "j26winner", "lower", name="90+1'", role="Brazil appeal for a foul. Japan play on.", late=0.1, cut=5.0),
 N("Three-two. Ancelotti is sent off. Raphinha is sent off. After the match, the manager blames the referee.", "j26end", "word", text="SENT OFF", sub="ANCELOTTI AND RAPHINHA", stamp=True, late=0.22),
 N("But look at what happened. Brazil's best player scored two brilliant goals. And Brazil still lost to Japan. In Brazil, one newspaper writes that after twenty-one matches, this team still has no collective identity. That it depends on individual flashes. Read that again. Then go back to June.", "j26vini+j25sad+j26score", "define", term="NO IDENTITY", full="BRAZILIAN PRESS · AFTER 21 MATCHES", body="“Still no collective identity. It depends on individual flashes.”", small=True, music="drone"),
 C(Z, 17.2, 5.0, *ZL, [(0.2, 4.8, "The coach will tell the player *how to move, where to go, and how to play.*")], ZC),
 C(E, 80.6, 12.3, "", "ESPN FC · November 14, 2026", [(0.3, 6.9, "It used to be *smiles and samba.* It was the team to watch."), (7.7, 12.0, "Now that Brazil shirt is clearly *so heavy* for whoever wears it.")]),
 N("These are the numbers of Ancelotti's Brazil. Twenty-one matches. Five defeats. Two of them to Japan. One World Cup, and the country's worst finish in thirty-six years. The best-paid coach in international football. And after eighteen months, nobody can say how his team plays.", "anc+j25sad+j26end+train", "list", tag="ANCELOTTI'S BRAZIL", title="THE NUMBERS", items=["21 matches · 5 defeats", "2 defeats to Japan", "Worst World Cup in 36 years", "The best-paid coach in international football"], t0=0.1, lasthot=True),
 N("In Brazil, the reaction is not analysis. It is Romário. The man who won them the 1994 World Cup.", "j26end+j26score", "define", term="ROMÁRIO", full="1994 WORLD CUP WINNER · NOVEMBER 14, 2026", body="“Ancelotti, that's enough. Pack your things and get out.”", small=True),
 N("The last World Cup came twenty-four years after Yokohama. The next one is in 2030. Twenty-eight. And the contract Ancelotti signed in May runs until the day it ends.", "f2002+neymar+anc", "counter", value=28, suffix=" YEARS", label="WITHOUT A WORLD CUP · IF BRAZIL DO NOT WIN IN 2030", sub="ANCELOTTI'S CONTRACT RUNS UNTIL 2030", t0=0.3, sublate=0.62),
 C(E, 278.0, 10.7, "", "ESPN FC · November 14, 2026", [(0.2, 3.4, "When they win, they haven't played well enough."), (4.6, 6.6, "If they don't win, then everybody jumps on them."), (7.3, 10.5, "*There's nowhere for them to go.*")]),
 N("Ancelotti says his team played the way he wanted for seventy minutes. Zlatan was not criticising him. He was describing the best manager of stars the game has ever seen. But Brazil had twenty-four years of stars. What it never had was someone to tell them how to move, where to go, and how to play. So did Brazil hire the wrong man? Or the right man for a problem it does not have?", "j26end+anc+f2002+neymar+j26score+j25sad", "word", text="THE WRONG MAN?", late=0.86, music="finale"),
]

def silences(p):
    out = subprocess.run(["ffmpeg", "-i", p, "-af", "silencedetect=noise=-34dB:d=0.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    return list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]))
def weight(t): return sum(3.2 if c.isdigit() else 1 for c in t) + 6 * t.count(".") + 3 * t.count(",")
def beat_cuts(path, texts):
    """Align every sentence end to a pause (DP), then keep paragraph ends."""
    d = dur(path); sil = [(s, e) for s, e in silences(path) if e - s >= 0.3 and s > 0.3 and e < d - 0.2]
    sents = []; pend = []
    for t in texts:
        ss = [x for x in re.split(r"(?<=[.?!])\s+", t) if x]; sents += ss; pend.append(len(sents) - 1)
    w = [weight(x) for x in sents]; W = sum(w); n = len(sents) - 1; m = len(sil); INF = 1e18
    mid = [(s + e) / 2 for s, e in sil]
    cost = [[INF] * m for _ in range(n)]; back = [[-1] * m for _ in range(n)]
    for i in range(n):
        for j in range(i, m):
            if i == 0: prev, pj = 0.0, 0.0; best = 0; bk = -1
            else:
                best = INF; bk = -1
                for k in range(i - 1, j):
                    if cost[i - 1][k] < best: pass
                    c = cost[i - 1][k] + ((mid[j] - mid[k]) - w[i] / W * d) ** 2
                    if c < best: best = c; bk = k
                cost[i][j] = best - 1.5 * min(sil[j][1] - sil[j][0], 1.0); back[i][j] = bk; continue
            cost[i][j] = (mid[j] - w[0] / W * d) ** 2 - 1.5 * min(sil[j][1] - sil[j][0], 1.0)
    j = min(range(m), key=lambda j: cost[n - 1][j] + ((d - mid[j]) - w[n] / W * d) ** 2); ends = [0] * n
    for i in range(n - 1, -1, -1): ends[i] = mid[j]; j = back[i][j]
    for x, e in zip(sents, ends): print(f"   {e:6.1f}  {x[:60]}")
    return [0.0] + [ends[i] for i in pend[:-1]] + [d]

def main():
    files = {1: f"{ROOT}/assets/vo/v1.mp3", 2: f"{ROOT}/assets/vo/v2.mp3"}; groups = {1: [], 2: []}; cur = None
    for it in SEQ:
        if isinstance(it, tuple): cur = it[1]
        elif "text" in it: it["vof"] = cur; groups[cur].append(it)
    for k, g in groups.items():
        cuts = beat_cuts(files[k], [b["text"] for b in g])
        for b, a, e in zip(g, cuts, cuts[1:]): b["ss"] = a; b["vd"] = e - a
    scenes = []; vo = []; music = [{"track": "drone", "start": 0}]; t = 0.0; n = 0
    def add(d, sid, **k):
        nonlocal t
        scenes.append({"id": sid, "start": t, "dur": d, "label": "", **k}); t += d
    for it in SEQ:
        if isinstance(it, tuple): continue
        if it.get("sting"):
            add(4.6, "sting", gfx={"type": "sting", "title": "MANAGER, NOT COACH", "sub": "HOW BRAZIL BECAME A TEAM THAT LOSES TO JAPAN"}); continue
        if it.get("clip"):
            add(it["d"], f"c{n:02d}", gfx=it["gfx"], takes=[{"src": it["src"], "ss": it["ss"], "slow": 1.0, "frames": round(it["d"] * FPS), "crop": "", "pillar": it["pillar"]}], nat={"src": it["src"], "ss": it["ss"]}); n += 1; continue
        if it.get("music"): music.append({"track": it["music"], "start": t})
        d = it["vd"] + 0.15
        vo.append({"file": os.path.basename(files[it["vof"]]), "start": t + 0.12, "ss": it["ss"], "dur": it["vd"]})
        add(d, f"n{n:02d}", gfx=it["gfx"], pools=it["pools"], cut=it["cut"], text=it["text"], vo0=t + 0.12, label="BRAZIL · THE FALL"); n += 1
    music.append({"track": "finale", "start": t})
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
               "brand": "BRAZIL · <b>THE FALL</b>", "tagline": "ZLATAN · ANCELOTTI · BRAZIL", "stingbg": "28", "endtitle": "BRAZIL · <span style=\"color:var(--amber)\">THE FALL</span>", "sources": "FOX Sports · ESPN FC · FIFA · AFP"},
              open(f"{ROOT}/build/timeline.json", "w"), indent=1, ensure_ascii=False)
    tk = [x for s in scenes for x in s.get("takes", [])]
    print(f"{len(scenes)} scenes, {total/60:.2f} min, {len(tk)} takes, avg {sum(x['frames'] for x in tk)/25/len(tk):.2f}s")
    for s in scenes: print(f'{s["id"]} {s["start"]:7.2f} {s["dur"]:6.2f} {s["gfx"]["type"]:8s} {len(s.get("takes",[]))} {s.get("text","")[:50]}')
if __name__ == "__main__": main()
