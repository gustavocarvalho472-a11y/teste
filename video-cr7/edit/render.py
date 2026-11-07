"""Render paralelo -> ffmpeg; e 'snap' para conferir quadros soltos numa grade.
    python3 render.py snap amostra grade.png 1.0 7.5 ...
    python3 render.py video amostra saida.mp4 [audio.wav] [t0 t1]
"""
import importlib
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image

W, H, FPS = 1920, 1080, 30
_P = None


def _frame(args):
    global _P
    name, i = args
    if _P is None:
        _P = importlib.import_module(name)
    return _P.frame(i)


def snap(name, out, times):
    with Pool(min(4, len(times))) as pool:
        frames = pool.map(_frame, [(name, int(round(float(t) * FPS))) for t in times])
    tw, th = 960, 540
    cols = 2
    rows = (len(frames) + cols - 1) // cols
    grid = Image.new("RGB", (tw * cols, th * rows))
    for k, fr in enumerate(frames):
        im = Image.frombuffer("RGBA", (W, H), fr, "raw", "BGRA", 0, 1).convert("RGB").resize((tw, th), Image.LANCZOS)
        grid.paste(im, ((k % cols) * tw, (k // cols) * th))
    grid.save(out, quality=88)
    print("grade:", out)


def video(name, out, audio=None, t0=None, t1=None):
    mod = importlib.import_module(name)
    a = int(round((t0 or 0) * FPS))
    b = int(round((t1 if t1 is not None else mod.TOTAL) * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r",
           str(FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", f"{(t0 or 0):.3f}", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "256k",
                "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    st = time.time()
    with Pool(os.cpu_count()) as pool:
        for k, fr in enumerate(pool.imap(_frame, [(name, i) for i in range(a, b)], chunksize=6)):
            p.stdin.write(fr)
            if k % 300 == 0:
                print(f"{k}/{b - a} quadros  {time.time() - st:.0f}s", flush=True)
    p.stdin.close()
    p.wait()
    print("OK", out, f"{(b - a) / FPS:.1f}s em {time.time() - st:.0f}s")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if sys.argv[1] == "snap":
        snap(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        args = sys.argv[2:]
        audio = args[2] if len(args) > 2 and args[2] not in ("-", "") else None
        t0 = float(args[3]) if len(args) > 3 else None
        t1 = float(args[4]) if len(args) > 4 else None
        video(args[0], args[1], audio, t0, t1)
