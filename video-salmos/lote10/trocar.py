"""Troca clipes ruins numa lista de cenas sem refazer a escolha inteira.
Uso: trocar.py cenas_rXX.json id1 id2 ...  -> bloqueia os ids, escolhe substitutos novos e baixa."""
import glob, importlib.util, json, os, sys
from PIL import Image, ImageStat
spec = importlib.util.spec_from_file_location("px", "02_pexels.py"); px = importlib.util.module_from_spec(spec)
sys.argv, args = ["x"], sys.argv[1:]
spec.loader.exec_module(px)
arq, ruins = args[0], {int(x) for x in args[1:]}
b = set(json.load(open("clips/bloqueados.json"))) | ruins; json.dump(sorted(b), open("clips/bloqueados.json", "w"))
usados = set(json.load(open("clips/usados.json")))
em_uso = {c["clip"]["id"] for f in glob.glob("lote10/cenas_r*.json") + ["cenas.json"] for c in json.load(open(f))}
pools = json.load(open("clips/pools.json"))
cenas = json.load(open(arq)); novos = []
SUB = [t for t in os.environ.get("TAGS_SUB", "").split(",") if t]  # ex.: TAGS_SUB=trigo,rio
def colorido(k):
    th = f"clips/thumbs/{k['id']}.jpg"
    if not os.path.exists(th): return True
    s_ = ImageStat.Stat(Image.open(th).convert("HSV")).mean[1]
    return s_ > 25  # descarta preto e branco / quase sem cor
for c in cenas:
    if c["clip"]["id"] not in ruins: continue
    esc = None
    for tag in (SUB or [c["tag"]] + px.RELACIONADAS[c["tag"]]):
        livres = [k for k in pools.get(tag, []) if k["id"] not in b | usados | em_uso and colorido(k)]
        if livres: esc = livres[0]; break
    if esc is None: print("sem substituto para", c["clip"]["id"], c["tag"]); continue
    em_uso.add(esc["id"]); novos.append(esc["id"])
    c["clip"] = {k: esc[k] for k in ("id", "tag", "duracao", "autor", "autor_url", "url", "arquivo", "w", "h")}
    c["clip"]["arquivo_local"] = f"clips/{esc['id']}.mp4"
    px.baixar(esc["arquivo"], c["clip"]["arquivo_local"])
json.dump(cenas, open(arq, "w"), indent=1)
print("novos:", " ".join(map(str, novos)))
