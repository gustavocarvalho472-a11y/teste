#!/usr/bin/env python3
"""Camera language for the channel's v2 style: every shot gets a slow, motivated move framed on the face.

A shot is {kind: video|photo|plate, src, ss, frames, slow, safe:(w,h,x,y) fractions of the source that are clean
(no logos/tickers/burned captions), face0/face1: [cx,cy,h] (normalised inside the safe area) or None, move, shot}.
plan(shot) adds z0,z1 (zoom), fx0,fy0,fx1,fy1 (focus inside the safe area) and frx,fry (where the focus sits on screen).
vf(shot) returns the ffmpeg chain that produces exactly shot['frames'] 1920x1080 frames.

Rules (what an editor does by hand):
- talk  : medium close-up, face ~34% of frame height, eyes on the upper third, very slow push (3-5%).
- tight : punch-in close-up (face ~46%) used on the second phrase of a soundbite (jump-zoom on the cut).
- broll : face ~24% of frame height; alternate push-in (wide -> face) and pull-out (face -> wide).
- photo : stronger Ken Burns (12-22%), always toward or away from the face; no face -> slow lateral drift.
- plate : graphics pictures rendered at 2x; slow push of 4-6% toward the subject.
- never magnify the source more than MAXMAG (softness), never show outside the safe area.
"""
import math, subprocess, functools
W, H, FPS = 1920, 1080, 25
MAXMAG = 2.45
TARGET = {"talk": 0.40, "tight": 0.52, "broll": 0.30, "photo": 0.32}
MAXMAG_PHOTO = 2.0

@functools.lru_cache(None)
def size(src):
    if src.endswith((".jpg", ".png")):
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", src]).decode().split()[0]
    else:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src]).decode().split()[0]
    w, h = out.split(",")[:2]; return int(w), int(h)

def cover(shot):
    sw, sh = size(shot["src"]) if shot["kind"] != "plate" else (3840, 2160)
    w, h, x, y = shot.get("safe") or (1, 1, 0, 0)
    cw, ch = sw * w, sh * h; s0 = max(W / cw, H / ch)
    return cw, ch, s0

def clamp(v, a, b): return max(a, min(b, v))

def plan(shot, i=0):
    """Choose zoom/focus for the shot. i alternates in/out so consecutive shots don't all move the same way."""
    cw, ch, s0 = cover(shot); kind = shot["kind"]; style = shot.get("shot") or ("broll" if kind == "video" else kind)
    zmax = 1.0 if kind == "plate" else max(1.0, (MAXMAG_PHOTO if kind == "photo" else MAXMAG) / s0)
    if kind == "plate":
        zmax = 1.08
    f0, f1 = shot.get("face0"), shot.get("face1") or shot.get("face0")
    if f0 is None and f1 is not None: f0 = f1
    move = shot.get("move") or ("in" if i % 2 == 0 else "out")
    frx = shot.get("frx", 0.5); fry = 0.42
    if kind == "plate":
        fx, fy = shot.get("focus", (0.5, 0.5)); amp = shot.get("amp", 0.05)
        z0, z1 = (1.0, 1.0 + amp) if move != "out" else (1.0 + amp, 1.0)
        return {**shot, "z0": z0, "z1": z1, "fx0": fx, "fy0": fy, "fx1": fx, "fy1": fy, "frx": fx, "fry": fy}
    if f0:
        fh = (f0[2] + f1[2]) / 2
        zc = clamp(TARGET.get(style, 0.24) * H / (fh * ch * s0), 1.0, zmax)
        toward = lambda f, k=0.45: (0.5 + (f[0] - 0.5) * k, 0.5 + (f[1] - 0.5) * k)
        if style in ("talk", "tight"):             # soundbites: hold the size, just breathe in
            z1 = zc; z0 = max(1.0, zc - 0.05)
            if z1 - z0 < 0.02: z0 = max(1.0, min(z1, zmax) - 0.04); z1 = min(zmax, z0 + 0.04)
            if style == "tight":                    # the punch-in must read as a cut to a closer lens
                z0 = max(z0, min(zmax - 0.04, 1.14)); z1 = min(zmax, max(z1, z0 + 0.04))
            z0, z1, c0, c1 = z0, z1, f0, f1
        else:
            amp = 0.2 if kind == "photo" else 0.12
            zfar = max(1.0, zc - amp)
            if zc - zfar < 0.05: zfar, zc = 1.0, min(zmax, 1.0 + amp * 0.7)
            if move == "out": z0, z1, c0, c1 = zc, zfar, f0, toward(f1)
            else: z0, z1, c0, c1 = zfar, zc, toward(f0), f1
        return {**shot, "z0": z0, "z1": z1, "fx0": c0[0], "fy0": c0[1], "fx1": c1[0], "fy1": c1[1], "frx": frx, "fry": fry}
    # no face: drift / push on a point of interest
    fx, fy = shot.get("focus", (0.5, 0.5)); amp = 0.14 if kind == "photo" else 0.08
    amp = min(amp, zmax - 1.0) if zmax > 1.0 else 0.0
    if move == "pan":
        z = 1.0 + max(amp, 0.0) + 0.04 if zmax >= 1.12 else zmax
        return {**shot, "z0": z, "z1": z, "fx0": 0.3, "fy0": fy, "fx1": 0.7, "fy1": fy, "frx": 0.5, "fry": 0.5}
    z0, z1 = (1.0, 1.0 + amp) if move == "in" else (1.0 + amp, 1.0)
    return {**shot, "z0": z0, "z1": z1, "fx0": fx, "fy0": fy, "fx1": fx, "fy1": fy, "frx": 0.5, "fry": 0.5}

def safe_crop(shot):
    w, h, x, y = shot.get("safe") or (1, 1, 0, 0)
    return "" if (w, h, x, y) == (1, 1, 0, 0) else f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},"

def move_chain(shot):
    """scale (per-frame zoom) + crop (per-frame focus). t is the output time of the shot."""
    cw, ch, s0 = cover(shot); D = max(0.04, shot["frames"] / FPS)
    BW, BH = math.ceil(cw * s0) + 2, math.ceil(ch * s0) + 2
    P = f"(0.5-0.5*cos(PI*min(t/{D:.3f}\\,1)))"
    Z = f"({shot['z0']:.4f}+{shot['z1'] - shot['z0']:.4f}*{P})"
    fx = f"({shot['fx0']:.4f}+{shot['fx1'] - shot['fx0']:.4f}*{P})"; fy = f"({shot['fy0']:.4f}+{shot['fy1'] - shot['fy0']:.4f}*{P})"
    return (f"scale=w='2*trunc({BW}*{Z}/2)':h='2*trunc({BH}*{Z}/2)':eval=frame:flags=bicubic,"
            f"crop={W}:{H}:x='clip({fx}*iw-{shot['frx'] * W:.1f}\\,0\\,iw-{W})':y='clip({fy}*ih-{shot['fry'] * H:.1f}\\,0\\,ih-{H})'")

GRADE = {"color": "eq=contrast=1.07:saturation=0.82:brightness=-0.015,colorbalance=rs=0.03:bs=-0.03:rh=0.02:bh=-0.025",
         "bw": "hue=s=0,eq=contrast=1.18:brightness=-0.03", "none": "null"}
