"""Gera legendas .srt (para subir no YouTube) a partir das legendas do projeto.

    VIDEO_LANG=pt VIDEO_NARRATION=tela python3 srt.py tela saida.srt [t0:t1]
"""
import importlib
import os
import sys

import render


def fmt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def build(projname, t0=0.0, t1=None):
    proj = importlib.import_module(projname)
    t1 = proj.TOTAL if t1 is None else t1
    items = []
    for k, sc in enumerate(proj.SCENES):
        st, scale = proj.STARTS[k], proj.SCALE[k]
        for cp in sc[3]:
            items.append((st + cp[0], st + cp[1], render.tr(cp[2]).replace("*", "")))
        extra = getattr(proj, "NARRATION_EXTRA", {}).get(k, [])
        for j, (ta, txt) in enumerate(extra):   # falas sem legenda na tela (montagem)
            tb = extra[j + 1][0] if j + 1 < len(extra) else ta + 1.1
            items.append((st + ta * scale, st + tb * scale - 0.05, render.tr(txt)))
    items = sorted((max(a, t0) - t0, min(b, t1) - t0, s) for a, b, s in items if b > t0 and a < t1)
    return "\n".join(f"{i}\n{fmt(a)} --> {fmt(b)}\n{s}\n" for i, (a, b, s) in enumerate(items, 1))


if __name__ == "__main__":
    rng = sys.argv[3].split(":") if len(sys.argv) > 3 else ["0", ""]
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(build(sys.argv[1], float(rng[0]), float(rng[1]) if rng[1] else None))
    print("OK:", sys.argv[2])
