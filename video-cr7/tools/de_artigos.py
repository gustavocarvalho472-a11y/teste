"""Baixa og:image e imagens grandes de páginas de reportagens. Uso: de_artigos.py cenas.json saida/"""
import json, sys, os, re, html, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def curl(url, out=None):
    cmd = ["curl", "-sSL", "--max-time", "25", "-A", UA, "-H", "Accept-Language: en", url]
    if out: cmd[1:1] = ["-o", out]
    r = subprocess.run(cmd, capture_output=True); return r.stdout if not out else r.returncode == 0
def imgs(page_url):
    h = curl(page_url).decode("utf8", "ignore")
    found = []
    for pat in [r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"',
                r'<meta[^>]+name="twitter:image"[^>]+content="([^"]+)"', r'<img[^>]+(?:data-src|src)="([^"]+\.(?:jpe?g|webp|png)[^"]*)"']:
        for u in re.findall(pat, h, re.I):
            u = urllib.parse.urljoin(page_url, html.unescape(u))
            if u not in found and not re.search(r'logo|icon|avatar|sprite|placeholder|1x1', u, re.I): found.append(u)
    return found[:12]
def get(job):
    url, fn = job
    if not curl(url, fn): return None
    try:
        im = Image.open(fn).convert("RGB")
        if im.width < 600: os.remove(fn); return None
        jp = os.path.splitext(fn)[0] + ".jpg"; im.save(jp, quality=92)
        if jp != fn: os.remove(fn)
        return (os.path.basename(jp), im.width, im.height, url)
    except Exception:
        os.path.exists(fn) and os.remove(fn); return None
cenas = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
mp = os.path.join(out, "_fontes.json"); meta = json.load(open(mp)) if os.path.exists(mp) else {}
for sid, pages in cenas.items():
    jobs, seen = [], set()
    for p in pages:
        for u in imgs(p):
            if u in seen: continue
            seen.add(u); jobs.append((u, os.path.join(out, f"{sid}_{len(jobs):02d}.tmp")))
    with ThreadPoolExecutor(8) as ex: got = [g for g in ex.map(get, jobs) if g]
    meta[sid] = [{"file": f, "w": w, "h": h, "src": s} for f, w, h, s in got]
    print(sid, len(got), flush=True)
json.dump(meta, open(mp, "w"), indent=1)
