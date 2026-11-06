"""Busca imagens no Bing por cena, baixa e gera folha de contato para conferência.
Uso: python3 coletar.py queries.json saida/ [n_por_query]"""
import json, sys, os, re, html, urllib.parse, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def curl(url, out=None, timeout=25):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-A", UA]
    if out: cmd += ["-o", out]
    r = subprocess.run(cmd + [url], capture_output=True)
    return r.stdout if not out else r.returncode == 0

def search(q, n):
    page = curl("https://www.bing.com/images/search?q=" + urllib.parse.quote(q) + "&qft=+filterui:imagesize-large&form=IRFLTR").decode("utf8", "ignore")
    res = []
    for m in re.finditer(r'class="iusc"[^>]*m="([^"]+)"', page):
        d = json.loads(html.unescape(m.group(1)))
        res.append({"img": d.get("murl"), "page": d.get("purl"), "title": d.get("t", "")})
        if len(res) >= n: break
    return res

def fetch(job):
    sid, i, r, outdir = job
    ext = ".img"
    fn = os.path.join(outdir, f"{sid}_{i:02d}{ext}")
    if not curl(r["img"], fn): return None
    try:
        im = Image.open(fn); im = im.convert("RGB")
        if im.width < 500: os.remove(fn); return None
        jp = fn.replace(ext, ".jpg"); im.save(jp, quality=92); os.remove(fn)
        r.update(file=os.path.basename(jp), w=im.width, h=im.height); return r
    except Exception:
        if os.path.exists(fn): os.remove(fn)
        return None

def contact(outdir, sid, items):
    W, cols = 360, 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, rows * 230), "black")
    d = ImageDraw.Draw(sheet)
    for k, r in enumerate(items):
        im = Image.open(os.path.join(outdir, r["file"])); im.thumbnail((W - 6, 200))
        x, y = (k % cols) * W, (k // cols) * 230
        sheet.paste(im, (x + 3, y + 3)); d.text((x + 5, y + 205), f'{r["file"]} {r["w"]}x{r["h"]}', fill="yellow")
    sheet.save(os.path.join(outdir, f"_sheet_{sid}.jpg"), quality=80)

if __name__ == "__main__":
    qs = json.load(open(sys.argv[1])); outdir = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    os.makedirs(outdir, exist_ok=True)
    meta = {}
    for sid, q in qs.items():
        res = search(q, n)
        with ThreadPoolExecutor(8) as ex:
            got = [r for r in ex.map(fetch, [(sid, i, r, outdir) for i, r in enumerate(res)]) if r]
        meta[sid] = {"query": q, "results": got}
        if got: contact(outdir, sid, got)
        print(sid, len(got), flush=True)
    mp = os.path.join(outdir, "_meta.json")
    old = json.load(open(mp)) if os.path.exists(mp) else {}
    old.update(meta); json.dump(old, open(mp, "w"), ensure_ascii=False, indent=1)
