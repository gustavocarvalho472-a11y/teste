"""Corrige o fim das palavras nas timelines do lote (nov/2026).

O Suno cola a pontuação no começo do token seguinte (".\n\nRep"); o 01c_externo antigo contava esse
pedaço no tempo da palavra anterior, então o fim de cada frase esticava até o início da próxima e,
na troca de frase, a legenda nova aparecia por cima da antiga. Aqui só os FINS mudam: os inícios
(e portanto cenas, capítulos e narração) ficam idênticos.

uso: python lote10/corrige_fins.py r01 r02 ...
"""
import json, sys

SPECS = {"r01": ["lote10/align/r01_A.json:226.2", "lote10/align/r01_B.json:209.9", "lote10/align/r01_C.json"]}
TEMPO = {"r03": 0.92}
INICIO = 1.0  # --inicio padrão do 01c_externo

def fim_real(cur):
    """Fim da palavra pelos caracteres de letra/número. Se há um buraco dentro da palavra (o Suno às vezes
    joga a última sílaba para depois da pausa: 'rit' ... 'o'), o fim vai para logo depois do buraco."""
    al = [c for c in cur if c[0].isalnum()] or cur
    for k in range(1, len(al)):
        if al[k][1] - al[k - 1][2] > 0.35:
            return al[k - 1][2] + 0.09 * (len(al) - k)
    return al[-1][2]

def palavras(specs, tempo):
    """Mesma conta do 01c_externo; devolve (início antigo, fim antigo, fim corrigido)."""
    out, off = [], 0.0
    for spec in specs:
        arq, _, corte = spec.partition(":")
        corte = float(corte) if corte else None
        chars = []
        for t in json.load(open(arq))["words"]:
            if corte is not None and t["start_s"] >= corte: break
            n = max(1, len(t["word"]))
            for k, ch in enumerate(t["word"]):
                a_ = t["start_s"] + (t["end_s"] - t["start_s"]) * k / n
                chars.append((ch, (off + a_) / tempo, (off + t["start_s"] + (t["end_s"] - t["start_s"]) * (k + 1) / n) / tempo))
        cur = []
        for ch in chars + [(" ", 0, 0)]:
            if ch[0].isspace():
                if cur:
                    out.append((cur[0][1], cur[-1][2], fim_real(cur))); cur = []
            else: cur.append(ch)
        off += corte if corte is not None else 0
    return out

for v in sys.argv[1:]:
    arq = f"lote10/timeline_{v}.json"
    tl = json.load(open(arq))
    rec = palavras(SPECS.get(v, [f"lote10/align/{v}_full.json"]), TEMPO.get(v, 1.0))
    por_ini = {}
    for s, e_velho, e_novo in rec:
        por_ini.setdefault(round(s + INICIO, 3), []).append((round(e_velho + INICIO, 3), round(e_novo + INICIO, 3)))
    mudou = casou = total = 0
    for f in tl["frases"]:
        if f.get("so_destaque"): continue
        for p in f["palavras"]:
            total += 1
            cand = por_ini.get(p["ini"])
            if not cand: continue
            # mesma palavra: início igual e fim antigo igual (ou já cortado pelo fim da voz)
            ok = [n for vel, n in cand if abs(vel - p["fim"]) < 0.002 or p["fim"] < vel]
            if not ok: continue
            casou += 1
            novo = max(p["ini"] + 0.05, min(p["fim"], ok[0]))
            if novo < p["fim"] - 0.0005: mudou += 1; p["fim"] = round(novo, 3)
        f["fim"] = f["palavras"][-1]["fim"]; f["duracao"] = round(f["fim"] - f["inicio"], 3)
    fr = [f for f in tl["frases"] if not f.get("so_destaque")]
    gaps = sorted(round(b["inicio"] - a["fim"], 2) for a, b in zip(fr, fr[1:]))
    json.dump(tl, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{v}: {casou}/{total} palavras achadas, {mudou} fins encurtados | pausa entre frases: "
          f"mín {gaps[0]} s, mediana {gaps[len(gaps)//2]} s")
