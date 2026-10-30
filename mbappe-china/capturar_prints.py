"""Captura prints de manchetes (páginas públicas de notícia) → assets/prints/PRT_xx_manchete_<site>.png

    python3 capturar_prints.py            # todos os que ainda não existem
    python3 capturar_prints.py PRT_09     # só um (sobrescreve)

Os tweets do handoff (X exige login) não são capturados aqui. Estes prints de manchete servem de versão
provisória e mostram o mesmo fato. Para a versão final, salve o print do tweet com o mesmo id e apague o
arquivo *_manchete_*.
"""
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "prints")
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"   # Chromium pré-instalado do container

PRINTS = {
    "PRT_01": "https://www.deccanchronicle.com/sports/football/chinese-state-tv-suspends-la-liga-broadcasts-after-mbappe-remark-1999353",
    "PRT_02": "https://www.iprofesional.com/negocios/467580-mbappe-pierde-contratos-en-china-tras-la-polemica-por-mao-zedong",
    "PRT_03": "https://stevivor.com/news/fc-online-china-removes-mbappe-promo-material-and-plans-a-game-update/",
    "PRT_04": "https://www.diaridetarragona.com/internacional/274096/television-estatal-china-suspende-emisiones-laliga-polemica-mbappe.html",
    "PRT_05": "https://beninwebtv.bj/en/mbappe-controversy-in-china-tebas-meets-chinese-ambassador-in-spain/",
    "PRT_06": "https://www.aljazeera.com/sports/2026/10/27/kylian-mbappe-apologises-after-dictator-comment-angers-chinese-fans",
    "PRT_07": "https://aljazeera.com/sports/2026/10/28/china-says-it-takes-mbappes-apology-seriously-after-mao-dictator-comment",
    "PRT_08": "https://time.com/article/2026/10/28/kylian-mbappe-china-mao-zedong-dictator-meme-backlash-controversy-explainer/",
    "PRT_09": "https://www.qatar-tribune.com/article/261343/sports/mbappe-loses-brand-deals-in-china-over-mao-meme-remarks",
    "PRT_10": "https://www.swissinfo.ch/eng/mbapp%c3%a9-apologizes-for-perceived-mao-insult-after-china-backlash/92283541",
    "PRT_11": "https://revistamercado.do/empresas/sport-business/real-madrid-china-mbappe-perdidas-tv-marcas/",
    "PRT_12": "https://www.italpress.com/?p=768057",
    "PRT_13": "https://africasoccer.com/?p=645964",
    "PRT_14": "https://africa.espn.com/football/arsenal/story/4013387/ozil-row-sees-arsenal-manchester-city-pulled-from-china-state-tv",
    "PRT_15": "https://witf.org/2019/10/08/chinese-state-tv-suspends-2-nba-preseason-game-broadcasts",
}

ACCEPT = ["Accept all", "Accept All", "I Accept", "I agree", "Agree", "Accept", "Aceptar", "Accepter", "Got it",
          "AGREE", "ACCEPT", "Allow all", "Consent"]


def site(url):
    return url.split("/")[2].replace("www.", "").split(".")[0]


def capture(page, pid, url):
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3500)
    for txt in ACCEPT:                                # banners de cookies
        try:
            b = page.get_by_role("button", name=txt, exact=True)
            if b.count():
                b.first.click(timeout=1500)
                page.wait_for_timeout(600)
                break
        except Exception:
            pass
    page.evaluate("""() => {                          // tira barras fixas e popups que cobrem a manchete
        for (const el of document.querySelectorAll('*')) {
            const s = getComputedStyle(el);
            if ((s.position === 'fixed' || s.position === 'sticky') && el.tagName !== 'HTML' && el.tagName !== 'BODY')
                el.style.setProperty('display', 'none', 'important');
        }
    }""")
    # a manchete é o h1 visível com o texto mais longo (alguns sites usam h1 no logo)
    best, h1 = 0, None
    for k in range(page.locator("h1").count()):
        el = page.locator("h1").nth(k)
        try:
            n = len(el.inner_text(timeout=1000).strip()) if el.is_visible() else 0
        except Exception:
            n = 0
        if n > best:
            best, h1 = n, el
    if h1 is None or best < 25:
        raise RuntimeError("manchete (h1) não encontrada")
    title = h1.inner_text().strip()
    if any(w in title.lower() for w in ("access denied", "error", "just a moment", "attention required")):
        raise RuntimeError("página bloqueada: " + title[:40])
    h1.scroll_into_view_if_needed(timeout=5000)
    page.wait_for_timeout(800)
    bb = h1.bounding_box()
    if not bb or bb["height"] < 10:
        raise RuntimeError("manchete (h1) não encontrada")
    vw = page.viewport_size["width"]
    x0 = max(0, bb["x"] - 60)
    w = min(vw - x0, max(bb["width"] + 120, 1000))
    y0 = max(0, bb["y"] - 140)
    clip = {"x": x0, "y": y0, "width": w, "height": min(bb["height"] + 520, 820)}
    path = os.path.join(OUT, f"{pid}_manchete_{site(url)}.png")
    page.screenshot(path=path, clip=clip)
    return path, title


def main():
    os.makedirs(OUT, exist_ok=True)
    only = [a for a in sys.argv[1:] if a.startswith("PRT_")]
    todo = {k: v for k, v in PRINTS.items() if (k in only) or (not only and not any(
        f.startswith(k + "_") for f in os.listdir(OUT)))}
    log = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        ctx = br.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2, locale="en-US",
                             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
        for pid, url in todo.items():
            page = ctx.new_page()
            try:
                path, title = capture(page, pid, url)
                print(f"OK    {pid}  {title[:90]}")
                log.append(f"| {pid} | {title} | {url} |")
            except Exception as e:
                print(f"FALHA {pid}  {url}  ({str(e).splitlines()[0][:80]})")
            page.close()
        br.close()
    if log:
        with open(os.path.join(OUT, "FONTES.md"), "a") as f:
            f.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
