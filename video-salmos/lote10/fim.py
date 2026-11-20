"""Uso: fim.py <alinhamento_suno.json> <destino.json>  -> copia e mostra onde a fala termina."""
import json, shutil, sys
shutil.copy(sys.argv[1], sys.argv[2])
w = json.load(open(sys.argv[2]))["words"]
linhas, cur, ini = [], "", None
for x in w:
    if ini is None: ini = x["start_s"]
    cur += x["word"]
    if "\n" in x["word"]:
        linhas.append((ini, x["end_s"], cur.strip())); cur, ini = "", None
if cur: linhas.append((ini, w[-1]["end_s"], cur.strip()))
for a, b, t in linhas[-3:]: print(f"{a:7.2f}-{b:7.2f} {t[:90]}")
print("palavras:", len(w), "| última termina em", round(w[-1]["end_s"], 2))
