"""Busca stills na wiki de The Boys (fandom). Uso: fandom.py consultas.json saida/"""
import json, sys, os, subprocess, urllib.parse
from PIL import Image
API = "https://the-boys.fandom.com/api.php?action=query&generator=search&gsrnamespace=6&gsrlimit=15&prop=imageinfo&iiprop=url|size&format=json&gsrsearch="
def curl(u, out=None):
    c = ["curl", "-sSL", "--max-time", "40", "-A", "Mozilla/5.0"] + (["-o", out] if out else []) + [u]
    return subprocess.run(c, capture_output=True).stdout
qs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
mp = os.path.join(out, "_fontes.json"); meta = json.load(open(mp)) if os.path.exists(mp) else {}
for sid, q in qs.items():
    d = json.loads(curl(API + urllib.parse.quote(q)) or b"{}")
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    got = []
    for p in pages:
        ii = p["imageinfo"][0]
        if ii["width"] < 1000: continue
        fn = os.path.join(out, f"{sid}_{len(got):02d}.jpg")
        curl(ii["url"], fn + ".tmp")
        try:
            im = Image.open(fn + ".tmp").convert("RGB"); im.thumbnail((2560, 2560)); im.save(fn, quality=92)
            got.append({"file": os.path.basename(fn), "title": p["title"], "src": ii["url"]})
        except Exception: pass
        os.remove(fn + ".tmp")
        if len(got) >= 8: break
    meta[sid] = got; print(sid, len(got), flush=True)
json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
