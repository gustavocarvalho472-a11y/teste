"""Narração + alinhamento → build/timing.json

Dois modos:
  1. Existe audio/narracao_<idioma>.mp3 (voz gravada/TTS final): transcreve com Whisper (palavra a palavra) e acha o
     início de cada bloco do roteiro pelo alinhamento do texto (difflib sobre as palavras).
  2. Não existe: gera a narração provisória com Kokoro (voz pm_alex, motor da skill video-ilustracao),
     bloco a bloco, e grava build/narracao_tts.wav. Os inícios de bloco saem exatos.
Nos dois modos o Whisper dá o tempo de cada palavra para a legenda karaokê.

    python3 narrar.py            # detecta o modo
    python3 narrar.py --tts      # força a narração provisória
"""
import difflib
import json
import os
import re
import sys
import unicodedata

import numpy as np
import soundfile as sf

from roteiro import B, LANG, fala_tts

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build", LANG)
SR = 24000
GAP = 0.32          # respiro entre blocos de fala
TOOLKIT = os.path.expanduser("~/video-ilustracao")


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if not unicodedata.combining(c)))


def tts():
    import hashlib
    key = hashlib.md5(json.dumps([(b["id"], b["fala"], b.get("dur"), b.get("pausa"), b.get("respiro")) for b in B]).encode()).hexdigest()
    cache = os.path.join(BUILD, "tts_blocks.json")
    path = os.path.join(BUILD, "narracao_tts.wav")
    if os.path.exists(cache) and json.load(open(cache))["key"] == key and os.path.exists(path):
        print("narração em cache (roteiro igual)")
        return path, json.load(open(cache))["blocks"]
    sys.path.insert(0, TOOLKIT)
    os.environ["VIDEO_LANG"] = LANG                 # define a voz do motor: am_michael (en) / pm_alex (pt)
    import narracao
    from kokoro_onnx import Kokoro
    narracao.EN_WORDS |= {"bridge", "online", "street"}
    m = os.path.expanduser("~/tts")
    k = Kokoro(os.path.join(m, "kokoro-v1.0.onnx"), os.path.join(m, "voices-v1.0.bin"))
    out, blocks, t = [], [], 0.6
    out.append(np.zeros(int(t * SR)))
    for b in B:
        if not b["fala"]:
            d = b.get("dur", 1.5)
            blocks.append({"id": b["id"], "start": t, "end": t + d})
            out.append(np.zeros(int(d * SR)))
            t += d
            continue
        a, sr = narracao.speak(k, fala_tts(b["fala"]))
        assert sr == SR
        pre = b.get("pausa", 0.0)
        out.append(np.zeros(int(pre * SR)))
        t += pre
        blocks.append({"id": b["id"], "start": t, "end": t + len(a) / SR})
        out.append(a)
        t += len(a) / SR
        gap = GAP + b.get("respiro", 0) + (0.45 if b.get("ato") or b["id"] in ("S06", "S09") else 0)
        out.append(np.zeros(int(gap * SR)))
        t += gap
        print(f'{b["id"]:6s} {blocks[-1]["start"]:7.2f}  {len(a) / SR:5.2f}s')
    os.makedirs(BUILD, exist_ok=True)
    sf.write(path, np.concatenate(out).astype(np.float32), SR)
    json.dump({"key": key, "blocks": blocks}, open(cache, "w"))
    return path, blocks


def whisper_words(path):
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
    import subprocess
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
    audio = np.frombuffer(raw, np.float32)        # passa o áudio já decodificado (evita a API do PyAV)
    segs, _ = model.transcribe(audio, language=LANG, word_timestamps=True, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words:
            words.append((w.word.strip(), w.start, w.end))
    return words


def align(blocks_known, words):
    """Atribui tempo a cada palavra do roteiro. Se blocks_known é None, deduz os inícios de bloco."""
    toks = []   # (bloco, palavra exibida)
    for i, b in enumerate(B):
        for w in b["fala"].split():
            toks.append((i, w))
    a = [norm(w) for _, w in toks]
    bw = [norm(w[0]) for w in words]
    times = [None] * len(toks)
    sm = difflib.SequenceMatcher(None, a, bw, autojunk=False)
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            times[blk.a + j] = (words[blk.b + j][1], words[blk.b + j][2])
    # blocos: modo gravado → início = 1ª palavra casada do bloco
    if blocks_known is None:
        blocks_known, prev = [], 0.0
        for i, b in enumerate(B):
            idx = [k for k, (bi, _) in enumerate(toks) if bi == i]
            got = [times[k] for k in idx if times[k]]
            if b["fala"] and got:
                st, en = got[0][0], got[-1][1]
            else:
                st = prev
                en = st + b.get("dur", 1.5)
            blocks_known.append({"id": b["id"], "start": st, "end": en})
            prev = en
    # palavras sem casamento (ou fora do bloco) → interpolação por caracteres dentro do bloco
    out = []
    for i, blk in enumerate(blocks_known):
        idx = [k for k, (bi, _) in enumerate(toks) if bi == i]
        if not idx:
            out.append([])
            continue
        st, en = blk["start"], blk["end"]
        tt = [times[k] if times[k] and st - 0.3 <= times[k][0] <= en + 0.3 else None for k in idx]
        lens = np.array([len(toks[k][1]) + 1 for k in idx], float)
        prop = st + (en - st) * np.concatenate([[0], np.cumsum(lens)]) / lens.sum()
        ws = []
        for j, k in enumerate(idx):
            t0 = tt[j][0] if tt[j] else prop[j]
            ws.append([toks[k][1], round(float(t0), 3)])
        for j in range(1, len(ws)):     # monotônico
            ws[j][1] = max(ws[j][1], ws[j - 1][1])
        out.append(ws)
    for blk, ws in zip(blocks_known, out):
        blk["words"] = ws
    return blocks_known


def main():
    mp3 = os.path.join(HERE, "audio", f"narracao_{LANG}.mp3")
    if os.path.exists(mp3) and "--tts" not in sys.argv:
        path, blocks = mp3, None
        print("modo: narração gravada", mp3)
    else:
        print("modo: narração provisória Kokoro", "am_michael" if LANG == "en" else "pm_alex")
        path, blocks = tts()
    words = whisper_words(path)
    blocks = align(blocks, words)
    import subprocess
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                           "-of", "csv=p=0", path]).decode())
    total = max(total, blocks[-1]["end"])
    json.dump({"audio": os.path.relpath(path, HERE), "total": total, "blocks": blocks,
               "whisper": " ".join(w[0] for w in words)},
              open(os.path.join(BUILD, "timing.json"), "w"), ensure_ascii=False, indent=1)
    print(f"OK build/timing.json  total {total:.1f}s")


if __name__ == "__main__":
    main()
