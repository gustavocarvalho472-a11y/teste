#!/usr/bin/env python3
"""Narração em PT do roteiro (Kokoro ONNX, grátis): narrador pm_alex, falas reais traduzidas em pm_santa.
Uso: python3 pt/tts_pt.py [ids…]  -> pt/vo/<id>.wav e, sem ids, pt/out/vinicius-arteta-PT-narracao.mp3"""
import os, sys, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
D = os.path.dirname(os.path.abspath(__file__)); VO = f"{D}/vo"; OUT = f"{D}/out"; os.makedirs(VO, exist_ok=True); os.makedirs(OUT, exist_ok=True)
VOICE = {"N": ("pm_alex", 1.0), "F": ("pm_santa", 0.97)}
k = Kokoro("/opt/kokoro/kokoro-v1.0.onnx", "/opt/kokoro/voices-v1.0.bin")
rows = [l.rstrip("\n").split("|", 2) for l in open(f"{D}/lines_pt.txt") if l.strip() and not l.startswith("#")]
only = sys.argv[1:]; SR = 24000
for i, v, t in rows:
    if v == "#" or (only and i not in only): continue
    f = f"{VO}/{i}.wav"
    if os.path.exists(f) and not only: continue
    voice, speed = VOICE[v]
    s, SR = k.create(t, voice=voice, speed=speed, lang="pt-br", sentence_pause=0.3, clause_pause=0.12)
    sf.write(f, s, SR); print(i, round(len(s) / SR, 1), flush=True)
if only: sys.exit()
def sil(sec): return np.zeros(int(sec * SR), np.float32)
out = [sil(0.4)]; prev = None
for i, v, t in rows:
    if v == "#": out.append(sil(1.3)); prev = "#"; continue
    s, _ = sf.read(f"{VO}/{i}.wav", dtype="float32")
    if prev is not None and prev != "#": out.append(sil(0.7 if (v == "F" or prev == "F") else 0.45))
    if v == "F": s = s * 0.92
    out.append(s); prev = v
out.append(sil(1.0)); wav = f"{OUT}/narracao.wav"; sf.write(wav, np.concatenate(out), SR)
mp3 = f"{OUT}/vinicius-arteta-PT-narracao.mp3"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar", "48000", "-b:a", "192k", mp3], check=True)
os.remove(wav)
print("OK", mp3, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3]).decode().strip())
