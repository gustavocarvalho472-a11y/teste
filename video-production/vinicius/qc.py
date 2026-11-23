#!/usr/bin/env python3
"""QC: contact sheets of the final video (every 1.2 s in the first 40 s, every 12 s after) + loudness."""
import os, subprocess, sys
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.abspath(__file__)); V = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/out/ferguson-ghost-EN.mp4"
O = f"{ROOT}/build/qc"; os.makedirs(O, exist_ok=True)
d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V]))
ts = [round(0.6 + 1.2 * i, 1) for i in range(33)] + [round(t, 1) for t in range(46, int(d), 12)]
def grab(t):
    f = f"{O}/{t:07.1f}.jpg"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", V, "-frames:v", "1", "-vf", "scale=384:216", f]); return t, f
with ThreadPoolExecutor(4) as ex: shots = list(ex.map(grab, ts))
for k, part in enumerate([shots[:33], shots[33:]]):
    img = Image.new("RGB", (384 * 6, 216 * ((len(part) + 5) // 6)))
    for i, (t, f) in enumerate(part):
        im = Image.open(f); ImageDraw.Draw(im).text((4, 4), f"{int(t // 60)}:{t % 60:04.1f}", fill="yellow"); img.paste(im, ((i % 6) * 384, (i // 6) * 216))
    img.save(f"{ROOT}/build/qc_{k}.jpg", quality=80); print(f"{ROOT}/build/qc_{k}.jpg")
r = subprocess.run(["ffmpeg", "-i", V, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "LRA:", "Peak:"))][-3:])
