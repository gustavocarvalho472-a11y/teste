"""Busca pools de clipes no Pexels por tag, escolhe clipes por cena (sem repetir em ~10 min),
baixa com cache e grava cenas.json + out/creditos.txt.

Uso:
  python 02_pexels.py pools     # só busca/atualiza os pools (metadados + thumbnails)
  python 02_pexels.py           # pools + escolha das cenas + download
"""
import json, math, os, re, sys, time, urllib.request, urllib.parse, urllib.error

def load_env():
    for p in (".env", "../.env"):
        if os.path.exists(p):
            for line in open(p):
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1); os.environ.setdefault(k, v)
load_env()
KEY = os.environ.get("PEXELS_API_KEY")
if not KEY: sys.exit("PEXELS_API_KEY não encontrada (.env)")

QUERIES = {
 "ceu_noturno": "night sky stars", "lua": "moon clouds night", "nascer_sol": "sunrise clouds golden",
 "luz_divina": "sun rays through clouds", "vela": "candle flame dark", "biblia": "bible open candle",
 "maos_orando": "praying hands", "campo": "green meadow peaceful", "pastor_ovelhas": "sheep grazing hills",
 "rio": "calm river", "mar_calmo": "calm ocean waves sunset", "montanha": "mountains fog sunrise",
 "floresta": "forest light rays", "chuva_janela": "rain on window night", "cruz": "cross silhouette sunset",
 "aguia": "eagle flying", "fogo_lareira": "fireplace cozy",
}
# tags parecidas para quando o pool de uma tag se esgota dentro da janela de 10 min
RELACIONADAS = {
 "ceu_noturno": ["lua"], "lua": ["ceu_noturno"], "nascer_sol": ["luz_divina", "montanha"],
 "luz_divina": ["nascer_sol", "floresta"], "vela": ["fogo_lareira", "biblia"], "biblia": ["vela"],
 "maos_orando": ["vela", "biblia"], "campo": ["pastor_ovelhas", "floresta"], "pastor_ovelhas": ["campo"],
 "rio": ["mar_calmo", "floresta"], "mar_calmo": ["rio"], "montanha": ["nascer_sol", "floresta"],
 "floresta": ["luz_divina", "rio"], "chuva_janela": ["vela", "ceu_noturno"], "cruz": ["luz_divina", "nascer_sol"],
 "aguia": ["montanha", "luz_divina"], "fogo_lareira": ["vela"],
}
BANIDAS = r"\b(woman|women|man|men|girl|boy|people|person|face|portrait|city|street|traffic|text|logo|neon|crowd|couple|child|children|kid|selfie|car|cars|building|urban|party|dance|dancing|family|friends|bride|wedding|model|tourist|hike|hiker|hikers|hiking|walking|walk|runner|silhouette-of-a|traveler|climber|backpacker|fisherman|surfer|boat|kayak|drone-shot-of-a-city|timelapse-of-a-city)\b"
BANIDAS_MAOS = r"\b(face|portrait|smiling|selfie|crowd|city|street|text|logo|child|kid|couple)\b"
JANELA_SEM_REPETIR = 600  # s
CENA_MAX = float(os.environ.get("CENA_MAX", 7.5))  # s; frases longas ganham um clipe a cada ~7,5 s
POOL_MAX, DUR_MIN = 25, 8
# tags de natureza aparecem muito no roteiro: pool maior para variar mais
POOL_NATUREZA = {"ceu_noturno", "lua", "luz_divina", "nascer_sol", "montanha", "rio", "campo", "floresta", "mar_calmo"}
def alvo(tag): return 35 if tag in POOL_NATUREZA else POOL_MAX
os.makedirs("clips/thumbs", exist_ok=True); os.makedirs("out", exist_ok=True)

_last = [0.0]
def api(url):
    for tent in range(6):
        espera = 0.3 - (time.time() - _last[0])
        if espera > 0: time.sleep(espera)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "video-salmos/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                w = 30 * (tent + 1); print(f"  HTTP 429, aguardando {w}s"); time.sleep(w); continue
            raise
        except urllib.error.URLError:
            time.sleep(2 ** tent)
    raise RuntimeError(f"falhou: {url}")

def baixar(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0: return
    tmp = dest + ".part"
    for tent in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "video-salmos/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                while (b := r.read(1 << 20)): f.write(b)
            os.replace(tmp, dest); return
        except Exception as e:
            print(f"  erro baixando ({e}), tentativa {tent+1}"); time.sleep(2 ** tent)
    raise RuntimeError(f"download falhou: {url}")

def melhor_arquivo(v):
    fs = [f for f in v["video_files"] if f.get("width") and f.get("height") and f["width"] >= 1280
          and f["width"] > f["height"] and f.get("file_type") == "video/mp4"]
    if not fs: return None
    return min(fs, key=lambda f: (abs(f["width"] - 1920) + abs(f["height"] - 1080), -(f.get("fps") or 0)))

def slug(v): return v["url"].rstrip("/").split("/")[-1].lower()

def montar_pools():
    pools = json.load(open("clips/pools.json")) if os.path.exists("clips/pools.json") else {}
    bloqueados = set(json.load(open("clips/bloqueados.json"))) if os.path.exists("clips/bloqueados.json") else set()
    for tag, q in QUERIES.items():
        if tag in pools:
            pools[tag] = [c for c in pools[tag] if c["id"] not in bloqueados]
            if len(pools[tag]) >= 15: continue  # pools já revisados visualmente; só completa se ficar < 15
        print(f"[pool] {tag}: '{q}'")
        cands = list(pools.get(tag, [])); vistos = {c["id"] for c in cands}
        for page in range(1, 6):  # 2 páginas normalmente; mais se o pool ainda não chegou ao alvo
            if page > 2 and len(cands) >= alvo(tag): break
            d = api("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
                {"query": q, "orientation": "landscape", "size": "medium", "per_page": 15, "page": page}))
            for v in d.get("videos", []):
                if v["id"] in vistos or v["id"] in bloqueados: continue
                vistos.add(v["id"])
                ban = BANIDAS_MAOS if tag == "maos_orando" else BANIDAS
                if v["duration"] < DUR_MIN or re.search(ban, slug(v).replace("-", " ")): continue
                f = melhor_arquivo(v)
                if not f: continue
                cands.append({"id": v["id"], "tag": tag, "duracao": v["duration"], "autor": v["user"]["name"],
                              "autor_url": v["user"]["url"], "url": v["url"], "slug": slug(v), "thumb": v["image"],
                              "arquivo": f["link"], "w": f["width"], "h": f["height"], "fps": f.get("fps")})
        pools[tag] = cands[:alvo(tag)]
        for c in pools[tag]:
            if os.path.exists(f"clips/thumbs/{c['id']}.jpg"): continue
            baixar(c["thumb"] + ("&" if "?" in c["thumb"] else "?") + "w=320", f"clips/thumbs/{c['id']}.jpg")
        print(f"   {len(pools[tag])} clipes no pool")
    json.dump(pools, open("clips/pools.json", "w"), indent=1)
    return pools

def montar_cenas(pools):
    tl = json.load(open("timeline.json")); frases = tl["frases"]; total = tl["duracao_total"]
    # cenas: uma por frase (slot = frase + pausa), mínimo 4 s (frases curtas se juntam à seguinte),
    # frase > 12 s ganha 2 clipes
    cenas, i = [], 0
    while i < len(frases):
        f = frases[i]
        ini = f["inicio"] if i > 0 else 0.0
        j = i
        def fim_slot(j): return frases[j + 1]["inicio"] if j + 1 < len(frases) else total
        while fim_slot(j) - ini < 4.0 and j + 1 < len(frases) and frases[j + 1]["bloco"] == f["bloco"]:
            j += 1
        fim = fim_slot(j)
        partes = max(1, math.ceil((fim - ini) / CENA_MAX))
        for p in range(partes):
            a = ini + (fim - ini) * p / partes; b = ini + (fim - ini) * (p + 1) / partes
            cenas.append({"frases": list(range(i, j + 1)), "bloco": f["bloco"], "tag": f["tag_visual"],
                          "inicio": round(a, 3), "fim": round(b, 3)})
        i = j + 1
    usados_em, violacoes = {}, 0
    for c in cenas:
        escolha = None
        for tag in [c["tag"]] + RELACIONADAS[c["tag"]]:
            livres = [k for k in pools[tag] if c["inicio"] - usados_em.get(k["id"], -1e9) >= JANELA_SEM_REPETIR]
            if livres:
                escolha = min(livres, key=lambda k: usados_em.get(k["id"], -1e9)); break
        if escolha is None:  # tudo usado nos últimos 10 min: pega o usado há mais tempo
            escolha = min(pools[c["tag"]], key=lambda k: usados_em.get(k["id"], -1e9)); violacoes += 1
        usados_em[escolha["id"]] = c["fim"]
        c["clip"] = {k: escolha[k] for k in ("id", "tag", "duracao", "autor", "autor_url", "url", "arquivo", "w", "h")}
        c["clip"]["arquivo_local"] = f"clips/{escolha['id']}.mp4"
    json.dump(cenas, open("cenas.json", "w"), indent=1)
    print(f"{len(cenas)} cenas, {len(usados_em)} clipes distintos, {violacoes} repetições dentro de 10 min")
    return cenas

if __name__ == "__main__":
    pools = montar_pools()
    if sys.argv[1:] == ["pools"]: sys.exit()
    cenas = montar_cenas(pools)
    alvo = sys.argv[2] if len(sys.argv) > 2 else None
    ids = {}
    for c in cenas: ids.setdefault(c["clip"]["id"], c["clip"])
    print(f"baixando {len(ids)} clipes (cache em clips/)")
    for n, (cid, c) in enumerate(ids.items(), 1):
        baixar(c["arquivo"], c["arquivo_local"])
        if n % 20 == 0: print(f"  {n}/{len(ids)}", flush=True)
    with open("out/creditos.txt", "w", encoding="utf-8") as f:
        f.write("Vídeos de stock: Pexels (pexels.com)\n\n")
        for c in sorted(ids.values(), key=lambda c: c["autor"].lower()):
            f.write(f"{c['autor']} | {c['url']}\n")
    print("ok: cenas.json, out/creditos.txt")
