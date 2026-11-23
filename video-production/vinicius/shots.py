#!/usr/bin/env python3
"""Detects shots in every real source clip and builds labelled contact sheets for take selection."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.abspath(__file__)); R = f"{ROOT}/assets/real"; O = f"{ROOT}/build/shots"
os.makedirs(O, exist_ok=True)
DB = f"{ROOT}/build/shots.json"
db = json.load(open(DB)) if os.path.exists(DB) else {}


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def detect(name):
    p = f"{R}/{name}.mp4"; d = dur(p)
    out = subprocess.run(["ffmpeg", "-i", p, "-vf", "scale=320:-2,select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [0.0] + [float(x) for x in re.findall(r"pts_time:([\d.]+)", out)] + [d]
    shots = [[round(a, 2), round(b, 2)] for a, b in zip(cuts, cuts[1:]) if b - a >= 1.6]
    return name, shots


def thumb(args):
    name, i, a, b = args; f = f"{O}/{name}_{i:03d}.jpg"
    if not os.path.exists(f):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a + min(1.0, (b - a) / 2)), "-i", f"{R}/{name}.mp4", "-frames:v", "1", "-vf",
                        f"scale=384:216:force_original_aspect_ratio=increase,crop=384:216,drawtext=text='{name} {i} ({b-a:.0f}s)':fontcolor=yellow:fontsize=17:x=4:y=4:box=1:boxcolor=black@0.7", f])
    return f


names = sorted(f[:-4] for f in os.listdir(R) if f.endswith(".mp4"))
new = [n for n in names if n not in db]
with ThreadPoolExecutor(4) as ex:
    for name, shots in ex.map(detect, new):
        db[name] = shots; print(name, len(shots))
json.dump(db, open(DB, "w"))
jobs = [(n, i, a, b) for n in (sys.argv[1:] or new) for i, (a, b) in enumerate(db[n])]
with ThreadPoolExecutor(4) as ex:
    files = list(ex.map(thumb, jobs))
for k in range(0, len(files), 40):
    lst = f"{O}/list.txt"; open(lst, "w").write("".join(f"file '{f}'\n" for f in files[k:k + 40]))
    tag = (sys.argv[1] if len(sys.argv) == 2 else "new") + f"_{k//40}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "tile=5x8", "-frames:v", "1", "-q:v", "4", f"{O}/sheet_{tag}.jpg"])
    print("sheet", f"{O}/sheet_{tag}.jpg")
