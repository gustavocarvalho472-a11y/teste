"""Linha do tempo: timing.json + roteiro → shots com tempo, eventos de som e capítulos."""
import json
import os

from roteiro import B, FALL_WORD, LANG

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build", LANG)
MAX_STATIC = 4.0     # regra do handoff: nada fica mais de 4 s parado


def load():
    tm = json.load(open(os.path.join(BUILD, "timing.json")))
    blocks = tm["blocks"]
    total = tm["total"] + 0.5
    shots = []
    for i, (b, bt) in enumerate(zip(B, blocks)):
        t0 = 0.0 if i == 0 else bt["start"] - 0.08          # o corte vem um tiquinho antes da fala
        t1 = (blocks[i + 1]["start"] - 0.08) if i + 1 < len(B) else total
        n = len(b["shots"])
        for j, s in enumerate(b["shots"]):
            asset, opts = (s, {}) if isinstance(s, str) else s
            a, z = t0 + (t1 - t0) * j / n, t0 + (t1 - t0) * (j + 1) / n
            # shot longo: sub-cortes alternando enquadramento (vira "segundo recorte")
            k = max(1, int((z - a) / MAX_STATIC + 0.999))
            for m in range(k):
                shots.append(dict(asset=asset, opts=opts, t0=a + (z - a) * m / k, t1=a + (z - a) * (m + 1) / k,
                                  sub=m, first=(j == 0 and m == 0), blk=i, b=b, bt=bt, bt0=t0, bt1=t1))
    return tm, blocks, shots, total


def events(blocks, shots):
    """(tempo, nome do sfx) — sfx explícitos do roteiro + whoosh/impact automáticos por tipo de shot."""
    ev = []
    for b, bt in zip(B, blocks):
        if b.get("sfx") == "paper_rip3":      # um rasgo por logo, em cada "rompe" (montar.py usa os mesmos tempos)
            ev += [(bt["start"] + x, "paper_rip") for x in fall_times(bt)]
        elif b.get("sfx"):
            ev.append((max(0.0, bt["start"] - 0.1), b["sfx"]))
    explicit = {round(t, 1) for t, _ in ev}
    for s in shots:
        if s["sub"] or round(max(0.0, s["bt"]["start"] - 0.1), 1) in explicit and s["first"]:
            continue
        a = s["asset"]
        if a.startswith("PRT"):
            ev.append((s["t0"], "whoosh"))
        elif a.startswith("MEME") and not s["opts"].get("dark"):
            ev.append((s["t0"], "impact"))
        elif a == "grid":
            for k in range(4):
                ev.append((s["t0"] + 0.35 * k, "shutter"))
    return sorted(ev)


def fall_times(bt, word=FALL_WORD, n=3):
    """Tempos (relativos ao bloco) em que a palavra é dita; reserva: divide o bloco em n partes."""
    ts = [t - bt["start"] for w, t in bt.get("words", []) if w.lower().startswith(word)]
    if len(ts) >= n:
        return ts[:n]
    d = bt["end"] - bt["start"]
    return [d * (k + 0.5) / (n + 0.5) for k in range(n)]


def chapters(blocks):
    out = []
    for b, bt in zip(B, blocks):
        if b.get("ato"):
            t = 0 if not out else int(bt["start"])
            out.append(f"{t // 60}:{t % 60:02d} {b['ato']}")
    return out


def music_marks(blocks):
    return [(bt["start"], b["mus"]) for b, bt in zip(B, blocks) if b.get("mus")]
