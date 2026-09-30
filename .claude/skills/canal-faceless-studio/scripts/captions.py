#!/usr/bin/env python3
"""Áudio -> legendas SRT (faster-whisper, local). Uso: captions.py audio.mp3 out.srt [--lang en] [--words 6]"""
import argparse
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--lang", default=None); ap.add_argument("--model", default="base")
ap.add_argument("--words", type=int, default=6, help="máx. de palavras por legenda")
a = ap.parse_args()

model = WhisperModel(a.model, compute_type="int8")
segs, _ = model.transcribe(a.audio, language=a.lang, word_timestamps=True)
words = [w for s in segs for w in s.words]

def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"

lines, i = [], 0
while i < len(words):
    chunk = words[i:i + a.words]
    lines.append((chunk[0].start, chunk[-1].end, "".join(w.word for w in chunk).strip()))
    i += a.words
with open(a.out, "w", encoding="utf-8") as f:
    for n, (s, e, t) in enumerate(lines, 1):
        f.write(f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n\n")
print("ok:", a.out, len(lines), "legendas")
