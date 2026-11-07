"""Regera só algumas frases (texto novo) e alinha as palavras delas; depois rode retime.py.
    python3 tts_fix.py linhas.json narr/<pasta> ID1,ID2"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly

from tts import FIX, VOICE

lines = json.load(open(sys.argv[1]))
d = sys.argv[2]
ids = sys.argv[3].split(",")
tts = Kokoro(os.path.expanduser("~/tts/kokoro-v1.0.onnx"), os.path.expanduser("~/tts/voices-v1.0.bin"))
tm = json.load(open(os.path.join(d, "timing.json")))
byid = {l["id"]: l for l in tm["lines"]}
from faster_whisper import WhisperModel
m = WhisperModel("small.en", compute_type="int8")
for lid, text, speed, pause in lines:
    if lid not in ids:
        continue
    ph = tts.tokenizer.phonemize(text, "en-us")
    for a, b in FIX.items():
        ph = ph.replace(a, b)
    audio, sr = tts.create(ph, voice=VOICE, speed=speed, is_phonemes=True)
    nz = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(0, nz[0] - 240): nz[-1] + 1200]
    sf.write(os.path.join(d, f"{lid}.wav"), audio, sr)
    st = byid[lid]["start"]
    segs, _ = m.transcribe(resample_poly(audio, 2, 3).astype(np.float32), language="en", word_timestamps=True)
    words = [(w.word.strip(), round(st + w.start, 3), round(st + w.end, 3)) for s in segs for w in s.words]
    byid[lid].update(text=text, words=words, heard=" ".join(w[0] for w in words), end=round(st + len(audio) / sr, 3))
    print(lid, "->", byid[lid]["heard"])
json.dump(tm, open(os.path.join(d, "timing.json"), "w"), indent=1, ensure_ascii=False)
