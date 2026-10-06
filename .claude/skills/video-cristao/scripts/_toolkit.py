"""Descobre a pasta de trabalho do motor (toolkit) — usada por todos os scripts da skill.

Ordem: $TOOLKIT → uma pasta video-jesus/ (com engine.py) no diretório atual ou acima → ~/video-cristao
(cópia do toolkit embutido na skill, criada pelo setup.sh).
"""
import os

SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOME_TK = os.path.expanduser("~/video-cristao")


def find():
    if os.environ.get("TOOLKIT"):
        return os.environ["TOOLKIT"]
    d = os.getcwd()
    while True:
        for cand in (d, os.path.join(d, "video-jesus")):
            if os.path.exists(os.path.join(cand, "engine.py")) and os.path.exists(os.path.join(cand, "synth.py")):
                return cand
        if d == "/":
            break
        d = os.path.dirname(d)
    return HOME_TK


if __name__ == "__main__":
    print(find())
