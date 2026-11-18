#!/usr/bin/env python3
"""Search Wikimedia Commons (rate-limited) and download candidate free photos. Usage: python3 photos.py"""
import json, os, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f"{ROOT}/assets/photos/cand"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "FootballDocBot/1.0 (educational video research)"}
Q = {"ferguson": "Alex Ferguson Manchester United", "ferguson80": "Alex Ferguson 1980s", "poch": "Mauricio Pochettino", "pochspurs": "Pochettino Tottenham",
     "pochusa": "Pochettino United States", "moyes": "David Moyes Manchester United", "vangaal": "Louis van Gaal Manchester United", "mourinho": "José Mourinho Manchester United",
     "ole": "Ole Gunnar Solskjær Manchester United", "rangnick": "Ralf Rangnick", "tenhag": "Erik ten Hag Manchester United", "amorim": "Rúben Amorim",
     "carrick": "Michael Carrick", "klopp": "Jürgen Klopp Liverpool", "slot": "Arne Slot Liverpool", "oldtrafford": "Old Trafford stadium", "anfield": "Anfield stadium",
     "statue": "Alex Ferguson statue Old Trafford", "kane": "Harry Kane Tottenham", "espanyol": "Pochettino Espanyol"}
meta = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else {}
def get(url):
    for k in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print("retry", k, e, flush=True); time.sleep(30 * (k + 1))
for key, q in Q.items():
    if key in meta: continue
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 14, "gsrsearch": f"{q} filetype:bitmap",
         "prop": "imageinfo", "iiprop": "url|size|extmetadata"}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
    items = []
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99)):
        ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
        if ii["width"] < 900 or ii.get("size", 0) > 25e6: continue
        items.append({"title": pg["title"], "url": ii["url"], "w": ii["width"], "h": ii["height"], "page": ii.get("descriptionurl"),
                      "artist": em.get("Artist", {}).get("value", ""), "license": em.get("LicenseShortName", {}).get("value", ""), "date": em.get("DateTimeOriginal", {}).get("value", "")})
    for i, it in enumerate(items[:10]):
        fn = f"{OUT}/{key}_{i:02d}.jpg"
        if not os.path.exists(fn):
            open(fn + ".orig", "wb").write(get(it["url"])); os.system(f"ffmpeg -v error -y -i '{fn}.orig' -vf \"scale='min(2400,iw)':-2\" -q:v 3 '{fn}' && rm '{fn}.orig'"); time.sleep(3)
        it["file"] = os.path.basename(fn)
    meta[key] = items[:10]; json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1, ensure_ascii=False)
    print(key, len(items), flush=True); time.sleep(40)
print("DONE")
