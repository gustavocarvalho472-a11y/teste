#!/usr/bin/env python3
"""Busca e baixa vídeos livres para as cenas STOCK_VIDEO.

  find_clips.py search scenes.json  > candidates.json   # top 3 por cena
  find_clips.py download selection.json assets/         # baixa e grava credits.csv

scenes.json: {"scenes":[{"id":1,"stock_query":"stock exchange trading floor","duration":6}, ...]}
selection.json: [{"scene":1,"url":"...","source":"pexels","author":"...","license":"...","page":"..."}]
Fontes com chave (grátis): PEXELS_API_KEY, PIXABAY_API_KEY. Sem chave: Wikimedia Commons, Internet Archive."""
import csv, json, os, sys, requests

UA = {"User-Agent": "faceless-studio/1.0 (claude-code skill)"}

def pexels(q, dur):
    k = os.environ.get("PEXELS_API_KEY")
    if not k: return []
    r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": k},
                     params={"query": q, "per_page": 15, "orientation": "landscape", "size": "medium"}, timeout=30).json()
    out = []
    for v in r.get("videos", []):
        files = [f for f in v["video_files"] if f.get("width", 0) >= 1920 and f["file_type"] == "video/mp4"] or \
                [f for f in v["video_files"] if f.get("width", 0) >= 1280]
        if not files or v["duration"] < dur: continue
        out.append({"source": "pexels", "url": files[0]["link"], "preview": v["image"], "duration": v["duration"],
                    "author": v["user"]["name"], "license": "Pexels License (livre, sem atribuição obrigatória)", "page": v["url"]})
    return out

def pixabay(q, dur):
    k = os.environ.get("PIXABAY_API_KEY")
    if not k: return []
    r = requests.get("https://pixabay.com/api/videos/", params={"key": k, "q": q, "per_page": 15}, timeout=30).json()
    out = []
    for v in r.get("hits", []):
        f = v["videos"].get("large") or v["videos"].get("medium")
        if not f or v["duration"] < dur: continue
        out.append({"source": "pixabay", "url": f["url"], "preview": v.get("videos", {}).get("tiny", {}).get("thumbnail"),
                    "duration": v["duration"], "author": v["user"], "license": "Pixabay Content License", "page": v["pageURL"]})
    return out

def wikimedia(q, dur):
    r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=30, params={
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 10,
        "gsrsearch": f"filetype:video {q}", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata"})
    r.raise_for_status(); r = r.json()
    out = []
    for p in r.get("query", {}).get("pages", {}).values():
        i = p["imageinfo"][0]; m = i.get("extmetadata", {})
        out.append({"source": "wikimedia", "url": i["url"], "duration": None, "mime": i["mime"],
                    "author": m.get("Artist", {}).get("value", "?"), "license": m.get("LicenseShortName", {}).get("value", "?"),
                    "page": i["descriptionurl"], "title": p["title"]})
    return out

def archive(q, dur):
    r = requests.get("https://archive.org/advancedsearch.php", headers=UA, timeout=30, params={
        "q": f"({q}) AND mediatype:movies AND (collection:prelinger OR collection:opensource_movies OR licenseurl:*publicdomain*)", "fl[]": ["identifier", "title", "licenseurl"], "rows": 8, "output": "json"}).json()
    return [{"source": "archive.org", "url": f"https://archive.org/details/{d['identifier']}", "duration": None,
             "author": "?", "license": d.get("licenseurl") or "VERIFICAR (Prelinger/opensource_movies: em geral domínio público)",
             "page": f"https://archive.org/details/{d['identifier']}", "title": d.get("title")}
            for d in r.get("response", {}).get("docs", [])]

def search(path):
    res = {}
    for s in json.load(open(path))["scenes"]:
        q = s.get("stock_query")
        if not q: continue
        c = []
        for fn in (pexels, pixabay, wikimedia, archive):
            try: c += fn(q, s.get("duration", 5))
            except Exception as e: sys.stderr.write(f"[{fn.__name__}] {e}\n")
        res[s["id"]] = {"query": q, "candidates": c[:12]}
    json.dump(res, sys.stdout, indent=1, ensure_ascii=False)

def download(sel, dest):
    os.makedirs(dest, exist_ok=True)
    cred = os.path.join(dest, "credits.csv"); new = not os.path.exists(cred)
    with open(cred, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["scene", "source", "author", "license", "page"])
        for s in json.load(open(sel)):
            if s["source"] == "archive.org":
                sys.stderr.write(f"cena {s['scene']}: archive.org — abra {s['page']} e escolha o arquivo .mp4 (use `curl -L`).\n"); continue
            ext = os.path.splitext(s["url"].split("?")[0])[1] or ".mp4"
            fn = os.path.join(dest, f"s{int(s['scene']):02}{ext}")
            with requests.get(s["url"], headers=UA, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(fn, "wb") as o:
                    for ch in r.iter_content(1 << 20): o.write(ch)
            w.writerow([s["scene"], s["source"], s.get("author"), s.get("license"), s.get("page")]); print("ok:", fn)

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search": search(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "download": download(sys.argv[2], sys.argv[3])
    else: sys.exit(__doc__)
