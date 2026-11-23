#!/usr/bin/env python3
"""Local Whisper small (multilingual). Usage: asr.py file lang [win] [start] [end]"""
import sys, subprocess, numpy as np, sherpa_onnx
M = "/opt/asr/sherpa-onnx-whisper-small"
lang = sys.argv[2] if len(sys.argv) > 2 else "en"
W = float(sys.argv[3]) if len(sys.argv) > 3 else 20
A = float(sys.argv[4]) if len(sys.argv) > 4 else 0; B = float(sys.argv[5]) if len(sys.argv) > 5 else 1e6
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/small-encoder.int8.onnx", decoder=f"{M}/small-decoder.int8.onnx", tokens=f"{M}/small-tokens.txt", language=lang, task="transcribe", num_threads=4)
x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(A), "-i", sys.argv[1], "-t", str(B - A), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]), dtype=np.float32)
n = int(W * 16000)
for i in range(0, len(x), n):
    s = rec.create_stream(); s.accept_waveform(16000, x[i:i + n]); rec.decode_stream(s)
    t = s.result.text.strip()
    if t: print(f"[{A + i/16000:7.1f}] {t}", flush=True)
