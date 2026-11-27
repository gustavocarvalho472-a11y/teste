#!/usr/bin/env python3
"""Multilingual local transcription (sherpa-onnx Whisper small). Usage: python3 asr_ml.py file.mp4 lang [start end win]"""
import sys, subprocess, numpy as np, sherpa_onnx
M = "/opt/asr/sherpa-onnx-whisper-small"
f, lang = sys.argv[1], sys.argv[2]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/small-encoder.int8.onnx", decoder=f"{M}/small-decoder.int8.onnx", tokens=f"{M}/small-tokens.txt", language=lang, task="transcribe", num_threads=4)
a = float(sys.argv[3]) if len(sys.argv) > 3 else 0; b = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9; W = float(sys.argv[5]) if len(sys.argv) > 5 else 8
x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(a), "-i", f, "-t", str(min(b - a, 99999)), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]), dtype=np.float32)
n = int(W * 16000)
for i in range(0, len(x), n):
    s = rec.create_stream(); s.accept_waveform(16000, x[i:i + n]); rec.decode_stream(s)
    t = s.result.text.strip()
    if t: print(f"[{a + i / 16000:7.1f}] {t}", flush=True)
