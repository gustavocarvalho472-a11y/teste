#!/usr/bin/env python3
"""Free local transcription (sherpa-onnx Whisper base.en) in fixed windows. Usage: python3 asr.py file.mp4 [start end win]"""
import sys, subprocess, numpy as np, sherpa_onnx
M = "/opt/asr/sherpa-onnx-whisper-base.en"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/base.en-encoder.int8.onnx", decoder=f"{M}/base.en-decoder.int8.onnx", tokens=f"{M}/base.en-tokens.txt", num_threads=4)
f = sys.argv[1]; a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; b = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9; W = float(sys.argv[4]) if len(sys.argv) > 4 else 8
x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(a), "-i", f, "-t", str(min(b - a, 99999)), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]), dtype=np.float32)
n = int(W * 16000)
for i in range(0, len(x), n):
    s = rec.create_stream(); s.accept_waveform(16000, x[i:i + n]); rec.decode_stream(s)
    t = s.result.text.strip()
    if t: print(f"[{a + i / 16000:7.1f}] {t}", flush=True)
