"""Narração em português (Kokoro pm_alex) encaixada na mesma edição: cada frase começa no ponto da frase em
inglês; se for mais longa que o espaço disponível, acelera (até 1.3x) sem invadir as falas reais dos clipes.
    python3 tts_pt.py teste            # só testa a pronúncia de nomes difíceis
    python3 tts_pt.py                  # gera tudo em narr/fiel_pt/
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

os.environ["VIDEO_LANG"] = "pt"
os.environ["VIDEO_VOICE"] = "pm_alex"
sys.path.insert(0, "/root/video-ilustracao")
import narracao as NR  # noqa: E402  (phonemes_pt com as correções de pronúncia do canal)
from kokoro_onnx import Kokoro  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "narr", "fiel_pt")
NR.EN_WORDS |= {"the", "boys", "old", "trafford", "piers", "morgan", "athletic", "aviva", "stadium", "manchester",
                "united", "city", "tottenham", "erik", "ten", "hag", "o'shea", "dara", "houston", "dallas",
                "instagram"}
VOICE = "pm_alex"
MAXSPD = 1.3
tts = Kokoro(os.path.expanduser("~/tts/kokoro-v1.0.onnx"), os.path.expanduser("~/tts/voices-v1.0.bin"))


def say(text, speed=1.0):
    ph = NR.phonemes_pt(tts, text)
    a, sr = tts.create(ph, voice=VOICE, speed=speed, is_phonemes=True)
    nz = np.where(np.abs(a) > 0.01)[0]
    return (a[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else a), sr


def whisper_check(items):
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    m = WhisperModel("small", compute_type="int8")
    import difflib
    def norm(s):
        return re.sub(r"[^\w ]", "", s.lower()).split()
    bad = 0
    for lid, text, a in items:
        segs, _ = m.transcribe(resample_poly(a, 2, 3).astype(np.float32), language="pt")
        heard = " ".join(s.text.strip() for s in segs)
        r = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
        if r < 0.9:
            bad += 1
            print(f"[{lid}] {r:.2f}\n   texto: {text}\n   ouviu: {heard}")
    print("frases com diferença:", bad, "de", len(items))


if __name__ == "__main__":
    lines = json.load(open(os.path.join(HERE, "roteiro_fiel", "roteiro_pt.json")))
    if len(sys.argv) > 1 and sys.argv[1] == "teste":
        tests = ["Em Old Trafford, o Manchester United vencia o Tottenham por 2 a 0.",
                 "Erik ten Hag falou ao The Athletic.", "Na terceira temporada de The Boys, o Capitão Pátria.",
                 "Na estreia contra a RD Congo, em Houston.", "Uma cotovelada nas costas de Dara O'Shea, no Aviva Stadium.",
                 "Ele ganhou um apelido novo nas redes: Homelando.", "Em 2026, aos 41 anos, em 226 jogos pela seleção."]
        items = []
        for i, t in enumerate(tests):
            a, sr = say(t)
            items.append((f"T{i}", t, a))
        whisper_check([(i, t, a) for i, t, a in items])
        sys.exit()
    sys.path.insert(0, HERE)
    import video as V   # tempos da edição (narração em inglês) e janelas das falas reais
    speech = sorted((c[0], c[0] + (c[5] or 0)) for c in V.CLIPA if c[1] in V.SPEECH_CLIPS)
    os.makedirs(OUT, exist_ok=True)
    order = [l[0] for l in lines]
    sr = 24000
    track = np.zeros(int((V.TM["total"] + 2) * sr), np.float32)
    prev_end, items, log = 0.0, [], []
    for k, (lid, sec, text) in enumerate(lines):
        st = V.S(lid)
        nxt = V.S(order[k + 1]) - 0.2 if k + 1 < len(order) else V.TM["total"] + 1.5
        hard = min([nxt] + [a - 0.12 for a, b in speech if a > st - 0.01])
        slot = hard - st
        a, sr = say(text, 1.0)
        spd = 1.0
        if len(a) / sr > slot:
            spd = min(MAXSPD, len(a) / sr / slot * 1.03)
            a, sr = say(text, spd)
        t0 = max(st, prev_end + 0.1)
        over = t0 + len(a) / sr - hard
        i0 = int(t0 * sr)
        track[i0:i0 + len(a)] += a.astype(np.float32)[: len(track) - i0]
        prev_end = t0 + len(a) / sr
        sf.write(os.path.join(OUT, f"{lid}.wav"), a, sr)
        items.append((lid, text, a))
        log.append({"id": lid, "start": round(t0, 3), "end": round(prev_end, 3), "speed": round(spd, 3),
                    "overflow": round(max(0.0, over), 3)})
        flag = f"  ESTOUROU {over:.2f}s" if over > 0.05 else ""
        print(f"{lid:5s} {t0:7.2f}-{prev_end:7.2f} x{spd:.2f}{flag}", flush=True)
    sf.write(os.path.join(OUT, "narracao.wav"), track[: int((V.TM["total"] + 0.5) * sr)], sr)
    json.dump(log, open(os.path.join(OUT, "timing.json"), "w"), indent=1)
    print("velocidade média", round(float(np.mean([l["speed"] for l in log])), 3),
          "| acelerou:", sum(l["speed"] > 1.0 for l in log), "| estourou:", sum(l["overflow"] > 0.05 for l in log))
    whisper_check(items)
    print("FIM")
