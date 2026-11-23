#!/usr/bin/env python3
"""Kokoro (ONNX) narration: one MP3 per beat from lines.txt (id|text). Usage: python3 tts.py [ids...]"""
import os, sys, subprocess, json, re
import soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f"{ROOT}/assets/vo"; os.makedirs(OUT, exist_ok=True)
SAY = {"Vinicius's": "Vinisius's", "Vinicius": "Vinisius", "Xabi": "Shahbee", "Arteta": "Ar-tetta", "Diomande": "Dee-oh-mahn-day", "Mbappé": "Em-bappay", "Bernabéu": "Bernabay-oo",
       "Clásico": "Classico", "Saliba": "Saleeba", "Arbeloa": "Arbeh-loa", "Mourinho": "Mo-reen-yo", "José": "Jozay", "Camp Nou": "Camp Noo",
       "Ballon d'Or": "Ballon Dor", "newspaper AS": "newspaper A.S.", "according to AS": "according to A.S.", "VAR": "V.A.R.", "Girona": "Jee-rona",
       "Villarreal": "Vee-ya-ray-al", "Sevilla": "Seviya", "Betis": "Bettis", "Leipzig": "Lipe-zig", "La Liga": "La Leega"}
k = Kokoro("/opt/kokoro/kokoro-v1.0.onnx", "/opt/kokoro/voices-v1.0.bin")
only = sys.argv[1:]; durs = json.load(open(f"{OUT}/durations.json")) if os.path.exists(f"{OUT}/durations.json") else {}
for line in open(f"{ROOT}/lines.txt"):
    if "|" not in line: continue
    i, t = line.strip().split("|", 1)
    if only and i not in only: continue
    for a, b in SAY.items(): t = t.replace(a, b)
    s, sr = k.create(t, voice="am_michael", speed=1.0, lang="en-us")
    wav = f"{OUT}/{i}.wav"; sf.write(wav, s, sr)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse", "-ar", "48000", "-b:a", "192k", f"{OUT}/{i}.mp3"], check=True)
    os.remove(wav)
    durs[i] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{OUT}/{i}.mp3"]))
    print(i, round(durs[i], 2), flush=True)
json.dump(durs, open(f"{OUT}/durations.json", "w"), indent=1)
print("TOTAL", round(sum(durs.values()), 1))
