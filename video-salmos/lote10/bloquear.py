"""Uso: bloquear.py id1 id2 ... -> bloqueia esses e marca o resto das cenas atuais como aprovado."""
import json, sys
bad = {int(x) for x in sys.argv[1:]}
b = set(json.load(open("clips/bloqueados.json"))) | bad
json.dump(sorted(b), open("clips/bloqueados.json", "w"))
apr = set(json.load(open("lote10/aprovados.json")))
apr |= {c["clip"]["id"] for c in json.load(open("cenas.json"))} - bad
json.dump(sorted(apr), open("lote10/aprovados.json", "w"))
print(len(b), "bloqueados")
