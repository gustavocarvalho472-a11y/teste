"""Baixa fotos e logos de licença livre do Wikimedia Commons → assets/<pasta>/<ID>_commons_….jpg|png

    python3 baixar_commons.py           # só os que ainda não existem
Autor e licença de cada arquivo vão para assets/CREDITOS_COMMONS.md (cite na descrição do vídeo).
"""
import json
import time
import os
import re
import urllib.parse
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://commons.wikimedia.org/w/api.php?"
UA = {"User-Agent": "mbappe-china-video/1.0 (https://github.com/gustavocarvalho472-a11y/teste)"}

# id → (pasta, busca no Commons)
WANT = {
    "FOT_01": ("fotos", "Tiananmen gate Mao Zedong portrait"),
    "FOT_02": ("fotos", "100 yuan banknote 2015 front"),
    "FOT_03": ("fotos", "Kylian Mbappé press conference"),
    "FOT_04": ("fotos", "people holding Mao Zedong portrait"),
    "FOT_05": ("fotos", "Mao Zedong proclaiming People's Republic of China 1949"),
    "FOT_08": ("fotos", "Kylian Mbappe Real Madrid game 2025"),
    "FOT_09": ("fotos", "Javier Tebas"),
    "LOG_01": ("logos", "Eastroc Beverage logo"),
    "LOG_02": ("logos", "Mengniu logo"),
    "LOG_03": ("logos", "Milkground logo"),
    "LOG_04": ("logos", "LaLiga logo 2023"),
}


def get(params):
    with urllib.request.urlopen(urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA)) as r:
        return json.load(r)


def search(q):
    res = get({"action": "query", "format": "json", "list": "search", "srnamespace": 6, "srlimit": 8, "srsearch": q})
    return [x["title"] for x in res["query"]["search"]
            if re.search(r"\.(jpe?g|png|svg)$", x["title"], re.I)]


def info(title):
    res = get({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
               "iiprop": "url|extmetadata|size", "iiurlwidth": 1920})
    page = next(iter(res["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    md = ii.get("extmetadata", {})
    clean = lambda k: re.sub("<[^>]+>", "", md.get(k, {}).get("value", "")).strip()
    return ii.get("thumburl") or ii["url"], clean("Artist"), clean("LicenseShortName"), ii["descriptionurl"]


def main():
    cred = []
    for aid, (folder, q) in WANT.items():
        d = os.path.join(HERE, "assets", folder)
        os.makedirs(d, exist_ok=True)
        if any(f.startswith(aid + "_") for f in os.listdir(d)):
            continue
        titles = search(q)
        if not titles:
            print(f"NADA  {aid}  ({q})")
            continue
        url, artist, lic, page = info(titles[0])
        ext = ".png" if url.lower().endswith((".png", ".svg.png")) else ".jpg"
        slug = re.sub(r"[^a-z0-9]+", "_", titles[0][5:].lower())[:40].strip("_")
        out = os.path.join(d, f"{aid}_commons_{slug}{ext}")
        for tent in range(5):                          # o Commons limita a taxa (429): espera e tenta de novo
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
                    data = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or tent == 4:
                    raise
                time.sleep(5 * 2 ** tent)
        open(out, "wb").write(data)
        time.sleep(2)
        print(f"OK    {aid}  {titles[0]}  [{lic}]")
        cred.append(f"| {aid} | {titles[0][5:]} | {artist or '?'} | {lic or '?'} | {page} |")
    if cred:
        p = os.path.join(HERE, "assets", "CREDITOS_COMMONS.md")
        new = not os.path.exists(p)
        with open(p, "a") as f:
            if new:
                f.write("| id | arquivo | autor | licença | página |\n|---|---|---|---|---|\n")
            f.write("\n".join(cred) + "\n")


if __name__ == "__main__":
    main()
