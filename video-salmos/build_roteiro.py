"""Converte roteiro_fonte.txt em roteiro.json e faz checagens de texto para a voz."""
import json, re, sys, collections
src = sys.argv[1] if len(sys.argv) > 1 else "roteiro_fonte.txt"
TAGS = {"ceu_noturno","lua","nascer_sol","luz_divina","vela","biblia","maos_orando","campo",
        "pastor_ovelhas","rio","mar_calmo","montanha","floresta","chuva_janela","cruz","aguia","fogo_lareira"}
out, bloco, titulos, erros = [], None, {}, []
for n, line in enumerate(open(src, encoding="utf-8"), 1):
    line = line.strip()
    if not line: continue
    if line.startswith("#"):
        bid, tit = [x.strip() for x in line[1:].split("|")]
        bloco = bid; titulos[bid] = tit; continue
    tag, ref, frase = line.split("|", 2)
    if tag not in TAGS: erros.append(f"{n}: tag desconhecida {tag}")
    if re.search(r"\d|[()\[\]—–]", frase): erros.append(f"{n}: número/parêntese/travessão: {frase}")
    out.append({"bloco": bloco, "titulo_bloco": titulos[bloco], "frase": frase, "tag_visual": tag,
                "mostrar_texto": bool(ref), "referencia": ref or None})
dups = [f for f, c in collections.Counter(o["frase"] for o in out).items() if c > 1]
if dups: erros.append(f"frases duplicadas: {dups}")
json.dump(out, open("roteiro.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
words = sum(len(o["frase"].split()) for o in out)
print(f"{len(out)} frases, {words} palavras")
for b in titulos:
    fs = [o for o in out if o["bloco"] == b]
    print(f"  {b:10s} {len(fs):3d} frases {sum(len(o['frase'].split()) for o in fs):5d} palavras")
lens = [len(o["frase"].split()) for o in out]
print("frases fora de 8-20 palavras:", sum(1 for l in lens if l < 8 or l > 20))
print("\n".join(erros) or "sem erros")
