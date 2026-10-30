"""Baixa os assets a partir dos links enviados (assets/links.txt, uma linha "ID url" por asset).

  - post do X + id MEME_/FOT_   → baixa as fotos do post (tamanho original); vídeo vira CLP se o id for CLP_
  - post do X + id PRT_         → print do embed oficial do X (platform.twitter.com), recortado no card
  - URL direta de imagem        → baixa (SVG vira PNG)

    python3 baixar_links.py                # só ids que ainda não têm arquivo "_x_"/"_link_"
    python3 baixar_links.py --force        # refaz tudo
Registra autor/link de cada asset em assets/FONTES_LINKS.md.
"""
import json
import os
import re
import sys
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDERS = {"MEME": "memes", "PRT": "prints", "FOT": "fotos", "CLP": "clips", "LOG": "logos"}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


def tweet(tid):
    data, _ = fetch(f"https://cdn.syndication.twimg.com/tweet-result?id={tid}&lang=pt&token=4c2mmul6mnh")
    return json.loads(data)


def save_image(data, base):
    """Grava como PNG (converte webp/svg/jpg) e devolve o caminho."""
    tmp = base + ".tmp"
    open(tmp, "wb").write(data)
    out = base + ".png"
    if data.lstrip()[:5] in (b"<?xml", b"<svg ") or b"<svg" in data[:400]:
        from playwright.sync_api import sync_playwright        # SVG → PNG renderizado pelo Chromium
        with sync_playwright() as p:
            br = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
            pg = br.new_page(viewport={"width": 1200, "height": 1200})
            pg.goto("file://" + os.path.abspath(tmp).replace(".tmp", ".tmp"), wait_until="load")
            pg.set_content(f'<body style="margin:0;background:transparent"><img id="i" src="file://{os.path.abspath(tmp)}"'
                           ' style="width:1000px;display:block"></body>')
            pg.wait_for_timeout(500)
            pg.locator("#i").screenshot(path=out, omit_background=True)
            br.close()
    else:
        im = Image.open(tmp)
        im.load()
        im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB").save(out)
    os.remove(tmp)
    return out


def embed_shot(tid, base, page):
    page.goto(f"https://platform.twitter.com/embed/Tweet.html?id={tid}&theme=light&lang=pt&dnt=true",
              wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(2500)
    card = page.locator("article").first
    card.wait_for(timeout=15000)
    out = base + ".png"
    card.screenshot(path=out)
    return out


def main():
    force = "--force" in sys.argv
    lines = [l.split(None, 1) for l in open(os.path.join(HERE, "assets", "links.txt")) if l.strip()]
    log, pw, page = [], None, None
    for aid, url in lines:
        url = url.strip()
        kind = aid.split("_")[0]
        d = os.path.join(HERE, "assets", FOLDERS[kind])
        os.makedirs(d, exist_ok=True)
        tag = "x" if "x.com/" in url or "twitter.com/" in url else "link"
        if not force and any(f.startswith(aid + "_" + tag) for f in os.listdir(d)):
            continue
        base = os.path.join(d, f"{aid}_{tag}")
        try:
            if tag == "x":
                tid = re.search(r"status/(\d+)", url).group(1)
                tw = tweet(tid)
                who = tw.get("user", {}).get("screen_name", "?")
                if kind == "PRT":
                    if pw is None:
                        from playwright.sync_api import sync_playwright
                        pw = sync_playwright().start()
                        br = pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
                        page = br.new_page(viewport={"width": 560, "height": 1400}, device_scale_factor=3)
                    out = embed_shot(tid, base + "_" + who, page)
                else:
                    photos = [m["media_url_https"] for m in tw.get("mediaDetails", []) if m["type"] == "photo"]
                    if not photos:                     # post só com vídeo: usa a capa do vídeo
                        photos = [m["media_url_https"] for m in tw.get("mediaDetails", []) if m["type"] == "video"]
                    if not photos:
                        raise RuntimeError("post sem foto")
                    outs = []
                    for k, ph in enumerate(photos):
                        data, _ = fetch(ph + "?name=orig")
                        outs.append(save_image(data, f"{base}_{who}" + (f"_{k + 1}" if len(photos) > 1 else "")))
                    out = ", ".join(os.path.basename(o) for o in outs)
                log.append(f"| {aid} | @{who} | {url} |")
            else:
                data, _ = fetch(url)
                out = save_image(data, base + "_" + url.split("/")[2].replace("www.", "").split(".")[0])
                log.append(f"| {aid} | {url.split('/')[2]} | {url} |")
            print(f"OK    {aid}  {os.path.basename(str(out))}")
        except Exception as e:
            print(f"FALHA {aid}  {url}  ({str(e).splitlines()[0][:90]})")
    if pw:
        pw.stop()
    if log:
        p = os.path.join(HERE, "assets", "FONTES_LINKS.md")
        new = not os.path.exists(p)
        with open(p, "a") as f:
            if new:
                f.write("| id | autor / site | link |\n|---|---|---|\n")
            f.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
