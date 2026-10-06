"""Cria um projeto novo no toolkit a partir do modelo.

    python3 novo_projeto.py <nome_curto> "Título do vídeo" [--toolkit /caminho/video-jesus]

Gera <toolkit>/<nome>.py (cenas, legendas, versículos, traduções) e <toolkit>/<nome>_audio.py (trilha).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def find_toolkit():
    d = HERE
    while d != "/":
        cand = os.path.join(d, "video-jesus")
        if os.path.exists(os.path.join(cand, "engine.py")):
            return cand
        d = os.path.dirname(d)
    sys.exit("Toolkit não encontrado (pasta video-jesus/ com engine.py). Use --toolkit.")


ap = argparse.ArgumentParser()
ap.add_argument("nome")
ap.add_argument("titulo")
ap.add_argument("--toolkit")
a = ap.parse_args()
if not re.fullmatch(r"[a-z][a-z0-9_]*", a.nome):
    sys.exit("nome: só minúsculas, números e _ (vira nome de módulo Python)")
tk = a.toolkit or find_toolkit()
for src, dst in (("projeto_modelo.py", f"{a.nome}.py"), ("audio_modelo.py", f"{a.nome}_audio.py")):
    out = os.path.join(tk, dst)
    if os.path.exists(out):
        sys.exit(f"Já existe: {out} (escolha outro nome)")
    txt = open(os.path.join(ASSETS, src), encoding="utf-8").read()
    open(out, "w", encoding="utf-8").write(txt.replace("__NOME__", a.nome).replace("__TITULO__", a.titulo))
    print("criado:", out)
