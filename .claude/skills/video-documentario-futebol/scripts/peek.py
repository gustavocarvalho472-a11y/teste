#!/usr/bin/env python3
"""Time-sampled contact sheet: python3 peek.py name step [start end] -> build/peek/<name>.jpg (6 columns, labelled with seconds)."""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/build/peek"; os.makedirs(O, exist_ok=True)
name, step = sys.argv[1], float(sys.argv[2]); src = f"{ROOT}/assets/real/{name}.mp4"
d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))
a = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5; b = float(sys.argv[4]) if len(sys.argv) > 4 else d - 0.3
ts = []; t = a
while t < b and len(ts) < 60: ts.append(round(t, 1)); t += step
tmp = tempfile.mkdtemp()
def one(i):
    f = f"{tmp}/{i:03d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ts[i]), "-i", src, "-frames:v", "1", "-vf",
                    f"scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,drawtext=text='{ts[i]}':fontcolor=yellow:fontsize=20:x=4:y=4:box=1:boxcolor=black@0.7", f])
    return f
with ThreadPoolExecutor(4) as ex: files = list(ex.map(one, range(len(ts))))
open(f"{tmp}/l.txt", "w").write("".join(f"file '{f}'\n" for f in files))
rows = (len(files) + 5) // 6
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/l.txt", "-vf", f"tile=6x{rows}", "-frames:v", "1", "-q:v", "5", f"{O}/{name}.jpg"])
print(f"{O}/{name}.jpg", len(ts))
