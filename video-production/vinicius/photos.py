#!/usr/bin/env python3
"""Free photos from Wikimedia Commons via the HTML search (the API is rate-limited for bots).
Usage: python3 photos.py  -> assets/photos/cand/<key>_NN.jpg + meta.json (title, author, license, page) for the credits."""
import html, json, os, re, subprocess, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f"{ROOT}/assets/photos/cand"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
Q = {"vini": "Vinícius Júnior", "vinirm": "Vinícius Júnior Real Madrid", "vini18": "Vinicius Junior 2018", "xabi": "Xabi Alonso",
     "xabicoach": "Xabi Alonso Leverkusen", "arteta": "Mikel Arteta", "artetacoach": "Mikel Arteta manager", "mourinho": "José Mourinho",
     "mou25": "José Mourinho 2025", "diomande": "Yan Diomande", "bernabeu": "Santiago Bernabéu stadium", "campnou": "Spotify Camp Nou",
     "emirates": "Emirates Stadium", "anfield": "Anfield", "ancelotti": "Carlo Ancelotti Real Madrid", "mbappe": "Kylian Mbappé Real Madrid",
     "arbeloa": "Álvaro Arbeloa", "montilivi": "Estadi Montilivi", "arsfans": "Arsenal supporters", "rmfans": "Real Madrid supporters",
     "saliba": "Nathan Saliba", "martinelli": "Gabriel Martinelli", "havertz": "Kai Havertz Arsenal", "leipzig": "RB Leipzig Red Bull Arena"}
import sys
META_ONLY = "--meta" in sys.argv
meta = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else {}
def get(url):
    for k in range(8):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e: print("retry", k, str(e)[:40], url[-70:], flush=True); time.sleep(120)
    return None
def text(h): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))).strip()
for key, q in Q.items():
    if key in meta: continue
    s = get("https://commons.wikimedia.org/w/index.php?" + urllib.parse.urlencode({"search": q, "ns6": 1, "fulltext": 1, "limit": 20})).decode("utf-8", "ignore")
    names = []
    for m in re.finditer(r'href="/wiki/(File:[^"]+?\.(?:jpe?g|png))"', s, re.I):
        n = urllib.parse.unquote(m.group(1))
        if n not in names: names.append(n)
    items = []
    for n in names[:9]:
        p = get("https://commons.wikimedia.org/wiki/" + urllib.parse.quote(n))
        if not p: continue
        p = p.decode("utf-8", "ignore")
        u = re.search(r'href="(https://upload\.wikimedia\.org/wikipedia/commons/[0-9a-f]/[0-9a-f]{2}/[^"]+)"', p)
        wh = re.search(r"\(([\d,\.]+) × ([\d,\.]+) pixels", p)
        if not u or not wh: continue
        w = int(re.sub(r"\D", "", wh.group(1))); h = int(re.sub(r"\D", "", wh.group(2)))
        if w < 900: continue
        lic = re.search(r'class="licensetpl(?:_|&#95;)short[^"]*"[^>]*>(.*?)</span>', p, re.S)
        aut = re.search(r'id="fileinfotpl(?:_|&#95;)aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', p, re.S)
        dat = re.search(r'id="fileinfotpl(?:_|&#95;)date"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', p, re.S)
        it = {"title": n, "url": u.group(1), "w": w, "h": h, "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(n),
              "license": text(lic.group(1)) if lic else "?", "artist": text(aut.group(1))[:120] if aut else "?", "date": text(dat.group(1))[:40] if dat else ""}
        fn = f"{OUT}/{key}_{len(items):02d}.jpg"
        it["url"] = html.unescape(it["url"]).split("?")[0]; nm = it["url"].rsplit("/", 1)[1]
        src = it["url"].replace("/commons/", "/commons/thumb/", 1) + f"/960px-{nm}" + (".jpg" if nm.lower().endswith(".png") else "") if w > 960 else it["url"]
        it["thumb"] = src
        if META_ONLY:
            items.append(it)
            if len(items) >= 6: break
            continue
        data = get(src)
        if not data: continue
        open(fn + ".orig", "wb").write(data)
        subprocess.run(f"ffmpeg -v error -y -i '{fn}.orig' -vf \"scale='min(2400,iw)':-2\" -q:v 3 '{fn}'", shell=True); os.remove(fn + ".orig")
        it["file"] = os.path.basename(fn); items.append(it); time.sleep(25)
        if len(items) >= 6: break
    meta[key] = items; json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1, ensure_ascii=False)
    print(key, len(items), flush=True); time.sleep(3)
print("DONE")
