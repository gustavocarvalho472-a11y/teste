"""Remonta a narração com novas pausas sem regerar a voz: reaproveita os WAVs de cada frase e
desloca os tempos de palavra no timing.json.   python3 retime.py linhas.json narr/<pasta> [lead]"""
import json
import os
import sys

import numpy as np
import soundfile as sf


def main(lines_path, d, lead=0.4):
    lines = json.load(open(lines_path))
    old = json.load(open(os.path.join(d, "timing.json")))
    byid = {l["id"]: l for l in old["lines"]}
    sr = 24000
    track, t, out = [np.zeros(int(lead * sr), np.float32)], lead, []
    for lid, text, speed, pause in lines:
        a, sr = sf.read(os.path.join(d, f"{lid}.wav"), dtype="float32")
        dur = len(a) / sr
        o = byid[lid]
        shift = t - o["start"]
        words = [(w, round(s + shift, 3), round(e + shift, 3)) for w, s, e in o["words"]]
        out.append({**o, "start": round(t, 3), "end": round(t + dur, 3), "words": words})
        track += [a, np.zeros(int(pause * sr), np.float32)]
        t += dur + pause
    sf.write(os.path.join(d, "narracao.wav"), np.concatenate(track), sr)
    json.dump({"total": round(t, 3), "lines": out}, open(os.path.join(d, "timing.json"), "w"), indent=1,
              ensure_ascii=False)
    print("TOTAL", round(t, 2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.4)
