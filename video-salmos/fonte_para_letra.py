"""Gera a letra para o Suno a partir de roteiro_<nome>_fonte.txt.
Uma frase por linha, linha em branco entre blocos. Uma linha '%' divide em duas gerações
(criação + extensão no Suno): grava <saida>_A.txt e <saida>_B.txt."""
import sys
src, dst = sys.argv[1], sys.argv[2].removesuffix(".txt")
partes, out = [], []
for line in open(src, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("@"): continue
    if line.startswith("%"):
        partes.append(out); out = []; continue
    if line.startswith("#"):
        if out: out.append("")
        continue
    out.append(line.split("|", 2)[2])
partes.append(out)
for i, p in enumerate(partes):
    txt = "\n".join(p).strip() + "\n"
    nome = f"{dst}_{'ABCDE'[i]}.txt" if len(partes) > 1 else f"{dst}.txt"
    open(nome, "w", encoding="utf-8").write(txt)
    print(f"{len(txt)} caracteres -> {nome}")
