#!/usr/bin/env python3
"""Search Wikimedia Commons (rate-limited) and download candidate free photos. Usage: python3 photos.py"""
import json, os, time, urllib.error, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f"{ROOT}/assets/photos/cand"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "FootballDocBot/1.0 (educational video research)"}
Q = {"ferguson": "Alex Ferguson Manchester United", "poch": "Mauricio Pochettino", "pochspurs": "Pochettino Tottenham", "statue": "Alex Ferguson statue Old Trafford",
     "oldtrafford": "Old Trafford stadium", "vangaal": "Louis van Gaal Manchester United", "ole": "Ole Gunnar Solskjær Manchester United", "carrick": "Michael Carrick",
     "klopp": "Jürgen Klopp Liverpool", "slot": "Arne Slot Liverpool", "anfield": "Anfield stadium", "moyes": "David Moyes Manchester United",
     "tenhag": "Erik ten Hag Manchester United", "amorim": "Rúben Amorim", "mourinho": "José Mourinho Manchester United", "kane": "Harry Kane Tottenham",
     "rangnick": "Ralf Rangnick", "pochusa": "Pochettino United States", "espanyol": "Pochettino Espanyol", "ferguson80": "Alex Ferguson 1980s"}
meta = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else {}
def get(url, tries=40):
    for k in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500: print("http", e.code, url[-80:], flush=True); return None
            print("retry", k, e, flush=True); time.sleep(45)
        except Exception as e:
            print("retry", k, e, flush=True); time.sleep(45)
    return None
def fetch_img(orig, w):
    orig = orig.split("?")[0]
    name = orig.rsplit("/", 1)[1]; th = orig.replace("/commons/", "/commons/thumb/", 1)
    for size in (1280, 960):
        if w > size:
            data = get(f"{th}/{size}px-{name}", tries=6)
            if data: return data
    return get(orig, tries=6)
for key, q in Q.items():
    if key in meta: continue
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 14, "gsrsearch": f"{q} filetype:bitmap",
         "prop": "imageinfo", "iiprop": "url|size|extmetadata"}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
    items = []
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99)):
        ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
        if ii["width"] < 900 or ii.get("size", 0) > 25e6: continue
        items.append({"title": pg["title"], "url": ii["url"].split("?")[0], "w": ii["width"], "h": ii["height"], "page": ii.get("descriptionurl"),
                      "artist": em.get("Artist", {}).get("value", ""), "license": em.get("LicenseShortName", {}).get("value", ""), "date": em.get("DateTimeOriginal", {}).get("value", "")})
    for i, it in enumerate(items[:10]):
        fn = f"{OUT}/{key}_{i:02d}.jpg"
        if not os.path.exists(fn):
            data = fetch_img(it["url"], it["w"])
            if not data: print("skip", it["title"], flush=True); continue
            open(fn + ".orig", "wb").write(data); os.system(f"ffmpeg -v error -y -i '{fn}.orig' -vf \"scale='min(2400,iw)':-2\" -q:v 3 '{fn}' && rm '{fn}.orig'"); time.sleep(6)
        it["file"] = os.path.basename(fn)
    meta[key] = items[:10]; json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1, ensure_ascii=False)
    print(key, len(items), flush=True); time.sleep(40)
print("DONE")
